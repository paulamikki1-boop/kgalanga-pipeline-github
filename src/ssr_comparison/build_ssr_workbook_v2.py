import json
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

data = json.load(open("/sessions/serene-wonderful-dirac/mnt/outputs/misa_parsed.json"))

wb = openpyxl.Workbook()

FONT = "Arial"
HEADER_FILL = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
HEADER_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=11)
SUBHEADER_FONT = Font(name=FONT, bold=True, size=11)
NOTE_FONT = Font(name=FONT, italic=True, size=9, color="666666")
FLAG_FONT = Font(name=FONT, italic=True, bold=True, size=10, color="C00000")
BODY_FONT = Font(name=FONT, size=11)
TBD_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
TBD_FONT = Font(name=FONT, size=11, color="9C6500")
FLAG_FILL = PatternFill(start_color="FCE4E4", end_color="FCE4E4", fill_type="solid")
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

CLASS_NAMES = {1: "Mononucleotide", 2: "Dinucleotide", 3: "Trinucleotide",
               4: "Tetranucleotide", 5: "Pentanucleotide", 6: "Hexanucleotide"}

# ---------------------------------------------------------------
# README
# ---------------------------------------------------------------
ws = wb.active
ws.title = "README"
ws["A1"] = "K. galanga (KS vs KB vs KG ref) Chloroplast SSR Comparison — Cleaned Tables (v2, from raw MISA output)"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:H1")

ws["A3"] = ("CRITICAL DATA ISSUE -- READ FIRST: the uploaded 'KS SSR.statistics' file is byte-for-byte identical "
            "to 'KB SSR.statistics', and its own header states its source sequence was 'KBt9cusu.fasta' -- the "
            "same file used for KB, not the KS fasta ('KSt9cuoa.fasta' per your earlier sheet). This means the KS "
            "SSR statistics you uploaded were not actually generated from the narrow-leaf (KS) genome -- they are "
            "a duplicate of the KB run. I have NOT treated this as real KS data below; the KS column in every "
            "table is marked 'UNVERIFIED / = KB' until you re-run MISA-web on the correct KSt9cuoa.fasta file and "
            "share that statistics file.")
ws["A3"].font = FLAG_FONT
ws["A3"].fill = FLAG_FILL
ws["A3"].alignment = Alignment(wrap_text=True, vertical="top")
ws.merge_cells("A3:H3")
ws.row_dimensions[3].height = 90

lines = [
    "",
    "Source: raw MISA-web '.statistics' output files you uploaded for KB, KS, and KG ref, parsed directly (no "
    "manual transcription), replacing the earlier version of this workbook that was built by hand-copying a "
    "merged-cell Google Sheet table (which, on cross-check against these raw files, turned out to contain several "
    "transcription errors -- e.g. the previous Tetranucleotide KB total was off by one, and at least one motif row "
    "was misaligned between columns).",
    "",
    "What's new / changed in this version:",
    "  1. SSR_Summary, Repeat_Type_Distribution, and SSR_Motif_Totals are now populated straight from the parsed",
    "     .statistics files for KB and KG ref -- these numbers are authoritative and reconcile internally by",
    "     construction (no more reconciliation-check mismatches).",
    "  2. KG ref genome size (163,811 bp) is now known from its .statistics file, so its SSR density (SSRs/kb) is",
    "     calculated where it previously showed 'TBD'.",
    "  3. Compound-SSR counts are now reported per genome individually (KB 56, KG ref 58) rather than assuming",
    "     they matched.",
    "  4. Added a new SSR_Motif_Complementary sheet -- MISA also reports motif counts collapsed by reverse-",
    "     complement pairing (e.g. A/T combined, AT/AT combined), which is the form most chloroplast-genome SSR",
    "     papers actually report in their tables/figures. Use this sheet, not SSR_Motif_Totals, as your primary",
    "     source for a manuscript table if you want to match typical publication style.",
    "  5. KE (the fourth genome referenced in your very first sheet) is not covered by any of the three uploaded",
    "     files, so it still is not included here.",
    "",
    "Region_Size_GC and Variant_List_KBKS_vs_Ref are unchanged from the previous version of this workbook -- these",
    "files don't contain that information, so nothing new to reconcile there.",
]
r = 5
for line in lines:
    ws.cell(row=r, column=1, value=line).font = NOTE_FONT
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    r += 1
ws.column_dimensions["A"].width = 20
for c in range(2, 9):
    ws.column_dimensions[get_column_letter(c)].width = 12
