#!/usr/bin/env python3
"""
Faithful re-implementation of the MISA (MIcroSAtellite identification tool)
algorithm (Beier et al. 2017 / Thiel et al. 2003), validated against a
known-correct MISA-web run before being trusted on new sequences.

Algorithm: for unit sizes 1..6, in increasing order, find all runs where a
k-mer repeats consecutively >= min_repeats[k] times. Positions already
claimed by a smaller unit size are not reconsidered by larger unit sizes
(this is what prevents e.g. (A)8 from also being called a dinucleotide).
Adjacent SSRs separated by <= max_interruption bp are flagged as compound.
"""
import re
from collections import Counter, defaultdict

THRESH = {1:8, 2:5, 3:4, 4:3, 5:3, 6:3}
MAX_INTERRUPT = 100

def find_ssrs(seq):
    seq = seq.upper()
    n = len(seq)
    claimed = bytearray(n)          # 0 = free, 1 = claimed
    hits = []                       # (start0, end0_exclusive, unit, copies)

    for k in range(1, 7):
        min_rep = THRESH[k]
        min_len = k * min_rep
        i = 0
        while i <= n - k:
            if claimed[i]:
                i += 1; continue
            unit = seq[i:i+k]
            if 'N' in unit:
                i += 1; continue
            # count consecutive repeats of this unit starting at i
            j = i + k
            copies = 1
            while j + k <= n and seq[j:j+k] == unit:
                j += k; copies += 1
            length = copies * k
            if copies >= min_rep:
                # check primitivity: reject if unit itself has a smaller period
                # that would already have been claimed by an earlier (smaller) k
                is_primitive = True
                for d in range(1, k):
                    if k % d == 0 and unit == unit[:d] * (k//d):
                        is_primitive = False; break
                if is_primitive and not any(claimed[i:j]):
                    hits.append((i, j, unit, copies))
                    for p in range(i, j): claimed[p] = 1
                    i = j
                    continue
            i += 1
    hits.sort(key=lambda h: h[0])
    # compound formation flag
    compound_flags = [False]*len(hits)
    for a in range(len(hits)-1):
        gap = hits[a+1][0] - hits[a][1]
        if 0 <= gap <= MAX_INTERRUPT:
            compound_flags[a] = True
            compound_flags[a+1] = True
    return hits, compound_flags

def collapse_motif(unit):
    """Return canonical complementary-collapsed representation e.g. A/T, AT/AT."""
    comp = str.maketrans("ACGT","TGCA")
    rc = unit.translate(comp)[::-1]
    # cyclic rotations of unit and its reverse complement; pick lexicographically
    def rotations(s):
        return [s[i:]+s[:i] for i in range(len(s))]
    cands = sorted(set(rotations(unit)) | set(rotations(rc)))
    fwd = min(rotations(unit))
    rev = min(rotations(rc))
    a,b = sorted([fwd,rev])
    return f"{a}/{b}"

def summarize(hits):
    by_size = Counter(len(h[2]) for h in hits)
    motif_strand = Counter(h[2] for h in hits)
    motif_comp = Counter(collapse_motif(h[2]) for h in hits)
    return {
        "total": len(hits),
        "by_unit_size": dict(sorted(by_size.items())),
        "motif_strand": dict(motif_strand),
        "motif_complementary": dict(motif_comp),
    }

if __name__ == "__main__":
    import sys
    from pathlib import Path
    from Bio import SeqIO

    # ---- VALIDATION against known-correct KS MISA-web output ----
    ks = str(SeqIO.read("/sessions/tender-vibrant-faraday/mnt/uploads/GeSeqJob-galanga_KS_GenBank.gb","genbank").seq)
    hits, comp = find_ssrs(ks)
    s = summarize(hits)
    print("="*70); print("VALIDATION: KS genome vs known MISA-web result"); print("="*70)
    print(f"  My total SSRs: {s['total']}   (MISA-web reported: 239)")
    print(f"  My unit-size distribution: {s['by_unit_size']}")
    print(f"  Expected (MISA-web):        {{1: 177, 2: 31, 3: 6, 4: 21, 5: 3, 6: 1}}")
    n_compound = sum(1 for c in comp if c)
    print(f"  My compound-flagged SSRs: {n_compound}   (MISA-web reported: 56)")
    match = s['by_unit_size'] == {1:177,2:31,3:6,4:21,5:3,6:1}
    print(f"\n  EXACT MATCH: {match}")
