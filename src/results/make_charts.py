import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.gridspec import GridSpec

# ── Shared style ────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.titleweight': 'bold',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 180,
    'savefig.bbox': 'tight',
    'savefig.facecolor': 'white',
})

COLORS = {
    'KS':  '#2E86AB',   # blue  – narrow-leaf
    'KB':  '#A23B72',   # purple – broad-leaf
    'REF': '#F18F01',   # amber  – reference
}

OUT = '/sessions/great-blissful-davinci/mnt/outputs/'

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 – SSR Repeat-Type Distribution
# ══════════════════════════════════════════════════════════════════════════════
repeat_types = ['Mono-\nnucleotide', 'Di-\nnucleotide', 'Tri-\nnucleotide',
                'Tetra-\nnucleotide', 'Penta-\nnucleotide', 'Hexa-\nnucleotide']
ks_counts  = [177, 31, 6, 21, 3, 1]
kb_counts  = [177, 31, 6, 21, 3, 1]
ref_counts = [177, 32, 6, 21, 3, 1]

x = np.arange(len(repeat_types))
w = 0.26

fig, ax = plt.subplots(figsize=(9, 4.5))
bars_ks  = ax.bar(x - w,     ks_counts,  w, label='KS (narrow-leaf)', color=COLORS['KS'],  edgecolor='white', linewidth=0.5)
bars_kb  = ax.bar(x,         kb_counts,  w, label='KB (broad-leaf)',   color=COLORS['KB'],  edgecolor='white', linewidth=0.5)
bars_ref = ax.bar(x + w,     ref_counts, w, label='KG ref (NC_040851.1)', color=COLORS['REF'], edgecolor='white', linewidth=0.5)

# value labels on top of mononucleotide only (too tall for others)
for bars in (bars_ks, bars_kb, bars_ref):
    for bar in bars:
        h = bar.get_height()
        if h > 5:
            ax.text(bar.get_x() + bar.get_width()/2, h + 1.5, str(int(h)),
                    ha='center', va='bottom', fontsize=8, color='#333')

ax.set_xticks(x)
ax.set_xticklabels(repeat_types, fontsize=9)
ax.set_ylabel('Number of SSRs')
ax.set_title('Figure 1. SSR Repeat-Type Distribution in KS, KB, and Reference\nKaempferia galanga Chloroplast Genomes')
ax.legend(frameon=False, loc='upper right', fontsize=9)
ax.set_ylim(0, 210)
ax.yaxis.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(OUT + 'Fig1_SSR_RepeatType_Distribution.png')
plt.close(fig)
print("Fig1 done")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 – SSR Complementary-Collapsed Motif Classes (stacked bar)
# ══════════════════════════════════════════════════════════════════════════════
motifs = [
    'A/T',
    'C/G',
    'AT/AT',
    'AG/CT',
    'AAT/ATT',
    'AAG/CTT',
    'AGG/CCT',
    'AAAT/ATTT',
    'AAAG/CTTT',
    'AATG/ATTC',
    'AATT/AATT',
    'AACT/AGTT',
    'AAAC/GTTT',
    'Penta (×3)',
    'AATATT/AATATT',
]
ks_m  = [167, 10, 29, 2, 3, 2, 1, 12, 4, 2, 1, 1, 1, 3, 1]
kb_m  = [167, 10, 29, 2, 3, 2, 1, 12, 4, 2, 1, 1, 1, 3, 1]
ref_m = [167, 10, 30, 2, 3, 2, 1, 12, 4, 2, 1, 1, 1, 3, 1]

# Horizontal grouped bar – sorted by KS count desc
order = sorted(range(len(motifs)), key=lambda i: ks_m[i], reverse=True)
motifs_s = [motifs[i] for i in order]
ks_s  = [ks_m[i]  for i in order]
kb_s  = [kb_m[i]  for i in order]
ref_s = [ref_m[i] for i in order]

y  = np.arange(len(motifs_s))
wh = 0.26

fig, ax = plt.subplots(figsize=(9, 7))
ax.barh(y + wh,     ks_s,  wh, label='KS (narrow-leaf)',      color=COLORS['KS'],  edgecolor='white')
ax.barh(y,          kb_s,  wh, label='KB (broad-leaf)',        color=COLORS['KB'],  edgecolor='white')
ax.barh(y - wh,     ref_s, wh, label='KG ref (NC_040851.1)',   color=COLORS['REF'], edgecolor='white')

ax.set_yticks(y)
ax.set_yticklabels(motifs_s, fontsize=9, fontstyle='italic')
ax.set_xlabel('Number of SSRs')
ax.set_title('Figure 2. SSR Motif Class Frequencies (Complementary-Collapsed)\nin KS, KB, and Reference Kaempferia galanga Chloroplast Genomes')
ax.legend(frameon=False, fontsize=9)
ax.xaxis.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
ax.set_axisbelow(True)
ax.invert_yaxis()

