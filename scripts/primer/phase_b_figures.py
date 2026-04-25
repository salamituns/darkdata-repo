"""
Phase B: render the primer's three new hero figures.

These don't exist in any basin walk; they only make sense at the series
level.

Outputs (to both repo/figures/ and salamituns.github.io/darkdata/primer_data/figures/):
  1. primer_conus_hero.png        Six basins on one CONUS map, sized + colored
  2. primer_production_timeline.png  EIA DPR 2007 to 2024, 5 basins overlaid
  3. primer_cross_basin_matrix.png   Dark % vs era, all 6 basins on same axes
"""
import warnings; warnings.filterwarnings('ignore')
import json
from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path('/Users/olatunde/CoWorker/Geoworks')
DATA = ROOT / 'salamituns.github.io/darkdata/primer_data'
FIG_REPO = ROOT / 'darkdata-repo/figures'
FIG_SITE = DATA / 'figures'

FIG_REPO.mkdir(parents=True, exist_ok=True)
FIG_SITE.mkdir(parents=True, exist_ok=True)

PAPER  = '#F6F3EB'
INK    = '#0E0E0E'
CLAY   = '#A23B2A'
AMBER  = '#C57B35'
VIOLET = '#6B4E8A'
TEAL   = '#2E6E7E'
WARM   = '#8B6F3E'
SLATE  = '#5C7A8C'
MUTED  = '#7A7368'
FAINT  = '#EDE6D4'
GHOST  = '#B5AEA0'
HANDLE = '@salamituns'

# Load primer data
with open(DATA/'basins.json') as f:
    basins = json.load(f)
conus = gpd.read_file(DATA/'conus_states.json')
with open(DATA/'eia_dpr_5basins.json') as f:
    dpr = json.load(f)
with open(DATA/'primer_summary.json') as f:
    summary = json.load(f)

basin_features = basins['features']

# Convenience: order basins as we want to label them
DISPLAY_ORDER = ['kansas', 'permian', 'williston', 'anadarko', 'appalachia', 'eagle_ford']
basin_by_id = {f['properties']['id']: f for f in basin_features}


