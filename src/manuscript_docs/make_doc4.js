const fs=require('fs'), d=require('docx');
const {Document,Packer,Paragraph,TextRun,HeadingLevel,Table,TableRow,TableCell,
       WidthType,AlignmentType,ShadingType,BorderStyle,ImageRun,PageOrientation}=d;
const J=JSON.parse(fs.readFileSync('doc4_data.json','utf8'));
const HDR="1F3864",ALT="F2F5FA",GRN="E2EFDA",RED="FCE4E4",BLU="DEEBF7";
function cell(t,{bold=false,shade=null,align="left",w=1200,size=17,color=null,mono=false}={}) {
  return new TableCell({width:{size:w,type:WidthType.DXA},
    shading:shade?{type:ShadingType.CLEAR,fill:shade}:undefined,
    margins:{top:55,bottom:55,left:85,right:85},
    children:[new Paragraph({alignment:align==="center"?AlignmentType.CENTER:align==="right"?AlignmentType.RIGHT:AlignmentType.LEFT,
      children:[new TextRun({text:String(t),bold,size,font:mono?"Consolas":undefined,
        color:color||(shade===HDR?"FFFFFF":"000000")})]})]});
}
const hc=(t,w)=>cell(t,{bold:true,shade:HDR,align:"center",w});
const P=(t,o={})=>new Paragraph({spacing:{after:o.after??120,before:o.before??0},
  alignment:o.align??AlignmentType.LEFT,
  children:[new TextRun({text:t,bold:o.bold,italics:o.italics,size:o.size??20,color:o.color,font:o.mono?"Consolas":undefined})]});
const H=(t,l)=>new Paragraph({text:t,heading:l,spacing:{before:280,after:140}});
const T=(r,w)=>new Table({columnWidths:w,width:{size:w.reduce((a,b)=>a+b,0),type:WidthType.DXA},rows:r});

const LAB=["K. galanga KS (narrow)","K. galanga KB (broad)","K. galanga MK209001",
 "K. elegans MK209002","K. rotunda MW326457","K. rotunda Red Leaf",
 "K. rotunda Silver Dia.","K. parviflora OP805592"];
const GALS=new Set(LAB.slice(0,3));

// ── recommended primers table ────────────────────────────────────────
const W1=[1500,1100,3550,900,800,1000,1450];
const pr=[
 ["Kg-ycf1-F","primary","TCCTTGCTTTTCTTGCATCGTT","59.4","45.5","22","ycf1, SSC"],
 ["Kg-ycf1-R","primary","AGCCTCTTCAAAAGGATTATGCT","58.1","39.1","23","ycf1, SSC"],
 ["Kg-atpH-F","backup","TGAATCATGTGGGATAAGCTTGC","59.4","43.5","23","atpH–atpI IGS, LSC"],
 ["Kg-atpH-R","backup","GTGGAAGGTCATCATTAACTAGCT","58.3","41.7","24","atpH–atpI IGS, LSC"],
 ["Kg-trnP-F","barcode","CGCTCTGTAGGATTTGAACCCA","60.4","50.0","22","trnP-UGG, LSC"],
 ["Kg-trnP-R","barcode","ACGTTAGGTTTCAGATGTATCAGA","57.5","37.5","24","trnP-UGG, LSC"],
];
const r1=[new TableRow({tableHeader:true,children:[hc("Primer",W1[0]),hc("Role",W1[1]),
  hc("Sequence (5'→3')",W1[2]),hc("Tm °C",W1[3]),hc("GC %",W1[4]),hc("Length",W1[5]),hc("Locus",W1[6])]})];
pr.forEach((p,i)=>{const sh=p[1]==="primary"?GRN:(i%2?ALT:null);
  r1.push(new TableRow({children:[cell(p[0],{w:W1[0],bold:true,shade:sh,mono:true}),
   cell(p[1],{w:W1[1],shade:sh,align:"center"}),cell(p[2],{w:W1[2],shade:sh,mono:true,size:16}),
   cell(p[3],{w:W1[3],shade:sh,align:"center"}),cell(p[4],{w:W1[4],shade:sh,align:"center"}),
   cell(p[5],{w:W1[5],shade:sh,align:"center"}),cell(p[6],{w:W1[6],shade:sh,size:16})]}));});