# Annotate the one difference: AT/AT ref = 30
ax.axvline(30, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)

fig.tight_layout()
fig.savefig(OUT + 'Fig2_SSR_MotifClasses_Complementary.png')
plt.close(fig)
print("Fig2 done")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 – Genome Region Composition & GC Content (two panels)
# ══════════════════════════════════════════════════════════════════════════════
regions    = ['LSC', 'IRb', 'SSC', 'IRa']
sizes_bp   = [88429, 29797, 15776, 29797]   # same for KS and KB
gc_pct     = [34.0,  41.0,  30.0,  41.0]
pie_colors = ['#4E9AF1', '#2ECC71', '#F39C12', '#9B59B6']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

# --- Panel A: donut chart ---
wedges, texts, autotexts = ax1.pie(
    sizes_bp,
    labels=None,
    autopct='%1.1f%%',
    startangle=90,
    colors=pie_colors,
    wedgeprops=dict(width=0.55, edgecolor='white', linewidth=2),
    pctdistance=0.75,
)
for t in autotexts:
    t.set_fontsize(9)
    t.set_color('white')
    t.set_fontweight('bold')

# centre label
ax1.text(0, 0, '163,799 bp\n(KS = KB)', ha='center', va='center',
         fontsize=9, color='#333', fontweight='bold')

legend_labels = [f'{r}\n{s:,} bp' for r, s in zip(regions, sizes_bp)]
ax1.legend(wedges, legend_labels, loc='lower center',
           bbox_to_anchor=(0.5, -0.18), ncol=2, frameon=False, fontsize=9)
ax1.set_title('(A) Genome Region Proportions', pad=10)

# --- Panel B: GC content bar chart ---
bar_colors_gc = ['#4E9AF1', '#2ECC71', '#F39C12', '#9B59B6']
bars = ax2.bar(regions, gc_pct, color=bar_colors_gc, edgecolor='white',
               width=0.55, linewidth=1.5)
for bar, pct in zip(bars, gc_pct):
    ax2.text(bar.get_x() + bar.get_width()/2, pct + 0.5, f'{pct:.1f}%',
             ha='center', va='bottom', fontsize=9, fontweight='bold')
ax2.set_ylabel('GC Content (%)')
ax2.set_ylim(0, 50)
ax2.yaxis.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
ax2.set_axisbelow(True)
ax2.set_title('(B) GC Content by Genome Region', pad=10)

# overall average line
overall_gc = sum(s * g for s, g in zip(sizes_bp, gc_pct)) / sum(sizes_bp)
ax2.axhline(overall_gc, color='#E74C3C', linestyle='--', linewidth=1.2,
            label=f'Overall GC = {overall_gc:.1f}%')
ax2.legend(frameon=False, fontsize=9)

fig.suptitle('Figure 3. Structural Features of the KS/KB Kaempferia galanga\nChloroplast Genome (163,799 bp)',
             fontsize=11, fontweight='bold', y=1.01)
fig.tight_layout()
fig.savefig(OUT + 'Fig3_Genome_Region_Composition_GC.png')
plt.close(fig)
print("Fig3 done")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 – RSCU Bar Chart (all 59 sense codons, coloured by amino acid)
# ══════════════════════════════════════════════════════════════════════════════
# Full RSCU data (KB = KS)
rscu_data = [
    ('Ala','GCU',566,1.86), ('Ala','GCA',373,1.22), ('Ala','GCC',179,0.59), ('Ala','GCG',102,0.33),
    ('Arg','AGA',432,1.93), ('Arg','CGU',318,1.42), ('Arg','CGA',294,1.31), ('Arg','AGG',135,0.60),
    ('Arg','CGG',88,0.39),  ('Arg','CGC',76,0.34),
    ('Asn','AAU',841,1.56), ('Asn','AAC',240,0.44),
    ('Asp','GAU',734,1.65), ('Asp','GAC',157,0.35),
    ('Cys','UGU',208,1.59), ('Cys','UGC',53,0.41),
    ('Glu','GAA',921,1.53), ('Glu','GAG',281,0.47),
    ('Phe','UUU',845,1.33), ('Phe','UUC',426,0.67),
    ('Gly','GGA',623,1.62), ('Gly','GGU',547,1.42), ('Gly','GGG',239,0.62), ('Gly','GGC',127,0.33),
    ('His','CAU',425,1.57), ('His','CAC',117,0.43),
    ('Ile','AUU',1003,1.50), ('Ile','AUA',645,0.96), ('Ile','AUC',359,0.54),
    ('Leu','UUA',789,2.01), ('Leu','UUG',489,1.25), ('Leu','CUU',490,1.25),
    ('Leu','CUA',312,0.80), ('Leu','CUC',145,0.37), ('Leu','CUG',126,0.32),
    ('Lys','AAA',928,1.51), ('Lys','AAG',299,0.49),
    ('Met','AUG',528,1.00),
    ('Asn','AAU',841,1.56),  # already above – skip duplicates
    ('Pro','CCU',381,1.65), ('Pro','CCA',259,1.12), ('Pro','CCC',176,0.76), ('Pro','CCG',107,0.46),
    ('Gln','CAA',611,1.56), ('Gln','CAG',173,0.44),
    ('Ser','UCU',497,1.72), ('Ser','AGU',381,1.32), ('Ser','UCA',345,1.19),
    ('Ser','UCC',275,0.95), ('Ser','UCG',152,0.53), ('Ser','AGC',86,0.30),
    ('Thr','ACU',463,1.62), ('Thr','ACA',364,1.27), ('Thr','ACC',197,0.69), ('Thr','ACG',122,0.43),
    ('Trp','UGG',396,1.00),
    ('Tyr','UAU',680,1.58), ('Tyr','UAC',183,0.42),
    ('Val','GUA',488,1.55), ('Val','GUU',462,1.47), ('Val','GUC',141,0.45), ('Val','GUG',169,0.54),
]
# Deduplicate (keep first occurrence)
seen = set()
rscu_unique = []
for row in rscu_data:
    key = row[1]
    if key not in seen:
        seen.add(key)
        rscu_unique.append(row)

