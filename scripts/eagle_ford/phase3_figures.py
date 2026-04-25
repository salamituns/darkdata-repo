"""
Phase 3: Eagle Ford basin-06 static figures.

Three hero figures, same editorial palette as the rest of the series.
All carry `Analysis: @salamituns` attribution.

Outputs (written to both repo/figures/ and salamituns.github.io/darkdata/eagle_ford/figures/):
  1. eagle_ford_basin_map.png            USGS AUs + 76 TX counties + state, no wells
  2. regulatory_accessibility.png        9 regulators ranked, TX bottom
  3. eagle_ford_production_curve.png     EIA DPR Eagle Ford 2007-present
"""
import warnings; warnings.filterwarnings('ignore')
import json
from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch

ROOT = Path('/Users/olatunde/CoWorker/Geoworks')
DATA = ROOT / 'salamituns.github.io/darkdata/eagle_ford/data'
FIG_REPO = ROOT / 'darkdata-repo/figures'
FIG_SITE = ROOT / 'salamituns.github.io/darkdata/eagle_ford/figures'

FIG_REPO.mkdir(parents=True, exist_ok=True)
FIG_SITE.mkdir(parents=True, exist_ok=True)

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

# ---- Load ---------------------------------------------------------------
print('loading data...')
ef_aus = gpd.read_file(DATA/'eagle_ford_aus.json')
ef_counties = gpd.read_file(DATA/'eagle_ford_counties.json')
tx_outline = gpd.read_file(DATA/'state_outline.json')
with open(DATA/'eia_eagle_ford_monthly.json') as f:
    dpr = json.load(f)
with open(DATA/'regulatory_comparison.json') as f:
    regs = json.load(f)
with open(DATA/'summary.json') as f:
    summary = json.load(f)

