const fs = require('fs');
const d = require('docx');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow,
        TableCell, WidthType, AlignmentType, ShadingType, BorderStyle,
        LevelFormat, PageOrientation } = d;

const R = JSON.parse(fs.readFileSync('doc1_data.json','utf8'));

const HDR = "2F5496", ALT = "F2F5FA";
const f = (x, n=2) => Number(x).toFixed(n);

function cell(text, {bold=false, shade=null, align="left", w=1200, size=18}={}) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: shade ? { type: ShadingType.CLEAR, fill: shade } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [ new Paragraph({
      alignment: align === "center" ? AlignmentType.CENTER
               : align === "right"  ? AlignmentType.RIGHT : AlignmentType.LEFT,
      children: [ new TextRun({ text: String(text), bold,
        color: shade === HDR ? "FFFFFF" : "000000", size }) ]
    })]
  });
}
function hcell(t, w) { return cell(t, {bold:true, shade:HDR, align:"center", w}); }

const P = (text, opts={}) => new Paragraph({
  spacing: { after: opts.after ?? 120, before: opts.before ?? 0 },
  alignment: opts.align ?? AlignmentType.LEFT,
  children: [ new TextRun({ text, bold: opts.bold, italics: opts.italics,
    size: opts.size ?? 20, color: opts.color, font: opts.font }) ]
});
const H = (text, lvl) => new Paragraph({ text, heading: lvl,
  spacing: { before: 260, after: 130 } });

// ── Table 1: codon-position composition ──────────────────────────────
const W = [1500,1150,1150,1150,1150,1300,1300];
const t1rows = [ new TableRow({ tableHeader: true, children: [
  hcell("Sample / position",W[0]), hcell("%T(U)",W[1]), hcell("%C",W[2]),
  hcell("%A",W[3]), hcell("%G",W[4]), hcell("%A+T",W[5]), hcell("%G+C",W[6]) ]}) ];

let band = false;
for (const s of ["KS","KB"]) {
  for (const [key,lbl] of [["1","1st position"],["2","2nd position"],
                           ["3","3rd position"],["all","All positions"]]) {
    const c = R.t1[s][key];
    const sh = band ? ALT : null;
    const isTot = key === "all";
    t1rows.push(new TableRow({ children: [
      cell(`${s} — ${lbl}`, {w:W[0], shade:sh, bold:isTot}),
      cell(f(c.T), {w:W[1], align:"center", shade:sh, bold:isTot}),
      cell(f(c.C), {w:W[2], align:"center", shade:sh, bold:isTot}),
      cell(f(c.A), {w:W[3], align:"center", shade:sh, bold:isTot}),
      cell(f(c.G), {w:W[4], align:"center", shade:sh, bold:isTot}),
      cell(f(c.AT),{w:W[5], align:"center", shade:sh, bold:isTot}),
      cell(f(c.GC),{w:W[6], align:"center", shade:sh, bold:isTot}),
    ]}));
    band = !band;
  }
}

// ── Table 2: region composition ──────────────────────────────────────
const W2 = [1400,1050,1150,1150,1150,1150,1200,1200];
const t2rows = [ new TableRow({ tableHeader: true, children: [
  hcell("Sample",W2[0]), hcell("Region",W2[1]), hcell("Length (bp)",W2[2]),
  hcell("%A",W2[3]), hcell("%T",W2[4]), hcell("%C",W2[5]), hcell("%G",W2[6]),
  hcell("%A+T",W2[7]) ]}) ];

const REGLEN = { genome:163799, LSC:88429, IRb:29797, SSC:15776, IRa:29797 };
band = false;
for (const s of ["KS","KB"]) {
  for (const reg of ["genome","LSC","IRb","SSC","IRa"]) {
    const c = R.rc[s][reg]; if (!c) continue;
    const sh = band ? ALT : null;
    t2rows.push(new TableRow({ children: [
      cell(s,{w:W2[0], shade:sh}),
      cell(reg === "genome" ? "Whole genome" : reg, {w:W2[1], shade:sh,
           bold: reg==="genome"}),
      cell(REGLEN[reg].toLocaleString(), {w:W2[2], align:"center", shade:sh}),
      cell(f(c.A),{w:W2[3], align:"center", shade:sh}),
      cell(f(c.T),{w:W2[4], align:"center", shade:sh}),
      cell(f(c.C),{w:W2[5], align:"center", shade:sh}),
      cell(f(c.G),{w:W2[6], align:"center", shade:sh}),
      cell(f(c.A + c.T),{w:W2[7], align:"center", shade:sh}),
    ]}));
    band = !band;
  }
}

