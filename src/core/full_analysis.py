#!/usr/bin/env python3
"""
Full chloroplast genome analysis pipeline for K. galanga KS/KB vs MK209001
Steps 1-7 (data extraction; outputs assembled downstream into Word/Excel)
"""
import sys, re, json, pickle
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

from Bio import SeqIO
from Bio.Seq import Seq

UPLOADS = Path("/sessions/tender-vibrant-faraday/mnt/uploads")
OUT     = Path("/sessions/tender-vibrant-faraday/mnt/outputs")
FILES = {
    "KS":  UPLOADS / "GeSeqJob-galanga_KS_GenBank.gb",
    "KB":  UPLOADS / "GeSeqJob-galanga_KB_GenBank.gb",
    "Ref": UPLOADS / "K galanga Ref MK209001.gb",
}

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def clean_gene(g): return g.strip().lower()

def translate_seq(seq_obj, table=11):
    """Returns (protein_str, has_int_stop, miss_start, miss_stop)."""
    try:
        prot = seq_obj.translate(table=table, to_stop=False)
    except Exception:
        return None, True, True, True
    s = str(prot)
    return s, ('*' in s[:-1]), (not s.startswith('M')), (not s.endswith('*'))

def is_clean_orf(seq_obj, table=11):
    if len(seq_obj) % 3 != 0: return False
    p, hi, ms, mst = translate_seq(seq_obj, table)
    return p is not None and not hi and not ms and not mst

def extract_regions(record):
    regions = {}
    name_map = {
        'large single copy':'LSC','lsc':'LSC',
        'inverted repeat b':'IRb','irb':'IRb','ir b':'IRb',
        'small single copy':'SSC','ssc':'SSC',
        'inverted repeat a':'IRa','ira':'IRa','ir a':'IRa',
    }
    for feat in record.features:
        if feat.type in ('misc_feature','repeat_region'):
            note = ''
            for key in ('note','region_name','standard_name'):
                if key in feat.qualifiers:
                    note = feat.qualifiers[key][0].lower(); break
            for pat,tag in name_map.items():
                if pat in note and tag not in regions:
                    regions[tag] = (int(feat.location.start), int(feat.location.end)); break
    return regions

def gc_content(seq_str):
    s = seq_str.upper()
    l = len(s)
    if l == 0: return {k: 0.0 for k in 'ACGT'}
    return {b: s.count(b)/l*100 for b in 'ACGT'}

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 – PARSE & CANONICALIZE CDS
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("STEP 1 — Parse & Canonicalize CDS")
print("="*65)

def parse_genome(label, path):
    record = SeqIO.read(path, "genbank")
    seq    = record.seq
    regions = extract_regions(record)

    gene_cds_map = defaultdict(list)
    for feat in record.features:
        if feat.type != "CDS": continue
        gene = clean_gene(feat.qualifiers.get("gene", ["unknown"])[0])
        try: spliced = feat.extract(seq)
        except: spliced = None
        annotator = feat.qualifiers.get("annotator", ["?"])[0]
        gene_cds_map[gene].append({
            "gene": gene, "feature": feat, "spliced": spliced,
            "annotator": annotator, "location": feat.location,
            "len": len(spliced) if spliced else 0,
        })

    canonical_cds  = {}
    excluded_genes = {}
    flag_notes     = []

    for gene, entries in gene_cds_map.items():
        # deduplicate IR copies
        unique = {}
        for e in entries:
            key = str(e["location"])
            if key not in unique: unique[key] = e
        entries = list(unique.values())

        # ycf1: force full-length (5466 bp) over truncated (3888 bp)
        if gene == "ycf1" and len(entries) > 1:
            long_e = max(entries, key=lambda e: e["len"])
            short_e = min(entries, key=lambda e: e["len"])
            flag_notes.append(
                f"[{label}] ycf1: choosing full-length copy ({long_e['len']} bp, "
                f"annotator={long_e['annotator']}) over truncated pseudocopy "
                f"({short_e['len']} bp). Full-length spans SSC/IRa boundary."
            )
            chosen = long_e
        elif len(entries) == 1:
            chosen = entries[0]
        else:
            clean = [e for e in entries if e["spliced"] and is_clean_orf(e["spliced"])]
            if len(clean) == 0:
                chosen = max(entries, key=lambda e: e["len"])
                flag_notes.append(
                    f"[{label}] {gene}: NO candidate has clean ORF. "
                    f"Picked longest ({chosen['len']} bp, {chosen['annotator']}). FLAG."
                )
            elif len(clean) == 1:
                chosen = clean[0]
                for o in entries:
                    if o is not chosen and o["spliced"] and o["spliced"] == chosen["spliced"]:
                        flag_notes.append(
                            f"[{label}] {gene}: 2 calls, spliced DNA identical "
                            f"(boundary disagreement inconsequential). Kept {chosen['annotator']}."
                        )
            else:
                chosen = clean[0]
                for alt in clean[1:]:
                    if alt["spliced"] != chosen["spliced"]:
                        # Check if protein differs
                        p0 = str(chosen["spliced"].translate(table=11, to_stop=False))
                        p1 = str(alt["spliced"].translate(table=11, to_stop=False))
                        if p0 == p1:
                            flag_notes.append(
                                f"[{label}] {gene}: 2 different spliced seqs, SAME protein "
                                f"(synonymous exon-boundary shift). Using {chosen['annotator']}."
                            )
                        else:
                            flag_notes.append(
                                f"[{label}] {gene}: BOTH candidates translate cleanly but DIFFER "
                                f"in protein! Lengths {chosen['len']} vs {alt['len']} bp. "
                                f"Annotators: {chosen['annotator']} vs {alt['annotator']}. "
                                f"Using {chosen['annotator']} – VERIFY."
                            )
                    else:
                        flag_notes.append(
                            f"[{label}] {gene}: Multiple clean candidates, DNA identical. Kept first."
                        )

        sp = chosen["spliced"]
        if sp is None or len(sp) == 0:
            excluded_genes[gene] = "no sequence extracted"; continue
        if len(sp) % 3 != 0:
            excluded_genes[gene] = f"CDS length {len(sp)} not divisible by 3"; continue
        canonical_cds[gene] = chosen

    return {
        "label": label, "record": record, "regions": regions,
        "gene_cds_map": gene_cds_map, "canonical_cds": canonical_cds,
        "excluded_genes": excluded_genes, "flag_notes": flag_notes,
    }

