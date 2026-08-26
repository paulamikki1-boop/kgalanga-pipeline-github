import json
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

data = json.load(open("/sessions/serene-wonderful-dirac/mnt/outputs/misa_parsed.json"))

GENOMES = ["K_rotunda", "K_rotunda_RedLeaf", "K_rotunda_SilverDiamonds", "K_parviflora"]
LABELS = {
    "K_rotunda": "K. rotunda (typical)",
    "K_rotunda_RedLeaf": "K. rotunda Red-Leaf",
    "K_rotunda_SilverDiamonds": "K. rotunda Silver Diamonds",
    "K_parviflora": "K. parviflora",
}

wb = openpyxl.Workbook()

FONT = "Arial"
HEADER_FILL = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
HEADER_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=11)
SUBHEADER_FONT = Font(name=FONT, bold=True, size=11)
NOTE_FONT = Font(name=FONT, italic=True, size=9, color="666666")
FLAG_FONT = Font(name=FONT, italic=True, bold=True, size=10, color="C00000")
GOOD_FONT = Font(name=FONT, italic=True, bold=True, size=10, color="1E7B34")
BODY_FONT = Font(name=FONT, size=11)
GOOD_FILL = PatternFill(start_color="E2F0D9", end_color="E2F0D9", fill_type="solid")
DIFF_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
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

# ---------------------------------------------------------------
# README
# ---------------------------------------------------------------
ws = wb.active
ws.title = "README"
ws["A1"] = "Kaempferia rotunda (3 leaf-color morphotypes) + K. parviflora — Chloroplast SSR Comparison"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:H1")

ws["A3"] = ("Source: raw MISA-web '.fasta.statistics' output files found in your connected folders "
            "Kaempferiarotunda, KaempferiarotundaRedLeafchloroplast, KaempferiarotundaSilverDiamonds, and "
            "Kaempferiaparviflora, parsed directly (same method used for the K. galanga KS/KB/KG-ref workbook). "
            "Plain-text .statistics files this time -- no merged-cell/Google-Sheet transcription risk.")
ws["A3"].font = GOOD_FONT
ws["A3"].fill = GOOD_FILL
ws["A3"].alignment = Alignment(wrap_text=True, vertical="top")
ws.merge_cells("A3:H3")
ws.row_dimensions[3].height = 45

lines = [
    "",
    "Genomes compared:",
    "  - K. rotunda (typical) -- 141,126 bp",
    "  - K. rotunda Red-Leaf -- 141,248 bp",
    "  - K. rotunda Silver Diamonds -- 141,222 bp",
    "  - K. parviflora (different species, included as outgroup context) -- 140,950 bp",
    "",
    "This mirrors the K. galanga KS-vs-KB structure: three K. rotunda leaf-color/pattern morphotypes plus a related",
    "species for context. If these three K. rotunda accessions are morphotypes of the same cultivated collection",
    "(the way KS/KB were narrow-/broad-leaf K. galanga), the same question applies: does leaf-color variation track",
    "with chloroplast-genome variation, or are the three morphotypes near-identical at the plastid level?",
    "",
    "Headline comparison:",
    "  - Total SSRs: K. rotunda 147, Red-Leaf 146, Silver Diamonds 155, K. parviflora 161 (different species, not",
    "    directly comparable in raw count without normalizing by genome size -- see density columns).",
    "  - K. rotunda and Red-Leaf are extremely close on every repeat-class count (109 vs 108 mono, 19 vs 19 di, 3 vs",
    "    3 tri, 14 vs 14 tetra, 2 vs 2 penta) -- only a 1-SSR difference in mononucleotides.",
    "  - Silver Diamonds differs a bit more from the other two rotunda accessions (115 mono, 17 di, 4 tri, 15 tetra,",
    "    3 penta, 1 hexa) -- worth checking whether that reflects a real biological difference or simply a less",
    "    complete/different assembly (its genome size, 141,222 bp, sits between the other two, so size alone",
    "    doesn't explain the gap).",
    "  - After collapsing by reverse complement (SSR_Motif_Complementary -- the strand-artifact-free comparison,",
    "    same lesson learned from the K. galanga KS/KB workbook): K. rotunda (typical) and Red-Leaf match on every",
    "    single repeat class except one -- A/T mononucleotides, 103 vs 102, a 1-SSR difference. That is the closest",
    "    thing to a real, confirmed SSR difference found between any of these genomes (unlike KS/KB, which were",
    "    perfectly identical after the same collapse). Silver Diamonds differs from both on several more rows",
    "    (A/T, C/G, AAT/ATT, AGG/CCT, AAAG/CTTT, AACT/AGTT, and three penta/hexa rows) -- a more substantial gap.",
    "  - MISA thresholds used: (1/8) (2/5) (3/4) (4/3) (5/3) (6/3) -- same '8' for mononucleotide flagged in the",
    "    K. galanga workbook. Same reminder applies if you're citing papers that used a threshold of 10.",
    "",
    "What this workbook does NOT cover (would need more source files):",
    "  - No SNP/indel or annotation (gene/exon/intron) data for these four genomes was provided this session --",
    "    only SSR statistics. If you want the same Region_Size_GC / Variant_List / gene-category tables built for",
    "    K. rotunda's three morphotypes, share the equivalent annotation/variant files and I'll build them the same",
    "    way as for K. galanga.",
    "  - The .fasta files are present in each folder, so codon-position nucleotide composition (as in Table 1 of",
    "    the reference paper) could be computed if wanted -- let me know if that's useful here too.",
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
ws.merge_cells("A1:E1")

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
    ["MISA thresholds used (mono..hexa)"] + ["8/5/4/3/3/3"] * len(GENOMES),
    ["Max interruption for compound SSR (bp)"] + [100] * len(GENOMES),
]
r0 = hr + 1
for i, row in enumerate(rows):
    r = r0 + i
    for c, v in enumerate(row, start=1):
        ws.cell(row=r, column=c, value=v)
