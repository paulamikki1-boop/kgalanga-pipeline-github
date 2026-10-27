import os
OUT_DIR = os.environ.get("KG_OUTPUT_DIR", "output")
IN_DIR = os.environ.get("KG_INPUT_DIR", "data")
os.makedirs(OUT_DIR, exist_ok=True)
import json, sys
from Bio import SeqIO

FILES = {
    "KB": IN_DIR + "/GeSeqJob-galanga_KB_GenBank.gb",
    "KS": IN_DIR + "/GeSeqJob-galanga_KS_GenBank.gb",
}

data = {}
for label, path in FILES.items():
    rec = SeqIO.read(path, "genbank")
    genome_len = len(rec.seq)
    cds_list = []
    for feat in rec.features:
        if feat.type != "CDS":
            continue
        gene = feat.qualifiers.get("gene", [feat.qualifiers.get("locus_tag", ["?"])[0]])[0]
        try:
            seq = feat.extract(rec.seq)
        except Exception as e:
            seq = None
        parts = []
        for part in feat.location.parts:
            parts.append({
                "start": int(part.start) + 1,  # 1-based
                "end": int(part.end),
                "strand": part.strand,
            })
        cds_list.append({
            "gene": gene,
            "location_str": str(feat.location),
            "parts": parts,
            "strand": feat.location.strand,
            "length": len(seq) if seq is not None else None,
            "seq": str(seq) if seq is not None else None,
            "note": feat.qualifiers.get("note", []),
            "trans_splicing": "trans_splicing" in feat.qualifiers,
        })
    data[label] = {
        "genome_length": genome_len,
        "n_cds_features": len(cds_list),
        "cds": cds_list,
    }
    print(f"{label}: genome length={genome_len}, CDS features={len(cds_list)}")

# unique gene names
for label in FILES:
    genes = [c["gene"] for c in data[label]["cds"]]
    uniq = sorted(set(genes))
    print(f"{label}: {len(genes)} CDS entries, {len(uniq)} unique gene names")

with open(OUT_DIR + "/cds_data.json", "w") as f:
    json.dump(data, f, indent=1)
print("saved cds_data.json")
