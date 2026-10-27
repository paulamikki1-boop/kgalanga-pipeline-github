const OUT_DIR = process.env.KG_OUTPUT_DIR || "output";
const IN_DIR = process.env.KG_INPUT_DIR || "data";
require("fs").mkdirSync(OUT_DIR, { recursive: true });
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  BorderStyle, ShadingType, ExternalHyperlink, Table, TableRow, TableCell,
  WidthType, convertInchesToTwip
} = require("docx");

const FONT = "Times New Roman";

function body(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 200, line: 276 },
    alignment: AlignmentType.JUSTIFIED,
    children: [new TextRun({ text, font: FONT, size: 24, ...opts })],
  });
}

function heading(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 300, after: 150 },
    children: [new TextRun({ text, font: FONT, size: 28, bold: true, color: "1F4E78" })],
  });
}

function subheading(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 200, after: 100 },
    children: [new TextRun({ text, font: FONT, size: 24, bold: true, italics: true })],
  });
}

function placeholder(text) {
  return new TextRun({ text, font: FONT, size: 24, bold: true, color: "C00000" });
}

function mixedParagraph(runs) {
  return new Paragraph({ spacing: { after: 200, line: 276 }, alignment: AlignmentType.JUSTIFIED, children: runs });
}

function note(lines) {
  // Shaded "author note" callout box using a bordered, shaded paragraph
  return lines.map((text, i) => new Paragraph({
    spacing: { after: i === lines.length - 1 ? 200 : 60 },
    shading: { type: ShadingType.CLEAR, fill: "FFF2CC" },
    border: {
      left: { style: BorderStyle.SINGLE, size: 24, color: "BF8F00", space: 8 },
    },
    children: [new TextRun({ text, font: FONT, size: 21, italics: true, color: "594100" })],
  }));
}

