"""Cross-check hand-written analysis code against Biopython reference implementations.

The analysis scripts run at import time, so the functions under test are sliced out
of the source files and executed in isolation.

Run from the repository root:  python -m unittest discover -s tests -v
"""
import io
import itertools
import unittest
import warnings
from pathlib import Path

import numpy as np
from Bio import Phylo
from Bio.Data import CodonTable
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor

warnings.simplefilter("ignore")
from Bio.codonalign import codonseq  # noqa: E402  (experimental module)

SRC = Path(__file__).resolve().parent.parent / "src"


def _slice(path, start, end, namespace):
    text = (SRC / path).read_text(encoding="utf-8").replace("\r\n", "\n")
    exec(text[text.index(start):text.index(end)], namespace)
    return namespace


class NeiGojoboriTest(unittest.TestCase):
    """full_analysis.nei_gojobori_sites vs Biopython's per-codon NG86 counts."""

    def test_all_sense_codon_pairs_match_biopython(self):
        ns = _slice("core/full_analysis.py", "def nei_gojobori_sites", "def jc_correct",
                    {"CodonTable": CodonTable, "permutations": itertools.permutations})
        table = CodonTable.unambiguous_dna_by_id[11]
        mismatches = []
        for a, b in itertools.permutations(sorted(table.forward_table), 2):
            sd, nd, _, _ = ns["nei_gojobori_sites"](a, b)
            ref_sd, ref_nd = codonseq._count_diff_NG86(a, b, codon_table=table)
            if abs(sd - ref_sd) > 1e-9 or abs(nd - ref_nd) > 1e-9:
                mismatches.append((a, b))
        self.assertEqual(mismatches, [])


class NeighbourJoiningTest(unittest.TestCase):
    """build_tree.nj vs Bio.Phylo.TreeConstruction NJ."""

    @staticmethod
    def _splits(tree):
        names = {t.name for t in tree.get_terminals()}
        out = set()
        for clade in tree.get_nonterminals():
            leaves = frozenset(t.name for t in clade.get_terminals())
            if 2 <= len(leaves) <= len(names) - 2:
                out.add(frozenset([leaves, frozenset(names - leaves)]))
        return out

    def test_topology_and_length_match_biopython(self):
        ns = _slice("tree/build_tree.py", "def nj(", "def splits_of", {"np": np})
        for seed in range(25):
            labels = [f"t{i}" for i in range(8)]
            pts = np.random.RandomState(seed).rand(8, 3)
            d = np.sqrt(((pts[:, None] - pts[None]) ** 2).sum(-1))
            mine = Phylo.read(io.StringIO(ns["nj"](d, labels)), "newick")
            lower = [[float(x) for x in d[i, : i + 1]] for i in range(8)]
            ref = DistanceTreeConstructor().nj(DistanceMatrix(labels, lower))
            self.assertEqual(self._splits(mine), self._splits(ref), f"seed {seed}")
            length = lambda t: sum(c.branch_length or 0 for c in t.find_clades())
            self.assertAlmostEqual(length(mine), length(ref), places=6)


class RscuTest(unittest.TestCase):
    """RSCU = (synonymous codons in family) * count / family total (Sharp & Li 1987)."""

    def test_formula_and_family_sums(self):
        ns = _slice("core/full_analysis.py", "def compute_rscu", "rscu_data = {}", {})
        table = CodonTable.unambiguous_dna_by_id[11]
        from collections import Counter, defaultdict
        aa_codons = defaultdict(list)
        for codon, aa in table.forward_table.items():
            aa_codons[aa].append(codon)
        for codon in table.stop_codons:
            aa_codons["*"].append(codon)
        ns.update(Counter=Counter, AA_CODONS=aa_codons)
        cds = {"g": {"spliced": "ATG" + "CTG" * 3 + "CTT" + "TAA"}}
        rscu = ns["compute_rscu"](cds)
        self.assertAlmostEqual(rscu["CTG"]["rscu"], 6 * 3 / 4)   # Leu: 6 codons, 3 of 4
        self.assertAlmostEqual(rscu["CTT"]["rscu"], 6 * 1 / 4)
        self.assertAlmostEqual(rscu["ATG"]["rscu"], 1.0)           # single-codon family
        for aa, codons in aa_codons.items():
            used = sum(rscu[c]["count"] for c in codons)
            if used:
                self.assertAlmostEqual(sum(rscu[c]["rscu"] for c in codons), len(codons))


if __name__ == "__main__":
    unittest.main()
