"""
Phase 3: the Kansas dark-data hero map.

One dot per drilled well. Grey = no public digitized log. Colored = public LAS,
shaded by spud decade (old→new). The eye should read:

  - Most of the state is grey.
  - Where colour shows up, it concentrates in the western third and in a few
    vintage-specific pockets: the "recent drilling where digital was standard"
    signature.

Output:
  figures/kansas_dark_data_map.png
"""
import warnings; warnings.filterwarnings('ignore')
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

ROOT = '/Users/olatunde/CoWorker/Geoworks'
PROC = f'{ROOT}/darkdata-repo/data/processed'
STATES = f'{ROOT}/data/raw/census_boundaries/gz_2010_us_040_00_5m.json'
COUNTIES = f'{ROOT}/data/raw/census_boundaries/gz_2010_us_050_00_5m.json'
OUT = f'{ROOT}/darkdata-repo/figures/kansas_dark_data_map.png'

# Editorial palette (matches GHGRP series)
PAPER   = '#F6F3EB'
INK     = '#0E0E0E'
CLAY    = '#A23B2A'
AMBER   = '#C57B35'
VIOLET  = '#6B4E8A'
MUTED   = '#7A7368'
FAINT   = '#EDE6D4'   # county fill
GHOST   = '#B5AEA0'   # dark-well grey

# Kansas extent
WEST, EAST = -102.2, -94.5
SOUTH, NORTH = 36.9, 40.1

# ---- Load wells ---------------------------------------------------------
df = pd.read_csv(f'{PROC}/phase2_kgs_master_with_las.csv', low_memory=False)
df = df[~df['is_paper']].copy()
df = df[df['latitude'].between(SOUTH, NORTH) & df['longitude'].between(WEST, EAST)]
print(f'drilled wells in Kansas bbox: {len(df):,}')
print(f'  with LAS: {df["has_las"].sum():,}')
print(f'  dark:     {(~df["has_las"]).sum():,}')

# Vintage buckets (only for LAS-available wells)
def vintage_bucket(y):
    if pd.isna(y): return 'unknown'
    if y < 2000: return 'pre_2000'
    if y < 2010: return 'decade_2000'
    return 'decade_2010_plus'
df['vintage_bucket'] = df['spud_year'].apply(vintage_bucket)

lit = df[df['has_las']]
dark = df[~df['has_las']]

VBUCKETS = [
    ('pre_2000',        AMBER,  'LAS, spud < 2000'),
    ('decade_2000',     CLAY,   'LAS, spud 2000s'),
    ('decade_2010_plus', VIOLET, 'LAS, spud 2010+'),
]

# ---- Render -------------------------------------------------------------
fig = plt.figure(figsize=(14, 10.6), dpi=300, facecolor=PAPER)
ax = fig.add_axes([0.02, 0.38, 0.96, 0.52])    # main map, top band
ax.set_facecolor(PAPER)

# Counties (Kansas subset): faint fill + lines
counties = gpd.read_file(COUNTIES, encoding='latin-1')
ks_counties = counties[counties['STATE'] == '20']
ks_counties.plot(ax=ax, color=FAINT, edgecolor=INK, linewidth=0.25, alpha=0.8, zorder=1)

# State outline (heavier)
states = gpd.read_file(STATES)
ks_state = states[states['NAME'] == 'Kansas']
ks_state.plot(ax=ax, facecolor='none', edgecolor=INK, linewidth=1.2, zorder=2)

# Dark wells first (bottom)
ax.scatter(dark['longitude'], dark['latitude'],
           s=1.2, c=GHOST, alpha=0.22, linewidth=0, zorder=3, marker='o',
           rasterized=True)

# LAS wells by vintage bucket (top)
for key, color, _label in VBUCKETS:
    sub = lit[lit['vintage_bucket'] == key]
    ax.scatter(sub['longitude'], sub['latitude'],
               s=4.5, c=color, alpha=0.85, linewidth=0, zorder=4, marker='o',
               rasterized=True)

