"""
Phase 6: County choropleth: LAS coverage per Kansas county.

The east-to-west gradient told briefly on the hero map, now resolved at the
county scale. Each county shaded by its LAS coverage rate; the 10 darkest
(lowest coverage, with >=500 wells) called out in a side table for scale.

Output:
  figures/kansas_county_choropleth.png
"""
import warnings; warnings.filterwarnings('ignore')
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.cm import ScalarMappable

ROOT = '/Users/olatunde/CoWorker/Geoworks'
PROC = f'{ROOT}/darkdata-repo/data/processed'
COUNTIES = f'{ROOT}/data/raw/census_boundaries/gz_2010_us_050_00_5m.json'
OUT = f'{ROOT}/darkdata-repo/figures/kansas_county_choropleth.png'

PAPER   = '#F6F3EB'
INK     = '#0E0E0E'
CLAY    = '#A23B2A'
AMBER   = '#C57B35'
VIOLET  = '#6B4E8A'
MUTED   = '#7A7368'
FAINT   = '#EDE6D4'
GHOST   = '#B5AEA0'

HANDLE  = '@salamituns'

# ---- Data ----------------------------------------------------------------
df = pd.read_csv(f'{PROC}/phase2_kgs_master_with_las.csv', low_memory=False)
df = df[~df['is_paper']].copy()

county = (df.groupby('County')
            .agg(total=('api_key','size'), lit=('has_las','sum'))
            .assign(pct_lit=lambda d: 100*d['lit']/d['total'])
            .reset_index())
county = county[county['County'].astype(bool) & (county['County'].str.lower() != 'nan')]

# County polygons (Kansas FIPS = 20)
counties = gpd.read_file(COUNTIES, encoding='latin-1')
ks = counties[counties['STATE'] == '20'].copy()
ks['NAME_U'] = ks['NAME'].str.upper().str.strip()
county['KEY'] = county['County'].str.upper().str.strip()
ks = ks.merge(county[['KEY','total','lit','pct_lit']],
              left_on='NAME_U', right_on='KEY', how='left')
ks['total'] = ks['total'].fillna(0); ks['lit'] = ks['lit'].fillna(0); ks['pct_lit'] = ks['pct_lit'].fillna(0)

# ---- Figure --------------------------------------------------------------
fig = plt.figure(figsize=(14, 8.8), dpi=300, facecolor=PAPER)

ax = fig.add_axes([0.03, 0.12, 0.62, 0.72])
ax.set_facecolor(PAPER)

# Custom gradient: clay (dark = low coverage) → amber → violet (lit = high)
cmap = LinearSegmentedColormap.from_list(
    'darkdata', [CLAY, '#C99276', AMBER, '#9A8AA8', VIOLET], N=256)
vmax = 45  # clip so the one outlier (Wichita 43%) doesn't flatten the rest
norm = plt.Normalize(vmin=0, vmax=vmax)

# Counties with no drilled wells: ghost shade
no_data = ks[ks['total'] == 0]
has_data = ks[ks['total'] > 0]
if len(no_data):
    no_data.plot(ax=ax, facecolor=FAINT, edgecolor=INK, linewidth=0.3, alpha=0.7, zorder=1)
has_data.plot(ax=ax, column='pct_lit', cmap=cmap, vmin=0, vmax=vmax,
              edgecolor=INK, linewidth=0.35, zorder=2)

# Label the 3 darkest big counties and 2 lightest
top = county.query('total >= 500').sort_values('pct_lit')
callout_counties = list(top.head(4)['County']) + list(top.tail(3).sort_values('pct_lit', ascending=False)['County'])
for _, row in ks.iterrows():
    if row.get('NAME') not in callout_counties: continue
    c = row.geometry.representative_point()
    ax.text(c.x, c.y, row['NAME'].upper(),
            fontsize=7.5, color=INK, fontfamily='sans-serif',
            ha='center', va='center', fontweight='medium', zorder=8,
            path_effects=[pe.withStroke(linewidth=2.2, foreground=PAPER)])

ax.set_xlim(ks.total_bounds[0] - 0.1, ks.total_bounds[2] + 0.1)
ax.set_ylim(ks.total_bounds[1] - 0.1, ks.total_bounds[3] + 0.1)
ax.set_aspect(1.25)
ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values(): sp.set_visible(False)

# Colorbar underneath
cax = fig.add_axes([0.08, 0.09, 0.50, 0.015])
sm = ScalarMappable(cmap=cmap, norm=norm); sm.set_array([])
cb = fig.colorbar(sm, cax=cax, orientation='horizontal')
cb.set_ticks([0, 10, 20, 30, 40, 45])
cb.set_ticklabels(['0%', '10%', '20%', '30%', '40%', '45%+'])
cb.ax.tick_params(labelsize=8, colors=MUTED, length=0)
cb.outline.set_visible(False)
cax.set_title('% of drilled wells with a publicly-accessible LAS file',
              fontsize=8.5, color=MUTED, fontfamily='sans-serif', pad=6, loc='left')