last_r = r0 + len(rows) - 1
style_body(ws, r0, last_r, 1, len(headers))
autosize(ws, [30] + [22] * len(GENOMES))

note_r = last_r + 2
ws.cell(row=note_r, column=1,
        value="Note: MISA thresholds read '(1/8)' for mononucleotide (minimum 8 repeats) in all four source files "
              "-- same as the K. galanga dataset. Confirm this matches what you intend to cite in the Methods.")
ws.cell(row=note_r, column=1).font = FLAG_FONT
ws.merge_cells(start_row=note_r, start_column=1, end_row=note_r, end_column=len(headers))
ws.row_dimensions[note_r].height = 30

# ---------------------------------------------------------------
# Repeat Type Distribution (+ density)
# ---------------------------------------------------------------
ws = wb.create_sheet("Repeat_Type_Distribution")
ws["A1"] = "SSR Repeat-Type Distribution and Density (SSRs per kb)"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:I1")

ws["A3"] = "Genome size (bp)"
ws["A3"].font = SUBHEADER_FONT
for i, g in enumerate(GENOMES):
    col = 2 + i
    ws.cell(row=3, column=col, value=LABELS[g]).font = SUBHEADER_FONT
    cell = ws.cell(row=4, column=col, value=data[g]["total_size_bp"])
    cell.font = BODY_FONT
    cell.alignment = Alignment(horizontal="center")
    cell.border = BORDER

header_row = 6
cols = ["Repeat Type"] + [f"{LABELS[g]} (n)" for g in GENOMES] + [f"{LABELS[g]} density (/kb)" for g in GENOMES]
for i, h in enumerate(cols, start=1):
    ws.cell(row=header_row, column=i, value=h)
style_header_row(ws, header_row, len(cols))

n_g = len(GENOMES)
r0 = header_row + 1
for i in range(1, 7):
    r = r0 + (i - 1)
    ws.cell(row=r, column=1, value=CLASS_NAMES[i])
    for gi, g in enumerate(GENOMES):
        col = 2 + gi
        val = data[g]["unit_distribution"].get(str(i), 0)
        ws.cell(row=r, column=col, value=val)
    for gi, g in enumerate(GENOMES):
        col = 2 + n_g + gi
        src_col_letter = get_column_letter(2 + gi)
        size_col_letter = get_column_letter(2 + gi)
        ws.cell(row=r, column=col, value=f'=IFERROR({src_col_letter}{r}/{size_col_letter}$4*1000,"")')