# Sort by amino acid then RSCU desc
rscu_unique.sort(key=lambda r: (r[0], -r[3]))

aa_list = [r[0] for r in rscu_unique]
codon_list = [r[1] for r in rscu_unique]
rscu_vals  = [r[3] for r in rscu_unique]

# Assign colour per amino acid
unique_aas = list(dict.fromkeys(aa_list))
cmap = plt.get_cmap('tab20', len(unique_aas))
aa_color = {aa: cmap(i) for i, aa in enumerate(unique_aas)}
bar_colors = [aa_color[aa] for aa in aa_list]

fig, ax = plt.subplots(figsize=(16, 5))
x_pos = np.arange(len(rscu_unique))
bars = ax.bar(x_pos, rscu_vals, color=bar_colors, edgecolor='white', linewidth=0.4, width=0.8)

ax.axhline(1.0, color='black', linestyle='--', linewidth=0.9, label='RSCU = 1.0 (neutral)')
ax.axhline(1.5, color='#E74C3C', linestyle=':', linewidth=0.8, alpha=0.7, label='RSCU = 1.5 (preferred threshold)')

ax.set_xticks(x_pos)
ax.set_xticklabels(codon_list, rotation=90, fontsize=7, fontfamily='monospace')
ax.set_ylabel('RSCU')
ax.set_ylim(0, 2.3)
ax.set_title('Figure 4. Relative Synonymous Codon Usage (RSCU) of 78 Protein-Coding Genes\nin Kaempferia galanga Chloroplast Genome (KS = KB; n = 22,645 codons)')

# AA legend
patches = [mpatches.Patch(color=aa_color[aa], label=aa) for aa in unique_aas]
ax.legend(handles=patches, ncol=5, frameon=False, fontsize=8,
          loc='upper right', title='Amino acid', title_fontsize=8)
ax.yaxis.grid(True, linestyle='--', linewidth=0.4, alpha=0.5)
ax.set_axisbelow(True)

# Shade alternating amino acid blocks
prev_aa = None
block_start = 0
shade = False
for i, aa in enumerate(aa_list):
    if aa != prev_aa:
        if prev_aa is not None and shade:
            ax.axvspan(block_start - 0.5, i - 0.5, color='#f0f0f0', zorder=0)
        shade = not shade
        block_start = i
        prev_aa = aa
if shade:
    ax.axvspan(block_start - 0.5, len(aa_list) - 0.5, color='#f0f0f0', zorder=0)

fig.tight_layout()
fig.savefig(OUT + 'Fig4_RSCU_All_Codons.png')
plt.close(fig)
print("Fig4 done")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 5 – Sequence Variant Summary (KS/KB vs Reference)
# ══════════════════════════════════════════════════════════════════════════════
# Variant breakdown from Variant_List and analysis report
variant_types  = ['SNP', 'Insertion', 'Deletion']
coding_counts  = [6, 0, 0]
noncoding_counts = [16, 9, 8]
totals = [c + n for c, n in zip(coding_counts, noncoding_counts)]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

# --- Panel A: stacked bar ---
x = np.arange(len(variant_types))
w = 0.45
b_nc = ax1.bar(x, noncoding_counts, w, label='Non-coding region', color='#5B8DB8', edgecolor='white')
b_c  = ax1.bar(x, coding_counts, w, bottom=noncoding_counts, label='Coding sequence (CDS)', color='#E07B54', edgecolor='white')

