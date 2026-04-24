"""
Phase 5: Who owns the Kansas dark universe?

Top 15 named operators, ranked by total drilled wells, with each bar split
into dark (no public LAS) and lit (has public LAS). A separate callout
panel carries the biggest single finding: 46% of the dark universe is
orphaned: no current operator at all.

Output:
  figures/kansas_operators_dark.png
"""
import warnings; warnings.filterwarnings('ignore')
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = '/Users/olatunde/CoWorker/Geoworks'
PROC = f'{ROOT}/darkdata-repo/data/processed'
OUT  = f'{ROOT}/darkdata-repo/figures/kansas_operators_dark.png'

PAPER = '#F6F3EB'
INK   = '#0E0E0E'
CLAY  = '#A23B2A'
AMBER = '#C57B35'
VIOLET = '#6B4E8A'
MUTED = '#7A7368'
GHOST = '#B5AEA0'

HANDLE = '@salamituns'

# ---- Data ----------------------------------------------------------------
df = pd.read_csv(f'{PROC}/phase2_kgs_master_with_las.csv', low_memory=False)
df = df[~df['is_paper']].copy()
df['Current Operator'] = df['Current Operator'].fillna('').astype(str).str.strip()

# Split: orphan (blank operator) vs named
orphan = df[df['Current Operator'] == '']
named  = df[df['Current Operator'] != '']

orphan_total = len(orphan)
orphan_dark = (~orphan['has_las']).sum()
all_dark = (~df['has_las']).sum()
orphan_share_of_dark = 100 * orphan_dark / all_dark

print(f'Orphan wells (no operator):      {orphan_total:,}')
print(f'Orphan dark wells:               {orphan_dark:,}  ({orphan_share_of_dark:.1f}% of all dark)')
print(f'All dark wells:                  {all_dark:,}')

# Top 15 named operators by total wells
op = (named.groupby('Current Operator')
         .agg(total=('api_key','size'), lit=('has_las','sum'))
         .assign(dark=lambda d: d['total']-d['lit'],
                 pct_lit=lambda d: 100*d['lit']/d['total'])
         .sort_values('total', ascending=False))
top = op.head(15).reset_index()
print(f"\nTop 15 named operators (by total drilled wells):")
print(top.to_string())

# Concentration stat (named only)
named_dark = named[~named['has_las']]
top10_dark = op.sort_values('dark', ascending=False).head(10)['dark'].sum()
concentration = 100 * top10_dark / named_dark.shape[0]
print(f"\nTop-10 named operators hold {top10_dark:,} dark wells = {concentration:.1f}% of NAMED dark wells")

# ---- Render --------------------------------------------------------------
fig = plt.figure(figsize=(14, 9.4), dpi=300, facecolor=PAPER)

# Main chart (left panel)
ax = fig.add_axes([0.06, 0.10, 0.62, 0.74])
ax.set_facecolor(PAPER)

top = top.iloc[::-1].reset_index(drop=True)  # reverse so #1 is at top
y = range(len(top))

ax.barh(y, top['dark'], color=GHOST, edgecolor='none', height=0.72, zorder=3,
        label='No public LAS')
ax.barh(y, top['lit'], left=top['dark'], color=CLAY, edgecolor='none',
        height=0.72, zorder=4, label='With public LAS')

# Operator names (as tick labels)
ax.set_yticks(list(y))
ax.set_yticklabels(top['Current Operator'].str.replace(', LLC','').str.replace(', Inc.','').str.replace(' Inc', ''),
                   fontsize=9.5, color=INK, fontfamily='sans-serif')

# Totals + %lit annotations at bar end
for i, row in top.iterrows():
    tot = int(row['total']); lit_pct = row['pct_lit']
    ax.text(tot + 90, i, f'{tot:,}', fontsize=9, color=INK,
            fontfamily='sans-serif', va='center', fontweight='medium')
    ax.text(tot + 860, i, f' {lit_pct:.0f}% lit', fontsize=8.5, color=MUTED,
            fontfamily='sans-serif', va='center', fontstyle='italic')

# Axes cosmetics
ax.set_xlim(0, top['total'].max() * 1.19)
ax.set_xticks([0, 2000, 4000, 6000])
ax.set_xticklabels(['0', '2,000', '4,000', '6,000'],
                   fontsize=8.5, color=MUTED, fontfamily='sans-serif')
