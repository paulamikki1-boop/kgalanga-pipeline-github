const fs=require('fs'), d=require('docx');
const {Document,Packer,Paragraph,TextRun,HeadingLevel,Table,TableRow,TableCell,
       WidthType,AlignmentType,ShadingType,BorderStyle,convertMillimetersToTwip}=d;
const N=JSON.parse(fs.readFileSync('manuscript_numbers.json','utf8'));

const FONT="Times New Roman", SZ=24, LINE=360;   // 12pt, 1.5 spacing
const HDR="D9D9D9", ALT="F2F2F2", FLAG="FFF2CC";

// ---- rich text: *italic* ----
function rich(t,{size=SZ,bold=false,color=null}={}) {
  const runs=[]; t.split(/(\*[^*]+\*)/g).forEach(seg=>{
    if(!seg) return;
    const it=seg.startsWith("*")&&seg.endsWith("*")&&seg.length>2;
    runs.push(new TextRun({text:it?seg.slice(1,-1):seg,italics:it,bold,size,font:FONT,color}));
  }); return runs;
}
const P=(t,o={})=>new Paragraph({
  spacing:{line:LINE,after:o.after??140,before:o.before??0},
  alignment:o.align??AlignmentType.JUSTIFIED,
  indent:o.indent?{firstLine:convertMillimetersToTwip(6)}:undefined,
  children:rich(t,{size:o.size??SZ,bold:o.bold,color:o.color})});
const H2=(t)=>new Paragraph({spacing:{line:LINE,before:260,after:130},
  children:rich(t,{bold:true,size:24})});
const H1=(t)=>new Paragraph({spacing:{line:LINE,before:300,after:160},
  children:rich(t,{bold:true,size:28})});
const CAP=(t)=>new Paragraph({spacing:{line:240,after:120,before:80},
  alignment:AlignmentType.LEFT,children:rich(t,{size:20})});

function cell(t,{bold=false,shade=null,align="left",w=1200,size=19}={}) {
  return new TableCell({width:{size:w,type:WidthType.DXA},
    shading:shade?{type:ShadingType.CLEAR,fill:shade}:undefined,
    margins:{top:50,bottom:50,left:80,right:80},
    children:[new Paragraph({spacing:{line:240},
      alignment:align==="center"?AlignmentType.CENTER:align==="right"?AlignmentType.RIGHT:AlignmentType.LEFT,
      children:rich(String(t),{bold,size})})]});
}
const hc=(t,w)=>cell(t,{bold:true,shade:HDR,align:"center",w});
const TBL=(rows,w)=>new Table({columnWidths:w,
  width:{size:w.reduce((a,b)=>a+b,0),type:WidthType.DXA},rows});

/* ================= TABLES ================= */
// Revision notes
const Wr=[2100,3300,3600];
const revRows=[new TableRow({tableHeader:true,children:[
 hc("Section",Wr[0]),hc("Change",Wr[1]),hc("Basis",Wr[2])]})];
[["3.5","GC values revised to 36.07% (genome), 33.83% (LSC), 29.58% (SSC), 41.11% (IR)",
  "Recomputed from the GeSeq GenBank sequence; previous values were rounded inconsistently."],
 ["3.6","tRNA count changed from 28 to 23 unique genes; gene total from 111 to 106",
  "The KS/KB GeSeq output contains 23 unique tRNA genes (32 features). 28 is the count for MK209001. Flagged for re-annotation."],
 ["3.7","Codon total revised to 22,667 codons (68,001 bp); several RSCU counts adjusted",
  "Recounted from the 78-gene canonical CDS set using the full-length 5,466 bp *ycf1* copy."],
 ["3.9","Coding-variant effects reassigned; *ycf1* added, *rpl16* no longer double-counted",
  "Codon-level re-analysis. *rpoC2*, *rpl33* and *rpl16* are synonymous; *ycf4*, *rpl14* and *ycf1* are nonsynonymous."],
 ["3.10","Retained unchanged (66 genes, 3/3, Ka/Ks = 0.28)",
  "Independently reproduced. An *rps12* substitution was shown to be an exon-boundary artifact and correctly excluded."],
 ["3.11","Junction distances added for all four junctions",
  "Measured per exon part from the annotated boundaries."],
 ["3.13–3.15","New sections",
  "Congener comparison, phylogeny and marker development."]
].forEach((r,i)=>{const sh=i%2?ALT:null;
 revRows.push(new TableRow({children:[cell(r[0],{w:Wr[0],bold:true,shade:sh}),
  cell(r[1],{w:Wr[1],shade:sh}),cell(r[2],{w:Wr[2],shade:sh})]}));});

