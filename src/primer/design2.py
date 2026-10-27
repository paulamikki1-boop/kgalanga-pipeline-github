#!/usr/bin/env python3
"""Design (b) indel/gel markers with small amplicons, (c) ARMS allele-specific primers."""
import os
OUT_DIR = os.environ.get("KG_OUTPUT_DIR", "output")
IN_DIR = os.environ.get("KG_INPUT_DIR", "data")
os.makedirs(OUT_DIR, exist_ok=True)
import pickle, json
import numpy as np
from pathlib import Path
from Bio.Seq import Seq
import primer3

OUT=Path(OUT_DIR + "/primer")
OUT.mkdir(parents=True, exist_ok=True)
D=pickle.load(open(OUT/"proj.pkl","rb"))
KEYS,M,INS,DESC=D["keys"],D["matrix"],D["inserts"],D["desc"]
GAL,OTH=D["galanga"],D["others"]
RL=134002
A=np.array([M[k][:RL] for k in KEYS])
V=list("ACGT")
gi=[KEYS.index(k) for k in GAL]; oi=[KEYS.index(k) for k in OTH]
gal,oth=A[gi],A[oi]
usable=np.isin(gal,V).all(axis=0)&np.isin(oth,V).all(axis=0)
gal_same=(gal==gal[0]).all(axis=0)
DIAG=usable&gal_same&(oth!=gal[0]).all(axis=0)
CONS=np.isin(A,V).all(axis=0)&(A==A[0]).all(axis=0)
ref=''.join(A[KEYS.index("Kgal_REF")])

exons=[]
for f in D["ref_record"].features:
    if f.type not in ("CDS","gene","tRNA","rRNA"): continue
    g=f.qualifiers.get("gene",["?"])[0]
    for p in f.location.parts: exons.append((int(p.start),int(p.end),g,f.type))
def ctx(pos):
    h=[e for e in exons if e[0]<=pos<e[1]]
    if not h:
        b=[e for e in exons if e[1]<=pos]; a=[e for e in exons if e[0]>pos]
        return f"{max(b,key=lambda e:e[1])[2] if b else '—'}-{min(a,key=lambda e:e[0])[2] if a else '—'} IGS"
    c=[x for x in h if x[3]=="CDS"]; return (c[0][2] if c else h[0][2])

def amp_len(k,s,e):
    return len(''.join(M[k][s:e]).replace('-',''))

