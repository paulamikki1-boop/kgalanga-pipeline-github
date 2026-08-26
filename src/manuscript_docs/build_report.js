const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, HeadingLevel, AlignmentType, ShadingType, BorderStyle, VerticalAlign
} = require("docx");

const TOTAL_W = 9016;

function cell(text, {header=false, width, align=AlignmentType.CENTER, bold=false} = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: header ? { type: ShadingType.CLEAR, fill: "1F3864" } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [ new Paragraph({
      alignment: align,
      children: [ new TextRun({ text: String(text), bold: bold || header, color: header ? "FFFFFF" : undefined, size: header ? 19 : 19 }) ]
    }) ]
  });
}

function row(cells) { return new TableRow({ children: cells }); }

function makeTable(headers, widths, dataRows) {
  return new Table({
    width: { size: TOTAL_W, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      row(headers.map((h,i)=>cell(h,{header:true,width:widths[i]}))),
      ...dataRows.map(r => row(r.map((v,i)=>cell(v,{width:widths[i]}))))
    ]
  });
}

function h1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing:{before:280, after:120}, children:[new TextRun({text})] });
}
function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing:{before:220, after:100}, children:[new TextRun({text})] });
}
function p(runs, opts={}) {
  const children = Array.isArray(runs) ? runs.map(r => typeof r === "string" ? new TextRun(r) : new TextRun(r)) : [new TextRun(runs)];
  return new Paragraph({ spacing:{after:160}, ...opts, children });
}
function bullet(text) {
  return new Paragraph({ spacing:{after:100}, bullet:{level:0}, children:[new TextRun(text)] });
}
function caption(text) {
  return new Paragraph({ spacing:{before:60, after:200}, children:[new TextRun({text, italics:true, size:18})] });
}