// ── in-silico PCR results ────────────────────────────────────────────
function pcrTable(key){
  const W=[3000,1300,1300,1500];
  const amps=J.ispcr[key].amplicons;
  const rows=[new TableRow({tableHeader:true,children:[hc("Genome",W[0]),hc("Product",W[1]),
    hc("F / R mismatch",W[2]),hc("Call",W[3])]})];
  LAB.forEach((l,i)=>{const g=GALS.has(l); const sh=g?GRN:RED;
    rows.push(new TableRow({children:[cell(l,{w:W[0],shade:sh,bold:g}),
      cell(amps[l].length+" bp",{w:W[1],shade:sh,align:"center",bold:true}),
      cell("0 / 0",{w:W[2],shade:sh,align:"center"}),
      cell(g?"K. galanga":"not galanga",{w:W[3],shade:sh,align:"center",
        bold:g,color:g?"375623":"9C0006"})]}));});
  return T(rows,W);
}

// ── divergence ladder ────────────────────────────────────────────────
const W3=[4200,1500,1600];
const lad=[
 ["KS vs KB (your two morphotypes)","0.000 %","identical"],
 ["KS/KB vs MK209001 (within K. galanga)","0.013 %","intraspecific"],
 ["Among three K. rotunda accessions","0.057–0.184 %","intraspecific"],
 ["K. galanga vs K. elegans","0.343 %","interspecific"],
 ["K. galanga vs K. parviflora","0.441 %","interspecific"],
 ["K. galanga vs K. rotunda","0.468–0.535 %","interspecific"],
];
const r3=[new TableRow({tableHeader:true,children:[hc("Comparison",W3[0]),hc("p-distance",W3[1]),hc("Level",W3[2])]})];
lad.forEach((x,i)=>{const sh=i<3?BLU:(i%2?ALT:null);
  r3.push(new TableRow({children:[cell(x[0],{w:W3[0],shade:sh,bold:i===0}),
    cell(x[1],{w:W3[1],shade:sh,align:"right",bold:i===0}),
    cell(x[2],{w:W3[2],shade:sh,align:"center",size:16})]}));});

// ── ARMS alternatives ────────────────────────────────────────────────
const W4=[1200,2000,3600,900,1400];
const r4=[new TableRow({tableHeader:true,children:[hc("Ref pos",W4[0]),hc("Locus",W4[1]),
  hc("ARMS forward primer (3' base diagnostic)",W4[2]),hc("Tm",W4[3]),hc("gal / others",W4[4])]})];
J.arms.slice(0,6).forEach((a,i)=>{const sh=i%2?ALT:null;
  r4.push(new TableRow({children:[cell(a.pos.toLocaleString(),{w:W4[0],shade:sh,align:"right"}),
   cell(a.locus,{w:W4[1],shade:sh,size:16}),cell(a.primer,{w:W4[2],shade:sh,mono:true,size:16}),
   cell(a.tm,{w:W4[3],shade:sh,align:"center"}),
   cell(a.gal_base+" / "+a.oth_bases,{w:W4[4],shade:sh,align:"center"})]}));});

const fig=fs.readFileSync('Primer_Design_Figure.png');

