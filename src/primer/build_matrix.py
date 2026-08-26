#!/usr/bin/env python3
"""Build a 7-genome character matrix in MK209001 coordinates."""
import re, pickle, json
from pathlib import Path
from Bio import SeqIO
from Bio.Seq import Seq
import mappy, numpy as np

UP  = Path("/sessions/tender-vibrant-faraday/mnt/uploads")
OUT = Path("/sessions/tender-vibrant-faraday/mnt/outputs/primer")

GENOMES = {
 "Kgal_KS":      (UP/"GeSeqJob-galanga_KS_GenBank.gb",            "K. galanga KS (narrow)"),
 "Kgal_KB":      (UP/"GeSeqJob-galanga_KB_GenBank.gb",            "K. galanga KB (broad)"),
 "Kgal_REF":     (UP/"K galanga Ref MK209001.gb",                 "K. galanga MK209001"),
 "Krot_MW":      (UP/"Kaempferia rotunda chloroplast.gb",         "K. rotunda MW326457"),
 "Krot_Red":     (UP/"Kaempferia rotunda cultivar Red Leaf chloroplast.gb",  "K. rotunda Red Leaf"),
 "Krot_Silver":  (UP/"Kaempferia rotunda cultivar Silver Diamonds.gb",       "K. rotunda Silver Diamonds"),
 "Kpar":         (UP/"Kaempferia parviflora chloroplast.gb",      "K. parviflora OP805592"),
}

GALANGA = ["Kgal_KS","Kgal_KB","Kgal_REF"]
OTHERS  = ["Krot_MW","Krot_Red","Krot_Silver","Kpar"]

# ── load ──────────────────────────────────────────────────────────────
recs = {}
for k,(p,desc) in GENOMES.items():
    r = SeqIO.read(p, "genbank")
    recs[k] = {"rec": r, "seq": str(r.seq).upper(), "desc": desc}
    print(f"{k:14} {len(r.seq):>8,} bp   {desc}")

# ── detect IR by self reverse-complement alignment ────────────────────
def detect_ir(seq):
    """Return (irb_start, irb_end, ira_start, ira_end) or None."""
    rc = str(Seq(seq).reverse_complement())
    al = mappy.Aligner(seq=seq, preset="asm5", best_n=20)
    best = None
    for h in al.map(rc):
        blen = h.r_en - h.r_st
        if blen < 15000: continue
        # position of this block in the forward genome (query was rc)
        L = len(seq)
        f_st, f_en = L - h.q_en, L - h.q_st   # map rc coords back to fwd
        if abs(f_st - h.r_st) < 1000: continue   # self-match, skip
        lo_s, lo_e = min((h.r_st,h.r_en),(f_st,f_en))
        hi_s, hi_e = max((h.r_st,h.r_en),(f_st,f_en))
        if best is None or blen > best[0]:
            best = (blen, lo_s, lo_e, hi_s, hi_e)
    if best is None: return None
    _, irb_s, irb_e, ira_s, ira_e = best
    return irb_s, irb_e, ira_s, ira_e

REGIONS = {}
# KS/KB have GeSeq annotations
for k in ("Kgal_KS","Kgal_KB"):
    r = recs[k]["rec"]
    reg = {}
    for f in r.features:
        if f.type in ("misc_feature","repeat_region"):
            n = (f.qualifiers.get("note",[""])[0]).lower()
            for pat,tag in [("large single copy","LSC"),("inverted repeat b","IRb"),
                            ("small single copy","SSC"),("inverted repeat a","IRa")]:
                if pat in n and tag not in reg:
                    reg[tag] = (int(f.location.start), int(f.location.end))
    REGIONS[k] = reg
REGIONS["Kgal_REF"] = {"LSC":(0,88429),"IRb":(88429,118226),
                       "SSC":(118226,134002),"IRa":(134002,163811)}

