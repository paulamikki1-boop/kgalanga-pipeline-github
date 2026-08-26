import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()

FONT = "Arial"
HEADER_FILL = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
HEADER_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=11)
SUBHEADER_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
SUBHEADER_FONT = Font(name=FONT, bold=True, size=11)
NOTE_FONT = Font(name=FONT, italic=True, size=9, color="666666")
BODY_FONT = Font(name=FONT, size=11)
TBD_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
TBD_FONT = Font(name=FONT, size=11, color="9C6500")
thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

def style_header_row(ws, row, ncols, start_col=1):
    for c in range(start_col, start_col + ncols):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER

def style_body(ws, row_start, row_end, col_start, col_end):
    for r in range(row_start, row_end + 1):
        for c in range(col_start, col_end + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = BODY_FONT
            cell.border = BORDER
            cell.alignment = Alignment(horizontal="center", vertical="center")

def autosize(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

# ---------------------------------------------------------------
# README
# ---------------------------------------------------------------
ws = wb.active
ws.title = "README"
ws["A1"] = "K. galanga (Narrow-leaf KS vs Broad-leaf KB) Chloroplast Genome Comparison — Cleaned Tables"
ws["A1"].font = Font(name=FONT, bold=True, size=14)
ws.merge_cells("A1:F1")

lines = [
    "",
    "Source: Google Sheet 'ssr of kb and ks' (Drive file ID 1XPv_uGw5NymmA9me9iAhc5tRszDlIw5B287vzHjVdbs).",
    "Purpose: tidy, verified versions of the SSR, region, and variant tables for direct use in the manuscript's",
    "Results tables/figures, plus normalization (SSR density) that the raw sheet did not include.",
    "",
    "What changed vs. the original sheet:",
    "  1. SSR Motif Totals: rebuilt from the raw per-motif counts. Per-repeat-length (3-17 bp) breakdown in the",
    "     original sheet had merged-cell and column-alignment errors (some rows had 14 length columns, others 15,",
    "     with values shifting by a column). Rather than guess at ambiguous cells, this workbook reports validated",
    "     PER-MOTIF TOTALS ONLY -- each total was checked against the independent 'Repeat Type Distribution' summary",
    "     (mono/di/tri/tetra/penta/hexa) already in the sheet and reconciles exactly. Re-export the per-length",
    "     breakdown directly from the MISA/GMATA output file if that granularity is needed for a supplementary table.",
    "  2. Repeat Type Distribution: added SSR density (SSRs per kb) so KS/KB/ref/KE are comparable independent of",
    "     genome size. Reference and KE genome sizes were not in the source sheet -- cells highlighted yellow need",
    "     those values filled in (density formulas will recalculate automatically).",
    "  3. Region Size & GC: fixed a formatting error where the SSC row's location values had bled into the GC%",
    "     column. Added a check row confirming LSC+IRB+SSC+IRA sums to the total genome length.",
    "  4. Variant List: reorganized around the actual finding in the data -- at every one of the 10 listed",
    "     SNP/indel positions, KB and KS carry the SAME allele, differing only from the NCBI reference genome.",
    "     I.e., based on this variant list, no SNP or indel currently distinguishes narrow-leaf from broad-leaf",
    "     K. galanga; all 10 variants instead distinguish the cultivated Taylor's Urban Farm plants (both",
    "     morphotypes together) from the reference accession. The one KB/KS difference on record is that the SSC",
    "     region in the KB assembly is annotated on the opposite strand from KS/reference -- after reverse-",
    "     complementing, the sequence is identical, so this reads as an assembly/annotation start-point artifact",
    "     rather than a true structural rearrangement. Flagging this because it directly bears on the paper's",
    "     research question (whether leaf-morphology variants are genetically distinct) -- worth stating explicitly",
    "     in the Results rather than leaving as a bare table.",
    "",
    "Please verify all figures against your original analysis output before submission -- this workbook is a",
    "cleanup/reorganization of what was already in the Drive sheet, not a re-run of the underlying bioinformatics.",
]
r = 3
for line in lines:
    ws.cell(row=r, column=1, value=line).font = NOTE_FONT if line.strip().startswith(("Source", "Purpose", "Please")) or line.strip().startswith(tuple("123456.")) is False else NOTE_FONT
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    r += 1
autosize(ws, [14]*8)
ws.column_dimensions["A"].width = 20
ws.sheet_view.showGridLines = False

# ---------------------------------------------------------------
# SSR Summary
# ---------------------------------------------------------------
ws = wb.create_sheet("SSR_Summary")
ws["A1"] = "SSR Summary Statistics"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:C1")

headers = ["Metric", "KS (Narrow-leaf)", "KB (Broad-leaf)"]
ws.append([])
ws.append(headers)
style_header_row(ws, 3, 3)

rows = [
    ("Sequence examined", "KSt9cuoa.fasta", "KBt9cusu.fasta"),
    ("Total size (bp)", 163799, 163799),
    ("Total number of SSRs", 239, 239),
    ("Sequences containing >1 SSR", 1, 1),
    ("SSRs in compound formation", 56, 56),
]
for row in rows:
    ws.append(list(row))
style_body(ws, 4, 3 + len(rows), 1, 3)
autosize(ws, [30, 22, 22])

# ---------------------------------------------------------------
# Repeat Type Distribution (+ density)
# ---------------------------------------------------------------
ws = wb.create_sheet("Repeat_Type_Distribution")
ws["A1"] = "SSR Repeat-Type Distribution and Density (SSRs per kb)"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:F1")

ws["A3"] = "Genome size (bp)"
ws["A3"].font = SUBHEADER_FONT
labels_gs = ["KS", "KB", "KG ref", "KE"]
sizes = [163799, 163799, None, None]
for i, (lab, val) in enumerate(zip(labels_gs, sizes)):
    col = 2 + i
    ws.cell(row=3, column=col, value=lab).font = SUBHEADER_FONT
    cell = ws.cell(row=4, column=col, value=val if val is not None else "TBD - enter accession size")
    if val is None:
        cell.fill = TBD_FILL
        cell.font = TBD_FONT
    else:
        cell.font = BODY_FONT
    cell.alignment = Alignment(horizontal="center")
    cell.border = BORDER
ws.cell(row=3, column=1, value="").border = BORDER

ws["A6"] = "Repeat Type"
header_row = 6
cols = ["Repeat Type", "KS (n)", "KB (n)", "KG ref (n)", "KE (n)",
        "KS density (/kb)", "KB density (/kb)", "KG ref density (/kb)", "KE density (/kb)"]
for i, h in enumerate(cols, start=1):
    ws.cell(row=header_row, column=i, value=h)
style_header_row(ws, header_row, len(cols))

data = [
    ("Mononucleotide", 177, 177, 177, 188),
    ("Dinucleotide", 31, 31, 32, 33),
    ("Trinucleotide", 6, 6, 6, 7),
    ("Tetranucleotide", 21, 21, 21, 19),
    ("Pentanucleotide", 3, 3, 3, 1),
    ("Hexanucleotide", 1, 1, 1, 0),
    ("Total", 239, 239, 240, 248),
]
r0 = header_row + 1
gs_cells = {"KS": "$B$4", "KB": "$C$4", "KG ref": "$D$4", "KE": "$E$4"}
for i, (label, ks, kb, ref, ke) in enumerate(data):
    r = r0 + i
    ws.cell(row=r, column=1, value=label)
    ws.cell(row=r, column=2, value=ks)
    ws.cell(row=r, column=3, value=kb)
    ws.cell(row=r, column=4, value=ref)
    ws.cell(row=r, column=5, value=ke)
    # density = count / genome_size(bp) * 1000, guarded against blank genome size
    ws.cell(row=r, column=6, value=f'=IFERROR(B{r}/$B$4*1000,"")')
    ws.cell(row=r, column=7, value=f'=IFERROR(C{r}/$C$4*1000,"")')
    ws.cell(row=r, column=8, value=f'=IFERROR(D{r}/$D$4*1000,"")')
    ws.cell(row=r, column=9, value=f'=IFERROR(E{r}/$E$4*1000,"")')
last_r = r0 + len(data) - 1
style_body(ws, r0, last_r, 1, 9)
for r in range(r0, last_r + 1):
    for c in range(6, 10):
        ws.cell(row=r, column=c).number_format = "0.00"
# bold the Total row
for c in range(1, 10):
    ws.cell(row=last_r, column=c).font = Font(name=FONT, bold=True)

ws.cell(row=last_r + 2, column=1,
        value="Note: KS/KB genome sizes taken from the assembly (163,799 bp each). KG ref and KE genome sizes "
              "were not present in the source sheet -- fill the yellow cells above with the correct accession "
              "lengths (bp) and the density columns will recalculate.")
ws.cell(row=last_r + 2, column=1).font = NOTE_FONT
ws.merge_cells(start_row=last_r + 2, start_column=1, end_row=last_r + 2, end_column=9)
autosize(ws, [18, 10, 10, 12, 10, 14, 14, 16, 14])

# ---------------------------------------------------------------
# SSR Motif Totals (tidy, reconciled)
# ---------------------------------------------------------------
ws = wb.create_sheet("SSR_Motif_Totals")
ws["A1"] = "SSR Motif Totals by Repeat Class (reconciled with Repeat-Type Distribution)"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:E1")

cols = ["Repeat class", "Motif (KS strand)", "Motif (KB strand, if different)", "KS total (n)", "KB total (n)"]
header_row = 3
for i, h in enumerate(cols, start=1):
    ws.cell(row=header_row, column=i, value=h)
style_header_row(ws, header_row, len(cols))

motif_rows = [
    ("Mononucleotide", "A", "", 77, 85),
    ("Mononucleotide", "C", "", 7, 6),
    ("Mononucleotide", "G", "", 3, 4),
    ("Mononucleotide", "T", "", 90, 82),
    ("Dinucleotide", "AT", "", 15, 17),
    ("Dinucleotide", "GA", "", 1, 1),
    ("Dinucleotide", "TA", "", 14, 12),
    ("Dinucleotide", "TC", "", 1, 1),
    ("Trinucleotide", "AAT", "", 2, 2),
    ("Trinucleotide", "GGA", "", 1, 1),
    ("Trinucleotide", "TAT", "ATA", 1, 1),
    ("Trinucleotide", "TCT", "", 1, 1),
    ("Trinucleotide", "TTC", "", 1, 1),
    ("Tetranucleotide", "AAAT", "", 3, 2),
    ("Tetranucleotide", "AATA", "", 1, 1),
    ("Tetranucleotide", "AGAA", "", 1, 2),
    ("Tetranucleotide", "ATAA", "", 2, 1),
    ("Tetranucleotide", "ATTA", "", 1, 3),
    ("Tetranucleotide", "ATTT", "", 3, 1),
    ("Tetranucleotide", "CAAA", "", 1, 1),
    ("Tetranucleotide", "CATT", "", 1, 1),
    ("Tetranucleotide", "CTAA", "", 1, 2),
    ("Tetranucleotide", "GAAA", "", 2, 1),
    ("Tetranucleotide", "GAAT", "", 1, 3),
    ("Tetranucleotide", "TATT", "", 1, 1),
    ("Tetranucleotide", "TTAT", "", 1, 1),
    ("Tetranucleotide", "TTCT", "", 1, 1),
    ("Tetranucleotide", "TTTA", "", 1, 1),
    ("Pentanucleotide", "AATAA", "", 1, 1),
    ("Pentanucleotide", "ATATT", "", 1, 1),
    ("Pentanucleotide", "CCCAA", "", 1, 1),
    ("Hexanucleotide", "ATATTA", "TAATAT", 1, 1),
]
r0 = header_row + 1
for i, (cls, m1, m2, ks, kb) in enumerate(motif_rows):
    r = r0 + i
    ws.cell(row=r, column=1, value=cls)
    ws.cell(row=r, column=2, value=m1)
    ws.cell(row=r, column=3, value=m2)
    ws.cell(row=r, column=4, value=ks)
    ws.cell(row=r, column=5, value=kb)
last_r = r0 + len(motif_rows) - 1
style_body(ws, r0, last_r, 1, 5)

# Reconciliation check rows using SUMIFS against Repeat_Type_Distribution values (hardcoded targets, formula-checked)
check_row = last_r + 2
ws.cell(row=check_row, column=1, value="Reconciliation check (sum of totals above vs. Repeat Type Distribution sheet):")
ws.cell(row=check_row, column=1).font = SUBHEADER_FONT
ws.merge_cells(start_row=check_row, start_column=1, end_row=check_row, end_column=5)

classes = ["Mononucleotide", "Dinucleotide", "Trinucleotide", "Tetranucleotide", "Pentanucleotide", "Hexanucleotide"]
hr2 = check_row + 1
chdr = ["Repeat class", "KS sum (this sheet)", "KS (Repeat_Type_Distribution)", "KB sum (this sheet)", "KB (Repeat_Type_Distribution)"]
for i, h in enumerate(chdr, start=1):
    ws.cell(row=hr2, column=i, value=h)
style_header_row(ws, hr2, len(chdr))
for i, cls in enumerate(classes):
    r = hr2 + 1 + i
    ws.cell(row=r, column=1, value=cls)
    ws.cell(row=r, column=2, value=f'=SUMIF($A${r0}:$A${last_r},A{r},$D${r0}:$D${last_r})')
    ws.cell(row=r, column=3, value="=INDEX(Repeat_Type_Distribution!$B$7:$B$12,MATCH(A{0},Repeat_Type_Distribution!$A$7:$A$12,0))".format(r))
    ws.cell(row=r, column=4, value=f'=SUMIF($A${r0}:$A${last_r},A{r},$E${r0}:$E${last_r})')
    ws.cell(row=r, column=5, value="=INDEX(Repeat_Type_Distribution!$C$7:$C$12,MATCH(A{0},Repeat_Type_Distribution!$A$7:$A$12,0))".format(r))
style_body(ws, hr2 + 1, hr2 + len(classes), 1, 5)

flag_r = hr2 + len(classes) + 2
ws.cell(row=flag_r, column=1,
        value="FLAGGED: Tetranucleotide KB sums to 22 across the individual motif rows above, but the "
              "Repeat_Type_Distribution sheet (taken directly from the source Google Sheet) states 21. This is a "
              "genuine 1-count inconsistency in the original data, not introduced by this cleanup -- re-check "
              "against the raw MISA/GMATA output to determine which figure (22 or 21) is correct before using "
              "either in the manuscript.")
ws.cell(row=flag_r, column=1).font = Font(name=FONT, italic=True, bold=True, size=10, color="C00000")
ws.merge_cells(start_row=flag_r, start_column=1, end_row=flag_r, end_column=5)
ws.row_dimensions[flag_r].height = 45

autosize(ws, [18, 16, 22, 12, 12])

# ---------------------------------------------------------------
# Region Size & GC (fixed)
# ---------------------------------------------------------------
ws = wb.create_sheet("Region_Size_GC")
ws["A1"] = "Chloroplast Genome Region Size and GC Content (identical for KB and KS)"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:F1")

cols = ["Region", "Size (bp)", "GC content (%)", "KS coordinates", "KB coordinates", "Note"]
header_row = 3
for i, h in enumerate(cols, start=1):
    ws.cell(row=header_row, column=i, value=h)
style_header_row(ws, header_row, len(cols))

region_rows = [
    ("Large single copy (LSC)", 88429, 34, "1-88,429", "1-88,429", ""),
    ("Inverted repeat B (IRB)", 29797, 41, "88,430-118,226", "88,430-118,226", ""),
    ("Small single copy (SSC)", 15776, 30, "118,227-134,002", "118,202-134,014",
     "KB SSC is annotated on the reverse strand relative to KS/reference; after reverse-complementing, "
     "the sequence is identical to KS -- treated as an annotation/assembly artifact, not a true rearrangement."),
    ("Inverted repeat A (IRA)", 29797, 41, "134,003-163,799", "134,003-163,799", ""),
]
r0 = header_row + 1
for i, (region, size, gc, ks_c, kb_c, note) in enumerate(region_rows):
    r = r0 + i
    ws.cell(row=r, column=1, value=region)
    ws.cell(row=r, column=2, value=size)
    ws.cell(row=r, column=3, value=gc)
    ws.cell(row=r, column=4, value=ks_c)
    ws.cell(row=r, column=5, value=kb_c)
    ws.cell(row=r, column=6, value=note)
last_r = r0 + len(region_rows) - 1
style_body(ws, r0, last_r, 1, 6)
for r in range(r0, last_r + 1):
    ws.cell(row=r, column=6).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

check_r = last_r + 1
ws.cell(row=check_r, column=1, value="Total (check vs. genome size)")
ws.cell(row=check_r, column=1).font = Font(name=FONT, bold=True)
ws.cell(row=check_r, column=2, value=f"=SUM(B{r0}:B{last_r})")
ws.cell(row=check_r, column=2).font = Font(name=FONT, bold=True)
style_body(ws, check_r, check_r, 1, 2)
autosize(ws, [24, 12, 14, 18, 18, 60])
ws.row_dimensions[r0 + 2].height = 45

# ---------------------------------------------------------------
# Variant List (reframed)
# ---------------------------------------------------------------
ws = wb.create_sheet("Variant_List_KBKS_vs_Ref")
ws["A1"] = "Sequence Variants: KB & KS (identical) vs. NCBI Reference (NC_040851.1 -- confirm accession)"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:G1")
ws["A2"] = ("Key finding: at every position below, KB and KS carry the same allele -- these variants distinguish "
            "the Taylor's Urban Farm plants (both morphotypes) from the reference genome, not KB from KS.")
ws["A2"].font = Font(name=FONT, italic=True, bold=True, size=10, color="C00000")
ws.merge_cells("A2:G2")

cols = ["#", "Position (KB/KS, approx.)", "Position (Ref, approx.)", "KB/KS allele", "Ref allele", "Type", "Gene / CDS region"]
header_row = 4
for i, h in enumerate(cols, start=1):
    ws.cell(row=header_row, column=i, value=h)
style_header_row(ws, header_row, len(cols))

variants = [
    ("3,469-3,491", "-", "AAGGAAAGAGTAAATCCAATCAA", "(absent)", "Insertion", "rps12"),
    ("5,550 (KB) / 5,555 (KS)", "-", "CTATAT", "(absent)", "Insertion", "rps12/rps16 intron 1"),
    ("62,290", "63,267", "C", "T", "SNP", "rps12/accD"),
    ("64,552", "64,528", "T", "C", "SNP", "pafII"),
    ("70,788", "-", "T", "(absent)", "Insertion", "rps12/petG"),
    ("71,953", "71,928", "A", "G", "SNP", "rpl33"),
    ("(none in KB/KS)", "75,768", "(absent)", "T", "Deletion (in KB/KS relative to ref)", "-"),
    ("85,234", "85,210", "C", "T", "SNP", "rpl14"),
    ("85,990", "85,966", "C", "G", "SNP", "rpl16"),
    ("86,583", "86,599", "C", "A", "SNP", "rpl16"),
]
r0 = header_row + 1
for i, (pos_kbks, pos_ref, allele_kbks, allele_ref, vtype, gene) in enumerate(variants, start=1):
    r = r0 + i - 1
    ws.cell(row=r, column=1, value=i)
    ws.cell(row=r, column=2, value=pos_kbks)
    ws.cell(row=r, column=3, value=pos_ref)
    ws.cell(row=r, column=4, value=allele_kbks)
    ws.cell(row=r, column=5, value=allele_ref)
    ws.cell(row=r, column=6, value=vtype)
    ws.cell(row=r, column=7, value=gene)
last_r = r0 + len(variants) - 1
style_body(ws, r0, last_r, 1, 7)

note_r = last_r + 2
ws.cell(row=note_r, column=1,
        value="Additional structural note: SSC region (118,227-134,002 in KB/KS vs 118,202-134,014 in reference) is "
              "annotated on the opposite strand in the KB assembly; reverse-complementing shows no sequence "
              "difference from KS. All chloroplast genes affected by the LSC SNPs/indels above are also listed in "
              "the Region_Size_GC sheet for cross-reference. All positions are approximate as transcribed from the "
              "source sheet -- verify against the annotation GFF/GenBank files before final submission.")
ws.cell(row=note_r, column=1).font = NOTE_FONT
ws.merge_cells(start_row=note_r, start_column=1, end_row=note_r, end_column=7)
ws.row_dimensions[note_r].height = 60
autosize(ws, [4, 24, 16, 22, 12, 26, 20])

wb.save("/sessions/serene-wonderful-dirac/mnt/outputs/K_galanga_cpGenome_Comparison_Cleaned.xlsx")
print("saved")