// ── Table 3: resolved annotation issues ──────────────────────────────
const W3 = [1300,1500,3400,2700];
const issueRows = [ new TableRow({ tableHeader: true, children: [
  hcell("Gene",W3[0]), hcell("Issue type",W3[1]),
  hcell("Detail",W3[2]), hcell("Resolution",W3[3]) ]}) ];

const ISSUES = [
  ["ycf1","Two candidate CDS calls, both clean ORFs, different lengths",
   "Chloe called a 3,888 bp copy lying entirely inside IRb; the merged Chloe+blatX call gave 5,466 bp spanning the SSC/IRa junction. Both start MIFKSFLLGN and have no internal stops.",
   "Kept the 5,466 bp full-length copy. The 3,888 bp IRb version is the truncated pseudogenic copy (ycf1 normally straddles JSB/JSA), not an independent gene."],
  ["ndhA","Two clean ORFs, identical length, 1 bp exon-boundary shift",
   "blatX and Chloe disagree by 2 bp at the intron boundary (exon 1 end / exon 2 start). Spliced products differ at a single position (nt 552, T vs C) but are both 1,092 bp.",
   "Inconsequential — both spliced sequences translate to an identical protein; the difference is a synonymous 3rd-codon position. Kept the blatX call."],
  ["clpP1 (=clpP)","CDS length not a multiple of 3 — EXCLUDED",
   "GeSeq called clpP1 at 622 bp across three exons. 622 / 3 = 207.33, so the reading frame cannot be resolved; the reference annotates clpP at 621 bp.",
   "Excluded from all codon-based analyses (Table 1 composition, RSCU, Ka/Ks). This is a GeSeq exon-boundary error, not a real frameshift — see the DNA-level check in the reference-comparison document."],
  ["ndhK","No candidate with a fully clean ORF",
   "blatX call = 678 bp (starts MNLIE), Chloe call = 744 bp (starts MVLTK). Both are divisible by 3 and free of internal stops, but neither terminates in a stop codon within the annotated span.",
   "Kept the longer 744 bp Chloe call. Reference annotates 753 bp, so both GeSeq calls are short at the 3' end. Excluded from the Ka/Ks pool on length-mismatch grounds."],
  ["rpl2","No candidate with a clean start codon",
   "Both GeSeq calls give 822 bp beginning TAIHLYKT (Thr start); the reference gives 828 bp beginning IHLYKTST. Neither begins with Met.",
   "Kept the 822 bp call. rpl2 uses an ACG start codon edited to AUG post-transcriptionally in many plastids, so the absent Met is expected. Excluded from Ka/Ks (length mismatch)."],
  ["rps12","Trans-spliced, multiple location strings",
   "rps12 is trans-spliced with exon 1 in the LSC and exons 2–3 in the IR; multiple identical calls arise from the IR duplication.",
   "Deduplicated by location string; single copy retained. Feature.extract() handles the trans-splice join correctly."],
  ["rps7, rps19, rpl23, ycf2, ndhB, pafI","Duplicate calls from IR duplication",
   "Each gene appears twice (once per IR copy) and in some cases twice more from the two sub-annotators. All spliced sequences are identical.",
   "Deduplicated to one copy per gene, matching the single-copy convention used for the 'N protein-coding genes' count in the literature."],
];
band = false;
for (const [g, t, det, res] of ISSUES) {
  const sh = band ? ALT : null;
  issueRows.push(new TableRow({ children: [
    cell(g,{w:W3[0], shade:sh, bold:true, size:17}),
    cell(t,{w:W3[1], shade:sh, size:16}),
    cell(det,{w:W3[2], shade:sh, size:16}),
    cell(res,{w:W3[3], shade:sh, size:16}),
  ]}));
  band = !band;
}

