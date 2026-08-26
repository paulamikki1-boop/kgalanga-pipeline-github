const fs=require('fs');
const d=require('docx');
const {Document,Packer,Paragraph,TextRun,HeadingLevel,Table,TableRow,TableCell,
       WidthType,AlignmentType,ShadingType,BorderStyle,ImageRun,PageOrientation}=d;

const HDR="2F5496",ALT="F2F5FA";
function cell(t,{bold=false,shade=null,align="left",w=1200,size=17,color=null}={}) {
  return new TableCell({width:{size:w,type:WidthType.DXA},
    shading:shade?{type:ShadingType.CLEAR,fill:shade}:undefined,
    margins:{top:55,bottom:55,left:85,right:85},
    children:[new Paragraph({
      alignment:align==="center"?AlignmentType.CENTER:align==="right"?AlignmentType.RIGHT:AlignmentType.LEFT,
      children:[new TextRun({text:String(t),bold,size,
        color:color||(shade===HDR?"FFFFFF":"000000")})]})]});
}
const hcell=(t,w)=>cell(t,{bold:true,shade:HDR,align:"center",w});
const P=(t,o={})=>new Paragraph({spacing:{after:o.after??120,before:o.before??0},
  alignment:o.align??AlignmentType.LEFT,
  children:[new TextRun({text:t,bold:o.bold,italics:o.italics,size:o.size??20,color:o.color})]});
const H=(t,l)=>new Paragraph({text:t,heading:l,spacing:{before:260,after:130}});
const mkTable=(r,w)=>new Table({columnWidths:w,
  width:{size:w.reduce((a,b)=>a+b,0),type:WidthType.DXA},rows:r});

// ── Region size table ────────────────────────────────────────────────
const WR=[1600,1500,1500,1500,1500];
const rRows=[new TableRow({tableHeader:true,children:[
  hcell("Genome",WR[0]),hcell("LSC (bp)",WR[1]),hcell("IRb (bp)",WR[2]),
  hcell("SSC (bp)",WR[3]),hcell("IRa (bp)",WR[4])]})];
[["KS","88,429","29,797","15,776","29,797"],
 ["KB","88,429","29,797","15,776","29,797"],
 ["MK209001*","88,429","29,797","15,776","29,809"]].forEach((r,i)=>{
  const sh=i%2?ALT:null;
  rRows.push(new TableRow({children:[
    cell(r[0],{w:WR[0],shade:sh,bold:true}),
    cell(r[1],{w:WR[1],align:"right",shade:sh}),
    cell(r[2],{w:WR[2],align:"right",shade:sh}),
    cell(r[3],{w:WR[3],align:"right",shade:sh}),
    cell(r[4],{w:WR[4],align:"right",shade:sh}),
  ]}));
});

// ── Junction flanking-gene table ─────────────────────────────────────
const WJ=[900,1000,1400,1500,1500,1500,1600];
const jRows=[new TableRow({tableHeader:true,children:[
  hcell("Genome",WJ[0]),hcell("Junction",WJ[1]),hcell("Coordinate",WJ[2]),
  hcell("Upstream gene",WJ[3]),hcell("Distance",WJ[4]),
  hcell("Downstream gene",WJ[5]),hcell("Distance",WJ[6])]})];

const JD=[
 ["KS","JLB (LSC/IRb)","88,429","rpl22","47 bp upstream","rps19","147 bp downstream"],
 ["KS","JSB (IRb/SSC)","118,226","trnN-GUU","4,205 bp upstream","ndhF","30 bp downstream"],
 ["KS","JSA (SSC/IRa)","134,002","rps15","2,011 bp upstream","trnN-GUU","4,205 bp downstream"],
 ["KS","JLA (IRa/LSC)","0 / 163,799","—","—","psbA","123 bp downstream"],
 ["KB","JLB (LSC/IRb)","88,429","rpl22","47 bp upstream","rps19","147 bp downstream"],
 ["KB","JSB (IRb/SSC)","118,226","trnN-GUU","4,205 bp upstream","rps15","2,011 bp downstream"],
 ["KB","JSA (SSC/IRa)","134,002","ndhF","30 bp upstream","trnN-GUU","4,205 bp downstream"],
 ["KB","JLA (IRa/LSC)","0 / 163,799","—","—","psbA","123 bp downstream"],
];
JD.forEach((r,i)=>{
  const sh=(i<4)?(i%2?ALT:null):(i%2?ALT:"F7F3EE");
  jRows.push(new TableRow({children:[
    cell(r[0],{w:WJ[0],shade:sh,bold:true,align:"center"}),
    cell(r[1],{w:WJ[1],shade:sh,size:16}),
    cell(r[2],{w:WJ[2],align:"right",shade:sh}),
    cell(r[3],{w:WJ[3],shade:sh,bold:r[3]!=="—"}),
    cell(r[4],{w:WJ[4],align:"right",shade:sh,size:16}),
    cell(r[5],{w:WJ[5],shade:sh,bold:r[5]!=="—"}),
    cell(r[6],{w:WJ[6],align:"right",shade:sh,size:16}),
  ]}));
});