const doc = new Document({
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 }, // US Letter
          margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 },
        },
      },
      children: [
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 100 },
          children: [new TextRun({
            text: "Methods Addendum: Selection Pressure (Ka/Ks), Chloroplast Isolation Statistics, SSR Identification, and Primer Design",
            font: FONT, size: 28, bold: true,
          })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 300 },
          children: [new TextRun({
            text: "Optimized Chloroplast Isolation and Comparative Analysis of Complete Chloroplast Genomes in Narrow- and Broad-Leaf Kaempferia galanga",
            font: FONT, size: 22, italics: true, color: "555555",
          })],
        }),
        ...note([
          "How to use this document: the paragraphs under each heading below are written to be pasted directly " +
          "into the Methods section, in the same style as your existing draft. Text in red brackets is a " +
          "placeholder you need to fill in (software version, model name, accession number). The shaded boxes " +
          "like this one are notes for you, not manuscript text -- delete them before submission.",
        ]),

        heading("1. Selection Pressure (Ka/Ks) Analysis"),
        subheading("Methods text (paste into Methods)"),
        mixedParagraph([
          new TextRun({ text: "Non-synonymous (Ka) and synonymous (Ks) substitution rates, and their ratio (Ka/Ks), were estimated for all protein-coding genes shared among the narrow-leaf (KS) and broad-leaf (KB) ", font: FONT, size: 24 }),
          new TextRun({ text: "Kaempferia galanga", font: FONT, size: 24, italics: true }),
          new TextRun({ text: " chloroplast genomes and the NCBI reference chloroplast genome (accession ", font: FONT, size: 24 }),
          placeholder("[NC_040851.1 -- confirm]"),
          new TextRun({ text: ") using KaKs_Calculator v2.0 (Wang et al., 2010). Homologous coding sequences were extracted per gene from the GeSeq annotations, aligned in a pairwise manner using ", font: FONT, size: 24 }),
          placeholder("[MAFFT/MUSCLE -- specify]"),
          new TextRun({ text: ", and Ka, Ks, and Ka/Ks values were calculated using the ", font: FONT, size: 24 }),
          placeholder("[YN / MYN -- specify model]"),
          new TextRun({ text: " method with default parameters. Three pairwise comparisons were performed for each gene: KS vs. reference, KB vs. reference, and KS vs. KB. A Ka/Ks ratio significantly less than 1 was interpreted as evidence of purifying (negative) selection, a ratio not significantly different from 1 as neutral evolution, and a ratio significantly greater than 1 as evidence of positive selection. Genes for which no synonymous or non-synonymous substitutions were detected between a given sequence pair were classified as invariant for that comparison and excluded from the ratio calculation.", font: FONT, size: 24 }),
        ]),

        ...note([
          "Author note -- read before running this: the variant list already in your 'ssr of kb and ks' sheet shows " +
          "that at every one of the 10 recorded SNP/indel positions, KB and KS carry the identical allele -- the " +
          "variants only separate {KB, KS} as a pair from the NCBI reference. None of the 10 variants fall inside " +
          "annotated exons in a way that would change a codon (most are in rps12/rpl-family genes, one is an " +
          "intron/intergenic insertion). Practically, this means the KS-vs-KB pairwise comparison above will most " +
          "likely return zero substitutions for every single gene -- i.e., Ka/Ks is undefined (0/0) genome-wide " +
          "between the two morphotypes. That is not a failure of the method; it is itself a result worth stating " +
          "plainly in the Results/Discussion: the chloroplast genome shows no coding-sequence divergence between " +
          "narrow-leaf and broad-leaf K. galanga, so if the two morphotypes are genetically distinct, that " +
          "distinction is not visible in the plastome (consistent with cpDNA's slow, uniparental evolution and with " +
          "leaf-shape variation more plausibly arising from nuclear loci or environment). The KS-vs-reference and " +
          "KB-vs-reference comparisons are where you will actually get non-trivial Ka/Ks values, since that is where " +
          "the 10 known variants (and any other coding differences) sit.",
        ]),

        heading("2. Statistical Analysis of Chloroplast Isolation Efficiency"),
        subheading("Methods text (paste into Methods)"),
        body(
          "Chloroplast yield, measured as absorbance at 440 nm, 546 nm, and 635 nm, was recorded for three " +
          "biological replicates per isolation method (high salt low pH, sucrose gradient, Percoll gradient) and " +
          "per morphotype (narrow-leaf, KS; broad-leaf, KB), and is reported as mean ± standard deviation. " +
          "Prior to hypothesis testing, the normality and homogeneity of variance of absorbance values were " +
          "assessed at each wavelength using the Shapiro-Wilk and Levene tests, respectively. Differences in " +
          "absorbance among the three isolation methods and between the two morphotypes were then evaluated at " +
          "each wavelength using two-way analysis of variance (ANOVA), with isolation method and morphotype as " +
          "fixed factors, including their interaction term. Where the assumptions of normality or homogeneity of " +
          "variance were violated, the non-parametric Kruskal-Wallis test was used in place of ANOVA, with " +
          "morphotypes analyzed separately. Where a significant main effect of isolation method was detected, " +
          "pairwise comparisons among methods were performed using Tukey's honestly significant difference (HSD) " +
          "post hoc test (or Dunn's test with Bonferroni correction following a significant Kruskal-Wallis result). " +
          "A significance threshold of α = 0.05 was applied throughout. All statistical analyses were performed " +
          "in "
        ),
        mixedParagraph([
          placeholder("[R v4.x (packages: stats, rstatix, car) / SPSS v29 / GraphPad Prism -- specify what you actually used]"),
          new TextRun({ text: ".", font: FONT, size: 24 }),
        ]),

        ...note([
          "Author note: this test needs the per-replicate absorbance readings (n=3 per method × morphotype × " +
          "wavelength), not just the means currently shown in your draft's Table 6 -- pull those from your raw " +
          "spectrophotometer log if they aren't already tabulated elsewhere. Given how large the gap already looks " +
          "(e.g. 440 nm: high salt low pH 0.9-1.4 vs. sucrose/Percoll well under 0.1), the method effect is very " +
          "likely to come out strongly significant (p < 0.001) even with only 3 replicates per group -- the real " +
          "value of running the ANOVA is (a) a defensible p-value to cite instead of an eyeballed claim, and (b) " +
          "checking whether morphotype (KS vs KB) or the method×morphotype interaction is also significant, since " +
          "broad-leaf absorbance reads consistently higher than narrow-leaf within the high salt low pH method.",
        ]),

        heading("3. Suggested Results-Section Reporting Templates"),
        body(
          "Ka/Ks: “Across the [N] protein-coding genes compared between KS and KB, no non-synonymous or " +
          "synonymous substitutions were detected, yielding an undefined Ka/Ks ratio at every locus; the two " +
          "morphotypes were therefore identical at the chloroplast coding-sequence level. In contrast, comparison " +
          "against the reference genome (NC_040851.1) yielded Ka/Ks ratios ranging from [X] to [Y] across the [N] " +
          "genes assessed, with [gene names] showing evidence of purifying selection (Ka/Ks < 1) and [gene names / " +
          "‘none’] showing evidence of positive selection (Ka/Ks > 1).”"
        ),
        body(
          "ANOVA: “Two-way ANOVA revealed a significant main effect of isolation method on chloroplast absorbance " +
          "at all three wavelengths (440 nm: F([df1],[df2]) = [F], p [< or =] [value]; similarly for 546 nm and " +
          "635 nm), with the high salt low pH method producing significantly higher absorbance than both the " +
          "sucrose gradient and Percoll gradient methods (Tukey HSD, p < 0.05 for all pairwise comparisons). The " +
          "effect of morphotype was [significant/not significant] (F = [value], p = [value]), and the method × " +
          "morphotype interaction was [significant/not significant] (F = [value], p = [value]).”"
        ),

        heading("4. SSR (Microsatellite) Identification"),
        subheading("Methods text (paste into Methods)"),
        mixedParagraph([
          new TextRun({ text: "Simple sequence repeats (SSRs) in the narrow-leaf (KS), broad-leaf (KB), and reference (", font: FONT, size: 24 }),
          placeholder("[NC_040851.1 -- confirm accession]"),
          new TextRun({ text: ") ", font: FONT, size: 24 }),
          new TextRun({ text: "Kaempferia galanga", font: FONT, size: 24, italics: true }),
          new TextRun({ text: " chloroplast genomes were identified using MISA-web (Beier et al., 2017; https://webblast.ipk-gatersleben.de/misa/), with minimum repeat-number thresholds of 10 for mononucleotide, 5 for dinucleotide, 4 for trinucleotide, and 3 each for tetra-, penta-, and hexanucleotide motifs, following the parameters commonly applied in chloroplast genome SSR surveys (e.g., Devi et al., 2022, PMC8980536; Beier et al., 2017). Compound microsatellites, defined as two or more SSRs separated by fewer than ", font: FONT, size: 24 }),
          placeholder("[100 -- confirm; MISA-web default]"),
          new TextRun({ text: " interrupting base pairs, were also reported. SSRs were tabulated by repeat-unit motif and repeat-class (mono- through hexanucleotide) for each genome, and their genomic location (LSC, SSC, IRA, or IRB) and overlap with annotated genes were determined by cross-referencing SSR coordinates against the GeSeq annotation.", font: FONT, size: 24 }),
        ]),
        ...note([
          "Author note: adjust the in-text citations above to your actual reference list format -- I've cited the " +
          "parameter source generically since your three source links (Cryptocoryne elliptica cpSSR study, the " +
          "MDPI codon-bias/SSR paper, and the Hippeastrinae ScienceDirect paper) all use the same 10/5/4/3/3/3 " +
          "MISA thresholds, which matches what you ran on KB/KS/KG ref. The Hippeastrinae paper cites Beier et al. " +
          "2017 directly for MISA itself -- I'd follow that convention and cite MISA-web's own paper (below) as the " +
          "primary tool citation, and cite one or two of your three source papers as precedent for using this " +
          "specific threshold combination in a chloroplast-genome context, rather than citing all three.",
        ]),

        heading("5. Primer Design for cpSSR Markers"),
        subheading("Methods text (paste into Methods)"),
        body(
          "Primer pairs flanking each identified SSR locus were designed using Primer3 (Untergasser et al., 2012; " +
          "Koressaar and Remm, 2007), either through MISA-web's integrated Primer3 module or a standalone " +
          "Primer3/Primer3Plus run against ~200-400 bp of flanking sequence on either side of each repeat. Primer " +
          "design parameters were set to a primer length of 18-27 nt (optimum 20-22 nt), an annealing temperature " +
          "of 55-60°C, a GC content of 40-60%, and an expected amplicon size of 100-300 bp. Loci located in the " +
          "duplicated inverted-repeat regions (IRA/IRB) were flagged and de-duplicated prior to primer design, " +
          "since a marker in one IR copy is redundant with its counterpart in the other. Primer specificity was " +
          "checked in silico by confirming a single expected amplicon per primer pair against the complete " +
          "chloroplast genome sequence."
        ),
        ...note([
          "Author note -- how to actually pick which of the 239 SSR loci to carry forward to primer design, since " +
          "designing and validating primers for every locus is not practical:",
          "  1. Deduplicate IR-region loci first -- the IRA/IRB pair is identical, so roughly a quarter of your " +
          "raw SSR count is a mirror-image duplicate of another locus in the list. Keep one representative per " +
          "duplicated pair.",
          "  2. Prioritize loci that differ in repeat number between KS, KB, and the reference -- those are the " +
          "only ones that will actually work as length-polymorphic markers on a gel. Given that your variant list " +
          "showed no SNPs/indels distinguishing KB from KS specifically, check the MISA output's repeat-count " +
          "column locus-by-locus for KS vs KB vs KG ref -- if none differ between KB and KS, your cpSSR markers " +
          "will end up useful for species/genus-level identification (K. galanga vs. other Kaempferia/reference) " +
          "rather than for telling the two morphotypes apart, which is worth stating plainly rather than searching " +
          "for a difference that may not exist.",
          "  3. Favor mono- and dinucleotide loci with longer, cleaner repeat tracts (e.g., the A/T homopolymers " +
          "and AT/TA dinucleotide repeats already dominate your motif table) -- these tend to be more reliably " +
          "polymorphic and easier to score on a gel than short tri-/tetra-nucleotide repeats.",
          "  4. Avoid loci sitting inside coding exons where possible (check against your gene annotation table) " +
          "-- intergenic or intronic SSRs are less likely to be selectively constrained and make cleaner markers.",
          "  5. After Primer3 design, validate a subset (e.g., 10-20 primer pairs spanning different repeat " +
          "classes and genome regions) by gradient PCR and agarose gel electrophoresis to confirm a single band " +
          "of the expected size, then Sanger-sequence a few amplicons to confirm the actual repeat count matches " +
          "the in silico prediction before reporting them as validated markers.",
        ]),

        heading("References to add"),
        body(
          "Wang, D., Zhang, Y., Zhang, Z., Zhu, J., & Yu, J. (2010). KaKs_Calculator 2.0: A toolkit incorporating " +
          "gamma-series methods and sliding window strategies. Genomics, Proteomics & Bioinformatics, 8(1), 77-80. " +
          "https://doi.org/10.1016/S1672-0229(10)60008-3"
        ),
        body(
          "Beier, S., Thiel, T., Münch, T., Scholz, U., & Mascher, M. (2017). MISA-web: a web server for " +
          "microsatellite prediction. Bioinformatics, 33(16), 2583-2585. https://doi.org/10.1093/bioinformatics/btx198"
        ),
        body(
          "Untergasser, A., Cutcutache, I., Koressaar, T., Ye, J., Faircloth, B. C., Remm, M., & Rozen, S. G. " +
          "(2012). Primer3 -- new capabilities and interfaces. Nucleic Acids Research, 40(15), e115. " +
          "https://doi.org/10.1093/nar/gks596"
        ),
        body(
          "Koressaar, T., & Remm, M. (2007). Enhancements and modifications of primer design program Primer3. " +
          "Bioinformatics, 23(10), 1289-1291. https://doi.org/10.1093/bioinformatics/btm091"
        ),
        mixedParagraph([
          new TextRun({ text: "R Core Team / SPSS / GraphPad citation -- ", font: FONT, size: 24 }),
          placeholder("[add once you confirm which software you actually ran]"),
          new TextRun({ text: ".", font: FONT, size: 24 }),
        ]),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  require("fs").writeFileSync(OUT_DIR + "/Methods_Addendum_KaKs_ANOVA.docx", buf);
  console.log("saved");
});