// ── Table 4: gene naming ─────────────────────────────────────────────
const W4 = [1800,1800,2700,2600];
const nameRows = [ new TableRow({ tableHeader: true, children: [
  hcell("GeSeq name (KS/KB)",W4[0]), hcell("MK209001 name",W4[1]),
  hcell("Positional evidence",W4[2]), hcell("Verdict",W4[3]) ]}) ];
const NAMES = [
  ["pafI","ycf3","Same locus, LSC. Both 507/513 bp, 3 exons.",
   "Synonym. pafI is the current name (photosystem I assembly factor I)."],
  ["pafII","ycf4","Same locus, LSC, adjacent to pafI/ycf3.",
   "Synonym. pafII = photosystem I assembly factor II."],
  ["pbf1","psbN","Same locus, LSC, within the psbB–psbT–psbH cluster.",
   "Synonym. pbf1 = PSII biogenesis factor 1."],
  ["clpP1","clpP","Same locus, LSC.","Synonym (numbering convention only)."],
  ["psbZ","lhbA","Identical 189 bp DNA at KS 39,025–39,214 vs Ref 39,003–39,192; identical 62 aa protein (MTIAFQLAVFALIATSSVLLISVPVVFASSDNWSSNKNIVFSGTSLWIGLVFLVAILNSLIS).",
   "MISLABELLING in MK209001. 'lhbA' is a light-harvesting-like symbol with no standard plastid assignment at this locus; the gene is psbZ (PSII protein Z). GeSeq is correct."],
];
band = false;
for (const [a,b,c2,v] of NAMES) {
  const sh = band ? ALT : null;
  const isFlag = a === "psbZ";
  nameRows.push(new TableRow({ children: [
    cell(a,{w:W4[0], shade:sh, bold:true, size:17}),
    cell(b,{w:W4[1], shade:sh, size:17}),
    cell(c2,{w:W4[2], shade:sh, size:16}),
    cell(v,{w:W4[3], shade:sh, size:16, bold:isFlag}),
  ]}));
  band = !band;
}

const mkTable = (rows, widths) => new Table({
  columnWidths: widths,
  width: { size: widths.reduce((a,b)=>a+b,0), type: WidthType.DXA },
  rows,
});

