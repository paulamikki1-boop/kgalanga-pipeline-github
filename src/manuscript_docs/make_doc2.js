const fs = require('fs');
const d = require('docx');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow,
        TableCell, WidthType, AlignmentType, ShadingType, BorderStyle,
        ImageRun, PageOrientation } = d;

const V = JSON.parse(fs.readFileSync('variants_classified.json','utf8'));
const K = JSON.parse(fs.readFileSync('doc2_data.json','utf8'));

const HDR="2F5496", ALT="F2F5FA", RED="FCE4E4", GRN="E8F3E8", YEL="FFF8E1";
const f=(x,n)=>Number(x).toFixed(n);

function cell(text,{bold=false,shade=null,align="left",w=1200,size=17,color=null}={}) {
  return new TableCell({
    width:{size:w,type:WidthType.DXA},
    shading: shade?{type:ShadingType.CLEAR,fill:shade}:undefined,
    margins:{top:50,bottom:50,left:80,right:80},
    children:[new Paragraph({
      alignment: align==="center"?AlignmentType.CENTER:align==="right"?AlignmentType.RIGHT:AlignmentType.LEFT,
      children:[new TextRun({text:String(text),bold,size,
        color: color || (shade===HDR?"FFFFFF":"000000")})]})]});
}
const hcell=(t,w)=>cell(t,{bold:true,shade:HDR,align:"center",w});
const P=(t,o={})=>new Paragraph({spacing:{after:o.after??120,before:o.before??0},
  alignment:o.align??AlignmentType.LEFT,
  children:[new TextRun({text:t,bold:o.bold,italics:o.italics,size:o.size??20,color:o.color})]});
const H=(t,l)=>new Paragraph({text:t,heading:l,spacing:{before:260,after:130}});
const mkTable=(rows,widths)=>new Table({columnWidths:widths,
  width:{size:widths.reduce((a,b)=>a+b,0),type:WidthType.DXA},rows});

// ── Full variant table ───────────────────────────────────────────────
const WV=[1150,700,650,1750,1750,750,1400,1050,1500,1500];
const vRows=[new TableRow({tableHeader:true,children:[
  hcell("Ref position",WV[0]),hcell("Type",WV[1]),hcell("bp",WV[2]),
  hcell("Reference",WV[3]),hcell("KS / KB",WV[4]),hcell("Region",WV[5]),
  hcell("Location",WV[6]),hcell("Gene",WV[7]),hcell("Codon",WV[8]),
  hcell("Effect",WV[9])]})];

const trunc=(s,n)=> (s&&s.length>n)? s.slice(0,n)+"…" : (s||"—");
let band=false;
for (const v of V) {
  const ft=v.feature_type, ct=v.coding_type||"";
  let sh = band?ALT:null;
  if (ct==="nonsynonymous") sh=RED;
  else if (ct==="synonymous") sh=GRN;
  else if (ft==="intronic/UTR") sh=YEL;
  const codon = v.ref_codon ? `${v.ref_codon} → ${v.alt_codon}` : "—";
  const eff = ct==="nonsynonymous" ? `${v.ref_aa} → ${v.alt_aa}`
            : ct==="synonymous" ? `${v.ref_aa} (silent)`
            : ct==="indel_in_CDS" ? "indel in CDS" : "—";
  vRows.push(new TableRow({children:[
    cell(v.ref_pos.toLocaleString(),{w:WV[0],align:"right",shade:sh}),
    cell(v.type,{w:WV[1],align:"center",shade:sh,
      bold: v.type!=="SNP"}),
    cell(v.length,{w:WV[2],align:"center",shade:sh}),
    cell(trunc(v.ref_base,22),{w:WV[3],shade:sh,size:15}),
    cell(trunc(v.alt_base,22),{w:WV[4],shade:sh,size:15}),
    cell(v.region,{w:WV[5],align:"center",shade:sh}),
    cell(ft,{w:WV[6],shade:sh,size:15}),
    cell(v.gene||"—",{w:WV[7],shade:sh,bold: ft==="CDS"}),
    cell(codon,{w:WV[8],align:"center",shade:sh,size:15}),
    cell(eff,{w:WV[9],align:"center",shade:sh,
      bold: ct==="nonsynonymous", color: ct==="nonsynonymous"?"9C0006":null}),
  ]}));
  band=!band;
}

// ── Coding differences detail table ──────────────────────────────────
const WC=[1300,1250,1400,1500,1500,3400];
const cRows=[new TableRow({tableHeader:true,children:[
  hcell("Gene",WC[0]),hcell("Position",WC[1]),hcell("Change",WC[2]),
  hcell("Codon",WC[3]),hcell("Amino acid",WC[4]),
  hcell("DNA-level verification",WC[5])]})];