ws.sheet_view.showGridLines = False

# ---------------------------------------------------------------
# SSR Summary
# ---------------------------------------------------------------
ws = wb.create_sheet("SSR_Summary")
ws["A1"] = "SSR Summary Statistics (parsed from MISA-web .statistics output)"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:D1")

ws["A3"] = ("KS column below is UNVERIFIED -- see README. Values shown are what the uploaded file contained "
            "(identical to KB) and should not be treated as confirmed KS data.")
ws["A3"].font = FLAG_FONT
ws.merge_cells("A3:D3")

headers = ["Metric", "KS (UNVERIFIED, = KB)", "KB", "KG ref"]
hr = 5
for i, h in enumerate(headers, start=1):
    ws.cell(row=hr, column=i, value=h)
style_header_row(ws, hr, len(headers))

rows = [
    ("Source fasta file", data["KS"]["source_file"], data["KB"]["source_file"], data["KG_ref"]["source_file"]),
    ("Total size (bp)", data["KS"]["total_size_bp"], data["KB"]["total_size_bp"], data["KG_ref"]["total_size_bp"]),
    ("Total number of SSRs", data["KS"]["total_ssrs"], data["KB"]["total_ssrs"], data["KG_ref"]["total_ssrs"]),
    ("SSRs in compound formation", data["KS"]["compound_ssrs"], data["KB"]["compound_ssrs"], data["KG_ref"]["compound_ssrs"]),
    ("MISA thresholds used (mono..hexa)", "8/5/4/3/3/3", "8/5/4/3/3/3", "8/5/4/3/3/3"),
    ("Max interruption for compound SSR (bp)", 100, 100, 100),
]
r0 = hr + 1
for i, row in enumerate(rows):
    r = r0 + i
    for c, v in enumerate(row, start=1):
        ws.cell(row=r, column=c, value=v)
last_r = r0 + len(rows) - 1
style_body(ws, r0, last_r, 1, 4)
for rr in range(r0, last_r + 1):
    ws.cell(row=rr, column=2).fill = TBD_FILL
autosize(ws, [30, 24, 20, 20])

note_r = last_r + 2
ws.cell(row=note_r, column=1,
        value="Note: MISA thresholds here read '8' for mononucleotide, not '10' as cited in the three reference "
              "papers from your last request -- confirm which value you actually ran (the .statistics file "
              "header says '(1/8)', i.e. minimum 8 repeats for mononucleotide SSRs). If your Methods text should "
              "say '10', either the run needs to be redone with that threshold, or the Methods text should be "
              "corrected to match what was actually run (8).")
ws.cell(row=note_r, column=1).font = FLAG_FONT
ws.merge_cells(start_row=note_r, start_column=1, end_row=note_r, end_column=4)
ws.row_dimensions[note_r].height = 45

# ---------------------------------------------------------------
# Repeat Type Distribution (+ density)
# ---------------------------------------------------------------
ws = wb.create_sheet("Repeat_Type_Distribution")
ws["A1"] = "SSR Repeat-Type Distribution and Density (SSRs per kb)"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:E1")

ws["A3"] = "Genome size (bp)"
ws["A3"].font = SUBHEADER_FONT
labels_gs = ["KS (UNVERIFIED)", "KB", "KG ref"]
sizes = [data["KS"]["total_size_bp"], data["KB"]["total_size_bp"], data["KG_ref"]["total_size_bp"]]
for i, (lab, val) in enumerate(zip(labels_gs, sizes)):
    col = 2 + i
    ws.cell(row=3, column=col, value=lab).font = SUBHEADER_FONT
    cell = ws.cell(row=4, column=col, value=val)
    cell.font = TBD_FONT if i == 0 else BODY_FONT
    if i == 0:
        cell.fill = TBD_FILL
    cell.alignment = Alignment(horizontal="center")
    cell.border = BORDER

header_row = 6
cols = ["Repeat Type", "KS (n, UNVERIFIED)", "KB (n)", "KG ref (n)",
        "KS density (/kb)", "KB density (/kb)", "KG ref density (/kb)"]