const doc = new Document({
  styles: { default: {
    document: { run: { font: "Calibri", size: 20 } },
    heading1: { run: { font:"Calibri", size:30, bold:true, color:"1F3864" } },
    heading2: { run: { font:"Calibri", size:24, bold:true, color:"2F5496" } },
  }},
  sections: [{
    properties: { page: {
      size: { width: 15840, height: 12240, orientation: PageOrientation.LANDSCAPE },
      margin: { top: 900, bottom: 900, left: 900, right: 900 } } },
    children: [
      new Paragraph({ spacing:{after:60}, children:[ new TextRun({
        text:"Kaempferia galanga chloroplast genomes — codon composition and annotation resolution",
        bold:true, size:30, color:"1F3864" })]}),
      new Paragraph({ spacing:{after:260}, children:[ new TextRun({
        text:"Samples KS and KB (GeSeq v2.03, BLAT v36x7 + Chloë v0.1.0), compared against Kaempferia galanga MK209001.1 (Li et al. 2019).",
        size:19, italics:true, color:"595959" })]}),

      H("1. Canonical gene set", HeadingLevel.HEADING_1),
      P("Both KS and KB are 163,799 bp. Each yielded 78 unique protein-coding genes after (i) deduplicating IR copies, (ii) choosing one canonical call per gene where GeSeq's two sub-annotators disagreed, and (iii) excluding one gene whose CDS length was not a multiple of 3. MK209001 carries 79. The single-gene gap is clpP1/clpP, excluded here on frame grounds rather than genuinely absent."),
      P("Selection rule: where a gene had more than one candidate CDS, each candidate was translated under genetic code table 11 and the call producing a clean ORF (Met start, no internal stop, terminal stop) was taken as canonical. Where several candidates were clean, their spliced sequences were compared directly — in most cases the boundary disagreement was inconsequential because the same bases reach the mature mRNA either way."),

      H("2. Resolved annotation issues", HeadingLevel.HEADING_1),
      mkTable(issueRows, W3),
      P("KS and KB produced an identical set of flags, as expected given that their sequences are identical (see the whole-genome comparison below).",
        {before:130, italics:true, size:18, color:"595959"}),

      H("3. Gene-name reconciliation with MK209001", HeadingLevel.HEADING_1),
      P("Five apparent gene-set differences are naming conventions rather than real content differences. Each was confirmed by genomic position and flanking-gene context, not by name alone."),
      mkTable(nameRows, W4),
      P("Note on lhbA: this is the one case that looks like genuine mislabelling in the published reference rather than a synonym. The 189 bp sequence at that locus is byte-for-byte identical to psbZ in KS/KB and encodes the canonical 62-residue PsbZ protein. 'lhbA' does not correspond to a recognised plastid gene at this position.",
        {before:130, size:18}),

      new Paragraph({ children:[ new d.PageBreak() ]}),

      H("4. Table 1 — Nucleotide composition by codon position", HeadingLevel.HEADING_1),
      P(`Concatenated canonical single-copy CDS set: 78 genes, ${R.t1.KS.all.n_bases.toLocaleString()} bp (${R.t1.KS['1'].n_bases.toLocaleString()} codons) per sample. clpP1 excluded (length not divisible by 3).`,
        {size:18, italics:true, color:"595959"}),
      mkTable(t1rows, W),
      P("The composition is identical between KS and KB to every decimal place, which follows from the two genomes being sequence-identical. The pattern is the standard plastid one: A+T rises steeply from 54.94% at 1st positions to 71.90% at 3rd positions, reflecting the AT bias at synonymously variable sites.",
        {before:150}),

      H("5. Genome-wide and per-region base composition", HeadingLevel.HEADING_1),
      P("Boundaries taken from GeSeq's own OGDRAW-derived misc_feature annotations.", {size:18, italics:true, color:"595959"}),
      mkTable(t2rows, W2),
      P("The IRs are the GC-richest region (41.11% G+C) and the SSC the poorest (29.58%), the usual plastid arrangement driven by the rRNA operon sitting in the IR. KB's SSC row shows A and T (and G and C) swapped relative to KS: the two assemblies annotate the SSC in opposite orientations. This is an assembly-rotation artifact, not a biological difference — see below.",
        {before:150}),

      H("6. Whole-genome comparison of KS and KB", HeadingLevel.HEADING_1),
      P("The SSC of KB is annotated on the opposite strand to that of KS. Three independent checks confirm this is orientation only:"),
      P("• Base composition mirrors exactly — KS SSC is A 35.92 / T 34.51 / C 15.62 / G 13.96; KB SSC is A 34.51 / T 35.92 / C 13.96 / G 15.62.", {size:19, after:60}),
      P("• Direct comparison of the two SSC sequences in the same orientation gives 28.60% identity (i.e. no better than chance); reverse-complementing KB's SSC gives 100.0000% identity across all 15,776 bp.", {size:19, after:60}),
      P("• Applying that correction and comparing the full 163,799 bp base by base gives 0 mismatches. Without the correction the same pipeline reports 11,264 mismatches, which confirms the comparison is genuinely sensitive to differences where they exist.", {size:19, after:150}),
      P("KS and KB are therefore identical in sequence content. Any downstream comparison of the two morphotypes against each other has no plastid-level signal to detect; both were carried forward against MK209001 and, as expected, returned the same variant set.",
        {bold:true}),

      new Paragraph({ spacing:{before:400}, border:{ top:{style:BorderStyle.SINGLE, size:6, color:"BFBFBF"} }, children:[]}),
      P("Methods: Biopython 1.87 (GenBank parsing, feature.extract() for spliced CDS, translation under NCBI table 11). Composition computed over concatenated single-copy canonical CDS. Region boundaries from GeSeq/OGDRAW misc_feature annotations.",
        {size:16, italics:true, color:"7F7F7F", before:100}),
    ]
  }]
});

Packer.toBuffer(doc).then(b => {
  fs.writeFileSync('Doc1_Table1_and_Annotation_Resolution.docx', b);
  console.log('Wrote Doc1_Table1_and_Annotation_Resolution.docx');
});