const fig=fs.readFileSync('IR_Junction_Diagram.png');

const doc=new Document({
  styles:{default:{
    document:{run:{font:"Calibri",size:20}},
    heading1:{run:{font:"Calibri",size:30,bold:true,color:"1F3864"}},
  }},
  sections:[{
    properties:{page:{
      size:{width:15840,height:12240,orientation:PageOrientation.LANDSCAPE},
      margin:{top:900,bottom:900,left:900,right:900}}},
    children:[
      new Paragraph({spacing:{after:60},children:[new TextRun({
        text:"Inverted repeat junctions — Kaempferia galanga KS and KB",
        bold:true,size:30,color:"1F3864"})]}),
      new Paragraph({spacing:{after:260},children:[new TextRun({
        text:"Junction coordinates, flanking genes, and comparison with MK209001.1.",
        size:19,italics:true,color:"595959"})]}),

      H("1. Region sizes", HeadingLevel.HEADING_1),
      mkTable(rRows,WR),
      P("* MK209001 carries no LSC/IR/SSC misc_feature annotations. Its boundaries were inferred by IRb/IRa self-comparison and confirmed at >98% identity; the 12 bp difference in IRa accounts for the whole length difference between the genomes (163,811 vs 163,799 bp).",
        {size:17,italics:true,color:"595959",before:100}),
      P("The quadripartite structure is identical across all three genomes. There is no IR expansion or contraction — the junctions sit at the same coordinates and involve the same genes, so no boundary shift distinguishes these accessions.",
        {before:130}),

      H("2. Junction diagram", HeadingLevel.HEADING_1),
      new Paragraph({spacing:{before:100,after:100},alignment:AlignmentType.CENTER,
        children:[new ImageRun({data:fig,type:"png",
          transformation:{width:696,height:218}})]}),
      P("Figure 1. The four junctions in KS (top row) and KB (bottom row). Blue = LSC, orange = IR, green = SSC. Arrows indicate the nearest gene on each side with its distance from the junction; ycf1 straddles both JSB and JSA in each genome. The apparent left/right swap between KS and KB at JSB and JSA is a consequence of the SSC being annotated in opposite orientations in the two assemblies — the underlying sequence is identical.",
        {size:17,italics:true,align:AlignmentType.CENTER,color:"595959",after:200}),

      new Paragraph({children:[new d.PageBreak()]}),

      H("3. Flanking-gene table", HeadingLevel.HEADING_1),
      P("Gene models were evaluated per exon part rather than by the compound feature's outer bounds, so trans-spliced rps12 does not falsely appear to span the region between its separated exons.",
        {size:18,italics:true,color:"595959"}),
      mkTable(jRows,WJ),

      H("4. Notes", HeadingLevel.HEADING_1),
      P("JLB (LSC/IRb). rpl22 terminates 47 bp before the junction and rps19 begins 147 bp inside IRb. rps19 is therefore fully duplicated rather than straddling — a common arrangement in Zingiberaceae, and one that distinguishes this family from lineages where rps19 is split by the junction."),
      P("JSB and JSA. ycf1 straddles both. The IRb-side fragment is the 3,888 bp truncated pseudogenic copy; the full-length 5,466 bp copy crosses JSA into the SSC. This is the standard plastid configuration and the reason the ycf1 annotation had to be resolved manually (see the annotation-resolution document). ndhF begins 30 bp from the SSC boundary — close, but not overlapping the IR, so there is no ndhF/ycf1 overlap in these genomes."),
      P("JLA (IRa/LSC). Corresponds to the origin of the circular map. psbA begins 123 bp into the LSC. No gene straddles this junction."),
      P("Comparison with MK209001. The same four genes occupy the same positions relative to each junction in the reference, within the 12 bp IRa length difference. Combined with the absence of any variant in IRb (see the reference-comparison document), the IR region is effectively invariant across all three genomes.",
        {bold:true}),

      new Paragraph({spacing:{before:400},border:{top:{style:BorderStyle.SINGLE,size:6,color:"BFBFBF"}},children:[]}),
      P("Methods: boundaries from GeSeq/OGDRAW misc_feature annotations (KS, KB) and IRb/IRa self-comparison (MK209001). Flanking genes identified per exon part using Biopython 1.87.",
        {size:16,italics:true,color:"7F7F7F",before:100}),
    ]
  }]
});

Packer.toBuffer(doc).then(b=>{
  fs.writeFileSync('Doc3_IR_Junctions.docx',b);
  console.log('Wrote Doc3_IR_Junctions.docx');
});
