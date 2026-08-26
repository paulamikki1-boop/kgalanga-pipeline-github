#!/usr/bin/env python3
"""
Step 1 – Parse GenBank files, extract & canonicalize CDS features.
"""
import sys, re
from pathlib import Path
from collections import defaultdict
from Bio import SeqIO
from Bio.Seq import Seq

UPLOADS = Path("/sessions/tender-vibrant-faraday/mnt/uploads")
FILES = {
    "KS":  UPLOADS / "GeSeqJob-galanga_KS_GenBank.gb",
    "KB":  UPLOADS / "GeSeqJob-galanga_KB_GenBank.gb",
    "Ref": UPLOADS / "K galanga Ref MK209001.gb",
}

def clean_gene_name(g):
    return g.strip().lower()

def translate_careful(seq_obj, table=11):
    try:
        prot = seq_obj.translate(table=table, to_stop=False)
    except Exception:
        return None, True, True, True
    s = str(prot)
    has_int = '*' in s[:-1]
    miss_start = not s.startswith('M')
    miss_stop  = not s.endswith('*')
    return s, has_int, miss_start, miss_stop

def is_clean_orf(seq_obj, table=11):
    if len(seq_obj) % 3 != 0:
        return False
    prot, has_int, miss_start, miss_stop = translate_careful(seq_obj, table)
    if prot is None:
        return False
    return (not has_int) and (not miss_start) and (not miss_stop)

def extract_regions(record):
    regions = {}
    name_map = {
        'large single copy': 'LSC',
        'lsc': 'LSC',
        'inverted repeat b': 'IRb',
        'irb': 'IRb',
        'ir b': 'IRb',
        'small single copy': 'SSC',
        'ssc': 'SSC',
        'inverted repeat a': 'IRa',
        'ira': 'IRa',
        'ir a': 'IRa',
    }
    for feat in record.features:
        if feat.type in ('misc_feature', 'repeat_region'):
            note = ''
            for key in ('note', 'region_name', 'standard_name'):
                if key in feat.qualifiers:
                    note = feat.qualifiers[key][0].lower()
                    break
            for pattern, tag in name_map.items():
                if pattern in note and tag not in regions:
                    loc = feat.location
                    regions[tag] = (int(loc.start), int(loc.end))
                    break
    return regions

def parse_genome(label, path):
    record = SeqIO.read(path, "genbank")
    genome_seq = record.seq
    regions = extract_regions(record)

    gene_cds_map = defaultdict(list)
    for feat in record.features:
        if feat.type != "CDS":
            continue
        gene = feat.qualifiers.get("gene", ["unknown"])[0]
        gene_norm = clean_gene_name(gene)
        try:
            spliced = feat.extract(genome_seq)
        except Exception:
            spliced = None
        annotator = feat.qualifiers.get("annotator", ["?"])[0]
        gene_cds_map[gene_norm].append({
            "gene":      gene_norm,
            "feature":   feat,
            "spliced":   spliced,
            "annotator": annotator,
            "location":  feat.location,
            "len":       len(spliced) if spliced else 0,
        })

    canonical_cds  = {}
    excluded_genes = {}
    flag_notes     = []

    for gene, entries in gene_cds_map.items():
        # Deduplicate IR copies by location string
        unique = {}
        for e in entries:
            loc_str = str(e["location"])
            if loc_str not in unique:
                unique[loc_str] = e
        entries = list(unique.values())

        if len(entries) == 1:
            chosen = entries[0]
        else:
            clean = [e for e in entries if e["spliced"] and is_clean_orf(e["spliced"])]
            if len(clean) == 0:
                chosen = max(entries, key=lambda e: e["len"])
                flag_notes.append(
                    f"[{label}] {gene}: NO candidate has clean ORF. "
                    f"Picked longest ({chosen['len']} bp). MANUAL CHECK NEEDED."
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
                        flag_notes.append(
                            f"[{label}] {gene}: BOTH candidates translate cleanly but differ! "
                            f"Lengths {chosen['len']} vs {alt['len']} bp. "
                            f"Annotators: {chosen['annotator']} vs {alt['annotator']}. "
                            f"Using {chosen['annotator']} version – VERIFY."
                        )
                    else:
                        flag_notes.append(
                            f"[{label}] {gene}: Multiple clean candidates, DNA identical. Kept first."
                        )

        spliced = chosen["spliced"]
        if spliced is None or len(spliced) == 0:
            excluded_genes[gene] = "no sequence extracted"
            continue
        if len(spliced) % 3 != 0:
            excluded_genes[gene] = f"CDS length {len(spliced)} not divisible by 3"
            continue
        canonical_cds[gene] = chosen

    return {
        "label":         label,
        "record":        record,
        "regions":       regions,
        "gene_cds_map":  gene_cds_map,
        "canonical_cds": canonical_cds,
        "excluded_genes":excluded_genes,
        "flag_notes":    flag_notes,
    }

if __name__ == "__main__":
    results = {}
    for label, path in FILES.items():
        print(f"\n{'='*60}")
        print(f"  Parsing {label}: {path.name}")
        print(f"{'='*60}")
        r = parse_genome(label, path)
        results[label] = r

        rec = r["record"]
        print(f"  Genome length: {len(rec.seq):,} bp")
        print(f"  Regions found: {r['regions']}")
        print(f"  Unique protein-coding genes (canonical): {len(r['canonical_cds'])}")
        print(f"  Excluded genes: {len(r['excluded_genes'])}")
        for g, reason in r['excluded_genes'].items():
            print(f"    EXCLUDED: {g} – {reason}")
        if r["flag_notes"]:
            print(f"\n  -- Annotation flags --")
            for note in r["flag_notes"]:
                print(f"  FLAG: {note}")

    print(f"\n{'='*60}")
    print("  Gene-set comparison")
    print(f"{'='*60}")
    ref_genes = set(results["Ref"]["canonical_cds"].keys())
    for label in ("KS", "KB"):
        my_genes = set(results[label]["canonical_cds"].keys())
        missing = ref_genes - my_genes
        extra   = my_genes - ref_genes
        print(f"\n  {label} vs Ref:")
        print(f"    In Ref, missing from {label}: {sorted(missing) or 'none'}")
        print(f"    In {label}, not in Ref:        {sorted(extra) or 'none'}")
        # Also list all canonical genes
    print("\n  KS canonical genes:")
    print("   ", sorted(results["KS"]["canonical_cds"].keys()))
    print("\n  Ref canonical genes:")
    print("   ", sorted(results["Ref"]["canonical_cds"].keys()))

    import pickle
    out = Path("/sessions/tender-vibrant-faraday/mnt/outputs")
    with open(out / "parsed_genomes.pkl", "wb") as fh:
        pickle.dump(results, fh)
    print("\n  Saved parsed_genomes.pkl")