print("="*100)
print("(B) INDEL / GEL MARKERS — small amplicons maximising % length difference")
print("="*100)
# scan windows containing a big galanga-vs-congener length difference
gel=[]
for s in range(0, RL-260, 25):
    for size in (140, 200, 260):
        e=s+size
        if not CONS[s:s+22].all() or not CONS[e-22:e].all(): continue
        L={k:amp_len(k,s,e) for k in KEYS}
        g=set(L[k] for k in GAL); o=[L[k] for k in OTH]
        if len(g)!=1: continue
        gl=g.pop()
        sep=min(abs(gl-x) for x in o)
        if sep < 10: continue
        gel.append({"s":s,"e":e,"gal_len":gl,"oth":o,"sep":sep,
                    "pct":sep/gl*100,"locus":ctx(s+size//2),
                    "region":"LSC" if s<88429 else("IRb" if s<118226 else "SSC")})
gel.sort(key=lambda x:-x["pct"])
kept=[]
for c in gel:
    if any(not(c["e"]<=k["s"] or c["s"]>=k["e"]) for k in kept): continue
    kept.append(c)
    if len(kept)>=6: break
print(f"{'locus':<26}{'region':<6}{'galanga':>8}{'congeners':>26}{'min Δ':>7}{'% diff':>8}")
for c in kept:
    print(f"{c['locus'][:25]:<26}{c['region']:<6}{c['gal_len']:>8}{str(c['oth']):>26}{c['sep']:>7}{c['pct']:>7.1f}%")

def p3(s,e,lo,hi,tgt=None):
    seq=ref[s:e]
    args={"SEQUENCE_ID":f"x{s}","SEQUENCE_TEMPLATE":seq}
    if tgt: args["SEQUENCE_TARGET"]=tgt
    try:
        r=primer3.bindings.design_primers(args,{
          "PRIMER_TASK":"generic","PRIMER_NUM_RETURN":1,
          "PRIMER_OPT_SIZE":22,"PRIMER_MIN_SIZE":18,"PRIMER_MAX_SIZE":26,
          "PRIMER_OPT_TM":60,"PRIMER_MIN_TM":56,"PRIMER_MAX_TM":64,
          "PRIMER_MIN_GC":30,"PRIMER_MAX_GC":70,"PRIMER_MAX_POLY_X":5,
          "PRIMER_PRODUCT_SIZE_RANGE":[[lo,hi]]})
        if r.get("PRIMER_PAIR_NUM_RETURNED",0):
            return (r["PRIMER_LEFT_0_SEQUENCE"],r["PRIMER_RIGHT_0_SEQUENCE"],
                    round(r["PRIMER_LEFT_0_TM"],1),round(r["PRIMER_RIGHT_0_TM"],1),
                    r["PRIMER_PAIR_0_PRODUCT_SIZE"],s+r["PRIMER_LEFT_0"][0],
                    s+r["PRIMER_RIGHT_0"][0])
    except Exception as ex: pass
    return None

print(f"\n{'-'*100}\nPrimer pairs for the best gel markers:\n")
GELP=[]
for c in kept[:4]:
    res=p3(c["s"],c["e"],80,c["e"]-c["s"])
    if not res: print(f"  {c['locus']}: primer3 found no acceptable pair"); continue
    f_,r_,ft,rt,prod,fa,ra=res
    rs=ra-len(r_)+1
    lens={k:amp_len(k,fa,rs+len(r_)) for k in KEYS}
    gset=set(lens[k] for k in GAL)
    print(f"  {c['locus']}  ({c['region']})")
    print(f"    F 5'-{f_}-3'  Tm {ft}")
    print(f"    R 5'-{r_}-3'  Tm {rt}")
    print(f"    product sizes: " + "  ".join(
        f"{DESC[k].split()[1][:4]}{'*' if k in GAL else ''}={lens[k]}" for k in KEYS))
    GELP.append({**c,"fwd":f_,"rev":r_,"fwd_tm":ft,"rev_tm":rt,
                 "lens":{DESC[k]:lens[k] for k in KEYS},
                 "gal_uniform":len(gset)==1})

print(f"\n{'='*100}")
print("(C) ARMS / ALLELE-SPECIFIC CANDIDATES — diagnostic SNP at primer 3' end")
print("="*100)
arms=[]
for pos in np.flatnonzero(DIAG):
    if pos<40 or pos>RL-40: continue
    # need conserved 21 bp immediately 5' of the SNP (primer body)
    if not CONS[pos-21:pos].all(): continue
    galb=A[gi][0][pos]; othb=sorted(set(A[oi][:,pos].tolist()))
    body=ref[pos-21:pos]
    primer=body+galb
    tm=primer3.calc_tm(primer)
    if not (55<=tm<=66): continue
    gc=(primer.count('G')+primer.count('C'))/len(primer)*100
    if not (35<=gc<=65): continue
    arms.append({"pos":int(pos),"primer":primer,"tm":round(tm,1),"gc":round(gc,1),
                 "gal_base":galb,"oth_bases":"/".join(othb),"locus":ctx(int(pos)),
                 "region":"LSC" if pos<88429 else("IRb" if pos<118226 else "SSC")})
print(f"Viable ARMS forward primers (3' base = galanga-diagnostic): {len(arms)}\n")
print(f"{chr(39)+chr(39):>0}{'pos':>9} {'locus':<24}{'ARMS primer':<26}{'Tm':>5}{'GC':>6}  gal/others")
for a in arms[:12]:
    print(f"{a['pos']:>9,} {a['locus'][:23]:<24}{a['primer']:<26}{a['tm']:>5}{a['gc']:>6}  {a['gal_base']}/{a['oth_bases']}")

json.dump({"gel":GELP,"arms":arms}, open(OUT/"design2.json","w"), indent=1)
print(f"\nSaved design2.json")
