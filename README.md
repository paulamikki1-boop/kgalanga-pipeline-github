# Kaempferia galanga Chloroplast Genome Analysis Pipeline

Bioinformatic pipeline supporting comparative chloroplast genome analysis of
narrow- and broad-leaf *Kaempferia galanga*, including gap analysis, SSR
(microsatellite) comparison across 8 *Kaempferia* genomes, primer design and
validation, phylogenetic tree construction, and manuscript figure/table
generation.

## Structure

```
src/
├── core/            CDS parsing, RSCU calculation, variant tables, full analysis
├── primer/          Primer design, in-silico PCR, gel/diagnostic validation
├── ssr/             SSR (microsatellite) detection (single genome)
├── ssr_comparison/  8-genome SSR comparison workbook builders
├── tree/            Phylogenetic tree construction
├── results/         Figure/chart generation
├── manuscript_docs/ Manuscript section & report .docx generators (Node.js)
└── cpgavas/         cpGAVAS-based annotation report builder (Node.js)
```

## Requirements

Python 3.10+:

```
pip install -r requirements.txt
```

Node.js (for manuscript `.docx` generation scripts):

```
npm install
```

## Dependencies

- [Biopython](https://biopython.org/) (Biopython License / BSD-3-Clause) —
  Cock, P.J.A. *et al.* (2009) Biopython: freely available Python tools for
  computational molecular biology and bioinformatics. *Bioinformatics*
  25(11), 1422–1423.
- [mappy](https://github.com/lh3/minimap2) (minimap2 Python bindings)
- [primer3-py](https://github.com/libnano/primer3-py)
- numpy, matplotlib, openpyxl
- [docx (Node.js)](https://www.npmjs.com/package/docx) — manuscript `.docx`
  assembly

## Data availability

Raw sequence data and chloroplast genome assemblies are deposited under
their respective NCBI GenBank accession numbers (see manuscript Data
Availability statement) and are not included in this repository. Scripts
here expect local GenBank/FASTA input files as described in code comments.

## License

MIT — see [LICENSE](LICENSE).