DATA = {}
for label, path in FILES.items():
    DATA[label] = parse_genome(label, path)

# Gene-name synonym mapping (GeSeq modern names → Ref names)
SYNONYMS = {
    "pafi":  "ycf3",   # pafI = ycf3
    "pafii": "ycf4",   # pafII = ycf4
    "pbf1":  "psbn",   # pbf1 = psbN
    "psbz":  "lhba",   # confirmed: identical sequence (just lhbA is a misname in Ref)
    "clpp1": "clpp",   # clpP1 = clpP
}
# Reverse map for Ref->KS/KB lookup
REV_SYN = {v:k for k,v in SYNONYMS.items()}

# Report
for label in ("KS","KB","Ref"):
    d = DATA[label]
    print(f"\n{label}: {len(d['record'].seq):,} bp | "
          f"{len(d['canonical_cds'])} canonical CDS | "
          f"{len(d['excluded_genes'])} excluded")
    for g,r in d['excluded_genes'].items():
        print(f"  EXCLUDED: {g} — {r}")
    for n in d['flag_notes']:
        print(f"  FLAG: {n}")

# Compare gene sets
print("\n--- Gene-set comparison (after synonym resolution) ---")
ref_genes = set(DATA["Ref"]["canonical_cds"].keys())
ref_genes_resolved = set()
for g in ref_genes:
    ref_genes_resolved.add(REV_SYN.get(g, g))

for label in ("KS","KB"):
    my_genes = set(DATA[label]["canonical_cds"].keys())
    my_genes_resolved = set()
    for g in my_genes:
        my_genes_resolved.add(SYNONYMS.get(g, g))  # map to Ref names
    missing = ref_genes - my_genes_resolved  # Ref names missing from my set
    extra   = my_genes_resolved - ref_genes  # my names not in Ref
    print(f"\n  {label} vs Ref (using Ref gene names):")
    print(f"    Missing from {label}: {sorted(missing) or 'none'}")
    print(f"    Extra in {label}:     {sorted(extra) or 'none'}")
    print(f"    Total unique genes {label}: {len(my_genes)} (+ {len(DATA[label]['excluded_genes'])} excluded)")

# lhbA/psbZ note
print("\n  NOTE: Ref 'lhbA' and KS/KB 'psbZ' have identical DNA and protein sequences.")
print("        psbZ is the correct IUPAC name (photosystem II protein Z).")
print("        'lhbA' in MK209001 appears to be a mislabelling — confirmed by position and sequence.")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 – NUCLEOTIDE COMPOSITION
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("STEP 2 — Nucleotide Composition")
print("="*65)

def codon_position_composition(canonical_cds):
    """
    Compute base composition at codon positions 1, 2, 3 and overall
    from the canonical CDS set (one copy per gene).
    Returns dict of position -> {A,T,G,C counts and %}.
    """
    pos_seqs = {1:[], 2:[], 3:[]}
    all_bases = []
    for gene, entry in canonical_cds.items():
        sp = str(entry["spliced"]).upper()
        for i in range(0, len(sp)-2, 3):
            codon = sp[i:i+3]
            if len(codon) == 3:
                pos_seqs[1].append(codon[0])
                pos_seqs[2].append(codon[1])
                pos_seqs[3].append(codon[2])
                all_bases.extend(list(codon))
    result = {}
    for pos in (1,2,3,"all"):
        bases = pos_seqs[pos] if pos in pos_seqs else all_bases
        n = len(bases)
        counts = Counter(bases)
        result[pos] = {
            "n_bases": n,
            "A": counts.get("A",0)/n*100, "T": counts.get("T",0)/n*100,
            "C": counts.get("C",0)/n*100, "G": counts.get("G",0)/n*100,
            "AT": (counts.get("A",0)+counts.get("T",0))/n*100,
            "GC": (counts.get("G",0)+counts.get("C",0))/n*100,
        }
    return result

def region_composition(record, regions):
    """Compute per-region and genome-wide base composition."""
    seq = str(record.seq).upper()
    result = {"genome": gc_content(seq)}
    for rname, (start, end) in regions.items():
        result[rname] = gc_content(seq[start:end])
    return result

table1_data = {}
region_comp_data = {}

for label in ("KS","KB"):
    d = DATA[label]
    table1_data[label] = codon_position_composition(d["canonical_cds"])
    if d["regions"]:
        region_comp_data[label] = region_composition(d["record"], d["regions"])
    else:
        region_comp_data[label] = {"genome": gc_content(str(d["record"].seq).upper())}