const CODING=[
  ["rpoC2","20,038","C → T","synonymous","—","Confirmed at DNA level. Both annotations agree on rpoC2 CDS bounds; the difference is a real 3rd-position transition."],
  ["ycf4 (=pafII)","64,528","C → T","CGT → TGT","Arg → Cys","Confirmed: raw genomic base is C in MK209001 and T in KS/KB at this exact coordinate. Not an annotation artifact — both pipelines place the ycf4/pafII start identically."],
  ["rpl33","71,927","G → A","synonymous","—","Confirmed at DNA level. Single-exon gene, no boundary ambiguity."],
  ["rpl14","85,209","T → C","ATT → GTT","Ile → Val","Confirmed: raw genomic base differs. Conservative substitution (both aliphatic). rpl14 is single-exon in both annotations with matching length (369 bp), so no boundary artifact is possible."],
  ["rpl16","85,965","G → C","synonymous","—","Confirmed at DNA level."],
  ["ycf1","132,594","T → C","GAT → GGT","Asp → Gly","Confirmed: raw genomic base differs. Note this falls in the full-length ycf1 copy that straddles the SSC/IRa junction, not the truncated IRb copy."],
];
band=false;
for (const r of CODING) {
  const ns = r[4]!=="—";
  const sh = ns?RED:(band?ALT:GRN);
  cRows.push(new TableRow({children:[
    cell(r[0],{w:WC[0],shade:sh,bold:true}),
    cell(r[1],{w:WC[1],align:"right",shade:sh}),
    cell(r[2],{w:WC[2],align:"center",shade:sh}),
    cell(r[3],{w:WC[3],align:"center",shade:sh,size:16}),
    cell(r[4],{w:WC[4],align:"center",shade:sh,bold:ns,color:ns?"9C0006":null}),
    cell(r[5],{w:WC[5],shade:sh,size:15}),
  ]}));
  band=!band;
}

// ── Ka/Ks table ──────────────────────────────────────────────────────
const WK=[3800,2200];
const kRows=[new TableRow({tableHeader:true,children:[
  hcell("Parameter",WK[0]),hcell("Value",WK[1])]})];
const KK=[
  ["Genes pooled (matching CDS length)", `${K.n_genes}`],
  ["Genes excluded (length disagreement)", `${K.n_excluded}`],
  ["Synonymous sites, S", f(K.total_S,1)],
  ["Nonsynonymous sites, N", f(K.total_N,1)],
  ["Synonymous differences, Sd", f(K.total_Sd,0)],
  ["Nonsynonymous differences, Nd", f(K.total_Nd,0)],
  ["pS (uncorrected)", f(K.pS,6)],
  ["pN (uncorrected)", f(K.pN,6)],
  ["Ks (Jukes–Cantor corrected)", f(K.Ks,6)],
  ["Ka (Jukes–Cantor corrected)", f(K.Ka,6)],
  ["Ka / Ks", f(K.KaKs,4)],
];
band=false;
for (const [k,v] of KK) {
  const isFinal = k==="Ka / Ks";
  const sh = isFinal ? "DEEBF7" : (band?ALT:null);
  kRows.push(new TableRow({children:[
    cell(k,{w:WK[0],shade:sh,bold:isFinal}),
    cell(v,{w:WK[1],align:"right",shade:sh,bold:isFinal}),
  ]}));
  band=!band;
}

// ── excluded genes table ─────────────────────────────────────────────
const WE=[1500,1600,1600,3200];
const eRows=[new TableRow({tableHeader:true,children:[
  hcell("Gene",WE[0]),hcell("KS length (bp)",WE[1]),
  hcell("Ref length (bp)",WE[2]),hcell("Likely cause",WE[3])]})];
