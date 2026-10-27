const OUT_DIR = process.env.KG_OUTPUT_DIR || "output";
const IN_DIR = process.env.KG_INPUT_DIR || "data";
require("fs").mkdirSync(OUT_DIR, { recursive: true });
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, HeadingLevel, AlignmentType, ShadingType, BorderStyle, VerticalAlign, ImageRun
} = require("docx");

const TOTAL_W = 9016;

function cell(text, {header=false, width, align=AlignmentType.CENTER, fill} = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: header ? { type: ShadingType.CLEAR, fill: "1F3864" } : (fill ? {type:ShadingType.CLEAR, fill} : undefined),
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [ new Paragraph({ alignment: align, children: [ new TextRun({ text: String(text), bold: header, color: header ? "FFFFFF" : undefined, size: 19 }) ] }) ]
  });
}
function row(cells) { return new TableRow({ children: cells }); }
function makeTable(headers, widths, dataRows, fills=null) {
  return new Table({
    width: { size: TOTAL_W, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      row(headers.map((h,i)=>cell(h,{header:true,width:widths[i]}))),
      ...dataRows.map((r,ri) => row(r.map((v,i)=>cell(v,{width:widths[i], fill: fills?fills[ri]:undefined}))))
    ]
  });
}
function h1(text) { return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing:{before:280, after:120}, children:[new TextRun({text})] }); }
function h2(text) { return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing:{before:220, after:100}, children:[new TextRun({text})] }); }
function p(text, opts={}) { return new Paragraph({ spacing:{after:160}, ...opts, children:[new TextRun(text)] }); }
function bullet(text) { return new Paragraph({ spacing:{after:100}, bullet:{level:0}, children:[new TextRun(text)] }); }
function caption(text) { return new Paragraph({ spacing:{before:60, after:200}, children:[new TextRun({text, italics:true, size:18})] }); }

const imgBuf = fs.readFileSync(OUT_DIR + "/variant_map.png");

