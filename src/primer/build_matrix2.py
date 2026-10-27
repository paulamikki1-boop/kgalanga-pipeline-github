#!/usr/bin/env python3
"""Full-genome to full-genome projection onto MK209001 coordinates."""
import os
OUT_DIR = os.environ.get("KG_OUTPUT_DIR", "output")
IN_DIR = os.environ.get("KG_INPUT_DIR", "data")
os.makedirs(OUT_DIR, exist_ok=True)
import re, pickle
from pathlib import Path
from Bio import SeqIO
from Bio.Seq import Seq
import mappy, numpy as np

UP  = Path(IN_DIR)
OUT = Path(OUT_DIR + "/primer")
OUT.mkdir(parents=True, exist_ok=True)
GENOMES = {
 "Kgal_KS":     (UP/"GeSeqJob-galanga_KS_GenBank.gb", "K. galanga KS (narrow)"),
 "Kgal_KB":     (UP/"GeSeqJob-galanga_KB_GenBank.gb", "K. galanga KB (broad)"),
 "Kgal_REF":    (UP/"K galanga Ref MK209001.gb",      "K. galanga MK209001"),
 "Krot_MW":     (UP/"Kaempferia rotunda chloroplast.gb", "K. rotunda MW326457"),
 "Krot_Red":    (UP/"Kaempferia rotunda cultivar Red Leaf chloroplast.gb","K. rotunda Red Leaf"),
 "Krot_Silver": (UP/"Kaempferia rotunda cultivar Silver Diamonds.gb","K. rotunda Silver Diamonds"),
 "Kpar":        (UP/"Kaempferia parviflora chloroplast.gb","K. parviflora OP805592"),
}
GAL = ["Kgal_KS","Kgal_KB","Kgal_REF"]; OTH=["Krot_MW","Krot_Red","Krot_Silver","Kpar"]

recs={}
for k,(p,d) in GENOMES.items():
    r=SeqIO.read(p,"genbank"); recs[k]={"rec":r,"seq":str(r.seq).upper(),"desc":d}

REF="Kgal_REF"; ref_full=recs[REF]["seq"]; FL=len(ref_full)
# MK209001 boundaries (verified earlier by IRb/IRa self-identity >98%)
RREG={"LSC":(0,88429),"IRb":(88429,118226),"SSC":(118226,134002),"IRa":(134002,FL)}

def parse_cs(cs):
    ops=[];i=0
    while i<len(cs):
        c=cs[i]
        if c==':': m=re.match(r':(\d+)',cs[i:]);ops.append(('=',int(m.group(1)),'',''));i+=m.end()
        elif c=='*': ops.append(('*',1,cs[i+1].upper(),cs[i+2].upper()));i+=3
        elif c=='+': m=re.match(r'\+([acgtnACGTN]+)',cs[i:]);s=m.group(1).upper();ops.append(('+',len(s),'',s));i+=m.end()
        elif c=='-': m=re.match(r'-([acgtnACGTN]+)',cs[i:]);s=m.group(1).upper();ops.append(('-',len(s),s,''));i+=m.end()
        else: i+=1
    return ops

# align FULL genome to FULL reference; keep all non-overlapping alignments
aligner = mappy.Aligner(seq=ref_full, preset="asm10", best_n=5)
MATRIX={}; INSERTS={}
print(f"Reference {REF}: {FL:,} bp (full, both IRs)\n")
for k in GENOMES:
    arr=np.full(FL,'N',dtype='<U1'); ins={}
    if k==REF:
        arr[:]=list(ref_full)
    else:
        q=recs[k]["seq"]
        # try both orientations of the query, keep all alignments
        hits=sorted(aligner.map(q,cs=True), key=lambda h:-(h.r_en-h.r_st))
        used=0
        for h in hits:
            if not h.cs: continue
            # skip if this ref span already ~filled
            span=arr[h.r_st:h.r_en]
            if (span!='N').mean() > 0.5: continue
            used+=1
            rp,qp=h.r_st,h.q_st
            for t,n,rb,qb in parse_cs(h.cs):
                if t=='=':
                    seg=q[qp:qp+n] if h.strand==1 else str(Seq(q[qp:qp+n]).reverse_complement())
                    if h.strand==1: arr[rp:rp+n]=list(q[qp:qp+n])
                    else: arr[rp:rp+n]=list(seg)
                    rp+=n; qp+=n
                elif t=='*': arr[rp]=qb; rp+=1; qp+=1
                elif t=='-': arr[rp:rp+n]='-'; rp+=n
                elif t=='+': ins[rp]=qb; qp+=n
        cov=float((arr!='N').sum())/FL*100
        print(f"  {k:14} {used} block(s)  coverage {cov:6.2f}%  insertions {len(ins)}")
    MATRIX[k]=arr; INSERTS[k]=ins

# sanity: divergence by region, galanga vs each congener
print(f"\n{'genome':<14}" + "".join(f"{r:>10}" for r in ("LSC","IRb","SSC","IRa")))
V=set("ACGT"); ref_arr=MATRIX[REF]
for k in OTH:
    row=f"  {k:<12}"
    for r,(s,e) in RREG.items():
        a,b=MATRIX[k][s:e],ref_arr[s:e]
        ok=np.isin(a,list(V))&np.isin(b,list(V))
        row+=f"{(a[ok]!=b[ok]).mean()*100:>9.2f}%" if ok.sum() else f"{'—':>10}"
    print(row)

pickle.dump({"keys":list(GENOMES),"desc":{k:v[1] for k,v in GENOMES.items()},
             "matrix":MATRIX,"inserts":INSERTS,"ref_seq":ref_full,"regions":RREG,
             "coll_len":FL,"galanga":GAL,"others":OTH,"ref_record":recs[REF]["rec"]},
            open(OUT/"proj.pkl","wb"))
print(f"\nSaved projection: {FL:,} positions x {len(GENOMES)} genomes")