const doc = new Document({
  sections: [{
    properties: { page: { margin: { top:1440, bottom:1440, left:1440, right:1440 } } },
    children: [

      new Paragraph({ heading: HeadingLevel.TITLE, spacing:{after:80}, children:[new TextRun("K. galanga KB vs KS Chloroplast Genome")]}),
      new Paragraph({ spacing:{after:280}, children:[new TextRun({text:"Codon-position composition (Table 1), annotation QC, and whole-genome identity check — from GeSeq GFF3/GenBank files only", italics:true, size:22})]}),
      p([{text:"Date: ", bold:true}, {text:"24 July 2026"}]),
      p([{text:"Input files: ", bold:true}, {text:"GeSeqJob-galanga_KB_GenBank.gb, GeSeqJob-galanga_KS_GenBank.gb (and matching GFF3+FASTA files)"}]),

      h1("Summary"),
      p("Table 1 (codon-position nucleotide composition) is produced directly from the GenBank annotations already on hand for KB (broad-leaf) and KS (narrow-leaf) K. galanga. The separate FASTA files flagged in the last session are not needed — GenBank format already carries the full 163,799 bp sequence plus exact CDS coordinates, so the coding sequences can be extracted directly."),
      p("Three annotation ambiguities flagged previously (rps12, petD/ndhK, ycf3/pafI) are resolved below by pulling their exact feature structure from these files and translating each candidate reading. As a bonus check, a full base-by-base comparison of the two entire plastomes (not a sample of variants) was also run."),

      h1("Table 1. Nucleotide composition at each codon position of protein-coding genes"),
      makeTable(
        ["Genome","Position","T(U)%","C%","A%","G%","A+T%"],
        [1288,1288,1288,1288,1288,1288,1288],
        [
          ["KB","1st","23.91","18.10","31.01","26.98","54.93"],
          ["KB","2nd","32.75","20.13","29.38","17.74","62.13"],
          ["KB","3rd","39.04","12.97","32.86","15.13","71.90"],
          ["KB","Overall","31.90","17.06","31.08","19.95","62.99"],
          ["KS","1st","23.91","18.10","31.01","26.98","54.93"],
          ["KS","2nd","32.75","20.13","29.38","17.74","62.13"],
          ["KS","3rd","39.04","12.97","32.86","15.13","71.90"],
          ["KS","Overall","31.90","17.06","31.08","19.95","62.99"],
        ]
      ),
      caption("n = 78 protein-coding genes, 22,645 codons (67,935 bp) per genome. clpP1 excluded (see below). KB and KS values are identical at every position because the two plastomes are 100% sequence-identical (Whole-genome identity check, below)."),

      p("Where GeSeq produced two overlapping candidate CDS calls for the same gene, the biologically valid reading was used, confirmed by translation (stop-codon / internal-stop check, genetic code table 11):"),
      bullet("ycf3 / pafI — both candidate exon2/exon3 boundaries (228/155 bp vs 230/153 bp) give the identical spliced sequence (507 bp / 169 codons); either is fine."),
      bullet("petD — 483 bp / 161-codon spliced form used (clean ORF, proper start and stop). The alternate 486 bp single-exon call contains 21 in-frame stop codons — an annotation artifact, not a real gene model."),
      bullet("ndhK — 678 bp / 226-codon form used. An alternate upstream start codon gives 744 bp / 248 codons; neither annotated interval includes a stop codon within it (common when a CDS feature stops at the last sense codon, with the stop immediately downstream) — worth a quick check against the MK209001 reference annotation to confirm which start the manuscript should cite."),
      bullet("clpP1 excluded from Table 1 — GeSeq's call is 622 bp (71 + 292 + 259 bp across 3 exons), identical in KB and KS, but not a multiple of 3, so it cannot be split into codons as annotated. Needs manual exon-boundary correction against a reference before it enters any codon-usage analysis."),

      h1("Table 2 (supplementary). Nucleotide composition by genome region"),
      makeTable(
        ["Region","n (bp)","A%","T%","G%","C%","GC%"],
        [1288,1288,1288,1288,1288,1288,1288],
        [
          ["Total – KB","163,799","31.56","32.37","17.89","18.18","36.07"],
          ["Total – KS","163,799","31.70","32.23","17.73","18.34","36.07"],
          ["LSC (KB = KS)","88,429","32.47","33.70","16.49","17.33","33.83"],
          ["IRb (KB = KS)","29,797","30.04","28.85","21.29","19.82","41.11"],
          ["SSC – KB","15,776","34.51","35.92","15.62","13.96","29.58"],
          ["SSC – KS","15,776","35.92","34.51","13.96","15.62","29.58"],
          ["IRa (KB = KS)","29,797","28.85","30.04","19.82","21.29","41.11"],
        ]
      ),
      caption("LSC/IRb/IRa are shown once because KB and KS are base-for-base identical in those regions. The small (~0.15%) difference between KB's and KS's Total row, and the mirrored A%↔T%, G%↔C% in the SSC row, are both explained below — they are not a biological difference."),

      h1("Whole-genome identity check (bonus)"),
      p("Both genomes share identical LSC (88,429 bp), IRb (29,797 bp), SSC (15,776 bp) and IRa (29,797 bp) boundaries — GeSeq placed the quadripartite junctions at exactly the same coordinates in both assemblies. KB's SSC block, however, is annotated on the opposite strand from KS's: its base composition is the exact mirror of KS's SSC (A%↔T%, G%↔C%), which is the expected signature of a pure reverse-complement, and matches the SSC-orientation artifact already noted from the coordinate-based comparison in the last session."),
      p("Reassembling both genomes in the same LSC–IRb–SSC–IRa frame (reverse-complementing KB's SSC to match KS's orientation) and comparing all 163,799 positions base-by-base found zero mismatches. As a sanity check, the identical comparison without that orientation correction finds 11,264 mismatches, all confined to the SSC block — confirming the pipeline genuinely detects differences where they exist, and that the zero-mismatch result is real rather than a script artifact."),
      p("This is a full, exhaustive comparison rather than a sample of variant sites. Combined with the CDS-level check (all 79 annotated protein-coding genes, including duplicated IR copies, translate identically between KB and KS), it confirms the KB and KS plastomes are indistinguishable at the sequence level — consistent with, and now considerably stronger than, the earlier 10-variant finding (where KB and KS shared the same allele at all 10 positions relative to the reference)."),

      h1("Resolved annotation items"),
      h2("rps12 (trans-spliced)"),
      p("Exon 1 (LSC) 114 bp + exon 2 (IR) 232 bp + exon 3 (IR) 26 bp = 372 bp / 124 codons, identical in KB and KS. The earlier “corrupted coordinates” were a parsing issue in the previous coordinate-diff script — a trans-spliced join spans non-adjacent regions, which a naive start/end subtraction mishandles. Biopython's location parser resolves it correctly."),
      h2("ycf1 / SSC orientation (bonus)"),
      p("KB carries the full-length ycf1 copy (5,466 bp) adjacent to one IR junction and the truncated copy (3,888 bp) at the other; KS has them at the mirrored positions. This is the same SSC-flip artifact, now confirmed at the single-gene level and quantitatively via the whole-genome check above — not a true structural rearrangement."),
      h2("ndhA (minor, not previously flagged)"),
      p("Both genomes carry the same 2 bp exon1/exon2 boundary ambiguity seen in ycf3/pafI. Both readings translate to the identical 363-aa protein in both KB and KS — inconsequential."),

      h1("Suggested next analyses"),
      p("Since KB and KS are now confirmed identical genome-wide, further KB-vs-KS comparison will not add information — the diagnostic-marker and divergence angle only makes sense against the published reference (MK209001 / NC_040851.1) from here. In priority order:"),
      bullet("Whole-genome alignment vs MK209001 (mVISTA, Shuffle-LAGAN) — already planned in the workflow doc; canonical single-sequence FASTA for KB and KS (oriented LSC–IRb–SSC–IRa) are ready now."),
      bullet("IR junction diagram (LSC/IRb/SSC/IRa, with flanking genes) — exact boundary coordinates were extracted above; the standard junction figure can be built directly from these files."),
      bullet("Ka/Ks (dN/dS) per gene, KB or KS vs MK209001 — the 78 clean, frame-correct CDS sets extracted here are ready to feed in directly."),
      bullet("Full codon usage / RSCU table (all 64 codons, not just position) — a direct extension of Table 1 using the same extracted CDS."),
      bullet("SSR / repeat mining on these sequences — resolves the mononucleotide-threshold (8 vs 10) question flagged earlier, directly on this data."),
      bullet("Two-way ANOVA / Kruskal-Wallis on the chloroplast-isolation absorbance data — needs the raw replicate values, not contained in these annotation files."),

    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/sessions/awesome-wizardly-hypatia/mnt/outputs/KB_KS_Table1_and_QC_report.docx", buf);
  console.log("written");
});