// Codon-position composition
const Wc=[2200,1300,1300,1300,1300,1400];
const cp=N.codon_pos;
const cpRows=[new TableRow({tableHeader:true,children:[
 hc("Codon position",Wc[0]),hc("T(U) %",Wc[1]),hc("C %",Wc[2]),hc("A %",Wc[3]),
 hc("G %",Wc[4]),hc("A+T %",Wc[5])]})];
[["1st position","1"],["2nd position","2"],["3rd position","3"],["All positions","all"]]
 .forEach(([lab,k],i)=>{const c=cp[k]; const last=k==="all"; const sh=last?HDR:(i%2?ALT:null);
  cpRows.push(new TableRow({children:[cell(lab,{w:Wc[0],bold:last,shade:sh}),
   cell(c.T.toFixed(2),{w:Wc[1],align:"center",bold:last,shade:sh}),
   cell(c.C.toFixed(2),{w:Wc[2],align:"center",bold:last,shade:sh}),
   cell(c.A.toFixed(2),{w:Wc[3],align:"center",bold:last,shade:sh}),
   cell(c.G.toFixed(2),{w:Wc[4],align:"center",bold:last,shade:sh}),
   cell(c.AT.toFixed(2),{w:Wc[5],align:"center",bold:last,shade:sh})]}));});

// Coding variants
const Wv=[1500,1500,1300,1500,1500,1900];
const cvRows=[new TableRow({tableHeader:true,children:[
 hc("Gene",Wv[0]),hc("Position",Wv[1]),hc("Codon no.",Wv[2]),hc("Change",Wv[3]),
 hc("Amino acid",Wv[4]),hc("Effect",Wv[5])]})];
N.coding.forEach((v,i)=>{const ns=v.type==="nonsynonymous"; const sh=ns?FLAG:(i%2?ALT:null);
 const aa=v.aa.replace("->"," → ");
 cvRows.push(new TableRow({children:[cell("*"+v.gene+"*",{w:Wv[0],bold:true,shade:sh}),
  cell(v.pos.toLocaleString(),{w:Wv[1],align:"right",shade:sh}),
  cell(v.codon_no,{w:Wv[2],align:"center",shade:sh}),
  cell(v.ref+" → "+v.alt,{w:Wv[3],align:"center",shade:sh}),
  cell(ns?aa:aa.split(" ")[0]+" (unchanged)",{w:Wv[4],align:"center",shade:sh}),
  cell(v.type,{w:Wv[5],align:"center",bold:ns,shade:sh})]}));});

// Divergence
const Wd=[4400,1700,1900];
const dv=N.div;
const dvRows=[new TableRow({tableHeader:true,children:[
 hc("Comparison",Wd[0]),hc("K2P distance (%)",Wd[1]),hc("Level",Wd[2])]})];
[["KS vs KB (narrow- vs broad-leaf)",dv.KS_KB.toFixed(4),"within morphotypes"],
 ["KS/KB vs *K. galanga* MK209001",dv.KS_REF.toFixed(4),"intraspecific"],
 ["Among three *K. rotunda* accessions",dv.rot_internal[0].toFixed(4)+"–"+dv.rot_internal[1].toFixed(4),"intraspecific"],
 ["*K. galanga* vs *K. elegans*",dv.gal_ele.toFixed(4),"interspecific"],
 ["*K. galanga* vs *K. parviflora*",dv.gal_par.toFixed(4),"interspecific"],
 ["*K. galanga* vs *K. rotunda*",dv.gal_rot[0].toFixed(4)+"–"+dv.gal_rot[2].toFixed(4),"interspecific"]
].forEach((r,i)=>{const sh=i<3?ALT:null;
 dvRows.push(new TableRow({children:[cell(r[0],{w:Wd[0],shade:sh,bold:i===0}),
  cell(r[1],{w:Wd[1],align:"right",shade:sh,bold:i===0}),
  cell(r[2],{w:Wd[2],align:"center",shade:sh,size:18})]}));});