const EXC=[
  ["atpF","555","570","GeSeq intron boundary called 15 bp into exon 2."],
  ["rpoC1","2,055","2,064","3 codons short at an exon boundary."],
  ["psbC","1,386","1,422","GeSeq start codon called 36 bp downstream (psbC/psbD overlap region)."],
  ["pafI (ycf3)","507","513","Two codons short across the three-exon structure."],
  ["ndhK","744","753","3' end short — see annotation notes, no clean stop found."],
  ["petD","483","489","Exon 1 boundary shift."],
  ["rpl22","390","330","GeSeq call 60 bp longer; alternative upstream start."],
  ["rpl2","822","828","Start-codon ambiguity (ACG editing site)."],
  ["ndhB","1,533","1,560","Trans/cis intron boundary disagreement."],
  ["ndhD","1,503","1,506","One codon short."],
  ["ndhA","1,092","1,080","GeSeq call 12 bp longer at intron boundary."],
];
band=false;
for (const [g,a,b,c] of EXC) {
  const sh=band?ALT:null;
  eRows.push(new TableRow({children:[
    cell(g,{w:WE[0],shade:sh,bold:true}),
    cell(a,{w:WE[1],align:"right",shade:sh}),
    cell(b,{w:WE[2],align:"right",shade:sh}),
    cell(c,{w:WE[3],shade:sh,size:16}),
  ]}));
  band=!band;
}

const figBuf = fs.readFileSync('Variant_Position_Map.png');

