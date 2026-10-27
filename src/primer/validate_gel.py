#!/usr/bin/env python3
import os
OUT_DIR = os.environ.get("KG_OUTPUT_DIR", "output")
IN_DIR = os.environ.get("KG_INPUT_DIR", "data")
os.makedirs(OUT_DIR, exist_ok=True)
import pickle, json
import numpy as np
from pathlib import Path
from Bio.Seq import Seq

OUT=Path(OUT_DIR + "/primer")
OUT.mkdir(parents=True, exist_ok=True)
D=pickle.load(open(OUT/"proj.pkl","rb"))
KEYS,M,DESC=D["keys"],D["matrix"],D["desc"]
GAL,OTH=D["galanga"],D["others"]
G2=json.load(open(OUT/"design2.json"))

def mm(k,start,primer):
    seg=''.join(M[k][start:start+len(primer)])
    if set(seg)-set("ACGT"): return None,seg
    return sum(a!=b for a,b in zip(seg,primer)),seg

for gp in G2["gel"]:
    f_,r_=gp["fwd"],gp["rev"]
    rp=str(Seq(r_).reverse_complement())
    # locate primer sites in reference
    refs=''.join(M["Kgal_REF"])
    fa=refs.find(f_); ra=refs.find(rp)
    if fa<0 or ra<0:
        print(f"{gp['locus']}: could not locate primer sites"); continue
    print("="*88)
    print(f"{gp['locus']}   ({gp['region']})   amplicon spans {fa:,}-{ra+len(rp):,}")
    print(f"  F 5'-{f_}-3'   Tm {gp['fwd_tm']}")
    print(f"  R 5'-{r_}-3'   Tm {gp['rev_tm']}")
    print(f"  {'genome':<32}{'F mm':>6}{'R mm':>6}{'product':>9}   call")
    lens={}
    for k in KEYS:
        fm,_=mm(k,fa,f_); rm,_=mm(k,ra,rp)
        prod=len(''.join(M[k][fa:ra+len(rp)]).replace('-',''))
        lens[k]=prod
        tag="K. galanga" if k in GAL else ""
        print(f"  {DESC[k][:31]:<32}{str(fm):>6}{str(rm):>6}{prod:>9}   {tag}")
    gset={lens[k] for k in GAL}; oset={lens[k] for k in OTH}
    gap=min(abs(g-o) for g in gset for o in oset)
    print(f"  → galanga {sorted(gset)}   congeners {sorted(oset)}   separation {gap} bp "
          f"({gap/max(gset)*100:.0f}% of product)")
    print(f"  → diagnostic: {'YES — ranges do not overlap' if max(oset)<min(gset) or min(oset)>max(gset) else 'NO — ranges overlap'}")