// Markers
const Wm=[1700,3400,1100,1500,1600];
const mk=N.markers["ycf1 indel  [GEL]"], mk2=N.markers["atpH-atpI indel  [GEL]"],
      mk3=N.markers["trnP-UGG  [SANGER]"];
const mkRows=[new TableRow({tableHeader:true,children:[
 hc("Primer",Wm[0]),hc("Sequence (5′→3′)",Wm[1]),hc("Length",Wm[2]),
 hc("*K. galanga*",Wm[3]),hc("Congeners",Wm[4])]})];
[["Kg-ycf1-F",mk.fwd,mk.fwd.length,"85 bp","67 bp",true],
 ["Kg-ycf1-R",mk.rev,mk.rev.length,"85 bp","67 bp",true],
 ["Kg-atpH-F",mk2.fwd,mk2.fwd.length,"99 bp","82–83 bp",false],
 ["Kg-atpH-R",mk2.rev,mk2.rev.length,"99 bp","82–83 bp",false],
 ["Kg-trnP-F",mk3.fwd,mk3.fwd.length,"489–490 bp","489–510 bp",false],
 ["Kg-trnP-R",mk3.rev,mk3.rev.length,"489–490 bp","489–510 bp",false]
].forEach((r,i)=>{const sh=r[5]?FLAG:(i%2?ALT:null);
 mkRows.push(new TableRow({children:[cell(r[0],{w:Wm[0],bold:true,shade:sh}),
  cell(r[1],{w:Wm[1],shade:sh,size:18}),cell(r[2],{w:Wm[2],align:"center",shade:sh}),
  cell(r[3],{w:Wm[3],align:"center",shade:sh,bold:r[5]}),
  cell(r[4],{w:Wm[4],align:"center",shade:sh})]}));});