# ---- Orientation: US locator inset + city + basin anchors ----
# US locator inset (NE of map: the least-populated well corner, safe)
ax_us = fig.add_axes([0.835, 0.80, 0.13, 0.08])
ax_us.set_facecolor(PAPER)
conus = states[~states['NAME'].isin(['Alaska', 'Hawaii', 'Puerto Rico', 'District of Columbia'])]
conus.plot(ax=ax_us, facecolor=FAINT, edgecolor=INK, linewidth=0.25, alpha=0.9)
ks_state.plot(ax=ax_us, facecolor=CLAY, edgecolor=INK, linewidth=0.35)
ax_us.set_xticks([]); ax_us.set_yticks([])
for sp in ax_us.spines.values(): sp.set_visible(False)
ax_us.text(0.5, -0.18, 'K A N S A S', transform=ax_us.transAxes,
           ha='center', va='top', fontsize=7.5, color=INK,
           fontfamily='sans-serif', fontweight='bold')

# State name overlay (upper-left of map)
ax.text(WEST + 0.25, NORTH - 0.30, 'KANSAS',
        fontsize=13, color=INK, fontfamily='sans-serif', fontweight='bold',
        alpha=0.45, zorder=9)

# City anchors (picked to sit in low-density areas)
cities = [
    ('Wichita',     -97.34, 37.69, 'lr'),   # south-central
    ('Topeka',      -95.68, 39.05, 'ur'),   # NE-ish
    ('Dodge City',  -100.02, 37.75, 'ur'),  # SW
    ('Hays',         -99.33, 38.87, 'ur'),  # west-central
    ('Garden City',  -100.87, 37.97, 'll'),
]
for name, lon, lat, pos in cities:
    ax.scatter([lon], [lat], s=28, facecolor=PAPER,
               edgecolor=INK, lw=0.9, zorder=8, marker='s')
    dx, dy, ha = 0.13, 0.10, 'left'
    if pos == 'ur':    dx, dy, ha =  0.13, 0.12, 'left'
    elif pos == 'll':  dx, dy, ha = -0.13, -0.12, 'right'
    elif pos == 'lr':  dx, dy, ha =  0.13, -0.18, 'left'
    ax.text(lon + dx, lat + dy, name, fontsize=8.8, color=INK,
            fontfamily='sans-serif', fontweight='medium',
            ha=ha, va='center', zorder=9,
            path_effects=[])

# Basin / play name labels (italic, muted: sit over well clusters)
basin_labels = [
    ('Hugoton\nEmbayment',  -101.0, 37.25),
    ('Cherokee\nBasin',      -95.5, 37.35),
    ('Central Kansas\nUplift', -98.5, 38.7),
]
for label, lon, lat in basin_labels:
    ax.text(lon, lat, label, fontsize=8.5, color=INK, alpha=0.55,
            fontfamily='serif', fontstyle='italic', ha='center', va='center',
            zorder=7)

# Extent + cosmetic
ax.set_xlim(WEST, EAST); ax.set_ylim(SOUTH, NORTH)
ax.set_aspect(1.25)
ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values(): sp.set_visible(False)

# ---- Title block --------------------------------------------------------
fig.text(0.035, 0.955,
         'Where Kansas oil data lives.',
         fontsize=22, color=INK, fontfamily='serif', fontweight='medium')
n_drilled = len(df); n_lit = df['has_las'].sum()
pct_dark = 100 * (1 - n_lit / n_drilled)
fig.text(0.035, 0.918,
         f'{n_drilled:,} drilled wells on the Kansas Geological Survey master list. '
         f'Only {n_lit:,} have a publicly-accessible digitized log. '
         f'{pct_dark:.1f}% of the state\u2019s drilling history is dark.',
         fontsize=11, color=MUTED, fontfamily='sans-serif')

# ---- Legend -------------------------------------------------------------
legend_handles = [
    Line2D([0],[0], marker='o', color='w', markerfacecolor=GHOST,
           markeredgecolor='none', alpha=0.7, markersize=7,
           label=f'No public LAS  ({len(dark):,})'),
]
for key, color, label in VBUCKETS:
    n = (lit['vintage_bucket'] == key).sum()
    legend_handles.append(
        Line2D([0],[0], marker='o', color='w', markerfacecolor=color,
               markeredgecolor='none', markersize=8,
               label=f'{label}  ({n:,})')
    )
