const OUT_DIR = process.env.KG_OUTPUT_DIR || "output";
const IN_DIR = process.env.KG_INPUT_DIR || "data";
require("fs").mkdirSync(OUT_DIR, { recursive: true });
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
} = require("docx");

const FONT = "Times New Roman";
const PAGE_W = 12240, MARGIN = 1080; // US Letter, narrower margins for wide tables
const USABLE_W = PAGE_W - 2 * MARGIN;

function cell(text, { header = false, width, italics = false, bold = false, align = AlignmentType.CENTER, shading } = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: shading ? { type: ShadingType.CLEAR, fill: shading } : (header ? { type: ShadingType.CLEAR, fill: "1F4E78" } : undefined),
    margins: { top: 60, bottom: 60, left: 80, right: 80 },
    children: [new Paragraph({
      alignment: align,
      children: [new TextRun({
        text, font: FONT, size: 19, bold: header || bold,
        italics, color: header ? "FFFFFF" : "000000",
      })],
    })],
  });
}

function row(cells) { return new TableRow({ children: cells }); }

function makeTable(headers, widths, rows) {
  return new Table({
    width: { size: USABLE_W, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      row(headers.map((h, i) => cell(h, { header: true, width: widths[i] }))),
      ...rows.map(r => row(r.map((v, i) => cell(String(v), { width: widths[i] })))),
    ],
  });
}

function title(text) {
  return new Paragraph({
    spacing: { before: 300, after: 80 },
    children: [new TextRun({ text, font: FONT, size: 22, bold: true })],
  });
}
function caption(text) {
  return new Paragraph({
    spacing: { after: 150 },
    children: [new TextRun({ text, font: FONT, size: 22, italics: true })],
  });
}
function note(text) {
  return new Paragraph({
    spacing: { before: 100, after: 80 },
    children: [new TextRun({ text, font: FONT, size: 17 })],
  });
}
function body(text) {
  return new Paragraph({
    spacing: { after: 150, line: 276 },
    alignment: AlignmentType.JUSTIFIED,
    children: [new TextRun({ text, font: FONT, size: 22 })],
  });
}
function heading(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 300, after: 150 },
    children: [new TextRun({ text, font: FONT, size: 26, bold: true, color: "1F4E78" })],
  });
}
function flagBox(lines) {
  return lines.map((text, i) => new Paragraph({
    spacing: { after: i === lines.length - 1 ? 200 : 60 },
    shading: { type: ShadingType.CLEAR, fill: "FCE4E4" },
    border: { left: { style: BorderStyle.SINGLE, size: 24, color: "C00000", space: 8 } },
    children: [new TextRun({ text, font: FONT, size: 19, italics: true, color: "7A0000" })],
  }));
}

// ---------------- TABLE 1 ----------------
const t1Headers = ["Region", "Length (bp)", "GC content (%)"];
const t1Widths = [4000, 3000, 3000];
const t1Rows = [
  ["Genome (total)", "163,799", "36.2 †"],
  ["Large single copy (LSC)", "88,429", "34"],
  ["Inverted repeat B (IRB)", "29,797", "41"],
  ["Small single copy (SSC)", "15,776", "30"],
  ["Inverted repeat A (IRA)", "29,797", "41"],
  ["Protein-coding genes (79 loci, 87 copies incl. IR duplicates) ‡", "≈94,139", "n/a *"],
  ["rRNA genes (4 loci, 10 copies)", "9,060", "n/a *"],
  ["tRNA genes (~28-32 copies)", "n/a *", "n/a *"],
];