for i, h in enumerate(cols, start=1):
    ws.cell(row=header_row, column=i, value=h)
style_header_row(ws, header_row, len(cols))

r0 = header_row + 1
for i in range(1, 7):
    r = r0 + (i - 1)
    ws.cell(row=r, column=1, value=CLASS_NAMES[i])
    ws.cell(row=r, column=2, value=data["KS"]["unit_distribution"][str(i)] if str(i) in data["KS"]["unit_distribution"] else data["KS"]["unit_distribution"].get(i))
    ws.cell(row=r, column=3, value=data["KB"]["unit_distribution"].get(str(i), data["KB"]["unit_distribution"].get(i)))
    ws.cell(row=r, column=4, value=data["KG_ref"]["unit_distribution"].get(str(i), data["KG_ref"]["unit_distribution"].get(i)))
    ws.cell(row=r, column=5, value=f'=IFERROR(B{r}/$B$4*1000,"")')
    ws.cell(row=r, column=6, value=f'=IFERROR(C{r}/$C$4*1000,"")')
    ws.cell(row=r, column=7, value=f'=IFERROR(D{r}/$D$4*1000,"")')
total_r = r0 + 6
ws.cell(row=total_r, column=1, value="Total")
ws.cell(row=total_r, column=2, value=f"=SUM(B{r0}:B{r0+5})")
ws.cell(row=total_r, column=3, value=f"=SUM(C{r0}:C{r0+5})")
ws.cell(row=total_r, column=4, value=f"=SUM(D{r0}:D{r0+5})")
ws.cell(row=total_r, column=5, value=f'=IFERROR(B{total_r}/$B$4*1000,"")')
ws.cell(row=total_r, column=6, value=f'=IFERROR(C{total_r}/$C$4*1000,"")')
ws.cell(row=total_r, column=7, value=f'=IFERROR(D{total_r}/$D$4*1000,"")')
style_body(ws, r0, total_r, 1, 7)
for r in range(r0, total_r + 1):
    for c in range(5, 8):
        ws.cell(row=r, column=c).number_format = "0.00"
for c in range(1, 8):
    ws.cell(row=total_r, column=c).font = Font(name=FONT, bold=True)

autosize(ws, [18, 16, 10, 12, 14, 14, 16])

# ---------------------------------------------------------------
# SSR Motif Totals (identified SSR motifs, strand-specific -- authoritative)
# ---------------------------------------------------------------
ws = wb.create_sheet("SSR_Motif_Totals")
ws["A1"] = "SSR Motif Totals -- strand-specific (as reported by MISA 'Frequency of identified SSR motifs')"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:D1")

cols = ["Repeat class", "Motif", "KB total (n)", "KG ref total (n)"]
header_row = 3
for i, h in enumerate(cols, start=1):
    ws.cell(row=header_row, column=i, value=h)
style_header_row(ws, header_row, len(cols))

kb_motifs = data["KB"]["motifs"]
ref_motifs = data["KG_ref"]["motifs"]
all_motifs = list(dict.fromkeys(list(kb_motifs.keys()) + list(ref_motifs.keys())))
all_motifs.sort(key=lambda m: (len(m), m))

r0 = header_row + 1
for i, motif in enumerate(all_motifs):
    r = r0 + i
    ws.cell(row=r, column=1, value=CLASS_NAMES[len(motif)])
    ws.cell(row=r, column=2, value=motif)
    ws.cell(row=r, column=3, value=kb_motifs.get(motif, {}).get("total", 0))
    ws.cell(row=r, column=4, value=ref_motifs.get(motif, {}).get("total", 0))
last_r = r0 + len(all_motifs) - 1
style_body(ws, r0, last_r, 1, 4)

check_r = last_r + 1
ws.cell(row=check_r, column=1, value="Total")
ws.cell(row=check_r, column=1).font = Font(name=FONT, bold=True)
ws.cell(row=check_r, column=3, value=f"=SUM(C{r0}:C{last_r})")
ws.cell(row=check_r, column=4, value=f"=SUM(D{r0}:D{last_r})")
style_body(ws, check_r, check_r, 1, 4)
for c in range(1, 5):
    ws.cell(row=check_r, column=c).font = Font(name=FONT, bold=True)

