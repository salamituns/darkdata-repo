"""
Phase 3: Williston basin static figures.

Four hero figures, same editorial palette as Kansas + GHGRP. All carry
`Analysis: @salamituns` attribution per the figure-attribution rule.

Outputs (written to both repo/figures/ and salamituns.github.io/darkdata/williston/figures/):
  1. williston_basin_map.png         hero map: ND+MT wells inside TPS polygon
  2. williston_state_gradient.png    ND vs MT dark share split
  3. williston_vintage_split.png     vintage distribution with horizontal flag
  4. williston_operators.png         top-15 operators by well count + dark share
"""
import warnings; warnings.filterwarnings('ignore')
import json
from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path('/Users/olatunde/CoWorker/Geoworks')
DATA = ROOT / 'salamituns.github.io/darkdata/williston/data'
FIG_REPO = ROOT / 'darkdata-repo/figures'
FIG_SITE = ROOT / 'salamituns.github.io/darkdata/williston/figures'
STATES_SRC = ROOT / 'data/raw/census_boundaries/gz_2010_us_040_00_5m.json'

FIG_REPO.mkdir(parents=True, exist_ok=True)
FIG_SITE.mkdir(parents=True, exist_ok=True)

# ---- Editorial palette (matches Kansas + GHGRP) --------------------------
PAPER  = '#F6F3EB'
INK    = '#0E0E0E'
CLAY   = '#A23B2A'
AMBER  = '#C57B35'
VIOLET = '#6B4E8A'
TEAL   = '#2E6E7E'
MUTED  = '#7A7368'
FAINT  = '#EDE6D4'
GHOST  = '#B5AEA0'

HANDLE = '@salamituns'

# ---- Load data -----------------------------------------------------------
print('loading wells + basin...')
wells = pd.read_csv(DATA / 'wells.csv')
with open(DATA / 'williston_basin.json') as f:
    basin_gj = json.load(f)
with open(DATA / 'summary.json') as f:
    summary = json.load(f)

basin_geom = shape(basin_gj['features'][0]['geometry'])
basin_gdf = gpd.GeoDataFrame(geometry=[basin_geom], crs='EPSG:4269')
states = gpd.read_file(STATES_SRC)
nd_mt = states[states['NAME'].isin(['North Dakota', 'Montana'])]

# Vintage label map (schema shared with Kansas/Permian)
VINTAGE_LABELS = {
    0: 'pre-1980',
    1: '1980s',
    2: '1990s',
    3: '2000s',
    4: '2010+',
    5: 'unknown',
}
STATE_LABELS = {0: 'North Dakota', 1: 'Montana'}

print(f'wells={len(wells):,}  basin_bounds={basin_geom.bounds}')