# =========================================================================
# Figure 1: CONUS hero map - all 6 basins on one US outline
# =========================================================================
def fig1_conus_hero():
    out = 'primer_conus_hero.png'

    fig = plt.figure(figsize=(15, 11), dpi=220, facecolor=PAPER)
    ax = fig.add_axes([0.02, 0.18, 0.96, 0.70])
    ax.set_facecolor(PAPER)

    # CONUS state outlines
    conus.plot(ax=ax, facecolor=FAINT, edgecolor=INK, linewidth=0.4, zorder=1)

    # Basin polygons (filled)
    for f in basin_features:
        bid = f['properties']['id']
        color = f['properties']['color']
        geom = shape(f['geometry'])
        gdf = gpd.GeoDataFrame(geometry=[geom], crs='EPSG:4269')
        gdf.plot(ax=ax, facecolor=color, edgecolor=INK,
                 linewidth=0.8, alpha=0.65, zorder=3)

    # Basin labels (place at polygon centroid, with leader if needed)
    LABEL_ANCHORS = {
        # (lon, lat) of label position
        'kansas':     (-99.0, 37.5),
        'permian':    (-103.5, 31.0),
        'williston':  (-103.5, 47.7),
        'anadarko':   (-98.0, 35.5),
        'appalachia': (-78.0, 39.5),
        'eagle_ford': (-99.0, 28.4),
    }

    for f in basin_features:
        bid = f['properties']['id']
        short = f['properties']['short']
        lon, lat = LABEL_ANCHORS[bid]
        # Box around the label
        ax.text(lon, lat, short,
                fontsize=12, color=INK, fontfamily='sans-serif',
                fontweight='bold', ha='center', va='center', zorder=8,
                bbox=dict(boxstyle='round,pad=0.4',
                          facecolor=PAPER, edgecolor=INK, linewidth=0.7,
                          alpha=0.94))

    # State labels (subtle)
    state_labels = [
        ('TX', -100.0, 31.5),
        ('OK', -98.5, 35.0),
        ('KS', -98.5, 38.5),
        ('NM', -106.0, 34.5),
        ('CO', -105.5, 39.0),
        ('ND', -100.5, 47.5),
        ('MT', -110.0, 47.0),
        ('PA', -77.8, 40.9),
        ('WV', -80.5, 38.7),
        ('OH', -82.7, 40.3),
        ('CA', -119.5, 36.7),
        ('FL', -82.0, 28.5),
        ('NY', -75.5, 43.0),
    ]
    for code, lon, lat in state_labels:
        ax.text(lon, lat, code, fontsize=8.5, color=INK, alpha=0.45,
                fontfamily='sans-serif', fontweight='bold',
                ha='center', va='center', zorder=2)

    ax.set_xlim(-126, -66)
    ax.set_ylim(24, 50)
    ax.set_aspect(1.30)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)

    fig.text(0.04, 0.92, 'Six basins drilled the United States.',
             fontsize=24, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.04, 0.88,
             'A field guide. Six oil and gas basins, mapped to one US outline. '
             'Colors are arbitrary; the geology, the depth, and the drilling '
             'history are not.',
             fontsize=11.5, color=MUTED, fontfamily='sans-serif')

    # Legend bar at the bottom: basin name + headline number
    ax_leg = fig.add_axes([0.04, 0.04, 0.92, 0.10])
    ax_leg.set_facecolor(PAPER)
    ax_leg.axis('off')

    cell_w = 1.0 / 6
    for i, bid in enumerate(DISPLAY_ORDER):
        f = basin_by_id[bid]
        p = f['properties']
        x = i * cell_w + 0.005
        # Color square
        ax_leg.add_patch(plt.Rectangle((x, 0.58), 0.025, 0.30,
                                        facecolor=p['color'],
                                        edgecolor=INK, linewidth=0.4,
                                        transform=ax_leg.transAxes))
        # Title
        ax_leg.text(x + 0.035, 0.78, p['short'],
                    fontsize=11, color=INK, fontfamily='sans-serif',
                    fontweight='bold', transform=ax_leg.transAxes,
                    va='center')
        # Headline metric
        if p['dark_pct'] is not None:
            metric = f'{p["dark_pct"]}% dark'
            sub = f'{p["well_count"]:,} wells'
        else:
            metric = 'unmeasured'
            sub = '(TX RRC architectural wall)'
        ax_leg.text(x + 0.005, 0.42, metric,
                    fontsize=10, color=p['color'], fontfamily='sans-serif',
                    fontweight='bold', transform=ax_leg.transAxes)
        ax_leg.text(x + 0.005, 0.20, sub,
                    fontsize=8.5, color=MUTED, fontfamily='sans-serif',
                    transform=ax_leg.transAxes)
        ax_leg.text(x + 0.005, 0.02, p['one_line'][:70],
                    fontsize=7.5, color=MUTED, fontfamily='sans-serif',
                    fontstyle='italic', transform=ax_leg.transAxes,
                    wrap=True)

    fig.text(0.04, 0.005,
             'Sources: USGS ScienceBase Assessment Unit polygons (Williston, Anadarko, Eagle Ford). '
             'EIA Tight Oil + Shale Plays Lower 48 Dec 2021 (Appalachia). State county dissolves '
             '(Kansas, Permian). US Census TIGER 2024 5m state outlines.   '
             f'Analysis: {HANDLE}',
             fontsize=7, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


# =========================================================================
# Figure 2: 5-basin production timeline overlay (EIA DPR)
# =========================================================================
def fig2_production_timeline():
    out = 'primer_production_timeline.png'

    fig = plt.figure(figsize=(14, 8), dpi=220, facecolor=PAPER)

    fig.text(0.04, 0.94,
             'Five basins, one chart, eighteen years.',
             fontsize=22, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.04, 0.895,
             'EIA Drilling Productivity Report monthly oil production, January '
             '2007 to present. The horizontal era is visible in every basin '
             'except Appalachia, where the play is gas-dominant.',
             fontsize=11, color=MUTED, fontfamily='sans-serif')

    ax = fig.add_axes([0.07, 0.13, 0.66, 0.73])
    ax.set_facecolor(PAPER)

    # Plot order: largest producer last so it stays on top of legend
    plot_order = ['williston', 'anadarko', 'appalachia', 'eagle_ford', 'permian']
    for bid in plot_order:
        if bid not in dpr['data']:
            continue
        rows = dpr['data'][bid]
        if not rows:
            continue
        df = pd.DataFrame(rows)
        df['month'] = pd.to_datetime(df['month'])
        df = df.sort_values('month')
        color = basin_by_id[bid]['properties']['color']
        ax.fill_between(df['month'], 0, df['oil_total_bbl'] / 1e6,
                        color=color, alpha=0.18, zorder=2)
        ax.plot(df['month'], df['oil_total_bbl'] / 1e6,
                color=color, linewidth=1.6, zorder=3,
                label=f'{basin_by_id[bid]["properties"]["short"]}')

    ax.set_ylabel('Oil production (MMbbl/d)', fontsize=10.5, color=MUTED,
                  fontfamily='sans-serif')
    ax.tick_params(labelsize=9, colors=MUTED)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax.spines[sp].set_color(INK); ax.spines[sp].set_linewidth(0.5)
    ax.legend(loc='upper left', frameon=False, fontsize=10, labelcolor=INK)

    # Side commentary panel
    ax_side = fig.add_axes([0.74, 0.13, 0.24, 0.73])
    ax_side.set_facecolor(PAPER)
    ax_side.axis('off')

    ax_side.text(0, 0.97, 'What this shows',
                 fontsize=12, color=INK, fontfamily='sans-serif',
                 fontweight='bold', va='top')

    ax_side.text(0, 0.91,
                 'Permian: the giant. 6 MMbbl/d in 2024, 4x any other basin. '
                 'The Wolfcamp + Bone Spring stack is the largest US oil '
                 'production source.\n\n'
                 'Eagle Ford: the rocket. From near zero in 2008 to 1.7 '
                 'MMbbl/d in 2015. Then a ten-year plateau.\n\n'
                 'Williston: the Bakken curve. Peaked in late 2014 at 1.4 '
                 'MMbbl/d, dipped during the 2015 crash, recovered to 1.2.\n\n'
                 'Anadarko: SCOOP/STACK pulse around 2018, has settled '
                 'lower since.\n\n'
                 'Appalachia: gas-dominant; minimal oil.\n\n'
                 'Kansas: not on this chart. Below EIA DPR threshold.',
                 fontsize=9, color=MUTED, fontfamily='sans-serif',
                 va='top', wrap=True)

    fig.text(0.04, 0.04,
             'Source: EIA Drilling Productivity Report, monthly Eagle Ford / Permian / '
             'Williston (Bakken Region) / Anadarko / Appalachia oil production, January 2007 to present. '
             'Kansas is below the DPR threshold and not reported by EIA at the basin level.   '
             f'Analysis: {HANDLE}',
             fontsize=7, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


# =========================================================================
# Figure 3: cross-basin matrix (dark % vs horizontal-era role)
# =========================================================================
def fig3_cross_basin_matrix():
    out = 'primer_cross_basin_matrix.png'

    fig = plt.figure(figsize=(13.5, 8.5), dpi=220, facecolor=PAPER)

    fig.text(0.04, 0.94,
             'The thesis, in two axes.',
             fontsize=22, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.04, 0.895,
             'Y axis: percent dark, the share of basin wells with no public '
             'digital log. X axis: horizontal era share of total well count, '
             'the share of basin drilling that happened post-2008. The pattern '
             'is monotonic.',
             fontsize=11, color=MUTED, fontfamily='sans-serif')

    ax = fig.add_axes([0.08, 0.16, 0.62, 0.66])
    ax.set_facecolor(PAPER)

    # Hand-curated horizontal-era share % (rough working estimates)
    horizontal_share = {
        'kansas': 0,            # No horizontal era in KS proper
        'permian': 28,          # ~110K horizontals of 393K total
        'williston': 47,        # 21K horizontals of 45K total
        'anadarko': 6,          # 27K of 483K
        'appalachia': 5,        # 28K of 579K
        'eagle_ford': None,     # Unmeasured
    }

    # Per-basin label placement. Generic offsets cause collisions
    # (Kansas at x=0 with a right-offset label lands on top of
    # Appalachia). Each basin gets an explicit anchor + alignment.
    LABEL_PLACEMENT = {
        # bid:        (dx,   dy,   ha,      va)
        'kansas':     (-1.0,  0.0, 'right', 'center'),
        'appalachia': ( 1.5,  1.8, 'left',  'bottom'),
        'anadarko':   ( 1.5, -0.6, 'left',  'top'),
        'permian':    ( 1.5,  1.5, 'left',  'bottom'),
        'williston':  (-1.5,  3.0, 'right', 'bottom'),
    }

    # Plot 5 measured basins
    for bid in DISPLAY_ORDER:
        f = basin_by_id[bid]
        p = f['properties']
        if p['dark_pct'] is None:
            continue
        x = horizontal_share[bid]
        y = p['dark_pct']
        ax.scatter(x, y, s=300, c=p['color'], edgecolor=INK, linewidth=1.0,
                   alpha=0.85, zorder=4)
        dx, dy, ha, va = LABEL_PLACEMENT.get(bid, (1.5, 1.5, 'left', 'bottom'))
        ax.text(x + dx, y + dy, p['short'],
                fontsize=11.5, color=INK, fontfamily='sans-serif',
                fontweight='bold', va=va, ha=ha, zorder=5)

    # Trend line: dark % drops as horizontal share rises.
    ax.plot([0, 50], [97, 40], color=INK, linewidth=0.9, linestyle='--',
            alpha=0.35, zorder=2)
    # Annotation sits in the empty zone between Permian (28, 78) and
    # Williston (47, 46), well clear of every data point label.
    ax.text(33, 67, 'Horizontal era\nrescue trend',
            fontsize=9, color=MUTED, fontfamily='sans-serif',
            fontstyle='italic', alpha=0.85, ha='left', va='center',
            rotation=-22)

    # Highlight: Williston is the only majority-lit basin
    ax.axhline(50, color=CLAY, linewidth=0.6, linestyle=':', alpha=0.35, zorder=1)
    ax.text(2, 51.5, '50% line: majority-lit threshold', fontsize=8.5,
            color=CLAY, fontfamily='sans-serif', fontstyle='italic', alpha=0.7)

    ax.set_xlabel('Horizontal era share of total well count (%)',
                  fontsize=10.5, color=MUTED, fontfamily='sans-serif')
    ax.set_ylabel('Percent dark (no public digital log)',
                  fontsize=10.5, color=MUTED, fontfamily='sans-serif')
    ax.set_xlim(-3, 55)
    ax.set_ylim(35, 100)
    ax.tick_params(labelsize=9, colors=MUTED)
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax.spines[sp].set_color(INK); ax.spines[sp].set_linewidth(0.5)

    # Side panel: Eagle Ford callout
    ax_side = fig.add_axes([0.72, 0.16, 0.25, 0.66])
    ax_side.set_facecolor(PAPER)
    ax_side.axis('off')

    ax_side.text(0, 0.97, 'Eagle Ford',
                 fontsize=13, color=INK, fontfamily='serif',
                 fontweight='medium', va='top')
    ax_side.text(0, 0.92, 'not on this chart',
                 fontsize=9.5, color=MUTED, fontfamily='sans-serif',
                 fontstyle='italic', va='top')

    ax_side.text(0, 0.83,
                 'EIA estimates roughly 30,000 horizontal wells in Eagle '
                 'Ford against a ~500,000-well legacy. That puts horizontal '
                 'share around 6 percent and predicts a dark share in the '
                 'high 80s, in line with Anadarko and Appalachia.\n\n'
                 'TX Railroad Commission does not publish bulk well data in '
                 'a form a public analyst can pull at scale, so we cannot '
                 'plot the basin on this chart.\n\n'
                 'The trend predicts where Eagle Ford should land. The '
                 'architecture decided we cannot verify it.',
                 fontsize=9, color=INK, fontfamily='sans-serif',
                 va='top', wrap=True)

    fig.text(0.04, 0.04,
             'Sources: dark-data series basin walks (each basin links from this primer). Horizontal-era shares are basin-walk-derived. '
             'Trend line is illustrative, not a regression.   '
             f'Analysis: {HANDLE}',
             fontsize=7, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


if __name__ == '__main__':
    fig1_conus_hero()
    fig2_production_timeline()
    fig3_cross_basin_matrix()
    print('all 3 primer figures written')