leg = fig.legend(handles=legend_handles, loc='lower left', frameon=False,
                 fontsize=10, labelcolor=INK, bbox_to_anchor=(0.05, 0.10),
                 ncol=1, handletextpad=0.6)
for t in leg.get_texts():
    t.set_fontfamily('sans-serif')
fig.text(0.05, 0.32, 'Legend', fontsize=9.5, color=INK,
         fontfamily='sans-serif', fontweight='bold')

# ---- Companion panel: vintage curve -------------------------------------
# Per-decade: share of drilled wells with a public LAS.
# Bar colours match the main map vintage buckets (pre-2000, 2000s, 2010+).
ax_inset = fig.add_axes([0.42, 0.10, 0.52, 0.20])
ax_inset.set_facecolor(PAPER)

decade_df = (df[df['spud_year'].notna()]
             .assign(decade=lambda d: (d['spud_year'] // 10 * 10).astype(int))
             .groupby('decade')
             .agg(total=('api_key', 'size'), with_las=('has_las', 'sum'))
             .reset_index())
decade_df = decade_df[decade_df['decade'] >= 1920].copy()
decade_df['pct'] = 100 * decade_df['with_las'] / decade_df['total']

def bar_color(d):
    if d < 2000:  return AMBER
    if d < 2010:  return CLAY
    return VIOLET

xs = [f"{int(d)}s" for d in decade_df['decade']]
colors = [bar_color(d) for d in decade_df['decade']]

ax_inset.bar(xs, decade_df['pct'], color=colors, edgecolor='none',
             width=0.78, zorder=3)
# faint baseline ticks at 10/20/30%
for y in [10, 20, 30]:
    ax_inset.axhline(y, color=INK, lw=0.3, alpha=0.15, zorder=1)

# Label the 2010s bar with its share
r2010 = decade_df[decade_df['decade'] == 2010].iloc[0]
x_idx = xs.index('2010s')
ax_inset.text(x_idx, r2010['pct'] + 1.5,
              f"{r2010['pct']:.1f}%", ha='center', va='bottom',
              fontsize=8.5, color=VIOLET, fontweight='bold', fontfamily='sans-serif')

# Cosmetic
ax_inset.set_ylim(0, 45)
ax_inset.set_yticks([0, 10, 20, 30, 40])
ax_inset.set_yticklabels(['0', '10%', '20%', '30%', '40%'],
                         fontsize=7.5, color=MUTED, fontfamily='sans-serif')
ax_inset.tick_params(axis='x', labelsize=7.5, colors=MUTED, pad=1)
for lbl in ax_inset.get_xticklabels():
    lbl.set_fontfamily('sans-serif')
for sp in ['top', 'right', 'left']:
    ax_inset.spines[sp].set_visible(False)
ax_inset.spines['bottom'].set_color(INK)
ax_inset.spines['bottom'].set_linewidth(0.5)

ax_inset.set_title('Share of drilled wells with a public LAS, by spud decade',
                   fontsize=9, color=INK, fontfamily='sans-serif',
                   loc='left', pad=6)
ax_inset.text(0, -0.26,
              'Dark data is a stratigraphy of time: pre-2000 coverage averages ~2%. '
              'The 2010s clear 37%: the first decade where digitized logs became the norm. '
              '2020s dips on reporting lag.',
              transform=ax_inset.transAxes, fontsize=8.5, color=MUTED,
              fontfamily='sans-serif', ha='left', va='top', wrap=True)

# ---- Footnote -----------------------------------------------------------
HANDLE = '@salamituns'
fig.text(0.035, 0.005,
         'Sources: Kansas Geological Survey master well list (515K records, deduped to 476,869 unique wells; '
         '419,777 after excluding paper/cancelled permits). LAS availability: KGS WebDocs LAS archive, deduped by well. '
         'Coordinates: NAD27. Spud-year parsed from KGS Spud Date field; 64.7% coverage.   '
         f'Analysis: {HANDLE}',
         fontsize=7, color=MUTED, fontfamily='sans-serif')

plt.savefig(OUT, facecolor=PAPER, dpi=300, bbox_inches='tight')
print(f'\nwrote {OUT}')