/* ================= DOCUMENT ================= */
const body=[
 new Paragraph({spacing:{after:80},alignment:AlignmentType.CENTER,
  children:rich("Revised Materials and Methods (computational) and Results",{bold:true,size:30})}),
 new Paragraph({spacing:{after:300},alignment:AlignmentType.CENTER,
  children:rich("Chloroplast genomes of narrow-leaf and broad-leaf *Kaempferia galanga*",{size:24})}),

 P("This document provides (i) the computational Materials and Methods subsections, (ii) revised text for Results sections 3.5–3.12, and (iii) three new Results sections. Wet-laboratory Methods subsections (plant material, chloroplast isolation, DNA extraction, library preparation) and Results sections 3.1–3.4 and 3.8 are unchanged and are not reproduced here. Methods subsections are numbered from 2.7 on the assumption that 2.1–2.6 cover the wet-laboratory procedures; adjust to match the manuscript.",{size:20}),

 H1("Revision notes"),
 P("Every value below was recomputed from the primary GenBank files. The following substantive changes were made to the existing Results text.",{size:20}),
 TBL(revRows,Wr),

 // ============ METHODS ============
 H1("2. Materials and Methods (computational subsections)"),

 H2("2.7 Genome annotation and resolution of annotation conflicts"),
 P("Both assemblies were annotated with GeSeq v2.03 (Tillich et al., 2017) using BLAT v36x7 and Chloë v0.1.0 as parallel coding-sequence annotators, with inverted-repeat duplication enabled and tRNAscan-SE v2.0.7 for tRNA prediction. GenBank-format output was parsed with Biopython v1.87 (Cock et al., 2009), and coding sequences were extracted with the feature-extraction function so that intron splicing, exon order and strand orientation were handled automatically."),
 P("Where the two annotators produced more than one candidate coding sequence for the same gene, each candidate was translated under NCBI genetic code table 11 and the candidate yielding a clean open reading frame — methionine start, no internal stop codon, terminal stop codon — was retained as canonical. Where several candidates translated cleanly, their spliced nucleotide sequences were compared directly and the corresponding genomic sequences were inspected to determine whether the disagreement altered the mature transcript. Copies arising from inverted-repeat duplication were collapsed to a single representative per gene, following the single-copy convention used for protein-coding gene counts in the chloroplast genome literature."),
 P("Genes whose canonical coding length was not an exact multiple of three were excluded from all codon-based analyses. Gene symbols differing between the GeSeq output and the reference annotation were reconciled by genomic position and flanking-gene context rather than by name."),

 H2("2.8 Nucleotide composition"),
 P("Base composition was calculated genome-wide and separately for the LSC, SSC, IRa and IRb regions using the region boundaries annotated in the GeSeq output. Composition by codon position was calculated from the concatenated canonical single-copy coding sequence set, counting first, second and third codon positions separately."),

 H2("2.9 Comparison of the two morphotypes"),
 P("The KS and KB assemblies were compared base by base over their full length. Because the SSC region may be assembled in either of two equally valid orientations, SSC strand orientation was assessed first by comparing regional base composition for the mirrored pattern expected under inversion, and then by direct sequence comparison before and after reverse-complementation. Mismatch counts are reported both with and without the orientation correction so that the sensitivity of the comparison is verifiable."),

 H2("2.10 Alignment against the published reference and variant calling"),
 P("Each genome was reduced to a single-inverted-repeat (collinear) representation comprising LSC + IRb + SSC, with the duplicate IRa excluded; without this step a whole-genome aligner matches the inverted repeat equally well to either copy. Collinear representations were aligned to *K. galanga* MK209001.1 with minimap2 (Li, 2018) under the asm5 preset via the mappy Python interface. The alignment cs tag was parsed to recover every substitution and insertion or deletion at reference coordinates."),
 P("Variants were assigned to genomic regions and to gene models using the reference annotation, testing each exon part individually rather than the outer coordinates of the compound feature, so that the trans-spliced gene *rps12* was not treated as spanning the interval between its separated exons. For substitutions falling in coding sequence, the affected codon was identified from the reading frame and translated in both genomes to classify the change as synonymous or nonsynonymous. Every coding difference was then verified by comparing the raw genomic sequence at that locus between the two assemblies, because a one- or two-base exon-boundary disagreement between annotation pipelines can generate an apparent amino acid substitution where the underlying DNA is identical."),

 H2("2.11 Codon usage"),
 P("Relative synonymous codon usage (RSCU) was calculated from the canonical single-copy coding sequence set following Sharp, Tuohy and Mosurski (1986), as RSCU = n × (observed codon count) / (total count for that synonymous family), where n is the number of codons encoding the amino acid. Synonymous families were defined under genetic code table 11, with the three stop codons treated as a separate family. Values were computed independently for KS and KB."),

 H2("2.12 Substitution rate analysis"),
 P("Per-gene Ka/Ks ratios were not calculated, because almost every gene carried zero or one substitution relative to the reference, at which resolution per-gene ratios are statistically uninformative. Instead, synonymous and nonsynonymous site and difference counts were pooled across all genes for which the two annotations agreed on coding length, following Nei and Gojobori (1986), and a Jukes–Cantor (1969) correction was applied to yield a single genome-wide estimate. Genes for which the two annotations disagreed on coding length were excluded and are listed with their respective lengths; for each, the whole-genome alignment was inspected to confirm that no insertion or deletion was present within the coding region."),

 H2("2.13 Inverted repeat junction analysis"),
 P("The four junctions (JLB, LSC/IRb; JSB, IRb/SSC; JSA, SSC/IRa; JLA, IRa/LSC) were located from the annotated region boundaries of each genome. For each junction, the nearest gene on either side and its distance from the boundary were determined, together with any gene straddling the junction. Gene models were evaluated per exon part to avoid bounding-box artifacts from trans-spliced genes."),

 H2("2.14 Comparison with congeneric species"),
 P("Five published *Kaempferia* plastomes were included for comparison: *K. elegans* MK209002.1, *K. rotunda* MW326457.1, *K. rotunda* cv. Red Leaf MT473710.1, *K. rotunda* cv. Silver Diamonds MT473711.1, and *K. parviflora* OP805592.1. Each genome was aligned to MK209001.1 with minimap2 under the asm10 preset and projected onto reference coordinates to give a positional character matrix across all eight genomes. Alignments were searched on both strands to accommodate differences in SSC orientation between assemblies. Pairwise divergence was calculated over positions scorable in all eight genomes, genome-wide and separately by region."),

 H2("2.15 Phylogenetic analysis"),
 P("Phylogenetic analysis used the positional character matrix restricted to LSC + IRb + SSC, excluding the duplicate IRa. Columns unscorable in any genome were removed, leaving "+N.tree.nsites.toLocaleString()+" aligned positions of which "+N.tree.nvar.toLocaleString()+" were variable, comprising "+N.tree.npat+" distinct site patterns. Pairwise distances were calculated under the Kimura two-parameter model and a tree was constructed by neighbour-joining. Uncorrected p-distances and Jukes–Cantor distances were also computed and gave the same topology. Node support was assessed from 1,000 bootstrap replicates generated by multinomial resampling of site patterns. The tree was rooted at its midpoint; no outgroup was included, so the position of the root is not independently established."),

 H2("2.16 Development of species-diagnostic markers"),
 P("Positions were screened for candidate diagnostic sites, defined as positions scorable in all eight genomes at which the three *K. galanga* accessions shared one state and all five congeners carried a different state. Insertions and deletions were screened on the same criterion. Candidate amplicons were required to have primer-binding flanks identical across all eight genomes. Primer pairs were designed with Primer3 (primer3-py) under constraints of 19–26 nucleotides, melting temperature 57–63 °C, GC content 35–65% and a maximum melting-temperature difference of 2 °C between partners."),
 P("Candidate pairs were validated by in-silico PCR against the complete sequence of each genome, searching both strands with circular padding, permitting up to three mismatches per primer and requiring an exact match across the terminal five nucleotides at the 3′ end. Predicted product sizes were recorded for every genome, and candidate length polymorphisms were inspected for adjacent homopolymer tracts or tandem repeats that could render length calls unreliable."),
];

