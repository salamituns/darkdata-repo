"""
Phase 4: Southeast Kansas close-up: the Cherokee Group CBM play.

The second figure for the launch post. Zooms into the eleven-county region
where the 2000s coalbed-methane boom drove the most concentrated LAS-filing
event in Kansas history: and where the regional log archive is dominated by
a single operator (River Rock, successor to Quest Cherokee).

Output:
  figures/kansas_cherokee_closeup.png
"""
import warnings; warnings.filterwarnings('ignore')
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

ROOT = '/Users/olatunde/CoWorker/Geoworks'
PROC = f'{ROOT}/darkdata-repo/data/processed'
COUNTIES = f'{ROOT}/data/raw/census_boundaries/gz_2010_us_050_00_5m.json'
OUT = f'{ROOT}/darkdata-repo/figures/kansas_cherokee_closeup.png'

# Editorial palette (same as hero)
PAPER   = '#F6F3EB'
INK     = '#0E0E0E'
CLAY    = '#A23B2A'
AMBER   = '#C57B35'
VIOLET  = '#6B4E8A'
MUTED   = '#7A7368'
FAINT   = '#EDE6D4'
GHOST   = '#B5AEA0'

HANDLE  = '@salamituns'

# ---- Region definition ---------------------------------------------------
CHEROKEE_COUNTIES = ['Cherokee', 'Crawford', 'Labette', 'Montgomery', 'Neosho',
                     'Wilson', 'Allen', 'Bourbon', 'Woodson', 'Chautauqua', 'Elk']

# Bounding box (a little padded beyond the 11 counties for breathing room)
WEST, EAST = -96.05, -94.55
SOUTH, NORTH = 36.93, 38.15

# ---- Load wells ----------------------------------------------------------
df = pd.read_csv(f'{PROC}/phase2_kgs_master_with_las.csv', low_memory=False)
df = df[~df['is_paper']].copy()
sub = df[df['County'].isin(CHEROKEE_COUNTIES)].copy()
sub = sub[sub['latitude'].between(SOUTH, NORTH)
          & sub['longitude'].between(WEST, EAST)]

def vintage_bucket(y):
    if pd.isna(y): return 'unknown'
    if y < 2000: return 'pre_2000'
    if y < 2010: return 'decade_2000'
    return 'decade_2010_plus'
sub['vintage_bucket'] = sub['spud_year'].apply(vintage_bucket)

lit = sub[sub['has_las']]
dark = sub[~sub['has_las']]

n_total = len(sub); n_lit = len(lit)
pct_lit = 100 * n_lit / n_total
top_op = lit['Current Operator'].value_counts().head(1)
top_op_name = top_op.index[0] if len(top_op) else 'n/a'
top_op_count = int(top_op.iloc[0]) if len(top_op) else 0
top_op_pct = 100 * top_op_count / n_lit if n_lit else 0

print(f'Cherokee region wells: {n_total:,}  with LAS: {n_lit:,}  ({pct_lit:.1f}%)')
print(f'Top operator: {top_op_name}  {top_op_count:,} LAS wells  ({top_op_pct:.0f}% of regional LAS)')

# ---- Render --------------------------------------------------------------
fig = plt.figure(figsize=(13, 8.5), dpi=300, facecolor=PAPER)
ax = fig.add_axes([0.04, 0.17, 0.92, 0.68])
ax.set_facecolor(PAPER)

# Counties (highlight Cherokee-region counties, fade the rest)
counties = gpd.read_file(COUNTIES, encoding='latin-1')
ks_counties = counties[counties['STATE'] == '20'].copy()
ks_counties['in_region'] = ks_counties['NAME'].isin(CHEROKEE_COUNTIES)
# Non-region counties: very faint
ks_counties[~ks_counties['in_region']].plot(ax=ax, facecolor=FAINT, edgecolor=INK,
                                            linewidth=0.25, alpha=0.45, zorder=1)
# Region counties: crisper
ks_counties[ks_counties['in_region']].plot(ax=ax, facecolor=PAPER, edgecolor=INK,
                                           linewidth=0.7, zorder=2)

# Well layers
ax.scatter(dark['longitude'], dark['latitude'],
           s=2.5, c=GHOST, alpha=0.35, linewidth=0, zorder=3, marker='o',
           rasterized=True)
VBUCKETS = [
    ('pre_2000',         AMBER),
    ('decade_2000',      CLAY),
    ('decade_2010_plus', VIOLET),
]
for key, color in VBUCKETS:
    pts = lit[lit['vintage_bucket'] == key]
    ax.scatter(pts['longitude'], pts['latitude'],
               s=9, c=color, alpha=0.90, linewidth=0, zorder=4,
               rasterized=True)

