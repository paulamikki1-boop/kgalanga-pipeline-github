#!/usr/bin/env python3
"""Sliding-window Pi + fixed diagnostic site / indel screen."""
import pickle, json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

OUT = Path("/sessions/tender-vibrant-faraday/mnt/outputs/primer")
D = pickle.load(open(OUT/"proj.pkl","rb"))
KEYS, M, INS = D["keys"], D["matrix"], D["inserts"]
GAL, OTH = D["galanga"], D["others"]
RL = 134002  # LSC+IRb+SSC only; exclude IRa duplicate
ref_seq, ref_rec = D["ref_seq"], D["ref_record"]

A = np.array([M[k][:RL] for k in KEYS])
gi = [KEYS.index(k) for k in GAL]
oi = [KEYS.index(k) for k in OTH]
VALID = set("ACGT")

# ── per-site classification ───────────────────────────────────────────
gal_block = A[gi]; oth_block = A[oi]
gal_ok = np.isin(gal_block, list(VALID)).all(axis=0)
oth_ok = np.isin(oth_block, list(VALID)).all(axis=0)
usable = gal_ok & oth_ok
gal_same = (gal_block == gal_block[0]).all(axis=0)

# diagnostic = galanga monomorphic AND no congener shares the galanga base
diff_from_gal = (oth_block != gal_block[0]).all(axis=0)
DIAG = usable & gal_same & diff_from_gal
diag_pos = np.flatnonzero(DIAG)
print(f"Usable sites            : {usable.sum():,} / {RL:,}")
print(f"Galanga-monomorphic     : {(usable & gal_same).sum():,}")
print(f"FIXED DIAGNOSTIC sites  : {len(diag_pos):,}")

