#!/usr/bin/env python3
"""8-genome projection onto MK209001 coords, with correct minus-strand handling."""
import re, pickle
from pathlib import Path
from Bio import SeqIO
from Bio.Seq import Seq
import mappy, numpy as np

UP  = Path("/sessions/tender-vibrant-faraday/mnt/uploads")
OUT = Path("/sessions/tender-vibrant-faraday/mnt/outputs/primer")
G = {
 "Kgal_KS":     (UP/"GeSeqJob-galanga_KS_GenBank.gb","K. galanga KS (narrow-leaf)"),
 "Kgal_KB":     (UP/"GeSeqJob-galanga_KB_GenBank.gb","K. galanga KB (broad-leaf)"),
 "Kgal_REF":    (UP/"K galanga Ref MK209001.gb","K. galanga MK209001"),
 "Kele":        (UP/"MK209002.gb","K. elegans MK209002"),
 "Krot_MW":     (UP/"Kaempferia rotunda chloroplast.gb","K. rotunda MW326457"),
 "Krot_Red":    (UP/"Kaempferia rotunda cultivar Red Leaf chloroplast.gb","K. rotunda cv Red Leaf"),
 "Krot_Silver": (UP/"Kaempferia rotunda cultivar Silver Diamonds.gb","K. rotunda cv Silver Diamonds"),
 "Kpar":        (UP/"Kaempferia parviflora chloroplast.gb","K. parviflora OP805592"),
}
GAL=["Kgal_KS","Kgal_KB","Kgal_REF"]
OTH=["Kele","Krot_MW","Krot_Red","Krot_Silver","Kpar"]

recs={k:{"rec":SeqIO.read(p,"genbank")} for k,(p,d) in G.items()}
for k in recs: recs[k]["seq"]=str(recs[k]["rec"].seq).upper()

REF="Kgal_REF"; ref=recs[REF]["seq"]; FL=len(ref)
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

al = mappy.Aligner(seq=ref, preset="asm10", best_n=10)
MATRIX={}; INSERTS={}
print(f"Reference {REF}: {FL:,} bp\n")
for k in G:
    arr=np.full(FL,'N',dtype='<U1'); ins={}
    if k==REF:
        arr[:]=list(ref)
    else:
        q=recs[k]["seq"]; qrc=str(Seq(q).reverse_complement()); LQ=len(q)
        blocks=0
        for h in sorted(al.map(q,cs=True), key=lambda h:-(h.r_en-h.r_st)):
            if not h.cs: continue
            if (arr[h.r_st:h.r_en]!='N').mean() > 0.5: continue
            blocks+=1
            # For minus-strand hits, walk the reverse-complemented query.
            work = q if h.strand==1 else qrc
            qp   = h.q_st if h.strand==1 else (LQ - h.q_en)
            rp   = h.r_st
            for t,n,rb,qb in parse_cs(h.cs):
                if t=='=':
                    arr[rp:rp+n]=list(work[qp:qp+n]); rp+=n; qp+=n
                elif t=='*':
                    arr[rp]=qb; rp+=1; qp+=1
                elif t=='-':
                    arr[rp:rp+n]='-'; rp+=n
                elif t=='+':
                    ins[rp]=qb; qp+=n
        print(f"  {k:14} {blocks} block(s)  cov {float((arr!='N').sum())/FL*100:6.2f}%  ins {len(ins)}")
    MATRIX[k]=arr; INSERTS[k]=ins

# ── validation ────────────────────────────────────────────────────────
V=list("ACGT"); RL=134002
A=np.array([MATRIX[k][:RL] for k in G])
keys=list(G)
ok=np.isin(A,V).all(axis=0); sub=A[:,ok]
print(f"\nUsable columns: {ok.sum():,} / {RL:,}")
print("\nPairwise divergence (%), LSC+IRb+SSC:")
print(f"{'':14}"+"".join(f"{k.split('_')[0][:6]:>9}" for k in keys))
for a,ka in enumerate(keys):
    row=f"  {ka:<12}"
    for b,kb in enumerate(keys):
        row += "        —" if a==b else f"{(sub[a]!=sub[b]).mean()*100:>9.3f}"
    print(row)

print("\nRegion divergence vs K. galanga reference (%):")
print(f"{'genome':<14}"+"".join(f"{r:>9}" for r in RREG))
for k in OTH:
    row=f"  {k:<12}"
    for r,(s,e) in RREG.items():
        x,y=MATRIX[k][s:e],MATRIX[REF][s:e]
        m=np.isin(x,V)&np.isin(y,V)
        row+=f"{(x[m]!=y[m]).mean()*100:>9.3f}" if m.sum() else f"{'—':>9}"
    print(row)

pickle.dump({"keys":keys,"desc":{k:v[1] for k,v in G.items()},"matrix":MATRIX,
             "inserts":INSERTS,"ref_seq":ref,"regions":RREG,"coll_len":FL,
             "galanga":GAL,"others":OTH,"ref_record":recs[REF]["rec"]},
            open(OUT/"proj.pkl","wb"))
print("\nSaved proj.pkl")
