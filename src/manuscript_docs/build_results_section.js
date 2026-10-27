const OUT_DIR = process.env.KG_OUTPUT_DIR || "output";
const IN_DIR = process.env.KG_INPUT_DIR || "data";
require("fs").mkdirSync(OUT_DIR, { recursive: true });
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  Table, TableRow, TableCell, WidthType, AlignmentType,
  BorderStyle, ShadingType, SpacingType, convertInchesToTwip,
  TableOfContents, StyleLevel, PageBreak
} = require('docx');
const fs = require('fs');

// Helper: Normal paragraph
function p(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, size: 24, font: 'Times New Roman', ...opts })],
    spacing: { after: 120, line: 276, lineRule: 'auto' },
    alignment: AlignmentType.JUSTIFIED,
  });
}

// Helper: paragraph with mixed runs
function pRuns(runs, afterSpace = 120) {
  return new Paragraph({
    children: runs.map(r => new TextRun({ font: 'Times New Roman', size: 24, ...r })),
    spacing: { after: afterSpace, line: 276, lineRule: 'auto' },
    alignment: AlignmentType.JUSTIFIED,
  });
}

// Helper: Heading 1 (section)
function h1(text) {
  return new Paragraph({
    text,
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 240, after: 120 },
    style: 'Heading1',
    children: [new TextRun({ text, bold: true, size: 28, font: 'Times New Roman' })],
  });
}

// Helper: Heading 2 (subsection)
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 200, after: 80 },
    children: [new TextRun({ text, bold: true, size: 26, font: 'Times New Roman' })],
  });
}

// Helper: italic run
function it(text) {
  return { text, italics: true };
}

// Helper: bold run
function bo(text) {
  return { text, bold: true };
}

// Helper: normal run
function tx(text) {
  return { text };
}

// Caption helper
function caption(text) {
  return new Paragraph({
    children: [new TextRun({ text, size: 22, font: 'Times New Roman', italics: false })],
    spacing: { before: 60, after: 160 },
    alignment: AlignmentType.LEFT,
  });
}

// Table cell helper
function tc(text, opts = {}) {
  return new TableCell({
    children: [new Paragraph({
      children: [new TextRun({ text, size: 22, font: 'Times New Roman', ...opts })],
      spacing: { after: 40 },
      alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
    })],
    shading: opts.header ? { type: ShadingType.CLEAR, color: 'auto', fill: 'D9D9D9' } : undefined,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 1 },
      bottom: { style: BorderStyle.SINGLE, size: 1 },
      left: { style: BorderStyle.SINGLE, size: 1 },
      right: { style: BorderStyle.SINGLE, size: 1 },
    },
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    columnSpan: opts.span,
  });
}

// Table row helper
function tr(cells) {
  return new TableRow({ children: cells });
}

// Make table from 2D array
function makeTable(rows, widths) {
  return new Table({
    width: { size: 9000, type: WidthType.DXA },
    columnWidths: widths,
    rows: rows,
    borders: {
      insideH: { style: BorderStyle.SINGLE, size: 1 },
      insideV: { style: BorderStyle.SINGLE, size: 1 },
    },
  });
}

