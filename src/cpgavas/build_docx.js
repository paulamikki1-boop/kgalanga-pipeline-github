const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle } = require("docx");
const fs = require("fs");

const FONT = "Times New Roman";

function body(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 200, line: 360 },
    children: [new TextRun({ text, font: FONT, size: 24, ...opts })],
  });
}

// runs: array of either a string (plain) or {t: string, i: true} for italic
function bodyRuns(runs) {
  return new Paragraph({
    spacing: { after: 200, line: 360 },
    children: runs.map((r) =>
      typeof r === "string"
        ? new TextRun({ text: r, font: FONT, size: 24 })
        : new TextRun({ text: r.t, font: FONT, size: 24, italics: true })
    ),
  });
}

function noteBox(lines) {
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC" },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC" },
      left: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC" },
      right: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC" },
    },
    rows: [
      new TableRow({
        children: [
          new TableCell({
            shading: { type: ShadingType.CLEAR, fill: "F2F2F2" },
            margins: { top: 150, bottom: 150, left: 150, right: 150 },
            children: lines.map(
              (t) =>
                new Paragraph({
                  spacing: { after: 100, line: 300 },
                  children: [
                    new TextRun({ text: t, font: FONT, size: 22, italics: true, color: "555555" }),
                  ],
                })
            ),
          }),
        ],
      }),
    ],
  });
}

function refEntry(text) {
  return new Paragraph({
    indent: { left: 720, hanging: 720 },
    spacing: { after: 160, line: 300 },
    children: [new TextRun({ text, font: FONT, size: 22 })],
  });
}