// ---------------- TABLE 2 ----------------
const t2Headers = ["Category", "Gene names (‡ = duplicated in IR; * = contains intron(s))"];
const t2Widths = [3200, 6800];
const t2Rows = [
  ["Photosystem I", "psaA, psaB, psaC, psaI, psaJ"],
  ["Photosystem II", "psbA, psbB, psbC, psbD, psbE, psbF, psbH, psbI, psbJ, psbK, psbL, psbM, psbN (pbf1), psbT, psbZ (lhbA)"],
  ["Cytochrome b6/f complex", "petA, petB *, petD *, petG, petL, petN"],
  ["ATP synthase", "atpA, atpB, atpE, atpF *, atpH, atpI"],
  ["NADH dehydrogenase (ndh)", "ndhA *, ndhB ‡ *, ndhC, ndhD, ndhE, ndhF, ndhG, ndhH, ndhI, ndhJ, ndhK"],
  ["RuBisCO large subunit", "rbcL"],
  ["DNA-dependent RNA polymerase", "rpoA, rpoB, rpoC1 *, rpoC2"],
  ["Large-subunit ribosomal proteins", "rpl2 ‡ *, rpl14, rpl16 *, rpl20, rpl22, rpl23 ‡, rpl32, rpl33, rpl36"],
  ["Small-subunit ribosomal proteins", "rps2, rps3, rps4, rps7 ‡, rps8, rps11, rps12 ‡ *, rps14, rps15, rps16 *, rps18, rps19 ‡"],
  ["Other proteins", "accD, ccsA, cemA, clpP1 (clpP) *, infA, matK"],
  ["Proteins of unknown function", "ycf1 ‡, ycf2 ‡, pafI (ycf3) *, pafII (ycf4)"],
  ["Ribosomal RNA genes (4)", "rrn4.5 ‡, rrn5 ‡, rrn16 ‡, rrn23 ‡"],
  ["Transfer RNA genes (~28-32 copies across 22 anticodon types)", "trnA-UGC *, trnC-GCA, trnD-GUC, trnE-UUC, trnF-GAA, trnfM-CAU, trnG-GCC, trnG-UCC, trnH-GUG ‡, trnI-CAU, trnI-GAU *, trnK-UUU *, trnL-CAA ‡, trnL-UAA *, trnL-UAG, trnM-CAU (×4), trnN-GUU ‡, trnP-UGG, trnQ-UUG, trnR-ACG ‡, trnR-UCU, trnS-GGA, trnS-UGA, trnS-GCU, trnT-GGU, trnT-UGU, trnV-GAC ‡, trnV-UAC *, trnW-CCA, trnY-GUA"],
];

// ---------------- TABLE 3 ----------------
const t3Headers = ["Gene", "Location", "Exon I (bp)", "Intron I (bp)", "Exon II (bp)", "Intron II (bp)", "Exon III (bp)"];
const t3Widths = [1300, 1900, 1300, 1300, 1300, 1300, 1300];
const t3Rows = [
  ["rps16", "LSC", "40", "755", "212", "-", "-"],
  ["atpF", "LSC", "145", "831", "410", "-", "-"],
  ["rpoC1", "LSC", "432", "735", "1,623", "-", "-"],
  ["pafI (ycf3) †", "LSC", "124", "720", "230 / 228 †", "794", "153 / 155 †"],
  ["clpP1 (clpP)", "LSC", "71", "858", "292", "629", "259"],
  ["petB", "LSC", "6", "852", "642", "-", "-"],
  ["petD", "LSC", "8", "746", "475", "-", "-"],
  ["rpl16", "LSC", "9", "1,058", "402", "-", "-"],
  ["rpl2 (×2, IRA + IRB)", "IR", "391", "662", "431", "-", "-"],
  ["ndhB (×2, IRA + IRB)", "IR", "777", "700", "756", "-", "-"],
  ["rps12 (×2, IRA + IRB) ‡", "LSC + IR (trans-spliced)", "n/a ‡", "n/a ‡", "232", "540", "26"],
];

