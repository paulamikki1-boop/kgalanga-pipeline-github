#!/usr/bin/env python3
"""Rebuild the Kaempferia phylogeny from the 8-genome whole-plastome alignment."""
import pickle, json, itertools
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

OUT=Path("/sessions/tender-vibrant-faraday/mnt/outputs/tree")
D=pickle.load(open("/sessions/tender-vibrant-faraday/mnt/outputs/primer/proj.pkl","rb"))
KEYS,M,DESC=D["keys"],D["matrix"],D["desc"]
RL=134002                     # LSC + IRb + SSC (IRa duplicate excluded)

NAME={"Kgal_KS":"K. galanga KS (narrow)","Kgal_KB":"K. galanga KB (broad)",
      "Kgal_REF":"K. galanga MK209001","Kele":"K. elegans MK209002",
      "Krot_MW":"K. rotunda MW326457","Krot_Red":"K. rotunda cv Red Leaf",
      "Krot_Silver":"K. rotunda cv Silver Diamonds","Kpar":"K. parviflora OP805592"}
TAXA=[NAME[k] for k in KEYS]; n=len(TAXA)

A=np.array([M[k][:RL] for k in KEYS])
ok=np.isin(A,list("ACGT")).all(axis=0)
aln=A[:,ok]
N=aln.shape[1]
var=(aln!=aln[0]).any(axis=0)
print(f"Alignment: {n} taxa x {N:,} sites ({int(var.sum()):,} variable, "
      f"{N-int(var.sum()):,} invariant)")

# ── site-pattern compression ──────────────────────────────────────────
cols=[''.join(aln[:,i]) for i in np.flatnonzero(var)]
pat=Counter(cols)
pats=list(pat.keys()); wts=np.array([pat[p] for p in pats],dtype=float)
PM=np.array([list(p) for p in pats]).T          # n x npat
n_inv=N-int(var.sum())
print(f"Distinct variable site patterns: {len(pats):,}")

def dist_matrix(w, model="K2P"):
    """Pairwise distance from weighted variable patterns + invariant sites."""
    Dm=np.zeros((n,n))
    tot=w.sum()+n_inv
    PUR=set("AG"); 
    for i,j in itertools.combinations(range(n),2):
        a,b=PM[i],PM[j]
        diff=a!=b
        if not diff.any():
            Dm[i,j]=Dm[j,i]=0.0; continue
        # transitions vs transversions
        ti=np.array([ (x in PUR)==(y in PUR) for x,y in zip(a,b) ])
        P=w[diff&ti].sum()/tot          # transition proportion
        Q=w[diff&~ti].sum()/tot         # transversion proportion
        if model=="p":
            d=P+Q
        elif model=="JC69":
            p=P+Q
            d=-0.75*np.log(1-4*p/3) if p<0.75 else 3.0
        else:                            # K2P
            t1=1-2*P-Q; t2=1-2*Q
            d=0.5*np.log(1/t1)+0.25*np.log(1/t2) if (t1>0 and t2>0) else 3.0
        Dm[i,j]=Dm[j,i]=d
    return Dm

def nj(Dm, labels):
    """Neighbour-joining; returns newick with branch lengths."""
    Dm=Dm.copy().astype(float); nodes=list(labels); m=len(nodes)
    blen={l:0.0 for l in labels}
    while m>2:
        r=Dm.sum(axis=1)
        Q=np.full((m,m),np.inf)
        for i in range(m):
            for j in range(i+1,m):
                Q[i,j]=Q[j,i]=(m-2)*Dm[i,j]-r[i]-r[j]
        i,j=np.unravel_index(np.argmin(Q),Q.shape)
        if i>j: i,j=j,i
        di=0.5*Dm[i,j]+(r[i]-r[j])/(2*(m-2))
        dj=Dm[i,j]-di
        di,dj=max(di,0.0),max(dj,0.0)
        newlab=f"({nodes[i]}:{di:.8f},{nodes[j]}:{dj:.8f})"
        newrow=np.array([0.5*(Dm[i,k]+Dm[j,k]-Dm[i,j]) for k in range(m)])
        keep=[k for k in range(m) if k not in (i,j)]
        newD=np.zeros((m-1,m-1))
        newD[:m-2,:m-2]=Dm[np.ix_(keep,keep)]
        newD[m-2,:m-2]=newD[:m-2,m-2]=newrow[keep]
        Dm=newD; nodes=[nodes[k] for k in keep]+[newlab]; m-=1
    return f"({nodes[0]}:{Dm[0,1]:.8f},{nodes[1]}:0.0);"

def splits_of(Dm, labels):
    """Return set of non-trivial splits from an NJ tree (via dendropy)."""
    import dendropy
    tr=dendropy.Tree.get(data=nj(Dm,labels), schema="newick",
                         preserve_underscores=True)
    tr.encode_bipartitions()
    S=set()
    for e in tr.edges():
        if e.head_node is None or e.head_node.is_leaf(): continue
        leaves=frozenset(l.taxon.label for l in e.head_node.leaf_iter())
        comp=frozenset(set(labels)-leaves)
        if 2<=len(leaves)<=len(labels)-2:
            S.add(frozenset([leaves,comp]))
    return S

SAFE=[t.replace(" ","_").replace("(","").replace(")","").replace(".","") for t in TAXA]
print("\nDistance matrices:")
for model in ("p","JC69","K2P"):
    Dm=dist_matrix(wts,model)
    print(f"\n  {model} distances (x100):")
    print("        "+"".join(f"{s.split('_')[1][:6]:>9}" for s in SAFE))
    for i,s in enumerate(SAFE):
        print(f"  {s[:16]:<18}"+"".join("        —" if i==j else f"{Dm[i,j]*100:>9.4f}" for j in range(n)))

DK=dist_matrix(wts,"K2P")
best_newick=nj(DK,SAFE)

# ── bootstrap ─────────────────────────────────────────────────────────
rng=np.random.default_rng(20260803)
B=1000
obs=splits_of(DK,SAFE)
cnt=Counter()
for b in range(B):
    w=rng.multinomial(int(wts.sum()), wts/wts.sum()).astype(float)
    try:
        for s in splits_of(dist_matrix(w,"K2P"),SAFE): cnt[s]+=1
    except Exception: pass
print(f"\nBootstrap: {B} replicates (multinomial resampling of {len(pats):,} site patterns)")

json.dump({"newick":best_newick,"taxa":TAXA,"safe":SAFE,
           "nsites":int(N),"nvar":int(var.sum()),"npat":len(pats),
           "dist_K2P":DK.tolist(),
           "boot":{ "|".join(sorted("+".join(sorted(x)) for x in s)):c/B*100
                    for s,c in cnt.items()},
           "obs_splits":["|".join(sorted("+".join(sorted(x)) for x in s)) for s in obs]},
          open(OUT/"tree.json","w"),indent=1)
print("\nNewick (K2P NJ):"); print(best_newick)
print("\nSupport for splits in the NJ tree:")
for s in obs:
    lab=" | ".join(sorted(", ".join(sorted(x)) for x in s))
    key="|".join(sorted("+".join(sorted(x)) for x in s))
    print(f"  {cnt[s]/B*100:5.1f}%   {lab[:110]}")