total_r = r0 + 6
ws.cell(row=total_r, column=1, value="Total")
for gi in range(n_g):
    col = 2 + gi
    letter = get_column_letter(col)
    ws.cell(row=total_r, column=col, value=f"=SUM({letter}{r0}:{letter}{r0+5})")
for gi in range(n_g):
    col = 2 + n_g + gi
    src_letter = get_column_letter(2 + gi)
    ws.cell(row=total_r, column=col, value=f'=IFERROR({src_letter}{total_r}/{src_letter}$4*1000,"")')
style_body(ws, r0, total_r, 1, len(cols))
for r in range(r0, total_r + 1):
    for c in range(2 + n_g, 2 + 2 * n_g):
        ws.cell(row=r, column=c).number_format = "0.00"
for c in range(1, len(cols) + 1):
    ws.cell(row=total_r, column=c).font = Font(name=FONT, bold=True)

autosize(ws, [18] + [14] * n_g + [16] * n_g)

# ---------------------------------------------------------------
# SSR Motif Totals (strand-specific)
# ---------------------------------------------------------------
ws = wb.create_sheet("SSR_Motif_Totals")
ws["A1"] = "SSR Motif Totals -- strand-specific (MISA 'Frequency of identified SSR motifs')"
ws["A1"].font = Font(name=FONT, bold=True, size=13)
ws.merge_cells("A1:F1")
ws["A2"] = ("Yellow highlight = motif total differs among the three K. rotunda morphotypes (Red-Leaf and Silver "
            "Diamonds columns only, compared to typical). Check SSR_Motif_Complementary before treating any "
            "highlighted row as a real difference -- strand/orientation artifacts inflated apparent KS-vs-KB "
            "differences the same way in the K. galanga workbook.")
ws["A2"].font = Font(name=FONT, italic=True, size=9, color="9C6500")
ws.merge_cells("A2:F2")
ws.row_dimensions[2].height = 30

cols = ["Repeat class", "Motif"] + [f"{LABELS[g]} (n)" for g in GENOMES]
header_row = 4
for i, h in enumerate(cols, start=1):
    ws.cell(row=header_row, column=i, value=h)
style_header_row(ws, header_row, len(cols))

motif_tables = {g: data[g]["motifs"] for g in GENOMES}
all_motifs = list(dict.fromkeys([m for g in GENOMES for m in motif_tables[g].keys()]))
all_motifs.sort(key=lambda m: (len(m), m))

r0 = header_row + 1
for i, motif in enumerate(all_motifs):
    r = r0 + i
    vals = [motif_tables[g].get(motif, {}).get("total", 0) for g in GENOMES]
    ws.cell(row=r, column=1, value=CLASS_NAMES[len(motif)])
    ws.cell(row=r, column=2, value=motif)
    for gi, v in enumerate(vals):
        ws.cell(row=r, column=3 + gi, value=v)
    # highlight if rotunda-typical differs from RedLeaf or SilverDiamonds
    if vals[0] != vals[1] or vals[0] != vals[2]:
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
autosize(ws, [18, 14] + [16] * n_g)

# ---------------------------------------------------------------
# SSR Motif Complementary
# ---------------------------------------------------------------
ws = wb.create_sheet("SSR_Motif_Complementary")
ws["A1"] = ("SSR Repeat-Type Classes, Collapsed by Reverse Complement (MISA 'Frequency of classified repeat types "
            "considering sequence complementary') -- authoritative comparison, strand-artifact-free")
ws["A1"].font = Font(name=FONT, bold=True, size=12)
ws.merge_cells("A1:F1")

cols = ["Repeat class", "Motif class"] + [f"{LABELS[g]} (n)" for g in GENOMES]
header_row = 3
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
    if vals[0] != vals[1] or vals[0] != vals[2]:
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
autosize(ws, [18, 18] + [16] * n_g)

wb.save("/sessions/serene-wonderful-dirac/mnt/outputs/Kaempferia_rotunda_parviflora_SSR_Comparison.xlsx")
print("saved")