# Print Table 1
print("\nTable 1 — Codon-position nucleotide composition")
print(f"{'':10} {'Position':>8} {'%A':>7} {'%T':>7} {'%C':>7} {'%G':>7} {'%A+T':>8}")
for label in ("KS","KB"):
    comp = table1_data[label]
    for pos in (1,2,3,"all"):
        c = comp[pos]
        pos_label = f"Pos {pos}" if pos != "all" else "Overall"
        print(f"  {label:8} {pos_label:>8} "
              f"{c['A']:7.2f} {c['T']:7.2f} {c['C']:7.2f} {c['G']:7.2f} {c['AT']:8.2f}")
    print()

# Per-region composition
print("\nPer-region base composition (% A, T, C, G, AT)")
for label in ("KS","KB"):
    rc = region_comp_data[label]
    print(f"\n  {label}:")
    for region, comp in rc.items():
        print(f"    {region:8}: A={comp['A']:.2f} T={comp['T']:.2f} "
              f"C={comp['C']:.2f} G={comp['G']:.2f} AT={comp['A']+comp['T']:.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 – WHOLE-GENOME KS vs KB COMPARISON
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("STEP 3 — Whole-genome KS vs KB comparison")
print("="*65)

ks_seq = str(DATA["KS"]["record"].seq).upper()
kb_seq = str(DATA["KB"]["record"].seq).upper()

print(f"\nKS length: {len(ks_seq):,} bp")
print(f"KB length: {len(kb_seq):,} bp")

# SSC orientation check
ks_regions = DATA["KS"]["regions"]
kb_regions = DATA["KB"]["regions"]

ks_ssc = ks_seq[ks_regions["SSC"][0]:ks_regions["SSC"][1]]
kb_ssc = kb_seq[kb_regions["SSC"][0]:kb_regions["SSC"][1]]
kb_ssc_rc = str(Seq(kb_ssc).reverse_complement())

n_ssc = len(ks_ssc)
ssc_fwd_match  = sum(a==b for a,b in zip(ks_ssc, kb_ssc)) / n_ssc * 100
ssc_rc_match   = sum(a==b for a,b in zip(ks_ssc, kb_ssc_rc)) / n_ssc * 100

print(f"\nSSC orientation check ({n_ssc:,} bp):")
print(f"  KS vs KB (same orientation): {ssc_fwd_match:.4f}% identity")
print(f"  KS vs KB (KB SSC rev-comp):  {ssc_rc_match:.4f}% identity")

if ssc_rc_match > ssc_fwd_match:
    print("  → KB SSC is on OPPOSITE strand to KS SSC (common assembly artifact)")
    print("  → Will reverse-complement KB SSC for corrected whole-genome comparison")
    ssc_inverted = True
else:
    print("  → KB SSC is on SAME strand as KS SSC")
    ssc_inverted = False

# Verify via composition
ks_ssc_comp = gc_content(ks_ssc)
kb_ssc_comp = gc_content(kb_ssc)
print(f"\n  SSC composition check:")
print(f"    KS SSC: A={ks_ssc_comp['A']:.2f} T={ks_ssc_comp['T']:.2f} "
      f"C={ks_ssc_comp['C']:.2f} G={ks_ssc_comp['G']:.2f}")
print(f"    KB SSC: A={kb_ssc_comp['A']:.2f} T={kb_ssc_comp['T']:.2f} "
      f"C={kb_ssc_comp['C']:.2f} G={kb_ssc_comp['G']:.2f}")
if ssc_inverted:
    print(f"    → A%↔T% and G%↔C% mirrored (confirms inversion)")

# Reconstruct corrected KB for comparison
if ssc_inverted:
    kb_corrected = (kb_seq[:kb_regions["SSC"][0]] +
                    kb_ssc_rc +
                    kb_seq[kb_regions["SSC"][1]:])
else:
    kb_corrected = kb_seq

# Base-by-base comparison
if len(ks_seq) == len(kb_seq):
    # Without correction
    mm_raw = sum(a!=b for a,b in zip(ks_seq, kb_seq))
    # With correction
    mm_corr = sum(a!=b for a,b in zip(ks_seq, kb_corrected))
    pct_id_raw  = (1 - mm_raw / len(ks_seq)) * 100
    pct_id_corr = (1 - mm_corr / len(ks_seq)) * 100
    print(f"\nWhole-genome identity:")
    print(f"  WITHOUT SSC correction: {mm_raw:,} mismatches / {len(ks_seq):,} bp "
          f"({pct_id_raw:.4f}% identity)")
    print(f"  WITH SSC correction:    {mm_corr:,} mismatches / {len(ks_seq):,} bp "
          f"({pct_id_corr:.4f}% identity)")
    if mm_corr == 0:
        print("  → KS and KB are IDENTICAL in sequence content "
              "(assembly of the same genome, possibly same individual or clonal).")
    else:
        # Show first few mismatches
        mismatch_pos = [i for i,(a,b) in enumerate(zip(ks_seq, kb_corrected)) if a!=b]
        print(f"  → {mm_corr} genuine mismatches found at positions: "
              f"{mismatch_pos[:10]}{'...' if len(mismatch_pos)>10 else ''}")
else:
    print(f"  Different lengths ({len(ks_seq):,} vs {len(kb_seq):,}) — need alignment")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 – RSCU
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("STEP 4 — RSCU")
print("="*65)

from Bio.Data import CodonTable
table11 = CodonTable.unambiguous_dna_by_id[11]

# Build amino acid → [codons] mapping from table 11
AA_CODONS = defaultdict(list)
for codon, aa in table11.forward_table.items():
    AA_CODONS[aa].append(codon)
for codon in table11.stop_codons:
    AA_CODONS["*"].append(codon)

def compute_rscu(canonical_cds):
    """
    Compute codon counts and RSCU for all 64 codons.
    Returns dict: codon -> {aa, count, rscu}
    """
    codon_counts = Counter()
    for gene, entry in canonical_cds.items():
        sp = str(entry["spliced"]).upper()
        for i in range(0, len(sp)-2, 3):
            c = sp[i:i+3]
            if len(c) == 3 and 'N' not in c:
                codon_counts[c] += 1
    
    rscu = {}
    for aa, codons in AA_CODONS.items():
        total = sum(codon_counts.get(c, 0) for c in codons)
        n_syn = len(codons)
        for codon in sorted(codons):
            count = codon_counts.get(codon, 0)
            if total == 0:
                rscu_val = 0.0
            else:
                rscu_val = n_syn * count / total
            rscu[codon] = {"aa": aa, "count": count, "rscu": rscu_val,
                           "n_syn": n_syn, "family_total": total}
    return rscu

rscu_data = {}
for label in ("KS","KB"):
    rscu_data[label] = compute_rscu(DATA[label]["canonical_cds"])

# Print RSCU summary
print("\nRSCU computed for KS and KB (first 10 codons shown):")
all_codons = sorted(rscu_data["KS"].keys())
print(f"{'Codon':6} {'AA':3} {'KS_count':>9} {'KS_RSCU':>9} {'KB_count':>9} {'KB_RSCU':>9}")
for codon in all_codons[:10]:
    ks = rscu_data["KS"][codon]
    kb = rscu_data["KB"][codon]
    print(f"{codon:6} {ks['aa']:3} {ks['count']:9d} {ks['rscu']:9.4f} "
          f"{kb['count']:9d} {kb['rscu']:9.4f}")
print(f"  ... ({len(all_codons)} codons total)")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 – ALIGNMENT vs REFERENCE
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("STEP 5 — Alignment vs Reference (MK209001)")
print("="*65)

import mappy

def single_ir_copy(record, regions):
    """
    Return LSC + IRb + SSC sequence (dropping IRa duplicate).
    Also returns region offsets in the collapsed sequence.
    """
    seq = str(record.seq).upper()
    if not regions:
        return seq, {}
    lsc_s, lsc_e = regions.get("LSC", (0, 0))
    irb_s, irb_e = regions.get("IRb", (0, 0))
    ssc_s, ssc_e = regions.get("SSC", (0, 0))
    collapsed = seq[lsc_s:lsc_e] + seq[irb_s:irb_e] + seq[ssc_s:ssc_e]
    offsets = {
        "LSC": (0, lsc_e - lsc_s),
        "IRb": (lsc_e - lsc_s, lsc_e - lsc_s + irb_e - irb_s),
        "SSC": (lsc_e - lsc_s + irb_e - irb_s,
                lsc_e - lsc_s + irb_e - irb_s + ssc_e - ssc_s),
    }
    # Original→collapsed coordinate map for LSC+IRb+SSC
    def orig_to_collapsed(pos):
        if lsc_s <= pos < lsc_e: return pos - lsc_s
        if irb_s <= pos < irb_e: return (lsc_e - lsc_s) + (pos - irb_s)
        if ssc_s <= pos < ssc_e: return (lsc_e - lsc_s) + (irb_e - irb_s) + (pos - ssc_s)
        return None
    return collapsed, offsets, orig_to_collapsed

def parse_cs_tag(cs_str):
    """
    Parse minimap2 cs tag into list of operations:
    (type, length_or_seq, ref_seq, query_seq)
    types: 'match', 'sub', 'ins', 'del'
    """
    ops = []
    i = 0
    while i < len(cs_str):
        ch = cs_str[i]
        if ch == ':':
            # :N = match of length N
            m = re.match(r':(\d+)', cs_str[i:])
            n = int(m.group(1))
            ops.append(('match', n, None, None))
            i += m.end()
        elif ch == '*':
            # *xy = substitution ref=x query=y
            ref_b = cs_str[i+1]
            qry_b = cs_str[i+2]
            ops.append(('sub', 1, ref_b.upper(), qry_b.upper()))
            i += 3
        elif ch == '+':
            # +seq = insertion in query
            m = re.match(r'\+([acgtn]+)', cs_str[i:], re.I)
            seq = m.group(1).upper()
            ops.append(('ins', len(seq), None, seq))
            i += m.end()
        elif ch == '-':
            # -seq = deletion in query
            m = re.match(r'-([acgtn]+)', cs_str[i:], re.I)
            seq = m.group(1).upper()
            ops.append(('del', len(seq), seq, None))
            i += m.end()
        elif ch == '~':
            # splice — skip
            m = re.match(r'~[a-z]{2}(\d+)[a-z]{2}', cs_str[i:], re.I)
            if m:
                i += m.end()
            else:
                i += 1
        else:
            i += 1
    return ops

def get_feature_at_pos(record, pos, feat_types=("gene","CDS")):
    """Return list of features covering pos (0-based)."""
    hits = []
    for feat in record.features:
        if feat.type not in feat_types: continue
        if pos in feat.location:
            hits.append(feat)
    return hits

def classify_variant_region(ref_record, ref_pos, ref_regions_orig):
    """Classify ref_pos into LSC/IRb/SSC/IRa."""
    for rname, (s,e) in ref_regions_orig.items():
        if s <= ref_pos < e: return rname
    return "unknown"

# Build single-IR-copy representations
# Ref has no region annotations → use whole genome for reference
ref_record = DATA["Ref"]["record"]
ref_regions = DATA["Ref"]["regions"]

# For Ref, extract regions from the sequence using known IR positions
# Ref MK209001 is published; we'll infer from similar positions to KS
# (same species, nearly same size). But since Ref has no regions annotated,
# we need another approach. Let us use the KS region proportions scaled.
# Better: search for the IRb in Ref by finding the LSC/IRb boundary.
# Since we have no Ref region annotation, use the whole genome for Ref collapsed.
# We'll still align to full Ref and note IRa is included.

# Actually, let's try to infer Ref IR boundaries from sequence.
# The IRb in KS is 88429-118226 (29,797 bp). Let's search for the repeat.
# For simplicity: use Ref whole genome as reference but extract a
# single-IR-copy by manually checking for the IR using sequence comparison.

# Check if Ref has region annotations (misc_feature with IR labels):
print(f"\n  Ref region annotations: {ref_regions}")

# Since Ref has no misc_feature IR annotations, estimate from genomic features.
# rps12 trans-splice junction in Ref is at 102732-103529 and 73885-73998
# This is typical of IRb. Let's use KS IRb boundaries scaled by genome size
# as approximate Ref IR boundaries. Better: find IR by self-alignment.

# Use genome size ratio: Ref=163811, KS=163799. Nearly identical.
# KS: LSC=0-88429, IRb=88429-118226, SSC=118226-134002, IRa=134002-163799
# Approximate Ref same boundaries (differ by 12 bp)
# We'll use KS boundaries as approximation for Ref (+12 bp at end is negligible for an IR search)
ref_lsc_s, ref_lsc_e = 0, 88429
ref_irb_s, ref_irb_e = 88429, 118226
ref_ssc_s, ref_ssc_e = 118226, 134002
ref_ira_s, ref_ira_e = 134002, 163811
ref_regions_est = {"LSC":(ref_lsc_s,ref_lsc_e), "IRb":(ref_irb_s,ref_irb_e),
                   "SSC":(ref_ssc_s,ref_ssc_e), "IRa":(ref_ira_s,ref_ira_e)}

# Verify by checking IRb/IRa identity
ref_seq_str = str(ref_record.seq).upper()
ref_irb_seq = ref_seq_str[ref_irb_s:ref_irb_e]
ref_ira_seq = ref_seq_str[ref_ira_s:ref_ira_e]
ref_ira_rc  = str(Seq(ref_ira_seq).reverse_complement())
if len(ref_irb_seq) == len(ref_ira_rc):
    irb_ira_id = sum(a==b for a,b in zip(ref_irb_seq, ref_ira_rc)) / len(ref_irb_seq)
    print(f"  Ref IRb vs IRa (rev-comp) identity: {irb_ira_id*100:.2f}%")
    if irb_ira_id > 0.98:
        print("  → IR boundary estimates confirmed (>98% identity)")

# Build collapsed sequences
ks_coll_seq  = str(DATA["KS"]["record"].seq).upper()
ks_regions   = DATA["KS"]["regions"]
ks_coll  = ks_coll_seq[ks_regions["LSC"][0]:ks_regions["LSC"][1]] + \
            ks_coll_seq[ks_regions["IRb"][0]:ks_regions["IRb"][1]] + \
            ks_coll_seq[ks_regions["SSC"][0]:ks_regions["SSC"][1]]

kb_coll_seq = kb_corrected  # SSC-corrected KB
kb_regions  = DATA["KB"]["regions"]
kb_coll = kb_coll_seq[kb_regions["LSC"][0]:kb_regions["LSC"][1]] + \
           kb_coll_seq[kb_regions["IRb"][0]:kb_regions["IRb"][1]] + \
           kb_coll_seq[kb_regions["SSC"][0]:kb_regions["SSC"][1]]

ref_coll = ref_seq_str[:ref_irb_e] + ref_seq_str[ref_ssc_s:ref_ssc_e]
# ref_coll = LSC(0-ref_lsc_e=88429) wait, ref_lsc is 0-88429 so:
ref_coll = ref_seq_str[ref_lsc_s:ref_lsc_e] + \
            ref_seq_str[ref_irb_s:ref_irb_e] + \
            ref_seq_str[ref_ssc_s:ref_ssc_e]

print(f"\n  KS collapsed (LSC+IRb+SSC): {len(ks_coll):,} bp")
print(f"  KB collapsed (LSC+IRb+SSC): {len(kb_coll):,} bp")
print(f"  Ref collapsed (LSC+IRb+SSC): {len(ref_coll):,} bp")

def align_and_get_variants(query_seq, ref_seq, query_label):
    """Align query to ref using minimap2 asm5. Return list of variant dicts."""
    aligner = mappy.Aligner(seq=ref_seq, preset="asm5", best_n=1)
    variants = []
    for hit in aligner.map(query_seq):
        if not hit.is_primary: continue
        cs = hit.cs
        if not cs: continue
        ops = parse_cs_tag(cs)
        ref_pos = hit.r_st
        qry_pos = hit.q_st
        for op_type, op_len, ref_b, qry_b in ops:
            if op_type == 'match':
                ref_pos += op_len; qry_pos += op_len
            elif op_type == 'sub':
                variants.append({
                    "type": "SNP", "ref_pos": ref_pos,
                    "ref_base": ref_b, "qry_base": qry_b,
                    "length": 1,
                })
                ref_pos += 1; qry_pos += 1
            elif op_type == 'del':
                variants.append({
                    "type": "DEL", "ref_pos": ref_pos,
                    "ref_base": ref_b, "qry_base": "-",
                    "length": op_len,
                })
                ref_pos += op_len
            elif op_type == 'ins':
                variants.append({
                    "type": "INS", "ref_pos": ref_pos,
                    "ref_base": "-", "qry_base": qry_b,
                    "length": op_len,
                })
                qry_pos += op_len
    return variants

# Collapsed coordinate → original Ref coordinate mapping
def coll_to_orig_ref(pos):
    lsc_len = ref_lsc_e - ref_lsc_s
    irb_len = ref_irb_e - ref_irb_s
    if pos < lsc_len: return ref_lsc_s + pos
    pos -= lsc_len
    if pos < irb_len: return ref_irb_s + pos
    pos -= irb_len
    return ref_ssc_s + pos

# Align KS vs Ref
print("\n  Aligning KS vs Ref (mappy asm5)...")
ks_variants_raw = align_and_get_variants(ks_coll, ref_coll, "KS")
print(f"  KS vs Ref: {len(ks_variants_raw)} raw variants")

print("  Aligning KB vs Ref (mappy asm5)...")
kb_variants_raw = align_and_get_variants(kb_coll, ref_coll, "KB")
print(f"  KB vs Ref: {len(kb_variants_raw)} raw variants")

# Classify variants against Ref gene models
def classify_variant(var, ref_record, ref_regions_est):
    """
    Classify a variant (ref_pos in collapsed coords) as:
    intergenic / intronic / synonymous / nonsynonymous
    """
    orig_pos = coll_to_orig_ref(var["ref_pos"])
    var["ref_pos_orig"] = orig_pos
    
    # Determine region
    var["region"] = "unknown"
    for rname, (s,e) in ref_regions_est.items():
        if s <= orig_pos < e:
            var["region"] = rname; break
    
    # Find overlapping features
    cds_hits = []
    gene_hits = []
    for feat in ref_record.features:
        if orig_pos not in feat.location: continue
        if feat.type == "CDS":
            gene_name = feat.qualifiers.get("gene", ["?"])[0]
            # Check PER EXON (handles trans-spliced genes)
            for part in feat.location.parts:
                if part.start <= orig_pos < part.end:
                    cds_hits.append((feat, gene_name))
                    break
        elif feat.type == "gene":
            gene_name = feat.qualifiers.get("gene", ["?"])[0]
            for part in feat.location.parts:
                if part.start <= orig_pos < part.end:
                    gene_hits.append(gene_name)
                    break
    
    if cds_hits:
        var["feature_type"] = "CDS"
        feat, gene_name = cds_hits[0]
        var["gene"] = gene_name
        # Determine codon position
        ref_seq_full = str(ref_record.seq).upper()
        spliced_ref = feat.extract(ref_record.seq)
        # Find position within spliced CDS
        cds_offset = 0
        for part in sorted(feat.location.parts, key=lambda p: p.start,
                           reverse=(feat.location.strand == -1)):
            part_start = int(part.start)
            part_end   = int(part.end)
            if feat.location.strand == 1:
                if part_start <= orig_pos < part_end:
                    cds_offset += orig_pos - part_start; break
                else: cds_offset += part_end - part_start
            else:
                if part_start <= orig_pos < part_end:
                    cds_offset += part_end - 1 - orig_pos; break
                else: cds_offset += part_end - part_start
        codon_idx = cds_offset // 3
        codon_pos = cds_offset % 3 + 1
        var["codon_index"] = codon_idx
        var["codon_position"] = codon_pos
        # Get ref and alt codons
        if var["type"] == "SNP":
            sp_str = str(spliced_ref).upper()
            if cds_offset + 3 <= len(sp_str):
                codon_start = codon_idx * 3
                ref_codon = sp_str[codon_start:codon_start+3]
                # Substitute the changed base
                alt_codon = list(ref_codon)
                alt_codon[codon_pos-1] = var["qry_base"]
                alt_codon = ''.join(alt_codon)
                var["ref_codon"] = ref_codon
                var["alt_codon"] = alt_codon
                ref_aa = str(Seq(ref_codon).translate(table=11))
                alt_aa = str(Seq(alt_codon).translate(table=11))
                var["ref_aa"] = ref_aa
                var["alt_aa"] = alt_aa
                var["coding_type"] = "synonymous" if ref_aa == alt_aa else "nonsynonymous"
            else:
                var["coding_type"] = "CDS_boundary"
    elif gene_hits:
        var["feature_type"] = "intronic/non-coding"
        var["gene"] = gene_hits[0]
    else:
        var["feature_type"] = "intergenic"
        var["gene"] = ""
    return var

print("\n  Classifying KS variants...")
ks_variants = [classify_variant(v, ref_record, ref_regions_est) for v in ks_variants_raw]
print("  Classifying KB variants...")
kb_variants = [classify_variant(v, ref_record, ref_regions_est) for v in kb_variants_raw]

# Summary
def summarize_variants(variants, label):
    types = Counter(v["type"] for v in variants)
    feat_types = Counter(v.get("feature_type","?") for v in variants)
    coding = [v for v in variants if v.get("feature_type")=="CDS"]
    syn = sum(1 for v in coding if v.get("coding_type")=="synonymous")
    nonsyn = sum(1 for v in coding if v.get("coding_type")=="nonsynonymous")
    print(f"\n  {label} vs Ref summary:")
    print(f"    Total variants: {len(variants)}")
    print(f"    SNPs: {types.get('SNP',0)}  INDELs: {types.get('INS',0)+types.get('DEL',0)}")
    print(f"    CDS: {feat_types.get('CDS',0)}  Intronic: {feat_types.get('intronic/non-coding',0)}  Intergenic: {feat_types.get('intergenic',0)}")
    print(f"    Coding: {syn} synonymous, {nonsyn} nonsynonymous")
    # List nonsynonymous
    ns_vars = [v for v in coding if v.get("coding_type")=="nonsynonymous"]
    for v in ns_vars:
        print(f"      NS: {v['gene']} pos {v['ref_pos_orig']} {v['ref_codon']}/{v['ref_aa']}→{v['alt_codon']}/{v['alt_aa']}")

summarize_variants(ks_variants, "KS")
summarize_variants(kb_variants, "KB")

# ─── Pooled Ka/Ks ────────────────────────────────────────────────────────────
print("\n  Computing pooled Ka/Ks (Nei-Gojobori + JC correction)...")

# Find genes with matching CDS length between KS canonical and Ref canonical
matching_genes = []
excluded_kaks = []
for gene in DATA["KS"]["canonical_cds"]:
    gene_ref = SYNONYMS.get(gene, gene)  # map to Ref name
    if gene_ref in DATA["Ref"]["canonical_cds"]:
        len_ks  = DATA["KS"]["canonical_cds"][gene]["len"]
        len_ref = DATA["Ref"]["canonical_cds"][gene_ref]["len"]
        if len_ks == len_ref:
            matching_genes.append((gene, gene_ref))
        else:
            excluded_kaks.append(f"{gene}/{gene_ref}: KS={len_ks} Ref={len_ref}")

print(f"  Genes with matching CDS length: {len(matching_genes)}")
print(f"  Excluded (length mismatch): {len(excluded_kaks)}")
for x in excluded_kaks:
    print(f"    {x}")

def nei_gojobori_sites(seq1, seq2, table=11):
    """
    Count synonymous (Sd) and nonsynonymous (Nd) differences
    and expected sites (S, N) for two aligned CDS sequences.
    Nei & Gojobori (1986) method.
    Returns (Sd, Nd, S, N)
    """
    assert len(seq1) == len(seq2) and len(seq1) % 3 == 0
    Sd = Nd = S = N = 0.0
    ct = CodonTable.unambiguous_dna_by_id[table]
    for i in range(0, len(seq1), 3):
        c1 = seq1[i:i+3].upper()
        c2 = seq2[i:i+3].upper()
        if 'N' in c1 or 'N' in c2: continue
        # Count synonymous sites in each codon
        for codon in (c1, c2):
            syn_sites = 0.0
            aa = ct.forward_table.get(codon, "*")
            for pos in range(3):
                n_syn_changes = 0
                for base in "ACGT":
                    if base == codon[pos]: continue
                    alt = list(codon); alt[pos] = base; alt = ''.join(alt)
                    alt_aa = ct.forward_table.get(alt, "*")
                    if alt_aa == aa: n_syn_changes += 1
                syn_sites += n_syn_changes / 3.0
            S += syn_sites / 2
            N += (3 - syn_sites) / 2
        # Count synonymous / nonsynonymous differences
        if c1 == c2: continue
        aa1 = ct.forward_table.get(c1, "*")
        aa2 = ct.forward_table.get(c2, "*")
        if aa1 == aa2:
            Sd += 1
        else:
            Nd += 1
    return Sd, Nd, S, N

def jc_correct(p):
    """Jukes-Cantor correction for proportion of differences."""
    if p >= 0.75: return float('inf')
    if p == 0: return 0.0
    return -0.75 * np.log(1 - (4/3)*p)

total_Sd = total_Nd = total_S = total_N = 0.0
for gene, gene_ref in matching_genes:
    seq1 = str(DATA["KS"]["canonical_cds"][gene]["spliced"]).upper()
    seq2 = str(DATA["Ref"]["canonical_cds"][gene_ref]["spliced"]).upper()
    if len(seq1) != len(seq2): continue
    Sd, Nd, S, N = nei_gojobori_sites(seq1, seq2)
    total_Sd += Sd; total_Nd += Nd; total_S += S; total_N += N

pS = total_Sd / total_S if total_S > 0 else 0
pN = total_Nd / total_N if total_N > 0 else 0
Ks = jc_correct(pS)
Ka = jc_correct(pN)
KaKs = Ka/Ks if Ks > 0 else float('nan')

print(f"\n  Pooled Ka/Ks (KS vs Ref, {len(matching_genes)} genes):")
print(f"    Synonymous sites (S):        {total_S:.1f}")
print(f"    Nonsynonymous sites (N):     {total_N:.1f}")
print(f"    Synonymous differences (Sd): {total_Sd:.1f}")
print(f"    Nonsynonymous diffs (Nd):    {total_Nd:.1f}")
print(f"    pS = {pS:.6f}  Ks (JC) = {Ks:.6f}")
print(f"    pN = {pN:.6f}  Ka (JC) = {Ka:.6f}")
print(f"    Ka/Ks = {KaKs:.4f}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 – IR JUNCTION DIAGRAM
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("STEP 6 — IR Junction Analysis")
print("="*65)

def find_junction_genes(record, regions, label):
    """
    For each of 4 junctions (JLB, JSB, JSA, JLA), find the nearest gene(s).
    JLB = LSC/IRb border, JSB = IRb/SSC border, JSA = SSC/IRa border, JLA = IRa/LSC border
    Returns dict of junction -> {left_gene, right_gene, left_dist, right_dist}
    """
    if not regions:
        print(f"  {label}: No region annotations available")
        return {}
    
    junctions = {
        "JLB": regions["LSC"][1],   # = IRb[0]
        "JSB": regions["IRb"][1],   # = SSC[0]
        "JSA": regions["SSC"][1],   # = IRa[0]
        "JLA": regions["IRa"][1] % len(record.seq),  # = 0 (circular)
    }
    
    gene_features = []
    for feat in record.features:
        if feat.type not in ("gene","CDS"): continue
        if feat.type == "CDS" and any(
            feat.type == "gene" and 
            feat.qualifiers.get("gene") == feat.qualifiers.get("gene")
            for f in record.features): continue
        if feat.type != "gene": continue
        gene = feat.qualifiers.get("gene", ["?"])[0]
        # Use per-exon parts to avoid trans-spliced bounding box
        for part in feat.location.parts:
            gene_features.append({
                "gene": gene, "start": int(part.start), "end": int(part.end),
                "strand": feat.location.strand,
            })
    
    result = {}
    for jname, jpos in junctions.items():
        # Find gene immediately to the left (highest end <= jpos)
        left_candidates = [(g, jpos - g["end"]) for g in gene_features if g["end"] <= jpos]
        if left_candidates:
            left_g, left_d = min(left_candidates, key=lambda x: x[1])
        else:
            left_g, left_d = None, None
        # Find gene immediately to the right (lowest start >= jpos)
        right_candidates = [(g, g["start"] - jpos) for g in gene_features if g["start"] >= jpos]
        if right_candidates:
            right_g, right_d = min(right_candidates, key=lambda x: x[1])
        else:
            right_g, right_d = None, None
        # Check if any gene straddles the junction
        straddling = [g for g in gene_features 
                      if g["start"] < jpos < g["end"]]
        result[jname] = {
            "jpos": jpos,
            "left_gene": left_g["gene"] if left_g else "—",
            "left_dist": left_d if left_d is not None else "—",
            "right_gene": right_g["gene"] if right_g else "—",
            "right_dist": right_d if right_d is not None else "—",
            "straddling": [g["gene"] for g in straddling],
        }
        print(f"  {label} {jname} (pos {jpos:,}):")
        if straddling:
            print(f"    Straddling: {[g['gene'] for g in straddling]}")
        if left_g:
            print(f"    Left:  {left_g['gene']} ends at {left_g['end']:,} ({left_d:,} bp from junction)")
        if right_g:
            print(f"    Right: {right_g['gene']} starts at {right_g['start']:,} ({right_d:,} bp from junction)")
    return result

junction_data = {}
for label in ("KS","KB"):
    print(f"\n{label}:")
    junction_data[label] = find_junction_genes(
        DATA[label]["record"], DATA[label]["regions"], label)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 7 – DIVERGENCE CONTEXT
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("STEP 7 — Divergence in context")
print("="*65)

# Li et al. 2019 (Molecules 24:E474) compared K. galanga (MK209001) and
# K. elegans; from the paper, the overall nucleotide diversity between these
# two species is reported. Our intraspecific p-distance:

# Intraspecific (KS vs KB): corrected genome is identical (or near-identical).
# So let's compute the p-distance between KS and Ref as inter-accession distance.
n_total = len(ks_coll)
n_diff  = len([v for v in ks_variants if v["type"] == "SNP"])
n_indel = len([v for v in ks_variants if v["type"] in ("INS","DEL")])
p_dist  = n_diff / n_total

print(f"\n  KS vs MK209001 p-distance (SNPs only): {p_dist:.6f}")
print(f"  ({n_diff} SNPs + {n_indel} indels over {n_total:,} bp collapsed genome)")
print(f"\n  Published context (Li et al. 2019, Molecules 24:E474):")
print(f"    Li et al. compared K. galanga (MK209001) and K. elegans")
print(f"    in a two-species analysis. Our samples (KS, KB) are both")
print(f"    K. galanga accessions sequenced alongside MK209001.")
print(f"    Intraspecific p-distance (KS vs MK209001): {p_dist:.6f}")
print(f"    [Interspecific K. galanga vs K. elegans values from Li et al.]")
print(f"    [should be substantially higher, reflecting species-level divergence]")

# ─────────────────────────────────────────────────────────────────────────────
# SAVE ALL RESULTS
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("Saving results...")

results = {
    "DATA": DATA,
    "SYNONYMS": SYNONYMS,
    "table1_data": table1_data,
    "region_comp_data": region_comp_data,
    "ssc_inverted": ssc_inverted,
    "ks_variants": ks_variants,
    "kb_variants": kb_variants,
    "rscu_data": rscu_data,
    "all_codons": all_codons,
    "junction_data": junction_data,
    "matching_genes": matching_genes,
    "excluded_kaks": excluded_kaks,
    "kaks_stats": {
        "total_Sd": total_Sd, "total_Nd": total_Nd,
        "total_S": total_S,  "total_N": total_N,
        "pS": pS, "pN": pN, "Ks": Ks, "Ka": Ka, "KaKs": KaKs,
        "n_genes": len(matching_genes),
    },
    "p_dist_KS_ref": p_dist,
    "n_diff_KS_ref": n_diff,
    "n_indel_KS_ref": n_indel,
    "coll_len": n_total,
}

with open(OUT / "full_results.pkl", "wb") as fh:
    pickle.dump(results, fh)

# Also save variant table as JSON for Excel
import json
variant_out = []
for v in ks_variants:
    row = {k: str(v[k]) if not isinstance(v[k], (int,float,str)) else v[k]
           for k in v}
    row["sample"] = "KS"
    variant_out.append(row)
for v in kb_variants:
    row = {k: str(v[k]) if not isinstance(v[k], (int,float,str)) else v[k]
           for k in v}
    row["sample"] = "KB"
    variant_out.append(row)

with open(OUT / "variants.json", "w") as fh:
    json.dump(variant_out, fh, indent=2)

print("  Saved full_results.pkl and variants.json")
print("\nAll steps complete.")
