import os
OUT_DIR = os.environ.get("KG_OUTPUT_DIR", "output")
IN_DIR = os.environ.get("KG_INPUT_DIR", "data")
os.makedirs(OUT_DIR, exist_ok=True)
import json
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

data = json.load(open(OUT_DIR + "/misa_parsed.json"))

GENOMES = ["KS", "KB", "KG_ref", "K_rotunda", "K_rotunda_RedLeaf", "K_rotunda_SilverDiamonds", "K_parviflora"]
LABELS = {
    "KS": "K. galanga KS (narrow-leaf)",
    "KB": "K. galanga KB (broad-leaf)",
    "KG_ref": "K. galanga (ref, MK209001)",
    "K_rotunda": "K. rotunda (typical)",
    "K_rotunda_RedLeaf": "K. rotunda Red-Leaf",
    "K_rotunda_SilverDiamonds": "K. rotunda Silver Diamonds",
    "K_parviflora": "K. parviflora",
}
SHORT = {
    "KS": "KS", "KB": "KB", "KG_ref": "KG ref",
    "K_rotunda": "K.rot", "K_rotunda_RedLeaf": "K.rot RedLeaf",
    "K_rotunda_SilverDiamonds": "K.rot SilverDia", "K_parviflora": "K.parv",
}

wb = openpyxl.Workbook()

FONT = "Arial"
HEADER_FILL = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
HEADER_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
SUBHEADER_FONT = Font(name=FONT, bold=True, size=11)
NOTE_FONT = Font(name=FONT, italic=True, size=9, color="666666")
FLAG_FONT = Font(name=FONT, italic=True, bold=True, size=10, color="C00000")
GOOD_FONT = Font(name=FONT, italic=True, bold=True, size=10, color="1E7B34")
BODY_FONT = Font(name=FONT, size=10)
GOOD_FILL = PatternFill(start_color="E2F0D9", end_color="E2F0D9", fill_type="solid")
DIFF_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
SPECIES_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

CLASS_NAMES = {1: "Mononucleotide", 2: "Dinucleotide", 3: "Trinucleotide",
               4: "Tetranucleotide", 5: "Pentanucleotide", 6: "Hexanucleotide"}

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

n_g = len(GENOMES)

# ---------------------------------------------------------------
# README
# ---------------------------------------------------------------
ws = wb.active
ws.title = "README"
ws["A1"] = "Kaempferia Chloroplast SSR Comparison — All 7 Genomes Combined"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:H1")

ws["A3"] = ("Combines the K. galanga KS/KB/KG-ref workbook with the K. rotunda (3 morphotypes) + K. parviflora "
            "workbook into one file, all parsed directly from raw MISA '.statistics' output (no manual "
            "transcription).")
ws["A3"].font = GOOD_FONT
ws["A3"].fill = GOOD_FILL
ws["A3"].alignment = Alignment(wrap_text=True, vertical="top")
ws.merge_cells("A3:H3")
ws.row_dimensions[3].height = 30