for i, (nc, c, tot) in enumerate(zip(noncoding_counts, coding_counts, totals)):
    ax1.text(i, tot + 0.3, str(tot), ha='center', va='bottom', fontsize=10, fontweight='bold')

ax1.set_xticks(x)
ax1.set_xticklabels(variant_types)
ax1.set_ylabel('Number of variants')
ax1.set_title('(A) Variants by Type and Genomic Location')
ax1.legend(frameon=False, fontsize=9)
ax1.yaxis.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
ax1.set_axisbelow(True)
ax1.set_ylim(0, 30)

# --- Panel B: pie for total variant type proportions ---
pie_vals   = [22, 9, 8]
pie_labels = ['SNPs\n(22)', 'Insertions\n(9; 68 bp total)', 'Deletions\n(8; 80 bp total)']
pie_cols   = ['#5B8DB8', '#2ECC71', '#E07B54']
wedges, texts, autotexts = ax2.pie(
    pie_vals, labels=pie_labels, autopct='%1.0f%%',
    colors=pie_cols, startangle=90,
    wedgeprops=dict(edgecolor='white', linewidth=2),
    pctdistance=0.6,
)
for t in autotexts:
    t.set_fontsize(9)
    t.set_color('white')
    t.set_fontweight('bold')
for t in texts:
    t.set_fontsize(9)
ax2.set_title('(B) Proportion of Variant Types\n(39 events total)')

fig.suptitle('Figure 5. Sequence Variants Between KS/KB Kaempferia galanga\nand Published Reference Genome (NC_040851.1; 99.87% identity)',
             fontsize=11, fontweight='bold')
fig.tight_layout()
fig.savefig(OUT + 'Fig5_Variant_Summary.png')
plt.close(fig)
print("Fig5 done")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 6 – RSCU A/T-ending vs G/C-ending codon bias summary
# ══════════════════════════════════════════════════════════════════════════════
# Aggregate: count codons ending in A or U vs G or C
au_codons = [(r[1], r[2], r[3]) for r in rscu_unique if r[1][-1] in ('A','U')]
gc_codons = [(r[1], r[2], r[3]) for r in rscu_unique if r[1][-1] in ('G','C')]

au_total = sum(c[1] for c in au_codons)
gc_total = sum(c[1] for c in gc_codons)

au_mean_rscu = np.mean([c[2] for c in au_codons])
gc_mean_rscu = np.mean([c[2] for c in gc_codons])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

# Panel A: codon count
cats = ['A/U-ending', 'G/C-ending']
counts = [au_total, gc_total]
pct = [au_total/(au_total+gc_total)*100, gc_total/(au_total+gc_total)*100]
cols = ['#2E86AB', '#A23B72']
bars = ax1.bar(cats, counts, color=cols, width=0.45, edgecolor='white')
for bar, n, p in zip(bars, counts, pct):
    ax1.text(bar.get_x()+bar.get_width()/2, n+120, f'{n:,}\n({p:.1f}%)',
             ha='center', va='bottom', fontsize=9, fontweight='bold')
ax1.set_ylabel('Total codon count')
ax1.set_title('(A) Total Usage by 3rd-Position\nNucleotide Type')
ax1.set_ylim(0, max(counts)*1.2)
ax1.yaxis.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
ax1.set_axisbelow(True)

# Panel B: mean RSCU
mean_rscus = [au_mean_rscu, gc_mean_rscu]
bars2 = ax2.bar(cats, mean_rscus, color=cols, width=0.45, edgecolor='white')
for bar, v in zip(bars2, mean_rscus):
    ax2.text(bar.get_x()+bar.get_width()/2, v+0.01, f'{v:.2f}',
             ha='center', va='bottom', fontsize=10, fontweight='bold')
ax2.axhline(1.0, color='black', linestyle='--', linewidth=0.9, label='RSCU = 1.0')
ax2.set_ylabel('Mean RSCU')
ax2.set_title('(B) Mean RSCU by 3rd-Position\nNucleotide Type')
ax2.set_ylim(0, 1.5)
ax2.legend(frameon=False, fontsize=9)
ax2.yaxis.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
ax2.set_axisbelow(True)

fig.suptitle('Figure 6. AT/GC Codon Usage Bias in Kaempferia galanga\nChloroplast Protein-Coding Genes (KS = KB; 78 genes)',
             fontsize=11, fontweight='bold')
fig.tight_layout()
fig.savefig(OUT + 'Fig6_AT_GC_Codon_Bias.png')
plt.close(fig)
print("Fig6 done")

print("\nAll charts saved to:", OUT)