# =========================================================================
# Figure 1: basin hero map
# =========================================================================
def fig1_basin_map():
    out = 'williston_basin_map.png'
    WEST, SOUTH, EAST, NORTH = basin_geom.bounds
    # expand a touch for context
    WEST -= 0.3; EAST += 0.3; SOUTH -= 0.2; NORTH += 0.25

    fig = plt.figure(figsize=(14, 10.6), dpi=220, facecolor=PAPER)
    ax = fig.add_axes([0.02, 0.30, 0.96, 0.60])
    ax.set_facecolor(PAPER)

    # State fills first
    nd_mt.plot(ax=ax, color=FAINT, edgecolor=INK, linewidth=0.35, zorder=1)
    # Basin polygon outline (the geological boundary)
    basin_gdf.plot(ax=ax, facecolor='none', edgecolor=INK,
                   linewidth=1.6, linestyle='-', zorder=2)

    # Dark wells first (bottom)
    dark = wells[wells['d'] == 1]
    lit = wells[wells['d'] == 0]
    ax.scatter(dark['lon'], dark['lat'], s=1.0, c=GHOST, alpha=0.30,
               linewidth=0, zorder=3, marker='o', rasterized=True)

    # Lit wells by vintage
    for v, color in [(3, AMBER), (4, VIOLET), (0, CLAY), (1, CLAY), (2, CLAY)]:
        sub = lit[lit['v'] == v]
        if len(sub) == 0:
            continue
        ax.scatter(sub['lon'], sub['lat'], s=3.5, c=color, alpha=0.75,
                   linewidth=0, zorder=4, marker='o', rasterized=True)

    # State label overlays
    ax.text(-103.5, 47.7, 'NORTH DAKOTA', fontsize=13, color=INK,
            fontfamily='sans-serif', fontweight='bold', alpha=0.45,
            ha='center', zorder=9)
    ax.text(-105.8, 47.2, 'MONTANA', fontsize=13, color=INK,
            fontfamily='sans-serif', fontweight='bold', alpha=0.45,
            ha='center', zorder=9)

    # US locator inset
    ax_us = fig.add_axes([0.83, 0.78, 0.14, 0.09])
    ax_us.set_facecolor(PAPER)
    conus = states[~states['NAME'].isin(
        ['Alaska', 'Hawaii', 'Puerto Rico', 'District of Columbia'])]
    conus.plot(ax=ax_us, facecolor=FAINT, edgecolor=INK,
               linewidth=0.25, alpha=0.9)
    nd_mt.plot(ax=ax_us, facecolor=CLAY, edgecolor=INK, linewidth=0.35)
    basin_gdf.plot(ax=ax_us, facecolor='none', edgecolor=INK, linewidth=0.6)
    ax_us.set_xticks([]); ax_us.set_yticks([])
    for sp in ax_us.spines.values(): sp.set_visible(False)
    ax_us.text(0.5, -0.18, 'WILLISTON BASIN', transform=ax_us.transAxes,
               ha='center', va='top', fontsize=7.5, color=INK,
               fontfamily='sans-serif', fontweight='bold')

    # City anchors
    cities = [
        ('Williston',  -103.62, 48.15),
        ('Dickinson',  -102.79, 46.88),
        ('Minot',       -101.30, 48.23),
        ('Bismarck',    -100.78, 46.81),
        ('Sidney MT',   -104.16, 47.71),
        ('Glendive MT', -104.71, 47.11),
    ]
    for name, lon, lat in cities:
        ax.scatter([lon], [lat], s=28, facecolor=PAPER,
                   edgecolor=INK, lw=0.9, zorder=8, marker='s')
        ax.text(lon + 0.10, lat + 0.08, name, fontsize=8.8, color=INK,
                fontfamily='sans-serif', fontweight='medium',
                ha='left', va='bottom', zorder=9)

    # Play labels
    ax.text(-103.3, 47.5, 'Bakken Core\n(Parshall–Sanish)', fontsize=9,
            color=INK, alpha=0.55, fontfamily='serif', fontstyle='italic',
            ha='center', va='center', zorder=7)
    ax.text(-105.0, 47.7, 'Elm Coulee', fontsize=9, color=INK, alpha=0.55,
            fontfamily='serif', fontstyle='italic', ha='center', zorder=7)

    ax.set_xlim(WEST, EAST); ax.set_ylim(SOUTH, NORTH)
    ax.set_aspect(1.35)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)

    # Title block
    fig.text(0.035, 0.955,
             'The basin that geology drew, not a border.',
             fontsize=22, color=INK, fontfamily='serif', fontweight='medium')
    n_total = summary['total_wells']
    pct_dark = summary['pct_dark']
    fig.text(0.035, 0.918,
             f'{n_total:,} wells drilled inside the USGS Bakken–Three Forks '
             f'Total Petroleum System. {pct_dark}% of them have no public '
             'digitized log. The Bakken horizontal campaign is lit; the '
             'pre-2000 legacy is not.',
             fontsize=11, color=MUTED, fontfamily='sans-serif')

    # Legend
    handles = [
        Line2D([0],[0], marker='o', color='w', markerfacecolor=GHOST,
               markeredgecolor='none', alpha=0.7, markersize=7,
               label=f'Dark (no public log)  ({len(dark):,})'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor=VIOLET,
               markeredgecolor='none', markersize=8,
               label=f'Lit, spud 2010+  ({len(lit[lit["v"]==4]):,})'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor=AMBER,
               markeredgecolor='none', markersize=8,
               label=f'Lit, spud 2000s  ({len(lit[lit["v"]==3]):,})'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor=CLAY,
               markeredgecolor='none', markersize=8,
               label=f'Lit, spud pre-2000  ({len(lit[lit["v"].isin([0,1,2])]):,})'),
    ]
    leg = fig.legend(handles=handles, loc='lower left', frameon=False,
                     fontsize=10, labelcolor=INK,
                     bbox_to_anchor=(0.05, 0.05), ncol=1, handletextpad=0.6)
    for t in leg.get_texts(): t.set_fontfamily('sans-serif')
    fig.text(0.05, 0.27, 'Legend', fontsize=9.5, color=INK,
             fontfamily='sans-serif', fontweight='bold')

    # Companion inset: state-line dark share
    ax2 = fig.add_axes([0.52, 0.07, 0.42, 0.18])
    ax2.set_facecolor(PAPER)
    states_rows = ['North Dakota', 'Montana']
    colors = [AMBER, TEAL]
    by_state = summary['by_state']
    pcts = [by_state['ND']['pct_dark'], by_state['MT']['pct_dark']]
    totals = [by_state['ND']['total'], by_state['MT']['total']]
    bars = ax2.barh(states_rows, pcts, color=colors, edgecolor='none', zorder=3)
    for i, (bar, pct, n) in enumerate(zip(bars, pcts, totals)):
        ax2.text(pct + 1.5, i, f'{pct:.1f}%  ({n:,} wells)',
                 va='center', fontsize=9, color=INK,
                 fontfamily='sans-serif', fontweight='medium')
    ax2.set_xlim(0, 100)
    ax2.set_xticks([0, 25, 50, 75, 100])
    ax2.set_xticklabels(['0', '25%', '50%', '75%', '100%'],
                        fontsize=7.5, color=MUTED, fontfamily='sans-serif')
    ax2.tick_params(axis='y', labelsize=9.5, colors=INK, pad=1)
    for lbl in ax2.get_yticklabels(): lbl.set_fontfamily('sans-serif')
    for sp in ['top', 'right']: ax2.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax2.spines[sp].set_color(INK); ax2.spines[sp].set_linewidth(0.5)
    ax2.set_title('Dark-data share by state',
                  fontsize=9.5, color=INK, fontfamily='sans-serif',
                  loc='left', pad=6)
    ax2.text(0, -0.25,
             'Montana holds the pre-2000 Bakken legacy. North Dakota\u2019s 2008+ '
             'horizontal campaign was logged digitally from day one.',
             transform=ax2.transAxes, fontsize=8.5, color=MUTED,
             fontfamily='sans-serif', ha='left', va='top', wrap=True)

    # Footnote
    fig.text(0.035, 0.006,
             'Sources: NDIC Oil & Gas Division shapefile (OGD_Wells, 43,445 ND wells). '
             'MT BOGC WellSurface shapefile (41,943 MT wells). USGS ScienceBase item '
             '618e90c8: Bakken + Three Forks Assessment Unit boundaries (unioned to a '
             'single basin polygon). Wells spatial-joined in EPSG:5070, emitted in EPSG:4269.   '
             f'Analysis: {HANDLE}',
             fontsize=7, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


# =========================================================================
# Figure 2: state-line gradient (ND vs MT detailed split)
# =========================================================================
def fig2_state_gradient():
    out = 'williston_state_gradient.png'
    fig = plt.figure(figsize=(13, 8), dpi=220, facecolor=PAPER)

    # Title
    fig.text(0.04, 0.94,
             'The Bakken doesn\u2019t care about the state line.',
             fontsize=20, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.04, 0.895,
             'One petroleum system, two regulatory regimes, two different '
             'data legacies. The rock is the same. The record is not.',
             fontsize=11, color=MUTED, fontfamily='sans-serif')

    # Left panel: stacked bar of dark vs lit per state
    ax1 = fig.add_axes([0.07, 0.20, 0.36, 0.56])
    ax1.set_facecolor(PAPER)
    by_state = summary['by_state']
    states_ = ['ND', 'MT']
    dark_n = [by_state[s]['dark'] for s in states_]
    lit_n  = [by_state[s]['total'] - by_state[s]['dark'] for s in states_]
    totals = [by_state[s]['total'] for s in states_]
    ax1.bar(states_, lit_n, color=VIOLET, edgecolor='none',
            label='Lit (public digital log)', zorder=3)
    ax1.bar(states_, dark_n, bottom=lit_n, color=GHOST, edgecolor='none',
            label='Dark', zorder=3)
    for i, (s, t) in enumerate(zip(states_, totals)):
        ax1.text(i, t + totals[0] * 0.015, f'{t:,}',
                 ha='center', fontsize=10, color=INK, fontweight='bold',
                 fontfamily='sans-serif')
        pct = by_state[s]['pct_dark']
        ax1.text(i, lit_n[i] + dark_n[i] / 2, f'{pct:.1f}%\ndark',
                 ha='center', va='center', fontsize=11, color=INK,
                 fontweight='bold', fontfamily='sans-serif')
    ax1.set_ylabel('Wells', fontsize=9.5, color=MUTED,
                   fontfamily='sans-serif')
    ax1.set_xticklabels(['North Dakota', 'Montana'],
                        fontsize=11, color=INK, fontfamily='sans-serif')
    ax1.tick_params(axis='y', labelsize=8, colors=MUTED)
    for sp in ['top', 'right']: ax1.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax1.spines[sp].set_color(INK); ax1.spines[sp].set_linewidth(0.5)
    ax1.legend(loc='upper right', frameon=False, fontsize=9,
               labelcolor=INK)
    ax1.set_title('Well count + dark share',
                  fontsize=10, color=INK, fontfamily='sans-serif',
                  loc='left', pad=6)

    # Right panel: vintage distribution, grouped by state
    ax2 = fig.add_axes([0.52, 0.20, 0.44, 0.56])
    ax2.set_facecolor(PAPER)
    buckets = [0, 1, 2, 3, 4, 5]
    labels = [VINTAGE_LABELS[b] for b in buckets]
    # Compute per-state vintage mix directly from wells (not in summary)
    # s: 0=ND, 1=MT
    nd_counts = [int(((wells['s'] == 0) & (wells['v'] == b)).sum()) for b in buckets]
    mt_counts = [int(((wells['s'] == 1) & (wells['v'] == b)).sum()) for b in buckets]
    # Normalize to percent within each state
    nd_tot = sum(nd_counts); mt_tot = sum(mt_counts)
    nd_pct = [100 * n / nd_tot for n in nd_counts]
    mt_pct = [100 * n / mt_tot for n in mt_counts]
    x = list(range(len(buckets)))
    w = 0.38
    ax2.bar([xi - w/2 for xi in x], nd_pct, width=w, color=AMBER,
            edgecolor='none', label=f'ND ({nd_tot:,})', zorder=3)
    ax2.bar([xi + w/2 for xi in x], mt_pct, width=w, color=TEAL,
            edgecolor='none', label=f'MT ({mt_tot:,})', zorder=3)
    for y in [10, 20, 30, 40, 50]:
        ax2.axhline(y, color=INK, lw=0.3, alpha=0.12, zorder=1)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=9, color=INK,
                        fontfamily='sans-serif')
    ax2.set_yticks([0, 10, 20, 30, 40, 50])
    ax2.set_yticklabels(['0', '10%', '20%', '30%', '40%', '50%'],
                        fontsize=8, color=MUTED, fontfamily='sans-serif')
    for sp in ['top', 'right']: ax2.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax2.spines[sp].set_color(INK); ax2.spines[sp].set_linewidth(0.5)
    ax2.legend(loc='upper left', frameon=False, fontsize=9, labelcolor=INK)
    ax2.set_title('Spud-vintage mix by state (% of in-basin wells)',
                  fontsize=10, color=INK, fontfamily='sans-serif',
                  loc='left', pad=6)

    fig.text(0.04, 0.08,
             'ND: a 2010+ bar that dwarfs everything before it. MT: a pre-1980 '
             'vertical legacy plus an Elm Coulee pulse in the 2000s, then flat. '
             'Same basin. Same Bakken. Two different drilling histories, one '
             'dark-data profile that inverts when you cross the border.',
             fontsize=10, color=MUTED, fontfamily='sans-serif')

    fig.text(0.04, 0.012,
             'Sources: NDIC OGD_Wells (ND), MT BOGC WellSurface (MT), basin-clipped to '
             'USGS Bakken \u2013 Three Forks TPS.   '
             f'Analysis: {HANDLE}',
             fontsize=7, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


# =========================================================================
# Figure 3: vintage split with horizontal flag
# =========================================================================
def fig3_vintage_horizontals():
    out = 'williston_vintage_split.png'
    fig = plt.figure(figsize=(13, 7.5), dpi=220, facecolor=PAPER)

    fig.text(0.04, 0.94,
             'When did the Williston go digital? 2008.',
             fontsize=20, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.04, 0.895,
             'North Dakota\u2019s horizontal Bakken era brought modern '
             'completion logs with it. Everything before: overwhelmingly dark.',
             fontsize=11, color=MUTED, fontfamily='sans-serif')

    ax = fig.add_axes([0.07, 0.18, 0.88, 0.60])
    ax.set_facecolor(PAPER)

    # Per-vintage: total, horizontal (ND only), dark
    buckets = [0, 1, 2, 3, 4, 5]
    labels = [VINTAGE_LABELS[b] for b in buckets]

    # Totals are the full basin (ND+MT); dark/horz computed from wells df
    rows = []
    for b in buckets:
        sub = wells[wells['v'] == b]
        rows.append({
            'v': b,
            'total': len(sub),
            'dark': int((sub['d'] == 1).sum()),
            'horz_nd': int(((sub['h'] == 1) & (sub['s'] == 0)).sum()),
        })
    df = pd.DataFrame(rows)
    df['lit'] = df['total'] - df['dark']

    x = list(range(len(buckets)))
    w = 0.78
    # Bottom: dark (ghost), top: lit (violet)
    ax.bar(x, df['dark'], width=w, color=GHOST, edgecolor='none',
           label='Dark (no log)', zorder=3)
    ax.bar(x, df['lit'], width=w, bottom=df['dark'], color=VIOLET,
           edgecolor='none', label='Lit (public log)', zorder=3)

    # Overlay: horizontal ND wells, hollow bar on top
    ax.bar(x, df['horz_nd'], width=w * 0.55, bottom=0,
           facecolor='none', edgecolor=CLAY, linewidth=2.0,
           label='of which ND horizontal', zorder=4)

    # Totals on top of bars
    for xi, total in zip(x, df['total']):
        ax.text(xi, total + df['total'].max() * 0.015,
                f'{total:,}', ha='center', fontsize=9, color=INK,
                fontweight='bold', fontfamily='sans-serif')

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, color=INK,
                       fontfamily='sans-serif')
    ax.set_ylabel('Wells (basin-clipped)', fontsize=10, color=MUTED,
                  fontfamily='sans-serif')
    ax.tick_params(axis='y', labelsize=8.5, colors=MUTED)
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax.spines[sp].set_color(INK); ax.spines[sp].set_linewidth(0.5)
    ax.legend(loc='upper left', frameon=False, fontsize=9.5, labelcolor=INK)

    fig.text(0.04, 0.08,
             'Pre-1980: 7,909 wells, mostly MT + ND verticals, ~95% dark. '
             '2010+: 21,225 wells, almost all ND horizontals, <10% dark. '
             'The unknown-vintage bucket (6,379 wells) carries the oldest, '
             'unloggged inventory: assume dark.',
             fontsize=10, color=MUTED, fontfamily='sans-serif')

    fig.text(0.04, 0.012,
             'Horizontal flag: NDIC OGD_Horizontals survey table (22,258 '
             'unique horizontal APIs, intersected with OGD_Wells). MT has '
             'no horizontal indicator in the BOGC shapefile and is '
             'excluded from that series.   '
             f'Analysis: {HANDLE}',
             fontsize=7, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


# =========================================================================
# Figure 4: top operators
# =========================================================================
def fig4_operators():
    out = 'williston_operators.png'
    ops = pd.DataFrame(summary['top_operators']).head(15)
    ops = ops.sort_values('total')  # for horizontal barh (bottom = smallest)

    fig = plt.figure(figsize=(12, 9), dpi=220, facecolor=PAPER)
    fig.text(0.04, 0.955,
             'Fifteen names drilled the basin.',
             fontsize=20, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.04, 0.915,
             'Top fifteen operators by in-basin well count. Bar length = '
             'wells drilled. Red overlay = share of those wells that are '
             'dark (no public digital log).',
             fontsize=10.5, color=MUTED, fontfamily='sans-serif')

    ax = fig.add_axes([0.30, 0.08, 0.65, 0.80])
    ax.set_facecolor(PAPER)

    y = list(range(len(ops)))
    ax.barh(y, ops['total'], color=VIOLET, edgecolor='none',
            label='Lit + dark', zorder=3)
    ax.barh(y, ops['dark'], color=CLAY, edgecolor='none',
            label='Dark', zorder=4)

    # Labels
    ax.set_yticks(y)
    short_names = [n.title().replace(', Llc', ', LLC').replace(' Llc', ' LLC')
                            .replace(', Inc.', ', Inc.').replace('L.L.C', 'LLC')
                   for n in ops['operator']]
    ax.set_yticklabels(short_names, fontsize=9, color=INK,
                       fontfamily='sans-serif')

    for yi, (total, dark, pct) in enumerate(zip(
            ops['total'], ops['dark'], ops['pct_dark'])):
        ax.text(total + ops['total'].max() * 0.015, yi,
                f'{total:,}  ({pct:.1f}% dark)',
                va='center', fontsize=9, color=INK,
                fontfamily='sans-serif')

    ax.set_xlabel('Wells inside basin', fontsize=10, color=MUTED,
                  fontfamily='sans-serif')
    ax.tick_params(axis='x', labelsize=8.5, colors=MUTED)
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax.spines[sp].set_color(INK); ax.spines[sp].set_linewidth(0.5)
    ax.legend(loc='lower right', frameon=False, fontsize=9, labelcolor=INK)

    fig.text(0.04, 0.04,
             'Continental, Hess, Whiting: the Bakken majors. Dark share <20% '
             'because their post-2008 horizontals dominate. The legacy operators '
             'with higher dark shares drilled pre-digital verticals that never '
             'got re-logged.',
             fontsize=10, color=MUTED, fontfamily='sans-serif')
    fig.text(0.04, 0.008,
             'Sources: NDIC OGD_Wells + MT BOGC Wells, operator strings '
             'as-is (not deduplicated across corporate name changes).   '
             f'Analysis: {HANDLE}',
             fontsize=7, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


if __name__ == '__main__':
    fig1_basin_map()
    fig2_state_gradient()
    fig3_vintage_horizontals()
    fig4_operators()
    print(f'\nfigures in:\n  {FIG_REPO}\n  {FIG_SITE}')