const doc = new Document({
  sections: [
    {
      properties: {},
      children: [
        new Paragraph({
          spacing: { after: 60 },
          children: [
            new TextRun({
              text: "Methods Addition: Chloroplast Genome Annotation via CPGAVAS2",
              bold: true,
              font: FONT,
              size: 28,
            }),
          ],
        }),
        new Paragraph({
          spacing: { after: 240 },
          children: [
            new TextRun({
              text: "Optimized Chloroplast Isolation and Comparative Analysis of Complete Chloroplast Genomes in Narrow- and Broad-Leaf Kaempferia galanga",
              italics: true,
              font: FONT,
              size: 22,
            }),
          ],
        }),

        noteBox([
          "How to use this document: the two subsections below are written to be pasted into the Materials and Methods section, in place of (or immediately after) the current “Chloroplast genomes were annotated using GeSeq…” sentence, since CPGAVAS2 is the tool that actually produced the annotation, repeat, and codon-usage results you now have. Bracketed text is a placeholder for you to fill in. This box and the note near the references are not manuscript text — delete them before submission.",
        ]),
        body(""),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 120, after: 120 },
          children: [new TextRun({ text: "Chloroplast Genome Annotation and Codon Usage Analysis", bold: true, font: FONT, size: 26 })],
        }),
        bodyRuns([
          "Following genome assembly, the complete chloroplast genomes of narrow-leaf (KS) and broad-leaf (KB) ",
          { t: "Kaempferia galanga" },
          " were each annotated using CPGAVAS2, an updated version of the Chloroplast Genome Annotation, Visualization, Analysis and GenBank Submission web server (http://www.herbalgenomics.org/cpgavas2) (Shi et al., 2019). Each assembled genome sequence was submitted to the server in FASTA format, with the pre-curated, RNA-seq-validated 43-plastome reference dataset selected as the reference for homology-based gene-model transfer. Protein-coding and ribosomal RNA genes were predicted through BLAST-based homology searches (BLAST+ v2.8.1; Camacho et al., 2009) against this reference set, incorporating the dedicated algorithms implemented in CPGAVAS2 for annotating the short exons of ",
          { t: "petB, petD" },
          " and ",
          { t: "rpl16" },
          " and the trans-spliced gene ",
          { t: "rps12" },
          ", which similarity-based searches alone cannot reliably resolve. Transfer RNA genes were predicted using both ARAGORN v1.2.36 (Laslett and Canback, 2004) and tRNAscan-SE v2.0 (Lowe and Eddy, 1997; Chan et al., 2021), and predicted gene identities were cross-checked to flag inconsistently named tRNAs for manual review.",
        ]),
        body(
          "For each genome, CPGAVAS2 generated a GFF3 annotation file, a GenBank-format flat file, a Sequin (.sqn) file for GenBank submission, and FASTA files of the predicted gene, mRNA, coding sequence (CDS) and protein sets, together with rRNA and tRNA sequences identified separately by ARAGORN and tRNAscan-SE. Gene composition and the lengths of introns and exons in multi-exon genes were tabulated from the CPGAVAS2 analysis report. Annotations flagged by the pipeline as potentially problematic — including missing 5′ or 3′ termini, putative frameshifts in protein-coding genes, and misassigned tRNA names — were manually inspected and corrected in the Apollo genome editor (Dunn et al., 2019). Relative synonymous codon usage (RSCU) was calculated for all annotated protein-coding genes using the codon usage module of CPGAVAS2. The finalized chloroplast genome sequences were deposited in GenBank under accession numbers [XXXXXX] and [XXXXXX] for KS and KB, respectively."
        ),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 120, after: 120 },
          children: [new TextRun({ text: "Identification of Repeat Elements", bold: true, font: FONT, size: 26 })],
        }),
        body(
          "Repetitive elements in the KS and KB chloroplast genomes were identified using the repeat-discovery pipeline integrated into CPGAVAS2, which combines three complementary tools. Simple sequence repeats (microsatellites with repeat-unit lengths of 1–6 bp) were detected using MISA (Beier et al., 2017). Long tandem repeats, defined as tandemly arrayed motifs with a repeat-unit length of ≥7 bp, were identified using Tandem Repeats Finder v4.0.9 (Benson, 1999). Long dispersed repeats, comprising forward and reverse (inverted) repeats, were identified using VMATCH v2.3.0 (Kurtz, 2010). All three tools were run with the default parameters implemented in the CPGAVAS2 pipeline. The predicted gene models and the three repeat classes were jointly visualized on a circular genome map generated with drawgenemap, in which genes were colored by functional category and forward repeats, reverse repeats, tandem repeats, and microsatellites were displayed as concentric tracks."
        ),

        body(""),
        noteBox([
          "Author note — read before pasting: your job report's “Dataset: 43-plastome dataset” line is CPGAVAS2's own internal, RNA-seq-validated reference set used for homology-based annotation (Shi et al., 2019); it is not 43 genomes that you submitted. I've written the paragraphs above assuming one CPGAVAS2 job was run per genome (KS and KB separately using this same reference dataset), based on your RSCU file showing matching codon counts for both. If you instead ran a single merged job, or used the 2544-plastome comprehensive dataset for either genome, adjust the wording accordingly. Replace the bracketed GenBank accession numbers once assigned, and remember to update the taxon and contact information in the GenBank/Sequin files before submission, as CPGAVAS2's results page reminds you to do.",
        ]),

        body(""),
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 120, after: 120 },
          children: [new TextRun({ text: "References to add", bold: true, font: FONT, size: 26 })],
        }),
        refEntry(
          "Beier, S., Thiel, T., Münch, T., Scholz, U., & Mascher, M. (2017). MISA-web: a web server for microsatellite prediction. Bioinformatics, 33(16), 2583–2585. https://doi.org/10.1093/bioinformatics/btx198"
        ),
        refEntry(
          "Benson, G. (1999). Tandem repeats finder: a program to analyze DNA sequences. Nucleic Acids Research, 27(2), 573–580. https://doi.org/10.1093/nar/27.2.573"
        ),
        refEntry(
          "Camacho, C., Coulouris, G., Avetisyan, V., Ma, N., Papadopoulos, J., Bealer, K., & Madden, T. L. (2009). BLAST+: architecture and applications. BMC Bioinformatics, 10, 421. https://doi.org/10.1186/1471-2105-10-421"
        ),
        refEntry(
          "Chan, P. P., Lin, B. Y., Mak, A. J., & Lowe, T. M. (2021). tRNAscan-SE 2.0: improved detection and functional classification of transfer RNA genes. Nucleic Acids Research, 49(16), 9077–9096. https://doi.org/10.1093/nar/gkab688"
        ),
        refEntry(
          "Dunn, N. A., Unni, D. R., Diesh, C., Munoz-Torres, M., Harris, N. L., Yao, E., Rasche, H., Holmes, I. H., Elsik, C. G., & Lewis, S. E. (2019). Apollo: Democratizing genome annotation. PLOS Computational Biology, 15(2), e1006790. https://doi.org/10.1371/journal.pcbi.1006790"
        ),
        refEntry(
          "Kurtz, S. (2010). The Vmatch large scale sequence analysis software. Available at: http://www.vmatch.de"
        ),
        refEntry(
          "Laslett, D., & Canback, B. (2004). ARAGORN, a program to detect tRNA genes and tmRNA genes in nucleotide sequences. Nucleic Acids Research, 32(1), 11–16. https://doi.org/10.1093/nar/gkh152"
        ),
        refEntry(
          "Lowe, T. M., & Eddy, S. R. (1997). tRNAscan-SE: a program for improved detection of transfer RNA genes in genomic sequence. Nucleic Acids Research, 25(5), 955–964. https://doi.org/10.1093/nar/25.5.955"
        ),
        refEntry(
          "Shi, L., Chen, H., Jiang, M., Wang, L., Wu, X., Huang, L., & Liu, C. (2019). CPGAVAS2, an integrated plastome sequence annotator and analyzer. Nucleic Acids Research, 47(W1), W65–W73. https://doi.org/10.1093/nar/gkz345"
        ),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("/sessions/brave-trusting-ramanujan/mnt/outputs/CPGAVAS2_Methodology_Kgalanga_v2.docx", buffer);
  console.log("written");
});