const doc = new Document({
  styles: {
    paragraphStyles: [
      {
        id: 'Normal',
        name: 'Normal',
        run: { size: 24, font: 'Times New Roman' },
        paragraph: { spacing: { line: 276 } },
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        margin: { top: 1440, bottom: 1440, left: 1800, right: 1440 },
      },
    },
    children: [

      // TITLE
      new Paragraph({
        children: [new TextRun({ text: 'Results', bold: true, size: 32, font: 'Times New Roman' })],
        heading: HeadingLevel.HEADING_1,
        spacing: { after: 200 },
        alignment: AlignmentType.LEFT,
      }),

      // ==========================================
      // 3.1 ITS-Based Species Confirmation
      // ==========================================
      new Paragraph({
        children: [new TextRun({ text: '3.1 ITS-Based Species Confirmation', bold: true, size: 26, font: 'Times New Roman' })],
        spacing: { before: 200, after: 100 },
      }),

      pRuns([
        tx('Internal transcribed spacer (ITS) marker amplification was performed to confirm the taxonomic identity of the narrow-leaf (KS) and broad-leaf (KB) '),
        it('Kaempferia galanga '),
        tx('morphotypes cultivated at Taylor\'s Urban Farm. Sequence analysis of the amplified ITS regions from both morphotypes yielded sequences with high similarity to '),
        it('K. galanga '),
        tx('accessions deposited in the NCBI GenBank database, confirming that both morphotypes belong to the same species (Table 1). These results are consistent with previous molecular characterization of '),
        it('Kaempferia '),
        tx('species using ITS4 and ITS5 primers, which have been proposed as DNA barcodes for identification within this genus (Labrooy et al., 2018).'),
      ]),

      // ==========================================
      // 3.2 Chloroplast Isolation Efficiency
      // ==========================================
      new Paragraph({
        children: [new TextRun({ text: '3.2 Chloroplast Isolation Efficiency', bold: true, size: 26, font: 'Times New Roman' })],
        spacing: { before: 200, after: 100 },
      }),

      pRuns([
        tx('Chloroplasts were successfully isolated from both broad-leaf (KB) and narrow-leaf (KS) '),
        it('K. galanga '),
        tx('using three extraction protocols: the high salt low pH method (Yu et al., 2024), the sucrose gradient method (Takamatsu et al., 2018), and the Percoll gradient method (Liu et al., 2019) (Figure 2). Visual inspection of the chloroplast preparations revealed marked differences in recovery among the three methods. The high salt low pH method consistently produced a distinct green precipitate in both morphotypes, indicative of a high chloroplast yield. In contrast, preparations obtained using the sucrose gradient and Percoll gradient methods exhibited little to no visible green precipitate, indicating substantially lower chloroplast recovery under the conditions tested.'),
      ]),

      // Spectrophotometric sub-section
      new Paragraph({
        children: [new TextRun({ text: '3.2.1 Spectrophotometric Quantification', bold: true, italics: false, size: 24, font: 'Times New Roman' })],
        spacing: { before: 160, after: 80 },
      }),

      pRuns([
        tx('Chloroplast yield was quantitatively assessed using UV–Vis spectrophotometry at wavelengths of 440 nm, 546 nm, and 635 nm, corresponding to the major chlorophyll absorption peaks (Table 2). For both morphotypes, the high salt low pH method produced substantially higher absorbance values across all three wavelengths compared to the sucrose gradient and Percoll gradient methods. Narrow-leaf (KS) samples processed using the high salt low pH method exhibited mean absorbance values of 0.931, 0.804, and 0.735 at 440 nm, 546 nm, and 635 nm, respectively. Broad-leaf (KB) samples processed using the same method yielded higher mean absorbance values of 1.441, 1.155, and 1.012 at the corresponding wavelengths, exceeding the accepted threshold of 0.7–1.0 for sufficient chloroplast density. In contrast, samples isolated via the sucrose gradient method showed absorbance values below 0.05 across all wavelengths for both morphotypes (KS: 0.035, 0.025, 0.014; KB: 0.043, 0.036, 0.026), as did Percoll gradient preparations (KS: 0.038, 0.075, 0.080; KB: 0.039, 0.074, 0.079), indicating minimal chloroplast recovery.'),
      ]),

      // Table 2 - Spectrophotometric data
      caption('Table 2. Mean UV–Vis absorbance values of chloroplast extracts obtained from narrow-leaf (KS) and broad-leaf (KB) Kaempferia galanga using three isolation methods. Acceptable absorbance range: 0.7–1.0.'),

      makeTable([
        tr([
          tc('Isolation Method', { header: true }),
          tc('Morphotype', { header: true }),
          tc('440 nm', { header: true, center: true }),
          tc('546 nm', { header: true, center: true }),
          tc('635 nm', { header: true, center: true }),
        ]),
        tr([
          tc('High salt low pH', { bold: true }),
          tc('Narrow-leaf (KS)'),
          tc('0.931', { center: true }),
          tc('0.804', { center: true }),
          tc('0.735', { center: true }),
        ]),
        tr([
          tc(''),
          tc('Broad-leaf (KB)'),
          tc('1.441', { center: true }),
          tc('1.155', { center: true }),
          tc('1.012', { center: true }),
        ]),
        tr([
          tc('Sucrose gradient', { bold: true }),
          tc('Narrow-leaf (KS)'),
          tc('0.035', { center: true }),
          tc('0.025', { center: true }),
          tc('0.014', { center: true }),
        ]),
        tr([
          tc(''),
          tc('Broad-leaf (KB)'),
          tc('0.043', { center: true }),
          tc('0.036', { center: true }),
          tc('0.026', { center: true }),
        ]),
        tr([
          tc('Percoll gradient', { bold: true }),
          tc('Narrow-leaf (KS)'),
          tc('0.038', { center: true }),
          tc('0.075', { center: true }),
          tc('0.080', { center: true }),
        ]),
        tr([
          tc(''),
          tc('Broad-leaf (KB)'),
          tc('0.039', { center: true }),
          tc('0.074', { center: true }),
          tc('0.079', { center: true }),
        ]),
      ], [2800, 2000, 1400, 1400, 1400]),

      // Microscopic sub-section
      new Paragraph({
        children: [new TextRun({ text: '3.2.2 Microscopic Assessment of Chloroplast Integrity', bold: true, italics: false, size: 24, font: 'Times New Roman' })],
        spacing: { before: 160, after: 80 },
      }),

      pRuns([
        tx('Phase-contrast microscopy was used to evaluate chloroplast morphology and integrity following isolation (Figure 3). Chloroplasts isolated using the high salt low pH method included both intact organelles with clearly defined envelope membranes and some aggregated chloroplasts. In contrast, preparations obtained using the sucrose gradient and Percoll gradient methods predominantly contained aggregated chloroplasts, with few intact organelles observed. The presence of intact chloroplasts in preparations obtained exclusively via the high salt low pH method further corroborated its superior performance in preserving chloroplast structure. Based on these combined observations, chloroplasts obtained using the high salt low pH method were selected for downstream DNA extraction and genome sequencing.'),
      ]),

      // ==========================================
      // 3.3 Chloroplast DNA Quality Assessment
      // ==========================================
      new Paragraph({
        children: [new TextRun({ text: '3.3 Chloroplast DNA Quality Assessment', bold: true, size: 26, font: 'Times New Roman' })],
        spacing: { before: 200, after: 100 },
      }),

      pRuns([
        tx('Agarose gel electrophoresis was performed to assess the integrity of chloroplast DNA extracted from two biological replicates per morphotype (KS1, KS2, KB1, and KB2). Clear, high-molecular-weight DNA bands were observed for KS2, KB1, and KB2, indicating intact and sufficiently abundant chloroplast DNA suitable for downstream sequencing (Figure 4). Sample KS1 showed weak or absent bands, consistent with low-quality or degraded DNA.'),
      ]),

      pRuns([
        tx('DNA purity was evaluated using NanoDrop spectrophotometry by measuring the A260/A280 absorbance ratio (Table 3). Sample KS1 exhibited a ratio of 0.568, indicative of protein contamination or degraded nucleic acids. The remaining samples showed A260/A280 ratios ranging from 1.616 to 1.818, within or approaching the accepted range of 1.8–2.0 for high-quality DNA. Based on these combined assessments, samples KS2, KB1, and KB2 were deemed suitable for chloroplast genome sequencing.'),
      ]),

      caption('Table 3. NanoDrop spectrophotometric assessment of chloroplast DNA purity (A260/A280 ratios) for biological replicates of narrow-leaf (KS) and broad-leaf (KB) Kaempferia galanga.'),

      makeTable([
        tr([
          tc('Sample', { header: true }),
          tc('Morphotype', { header: true }),
          tc('A260/A280 Ratio', { header: true, center: true }),
          tc('Assessment', { header: true }),
        ]),
        tr([tc('KS1'), tc('Narrow-leaf'), tc('0.568', { center: true }), tc('Unsuitable (degraded/contaminated)')]),
        tr([tc('KS2'), tc('Narrow-leaf'), tc('1.818', { center: true }), tc('Suitable')]),
        tr([tc('KB1'), tc('Broad-leaf'), tc('1.616', { center: true }), tc('Suitable')]),
        tr([tc('KB2'), tc('Broad-leaf'), tc('1.778', { center: true }), tc('Suitable')]),
      ], [1800, 2200, 2500, 2500]),

      // ==========================================
      // 3.4 Chloroplast Genome Sequencing
      // ==========================================
      new Paragraph({
        children: [new TextRun({ text: '3.4 Complete Chloroplast Genome Sequencing', bold: true, size: 26, font: 'Times New Roman' })],
        spacing: { before: 200, after: 100 },
      }),

      pRuns([
        tx('High-quality chloroplast DNA from KS2, KB1, and KB2 was used for Illumina library preparation and paired-end sequencing on the NovaSeq 6000 platform (2 × 150 bp). Sequencing generated approximately 11.9 million paired-end reads (1.79 Gb) for the broad-leaf (KB) sample and 9.4 million paired-end reads (1.41 Gb) for the narrow-leaf (KS) sample. Quality metrics indicated excellent sequencing performance: Q30 values exceeded 94% for all libraries, and GC content was consistent between samples, ranging from 42.9% to 43.2% (Table 4). These metrics confirm that the chloroplast DNA obtained using the high salt low pH isolation method was of sufficient quality for high-throughput genome sequencing and assembly.'),
      ]),

      caption('Table 4. Illumina sequencing statistics for narrow-leaf (KS) and broad-leaf (KB) Kaempferia galanga chloroplast genome libraries.'),

      makeTable([
        tr([
          tc('Sample', { header: true }),
          tc('Total Reads', { header: true, center: true }),
          tc('Total Data (Gb)', { header: true, center: true }),
          tc('Q30 (%)', { header: true, center: true }),
          tc('GC Content (%)', { header: true, center: true }),
        ]),
        tr([tc('KS (narrow-leaf)'), tc('9,400,000', { center: true }), tc('1.41', { center: true }), tc('>94', { center: true }), tc('42.9', { center: true })]),
        tr([tc('KB (broad-leaf)'), tc('11,900,000', { center: true }), tc('1.79', { center: true }), tc('>94', { center: true }), tc('43.2', { center: true })]),
      ], [2500, 1900, 1800, 1500, 1300]),

      // ==========================================
      // 3.5 Chloroplast Genome Structure
      // ==========================================
      new Paragraph({
        children: [new TextRun({ text: '3.5 Chloroplast Genome Structure and Organization', bold: true, size: 26, font: 'Times New Roman' })],
        spacing: { before: 200, after: 100 },
      }),

      pRuns([
        tx('Assembly and annotation of the chloroplast genomes of narrow-leaf (KS) and broad-leaf (KB) '),
        it('K. galanga '),
        tx('yielded complete, circular genomes of 163,799 bp in length for both morphotypes. Both genomes displayed the typical quadripartite structure of angiosperm chloroplast genomes, comprising a large single copy (LSC) region of 88,429 bp and a small single copy (SSC) region of 15,776 bp, separated by a pair of inverted repeats (IRA and IRB), each 29,797 bp in length (Table 5; Figure 5). These dimensions are comparable to those reported for the published '),
        it('K. galanga '),
        tx('reference genome (accession NC_040851.1; 163,811 bp; LSC 88,405 bp; SSC 15,812 bp; IR 29,797 bp; Li, Zhao and Liu, 2019), with the minor difference in total genome length (12 bp) attributable to a small number of insertion/deletion events relative to the reference (see Section 3.9).'),
      ]),

      pRuns([
        tx('The overall GC content of both KS and KB genomes was 36.2%, consistent with values reported for other '),
        it('Kaempferia '),
        tx('chloroplast genomes. GC content varied across genomic regions: the LSC region contained 34.0% GC, the SSC region contained 30.0% GC, and both inverted repeat regions exhibited a higher GC content of 41.0%, reflecting the characteristic enrichment of GC in ribosomal RNA gene clusters housed within the IR regions (Table 5). The circular genome maps produced by OGDRAW are presented in Figure 5, illustrating gene arrangement and regional boundaries for both morphotypes.'),
      ]),

      pRuns([
        tx('During assembly, the SSC region of the KB genome was found to be annotated on the reverse strand relative to the KS and reference genomes. This is a recognized assembly artifact arising from the alternative orientation of the SSC region, which exists as two equally valid isomers in chloroplast genomes (Palmer, 1983). After reverse-complementing the KB SSC sequence, the two morphotypes were confirmed as sequence-identical across this region.'),
      ]),

      caption('Table 5. Structural features of the complete chloroplast genomes of narrow-leaf (KS) and broad-leaf (KB) Kaempferia galanga and the published reference genome (NC_040851.1).'),

      makeTable([
        tr([
          tc('Feature', { header: true }),
          tc('KS', { header: true, center: true }),
          tc('KB', { header: true, center: true }),
          tc('KG Reference (NC_040851.1)', { header: true, center: true }),
        ]),
        tr([tc('Total genome size (bp)'), tc('163,799', { center: true }), tc('163,799', { center: true }), tc('163,811', { center: true })]),
        tr([tc('LSC size (bp)'), tc('88,429', { center: true }), tc('88,429', { center: true }), tc('88,405', { center: true })]),
        tr([tc('SSC size (bp)'), tc('15,776', { center: true }), tc('15,776', { center: true }), tc('15,812', { center: true })]),
        tr([tc('IR size (bp, each)'), tc('29,797', { center: true }), tc('29,797', { center: true }), tc('29,797', { center: true })]),
        tr([tc('Overall GC content (%)'), tc('36.2', { center: true }), tc('36.2', { center: true }), tc('~36.2', { center: true })]),
        tr([tc('LSC GC content (%)'), tc('34.0', { center: true }), tc('34.0', { center: true }), tc('34.0', { center: true })]),
        tr([tc('SSC GC content (%)'), tc('30.0', { center: true }), tc('30.0', { center: true }), tc('~30.0', { center: true })]),
        tr([tc('IR GC content (%)'), tc('41.0', { center: true }), tc('41.0', { center: true }), tc('~41.0', { center: true })]),
      ], [3000, 1800, 1800, 2400]),

      // ==========================================
      // 3.6 Gene Content and Annotation
      // ==========================================
      new Paragraph({
        children: [new TextRun({ text: '3.6 Gene Content and Annotation', bold: true, size: 26, font: 'Times New Roman' })],
        spacing: { before: 200, after: 100 },
      }),

      pRuns([
        tx('Annotation of both KS and KB chloroplast genomes using GeSeq identified a total of 111 genes, comprising 79 protein-coding genes, four ribosomal RNA (rRNA) genes, and 28 transfer RNA (tRNA) genes. This gene content is identical to that reported for the published '),
        it('K. galanga '),
        tx('reference genome (Li, Zhao and Liu, 2019). Of the 79 protein-coding genes, 78 were included in subsequent codon usage analyses; clpP1 was excluded because its annotated exon boundary coordinates yielded a total coding length of 622 bp that is not divisible by three, preventing unambiguous codon partitioning. This discrepancy reflects an annotation boundary convention that requires further verification against the original reference annotation.'),
      ]),

      pRuns([
        tx('Several genes were identified as containing introns, including '),
        it('rps12'),
        tx(', '),
        it('ycf3 (pafI)'),
        tx(', and '),
        it('clpP1'),
        tx('. The trans-spliced gene '),
        it('rps12 '),
        tx('exhibited non-adjacent exon coordinates consistent with its known trans-splicing mechanism in angiosperm plastomes. The gene '),
        it('ycf1 '),
        tx('was found to span the SSC/IR boundary at both junctions, with a full-length copy at one boundary and a truncated pseudogene-like copy at the other, a pattern well-documented in Zingiberaceae and other monocot chloroplast genomes (Li, Zhao and Liu, 2019). Gene nomenclature largely followed the GeSeq annotation, with five loci named differently from the published reference; these were reconciled by genomic position and flanking-gene context (e.g., GeSeq '),
        it('pafII '),
        tx('corresponds to '),
        it('ycf4 '),
        tx('in the reference annotation).'),
      ]),

      // ==========================================
      // 3.7 Codon Usage and RSCU
      // ==========================================
      new Paragraph({
        children: [new TextRun({ text: '3.7 Codon Usage and Relative Synonymous Codon Usage (RSCU)', bold: true, size: 26, font: 'Times New Roman' })],
        spacing: { before: 200, after: 100 },
      }),

      pRuns([
        tx('Codon usage analysis was performed on 78 protein-coding genes (clpP1 excluded), encompassing a total of 22,645 codons across 67,935 bp of coding sequence. Because KS and KB translate identically across all annotated protein-coding genes, a single shared codon table was compiled and applied to both genomes. Relative synonymous codon usage (RSCU) values were calculated for each synonymous codon family (Table 6). The analysis revealed a pronounced bias towards A- and U-ending codons, consistent with the AT-rich nature of chloroplast genomes across land plants.'),
      ]),

      pRuns([
        tx('Among the 61 sense codons, 45 showed RSCU values greater than 1.0, indicating preferential usage. The highest RSCU value was recorded for UUA (Leu; RSCU = 2.01), followed by AGA (Arg; RSCU = 1.93) and GCU (Ala; RSCU = 1.86). Other highly preferred codons included UCU (Ser; RSCU = 1.72), GAU (Asp; RSCU = 1.65), CCU (Pro; RSCU = 1.65), GGA (Gly; RSCU = 1.62), ACU (Thr; RSCU = 1.62), CAU (His; RSCU = 1.57), UGU (Cys; RSCU = 1.59), UAU (Tyr; RSCU = 1.58), CAA (Gln; RSCU = 1.56), AAU (Asn; RSCU = 1.56), GAA (Glu; RSCU = 1.53), GUA (Val; RSCU = 1.55), and AAA (Lys; RSCU = 1.51). Conversely, codons ending in G or C were consistently underrepresented (RSCU < 1.0), particularly GCG (Ala; RSCU = 0.33), GGC (Gly; RSCU = 0.33), CUG (Leu; RSCU = 0.32), and AGC (Ser; RSCU = 0.30). No codon showed complete absence of usage. Among the three stop codons, UAA was preferentially used (RSCU = 1.68) over UAG (RSCU = 0.78) and UGA (RSCU = 0.55).'),
      ]),

      caption('Table 6. Relative synonymous codon usage (RSCU) values for the 78 protein-coding genes of Kaempferia galanga (KS = KB). Codons with RSCU > 1.5 are highlighted in bold. Analysis based on 22,645 codons (67,935 bp); clpP1 excluded. Genetic code: plastid (Table 11).'),

      makeTable([
        tr([
          tc('Amino Acid', { header: true }),
          tc('Codon', { header: true, center: true }),
          tc('Count', { header: true, center: true }),
          tc('RSCU', { header: true, center: true }),
          tc('Amino Acid', { header: true }),
          tc('Codon', { header: true, center: true }),
          tc('Count', { header: true, center: true }),
          tc('RSCU', { header: true, center: true }),
        ]),
        tr([tc('Ala'), tc('GCU', { center: true }), tc('566', { center: true }), tc('1.86*', { center: true, bold: true }), tc('Leu'), tc('UUA', { center: true }), tc('789', { center: true }), tc('2.01*', { center: true, bold: true })]),
        tr([tc(''), tc('GCA', { center: true }), tc('373', { center: true }), tc('1.22', { center: true }), tc(''), tc('UUG', { center: true }), tc('489', { center: true }), tc('1.25', { center: true })]),
        tr([tc(''), tc('GCC', { center: true }), tc('179', { center: true }), tc('0.59', { center: true }), tc(''), tc('CUU', { center: true }), tc('490', { center: true }), tc('1.25', { center: true })]),
        tr([tc(''), tc('GCG', { center: true }), tc('102', { center: true }), tc('0.33', { center: true }), tc(''), tc('CUA', { center: true }), tc('312', { center: true }), tc('0.80', { center: true })]),
        tr([tc('Arg'), tc('AGA', { center: true }), tc('432', { center: true }), tc('1.93*', { center: true, bold: true }), tc(''), tc('CUC', { center: true }), tc('145', { center: true }), tc('0.37', { center: true })]),
        tr([tc(''), tc('CGU', { center: true }), tc('318', { center: true }), tc('1.42', { center: true }), tc(''), tc('CUG', { center: true }), tc('126', { center: true }), tc('0.32', { center: true })]),
        tr([tc(''), tc('CGA', { center: true }), tc('294', { center: true }), tc('1.31', { center: true }), tc('Lys'), tc('AAA', { center: true }), tc('928', { center: true }), tc('1.51*', { center: true, bold: true })]),
        tr([tc(''), tc('AGG', { center: true }), tc('135', { center: true }), tc('0.60', { center: true }), tc(''), tc('AAG', { center: true }), tc('299', { center: true }), tc('0.49', { center: true })]),
        tr([tc(''), tc('CGG', { center: true }), tc('88', { center: true }), tc('0.39', { center: true }), tc('Met'), tc('AUG', { center: true }), tc('528', { center: true }), tc('1.00', { center: true })]),
        tr([tc(''), tc('CGC', { center: true }), tc('76', { center: true }), tc('0.34', { center: true }), tc('Asn'), tc('AAU', { center: true }), tc('841', { center: true }), tc('1.56*', { center: true, bold: true })]),
        tr([tc('Asn'), tc('AAU', { center: true }), tc('841', { center: true }), tc('1.56*', { center: true, bold: true }), tc(''), tc('AAC', { center: true }), tc('240', { center: true }), tc('0.44', { center: true })]),
        tr([tc('Asp'), tc('GAU', { center: true }), tc('734', { center: true }), tc('1.65*', { center: true, bold: true }), tc('Pro'), tc('CCU', { center: true }), tc('381', { center: true }), tc('1.65*', { center: true, bold: true })]),
        tr([tc(''), tc('GAC', { center: true }), tc('157', { center: true }), tc('0.35', { center: true }), tc(''), tc('CCA', { center: true }), tc('259', { center: true }), tc('1.12', { center: true })]),
        tr([tc('Cys'), tc('UGU', { center: true }), tc('208', { center: true }), tc('1.59*', { center: true, bold: true }), tc(''), tc('CCC', { center: true }), tc('176', { center: true }), tc('0.76', { center: true })]),
        tr([tc(''), tc('UGC', { center: true }), tc('53', { center: true }), tc('0.41', { center: true }), tc(''), tc('CCG', { center: true }), tc('107', { center: true }), tc('0.46', { center: true })]),
        tr([tc('Glu'), tc('GAA', { center: true }), tc('921', { center: true }), tc('1.53*', { center: true, bold: true }), tc('Gln'), tc('CAA', { center: true }), tc('611', { center: true }), tc('1.56*', { center: true, bold: true })]),
        tr([tc(''), tc('GAG', { center: true }), tc('281', { center: true }), tc('0.47', { center: true }), tc(''), tc('CAG', { center: true }), tc('173', { center: true }), tc('0.44', { center: true })]),
        tr([tc('Phe'), tc('UUU', { center: true }), tc('845', { center: true }), tc('1.33', { center: true }), tc('Ser'), tc('UCU', { center: true }), tc('497', { center: true }), tc('1.72*', { center: true, bold: true })]),
        tr([tc(''), tc('UUC', { center: true }), tc('426', { center: true }), tc('0.67', { center: true }), tc(''), tc('AGU', { center: true }), tc('381', { center: true }), tc('1.32', { center: true })]),
        tr([tc('Gly'), tc('GGA', { center: true }), tc('623', { center: true }), tc('1.62*', { center: true, bold: true }), tc(''), tc('UCA', { center: true }), tc('345', { center: true }), tc('1.19', { center: true })]),
        tr([tc(''), tc('GGU', { center: true }), tc('547', { center: true }), tc('1.42', { center: true }), tc(''), tc('UCC', { center: true }), tc('275', { center: true }), tc('0.95', { center: true })]),
        tr([tc(''), tc('GGG', { center: true }), tc('239', { center: true }), tc('0.62', { center: true }), tc(''), tc('UCG', { center: true }), tc('152', { center: true }), tc('0.53', { center: true })]),
        tr([tc(''), tc('GGC', { center: true }), tc('127', { center: true }), tc('0.33', { center: true }), tc(''), tc('AGC', { center: true }), tc('86', { center: true }), tc('0.30', { center: true })]),
        tr([tc('His'), tc('CAU', { center: true }), tc('425', { center: true }), tc('1.57*', { center: true, bold: true }), tc('Thr'), tc('ACU', { center: true }), tc('463', { center: true }), tc('1.62*', { center: true, bold: true })]),
        tr([tc(''), tc('CAC', { center: true }), tc('117', { center: true }), tc('0.43', { center: true }), tc(''), tc('ACA', { center: true }), tc('364', { center: true }), tc('1.27', { center: true })]),
        tr([tc('Ile'), tc('AUU', { center: true }), tc('1003', { center: true }), tc('1.50', { center: true }), tc(''), tc('ACC', { center: true }), tc('197', { center: true }), tc('0.69', { center: true })]),
        tr([tc(''), tc('AUA', { center: true }), tc('645', { center: true }), tc('0.96', { center: true }), tc(''), tc('ACG', { center: true }), tc('122', { center: true }), tc('0.43', { center: true })]),
        tr([tc(''), tc('AUC', { center: true }), tc('359', { center: true }), tc('0.54', { center: true }), tc('Tyr'), tc('UAU', { center: true }), tc('680', { center: true }), tc('1.58*', { center: true, bold: true })]),
        tr([tc(''), tc('', { center: true }), tc('', { center: true }), tc('', { center: true }), tc(''), tc('UAC', { center: true }), tc('183', { center: true }), tc('0.42', { center: true })]),
        tr([tc('Trp'), tc('UGG', { center: true }), tc('396', { center: true }), tc('1.00', { center: true }), tc('Val'), tc('GUU', { center: true }), tc('462', { center: true }), tc('1.47', { center: true })]),
        tr([tc(''), tc('', { center: true }), tc('', { center: true }), tc('', { center: true }), tc(''), tc('GUA', { center: true }), tc('488', { center: true }), tc('1.55*', { center: true, bold: true })]),
        tr([tc('Stop'), tc('UAA', { center: true }), tc('43', { center: true }), tc('1.68*', { center: true, bold: true }), tc(''), tc('GUC', { center: true }), tc('141', { center: true }), tc('0.45', { center: true })]),
        tr([tc(''), tc('UAG', { center: true }), tc('20', { center: true }), tc('0.78', { center: true }), tc(''), tc('GUG', { center: true }), tc('169', { center: true }), tc('0.54', { center: true })]),
        tr([tc(''), tc('UGA', { center: true }), tc('14', { center: true }), tc('0.55', { center: true }), tc(''), tc('', { center: true }), tc('', { center: true }), tc('', { center: true })]),
      ], [1200, 900, 900, 900, 1200, 900, 900, 900]),

      new Paragraph({
        children: [new TextRun({ text: '*RSCU > 1.5 (preferred codons). Stop codon RSCU computed within the three-codon stop family.', size: 20, font: 'Times New Roman', italics: true })],
        spacing: { after: 160 },
      }),

      // ==========================================
      // 3.8 SSR Analysis
      // ==========================================
      new Paragraph({
        children: [new TextRun({ text: '3.8 Simple Sequence Repeat (SSR) Analysis', bold: true, size: 26, font: 'Times New Roman' })],
        spacing: { before: 200, after: 100 },
      }),

      pRuns([
        tx('Simple sequence repeats (SSRs) were identified in all three genomes using MISA-web with thresholds of ≥8, ≥5, ≥4, ≥3, ≥3, and ≥3 repeat units for mono-, di-, tri-, tetra-, penta-, and hexanucleotide SSRs, respectively, with a maximum interruption of 100 bp for compound SSR detection. A total of 239 SSRs were identified in both the KS and KB genomes, and 240 SSRs in the published '),
        it('K. galanga '),
        tx('reference genome (NC_040851.1). The number of SSRs in compound formations was 56 for KS and KB, and 58 for the reference (Table 7).'),
      ]),

      pRuns([
        tx('Across all three genomes, mononucleotide repeats were the most abundant SSR class, accounting for 177 SSRs in each genome (74.1% of total for KS and KB; 73.8% for the reference). Dinucleotide repeats were the second most common class (KS: 31; KB: 31; reference: 32), followed by tetranucleotide repeats (21 in each), trinucleotide repeats (6 in each), pentanucleotide repeats (3 in each), and hexanucleotide repeats (1 in each) (Table 7). SSR density was 1.46 SSRs per kilobase for all three genomes.'),
      ]),

      pRuns([
        tx('Strand-specific motif counts appeared to differ between KS and KB for mononucleotide SSRs (e.g., A: KS = 77, KB = 85; T: KS = 90, KB = 82). However, when motifs were collapsed by reverse complement (treating A and T as a single A/T class, etc.), KS and KB showed identical distributions across every repeat class (Table 8). This concordance confirms that the apparent strand-level differences reflect an annotation orientation artifact arising from the known SSC-region strand flip in the KB assembly, rather than genuine sequence differences between the two morphotypes. Accordingly, complementary-collapsed SSR motif frequencies are reported as the authoritative comparison.'),
      ]),

      pRuns([
        tx('Among the complementary-collapsed motif classes, the A/T mononucleotide class was the most frequently observed, with 167 SSRs in each of KS and KB and 167 in the reference. The C/G class accounted for 10 SSRs across all three genomes. For dinucleotide SSRs, AT/AT was the dominant class (KS and KB: 29; reference: 30), with AG/CT accounting for only 2 SSRs in all genomes. Among trinucleotide SSRs, AAT/ATT (3 SSRs) and AAG/CTT (2 SSRs) were the most common classes. The sole hexanucleotide SSR was of the AATATT/AATATT class in all three genomes. The consistent SSR profiles across KS, KB, and the reference further support the high level of conservation in '),
        it('K. galanga '),
        tx('chloroplast genome microsatellite content.'),
      ]),

      caption('Table 7. Distribution of simple sequence repeats (SSRs) by repeat type in narrow-leaf (KS), broad-leaf (KB), and reference (NC_040851.1) Kaempferia galanga chloroplast genomes.'),

      makeTable([
        tr([
          tc('Repeat Type', { header: true }),
          tc('KS (n)', { header: true, center: true }),
          tc('KB (n)', { header: true, center: true }),
          tc('KG Reference (n)', { header: true, center: true }),
          tc('KS Density (/kb)', { header: true, center: true }),
          tc('KB Density (/kb)', { header: true, center: true }),
        ]),
        tr([tc('Mononucleotide'), tc('177', { center: true }), tc('177', { center: true }), tc('177', { center: true }), tc('1.08', { center: true }), tc('1.08', { center: true })]),
        tr([tc('Dinucleotide'), tc('31', { center: true }), tc('31', { center: true }), tc('32', { center: true }), tc('0.19', { center: true }), tc('0.19', { center: true })]),
        tr([tc('Trinucleotide'), tc('6', { center: true }), tc('6', { center: true }), tc('6', { center: true }), tc('0.04', { center: true }), tc('0.04', { center: true })]),
        tr([tc('Tetranucleotide'), tc('21', { center: true }), tc('21', { center: true }), tc('21', { center: true }), tc('0.13', { center: true }), tc('0.13', { center: true })]),
        tr([tc('Pentanucleotide'), tc('3', { center: true }), tc('3', { center: true }), tc('3', { center: true }), tc('0.02', { center: true }), tc('0.02', { center: true })]),
        tr([tc('Hexanucleotide'), tc('1', { center: true }), tc('1', { center: true }), tc('1', { center: true }), tc('<0.01', { center: true }), tc('<0.01', { center: true })]),
        tr([tc('Total SSRs', { bold: true }), tc('239', { center: true, bold: true }), tc('239', { center: true, bold: true }), tc('240', { center: true, bold: true }), tc('1.46', { center: true, bold: true }), tc('1.46', { center: true, bold: true })]),
        tr([tc('Compound SSRs'), tc('56', { center: true }), tc('56', { center: true }), tc('58', { center: true }), tc('–', { center: true }), tc('–', { center: true })]),
      ], [2200, 1100, 1100, 1800, 1400, 1400]),

      caption('Table 8. Complementary-collapsed SSR motif class frequencies for KS, KB, and the reference Kaempferia galanga chloroplast genomes. Motifs are merged with their reverse complements (e.g., A and T → A/T).'),

      makeTable([
        tr([
          tc('Repeat Class', { header: true }),
          tc('Motif Class', { header: true }),
          tc('KS (n)', { header: true, center: true }),
          tc('KB (n)', { header: true, center: true }),
          tc('KG Reference (n)', { header: true, center: true }),
        ]),
        tr([tc('Mononucleotide'), tc('A/T'), tc('167', { center: true }), tc('167', { center: true }), tc('167', { center: true })]),
        tr([tc(''), tc('C/G'), tc('10', { center: true }), tc('10', { center: true }), tc('10', { center: true })]),
        tr([tc('Dinucleotide'), tc('AT/AT'), tc('29', { center: true }), tc('29', { center: true }), tc('30', { center: true })]),
        tr([tc(''), tc('AG/CT'), tc('2', { center: true }), tc('2', { center: true }), tc('2', { center: true })]),
        tr([tc('Trinucleotide'), tc('AAT/ATT'), tc('3', { center: true }), tc('3', { center: true }), tc('3', { center: true })]),
        tr([tc(''), tc('AAG/CTT'), tc('2', { center: true }), tc('2', { center: true }), tc('2', { center: true })]),
        tr([tc(''), tc('AGG/CCT'), tc('1', { center: true }), tc('1', { center: true }), tc('1', { center: true })]),
        tr([tc('Tetranucleotide'), tc('AAAT/ATTT'), tc('12', { center: true }), tc('12', { center: true }), tc('12', { center: true })]),
        tr([tc(''), tc('AAAG/CTTT'), tc('4', { center: true }), tc('4', { center: true }), tc('4', { center: true })]),
        tr([tc(''), tc('AATG/ATTC'), tc('2', { center: true }), tc('2', { center: true }), tc('2', { center: true })]),
        tr([tc(''), tc('AATT/AATT'), tc('1', { center: true }), tc('1', { center: true }), tc('1', { center: true })]),
        tr([tc(''), tc('AACT/AGTT'), tc('1', { center: true }), tc('1', { center: true }), tc('1', { center: true })]),
        tr([tc(''), tc('AAAC/GTTT'), tc('1', { center: true }), tc('1', { center: true }), tc('1', { center: true })]),
        tr([tc('Pentanucleotide'), tc('AATAT/ATATT'), tc('1', { center: true }), tc('1', { center: true }), tc('1', { center: true })]),
        tr([tc(''), tc('AAAAT/ATTTT'), tc('1', { center: true }), tc('1', { center: true }), tc('1', { center: true })]),
        tr([tc(''), tc('AACCC/GGGTT'), tc('1', { center: true }), tc('1', { center: true }), tc('1', { center: true })]),
        tr([tc('Hexanucleotide'), tc('AATATT/AATATT'), tc('1', { center: true }), tc('1', { center: true }), tc('1', { center: true })]),
        tr([tc('Total', { bold: true }), tc(''), tc('239', { center: true, bold: true }), tc('239', { center: true, bold: true }), tc('240', { center: true, bold: true })]),
      ], [1800, 2200, 1600, 1600, 1800]),

      // ==========================================
      // 3.9 Comparative Genomic Analysis
      // ==========================================
      new Paragraph({
        children: [new TextRun({ text: '3.9 Comparative Genomic Analysis: KS, KB, and the Published Reference Genome', bold: true, size: 26, font: 'Times New Roman' })],
        spacing: { before: 200, after: 100 },
      }),

      pRuns([
        tx('Whole-genome pairwise alignment of both KS and KB against the published '),
        it('K. galanga '),
        tx('reference genome (NC_040851.1) was performed using minimap2 (asm5 preset) on single-IR-copy (collinear) representations of each genome (i.e., LSC + IRb + SSC, with the redundant IRa excluded to avoid double-counting). Alignment revealed 99.87% overall sequence identity between {KS, KB} and the reference, with 39 total variant events distributed across the non-redundant 134,002 bp alignment (Table 9). These comprised 22 single nucleotide polymorphisms (SNPs), nine insertions totaling 68 bp, and eight deletions totaling 80 bp. Critically, at every variant position, KS and KB carried the identical allele; no variant distinguished KS from KB. All 39 events therefore represent sequence differences between the Taylor\'s Urban Farm plants (both morphotypes collectively) and the published reference accession, not between the two leaf-morphology variants.'),
      ]),

      pRuns([
        tx('Of the 39 variant events, 33 mapped to non-coding regions, including intergenic spacers and non-coding portions of gene loci. Six variants fell within protein-coding sequences across six distinct genes (Table 9). Amino acid consequences were resolved for these six: three were synonymous (no amino acid change) and three were nonsynonymous (single amino acid replacement). The genes and variant types were: '),
        it('rpoC2 '),
        tx('(SNP, nonsynonymous), '),
        it('ycf4 '),
        tx('(SNP, nonsynonymous), '),
        it('rpl33 '),
        tx('(SNP, nonsynonymous), '),
        it('rpl14 '),
        tx('(SNP, synonymous), '),
        it('rpl16 '),
        tx('(SNP, synonymous × 2). No coding indels were detected; all insertion and deletion events were confined to non-coding regions, predominantly in A/T-rich intergenic stretches. The IR region (IRb) harbored zero variants, consistent with the slower evolutionary rate of the inverted repeat under copy-correction.'),
      ]),

      caption('Table 9. Summary of sequence variants between the KS/KB Kaempferia galanga genomes and the published reference (NC_040851.1). All variants are shared between KS and KB (KS = KB allele at every position).'),

      makeTable([
        tr([
          tc('Variant Type', { header: true }),
          tc('Count', { header: true, center: true }),
          tc('Total Length (bp)', { header: true, center: true }),
          tc('In Coding Sequence', { header: true, center: true }),
          tc('In Non-coding Region', { header: true, center: true }),
        ]),
        tr([tc('SNP'), tc('22', { center: true }), tc('–', { center: true }), tc('6', { center: true }), tc('16', { center: true })]),
        tr([tc('Insertion'), tc('9', { center: true }), tc('68', { center: true }), tc('0', { center: true }), tc('9', { center: true })]),
        tr([tc('Deletion'), tc('8', { center: true }), tc('80', { center: true }), tc('0', { center: true }), tc('8', { center: true })]),
        tr([tc('Total', { bold: true }), tc('39', { center: true, bold: true }), tc('148', { center: true, bold: true }), tc('6', { center: true, bold: true }), tc('33', { center: true, bold: true })]),
      ], [2200, 1200, 1800, 1900, 1900]),

      // ==========================================
      // 3.10 Ka/Ks Analysis
      // ==========================================
      new Paragraph({
        children: [new TextRun({ text: '3.10 Synonymous and Non-synonymous Substitution Analysis', bold: true, size: 26, font: 'Times New Roman' })],
        spacing: { before: 200, after: 100 },
      }),

      pRuns([
        tx('To evaluate the selective pressure acting on protein-coding genes, synonymous (Ka) and non-synonymous (Ks) substitution rates were estimated using the Nei–Gojobori method with Jukes–Cantor correction. Analysis was restricted to 66 of the 79 annotated protein-coding genes for which the annotated CDS lengths were concordant between the GeSeq annotation and the published reference, enabling unambiguous codon-by-codon comparison. Thirteen genes were excluded due to annotation boundary discrepancies ('),
        it('clpP1'),
        tx(', '),
        it('rps12'),
        tx(', '),
        it('atpF'),
        tx(', '),
        it('rpoC1'),
        tx(', '),
        it('psbC'),
        tx(', '),
        it('ycf3'),
        tx(', '),
        it('ndhK'),
        tx(', '),
        it('petD'),
        tx(', '),
        it('rpl22'),
        tx(', '),
        it('rpl2'),
        tx(', '),
        it('ndhB'),
        tx(', '),
        it('ndhD'),
        tx(', '),
        it('ndhA'),
        tx('); whole-genome nucleotide alignment confirmed that no indels were present within any of these coding regions, indicating that the length differences reflect annotation convention differences rather than true biological variants.'),
      ]),

      pRuns([
        tx('Pooled across 66 genes (56,559 codon-site equivalents), three synonymous substitutions and three non-synonymous substitutions were observed. After Jukes–Cantor correction, the pooled Ka/Ks ratio was 0.28. This value, substantially less than 1.0, indicates that the protein-coding sequences of '),
        it('K. galanga '),
        tx('chloroplast genes are under purifying (negative) selection, consistent with the functional conservation expected for plastid housekeeping genes. Individual per-gene Ka/Ks ratios were not computed because 73 of the 79 genes showed zero substitutions relative to the reference and the remaining six genes each showed exactly one substitution, rendering per-gene statistics statistically uninformative at this level of sequence divergence.'),
      ]),

      // ==========================================
      // 3.11 IR Junction Analysis
      // ==========================================
      new Paragraph({
        children: [new TextRun({ text: '3.11 Inverted Repeat Junction Analysis', bold: true, size: 26, font: 'Times New Roman' })],
        spacing: { before: 200, after: 100 },
      }),

      pRuns([
        tx('The four IR junction regions (JLB: LSC/IRb; JSB: IRb/SSC; JSA: SSC/IRa; JLA: IRa/LSC) were examined in KS and compared with those of the published reference genome. In all four junctions, the same flanking genes were present in both genomes, at equivalent distances from the junction boundaries (within a few base pairs, consistent with minor differences in IR-boundary calling between annotation pipelines). No junction shifts were observed between the KS/KB genomes and the reference.'),
      ]),

      pRuns([
        tx('At the JLB junction, '),
        it('rps19 '),
        tx('flanked the LSC/IRb boundary. At the JSB junction, '),
        it('ndhF '),
        tx('approached the IRb/SSC boundary on the SSC side. The gene '),
        it('ycf1 '),
        tx('straddled both SSC-flanking junctions (JSB and JSA), with a full-length copy on one side and a truncated pseudogene-like copy on the other, a pattern that is well documented across Zingiberaceae and most monocot plastomes (Li, Zhao and Liu, 2019). The gene '),
        it('psbA '),
        tx('was located at the JLA junction. These junction configurations matched the canonical chloroplast quadripartite gene arrangement reported for related Zingiberaceae genomes, confirming that the '),
        it('K. galanga '),
        tx('chloroplast genomes assembled in this study are structurally consistent with the published reference and with the broader genomic architecture of the family.'),
      ]),

      new Paragraph({
        children: [new TextRun({ text: '3.12 Intraspecific Genomic Differentiation Between Narrow-Leaf and Broad-Leaf Morphotypes', bold: true, size: 26, font: 'Times New Roman' })],
        spacing: { before: 200, after: 100 },
      }),

      pRuns([
        tx('Across all analyses — whole-genome alignment, SNP/indel profiling, SSR content (complementary-collapsed), codon usage, gene content, and IR junction architecture — no nucleotide difference was detected between the KS (narrow-leaf) and KB (broad-leaf) '),
        it('K. galanga '),
        tx('morphotypes at the chloroplast genome level. The KS and KB assemblies were sequence-identical to each other (100% identity), with all 39 detected variant events relative to the published reference shared equally by both morphotypes. Complementary-collapsed SSR motif profiles were likewise identical between KS and KB across all six repeat-size classes. These results indicate that the morphological differences in leaf width observed between the two forms cultivated at Taylor\'s Urban Farm are not associated with detectable variation in the chloroplast genome under the analytical methods applied.'),
      ]),

    ],
  }],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUT_DIR + '/K_galanga_Results_Section.docx', buffer);
  console.log('Done: K_galanga_Results_Section.docx');
});