# =========================================================================
# Figure 1: basin map
# =========================================================================
def fig1_basin_map():
    out = 'eagle_ford_basin_map.png'

    fig = plt.figure(figsize=(13.5, 10.5), dpi=220, facecolor=PAPER)
    ax = fig.add_axes([0.02, 0.30, 0.96, 0.60])
    ax.set_facecolor(PAPER)

    # Texas outline
    tx_outline.plot(ax=ax, facecolor=FAINT, edgecolor=INK, linewidth=0.5, zorder=1)
    # Eagle Ford counties (shaded)
    ef_counties.plot(ax=ax, facecolor='#E2D8C2', edgecolor=INK, linewidth=0.25,
                     alpha=0.7, zorder=2)
    # USGS Eagle Ford AU polygons (different fill per AU)
    au_colors = [AMBER, VIOLET, TEAL, CLAY, '#A8A088', '#7A6FAA', '#3E8095']
    for i, (_, row) in enumerate(ef_aus.iterrows()):
        color = au_colors[i % len(au_colors)]
        gpd.GeoDataFrame(geometry=[row.geometry], crs=ef_aus.crs).plot(
            ax=ax, facecolor=color, edgecolor='none',
            alpha=0.45, linewidth=0, zorder=3,
        )

    # Basin envelope outline (union of AUs)
    from shapely.ops import unary_union
    env = unary_union(ef_aus.geometry.tolist())
    gpd.GeoDataFrame(geometry=[env], crs=ef_aus.crs).plot(
        ax=ax, facecolor='none', edgecolor=INK, linewidth=1.6, zorder=4,
    )

    # City anchors
    cities = [
        ('San Antonio', -98.49, 29.42),
        ('Austin', -97.74, 30.27),
        ('Houston', -95.37, 29.76),
        ('Corpus Christi', -97.40, 27.80),
        ('Laredo', -99.51, 27.50),
        ('Eagle Pass', -100.50, 28.71),
        ('Karnes City', -97.90, 28.89),
    ]
    for name, lon, lat in cities:
        ax.scatter([lon], [lat], s=26, facecolor=PAPER,
                   edgecolor=INK, lw=0.9, zorder=8, marker='s')
        ax.text(lon + 0.10, lat + 0.06, name, fontsize=8.6, color=INK,
                fontfamily='sans-serif', fontweight='medium',
                ha='left', va='bottom', zorder=9)

    # Annotation: where the wells would be
    ax.text(-98.4, 28.6, 'Karnes Trough\n(Eagle Ford core)',
            fontsize=10, color=INK, alpha=0.6, fontfamily='serif',
            fontstyle='italic', ha='center', va='center', zorder=7)

    # Texas focus bounds
    ax.set_xlim(-106.7, -93.5)
    ax.set_ylim(25.5, 36.7)
    ax.set_aspect(1.18)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)

    fig.text(0.035, 0.955,
             'A basin we cannot show you the wells in.',
             fontsize=22, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.035, 0.918,
             f'7 USGS Eagle Ford Group Assessment Units across {len(ef_counties)} '
             'South Texas counties. EIA estimates more than 30,000 horizontal '
             'wells inside this footprint and roughly a half-million conventional '
             'wells of every vintage drilled around them. Texas Railroad '
             'Commission does not publish per-well lat/lon, vintage, or dark/lit '
             'in any form a public analyst can pull at scale.',
             fontsize=11, color=MUTED, fontfamily='sans-serif')

    # Legend: the 7 AUs
    handles = []
    au_names = ef_aus['au_name'].tolist()
    for i, name in enumerate(au_names):
        color = au_colors[i % len(au_colors)]
        handles.append(Patch(facecolor=color, edgecolor='none', alpha=0.55,
                             label=name))
    leg = fig.legend(handles=handles, loc='lower left', frameon=False,
                     fontsize=8.5, labelcolor=INK,
                     bbox_to_anchor=(0.05, 0.05), ncol=1, handletextpad=0.6,
                     title='USGS Assessment Units')
    leg.get_title().set_fontfamily('sans-serif')
    leg.get_title().set_fontweight('bold')
    leg.get_title().set_fontsize(9.5)
    leg.get_title().set_color(INK)
    for t in leg.get_texts(): t.set_fontfamily('sans-serif')

    fig.text(0.035, 0.006,
             'Sources: USGS ScienceBase item 5d1246c2: Eagle Ford Group Assessment Unit boundaries, 7 AUs unioned. '
             'US Census TIGER 2024 5m county + state cartographic boundaries.   '
             f'Analysis: {HANDLE}',
             fontsize=7, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


# =========================================================================
# Figure 2: regulatory accessibility ranking
# =========================================================================
def fig2_regulatory_accessibility():
    out = 'regulatory_accessibility.png'
    fig = plt.figure(figsize=(13, 9), dpi=220, facecolor=PAPER)

    fig.text(0.04, 0.94,
             'Six basins, nine regulators, one outlier.',
             fontsize=20, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.04, 0.895,
             'Accessibility score is a working analyst\'s rating of how '
             'cleanly each agency publishes its bulk well data. 100 = direct '
             'CMS download, no auth, no session. 0 = inaccessible without '
             'browser automation. Order is by score.',
             fontsize=11, color=MUTED, fontfamily='sans-serif')

    ax = fig.add_axes([0.07, 0.13, 0.66, 0.72])
    ax.set_facecolor(PAPER)
    sorted_regs = sorted(regs['regulators'], key=lambda r: r['access_score'])
    labels = [f"{r['state']}  {r['agency'][:28]}" for r in sorted_regs]
    scores = [r['access_score'] for r in sorted_regs]
    # Color: TX = clay (the outlier), others by score band
    colors = []
    for r in sorted_regs:
        s = r['access_score']
        if r['state'] == 'TX':
            colors.append(CLAY)
        elif s >= 95:
            colors.append(VIOLET)
        elif s >= 80:
            colors.append(AMBER)
        elif s >= 60:
            colors.append(TEAL)
        else:
            colors.append(GHOST)

    y = list(range(len(labels)))
    ax.barh(y, scores, color=colors, edgecolor='none', height=0.74)

    for i, (s, r) in enumerate(zip(scores, sorted_regs)):
        ax.text(s + 1.5, i, f'{s}',
                va='center', fontsize=10, color=INK,
                fontfamily='sans-serif', fontweight='bold')

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9.5, color=INK,
                       fontfamily='sans-serif')
    ax.set_xlim(0, 110)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(['0', '25', '50', '75', '100'],
                       fontsize=8.5, color=MUTED, fontfamily='sans-serif')
    ax.set_xlabel('Accessibility score', fontsize=10, color=MUTED,
                  fontfamily='sans-serif')
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax.spines[sp].set_color(INK); ax.spines[sp].set_linewidth(0.5)

    # Side commentary panel
    ax2 = fig.add_axes([0.74, 0.13, 0.24, 0.72])
    ax2.set_facecolor(PAPER)
    ax2.axis('off')

    # Find Texas in the list
    tx = next(r for r in regs['regulators'] if r['state'] == 'TX')
    ax2.text(0, 0.95, 'Texas', fontsize=14, color=INK,
             fontfamily='serif', fontweight='medium', va='top')
    ax2.text(0, 0.88, 'TX Railroad Commission', fontsize=8.5, color=MUTED,
             fontfamily='sans-serif', va='top',
             style='italic')
    ax2.text(0, 0.81, f'Score: {tx["access_score"]}/100', fontsize=11,
             color=CLAY, fontfamily='sans-serif', fontweight='bold', va='top')
    ax2.text(0, 0.74,
             'Method: ' + tx['method'],
             fontsize=8.5, color=INK, fontfamily='sans-serif', va='top')
    ax2.text(0, 0.66, tx['notes'],
             fontsize=8.7, color=MUTED, fontfamily='sans-serif', va='top',
             wrap=True)

    ax2.text(0, 0.18, 'In contrast:', fontsize=10, color=INK,
             fontfamily='sans-serif', fontweight='bold', va='top')
    ax2.text(0, 0.12,
             'Oklahoma OCC, North Dakota NDIC, and Pennsylvania DEP all '
             'publish bulk well data as direct shapefile or CSV downloads, '
             'no auth, no session, no scraping. The cooperative regulators '
             'made one design choice; Texas made another.',
             fontsize=8.7, color=MUTED, fontfamily='sans-serif', va='top',
             wrap=True)

    fig.text(0.04, 0.04,
             'Source: this researcher\'s experience pulling each basin in this series, January 2026 to April 2026. '
             'Scores are working analyst ratings, not formal benchmarks.   '
             f'Analysis: {HANDLE}',
             fontsize=7, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


# =========================================================================
# Figure 3: EIA DPR Eagle Ford production timeline
# =========================================================================
def fig3_production_curve():
    out = 'eagle_ford_production_curve.png'

    df = pd.DataFrame(dpr['data'])
    df['month'] = pd.to_datetime(df['month'])
    df = df.sort_values('month').reset_index(drop=True)

    fig = plt.figure(figsize=(13, 8), dpi=220, facecolor=PAPER)

    fig.text(0.04, 0.94,
             'What we know about Eagle Ford anyway.',
             fontsize=20, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.04, 0.895,
             'EIA Drilling Productivity Report aggregates Eagle Ford rig '
             'count and production at the region level. We cannot see the '
             'wells, but we can see the curve.',
             fontsize=11, color=MUTED, fontfamily='sans-serif')

    # Rig count chart on top
    ax_rig = fig.add_axes([0.07, 0.55, 0.88, 0.30])
    ax_rig.set_facecolor(PAPER)
    ax_rig.fill_between(df['month'], 0, df['rig_count'],
                        color=AMBER, alpha=0.35, zorder=2)
    ax_rig.plot(df['month'], df['rig_count'], color=CLAY, linewidth=1.4, zorder=3)
    ax_rig.set_ylabel('Rig count', fontsize=9.5, color=MUTED,
                      fontfamily='sans-serif')
    rig_peak = df.loc[df['rig_count'].idxmax()]
    ax_rig.annotate(
        f"Peak {rig_peak['rig_count']:.0f} rigs\n{rig_peak['month'].strftime('%b %Y')}",
        xy=(rig_peak['month'], rig_peak['rig_count']),
        xytext=(rig_peak['month'] + pd.Timedelta(days=400), rig_peak['rig_count'] * 0.88),
        fontsize=9, color=INK, fontfamily='sans-serif', fontweight='medium',
        arrowprops=dict(arrowstyle='-', color=INK, lw=0.8),
    )
    for sp in ['top', 'right']: ax_rig.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax_rig.spines[sp].set_color(INK); ax_rig.spines[sp].set_linewidth(0.5)
    ax_rig.tick_params(labelsize=8.5, colors=MUTED)
    ax_rig.set_xlim(df['month'].min(), df['month'].max())
    ax_rig.xaxis.set_major_locator(mdates.YearLocator(2))
    ax_rig.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Oil production chart on bottom
    ax_oil = fig.add_axes([0.07, 0.13, 0.88, 0.36])
    ax_oil.set_facecolor(PAPER)
    ax_oil.fill_between(df['month'], 0, df['oil_total_bbl'] / 1e6,
                        color=VIOLET, alpha=0.30, zorder=2)
    ax_oil.plot(df['month'], df['oil_total_bbl'] / 1e6, color='#4E3A6B',
                linewidth=1.5, zorder=3)
    ax_oil.set_ylabel('Oil production (MMbbl/d)', fontsize=9.5, color=MUTED,
                      fontfamily='sans-serif')

    oil_peak = df.loc[df['oil_total_bbl'].idxmax()]
    ax_oil.annotate(
        f"Peak {oil_peak['oil_total_bbl']/1e6:.2f} MMbbl/d\n{oil_peak['month'].strftime('%b %Y')}",
        xy=(oil_peak['month'], oil_peak['oil_total_bbl'] / 1e6),
        xytext=(oil_peak['month'] + pd.Timedelta(days=600),
                oil_peak['oil_total_bbl'] / 1e6 * 0.90),
        fontsize=9, color=INK, fontfamily='sans-serif', fontweight='medium',
        arrowprops=dict(arrowstyle='-', color=INK, lw=0.8),
    )

    for sp in ['top', 'right']: ax_oil.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax_oil.spines[sp].set_color(INK); ax_oil.spines[sp].set_linewidth(0.5)
    ax_oil.tick_params(labelsize=8.5, colors=MUTED)
    ax_oil.set_xlim(df['month'].min(), df['month'].max())
    ax_oil.xaxis.set_major_locator(mdates.YearLocator(2))
    ax_oil.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax_oil.set_xlabel('', fontsize=9.5, color=MUTED, fontfamily='sans-serif')

    fig.text(0.04, 0.04,
             'Source: EIA Drilling Productivity Report (DPR), Eagle Ford Region monthly time series, January 2007 onward.   '
             f'Analysis: {HANDLE}',
             fontsize=7, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


if __name__ == '__main__':
    fig1_basin_map()
    fig2_regulatory_accessibility()
    fig3_production_curve()
    print('all 3 figures written')