# County name labels at centroids, with a paper-colored halo so they
# read over the dense well clusters
rep = ks_counties[ks_counties['in_region']].copy()
rep['centroid'] = rep.geometry.representative_point()
for _, row in rep.iterrows():
    c = row['centroid']
    ax.text(c.x, c.y, row['NAME'].upper(),
            fontsize=9.5, color=INK, fontweight='bold',
            fontfamily='sans-serif', ha='center', va='center',
            alpha=0.88, zorder=7,
            path_effects=[pe.withStroke(linewidth=2.6, foreground=PAPER)])

# Cherokee Group play label (subtle, faint italic: placed in a thin well-free band)
ax.text(-95.3, 38.05, 'CHEROKEE GROUP PLAY',
        fontsize=11, color=INK, alpha=0.55, fontfamily='serif',
        fontstyle='italic', ha='center', va='center', zorder=6,
        path_effects=[pe.withStroke(linewidth=2.0, foreground=PAPER)])

# Extent + cosmetic
ax.set_xlim(WEST, EAST); ax.set_ylim(SOUTH, NORTH)
ax.set_aspect(1.25)
ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values(): sp.set_visible(False)

# ---- Title block ---------------------------------------------------------
fig.text(0.04, 0.945,
         'A closer look: Southeast Kansas and the Cherokee Group play.',
         fontsize=19, color=INK, fontfamily='serif', fontweight='medium')
fig.text(0.04, 0.905,
         f'The 11-county region that drove Kansas\u2019s 2000s coalbed-methane boom. '
         f'{n_total:,} drilled wells; {n_lit:,} with a publicly-accessible LAS ({pct_lit:.1f}%).',
         fontsize=10.5, color=MUTED, fontfamily='sans-serif')

# ---- Legend + operator callout ------------------------------------------
legend_handles = [
    Line2D([0],[0], marker='o', color='w', markerfacecolor=GHOST, alpha=0.7,
           markersize=7, markeredgecolor='none', label=f'No public LAS  ({len(dark):,})'),
    Line2D([0],[0], marker='o', color='w', markerfacecolor=AMBER,
           markersize=8, markeredgecolor='none',
           label=f'LAS, spud < 2000  ({(lit["vintage_bucket"]=="pre_2000").sum():,})'),
    Line2D([0],[0], marker='o', color='w', markerfacecolor=CLAY,
           markersize=8, markeredgecolor='none',
           label=f'LAS, spud 2000s  ({(lit["vintage_bucket"]=="decade_2000").sum():,})'),
    Line2D([0],[0], marker='o', color='w', markerfacecolor=VIOLET,
           markersize=8, markeredgecolor='none',
           label=f'LAS, spud 2010+  ({(lit["vintage_bucket"]=="decade_2010_plus").sum():,})'),
]
leg = fig.legend(handles=legend_handles, loc='lower left', frameon=False,
                 fontsize=9.5, labelcolor=INK, bbox_to_anchor=(0.04, 0.03),
                 ncol=4, columnspacing=1.6, handletextpad=0.6)
for t in leg.get_texts():
    t.set_fontfamily('sans-serif')

# Operator dominance callout (right side)
fig.text(0.62, 0.145,
         f'One operator, {top_op_pct:.0f}% of the regional log archive.',
         fontsize=10.5, color=INK, fontfamily='sans-serif',
         fontweight='bold', ha='left')
fig.text(0.62, 0.095,
         f'{top_op_name} holds {top_op_count:,} of the region\u2019s {n_lit:,} public LAS files.\n'
         f'Successor to the Quest Cherokee CBM estate.',
         fontsize=9, color=MUTED, fontfamily='sans-serif', ha='left',
         linespacing=1.5)

# ---- Footnote ------------------------------------------------------------
fig.text(0.04, 0.005,
         'Sources: Kansas Geological Survey master well list; KGS WebDocs LAS archive. '
         'Region: Allen, Bourbon, Chautauqua, Cherokee, Crawford, Elk, Labette, Montgomery, '
         'Neosho, Wilson, Woodson counties. Coordinates: NAD27.   '
         f'Analysis: {HANDLE}',
         fontsize=7, color=MUTED, fontfamily='sans-serif')

plt.savefig(OUT, facecolor=PAPER, dpi=300, bbox_inches='tight')
print(f'\nwrote {OUT}')