ax.tick_params(axis='x', colors=MUTED)
ax.tick_params(axis='y', which='both', length=0)
for sp in ['top','right','left']: ax.spines[sp].set_visible(False)
ax.spines['bottom'].set_color(INK)
ax.spines['bottom'].set_linewidth(0.5)
ax.set_xlabel('Drilled wells  (stacked: no-LAS | with-LAS)',
              fontsize=9, color=MUTED, fontfamily='sans-serif', labelpad=8)

# ---- Right-side callout -------------------------------------------------
ax_right = fig.add_axes([0.70, 0.10, 0.28, 0.74])
ax_right.set_facecolor(PAPER)
ax_right.set_xticks([]); ax_right.set_yticks([])
for sp in ax_right.spines.values(): sp.set_visible(False)

# Big number
ax_right.text(0.0, 0.92, f'{orphan_share_of_dark:.0f}%',
              transform=ax_right.transAxes,
              fontsize=56, color=CLAY, fontfamily='serif', fontweight='medium',
              ha='left', va='top')

ax_right.text(0.0, 0.73, 'of the dark Kansas universe\nhas no current operator.',
              transform=ax_right.transAxes,
              fontsize=12.5, color=INK, fontfamily='sans-serif',
              ha='left', va='top', linespacing=1.3, fontweight='medium')

ax_right.text(0.0, 0.56,
              f'{orphan_dark:,} drilled wells in Kansas are both dark '
              f'and ownerless: orphan and plugged-and-abandoned wells whose '
              f'last operator no longer exists, or never registered a successor. '
              f'When a company exits, its wells go with it. Nobody left to digitize.',
              transform=ax_right.transAxes,
              fontsize=9.5, color=MUTED, fontfamily='sans-serif',
              ha='left', va='top', linespacing=1.55, wrap=True)

# Secondary stat
ax_right.text(0.0, 0.26,
              f'The remaining dark wells sit on a long tail.\n'
              f'The top 10 named operators hold {top10_dark:,} :\n'
              f'only {concentration:.0f}% of the named dark universe.',
              transform=ax_right.transAxes,
              fontsize=10, color=INK, fontfamily='sans-serif',
              ha='left', va='top', linespacing=1.45, fontweight='medium')

combined = orphan_share_of_dark + (100 * top10_dark / all_dark)
ax_right.text(0.0, 0.12,
              f'7,217 operators drilled in Kansas. Orphan wells plus the '
              f'ten largest named estates account for {combined:.0f}% of all dark wells.',
              transform=ax_right.transAxes,
              fontsize=9, color=MUTED, fontfamily='sans-serif',
              ha='left', va='top', linespacing=1.5)

# ---- Title block --------------------------------------------------------
fig.text(0.04, 0.945,
         'Who owns the Kansas dark universe?',
         fontsize=22, color=INK, fontfamily='serif', fontweight='medium')
fig.text(0.04, 0.905,
         'Top 15 named operators by drilled-well count, each bar split into dark (no public LAS) and lit (with LAS). '
         'The single largest holder of dark wells is nobody.',
         fontsize=10.5, color=MUTED, fontfamily='sans-serif')

# Legend (small, above chart)
legend_handles = [
    Line2D([0],[0], marker='s', color='w', markerfacecolor=GHOST,
           markeredgecolor='none', markersize=12, label='No public LAS'),
    Line2D([0],[0], marker='s', color='w', markerfacecolor=CLAY,
           markeredgecolor='none', markersize=12, label='With public LAS'),
]
leg = fig.legend(handles=legend_handles, loc='lower left', frameon=False,
                 fontsize=9.5, labelcolor=INK, bbox_to_anchor=(0.06, 0.86),
                 ncol=2, columnspacing=1.5, handletextpad=0.4)
for t in leg.get_texts():
    t.set_fontfamily('sans-serif')

# ---- Footnote -----------------------------------------------------------
fig.text(0.04, 0.015,
         'Source: Kansas Geological Survey master well list, 419,777 drilled wells (paper/cancelled excluded). '
         'Operator names: `Current Operator` field as published by KGS; blank where no current operator of record.   '
         f'Analysis: {HANDLE}',
         fontsize=7.5, color=MUTED, fontfamily='sans-serif')

plt.savefig(OUT, facecolor=PAPER, dpi=300, bbox_inches='tight')
print(f'\nwrote {OUT}')
