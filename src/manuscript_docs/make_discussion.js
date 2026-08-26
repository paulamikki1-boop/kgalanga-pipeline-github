const fs=require('fs'), d=require('docx');
const {Document,Packer,Paragraph,TextRun,HeadingLevel,AlignmentType,
       convertMillimetersToTwip,BorderStyle}=d;

const FONT="Times New Roman", SZ=24, LINE=360;

function rich(t,{size=SZ,bold=false,italics=false,color=null}={}) {
  const runs=[]; t.split(/(\*[^*]+\*)/g).forEach(seg=>{
    if(!seg) return;
    const it=seg.startsWith("*")&&seg.endsWith("*")&&seg.length>2;
    runs.push(new TextRun({text:it?seg.slice(1,-1):seg,italics:it||italics,bold,size,font:FONT,color}));
  }); return runs;
}
const P=(t,o={})=>new Paragraph({
  spacing:{line:LINE,after:o.after??200,before:o.before??0},
  alignment:o.align??AlignmentType.JUSTIFIED,
  indent:{firstLine:convertMillimetersToTwip(6)},
  children:rich(t,{size:o.size??SZ,bold:o.bold,color:o.color})});
const LEAD=(lead,rest,o={})=>new Paragraph({
  spacing:{line:LINE,after:o.after??200},
  alignment:AlignmentType.JUSTIFIED,
  indent:{firstLine:convertMillimetersToTwip(6)},
  children:[new TextRun({text:lead+" ",bold:true,italics:true,size:SZ,font:FONT}),
            ...rich(rest,{size:SZ})]});
const H1=(t)=>new Paragraph({spacing:{line:LINE,before:320,after:160},
  children:rich(t,{bold:true,size:28})});
const NOTE=(t)=>new Paragraph({spacing:{line:280,after:160,before:60},
  shading:{type:"clear",fill:"FFF2CC"},
  children:rich(t,{size:19,italics:true,color:"7F6000"})});

