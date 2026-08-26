#!/usr/bin/env python3
"""In-silico validation: primer-site conservation + amplicon discrimination."""
import pickle, json
import numpy as np
from pathlib import Path
from Bio.Seq import Seq

OUT=Path("/sessions/tender-vibrant-faraday/mnt/outputs/primer")
D=pickle.load(open(OUT/"proj.pkl","rb"))
P=json.load(open(OUT/"primers.json"))
KEYS,M,DESC=D["keys"],D["matrix"],D["desc"]
GAL,OTH=D["galanga"],D["others"]
RL=134002
A=np.array([M[k][:RL] for k in KEYS])

def genome_str(k): return ''.join(M[k][:RL])
GS={k:genome_str(k) for k in KEYS}

def site_ok(k,start,length):
    """Is the primer-binding site free of gaps/N in genome k?"""
    seg=M[k][start:start+length]
    return not (set(seg.tolist()) - set("ACGT"))

def mismatches(k, start, primer, revcomp=False):
    seg=''.join(M[k][start:start+len(primer)])
    if set(seg)-set("ACGT"): return None
    return sum(a!=b for a,b in zip(seg, primer))

# pick best pair per locus
best={}
for p in P["primers"]:
    key=p["locus"]
    if key not in best or p["penalty"]<best[key]["penalty"]: best[key]=p
cands=sorted(best.values(), key=lambda p:(-p["ndiag"], p["penalty"]))

print("="*104)
print("IN-SILICO VALIDATION — primer-site conservation across all 8 genomes")
print("="*104)

results=[]
for p in cands[:6]:
    fs,fl=p["fwd_abs"],len(p["fwd"])
    rs,rl=p["rev_abs"]-len(p["rev"])+1,len(p["rev"])
    # reverse primer binds the minus strand; compare its revcomp to plus strand
    rev_plus=str(Seq(p["rev"]).reverse_complement())
    print(f"\n{p['locus']}  ({p['region']}, product {p['product']} bp, {p['ndiag']} diagnostic sites)")
    print(f"  F 5'-{p['fwd']}-3'  Tm {p['fwd_tm']}  GC {p['fwd_gc']}%")
    print(f"  R 5'-{p['rev']}-3'  Tm {p['rev_tm']}  GC {p['rev_gc']}%")
    print(f"  {'genome':<32}{'F mm':>6}{'R mm':>6}{'amplicon':>10}{'diffs vs galanga':>18}")
    gal_amp=None; rows=[]
    ok_all=True
    for k in KEYS:
        fm=mismatches(k,fs,p["fwd"]); rm=mismatches(k,rs,rev_plus)
        amp=''.join(M[k][fs:rs+rl])
        ampc=amp.replace('-','')
        if k==GAL[0]: gal_amp=ampc
        nd=None
        if gal_amp is not None and len(ampc)==len(gal_amp):
            nd=sum(a!=b for a,b in zip(ampc,gal_amp))
        rows.append((k,fm,rm,len(ampc),nd))
        if k in OTH and (fm is None or rm is None or fm>2 or rm>2): ok_all=False
    for k,fm,rm,L,nd in rows:
        tag="galanga" if k in GAL else ""
        fmS="—" if fm is None else str(fm); rmS="—" if rm is None else str(rm)
        ndS="—" if nd is None else str(nd)
        print(f"  {DESC[k][:31]:<32}{fmS:>6}{rmS:>6}{L:>10}{ndS:>18}  {tag}")
    # discrimination: min diffs between galanga and any congener
    gal_amps={k:''.join(M[k][fs:rs+rl]).replace('-','') for k in GAL}
    oth_amps={k:''.join(M[k][fs:rs+rl]).replace('-','') for k in OTH}
    gal_set=set(gal_amps.values())
    intra = 0 if len(gal_set)==1 else max(
        sum(a!=b for a,b in zip(x,y)) for x in gal_set for y in gal_set if len(x)==len(y))
    mind=None
    for ok_,ov in oth_amps.items():
        gv=gal_amps[GAL[0]]
        d=sum(a!=b for a,b in zip(gv,ov)) + abs(len(gv)-len(ov))
        mind=d if mind is None else min(mind,d)
    print(f"  → intra-galanga variation: {intra}    min separation from any congener: {mind}")
    results.append({**p,"min_sep":mind,"intra":intra,"primer_sites_ok":ok_all})

json.dump(results, open(OUT/"validated.json","w"), indent=1)
print(f"\nSaved validated.json")