# variable sites overall (for Pi)
def pi_window(win=600, step=200):
    xs, ys = [], []
    n = len(KEYS)
    for s in range(0, RL-win, step):
        blk = A[:, s:s+win]
        col_ok = np.isin(blk, list(VALID)).all(axis=0)
        if col_ok.sum() < win*0.5:
            continue
        sub = blk[:, col_ok]
        diffs = 0; pairs = 0
        for a in range(n):
            for b in range(a+1, n):
                diffs += (sub[a] != sub[b]).sum(); pairs += 1
        xs.append(s + win//2); ys.append(diffs/pairs/sub.shape[1])
    return np.array(xs), np.array(ys)

px, py = pi_window()
print(f"\nPi windows              : {len(px)}  mean Pi = {py.mean():.5f}  max Pi = {py.max():.5f}")

# ── annotate positions with gene context ──────────────────────────────
exons = []
for f in ref_rec.features:
    if f.type not in ("CDS","gene","tRNA","rRNA"): continue
    g = f.qualifiers.get("gene",["?"])[0]
    for p in f.location.parts:
        exons.append((int(p.start), int(p.end), g, f.type))

def context(pos):
    hits = [e for e in exons if e[0] <= pos < e[1]]
    if not hits: 
        # nearest genes
        before = [e for e in exons if e[1] <= pos]
        after  = [e for e in exons if e[0] >  pos]
        b = max(before, key=lambda e:e[1])[2] if before else "—"
        a = min(after,  key=lambda e:e[0])[2] if after  else "—"
        return f"IGS {b}–{a}", "intergenic"
    cds = [h for h in hits if h[3]=="CDS"]
    if cds: return cds[0][2], "CDS"
    return hits[0][2], hits[0][3]

# ── top Pi hotspots ───────────────────────────────────────────────────
order = np.argsort(py)[::-1]
print(f"\n{'='*78}\nTOP 15 HYPERVARIABLE WINDOWS (600 bp, all 7 genomes)\n{'='*78}")
print(f"{'centre':>9} {'Pi':>9}  {'region':<7} {'locus':<32}")
seen=[]
for idx in order:
    c = int(px[idx])
    if any(abs(c-s) < 1200 for s in seen): continue
    seen.append(c)
    reg = "LSC" if c < 88429 else ("IRb" if c < 118226 else "SSC")
    loc, typ = context(c)
    print(f"{c:>9,} {py[idx]:>9.5f}  {reg:<7} {loc:<32}")
    if len(seen) >= 15: break

# ── diagnostic site clustering ────────────────────────────────────────
print(f"\n{'='*78}\nDIAGNOSTIC SITE CLUSTERS (galanga-specific, fixed)\n{'='*78}")
clusters=[]
if len(diag_pos):
    cur=[diag_pos[0]]
    for p in diag_pos[1:]:
        if p - cur[-1] <= 400: cur.append(p)
        else: clusters.append(cur); cur=[p]
    clusters.append(cur)
clusters.sort(key=len, reverse=True)
print(f"{'span':>20} {'n':>4} {'density/kb':>11}  {'region':<6} {'locus':<30}")
for c in clusters[:15]:
    span = c[-1]-c[0]+1
    reg = "LSC" if c[0] < 88429 else ("IRb" if c[0] < 118226 else "SSC")
    loc,_ = context(c[0])
    dens = len(c)/max(span,1)*1000
    print(f"{c[0]:>9,}-{c[-1]:<9,} {len(c):>4} {dens:>11.1f}  {reg:<6} {loc:<30}")

# ── indel screen: galanga vs congeners ────────────────────────────────
print(f"\n{'='*78}\nGALANGA-DIAGNOSTIC INDELS (gel-resolvable candidates)\n{'='*78}")
# deletions relative to ref: runs of '-'
def del_runs(key):
    arr = M[key]; runs=[]; s=None
    for i,ch in enumerate(arr):
        if ch=='-':
            if s is None: s=i
        else:
            if s is not None: runs.append((s,i-s)); s=None
    if s is not None: runs.append((s,len(arr)-s))
    return runs

delmap = {k: dict(del_runs(k)) for k in KEYS}
# candidate: length difference between galanga consensus and ALL congeners >= 10 bp
events=[]
allpos = set()
for k in KEYS:
    allpos |= set(delmap[k].keys()); allpos |= set(INS[k].keys())
for p in sorted(allpos):
    def netlen(k):
        return INS[k].get(p and p, "") and len(INS[k].get(p,"")) or -delmap[k].get(p,0)
    g = [ (len(INS[k].get(p,"")) - delmap[k].get(p,0)) for k in GAL ]
    o = [ (len(INS[k].get(p,"")) - delmap[k].get(p,0)) for k in OTH ]
    if len(set(g)) != 1: continue
    if any(abs(g[0]-x) < 10 for x in o): continue
    if all(x == o[0] for x in o) and abs(g[0]-o[0]) >= 10:
        loc,_ = context(p)
        reg = "LSC" if p < 88429 else ("IRb" if p < 118226 else "SSC")
        events.append((p, g[0], o[0], abs(g[0]-o[0]), reg, loc))
events.sort(key=lambda e:-e[3])
print(f"{'ref pos':>9} {'galanga':>8} {'others':>8} {'Δ bp':>6}  {'region':<6} {'locus':<30}")
for e in events[:20]:
    print(f"{e[0]:>9,} {e[1]:>+8} {e[2]:>+8} {e[3]:>6}  {e[4]:<6} {e[5]:<30}")
print(f"\nTotal galanga-diagnostic indels >=10 bp with uniform congener state: {len(events)}")

json.dump({"diag_pos": diag_pos.tolist(),
           "clusters": [[int(x) for x in c] for c in clusters[:40]],
           "pi_x": px.tolist(), "pi_y": py.tolist(),
           "indels": [[int(e[0]),int(e[1]),int(e[2]),int(e[3]),e[4],e[5]] for e in events]},
          open(OUT/"diagnostics.json","w"))
print("\nSaved diagnostics.json")