const body=[
 new Paragraph({spacing:{after:80},alignment:AlignmentType.CENTER,
  children:rich("4. Discussion",{bold:true,size:30})}),
 new Paragraph({spacing:{after:260},alignment:AlignmentType.CENTER,
  children:rich("Draft — pending verification against the target journal's guide for authors and completion of wet-laboratory marker validation",{size:19,italics:true,color:"7F6000"})}),

 NOTE("Formatting note: this draft could not be checked against the Guide for Authors for the intended journal (page fetch failed on both a direct request and a browser-based retry — the Chrome extension used for browser access was not connected). Citation style, discussion length limits, and subheading conventions should be verified once accessible and this draft adjusted to match. It is written in continuous prose with bolded lead-in phrases per paragraph, a format that reads naturally with or without formal numbered subsections."),

 LEAD("Chloroplast isolation method determined the quality of everything downstream.",
 "Of the three isolation protocols tested, only the high-salt low-pH method yielded chloroplast preparations with absorbance values in the accepted 0.7–1.0 range at 440, 546 and 635 nm; sucrose gradient and Percoll gradient preparations remained below 0.08 across all three wavelengths despite being applied to the same source tissue. This is consistent with rhizomatous, starch- and mucilage-rich tissue of the kind found in *Kaempferia* being poorly suited to gradient-based approaches that were largely developed for leaf tissue, and argues for high-salt low-pH extraction as the default starting point for chloroplast genome projects in Zingiberaceae rhizomes rather than a protocol to be selected empirically each time. The downstream sequencing metrics obtained from this material — Q30 values exceeding 94% and assemblies resolving cleanly into the expected quadripartite structure for both morphotypes — indicate that isolation quality, rather than sequencing depth or assembly method, was the limiting step for this species."),

 LEAD("The two morphotypes are indistinguishable at the chloroplast genome level.",
 "KS and KB shared 100% sequence identity across all 163,799 bp once the SSC orientation artifact in the KB assembly was corrected, with identical gene content, identical codon usage at all 22,667 codons, identical relative synonymous codon usage values, identical simple sequence repeat profiles, and the same allele at all 39 positions distinguishing both genomes from the published reference. This result is unambiguous rather than a matter of statistical power: the comparison detected 11,264 differences between the two assemblies before the orientation correction was applied, confirming that the pipeline is sensitive to real sequence differences where they exist. The narrow- and broad-leaf phenotypes observed at Taylor's Urban Farm are therefore not associated with any detectable chloroplast-genome variation. Because plastids are maternally inherited in most angiosperms and the chloroplast genome encodes a comparatively small, function-constrained gene set concentrated in photosynthesis and gene expression machinery, this is the expected outcome if leaf-width variation is controlled by nuclear loci, by epigenetic regulation, or by developmental plasticity in response to microsite conditions at a single cultivation site, rather than a reason to have expected otherwise. Distinguishing between these possibilities is outside the scope of a plastome-only study and would require nuclear sequence data — genotyping-by-sequencing or a targeted nuclear marker panel — applied to the same two morphotypes."),

 LEAD("Divergence from the published reference is low and consistent with purifying selection.",
 "The 39 variants separating KS/KB from *K. galanga* MK209001.1 correspond to 99.87% sequence identity over the 134,002 bp non-redundant genome, and the pooled Ka/Ks estimate of 0.28 across 66 genes indicates that nonsynonymous substitutions are being removed more effectively than synonymous ones, as expected for a functionally constrained organellar genome. This estimate rests on only three synonymous and three nonsynonymous substitutions genome-wide, and should be read as indicating the direction of selection rather than as a precise quantitative estimate; a comparison with additional *K. galanga* accessions from independent geographic sources would be needed to determine whether 0.28 is representative of the species or specific to the accessions compared here. The three nonsynonymous substitutions detected — in *ycf4*, *rpl14* and *ycf1* — each involve a single amino acid change relative to the reference and cannot on this evidence alone be distinguished from selectively neutral variation; no claim of functional consequence is made for any of them."),

 LEAD("Two independent annotation discrepancies were resolved by returning to the raw genomic sequence, illustrating a general risk in comparative plastome work.",
 "A candidate nonsynonymous substitution in *rps12* initially appeared in the pooled substitution analysis but was traced to a one-nucleotide disagreement in exon partitioning between the two annotations (27 + 231 bp against 26 + 232 bp); the genomic sequence underlying both exon regions is identical, and the substitution was an artefact of where each annotation pipeline placed the intron boundary rather than a true difference. Similarly, *ycf1* was annotated with two candidate coding sequences differing by 1,578 bp, corresponding to the full-length copy crossing the SSC/IRa boundary and a truncated, pseudogene-like copy confined to IRb; using the shorter candidate would have altered both the codon usage totals and the coding-variant count reported here. Neither error would necessarily be apparent from the annotation output alone, and both were caught only because coding differences were re-checked against the raw genomic sequence at the nucleotide level rather than accepted from the annotation as given. This supports raw-sequence verification as a standard step before reporting coding-sequence variants in comparative chloroplast genome studies, particularly for genes known to be duplicated, trans-spliced, or annotated near an inverted-repeat boundary."),

 LEAD("The transfer RNA complement reported here is very likely an undercount, not a biological reduction.",
 "Twenty-three unique tRNA genes were recovered against 28 in the published reference, with the seven absent genes (*trnK-UUU*, *trnI-CAU*, *trnI-GAU*, *trnG-UCC*, *trnL-UAA*, *trnV-UAC* and *trnfM-CAU*) representing a substantial fraction of a plastid tRNA set that is otherwise highly conserved across angiosperms and would not be expected to vary between two morphotypes of the same species growing at the same site. This is attributable to the annotation pipeline configuration used, in which one of the two coding-sequence annotators additionally used for tRNA prediction was disabled; the reported tRNA count should be treated as provisional pending re-annotation with tRNA prediction fully enabled, and is flagged as such rather than reported as a genuine reduction in gene content."),

 LEAD("A likely mislabelling in the published reference genome was identified through direct sequence comparison.",
 "The 189 bp coding sequence annotated as *lhbA* in *K. galanga* MK209001.1 is identical in nucleotide sequence, at the corresponding genomic position, to the gene annotated as *psbZ* in the present assemblies, and both encode the same 62-residue protein. *lhbA* has no established assignment among characterised plastid genes at this locus, whereas *psbZ* (photosystem II protein Z) is the expected gene at this position in angiosperm plastomes generally. Four further symbol differences between the present annotation and the reference — *pafI*/*ycf3*, *pafII*/*ycf4*, *pbf1*/*psbN*, and *clpP1*/*clpP* — reflect ordinary nomenclature change over time rather than annotation disagreement and were resolved without difficulty by position and flanking-gene context. The *lhbA*/*psbZ* case is reported here because it appears in a public, actively cited reference accession and would benefit from correction independent of the present study."),

 LEAD("The eight-genome comparison places *K. galanga* within expected bounds of intrageneric divergence and identifies *K. elegans* as its closest relative among the taxa sampled.",
 "Pairwise K2P distance between *K. galanga* and *K. elegans* (0.344%) was roughly an order of magnitude greater than intraspecific divergence within *K. galanga* (0.013%) and within *K. rotunda* (0.057–0.184%), while divergence from *K. parviflora* (0.443%) and *K. rotunda* (0.470–0.537%) was of comparable or greater magnitude. This divergence gradient, together with a fully resolved neighbour-joining topology in which every internal node received at least 98% bootstrap support, is consistent with plastome data retaining adequate resolving power at this taxonomic depth within *Kaempferia*, notwithstanding the absence of an outgroup and the resulting reliance on midpoint rooting rather than a rooted maximum-likelihood analysis. The present analysis recovers the three *K. rotunda* accessions as a well-supported monophyletic group (100% bootstrap support for the clade as a whole; 98% for the internal node joining MW326457.1 and the Red Leaf cultivar), consistent with the pairwise distances among them (0.057–0.184%) being an order of magnitude below their shared distance from any other taxon sampled. Topologies placing any one of these three accessions outside this group should be re-examined for alignment or annotation artefacts, such as an uncorrected SSC-orientation difference of the kind identified in the KB assembly during this study, before being interpreted as evidence of non-monophyly."),

 LEAD("Simple sequence repeat content did not, on its own, yield a locus suitable for species-diagnostic use.",
 "Microsatellite profiling across all eight genomes, following standard thresholds (minimum 8/5/4/3/3/3 repeats for mono- through hexanucleotide motifs), found that KS and KB were identical across every repeat class, and that aggregate motif-class composition varied between *K. galanga* and its congeners without resolving to a single, positionally fixed locus usable as a length-polymorphism marker: differences observed were predominantly in the overall count of loci belonging to a given motif class across the genome, rather than in the length of any one addressable locus shared by all taxa compared. This outcome motivated a positionally resolved screen of the entire plastome for fixed differences of any kind — substitutions and insertions or deletions alike — rather than a search restricted to conventional 1–6 bp microsatellite motifs, and is reported here as the basis for that broader approach rather than as a source of the markers ultimately developed."),

 LEAD("The whole-genome screen identified a tandem-duplication marker with practical advantages over a sequence-based barcode for authentication purposes.",
 "The Kg-ycf1 assay resolves *K. galanga* from all five congeneric accessions examined by product size alone (85 bp against 67 bp, a difference of 21% of product length), arising from an 18 bp motif present in two tandem copies in *K. galanga* and one copy in every congener tested. Because the assay reads as a length difference on a standard gel rather than requiring base-level resolution, it is expected to tolerate the degraded or fragmented template DNA typical of processed rhizome material — dried, powdered, or heat-treated *K. galanga* of the kind encountered in herbal trade authentication — better than a sequencing-based barcode would, which is a material consideration given that adulteration of *K. galanga* rhizome with *K. rotunda* is a documented concern in that trade.",
 {after:80}),

 NOTE("[Wet-laboratory validation to be inserted here once results are available: sample panel composition, PCR conditions used relative to those proposed, observed product sizes per sample and per assay (Kg-ycf1, Kg-atpH), any ambiguous or discordant results, and gel image reference. The paragraph below is written to accommodate either outcome and should be revised once the specific result is known.]"),

 P("[Wet-lab confirmation paragraph — insert observed results, then interpret:] Concordance between the in-silico prediction and the observed wet-laboratory result would indicate that the whole-genome projection and in-silico PCR approach used here is sufficient on its own to screen candidate diagnostic markers before committing to bench validation, supporting its use for future marker development in this genus without requiring an initial exploratory wet-laboratory phase. Any discordance — an unexpected product size, absence of amplification, or a result differing between accessions predicted to be identical — would itself be informative, and should be examined for causes not captured by the computational screen: within-species copy-number variation at the tandem-duplication locus beyond the three accessions sampled here, degraded template performance, or off-target priming not detected by the mismatch-tolerant in-silico search used during design."),

 LEAD("Limitations.",
 "Several constraints bound the conclusions above. Both cultivated *K. galanga* morphotypes originate from a single site, and the reference and five congeneric genomes are each represented by a single accession with the exception of *K. rotunda* (three accessions); the low intraspecific divergence reported here may not generalise to *K. galanga* sampled across its full geographic range, and species-level divergence estimates for taxa represented by one accession cannot be distinguished from population-level variation within those species. Diagnostic marker specificity was established against five congeneric plastomes out of a genus containing approximately 50 recognised species, and should be treated as validated against the adulterants tested rather than against *Kaempferia* generally. The tRNA gene count is provisional pending re-annotation, as discussed above."),

 LEAD("Future directions.",
 "Nuclear sequence data — targeted markers or genotyping-by-sequencing applied to the KS and KB morphotypes — would establish whether the observed leaf-morphology difference has a genetic basis despite the absence of any chloroplast-level signal. Extending the diagnostic marker screen to additional *Kaempferia* species as sequence data become available would strengthen the specificity claim beyond the five congeners tested here, and re-annotation of the KS and KB genomes with tRNA prediction fully enabled would resolve the gene-count discrepancy identified in Section 3.6. A rooted maximum-likelihood phylogeny incorporating an outgroup from a related Zingiberaceae genus would also allow the topology reported here to be evaluated against a properly resolved root rather than a midpoint approximation."),
];

const doc=new Document({
 styles:{default:{document:{run:{font:FONT,size:SZ}}}},
 sections:[{properties:{page:{margin:{
   top:convertMillimetersToTwip(25.4),bottom:convertMillimetersToTwip(25.4),
   left:convertMillimetersToTwip(25.4),right:convertMillimetersToTwip(25.4)}}},
  children:body}]});
Packer.toBuffer(doc).then(b=>{
 fs.writeFileSync('K_galanga_Discussion_DRAFT.docx',b);
 console.log('Wrote K_galanga_Discussion_DRAFT.docx');});