# ---- Right panel: bottom / top tables -----------------------------------
ax_r = fig.add_axes([0.68, 0.12, 0.30, 0.72])
ax_r.set_facecolor(PAPER)
ax_r.set_xticks([]); ax_r.set_yticks([])
for sp in ax_r.spines.values(): sp.set_visible(False)

# Headline callout
n_below_5 = (county.query('total >= 50')['pct_lit'] < 5).sum()
ax_r.text(0.0, 0.98, 'The darkest counties are the oldest.',
          transform=ax_r.transAxes,
          fontsize=12, color=INK, fontfamily='serif',
          fontweight='medium', ha='left', va='top')
ax_r.text(0.0, 0.92,
          f'{n_below_5} of 98 counties with 50+ wells sit below 5% LAS coverage.',
          transform=ax_r.transAxes,
          fontsize=9, color=MUTED, fontfamily='sans-serif',
          ha='left', va='top', linespacing=1.5)

# Bottom 8 table
bottom = county.query('total >= 500').sort_values('pct_lit').head(8).reset_index(drop=True)
ax_r.text(0.0, 0.82, 'Bottom 8 counties by coverage', transform=ax_r.transAxes,
          fontsize=9.5, color=INK, fontweight='medium', fontfamily='sans-serif',
          ha='left', va='top')
ax_r.text(0.0, 0.795, '(500+ drilled wells)', transform=ax_r.transAxes,
          fontsize=8, color=MUTED, fontfamily='sans-serif', ha='left', va='top')
y0 = 0.76; dy = 0.036
for i, row in bottom.iterrows():
    yy = y0 - i*dy
    ax_r.text(0.00, yy, row['County'], transform=ax_r.transAxes,
              fontsize=9, color=INK, fontfamily='sans-serif', ha='left', va='top')
    ax_r.text(0.55, yy, f"{int(row['total']):,}", transform=ax_r.transAxes,
              fontsize=8.5, color=MUTED, fontfamily='sans-serif', ha='right', va='top')
    ax_r.text(0.95, yy, f"{row['pct_lit']:.1f}%", transform=ax_r.transAxes,
              fontsize=9, color=CLAY, fontfamily='sans-serif',
              fontweight='medium', ha='right', va='top')

# Top 5 table
top5 = county.query('total >= 500').sort_values('pct_lit', ascending=False).head(5).reset_index(drop=True)
y_top_header = y0 - 8*dy - 0.04
ax_r.text(0.0, y_top_header, 'Top 5 counties by coverage', transform=ax_r.transAxes,
          fontsize=9.5, color=INK, fontweight='medium', fontfamily='sans-serif',
          ha='left', va='top')
ax_r.text(0.0, y_top_header - 0.025, '(500+ drilled wells)',
          transform=ax_r.transAxes,
          fontsize=8, color=MUTED, fontfamily='sans-serif', ha='left', va='top')
y0b = y_top_header - 0.055
for i, row in top5.iterrows():
    yy = y0b - i*dy
    ax_r.text(0.00, yy, row['County'], transform=ax_r.transAxes,
              fontsize=9, color=INK, fontfamily='sans-serif', ha='left', va='top')
    ax_r.text(0.55, yy, f"{int(row['total']):,}", transform=ax_r.transAxes,
              fontsize=8.5, color=MUTED, fontfamily='sans-serif', ha='right', va='top')
    ax_r.text(0.95, yy, f"{row['pct_lit']:.1f}%", transform=ax_r.transAxes,
              fontsize=9, color=VIOLET, fontfamily='sans-serif',
              fontweight='medium', ha='right', va='top')

# Reader note on column header
ax_r.text(0.55, 0.785, 'wells', transform=ax_r.transAxes,
          fontsize=7, color=MUTED, fontstyle='italic', ha='right', va='top',
          fontfamily='sans-serif')
ax_r.text(0.95, 0.785, '% lit', transform=ax_r.transAxes,
          fontsize=7, color=MUTED, fontstyle='italic', ha='right', va='top',
          fontfamily='sans-serif')

# ---- Title block --------------------------------------------------------
fig.text(0.03, 0.95, 'The east-west divide at county resolution.',
         fontsize=20, color=INK, fontfamily='serif', fontweight='medium')
fig.text(0.03, 0.915,
         'Kansas counties shaded by LAS coverage. Eastern counties: the old oil patch: are mostly dark. '
         'Western counties, drilled after digital was the default, are the state\u2019s only bright spots.',
         fontsize=10, color=MUTED, fontfamily='sans-serif')

# ---- Footnote -----------------------------------------------------------
fig.text(0.03, 0.015,
         'Source: Kansas Geological Survey master well list (419,777 drilled wells, paper/cancelled excluded) '
         'and KGS WebDocs LAS archive. County polygons: Census 2010 TIGER. '
         f'Coverage = LAS-available / drilled.   Analysis: {HANDLE}',
         fontsize=7, color=MUTED, fontfamily='sans-serif')

print(f'Bottom 8 counties with 500+ wells:')
print(bottom.to_string())
print(f'\nTop 5 counties with 500+ wells:')
print(top5.to_string())

plt.savefig(OUT, facecolor=PAPER, dpi=300, bbox_inches='tight')
print(f'\nwrote {OUT}')