for k in OTHERS:
    ir = detect_ir(recs[k]["seq"])
    L = len(recs[k]["seq"])
    if ir:
        irb_s, irb_e, ira_s, ira_e = ir
        REGIONS[k] = {"LSC":(0,irb_s),"IRb":(irb_s,irb_e),
                      "SSC":(irb_e,ira_s),"IRa":(ira_s,L)}
        print(f"{k:14} IR detected: LSC 0-{irb_s:,}  IRb {irb_s:,}-{irb_e:,}  "
              f"SSC {irb_e:,}-{ira_s:,}  IRa {ira_s:,}-{L:,}")
    else:
        REGIONS[k] = None
        print(f"{k:14} IR detection FAILED — using whole genome")

# ── collapse to LSC+IRb+SSC ───────────────────────────────────────────
def collapse(k):
    s = recs[k]["seq"]; reg = REGIONS[k]
    if not reg: return s
    if k == "Kgal_KB":   # SSC inverted in this assembly
        ss,se = reg["SSC"]
        ssc = str(Seq(s[ss:se]).reverse_complement())
    else:
        ssc = s[reg["SSC"][0]:reg["SSC"][1]]
    return s[reg["LSC"][0]:reg["LSC"][1]] + s[reg["IRb"][0]:reg["IRb"][1]] + ssc

COLL = {k: collapse(k) for k in GENOMES}
for k,v in COLL.items(): print(f"  collapsed {k:14} {len(v):>8,} bp")

REF = "Kgal_REF"
ref_seq = COLL[REF]
RL = len(ref_seq)

# ── project each genome onto reference coordinates ────────────────────
def parse_cs(cs):
    ops=[]; i=0
    while i < len(cs):
        c=cs[i]
        if c==':':
            m=re.match(r':(\d+)',cs[i:]); ops.append(('=',int(m.group(1)),'','')); i+=m.end()
        elif c=='*':
            ops.append(('*',1,cs[i+1].upper(),cs[i+2].upper())); i+=3
        elif c=='+':
            m=re.match(r'\+([acgtnACGTN]+)',cs[i:]); s=m.group(1).upper()
            ops.append(('+',len(s),'',s)); i+=m.end()
        elif c=='-':
            m=re.match(r'-([acgtnACGTN]+)',cs[i:]); s=m.group(1).upper()
            ops.append(('-',len(s),s,'')); i+=m.end()
        else: i+=1
    return ops

aligner = mappy.Aligner(seq=ref_seq, preset="asm10", best_n=1)
MATRIX = {}     # key -> np.array of chars length RL
INSERTS = {}    # key -> {ref_pos: inserted_seq}

for k in GENOMES:
    arr = np.full(RL, 'N', dtype='<U1')
    ins = {}
    if k == REF:
        arr[:] = list(ref_seq)
    else:
        q = COLL[k]
        got = False
        for h in aligner.map(q, cs=True):
            if not h.is_primary or not h.cs: continue
            got = True
            rp, qp = h.r_st, h.q_st
            for t,n,rb,qb in parse_cs(h.cs):
                if t=='=':
                    arr[rp:rp+n] = list(q[qp:qp+n]); rp+=n; qp+=n
                elif t=='*':
                    arr[rp] = qb; rp+=1; qp+=1
                elif t=='-':
                    arr[rp:rp+n] = '-'; rp+=n
                elif t=='+':
                    ins[rp] = qb; qp+=n
        if not got: print(f"  WARNING: no primary alignment for {k}")
    MATRIX[k]  = arr
    INSERTS[k] = ins
    cov = float((arr!='N').sum())/RL*100
    print(f"  projected {k:14} coverage {cov:6.2f}%   insertions {len(ins)}")

np.save(OUT/"matrix.npy", np.array([MATRIX[k] for k in GENOMES]))
with open(OUT/"proj.pkl","wb") as f:
    pickle.dump({"keys":list(GENOMES), "desc":{k:v[1] for k,v in GENOMES.items()},
                 "matrix":MATRIX, "inserts":INSERTS, "ref_seq":ref_seq,
                 "regions":REGIONS, "coll_len":RL,
                 "galanga":GALANGA, "others":OTHERS,
                 "ref_record":recs[REF]["rec"]}, f)
print(f"\nSaved projection: {RL:,} reference positions x {len(GENOMES)} genomes")