const doc = new Document({
  sections: [{
    properties: { page: { margin: { top:1440, bottom:1440, left:1440, right:1440 } } },
    children: [
      new Paragraph({ heading: HeadingLevel.TITLE, spacing:{after:80}, children:[new TextRun("KB/KS vs MK209001 Reference — Whole-genome Comparison")]}),
      new Paragraph({ spacing:{after:280}, children:[new TextRun({text:"Whole-genome alignment, variant list, coding differences and pooled Ka/Ks against the published K. galanga plastome (Li, Zhao & Liu 2019, Molecules 24(3):474)", italics:true, size:22})]}),
      p("Date: 24 July 2026"),
      p("Inputs: GeSeqJob-galanga_KB/KS_GenBank.gb (this project) + K galanga Ref MK209001.gb (user-supplied, DDBJ/NCBI NC_040851.1 equivalent)."),

      h1("Summary"),
      p("Because KB and KS were already shown to be 100% sequence-identical to each other (see KB_KS_Table1_and_QC_report.docx), this comparison uses one representative plastome against the published reference; every result applies equally to KB and KS."),
      p("Whole-genome alignment (minimap2/mappy, asm5 preset) against a single-IR-copy (collinear) representation of both genomes finds 99.87% identity overall: 39 variant events (22 SNPs, 9 insertions/68 bp, 8 deletions/80 bp) across 134,002-134,014 bp of non-redundant sequence. Only 6 of the 39 fall inside a coding sequence - 3 synonymous, 3 nonsynonymous - giving a pooled Ka/Ks of 0.28 (purifying selection, as expected for plastid housekeeping genes)."),

      h1("Whole-genome alignment"),
      p("Both genomes were reduced to a single-IR-copy (“collinear”) representation - LSC + IRb + SSC, dropping the redundant IRa - before alignment, since minimap2 otherwise reports the IR twice (it maps equally well to either duplicate copy), which double-counts and confuses a whole-genome comparison. KB's SSC block required reverse-complementing first (same orientation artifact noted against KS in the QC report); KS's collinear sequence aligns to the reference as a single 134,002 bp block with no strand flip, so KS is the more convenient sequence to reuse for any future alignment against public references."),
      makeTable(
        ["Block","Query (bp)","Reference (bp)","Strand","Identity"],
        [2200,1700,1900,1408,1808],
        [
          ["LSC + IRb","118,226","118,202","forward","99.90%"],
          ["SSC","15,776","15,812","KB: reverse / KS: forward","99.65%"],
          ["Combined (collinear)","134,002","134,014","-","99.87%"],
        ]
      ),
      caption("Identity = matched bases / aligned columns per minimap2's reported block statistics."),

      new Paragraph({
        children: [ new ImageRun({ type: "png", data: imgBuf, transformation: { width: 620, height: 180 } }) ],
        spacing: { before: 200, after: 80 },
        alignment: AlignmentType.CENTER,
      }),
      caption("Figure. All 39 variant events plotted on the reference's collinear coordinate axis. Note the IRb block carries zero variants - consistent with the IR's slower evolution under copy-correction - and most indels cluster in A/T-repeat intergenic stretches."),

      h1("Coding-sequence differences (6 of 79 genes)"),
      p("73 of 79 protein-coding genes are 100% identical to the reference. The remaining 6 each carry exactly one nucleotide difference:"),
      makeTable(
        ["Gene","Codon #","Ref codon (aa)","KB=KS codon (aa)","Effect"],
        [1400,1300,2100,2100,2116],
        [
          ["rpoC2","680 / 1379","CAG (Gln)","CAA (Gln)","synonymous"],
          ["rpl33","28 / 67","CCG (Pro)","CCA (Pro)","synonymous"],
          ["rpl16","23 / 137","CGC (Arg)","CGG (Arg)","synonymous"],
          ["ycf4","140 / 185","CGT (Arg)","TGT (Cys)","nonsynonymous (R140C)"],
          ["rpl14","98 / 123","ATT (Ile)","GTT (Val)","nonsynonymous (I98V)"],
          ["ycf1","1767 / 1822","GAT (Asp)","GGT (Gly)","nonsynonymous (D1767G)"],
        ]
      ),
      caption("ycf4 is annotated “pafII” in the GeSeq (KB/KS) files - see gene-naming note below."),

      h1("Pooled Ka/Ks (dN/dS)"),
      p("Individual per-gene Ka/Ks is not statistically meaningful here - 73 of 79 genes have zero substitutions and the other 6 have exactly one each, so a per-gene ratio is either 0, undefined, or driven by a single site. Instead, synonymous/nonsynonymous sites were counted (Nei-Gojobori) across all codons pooled from the 66 genes with matching annotated length between the two pipelines, then compared to the observed 3 synonymous / 3 nonsynonymous substitutions, with Jukes-Cantor correction:"),
      makeTable(
        ["Sites","Observed substitutions","Rate","Value"],
        [2400,2400,2100,2116],
        [
          ["Synonymous (S) ≈ 12,345","Sd = 3","Ks","0.000243"],
          ["Nonsynonymous (N) ≈ 44,214","Nd = 3","Ka","0.000068"],
          ["","","Ka/Ks","0.28"],
        ]
      ),
      caption("Pooled across 66 of 79 genes (56,559 codon-site-equivalents). Ka/Ks < 1 indicates purifying selection, consistent with expectation for plastid housekeeping genes at this very low divergence."),
      p("13 genes excluded from the pooled count: clpP1 (622 bp GeSeq call, not a multiple of 3 - see QC report), rps12 (see QC vignette below), and 11 genes where GeSeq's and the reference paper's annotations disagree on CDS length - atpF, rpoC1, psbC, ycf3/pafI, ndhK, petD, rpl22, rpl2, ndhB, ndhD, ndhA. The whole-genome nucleotide alignment above found zero indels inside any coding region, so these length differences are annotation-boundary conventions (start-codon choice, intron/exon boundary calls), not real indels - the underlying DNA matches; confirming the exact boundary each pipeline intended would need a manual check against MK209001's original submission notes, which is outside this pass."),

      h2("QC vignette: rps12 looked like a 7th coding difference - it wasn't"),
      p("A first pass flagged rps12 codon 116 as Gln→Lys. Investigating found GeSeq's exon2/exon3 boundary sits 1 bp earlier than the reference annotation's (231 vs 232 bp / 27 vs 26 bp - same 372 bp total). Direct comparison of the raw genomic sequence at that locus (not just the annotated exon) shows KB and the reference are byte-identical there; the apparent amino-acid change was a frameshift artifact from comparing two different exon-boundary conventions on identical DNA, not a real substitution. Excluded from the tables above."),

      h1("Gene-naming notes"),
      p("GeSeq and the reference publication name five loci differently - confirmed by matching genomic position and flanking-gene context, not just by name:"),
      makeTable(
        ["GeSeq (KB/KS)","Reference (MK209001)","Note"],
        [3000,3000,3016],
        [
          ["clpP1","clpP","naming convention only"],
          ["pafI","ycf3","modern function-based rename (Photosystem I Assembly Factor)"],
          ["pafII","ycf4","modern function-based rename"],
          ["pbf1","psbN","modern rename (“Photosystem Biogenesis Factor 1”)"],
          ["psbZ","lhbA","see flag below"],
        ]
      ),
      p("Flag: the reference's “lhbA” (position 39,003-39,192) sits at the exact locus and flanking-gene context (trnT-GGU - psbD - psbC - trnS-UGA - [this gene] - trnG - trnfM/trnM - rps14 - psaB, identical in both files) as GeSeq's psbZ. “lhbA” is otherwise a leghemoglobin gene symbol from legumes and has no known role in plastid biology - this looks like a mislabeling in the published reference's original annotation rather than a real alternative name, worth a footnote if this genome is cited by locus name in the manuscript."),

      h1("Bottom line"),
      p("KB/KS differ from the 2019 published reference at 39 sites genome-wide (99.87% identity) - modest, typical intraspecific-level divergence for an independently sequenced accession - with only 6 substitutions in coding sequence (half synonymous) and a purifying-selection signal (Ka/Ks = 0.28). Combined with the earlier finding that KB and KS are identical to each other, this places all detectable plastome variation in this study between {KB, KS} as a pair and the reference, not between the two morphotypes - reinforcing that if narrow-leaf vs broad-leaf is genetic, the chloroplast genome is not where it shows up."),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT_DIR + "/KB_KS_vs_MK209001_comparison_report.docx", buf);
  console.log("written");
});
