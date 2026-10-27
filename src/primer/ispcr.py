#!/usr/bin/env python3
"""True in-silico PCR: search each genome's real sequence for primer sites."""
import os
OUT_DIR = os.environ.get("KG_OUTPUT_DIR", "output")
IN_DIR = os.environ.get("KG_INPUT_DIR", "data")
os.makedirs(OUT_DIR, exist_ok=True)
import json, re
from pathlib import Path
from Bio import SeqIO
from Bio.Seq import Seq

UP=Path(IN_DIR)
OUT=Path(OUT_DIR + "/primer")
OUT.mkdir(parents=True, exist_ok=True)
G={
 "K. galanga KS (narrow)":UP/"GeSeqJob-galanga_KS_GenBank.gb",
 "K. galanga KB (broad)": UP/"GeSeqJob-galanga_KB_GenBank.gb",
 "K. galanga MK209001":   UP/"K galanga Ref MK209001.gb",
 "K. elegans MK209002":   UP/"MK209002.gb",
 "K. rotunda MW326457":   UP/"Kaempferia rotunda chloroplast.gb",
 "K. rotunda Red Leaf":   UP/"Kaempferia rotunda cultivar Red Leaf chloroplast.gb",
 "K. rotunda Silver Dia.":UP/"Kaempferia rotunda cultivar Silver Diamonds.gb",
 "K. parviflora OP805592":UP/"Kaempferia parviflora chloroplast.gb",
}
GALS={"K. galanga KS (narrow)","K. galanga KB (broad)","K. galanga MK209001"}
SEQ={}
for n,p in G.items():
    s=str(SeqIO.read(p,"genbank").seq).upper()
    SEQ[n]=s+s[:2000]        # circular padding

def find_sites(genome, primer, maxmm=3):
    """Return list of (pos, mismatches) where primer matches plus strand."""
    L=len(primer); hits=[]
    for i in range(len(genome)-L):
        seg=genome[i:i+L]
        mmv=0
        for a,b in zip(seg,primer):
            if a!=b:
                mmv+=1
                if mmv>maxmm: break
        else:
            # 3'-terminal 5 bases must match perfectly for extension
            if seg[-5:]==primer[-5:]: hits.append((i,mmv))
    return hits

def ispcr(genome, fwd, rev, maxmm=3, maxprod=3000):
    rp=str(Seq(rev).reverse_complement())
    F=find_sites(genome,fwd,maxmm); R=find_sites(genome,rp,maxmm)
    prods=[]
    for fp,fm in F:
        for rpos,rm in R:
            if rpos>=fp:
                size=rpos+len(rp)-fp
                if 40<=size<=maxprod: prods.append((size,fm,rm))
    return sorted(set(prods))

ASSAYS=[
 ("ycf1 indel (GEL)",      "TCCTTGCTTTTCTTGCATCGTT","AGCCTCTTCAAAAGGATTATGCT"),
 ("atpH-atpI indel (GEL)", "TGAATCATGTGGGATAAGCTTGC","GTGGAAGGTCATCATTAACTAGCT"),
 ("trnS-trnG IGS (SANGER)","CACTCAGCCATCTCTCCAAACT","AGTGAGACGCAATCAAGATAGGA"),
 ("clpP (SANGER)",         "GAATGGGCCCTTGCAATTCTTT","GCATCAATCATTCGGAGCGTG"),
 ("trnP-UGG (SANGER)",     "CGCTCTGTAGGATTTGAACCCA","ACGTTAGGTTTCAGATGTATCAGA"),
]
report={}
for name,f_,r_ in ASSAYS:
    print("="*92); print(f"{name}")
    print(f"  F 5'-{f_}-3'   R 5'-{r_}-3'")
    print(f"  {'genome':<26}{'products (size, Fmm, Rmm)':<44}{'call'}")
    gsz=set(); osz=set(); clean=True
    rows={}
    for n in G:
        pr=ispcr(SEQ[n],f_,r_)
        # collapse circular duplicates
        uniq=sorted({p[0] for p in pr})
        rows[n]=uniq
        desc=", ".join(f"{s}bp" for s in uniq) if uniq else "NO PRODUCT"
        if len(uniq)>1: clean=False
        tag="galanga" if n in GALS else ""
        print(f"  {n:<26}{desc:<44}{tag}")
        (gsz if n in GALS else osz).update(uniq)
    verdict="—"
    if gsz and osz:
        if not (gsz & osz) and (max(osz)<min(gsz) or min(osz)>max(gsz)):
            verdict=f"DIAGNOSTIC — galanga {sorted(gsz)} vs congeners {sorted(osz)}"
        elif gsz & osz: verdict="NOT diagnostic — sizes overlap"
    elif gsz and not osz: verdict="DIAGNOSTIC by presence/absence (congeners give no product)"
    print(f"  → {verdict}")
    if not clean: print("  → WARNING: multiple products in at least one genome")
    report[name]={"fwd":f_,"rev":r_,"rows":rows,"verdict":verdict,"single_product":clean}

json.dump(report,open(OUT/"ispcr.json","w"),indent=1)
print("\nSaved ispcr.json")