lines = [
    "",
    "Genomes included (7):",
    "  Kaempferia galanga:",
    "    - KS (narrow-leaf, cultivated) -- 163,799 bp",
    "    - KB (broad-leaf, cultivated) -- 163,799 bp",
    "    - KG ref (MK209001 / NC_040851.1, Zhang et al. 2019) -- 163,811 bp",
    "  Kaempferia rotunda:",
    "    - K. rotunda (typical) -- 141,126 bp",
    "    - K. rotunda Red-Leaf -- 141,248 bp",
    "    - K. rotunda Silver Diamonds -- 141,222 bp",
    "  Kaempferia parviflora (outgroup / different species):",
    "    - K. parviflora -- 140,950 bp",
    "",
    "Two independent within-species comparisons live in this one file, each with its own within-group headline",
    "finding once SSR motifs are collapsed by reverse complement (SSR_Motif_Complementary sheet -- always check",
    "this sheet, not the strand-specific SSR_Motif_Totals sheet, before calling anything a real difference):",
    "  - K. galanga: KS vs KB are IDENTICAL on every repeat class (0 differences) -- consistent with the SNP/indel",
    "    analysis also finding no variant distinguishing the two morphotypes.",
    "  - K. rotunda: typical vs Red-Leaf differ by exactly 1 SSR (A/T mononucleotide class, 103 vs 102) -- the",
    "    closest thing to a real SSR difference found in either species group. Silver Diamonds differs more from",
    "    both (several rows), which may reflect assembly completeness rather than biology -- worth checking.",
    "  - K. galanga and K. rotunda/parviflora are NOT directly comparable in raw SSR counts (different genome",
    "    sizes, ~164 kb vs ~141 kb) -- use the density (/kb) columns on the Repeat_Type_Distribution sheet for any",
    "    cross-species comparison.",
    "",
    "MISA thresholds were identical across all 7 files: (1/8) (2/5) (3/4) (4/3) (5/3) (6/3), i.e. minimum 8 repeats",
    "for mononucleotide SSRs -- flag this against any cited paper that used a threshold of 10.",
    "",
    "Region_Size_GC and Variant_List_KBKS_vs_Ref (K. galanga only -- SNP/indel and LSC/SSC/IR region data) are",
    "carried over unchanged from the earlier K. galanga workbook; no equivalent annotation/variant data has been",
    "provided for the K. rotunda / K. parviflora genomes this session.",
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
ws["A1"] = "SSR Summary Statistics — All 7 Genomes"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:H1")

headers = ["Metric"] + [LABELS[g] for g in GENOMES]
hr = 3
for i, h in enumerate(headers, start=1):
    ws.cell(row=hr, column=i, value=h)
style_header_row(ws, hr, len(headers))

rows = [
    ["Source fasta file"] + [data[g]["source_file"] for g in GENOMES],
    ["Total size (bp)"] + [data[g]["total_size_bp"] for g in GENOMES],
    ["Total number of SSRs"] + [data[g]["total_ssrs"] for g in GENOMES],
    ["SSRs in compound formation"] + [data[g]["compound_ssrs"] for g in GENOMES],
    ["MISA thresholds used (mono..hexa)"] + ["8/5/4/3/3/3"] * n_g,
    ["Max interruption for compound SSR (bp)"] + [100] * n_g,
]
r0 = hr + 1
for i, row in enumerate(rows):
    r = r0 + i
    for c, v in enumerate(row, start=1):
        ws.cell(row=r, column=c, value=v)
last_r = r0 + len(rows) - 1
style_body(ws, r0, last_r, 1, len(headers))
autosize(ws, [30] + [20] * n_g)

note_r = last_r + 2
ws.cell(row=note_r, column=1,
        value="Note: MISA threshold '(1/8)' for mononucleotide (min. 8 repeats) applies to all 7 files -- confirm "
              "this matches what you intend to cite in the Methods (some reference papers use a threshold of 10).")
ws.cell(row=note_r, column=1).font = FLAG_FONT
ws.merge_cells(start_row=note_r, start_column=1, end_row=note_r, end_column=len(headers))
ws.row_dimensions[note_r].height = 30

# ---------------------------------------------------------------
# Repeat Type Distribution (+ density)
# ---------------------------------------------------------------
ws = wb.create_sheet("Repeat_Type_Distribution")
ws["A1"] = "SSR Repeat-Type Distribution and Density (SSRs per kb) — All 7 Genomes"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:O1")

ws["A3"] = "Genome size (bp)"
ws["A3"].font = SUBHEADER_FONT
for i, g in enumerate(GENOMES):
    col = 2 + i
    ws.cell(row=3, column=col, value=SHORT[g]).font = SUBHEADER_FONT
    cell = ws.cell(row=4, column=col, value=data[g]["total_size_bp"])
    cell.font = BODY_FONT
    cell.alignment = Alignment(horizontal="center")
    cell.border = BORDER

header_row = 6
cols = ["Repeat Type"] + [f"{SHORT[g]} (n)" for g in GENOMES] + [f"{SHORT[g]} /kb" for g in GENOMES]
for i, h in enumerate(cols, start=1):
    ws.cell(row=header_row, column=i, value=h)
style_header_row(ws, header_row, len(cols))

r0 = header_row + 1
for i in range(1, 7):
    r = r0 + (i - 1)
    ws.cell(row=r, column=1, value=CLASS_NAMES[i])
    for gi, g in enumerate(GENOMES):
        col = 2 + gi
        val = data[g]["unit_distribution"].get(str(i), 0)
        ws.cell(row=r, column=col, value=val)
    for gi in range(n_g):
        col = 2 + n_g + gi
        letter = get_column_letter(2 + gi)
        ws.cell(row=r, column=col, value=f'=IFERROR({letter}{r}/{letter}$4*1000,"")')
total_r = r0 + 6
ws.cell(row=total_r, column=1, value="Total")
for gi in range(n_g):
    col = 2 + gi
    letter = get_column_letter(col)
    ws.cell(row=total_r, column=col, value=f"=SUM({letter}{r0}:{letter}{r0+5})")
for gi in range(n_g):
    col = 2 + n_g + gi
    letter = get_column_letter(2 + gi)
    ws.cell(row=total_r, column=col, value=f'=IFERROR({letter}{total_r}/{letter}$4*1000,"")')
style_body(ws, r0, total_r, 1, len(cols))
for r in range(r0, total_r + 1):
    for c in range(2 + n_g, 2 + 2 * n_g):
        ws.cell(row=r, column=c).number_format = "0.00"
for c in range(1, len(cols) + 1):
    ws.cell(row=total_r, column=c).font = Font(name=FONT, bold=True)

autosize(ws, [16] + [10] * n_g + [10] * n_g)

note_r2 = total_r + 2
ws.cell(row=note_r2, column=1,
        value="K. galanga (KS/KB/KG ref, ~164 kb genomes) and K. rotunda/parviflora (~141 kb genomes) are different "
              "species with different genome sizes -- compare across the species groups using the density (/kb) "
              "columns, not raw counts.")
ws.cell(row=note_r2, column=1).font = NOTE_FONT
ws.merge_cells(start_row=note_r2, start_column=1, end_row=note_r2, end_column=len(cols))

# ---------------------------------------------------------------
# SSR Motif Totals (strand-specific)
# ---------------------------------------------------------------
ws = wb.create_sheet("SSR_Motif_Totals")
ws["A1"] = "SSR Motif Totals -- strand-specific (MISA 'Frequency of identified SSR motifs') — All 7 Genomes"
ws["A1"].font = Font(name=FONT, bold=True, size=12)
ws.merge_cells("A1:I1")
ws["A2"] = ("Yellow = differs within a species group (KS vs KB vs KG ref; or K. rotunda vs Red-Leaf vs Silver "
            "Diamonds). K. parviflora is a different species and expected to differ throughout -- not highlighted. "
            "Check SSR_Motif_Complementary before treating any highlighted row as a real biological difference.")
ws["A2"].font = Font(name=FONT, italic=True, size=9, color="9C6500")
ws.merge_cells("A2:I2")
ws.row_dimensions[2].height = 30

cols = ["Repeat class", "Motif"] + [f"{SHORT[g]} (n)" for g in GENOMES]
header_row = 4
for i, h in enumerate(cols, start=1):
    ws.cell(row=header_row, column=i, value=h)
style_header_row(ws, header_row, len(cols))

motif_tables = {g: data[g]["motifs"] for g in GENOMES}
all_motifs = list(dict.fromkeys([m for g in GENOMES for m in motif_tables[g].keys()]))
all_motifs.sort(key=lambda m: (len(m), m))

galanga_idx = [GENOMES.index(g) for g in ("KS", "KB", "KG_ref")]
rotunda_idx = [GENOMES.index(g) for g in ("K_rotunda", "K_rotunda_RedLeaf", "K_rotunda_SilverDiamonds")]

r0 = header_row + 1
for i, motif in enumerate(all_motifs):
    r = r0 + i
    vals = [motif_tables[g].get(motif, {}).get("total", 0) for g in GENOMES]
    ws.cell(row=r, column=1, value=CLASS_NAMES[len(motif)])
    ws.cell(row=r, column=2, value=motif)
    for gi, v in enumerate(vals):
        ws.cell(row=r, column=3 + gi, value=v)
    galanga_vals = [vals[i] for i in galanga_idx]
    rotunda_vals = [vals[i] for i in rotunda_idx]
    differs = (len(set(galanga_vals)) > 1) or (len(set(rotunda_vals)) > 1)
    if differs:
        for c in range(1, len(cols) + 1):
            ws.cell(row=r, column=c).fill = DIFF_FILL
last_r = r0 + len(all_motifs) - 1
style_body(ws, r0, last_r, 1, len(cols))

check_r = last_r + 1
ws.cell(row=check_r, column=1, value="Total")
ws.cell(row=check_r, column=1).font = Font(name=FONT, bold=True)
for gi in range(n_g):
    col = 3 + gi
    letter = get_column_letter(col)
    ws.cell(row=check_r, column=col, value=f"=SUM({letter}{r0}:{letter}{last_r})")
    ws.cell(row=check_r, column=col).font = Font(name=FONT, bold=True)
style_body(ws, check_r, check_r, 1, len(cols))
autosize(ws, [16, 12] + [11] * n_g)

# ---------------------------------------------------------------
# SSR Motif Complementary
# ---------------------------------------------------------------
ws = wb.create_sheet("SSR_Motif_Complementary")
ws["A1"] = ("SSR Repeat-Type Classes, Collapsed by Reverse Complement — All 7 Genomes "
            "(authoritative, strand-artifact-free comparison)")
ws["A1"].font = Font(name=FONT, bold=True, size=12)
ws.merge_cells("A1:I1")
ws["A2"] = "Yellow = differs within a species group (same logic as SSR_Motif_Totals)."
ws["A2"].font = Font(name=FONT, italic=True, size=9, color="9C6500")
ws.merge_cells("A2:I2")

cols = ["Repeat class", "Motif class"] + [f"{SHORT[g]} (n)" for g in GENOMES]
header_row = 4
for i, h in enumerate(cols, start=1):
    ws.cell(row=header_row, column=i, value=h)
style_header_row(ws, header_row, len(cols))

def base_len(label):
    return len(label.split("/")[0])

comp_tables = {g: data[g]["motifs_complementary"] for g in GENOMES}
all_c = list(dict.fromkeys([m for g in GENOMES for m in comp_tables[g].keys()]))
all_c.sort(key=lambda m: (base_len(m), m))

r0 = header_row + 1
for i, label in enumerate(all_c):
    r = r0 + i
    vals = [comp_tables[g].get(label, {}).get("total", 0) for g in GENOMES]
    ws.cell(row=r, column=1, value=CLASS_NAMES.get(base_len(label), f"{base_len(label)}-mer"))
    ws.cell(row=r, column=2, value=label)
    for gi, v in enumerate(vals):
        ws.cell(row=r, column=3 + gi, value=v)
    galanga_vals = [vals[i] for i in galanga_idx]
    rotunda_vals = [vals[i] for i in rotunda_idx]
    differs = (len(set(galanga_vals)) > 1) or (len(set(rotunda_vals)) > 1)
    if differs:
        for c in range(1, len(cols) + 1):
            ws.cell(row=r, column=c).fill = DIFF_FILL
last_r = r0 + len(all_c) - 1
style_body(ws, r0, last_r, 1, len(cols))

check_r = last_r + 1
ws.cell(row=check_r, column=1, value="Total")
ws.cell(row=check_r, column=1).font = Font(name=FONT, bold=True)
for gi in range(n_g):
    col = 3 + gi
    letter = get_column_letter(col)
    ws.cell(row=check_r, column=col, value=f"=SUM({letter}{r0}:{letter}{last_r})")
    ws.cell(row=check_r, column=col).font = Font(name=FONT, bold=True)
style_body(ws, check_r, check_r, 1, len(cols))
autosize(ws, [16, 16] + [11] * n_g)

note_r = check_r + 2
ws.cell(row=note_r, column=1,
        value="Within-species headline results: K. galanga KS vs KB vs KG ref -- KS and KB are identical on every "
              "row (KG ref, the published reference accession, differs from both on a few rows, as expected for a "
              "different individual/population). K. rotunda typical vs Red-Leaf differ only on the A/T "
              "mononucleotide row (103 vs 102); Silver Diamonds differs from both on several more rows.")
ws.cell(row=note_r, column=1).font = NOTE_FONT
ws.merge_cells(start_row=note_r, start_column=1, end_row=note_r, end_column=len(cols))
ws.row_dimensions[note_r].height = 30

# ---------------------------------------------------------------
# Region Size & GC (K. galanga only, carried over unchanged)
# ---------------------------------------------------------------
ws = wb.create_sheet("Region_Size_GC")
ws["A1"] = ("Chloroplast Genome Region Size and GC Content — K. galanga (KS/KB) only. No equivalent region/GC "
            "data provided this session for K. rotunda or K. parviflora.")
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
# Variant List (K. galanga only, carried over unchanged)
# ---------------------------------------------------------------
ws = wb.create_sheet("Variant_List_KBKS_vs_Ref")
ws["A1"] = ("Sequence Variants: KB & KS (identical) vs. NCBI Reference — K. galanga only. No equivalent variant "
            "data provided this session for K. rotunda or K. parviflora.")
ws["A1"].font = Font(name=FONT, bold=True, size=12)
ws.merge_cells("A1:G1")
ws["A2"] = ("Key finding: at every position below, KB and KS carry the same allele -- these variants distinguish "
            "the Taylor's Urban Farm plants (both morphotypes) from the reference genome, not KB from KS. "
            "Corroborated by SSR_Motif_Complementary: KS and KB match exactly on every SSR repeat class too.")
ws["A2"].font = Font(name=FONT, italic=True, bold=True, size=10, color="C00000")
ws.merge_cells("A2:G2")
ws.row_dimensions[2].height = 30

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

wb.save(OUT_DIR + "/Kaempferia_All7_SSR_Comparison.xlsx")
print("saved")
