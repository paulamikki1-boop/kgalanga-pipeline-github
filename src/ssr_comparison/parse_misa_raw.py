import re, json
from collections import defaultdict

path = "/sessions/serene-wonderful-dirac/mnt/uploads/kaempfariatjepr2.fasta.misa"

# reverse-complement collapse table (same canonical grouping MISA itself uses)
def revcomp(s):
    comp = {"A": "T", "T": "A", "C": "G", "G": "C"}
    return "".join(comp[c] for c in reversed(s))

def canonical_rotations(motif):
    # all cyclic rotations of the motif and its reverse complement
    rots = set()
    n = len(motif)
    for i in range(n):
        rots.add(motif[i:] + motif[:i])
    rc = revcomp(motif)
    for i in range(n):
        rots.add(rc[i:] + rc[:i])
    return rots

component_re = re.compile(r"\(([ACGTN]+)\)(\d+)")

per_seq = defaultdict(lambda: {
    "n_loci": 0, "n_compound_loci": 0, "n_components": 0,
    "unit_dist": defaultdict(int),
    "motif_totals": defaultdict(int),  # motif string (as written) -> total repeat-count instances... actually -> count of loci (occurrences)
})

overall_unit_dist = defaultdict(int)
overall_motif_count = defaultdict(int)  # motif -> number of occurrences (loci/components)
total_components = 0
total_loci = 0
total_compound_loci = 0

rows = []
with open(path) as f:
    header = f.readline()
    for line in f:
        line = line.rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("\t")
        seq_id, ssr_nr, ssr_type, ssr_str, size, start, end = parts[:7]
        rows.append((seq_id, ssr_type, ssr_str))
        total_loci += 1
        is_compound = ssr_type == "c"
        if is_compound:
            total_compound_loci += 1
            per_seq[seq_id]["n_compound_loci"] += 1
        per_seq[seq_id]["n_loci"] += 1
        comps = component_re.findall(ssr_str)
        for motif, nrep in comps:
            unit = len(motif)
            per_seq[seq_id]["unit_dist"][unit] += 1
            per_seq[seq_id]["motif_totals"][motif] += 1
            overall_unit_dist[unit] += 1
            overall_motif_count[motif] += 1
            total_components += 1
            per_seq[seq_id]["n_components"] += 1

print("Total loci (rows):", total_loci)
print("Total compound loci:", total_compound_loci)
print("Total components (should match published 'Total number of identified SSRs' = 1158):", total_components)
print("Overall unit distribution (should match 865/144/27/108/12/2):", dict(sorted(overall_unit_dist.items())))
print()
for seq_id in sorted(per_seq):
    d = per_seq[seq_id]
    print(seq_id)
    print("  loci:", d["n_loci"], "compound loci:", d["n_compound_loci"], "components:", d["n_components"])
    print("  unit_dist:", dict(sorted(d["unit_dist"].items())))

# Build complementary (canonical, revcomp-collapsed) totals per sequence
def canonical_label(motif):
    rots = canonical_rotations(motif)
    # pick the lexicographically smallest rotation as canonical representative for grouping key,
    # but present using MISA's own "A/T"-style forward/revcomp pair label built from the motif itself
    fwd = min(motif[i:] + motif[:i] for i in range(len(motif)))
    rc = revcomp(motif)
    rcfwd = min(rc[i:] + rc[:i] for i in range(len(rc)))
    pair = tuple(sorted([fwd, rcfwd]))
    return pair

per_seq_complementary = defaultdict(lambda: defaultdict(int))
for seq_id, d in per_seq.items():
    for motif, cnt in d["motif_totals"].items():
        pair = canonical_label(motif)
        label = "/".join(pair)
        per_seq_complementary[seq_id][label] += cnt

out = {
    "total_loci": total_loci,
    "total_compound_loci": total_compound_loci,
    "total_components": total_components,
    "overall_unit_dist": dict(overall_unit_dist),
    "per_seq": {
        seq_id: {
            "n_loci": d["n_loci"],
            "n_compound_loci": d["n_compound_loci"],
            "n_components": d["n_components"],
            "unit_dist": dict(d["unit_dist"]),
            "motif_totals": dict(d["motif_totals"]),
            "motif_complementary": dict(per_seq_complementary[seq_id]),
        }
        for seq_id, d in per_seq.items()
    },
}
with open("/sessions/serene-wonderful-dirac/mnt/outputs/misa_raw_split.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nsaved misa_raw_split.json")
