import os
OUT_DIR = os.environ.get("KG_OUTPUT_DIR", "output")
IN_DIR = os.environ.get("KG_INPUT_DIR", "data")
os.makedirs(OUT_DIR, exist_ok=True)
import re, json
from collections import defaultdict

MISA_PATH = IN_DIR + "/kaempfariatjepr2.fasta.misa"

# true genome lengths from the individually-uploaded fasta files (ground truth, computed directly)
FASTA_LENS = {
    "MK209002.1_Kaempferia_elegans_chloroplast,_complete_genome": 163555,
    "MT473710.1_Kaempferia_rotunda_cultivar_Red_Leaf_chloroplast,_complete_genome": 162630,
    "MT473711.1_Kaempferia_rotunda_cultivar_Silver_Diamonds_chloroplast,_complete_genome": 162875,
    "MW326457.1_Kaempferia_rotunda_chloroplast,_complete_genome": 162391,
    "OP805592.1_Kaempferia_parviflora_chloroplast,_complete_genome": 163075,
}

KEY_MAP = {
    "MK209002.1_Kaempferia_elegans_chloroplast,_complete_genome": "K_elegans",
    "MT473710.1_Kaempferia_rotunda_cultivar_Red_Leaf_chloroplast,_complete_genome": "K_rotunda_RedLeaf",
    "MT473711.1_Kaempferia_rotunda_cultivar_Silver_Diamonds_chloroplast,_complete_genome": "K_rotunda_SilverDiamonds",
    "MW326457.1_Kaempferia_rotunda_chloroplast,_complete_genome": "K_rotunda",
    "OP805592.1_Kaempferia_parviflora_chloroplast,_complete_genome": "K_parviflora",
}

def revcomp(s):
    comp = {"A": "T", "T": "A", "C": "G", "G": "C", "N": "N"}
    return "".join(comp[c] for c in reversed(s))

def canonical_label(motif):
    fwd = min(motif[i:] + motif[:i] for i in range(len(motif)))
    rc = revcomp(motif)
    rcfwd = min(rc[i:] + rc[:i] for i in range(len(rc)))
    return "/".join(sorted([fwd, rcfwd]))

component_re = re.compile(r"\(([ACGTN]+)\)(\d+)")

per_seq = defaultdict(lambda: {
    "n_loci": 0, "n_compound_loci": 0, "n_components": 0,
    "unit_dist": defaultdict(int),
    "motif_totals": defaultdict(int),
})

with open(MISA_PATH) as f:
    f.readline()
    for line in f:
        line = line.rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("\t")
        seq_id, nr, typ, ssr, size, start, end = parts[:7]
        d = per_seq[seq_id]
        d["n_loci"] += 1
        if typ == "c":
            d["n_compound_loci"] += 1
        for motif, n in component_re.findall(ssr):
            u = len(motif)
            d["unit_dist"][u] += 1
            d["motif_totals"][motif] += 1
            d["n_components"] += 1

out = {}
for seq_id, d in per_seq.items():
    key = KEY_MAP[seq_id]
    comp = defaultdict(int)
    for motif, cnt in d["motif_totals"].items():
        comp[canonical_label(motif)] += cnt
    out[key] = {
        "source_file": seq_id.replace("_", " ") + " (split from kaempfariatjepr2.fasta.misa; published NCBI reference accession, verified length from user-uploaded single-sequence fasta)",
        "total_size_bp": FASTA_LENS[seq_id],
        "total_ssrs": d["n_components"],
        "compound_ssrs": d["n_compound_loci"],
        "unit_distribution": {str(k): v for k, v in sorted(d["unit_dist"].items())},
        "motifs": {m: {"total": c} for m, c in d["motif_totals"].items()},
        "motifs_complementary": {m: {"total": c} for m, c in comp.items()},
    }

with open(OUT_DIR + "/corrected_reference.json", "w") as f:
    json.dump(out, f, indent=2)

for k, v in out.items():
    print(k, "size=", v["total_size_bp"], "total_ssrs=", v["total_ssrs"], "compound_loci=", v["compound_ssrs"],
          "unit_dist=", v["unit_distribution"])
print("saved corrected_reference.json")
