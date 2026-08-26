import json
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

galanga_data = json.load(open("/sessions/serene-wonderful-dirac/mnt/outputs/misa_parsed.json"))
ref_data = json.load(open("/sessions/serene-wonderful-dirac/mnt/outputs/corrected_reference.json"))
data = {**galanga_data, **ref_data}

GENOMES = ["KS", "KB", "KG_ref", "K_elegans", "K_rotunda", "K_rotunda_RedLeaf", "K_rotunda_SilverDiamonds", "K_parviflora"]
LABELS = {
    "KS": "K. galanga KS (narrow-leaf)",
    "KB": "K. galanga KB (broad-leaf)",
    "KG_ref": "K. galanga (ref, MK209001)",
    "K_elegans": "K. elegans (ref, MK209002)",
    "K_rotunda": "K. rotunda (ref, MW326457)",
    "K_rotunda_RedLeaf": "K. rotunda Red-Leaf (ref, MT473710)",
    "K_rotunda_SilverDiamonds": "K. rotunda Silver Diamonds (ref, MT473711)",
    "K_parviflora": "K. parviflora (ref, OP805592)",
}
SHORT = {
    "KS": "KS", "KB": "KB", "KG_ref": "KG ref", "K_elegans": "KE ref",
    "K_rotunda": "K.rot ref", "K_rotunda_RedLeaf": "K.rot RedLeaf ref",
    "K_rotunda_SilverDiamonds": "K.rot SilverDia ref", "K_parviflora": "K.parv ref",
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
FIX_FILL = PatternFill(start_color="FCE4E4", end_color="FCE4E4", fill_type="solid")
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
ws["A1"] = "Kaempferia Chloroplast SSR Comparison — All 8 Genomes (corrected reference data)"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:H1")

ws["A3"] = ("This version REPLACES the K. rotunda / K. rotunda Red-Leaf / K. rotunda Silver Diamonds / K. parviflora "
            "figures used in the previous 7-genome workbook, which were built from the wrong source files (~141 kb "
            "genome sizes). The correct data below is split out of a single MISA run on a 5-sequence batch FASTA of "
            "published NCBI reference accessions, cross-checked against individually-uploaded single-sequence FASTA "
            "files for exact genome length. K. elegans (KE), long flagged as unverified in this project, is now "
            "included for the first time with real data.")
ws["A3"].font = Font(name=FONT, italic=True, bold=True, size=10, color="C00000")
ws["A3"].fill = FIX_FILL
ws["A3"].alignment = Alignment(wrap_text=True, vertical="top")
ws.merge_cells("A3:H3")
ws.row_dimensions[3].height = 60

lines = [
    "",
    "Genomes included (8):",
    "  Kaempferia galanga (own sequenced/assembled genomes, cultivated at Taylor's Urban Farm):",
    "    - KS (narrow-leaf) -- 163,799 bp",
    "    - KB (broad-leaf) -- 163,799 bp",
    "    - KG ref (MK209001 / NC_040851.1, Zhang et al. 2019) -- 163,811 bp",
    "  Published NCBI reference accessions (correct data, this update):",
    "    - K. elegans (MK209002.1, Zhang et al. 2019) -- 163,555 bp",
    "    - K. rotunda (MW326457.1) -- 162,391 bp",
    "    - K. rotunda cv. Red-Leaf (MT473710.1) -- 162,630 bp",
    "    - K. rotunda cv. Silver Diamonds (MT473711.1) -- 162,875 bp",
    "    - K. parviflora (OP805592.1) -- 163,075 bp",
    "",
    "How the corrected numbers were derived: all 5 reference sequences were originally run through MISA together as "
    "one batch FASTA (kaempfariatjepr2.fasta), which produced a single POOLED '.statistics' summary (1,158 SSRs, "
    "814,526 bp total) that cannot be attributed to any one genome on its own. The underlying '.misa' file lists "
    "every SSR locus with its source sequence ID, so each locus was reassigned to its correct genome by that ID and "
    "re-tallied from scratch (unit-size distribution, motif frequency, and reverse-complement-collapsed motif "
    "frequency). This reconstruction was validated by summing all 5 genomes back together and confirming an exact "
    "match to the pooled file's own published totals (1,158 SSRs; unit distribution 865/144/27/108/12/2 for "
    "mono-hexanucleotide) -- see 'Validation' row below. Genome sizes were taken directly from the individually "
    "uploaded single-sequence FASTA files (exact character counts), not estimated.",
    "",
    "Two independent within-taxon comparisons, checked on the SSR_Motif_Complementary sheet (always use this sheet, "
    "not the strand-specific SSR_Motif_Totals sheet, before calling anything a real difference):",
    "  - K. galanga: KS vs KB are IDENTICAL on every repeat class (0 differences) -- consistent with the SNP/indel "
    "analysis also finding no variant distinguishing the two morphotypes.",
    "  - K. rotunda references: the typical form (MW326457) and Red-Leaf cultivar (MT473710) are IDENTICAL on every "
    "repeat class (0 differences, 221 SSRs each) despite ~239 bp genome-size difference and being filed as separate "
    "GenBank accessions. Silver Diamonds (MT473711) differs from both on several rows (232 SSRs total) -- worth a "
    "closer look if cultivar-level distinction matters for the manuscript.",
    "  - K. elegans and K. parviflora are distinct species/genera-adjacent taxa, not repeats of the K. galanga or "
    "K. rotunda group, and are not expected to match either group -- included here as outgroup reference points.",
    "",
    "MISA thresholds used for KS/KB/KG ref (own runs): (1/8) (2/5) (3/4) (4/3) (5/3) (6/3), i.e. minimum 8 repeats "
    "for mononucleotide SSRs. The reference batch run (kaempfariatjepr2.fasta.misa) used a lower effective minimum "
    "on some compound-locus sub-components (as low as 2-3 repeats within a compound arm), which is expected MISA "
    "behaviour for compound SSRs and not a threshold error -- simple (non-compound) loci in that file are consistent "
    "with a comparable threshold. Confirm both against your intended Methods citation regardless.",
    "",
    "Region_Size_GC and Variant_List_KBKS_vs_Ref (K. galanga only -- SNP/indel and LSC/SSC/IR region data) are "
    "carried over unchanged; no equivalent annotation/variant data has been provided for the reference genomes.",
]
r = 5
for line in lines:
    ws.cell(row=r, column=1, value=line).font = NOTE_FONT
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    ws.row_dimensions[r].height = 28 if len(line) > 120 else 14
    r += 1
ws.column_dimensions["A"].width = 20
for c in range(2, 9):
    ws.column_dimensions[get_column_letter(c)].width = 12
ws.sheet_view.showGridLines = False

# ---------------------------------------------------------------
# Validation sheet -- proves the per-accession split reproduces the pooled file's own totals
# ---------------------------------------------------------------
ws = wb.create_sheet("Validation_ReferenceSplit")
ws["A1"] = "Validation: Per-Accession Split vs. Pooled kaempfariatjepr2.fasta.statistics"
ws["A1"].font = Font(name=FONT, bold=True, size=12)
ws.merge_cells("A1:D1")

ref_genomes = ["K_elegans", "K_rotunda", "K_rotunda_RedLeaf", "K_rotunda_SilverDiamonds", "K_parviflora"]
cols = ["Metric", "Sum across 5 split genomes", "Pooled file's own reported total", "Match?"]
hr = 3
for i, h in enumerate(cols, start=1):
    ws.cell(row=hr, column=i, value=h)
style_header_row(ws, hr, len(cols))

sum_ssrs = sum(data[g]["total_ssrs"] for g in ref_genomes)
sum_unit = {u: sum(data[g]["unit_distribution"].get(str(u), 0) for g in ref_genomes) for u in range(1, 7)}
pooled_unit = {1: 865, 2: 144, 3: 27, 4: 108, 5: 12, 6: 2}
pooled_total = 1158

rows_v = [["Total number of identified SSRs", sum_ssrs, pooled_total, "YES" if sum_ssrs == pooled_total else "NO"]]
for u in range(1, 7):
    rows_v.append([f"{CLASS_NAMES[u]} SSR count", sum_unit[u], pooled_unit[u],
                    "YES" if sum_unit[u] == pooled_unit[u] else "NO"])
r0 = hr + 1
for i, row in enumerate(rows_v):
    r = r0 + i
    for c, v in enumerate(row, start=1):
        cell = ws.cell(row=r, column=c, value=v)
    if row[3] == "YES":
        ws.cell(row=r, column=4).font = Font(name=FONT, bold=True, color="1E7B34")
    else:
        ws.cell(row=r, column=4).font = Font(name=FONT, bold=True, color="C00000")
last_r = r0 + len(rows_v) - 1
style_body(ws, r0, last_r, 1, len(cols))
autosize(ws, [32, 24, 26, 10])
note_r = last_r + 2
ws.cell(row=note_r, column=1,
        value="Every row matches exactly, confirming no SSR loci were lost, duplicated, or mis-assigned when "
              "splitting the pooled batch file by sequence ID.")
ws.cell(row=note_r, column=1).font = GOOD_FONT
ws.merge_cells(start_row=note_r, start_column=1, end_row=note_r, end_column=len(cols))

# ---------------------------------------------------------------
# SSR Summary
# ---------------------------------------------------------------
ws = wb.create_sheet("SSR_Summary")
ws["A1"] = "SSR Summary Statistics — All 8 Genomes"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:I1")

headers = ["Metric"] + [LABELS[g] for g in GENOMES]
hr = 3
for i, h in enumerate(headers, start=1):
    ws.cell(row=hr, column=i, value=h)
style_header_row(ws, hr, len(headers))

rows = [
    ["Total size (bp)"] + [data[g]["total_size_bp"] for g in GENOMES],
    ["Total number of SSRs"] + [data[g]["total_ssrs"] for g in GENOMES],
    ["SSR/compound loci in compound formation"] + [data[g]["compound_ssrs"] for g in GENOMES],
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
        value="Reference genomes (K. elegans, K. rotunda x3, K. parviflora) were corrected in this rebuild -- "
              "see README for what changed and the Validation sheet for the cross-check against the source file.")
ws.cell(row=note_r, column=1).font = FLAG_FONT
ws.merge_cells(start_row=note_r, start_column=1, end_row=note_r, end_column=len(headers))
ws.row_dimensions[note_r].height = 30

# ---------------------------------------------------------------
# Repeat Type Distribution (+ density)
# ---------------------------------------------------------------
ws = wb.create_sheet("Repeat_Type_Distribution")
ws["A1"] = "SSR Repeat-Type Distribution and Density (SSRs per kb) — All 8 Genomes"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:Q1")

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

autosize(ws, [16] + [11] * n_g + [10] * n_g)

note_r2 = total_r + 2
ws.cell(row=note_r2, column=1,
        value="Genomes differ in size across taxa (K. galanga ~164 kb vs K. elegans/rotunda/parviflora ~162-163 kb) "
              "-- use the density (/kb) columns for cross-taxon comparison, raw counts for within-taxon comparison.")
ws.cell(row=note_r2, column=1).font = NOTE_FONT
ws.merge_cells(start_row=note_r2, start_column=1, end_row=note_r2, end_column=len(cols))

# ---------------------------------------------------------------
# SSR Motif Totals (strand-specific)
# ---------------------------------------------------------------
ws = wb.create_sheet("SSR_Motif_Totals")
ws["A1"] = "SSR Motif Totals -- strand-specific (MISA 'Frequency of identified SSR motifs') — All 8 Genomes"
ws["A1"].font = Font(name=FONT, bold=True, size=12)
ws.merge_cells("A1:J1")
ws["A2"] = ("Yellow = differs within a taxon group (KS vs KB vs KG ref; or K. rotunda vs Red-Leaf vs Silver "
            "Diamonds). K. elegans and K. parviflora are different species/outgroups and expected to differ "
            "throughout -- not highlighted. Check SSR_Motif_Complementary before treating any highlighted row as a "
            "real biological difference.")
ws["A2"].font = Font(name=FONT, italic=True, size=9, color="9C6500")
ws.merge_cells("A2:J2")
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
autosize(ws, [16, 12] + [12] * n_g)

# ---------------------------------------------------------------
# SSR Motif Complementary
# ---------------------------------------------------------------
ws = wb.create_sheet("SSR_Motif_Complementary")
ws["A1"] = ("SSR Repeat-Type Classes, Collapsed by Reverse Complement — All 8 Genomes "
            "(authoritative, strand-artifact-free comparison)")
ws["A1"].font = Font(name=FONT, bold=True, size=12)
ws.merge_cells("A1:J1")
ws["A2"] = "Yellow = differs within a taxon group (same logic as SSR_Motif_Totals)."
ws["A2"].font = Font(name=FONT, italic=True, size=9, color="9C6500")
ws.merge_cells("A2:J2")

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
autosize(ws, [16, 16] + [12] * n_g)

note_r = check_r + 2
ws.cell(row=note_r, column=1,
        value="Within-taxon headline results: K. galanga KS vs KB vs KG ref -- KS and KB identical on every row "
              "(KG ref, the published accession, differs from both on a few rows, as expected for a different "
              "individual/population). K. rotunda (MW326457) vs Red-Leaf (MT473710) -- IDENTICAL on every row (0 "
              "differences). Silver Diamonds (MT473711) differs from both on several rows.")
ws.cell(row=note_r, column=1).font = NOTE_FONT
ws.merge_cells(start_row=note_r, start_column=1, end_row=note_r, end_column=len(cols))
ws.row_dimensions[note_r].height = 30

# ---------------------------------------------------------------
# Region Size & GC (K. galanga only, carried over unchanged)
# ---------------------------------------------------------------
ws = wb.create_sheet("Region_Size_GC")
ws["A1"] = ("Chloroplast Genome Region Size and GC Content — K. galanga (KS/KB) only. No equivalent region/GC "
            "data provided for the reference genomes.")
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
            "data provided for the reference genomes.")
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

wb.save("/sessions/serene-wonderful-dirac/mnt/outputs/Kaempferia_All8_SSR_Comparison_CORRECTED.xlsx")
print("saved")
