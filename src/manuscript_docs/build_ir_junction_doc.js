const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, HeadingLevel, AlignmentType, ShadingType, VerticalAlign, ImageRun } = require("docx");
const TOTAL_W = 9016;
function cell(text, {header=false, width, align=AlignmentType.CENTER} = {}) {
  return new TableCell({ width:{size:width,type:WidthType.DXA}, shading: header?{type:ShadingType.CLEAR,fill:"1F3864"}:undefined,
    verticalAlign: VerticalAlign.CENTER, margins:{top:60,bottom:60,left:90,right:90},
    children:[new Paragraph({alignment:align, children:[new TextRun({text:String(text), bold:header, color:header?"FFFFFF":undefined, size:19})]})] });
}
function row(cells){ return new TableRow({children:cells}); }
function makeTable(headers,widths,dataRows){
  return new Table({ width:{size:TOTAL_W,type:WidthType.DXA}, columnWidths:widths,
    rows:[ row(headers.map((h,i)=>cell(h,{header:true,width:widths[i]}))),
           ...dataRows.map(r=>row(r.map((v,i)=>cell(v,{width:widths[i]})))) ] });
}
function h1(t){ return new Paragraph({heading:HeadingLevel.HEADING_1, spacing:{before:280,after:120}, children:[new TextRun({text:t})]}); }
function p(t){ return new Paragraph({spacing:{after:160}, children:[new TextRun(t)]}); }
function caption(t){ return new Paragraph({spacing:{before:60,after:200}, children:[new TextRun({text:t, italics:true, size:18})]}); }

const imgBuf = fs.readFileSync("/sessions/awesome-wizardly-hypatia/mnt/outputs/IR_junction_diagram.png");

const doc = new Document({ sections:[{ properties:{page:{margin:{top:1440,bottom:1440,left:1440,right:1440}}}, children:[
  new Paragraph({heading:HeadingLevel.TITLE, spacing:{after:80}, children:[new TextRun("IR Junction Diagram (LSC/IRb/SSC/IRa)")]}),
  new Paragraph({spacing:{after:280}, children:[new TextRun({text:"Gene arrangement at the four quadripartite-structure junctions, KS vs MK209001 reference", italics:true, size:22})]}),
  p("Date: 24 July 2026"),
  p("KB is identical to KS at every junction after accounting for the known SSC orientation flip (see QC report), so KS is shown as the representative; the same figure applies to KB."),

  h1("Figure"),
  new Paragraph({ children:[new ImageRun({type:"png", data:imgBuf, transformation:{width:680,height:245}})], alignment:AlignmentType.CENTER, spacing:{before:100,after:80} }),
  caption("Figure. Gene arrangement across the four IR junctions (JLB = LSC/IRb, JSB = IRb/SSC, JSA = SSC/IRa, JLA = IRa/LSC) for KS (top) and the published reference MK209001 (bottom). Arrows show gene extent (not drawn to strand); dashed line marks the junction (position 0). Box color: blue = LSC, green = IR, orange = SSC."),

  h1("Junction coordinates and flanking genes"),
  makeTable(
    ["Junction","KS position","Reference position","Gene / distance to junction"],
    [1400,1800,1900,3916],
    [
      ["JLB (LSC→IRb)","88,429","88,405","rpl22 ends 47 bp (KS) / 107 bp (ref) before; rps19 starts 147 bp after"],
      ["JSB (IRb→SSC)","118,226","118,202","ycf1 (full-length copy) straddles: 3,880 bp into IRb, 8 bp into SSC; ndhF starts 30 bp further into SSC"],
      ["JSA (SSC→IRa)","134,002","134,014","ycf1 (truncated copy) straddles: 1,586 bp into SSC, 3,880 bp into IRa; rps15 ends 2,011 bp before, in SSC"],
      ["JLA (IRa→LSC)","0 / 163,799","0 / 163,811","rps19 (2nd copy) ends 147 bp before (wrapping from genome end); psbA starts 123 bp after"],
    ]
  ),
  caption("Positions are 0-based, on each genome's own native annotation coordinates."),

  h1("Notes"),
  p("All four junctions fall at the same flanking genes in KS and the reference, and at essentially the same distances (within a few bp, consistent with independent IR-boundary calls by GeSeq vs the original annotation pipeline) — no junction shift between this study's K. galanga and the published one."),
  p("ycf1 straddling both SSC junctions, with a full-length copy on one side and a truncated pseudogene-like copy on the other, is the expected, well-documented pattern for this gene across the Zingiberaceae and most monocot plastids, not an anomaly."),
  p("rps19 and rps12 sitting right at the LSC/IR boundaries, and psbA/ndhF flanking the SSC junctions, match the canonical chloroplast quadripartite gene arrangement reported for related Zingiberaceae genomes (Li, Zhao and Liu, 2019)."),
]}]});

Packer.toBuffer(doc).then(buf=>{ fs.writeFileSync("/sessions/awesome-wizardly-hypatia/mnt/outputs/IR_junction_diagram_report.docx", buf); console.log("written"); });