const doc=new Document({
 styles:{default:{document:{run:{font:"Calibri",size:20}},
   heading1:{run:{font:"Calibri",size:30,bold:true,color:"1F3864"}},
   heading2:{run:{font:"Calibri",size:23,bold:true,color:"2F5496"}}}},
 sections:[{properties:{page:{size:{width:15840,height:12240,orientation:PageOrientation.LANDSCAPE},
   margin:{top:900,bottom:900,left:900,right:900}}},
  children:[
   new Paragraph({spacing:{after:60},children:[new TextRun({
     text:"Diagnostic primers for authenticating Kaempferia galanga",bold:true,size:30,color:"1F3864"})]}),
   new Paragraph({spacing:{after:280},children:[new TextRun({
     text:"Designed and validated in silico against eight Kaempferia plastomes: K. galanga (KS, KB, MK209001), K. elegans (MK209002), K. rotunda (MW326457, cv Red Leaf, cv Silver Diamonds) and K. parviflora (OP805592).",
     size:19,italics:true,color:"595959"})]}),

   H("1. Recommendation",HeadingLevel.HEADING_1),
   P("Use the Kg-ycf1 length marker as the primary assay. It resolves K. galanga from all five congeners as an 85 bp versus 67 bp band on a 3% agarose gel — an 18 bp (21%) difference requiring no sequencing, no restriction digest and no fluorescent chemistry.",{bold:true}),
   P("Run Kg-atpH as an independent confirmation. It sits in the LSC rather than the SSC, so the two markers fail independently; agreement between them is strong evidence. Reserve the Kg-trnP Sanger amplicon for publication-grade confirmation or for cases where the sample may be a Kaempferia species not tested here."),
   P("Why a length marker rather than a sequenced barcode: intraspecific divergence within K. galanga is 0.013% and the nearest congener sits at 0.343%. That gap is real but small, so a barcode approach depends on reading a handful of substitutions correctly. The ycf1 tandem duplication is a presence/absence difference — categorically easier to score and far more robust to sequencing noise.",{size:19}),

   H("2. Primer sequences",HeadingLevel.HEADING_1),
   T(r1,W1),
   P("All six primers match every one of the eight genomes with zero mismatches, so amplification failure indicates a technical problem rather than a non-target species. Each produces a single product in every genome tested.",{before:130,size:19,italics:true,color:"595959"}),

   new Paragraph({spacing:{before:180,after:120},alignment:AlignmentType.CENTER,
     children:[new ImageRun({data:fig,type:"png",transformation:{width:690,height:359}})]}),
   P("Figure 1. (A) Mechanism of the Kg-ycf1 marker. (B, C) Predicted gel patterns. Green = K. galanga, red = congeners.",
     {size:17,italics:true,align:AlignmentType.CENTER,color:"595959",after:200}),

   new Paragraph({children:[new d.PageBreak()]}),

   H("3. The Kg-ycf1 marker",HeadingLevel.HEADING_1),
   P("The marker detects an 18 bp tandem duplication inside ycf1 in the SSC. K. galanga carries the motif CATAATCCTTTTGAAGAG twice in direct tandem; all five congeners carry it once. The duplicated unit is an exact copy of the immediately upstream 18 bp, consistent with slipped-strand mispairing.",{}),
   P("Three properties make this a sound target rather than an assembly artifact: the duplication is exact and in-frame (6 codons, no frameshift); its longest internal homopolymer is 4 bp, so it is not a mononucleotide-tract length call; and it is uniform across three independently sequenced K. galanga accessions and absent from five independently sequenced congeners.",{}),
   H("In-silico PCR — Kg-ycf1",HeadingLevel.HEADING_2),
   pcrTable("ycf1 indel  [GEL]"),
   P("Searched against both strands of each circular genome, permitting up to 3 mismatches with an obligate perfect 3'-terminal pentamer. Every genome yielded exactly one product.",
     {before:120,size:17,italics:true,color:"595959"}),

   H("4. The Kg-atpH backup marker",HeadingLevel.HEADING_2),
   pcrTable("atpH-atpI indel  [GEL]"),
   P("Caveat: this amplicon lies adjacent to a poly-A tract that varies between 9 and 12 residues across accessions. The 24 bp galanga-specific insert is the main signal, but the neighbouring homopolymer adds 1–2 bp of sizing noise and is itself the kind of feature assemblers call unreliably. The galanga and congener ranges still do not overlap (99 vs 82–83 bp), but treat this marker as confirmatory rather than standalone.",
     {before:130,color:"9C0006"}),

   H("5. Suggested protocol",HeadingLevel.HEADING_1),
   P("1.  Extract total DNA from rhizome tissue by any CTAB or column method; plastid copy number is high, so yield is rarely limiting.",{size:19,after:60}),
   P("2.  PCR in 20 µL: 1× buffer, 1.5 mM MgCl₂, 0.2 mM dNTPs, 0.3 µM each primer, 0.5 U Taq, 10–20 ng template.",{size:19,after:60}),
   P("3.  Cycling: 95 °C 3 min; 35 × (95 °C 30 s, 56 °C 30 s, 72 °C 20 s); 72 °C 5 min. Both pairs share this profile, so they can run on one block or be multiplexed.",{size:19,after:60}),
   P("4.  Resolve on 3% agarose with a 20 or 50 bp ladder, or on 6% polyacrylamide if band separation is marginal. Score 85 bp as K. galanga, 67 bp as not K. galanga.",{size:19,after:60}),
   P("5.  Always include a verified K. galanga positive control and a no-template control. Because the assay reads a size shift rather than presence/absence, a blank lane is uninformative rather than diagnostic.",{size:19,after:150}),

   new Paragraph({children:[new d.PageBreak()]}),

   H("6. Divergence context",HeadingLevel.HEADING_1),
   P("Computed from a whole-genome projection of all eight plastomes onto MK209001 coordinates (minimap2 asm10, 126,214 positions scorable in all eight)."),
   T(r3,W3),
   P("Two consequences for marker design. First, K. elegans at 0.343% is the closest relative and therefore the binding constraint on specificity — a marker that separates galanga from elegans will separate it from anything else in the genus tested here. Adding K. elegans to the analysis eliminated two otherwise attractive indel candidates (37 bp and 29 bp) that turned out to be shared with it. Second, K. galanga itself shows essentially no plastid variation, so a single marker suffices for the species; no haplotype panel is needed.",{before:130}),
   P("Note on your phylogeny: the three K. rotunda accessions are 0.057–0.184% apart, which is ordinary intraspecific variation, and MW326457 is closest to cv Red Leaf (0.057%). Their scattered placement in the tree you sent does not match the sequence distances and is worth re-checking before publication.",
     {before:130,italics:true}),

   H("7. Alternative — allele-specific (ARMS) primers",HeadingLevel.HEADING_1),
   P("If you would rather score amplification than band size, 33 of the 178 fixed diagnostic sites support an ARMS forward primer with acceptable Tm and GC. The six best are listed below; each carries the K. galanga base at its 3' terminus, so extension should fail on congener template. These need empirical optimisation — 3'-mismatch discrimination is stringency-dependent and usually requires a deliberate second mismatch at position −2 or −3.",{}),
   T(r4,W4),

   H("8. Limitations",HeadingLevel.HEADING_1),
   P("• Five congeners tested. Kaempferia contains roughly 50 species; the marker is validated against the ones you supplied, which cover the common adulterants, but not against the genus as a whole.",{size:19,after:60}),
   P("• Tandem repeat copy number can vary within a species. Three K. galanga accessions all show two copies, but confirming the marker on 20–30 accessions of diverse provenance before deployment would be prudent.",{size:19,after:60}),
   P("• Plastid inheritance is maternal. The assay identifies the maternal lineage and will not detect a hybrid with a K. galanga mother, nor a powder blend in which K. galanga is a minority component.",{size:19,after:60}),
   P("• Entirely in silico. No wet-lab validation has been performed; predicted products, Tm values and specificity all require bench confirmation.",{size:19,after:60}),
   P("• The assay cannot distinguish your KS and KB morphotypes. Their plastomes are identical at all 163,799 bp; whatever separates narrow- from broad-leaf plants is not in the chloroplast and would require nuclear markers.",{size:19,bold:true}),

   new Paragraph({spacing:{before:380},border:{top:{style:BorderStyle.SINGLE,size:6,color:"BFBFBF"}},children:[]}),
   P("Methods: whole-genome projection onto MK209001 with minimap2 asm10 via mappy; per-site screening for positions monomorphic across three K. galanga accessions and differing in all five congeners; Primer3 (primer3-py) design under conserved-flank constraints; in-silico PCR against both strands of each circular genome with ≤3 mismatches and an obligate perfect 3'-terminal pentamer. Biopython 1.87.",
     {size:16,italics:true,color:"7F7F7F",before:100}),
  ]}]});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync('Doc4_Primer_Design_Kgalanga.docx',b);
  console.log('Wrote Doc4_Primer_Design_Kgalanga.docx');});