const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_W, height: 15840 },
        margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN },
      },
    },
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 100 },
        children: [new TextRun({
          text: "Chloroplast Genome Feature Tables — Kaempferia galanga (KS / KB)",
          font: FONT, size: 28, bold: true,
        })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [new TextRun({
          text: "Organized in the style of Tables 1-3, Zhang et al. 2019, Molecules 24(3):474 (PMC6385120)",
          font: FONT, size: 20, italics: true, color: "555555",
        })],
      }),

      ...flagBox([
        "All values below are identical for KS (narrow-leaf) and KB (broad-leaf) unless noted — consistent with " +
        "every other analysis run so far (SNPs/indels and SSR content also showed no confirmed difference between " +
        "the two morphotypes). Built from your uploaded 'ssr of kb and ks.xlsx' (genes, intron and exon, ks/KB, " +
        "regions tabs), cross-checked by matching each exon/intron to its parent gene via coordinate containment.",
      ]),

      heading("Table 1. Chloroplast genome region features"),
      makeTable(t1Headers, t1Widths, t1Rows),
      note("† Weighted average computed from the four regional GC% values already in your sheet (not independently " +
           "re-measured from sequence). * Codon-position nucleotide composition (1st/2nd/3rd position A/T/C/G%, as " +
           "in the reference Table 1) requires the raw genome FASTA sequences (KSt9cuoa.fasta / KBt9cusu.fasta) to " +
           "extract and translate every CDS — upload those and I can complete this. ‡ Protein-coding total excludes " +
           "rps12: its two IR copies have a corrupted join-location string in the source sheet (parsed as a " +
           "negative-length feature), so its true contribution (~800+ bp per copy, trans-spliced from the LSC) " +
           "isn't reliably computable from this export alone."),

      heading("Table 2. Genes identified in the chloroplast genome, by functional category"),
      makeTable(t2Headers, t2Widths, t2Rows),
      note("Naming note: your source sheet uses two different names for the same two loci across its own tabs — " +
           "the 'genes' tab calls them ycf3/ycf4, while the 'ks'/'KB'/'intron and exon' tabs call them pafI/pafII. " +
           "(pafI/pafII is the updated nomenclature for ycf3/ycf4 used in some recent plastid literature — same " +
           "genes, different name.) Pick one convention and use it consistently before this goes into the " +
           "manuscript. Similarly, clpP1 (annotation tabs) and clpP (genes tab) are the same locus."),

      heading("Table 3. Genes with introns: exon and intron lengths (bp)"),
      makeTable(t3Headers, t3Widths, t3Rows),
      note("‡ rps12 is trans-spliced: one exon lies in the LSC (~74 kb region) and is joined post-transcriptionally " +
           "to two IR-located exons connected by a conventional (cis) intron. The LSC exon's length could not be " +
           "resolved from this export — its GenBank-style location is a join() of two non-adjacent coordinate " +
           "ranges, which the coordinate-extraction script appears to have parsed as a single (invalid, negative-" +
           "length) span. Cross-check directly against the GFF3/GenBank annotation file for the true exon I length " +
           "(commonly ~114 bp in related plastid genomes, but confirm for yours rather than assume). † pafI (ycf3): " +
           "your source sheet lists two slightly different values for Exon II / Exon III (230/153 bp vs 228/155 bp, " +
           "a 2 bp shift at the splice boundary) but both the 'ks' and 'KB' tabs list both values side by side — I " +
           "could not determine from the sheet which value belongs to KS and which to KB. Worth resolving directly " +
           "against each genome's annotation before reporting, since if the 2 bp shift really is genome-specific, " +
           "it would be the only confirmed exon-boundary difference found between the two morphotypes anywhere in " +
           "this analysis. Three tRNA genes (trnA-UGC, trnL-UAA, trnV-UAC) are also annotated as intron-containing " +
           "(noted in the 'genes' tab) but their exon/intron lengths are not present in the current export."),

      heading("Other things worth a look while rebuilding these tables"),
      body(
        "Two CDS entries look like annotation artifacts rather than real biology, spotted while cross-checking: " +
        "petD appears twice with different lengths (1,229 bp, which is the unspliced span = 8 + 746 + 475, i.e. " +
        "exon+intron+exon added together — and 486 bp, close to but not exactly the true spliced length of 483 bp). " +
        "ndhK also appears twice (678 bp and 744 bp, a 66 bp difference) with no intron on record for either — this " +
        "may reflect an RNA-editing-created start/stop codon or simply two overlapping annotation calls. Neither " +
        "affects the three tables above, but both are worth a quick check against the GFF3 before finalizing gene " +
        "lengths elsewhere in the manuscript."
      ),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  require("fs").writeFileSync(OUT_DIR + "/Chloroplast_Genome_Tables_1-3.docx", buf);
  console.log("saved");
});
