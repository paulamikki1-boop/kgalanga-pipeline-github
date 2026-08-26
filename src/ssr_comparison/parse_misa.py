import re, json

def parse_misa(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    d = {}
    m = re.search(r'Sequence source file:\s*"([^"]+)"', text)
    d["source_file"] = m.group(1) if m else None
    d["total_size_bp"] = int(re.search(r"Total size of examined sequences \(bp\):\s*(\d+)", text).group(1))
    d["total_ssrs"] = int(re.search(r"Total number of identified SSRs:\s*(\d+)", text).group(1))
    d["compound_ssrs"] = int(re.search(r"Number of SSRs present in compound formation:\s*(\d+)", text).group(1))

    # unit-size distribution
    dist = {}
    dist_block = re.search(r"Unit size\tNumber of SSRs\n(.*?)\n\n", text, re.S).group(1)
    for line in dist_block.strip().splitlines():
        u, n = line.split("\t")
        dist[int(u)] = int(n)
    d["unit_distribution"] = dist

    def parse_table(header_pat):
        block = re.search(header_pat + r"\n\n(Repeats\t.*?)(?:\n\n|\Z)", text, re.S)
        lines = block.group(1).strip().splitlines()
        header = lines[0].split("\t")  # Repeats,3,4,...,17,total
        lengths = header[1:-1]
        rows = {}
        for line in lines[1:]:
            parts = line.split("\t")
            motif = parts[0]
            vals = parts[1:]
            # pad
            while len(vals) < len(header) - 1:
                vals.append("-")
            per_len = {}
            for L, v in zip(lengths, vals[:-1]):
                v = v.strip()
                per_len[L] = int(v) if v not in ("", "-") else 0
            total_v = vals[-1].strip() if len(vals) >= len(header) - 1 else ""
            # total may be blank if row shorter than header; recompute from per_len if needed
            total = int(total_v) if total_v not in ("", "-") else sum(per_len.values())
            rows[motif] = {"per_length": per_len, "total": total}
        return rows

    d["motifs"] = parse_table(r"Frequency of identified SSR motifs\n-+")
    d["motifs_complementary"] = parse_table(r"Frequency of classified repeat types \(considering sequence complementary\)\n-+")
    return d

files = {
    "KB": "/sessions/serene-wonderful-dirac/mnt/outputs/misa_parse/KB SSR.statistics",
    "KS": "/sessions/serene-wonderful-dirac/mnt/uploads/KSt9cuoa.fasta.statistics",
    "KG_ref": "/sessions/serene-wonderful-dirac/mnt/outputs/misa_parse/KG REF SSR.statistics",
    "K_parviflora": "/sessions/serene-wonderful-dirac/mnt/Kaempferiaparviflora/Kaempferiaparviflora.fasta.statistics",
    "K_rotunda": "/sessions/serene-wonderful-dirac/mnt/Kaempferiarotunda/Kaempferiarotunda.fasta.statistics",
    "K_rotunda_RedLeaf": "/sessions/serene-wonderful-dirac/mnt/KaempferiarotundaRedLeafchloroplast/KaempferiarotundaRedLeafchloroplast.fasta.statistics",
    "K_rotunda_SilverDiamonds": "/sessions/serene-wonderful-dirac/mnt/KaempferiarotundaSilverDiamonds/KaempferiarotundaSilverDiamonds.fasta.statistics",
}

data = {k: parse_misa(v) for k, v in files.items()}

for k, v in data.items():
    print(k, "source=", v["source_file"], "size=", v["total_size_bp"], "total_ssrs=", v["total_ssrs"],
          "compound=", v["compound_ssrs"], "unit_dist=", v["unit_distribution"])

with open("/sessions/serene-wonderful-dirac/mnt/outputs/misa_parsed.json", "w") as f:
    json.dump(data, f, indent=2)
print("saved json")