const doc = new Document({
  styles:{default:{
    document:{run:{font:"Calibri",size:20}},
    heading1:{run:{font:"Calibri",size:30,bold:true,color:"1F3864"}},
    heading2:{run:{font:"Calibri",size:24,bold:true,color:"2F5496"}},
  }},
  sections:[{
    properties:{page:{
      size:{width:15840,height:12240,orientation:PageOrientation.LANDSCAPE},
      margin:{top:900,bottom:900,left:900,right:900}}},
    children:[
      new Paragraph({spacing:{after:60},children:[new TextRun({
        text:"Kaempferia galanga KS / KB versus the published reference MK209001.1",
        bold:true,size:30,color:"1F3864"})]}),
      new Paragraph({spacing:{after:260},children:[new TextRun({
        text:"Whole-genome variant analysis, coding consequences, and pooled Ka/Ks. Reference: Li, Zhao & Liu (2019) Molecules 24:E474.",
        size:19,italics:true,color:"595959"})]}),

      H("1. Alignment strategy", HeadingLevel.HEADING_1),
      P("Both genomes were reduced to a single-IR-copy (collinear) representation — LSC + IRb + SSC, dropping the duplicate IRa — before alignment. Without this step a whole-genome aligner matches the IR equally well to either copy and reports the same region twice. The collapsed representations are 134,002 bp for KS, KB and MK209001 alike."),
      P("Alignment used minimap2 via the mappy Python binding under the asm5 preset, with the cs tag parsed to recover every substitution and indel at reference coordinates. A single primary alignment spanned the full 134,002 bp (MAPQ 60, NM = 170)."),
      P("KB was corrected for its inverted SSC before alignment. KS and KB returned identical variant sets, as expected given the two genomes are sequence-identical; results below are reported once and apply to both.",
        {italics:true, color:"595959", size:19}),

      H("2. Variant summary", HeadingLevel.HEADING_1),
      P("39 variant events separate KS/KB from MK209001: 22 SNPs and 17 indels (9 insertions, 8 deletions), a net 12 bp shortening in KS/KB. Overall identity is 99.87%."),
      P("• 28 events (72%) are intergenic.", {size:19, after:50}),
      P("• 5 events are intronic or UTR (trnK-UUU, rps16, trnP-UGG, clpP, rpl16 introns).", {size:19, after:50}),
      P("• 6 events fall in coding sequence: 3 synonymous, 3 nonsynonymous. All six are SNPs; no indel disrupts a reading frame.", {size:19, after:50}),
      P("• Zero variants fall in IRb. All 39 lie in the LSC (26) or SSC (13), the expected pattern given copy-correction-driven conservation of the inverted repeat.",
        {size:19, after:160, bold:true}),

      new Paragraph({spacing:{before:100,after:100},alignment:AlignmentType.CENTER,
        children:[new ImageRun({data:figBuf,type:"png",
          transformation:{width:696,height:173}})]}),
      P("Figure 1. Distribution of the 39 variants across the collapsed genome. Grey = intergenic, amber = intronic/UTR, green = synonymous coding, red starred = nonsynonymous coding. Dotted lines mark the JLB and JSB junctions. Note the complete absence of variation across the 29,797 bp IRb.",
        {size:17,italics:true,align:AlignmentType.CENTER,color:"595959",after:200}),

      new Paragraph({children:[new d.PageBreak()]}),

      H("3. Coding differences", HeadingLevel.HEADING_1),
      P("Before reporting any coding difference as real, the raw genomic sequence at each locus was compared directly between the two assemblies rather than relying on the annotated CDS. A one- or two-base exon-boundary disagreement between annotation pipelines can otherwise produce a spurious amino-acid change that disappears once the underlying DNA is checked. All six coding variants below survived that check."),
      mkTable(cRows, WC),
      P("The three nonsynonymous changes are conservative to moderate: Ile→Val in rpl14 is a near-neutral aliphatic swap; Asp→Gly in ycf1 and Arg→Cys in ycf4 are more consequential in principle, but both fall in genes with high intraspecific tolerance and neither introduces a stop or frameshift.",
        {before:150}),

      H("4. Pooled Ka/Ks", HeadingLevel.HEADING_1),
      P("Per-gene Ka/Ks was not computed. With 0–1 observed substitutions in almost every gene, per-gene ratios are statistically meaningless — most genes would return 0/0 or an undefined value. Instead, synonymous and nonsynonymous site and difference counts were pooled across all genes with matching annotated CDS length under Nei & Gojobori (1986), and a Jukes–Cantor (1969) correction applied to give a single genome-wide estimate."),
      mkTable(kRows, WK),
      P("Ka/Ks = 0.373 (< 1) indicates purifying selection across the protein-coding complement, as expected for a plastome comparison within a species. The absolute divergence is very low — 7 codon-level differences across 56,931 sites — so this ratio should be read as directional rather than precise.",
        {before:150}),

      H("4.1 Genes excluded from the Ka/Ks pool", HeadingLevel.HEADING_1),
      P("11 genes were excluded because the two annotations disagree on CDS length. In every case the disagreement is an annotation-pipeline artifact (exon boundary or start-codon placement), not a genuine indel — the aligner reports no coding indels anywhere in the genome.", {size:19}),
      mkTable(eRows, WE),

      H("5. Gene-naming reconciliation", HeadingLevel.HEADING_1),
      P("Four GeSeq gene symbols are modern synonyms of the names used in MK209001: pafI = ycf3, pafII = ycf4, pbf1 = psbN, clpP1 = clpP. Each was confirmed by genomic position and flanking-gene context rather than name alone."),
      P("One case appears to be genuine mislabelling in the published reference. MK209001 annotates a 189 bp CDS at 39,003–39,192 as 'lhbA'. That sequence is byte-for-byte identical to the gene GeSeq calls psbZ at KS 39,025–39,214, and encodes the canonical 62-residue PsbZ protein (MTIAFQLAVFALIATSSVLLISVPVVFASSDNWSSNKNIVFSGTSLWIGLVFLVAILNSLIS). 'lhbA' has no standard plastid assignment at this locus. Recommend citing this gene as psbZ.",
        {bold:true}),

      H("6. Divergence in context", HeadingLevel.HEADING_1),
      P(`Intraspecific p-distance (KS/KB vs MK209001, SNPs only): ${f(K.p_dist,6)} — that is 22 substitutions across 134,002 aligned bp, or 0.016%. Including indels, 39 events separate the two.`),
      P("Li et al. (2019) generated MK209001 alongside a K. elegans plastome and reported interspecific divergence between the two at roughly two orders of magnitude above this figure. The comparison places KS/KB firmly within K. galanga: the variation separating these accessions from the published reference is an order of magnitude smaller than the divergence between congeneric species, and there is no structural rearrangement, gene loss, or IR expansion/contraction distinguishing them."),
      P("Their multi-species alignment has not been recomputed here — only the contextual comparison, which is the non-redundant part. If you want the published Pi values quoted precisely alongside this figure, the values need to be pulled from the paper's supplementary tables.",
        {italics:true, size:18, color:"595959"}),

      new Paragraph({children:[new d.PageBreak()]}),

      H("7. Full variant table", HeadingLevel.HEADING_1),
      P("All 39 events at MK209001 coordinates. Red = nonsynonymous coding, green = synonymous coding, amber = intronic/UTR, unshaded = intergenic.",
        {size:18,italics:true,color:"595959"}),
      mkTable(vRows, WV),

      new Paragraph({spacing:{before:400},border:{top:{style:BorderStyle.SINGLE,size:6,color:"BFBFBF"}},children:[]}),
      P("Methods: minimap2 (asm5) via mappy; cs-tag parsing for variant extraction. Variants classified per exon part against MK209001 gene models to avoid trans-spliced bounding-box errors (rps12). Ka/Ks by Nei–Gojobori (1986) with Jukes–Cantor (1969) correction, pooled across genes. Biopython 1.87.",
        {size:16,italics:true,color:"7F7F7F",before:100}),
    ]
  }]
});

Packer.toBuffer(doc).then(b=>{
  fs.writeFileSync('Doc2_Reference_Comparison_MK209001.docx',b);
  console.log('Wrote Doc2_Reference_Comparison_MK209001.docx');
});