/* ============ RESULTS ============ */
body.push(
 H1("3. Results (revised and new sections)"),

 H2("3.5 Chloroplast genome structure and organization (revised)"),
 P("Assembly and annotation of the narrow-leaf (KS) and broad-leaf (KB) *K. galanga* chloroplast genomes yielded complete circular molecules of 163,799 bp for both morphotypes. Both displayed the quadripartite structure typical of angiosperm plastomes, comprising an LSC region of 88,429 bp and an SSC region of 15,776 bp separated by two inverted repeats of 29,797 bp each (Table 5; Figure 5). The published *K. galanga* reference genome (MK209001.1, RefSeq NC_040851.1) is 163,811 bp, with an LSC of 88,405 bp, an SSC of 15,812 bp and inverted repeats of 29,797 bp (Li, Zhao and Liu, 2019); the 12 bp difference in total length is accounted for by the insertion and deletion events described in Section 3.9."),
 P("The overall GC content of both genomes was 36.07%. GC content varied by region, from 29.58% in the SSC and 33.83% in the LSC to 41.11% in each inverted repeat. Regional AT content followed the inverse pattern, reaching 70.42% in the SSC."),
 P("The SSC region of the KB assembly was annotated on the opposite strand to that of KS and the reference. Regional base composition was mirrored between the two assemblies, with KS showing 35.92% A and 34.51% T and KB showing 34.51% A and 35.92% T, and the corresponding inversion of G and C proportions. Direct comparison of the two SSC sequences in the same orientation gave 28.60% identity, whereas reverse-complementation of the KB SSC gave 100% identity across all 15,776 bp. This orientation difference is a recognised consequence of the two equally frequent SSC isomers present in chloroplast genomes (Palmer, 1983) and does not represent a structural rearrangement."),

 H2("3.6 Gene content and annotation (revised)"),
 P("Annotation of the KS and KB genomes identified 79 unique protein-coding genes, four rRNA genes and 23 unique tRNA genes, giving 106 unique genes in total. Counting inverted-repeat duplicates as separate features, the annotation comprised 32 tRNA features. The corresponding counts for MK209001.1 are 79 protein-coding, four rRNA and 28 unique tRNA genes (38 tRNA features). Seven tRNA genes annotated in the reference were absent from the present annotation: *trnK-UUU*, *trnI-CAU*, *trnI-GAU*, *trnG-UCC*, *trnL-UAA*, *trnV-UAC* and *trnfM-CAU*. The GeSeq run reported here used tRNAscan-SE v2.0.7 with the Chloë tRNA module disabled, and the tRNA complement is therefore reported as incomplete pending re-annotation with tRNA prediction fully enabled.",{}),
 P("Of the 79 protein-coding genes, 78 were carried forward into codon-based analyses. *clpP1* was excluded because its annotated exon coordinates gave a total coding length of 622 bp, which is not divisible by three and therefore does not permit unambiguous codon partitioning; the reference annotates the corresponding gene at 621 bp."),
 P("Introns were identified in *rps12*, *ycf3* (*pafI*), *clpP1*, *ndhA*, *ndhB*, *rpl2*, *rpl16*, *petB*, *petD* and *atpF*. The trans-spliced gene *rps12* showed non-adjacent exon coordinates, with one exon in the LSC and two in the inverted repeat. Two candidate annotations were recovered for *ycf1*: a 3,888 bp copy lying entirely within IRb and a 5,466 bp copy spanning the SSC/IRa boundary. Both translated without internal stop codons; the 5,466 bp copy was retained as the functional gene and the shorter IRb copy is the truncated pseudogene-like copy documented at this position in Zingiberaceae and other monocot plastomes (Li, Zhao and Liu, 2019)."),
 P("Two genes required manual resolution of conflicting annotator output. For *ndhA*, BLAT and Chloë placed the intron boundary two bases apart; the two spliced products differ at one third-codon-position nucleotide and translate to an identical protein. For *ndhK*, neither candidate terminated in a stop codon within the annotated span, and the longer 744 bp candidate was retained against a reference length of 753 bp."),
 P("Five gene symbols differed between the GeSeq output and the reference annotation. Four are current synonyms: *pafI* for *ycf3*, *pafII* for *ycf4*, *pbf1* for *psbN*, and *clpP1* for *clpP*. In the fifth case, the 189 bp coding sequence annotated as *lhbA* in MK209001.1 is identical in nucleotide sequence to the gene annotated as *psbZ* in the present assemblies and encodes the same 62-residue product; the locus is reported here as *psbZ*."),

 H2("3.7 Codon usage and relative synonymous codon usage (revised)"),
 P("Codon usage was analysed across the 78 canonical protein-coding genes, comprising 68,001 bp of coding sequence and 22,667 codons. KS and KB gave identical codon counts at every codon, and a single table therefore applies to both genomes (Table 6)."),
 P("Base composition varied markedly by codon position (Table 1). A+T content rose from 54.94% at first positions to 62.15% at second positions and 71.90% at third positions, with an overall value of 63.00%. Third positions showed the lowest C content (12.97%) and the highest T content (39.03%) of the three positions."),
 CAP("Table 1. Nucleotide composition by codon position across the 78 canonical protein-coding genes of *Kaempferia galanga* (KS = KB). Based on 22,667 codons (68,001 bp); *clpP1* excluded."),
 TBL(cpRows,Wc),
 P("RSCU values showed a consistent preference for A- and U-ending codons and under-representation of G- and C-ending codons across every synonymous family. No codon was unused. Among the three stop codons, UAA was preferred over UAG and UGA. Full per-codon counts and RSCU values are given in Table 6.",{before:150}),

 H2("3.9 Comparative genomic analysis: KS, KB and the published reference (revised)"),
 P("Alignment of the collinear representations of KS and KB against MK209001.1 recovered a single primary alignment spanning all 134,002 bp of the non-redundant reference (mapping quality 60). Overall identity was 99.87%. Thirty-nine variant events separated the two morphotypes collectively from the reference: 22 substitutions, nine insertions totalling 68 bp and eight deletions totalling 80 bp, giving the net 12 bp reduction in genome length. At every one of these 39 positions, KS and KB carried the identical allele; no variant distinguished the two morphotypes."),
 P("Twenty-six variants fell in the LSC and 13 in the SSC. No variant was detected anywhere in the 29,797 bp inverted repeat. By feature class, 28 variants were intergenic, five lay in introns or untranslated regions of *trnK-UUU*, *rps16*, *trnP-UGG*, *clpP* and *rpl16*, and six fell within coding sequence. All six coding variants were substitutions; no insertion or deletion fell within any coding sequence."),
 P("The six coding substitutions are listed in Table 9. Three were synonymous and three were nonsynonymous. Each was verified by direct comparison of the genomic sequence at that locus between the two annotations. A seventh apparent coding substitution, a glutamine-to-lysine change in *rps12*, was shown to arise from a one-base disagreement in exon partitioning between the two annotations (27 + 231 bp against 26 + 232 bp) and was excluded; the underlying genomic sequence is identical across both exon regions."),
 CAP("Table 9. Coding-sequence substitutions between the KS/KB *Kaempferia galanga* genomes and the published reference MK209001.1. Positions are given in reference coordinates. Nonsynonymous changes are shaded."),
 TBL(cvRows,Wv),

 H2("3.11 Inverted repeat junction analysis (revised)"),
 P("The same genes flanked all four junctions in the KS/KB genomes and in the reference, and no junction shift was detected. At JLB, *rpl22* terminated 47 bp before the boundary and *rps19* began 147 bp inside IRb, so *rps19* is fully duplicated rather than divided by the junction. At JSB, *ndhF* began 30 bp inside the SSC and *trnN-GUU* lay 4,205 bp upstream within IRb. At JSA, *rps15* terminated 2,011 bp before the boundary. *ycf1* straddled both JSB and JSA, with the truncated copy on the IRb side and the full-length copy crossing JSA into the SSC. At JLA, *psbA* began 123 bp inside the LSC and no gene straddled the boundary."),

 H2("3.13 Comparison with congeneric species (new)"),
 P("The KS and KB genomes were compared with five published *Kaempferia* plastomes together with MK209001.1, giving eight genomes in total. Of the 134,002 non-redundant reference positions, 126,214 were scorable in all eight genomes and were used for all comparisons. Pairwise divergences are given in Table 10."),
 CAP("Table 10. Pairwise Kimura two-parameter distances among *Kaempferia* chloroplast genomes, calculated over 126,214 positions scorable in all eight genomes."),
 TBL(dvRows,Wd),
 P("Divergence between KS and KB was zero. Divergence between the KS/KB genomes and MK209001.1 was 0.0127%. Among the three *K. rotunda* accessions, divergence ranged from 0.0571% to 0.1841%. Interspecific divergences were an order of magnitude higher, with *K. elegans* the closest congener at 0.3440%, followed by *K. parviflora* at 0.4428% and the three *K. rotunda* accessions at 0.4699% to 0.5370%.",{before:150}),
 P("Regional divergence followed a consistent pattern in all five congeneric comparisons. The inverted repeats were the most conserved regions, at 0.087% to 0.161% divergence from the reference, and the SSC the least conserved, at 0.731% to 1.030%. LSC divergence was intermediate, at 0.382% to 0.646%."),

 H2("3.14 Phylogenetic analysis (new)"),
 P("Neighbour-joining analysis of the eight-genome alignment ("+N.tree.nsites.toLocaleString()+" positions, "+N.tree.nvar.toLocaleString()+" variable) recovered a fully resolved topology in which every node received at least 98% bootstrap support (Figure 6). Uncorrected p-distances, Jukes–Cantor distances and Kimura two-parameter distances all gave the same topology."),
 P("The three *K. galanga* accessions formed a clade with 100% support, within which KS and KB were joined by a node of 100% support and zero branch length. *K. elegans* was recovered as sister to the *K. galanga* clade with 100% support. The three *K. rotunda* accessions formed a clade with 100% support, within which MW326457.1 and cv. Red Leaf were joined with 98% support. *K. parviflora* was placed as sister to the *K. rotunda* clade. Because no outgroup was included, the tree was rooted at its midpoint and the position of the root is not independently established."),

 H2("3.15 Development of species-diagnostic markers (new)"),
 P("Screening the eight-genome matrix identified 178 positions at which the three *K. galanga* accessions shared one nucleotide state and all five congeneric accessions carried a different state, together with 14 insertion or deletion differences of at least 10 bp satisfying the same criterion. Of the 134,002 reference positions, 124,931 (93.2%) were identical across all eight genomes and therefore available as primer-binding sites."),
 P("Two length-polymorphic loci were developed into diagnostic assays and one nucleotide-substitution locus into a sequencing-based assay (Table 11). Primer-binding sites for all three pairs were identical across all eight genomes, and in-silico PCR yielded a single product from every genome."),
 CAP("Table 11. Primers developed for the identification of *Kaempferia galanga*, with predicted product sizes from in-silico PCR against eight *Kaempferia* chloroplast genomes. The Kg-ycf1 assay is shaded."),
 TBL(mkRows,Wm),
 P("The Kg-ycf1 assay amplified an 85 bp product from all three *K. galanga* accessions and a 67 bp product from all five congeners, an 18 bp difference corresponding to 21% of the product length. The polymorphism is an exact tandem duplication of the 18 bp motif CATAATCCTTTTGAAGAG within *ycf1*, present in two copies in *K. galanga* and one copy in every congener examined. The duplicated unit is in frame, corresponding to six codons, and its longest internal homopolymer run is four nucleotides.",{before:150}),
 P("The Kg-atpH assay amplified 99 bp from all three *K. galanga* accessions and 82 to 83 bp from the congeners, a difference of 16 to 17 bp arising from a 24 bp insertion in the *atpH*–*atpI* intergenic spacer. This amplicon also contains a mononucleotide A tract that varied between nine and 12 residues among the eight genomes."),
 P("The Kg-trnP amplicon spanned a region of *trnP-UGG* containing four diagnostic substitutions. Product sizes ranged from 489 to 510 bp and overlapped between *K. galanga* and the congeners, so this locus is distinguished by sequence rather than by product length; the amplicon differed from *K. elegans* at four positions and from the *K. rotunda* accessions at six to seven positions."),

 H2("3.12 Intraspecific comparison of the two morphotypes (revised)"),
 P("No nucleotide difference was detected between the KS and KB chloroplast genomes. The two assemblies were identical at all 163,799 positions once the SSC orientation difference described in Section 3.5 was corrected; the same comparison without that correction returned 11,264 mismatches, confirming that the procedure detects differences where they are present. The two genomes gave identical gene content, identical codon counts and RSCU values at all 64 codons, identical complementary-collapsed SSR profiles, identical inverted-repeat junction positions and flanking genes, and the identical allele at all 39 variant positions relative to the published reference. In the phylogenetic analysis, KS and KB were separated by a branch of zero length."),

 H1("Notes for completion"),
 P("1. The tRNA complement in Section 3.6 is reported as 23 unique genes, which is what the present annotation contains. Re-running GeSeq with tRNA annotation fully enabled is recommended, after which this figure and the total gene count should be updated.",{size:20}),
 P("2. Reference accession numbers are given as MK209001.1 with the RefSeq equivalent NC_040851.1 noted at first mention; the manuscript should use one form consistently.",{size:20}),
 P("3. Sections 3.1–3.4 and 3.8 have not been altered. Table 6 (RSCU) should be regenerated from the accompanying workbook, as several codon counts differ slightly from the current version.",{size:20}),
 P("4. Figures referenced: Figure 6, phylogenetic tree; Figure 7, variant position map; Figure 8, marker design and predicted product sizes.",{size:20}),
 P("5. All Ka/Ks values, the excluded-gene list and Section 3.10 are unchanged from the existing draft, having been independently reproduced.",{size:20}),
);

const doc=new Document({
 styles:{default:{document:{run:{font:FONT,size:SZ}}}},
 sections:[{properties:{page:{margin:{
   top:convertMillimetersToTwip(25.4),bottom:convertMillimetersToTwip(25.4),
   left:convertMillimetersToTwip(25.4),right:convertMillimetersToTwip(25.4)}}},
  children:body}]});
Packer.toBuffer(doc).then(b=>{
 fs.writeFileSync('K_galanga_Methods_and_Results_REVISED.docx',b);
 console.log('Wrote K_galanga_Methods_and_Results_REVISED.docx');});