note_r = check_r + 2
ws.cell(row=note_r, column=1,
        value="KS column intentionally omitted here -- the uploaded KS statistics file is a duplicate of KB (see "
              "README). Re-run MISA on the correct KS fasta and re-parse to populate a genuine KS column.")
ws.cell(row=note_r, column=1).font = FLAG_FONT
ws.merge_cells(start_row=note_r, start_column=1, end_row=note_r, end_column=4)
ws.row_dimensions[note_r].height = 30
autosize(ws, [18, 14, 14, 14])

# ---------------------------------------------------------------
# SSR Motif Complementary (reverse-complement-collapsed classes)
# ---------------------------------------------------------------
ws = wb.create_sheet("SSR_Motif_Complementary")
ws["A1"] = ("SSR Repeat-Type Classes, Collapsed by Reverse Complement (MISA 'Frequency of classified repeat types "
            "considering sequence complementary') -- typical manuscript-table format")
ws["A1"].font = Font(name=FONT, bold=True, size=12)
ws.merge_cells("A1:D1")

cols = ["Repeat class", "Motif class", "KB total (n)", "KG ref total (n)"]
header_row = 3
for i, h in enumerate(cols, start=1):
    ws.cell(row=header_row, column=i, value=h)
style_header_row(ws, header_row, len(cols))

def base_len(label):
    # e.g. "AAAT/ATTT" -> 4 ; "A/T" -> 1
    first = label.split("/")[0]
    return len(first)

kb_c = data["KB"]["motifs_complementary"]
ref_c = data["KG_ref"]["motifs_complementary"]
all_c = list(dict.fromkeys(list(kb_c.keys()) + list(ref_c.keys())))
all_c.sort(key=lambda m: (base_len(m), m))

r0 = header_row + 1
for i, label in enumerate(all_c):
    r = r0 + i
    ws.cell(row=r, column=1, value=CLASS_NAMES.get(base_len(label), f"{base_len(label)}-mer"))
    ws.cell(row=r, column=2, value=label)
    ws.cell(row=r, column=3, value=kb_c.get(label, {}).get("total", 0))
    ws.cell(row=r, column=4, value=ref_c.get(label, {}).get("total", 0))
last_r = r0 + len(all_c) - 1
style_body(ws, r0, last_r, 1, 4)

check_r = last_r + 1
ws.cell(row=check_r, column=1, value="Total")
ws.cell(row=check_r, column=1).font = Font(name=FONT, bold=True)
ws.cell(row=check_r, column=3, value=f"=SUM(C{r0}:C{last_r})")
ws.cell(row=check_r, column=4, value=f"=SUM(D{r0}:D{last_r})")
style_body(ws, check_r, check_r, 1, 4)
for c in range(1, 5):
    ws.cell(row=check_r, column=c).font = Font(name=FONT, bold=True)
autosize(ws, [18, 18, 14, 14])

# ---------------------------------------------------------------
# Region Size & GC (carried over, unchanged)
# ---------------------------------------------------------------
ws = wb.create_sheet("Region_Size_GC")
ws["A1"] = "Chloroplast Genome Region Size and GC Content (identical for KB and KS per prior sheet -- unchanged, not covered by these files)"
ws["A1"].font = Font(name=FONT, bold=True, size=12)
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
for i, (region, size, gc, ks_c, kb_c_, note) in enumerate(region_rows):
    r = r0 + i
    ws.cell(row=r, column=1, value=region)
    ws.cell(row=r, column=2, value=size)
    ws.cell(row=r, column=3, value=gc)
    ws.cell(row=r, column=4, value=ks_c)
    ws.cell(row=r, column=5, value=kb_c_)
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
# Variant List (carried over, unchanged)
# ---------------------------------------------------------------
ws = wb.create_sheet("Variant_List_KBKS_vs_Ref")
ws["A1"] = "Sequence Variants: KB & KS (identical) vs. NCBI Reference (confirm accession) -- unchanged, not covered by these files"
ws["A1"].font = Font(name=FONT, bold=True, size=12)
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
autosize(ws, [4, 24, 16, 22, 12, 26, 20])

wb.save("/sessions/serene-wonderful-dirac/mnt/outputs/K_galanga_cpGenome_Comparison_Cleaned.xlsx")
print("saved v2")
