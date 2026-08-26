#!/usr/bin/env python3
"""Find loci with conserved flanks + diagnostic interior; design primers."""
import pickle, json
import numpy as np
from pathlib import Path
import primer3

OUT=Path("/sessions/tender-vibrant-faraday/mnt/outputs/primer")
D=pickle.load(open(OUT/"proj.pkl","rb"))
KEYS,M,INS=D["keys"],D["matrix"],D["inserts"]
GAL,OTH,ref_rec=D["galanga"],D["others"],D["ref_record"]
RL=134002
A=np.array([M[k][:RL] for k in KEYS])
gi=[KEYS.index(k) for k in GAL]; oi=[KEYS.index(k) for k in OTH]
V=list("ACGT")

gal=A[gi]; oth=A[oi]
gal_ok=np.isin(gal,V).all(axis=0); oth_ok=np.isin(oth,V).all(axis=0)
usable=gal_ok&oth_ok
gal_same=(gal==gal[0]).all(axis=0)
DIAG=usable&gal_same&(oth!=gal[0]).all(axis=0)
# fully conserved across all 8 (good primer sites)
CONS=np.isin(A,V).all(axis=0)&(A==A[0]).all(axis=0)

exons=[]
for f in ref_rec.features:
    if f.type not in ("CDS","gene","tRNA","rRNA"): continue
    g=f.qualifiers.get("gene",["?"])[0]
    for p in f.location.parts: exons.append((int(p.start),int(p.end),g,f.type))
def context(pos):
    h=[e for e in exons if e[0]<=pos<e[1]]
    if not h:
        b=[e for e in exons if e[1]<=pos]; a=[e for e in exons if e[0]>pos]
        bb=max(b,key=lambda e:e[1])[2] if b else "—"; aa=min(a,key=lambda e:e[0])[2] if a else "—"
        return f"{bb}-{aa} IGS"
    c=[x for x in h if x[3]=="CDS"]
    return (c[0][2] if c else h[0][2])

ref=''.join(A[KEYS.index("Kgal_REF")])

# ── candidate scan ────────────────────────────────────────────────────
PRIMER_LEN=24
cands=[]
for amp in (500, 700):
    for s in range(0, RL-amp, 50):
        e=s+amp
        # flanks must be fully conserved across all 8
        if not CONS[s:s+PRIMER_LEN].all(): continue
        if not CONS[e-PRIMER_LEN:e].all(): continue
        interior=DIAG[s+PRIMER_LEN:e-PRIMER_LEN]
        nd=int(interior.sum())
        if nd<2: continue
        # require no ambiguous/gap chars in reference amplicon
        seg=ref[s:e]
        if set(seg)-set("ACGT"): continue
        cands.append({"start":s,"end":e,"ndiag":nd,"len":amp,
                      "locus":context(s+amp//2),
                      "region":"LSC" if s<88429 else("IRb" if s<118226 else "SSC")})
# dedupe overlapping, keep best
cands.sort(key=lambda c:(-c["ndiag"], c["len"]))
kept=[]
for c in cands:
    if any(not(c["end"]<=k["start"] or c["start"]>=k["end"]) for k in kept): continue
    kept.append(c)
    if len(kept)>=12: break

print(f"Fixed diagnostic sites (galanga vs 5 congeners): {int(DIAG.sum())}")
print(f"Positions conserved across all 8 genomes       : {int(CONS.sum()):,} ({CONS.mean()*100:.1f}%)")
print(f"\nCandidate loci with conserved {PRIMER_LEN}bp flanks + >=2 diagnostic sites: {len(kept)}\n")
print(f"{'#':>2} {'start':>8} {'amp':>5} {'diag':>5} {'region':<5} {'locus':<26}")
for i,c in enumerate(kept,1):
    print(f"{i:>2} {c['start']:>8,} {c['len']:>5} {c['ndiag']:>5} {c['region']:<5} {c['locus']:<26}")

# ── primer3 on top candidates ────────────────────────────────────────
def design(c, nret=3):
    s,e=c["start"],c["end"]
    seq=ref[s:e]
    tgt=[int(x) for x in np.flatnonzero(DIAG[s:e])]
    if not tgt: return []
    lo,hi=min(tgt),max(tgt)
    res=primer3.bindings.design_primers(
        {"SEQUENCE_ID":f"cand_{s}","SEQUENCE_TEMPLATE":seq,
         "SEQUENCE_TARGET":[max(lo-2,1), max(hi-lo+4,6)]},
        {"PRIMER_TASK":"generic","PRIMER_NUM_RETURN":nret,
         "PRIMER_OPT_SIZE":22,"PRIMER_MIN_SIZE":19,"PRIMER_MAX_SIZE":26,
         "PRIMER_OPT_TM":60.0,"PRIMER_MIN_TM":57.0,"PRIMER_MAX_TM":63.0,
         "PRIMER_MAX_TM_DIFF":2.0,
         "PRIMER_MIN_GC":35.0,"PRIMER_MAX_GC":65.0,
         "PRIMER_MAX_POLY_X":4,"PRIMER_MAX_SELF_ANY_TH":45.0,
         "PRIMER_MAX_HAIRPIN_TH":40.0,
         "PRIMER_PRODUCT_SIZE_RANGE":[[250,c["len"]]]})
    out=[]
    for i in range(res.get("PRIMER_PAIR_NUM_RETURNED",0)):
        L=res[f"PRIMER_LEFT_{i}"]; R=res[f"PRIMER_RIGHT_{i}"]
        out.append({
          "locus":c["locus"],"region":c["region"],"abs_start":s,
          "fwd":res[f"PRIMER_LEFT_{i}_SEQUENCE"],"rev":res[f"PRIMER_RIGHT_{i}_SEQUENCE"],
          "fwd_tm":round(res[f"PRIMER_LEFT_{i}_TM"],1),"rev_tm":round(res[f"PRIMER_RIGHT_{i}_TM"],1),
          "fwd_gc":round(res[f"PRIMER_LEFT_{i}_GC_PERCENT"],1),"rev_gc":round(res[f"PRIMER_RIGHT_{i}_GC_PERCENT"],1),
          "product":res[f"PRIMER_PAIR_{i}_PRODUCT_SIZE"],
          "fwd_abs":s+L[0],"rev_abs":s+R[0],
          "ndiag":c["ndiag"],
          "penalty":round(res[f"PRIMER_PAIR_{i}_PENALTY"],3)})
    return out

ALL=[]
for c in kept[:8]:
    ALL += design(c)
ALL.sort(key=lambda p:(-p["ndiag"], p["penalty"]))
print(f"\n{'='*100}\nPRIMER PAIRS (universal flanks, diagnostic interior)\n{'='*100}")
print(f"{'locus':<24}{'prod':>6}{'diag':>5}  {'forward':<26}{'Tm':>5}  {'reverse':<26}{'Tm':>5}")
for p in ALL[:12]:
    print(f"{p['locus'][:23]:<24}{p['product']:>6}{p['ndiag']:>5}  "
          f"{p['fwd']:<26}{p['fwd_tm']:>5}  {p['rev']:<26}{p['rev_tm']:>5}")

json.dump({"candidates":kept,"primers":ALL,
           "n_diag":int(DIAG.sum()),"diag_pos":np.flatnonzero(DIAG).tolist()},
          open(OUT/"primers.json","w"))
print(f"\nSaved primers.json  ({len(ALL)} pairs)")
