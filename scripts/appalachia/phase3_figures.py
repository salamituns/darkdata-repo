"""
Phase 3: Appalachia basin static figures.

Four hero figures, same editorial palette as Kansas + Williston +
Anadarko + GHGRP. All carry `Analysis: @salamituns` attribution per
the figure-attribution rule.

Outputs (written to both repo/figures/ and salamituns.github.io/darkdata/appalachia/figures/):
  1. appalachia_basin_map.png       hero map: PA + WV + OH inside basin polygon
  2. appalachia_state_gradient.png  per-state dark share + vintage mix
  3. appalachia_vintage_split.png   vintage with horizontal flag
  4. appalachia_operators.png       split top operators per state
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
DATA = ROOT / 'salamituns.github.io/darkdata/appalachia/data'
FIG_REPO = ROOT / 'darkdata-repo/figures'
FIG_SITE = ROOT / 'salamituns.github.io/darkdata/appalachia/figures'
STATES_SRC = ROOT / 'data/raw/census_boundaries/gz_2010_us_040_00_5m.json'

FIG_REPO.mkdir(parents=True, exist_ok=True)
FIG_SITE.mkdir(parents=True, exist_ok=True)

# ---- Editorial palette --------------------------------------------------
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
print('loading wells + basin...')
wells = pd.read_csv(DATA / 'wells.csv')
with open(DATA / 'appalachia_basin.json') as f:
    basin_gj = json.load(f)
with open(DATA / 'summary.json') as f:
    summary = json.load(f)

basin_geom = shape(basin_gj['features'][0]['geometry'])
basin_gdf = gpd.GeoDataFrame(geometry=[basin_geom], crs='EPSG:4269')
states = gpd.read_file(STATES_SRC)
pa_wv_oh = states[states['NAME'].isin(['Pennsylvania', 'West Virginia', 'Ohio'])]

VINTAGE_LABELS = {
    0: 'pre-1980',
    1: '1980s',
    2: '1990s',
    3: '2000s',
    4: '2010+',
    5: 'unknown',
}
# s codes: 0 = PA (amber), 1 = WV (teal), 2 = OH (violet)
STATE_LABELS = {0: 'Pennsylvania', 1: 'West Virginia', 2: 'Ohio'}
STATE_COLORS = {0: AMBER, 1: TEAL, 2: VIOLET}

print(f'wells={len(wells):,}  basin_bounds={basin_geom.bounds}')


def _real_op(op):
    if op is None or pd.isna(op):
        return False
    s = str(op).strip()
    if not s or s.upper() in ('UNKNOWN', 'OPERATOR UNKNOWN'):
        return False
    if 'NOT ASSIGNED' in s.upper():
        return False
    if s.upper().startswith('HISTORIC'):
        return False
    return True


# =========================================================================
# Figure 1: hero basin map
# =========================================================================
def fig1_basin_map():
    out = 'appalachia_basin_map.png'
    WEST, SOUTH, EAST, NORTH = basin_geom.bounds
    WEST -= 0.4; EAST += 0.4; SOUTH -= 0.3; NORTH += 0.3

    fig = plt.figure(figsize=(12.5, 11.0), dpi=220, facecolor=PAPER)
    ax = fig.add_axes([0.02, 0.30, 0.96, 0.60])
    ax.set_facecolor(PAPER)

    pa_wv_oh.plot(ax=ax, color=FAINT, edgecolor=INK, linewidth=0.35, zorder=1)
    basin_gdf.plot(ax=ax, facecolor='none', edgecolor=INK,
                   linewidth=1.6, linestyle='-', zorder=2)

    dark = wells[wells['d'] == 1]
    lit = wells[wells['d'] == 0]
    ax.scatter(dark['lon'], dark['lat'], s=0.9, c=GHOST, alpha=0.30,
               linewidth=0, zorder=3, marker='o', rasterized=True)
    for v, color in [(3, AMBER), (4, VIOLET), (0, CLAY), (1, CLAY), (2, CLAY)]:
        sub = lit[lit['v'] == v]
        if len(sub) == 0:
            continue
        ax.scatter(sub['lon'], sub['lat'], s=3.0, c=color, alpha=0.75,
                   linewidth=0, zorder=4, marker='o', rasterized=True)

    # State labels
    ax.text(-77.7, 41.0, 'PENNSYLVANIA', fontsize=12, color=INK,
            fontfamily='sans-serif', fontweight='bold', alpha=0.45,
            ha='center', zorder=9)
    ax.text(-80.5, 38.6, 'WEST\nVIRGINIA', fontsize=12, color=INK,
            fontfamily='sans-serif', fontweight='bold', alpha=0.45,
            ha='center', zorder=9)
    ax.text(-82.3, 40.4, 'OHIO', fontsize=12, color=INK,
            fontfamily='sans-serif', fontweight='bold', alpha=0.45,
            ha='center', zorder=9)

    # US locator inset
    ax_us = fig.add_axes([0.83, 0.78, 0.14, 0.09])
    ax_us.set_facecolor(PAPER)
    conus = states[~states['NAME'].isin(
        ['Alaska', 'Hawaii', 'Puerto Rico', 'District of Columbia'])]
    conus.plot(ax=ax_us, facecolor=FAINT, edgecolor=INK,
               linewidth=0.25, alpha=0.9)
    pa_wv_oh.plot(ax=ax_us, facecolor=CLAY, edgecolor=INK, linewidth=0.35)
    basin_gdf.plot(ax=ax_us, facecolor='none', edgecolor=INK, linewidth=0.6)
    ax_us.set_xticks([]); ax_us.set_yticks([])
    for sp in ax_us.spines.values(): sp.set_visible(False)
    ax_us.text(0.5, -0.18, 'APPALACHIAN BASIN', transform=ax_us.transAxes,
               ha='center', va='top', fontsize=7.5, color=INK,
               fontfamily='sans-serif', fontweight='bold')

    # Anchor cities + the Drake well
    cities = [
        ('Titusville (Drake 1859)', -79.67, 41.63),
        ('Pittsburgh',  -79.99, 40.44),
        ('Williamsport', -77.00, 41.24),
        ('Morgantown', -79.96, 39.63),
        ('Charleston WV', -81.63, 38.35),
        ('Columbus', -82.99, 39.96),
        ('Youngstown', -80.65, 41.10),
        ('Cleveland', -81.69, 41.50),
    ]
    for name, lon, lat in cities:
        ax.scatter([lon], [lat], s=22, facecolor=PAPER,
                   edgecolor=INK, lw=0.9, zorder=8, marker='s')
        ax.text(lon + 0.10, lat + 0.06, name, fontsize=8.2, color=INK,
                fontfamily='sans-serif', fontweight='medium',
                ha='left', va='bottom', zorder=9)

    # Play labels
    ax.text(-79.0, 41.7, 'Marcellus core\n(NE PA)', fontsize=9.5,
            color=INK, alpha=0.6, fontfamily='serif', fontstyle='italic',
            ha='center', va='center', zorder=7)
    ax.text(-81.5, 40.0, 'Utica\n(eastern OH)', fontsize=9.5, color=INK,
            alpha=0.6, fontfamily='serif', fontstyle='italic',
            ha='center', va='center', zorder=7)

    ax.set_xlim(WEST, EAST); ax.set_ylim(SOUTH, NORTH)
    ax.set_aspect(1.30)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)

    fig.text(0.035, 0.955,
             'A century and a half of drilling, three regulators.',
             fontsize=22, color=INK, fontfamily='serif', fontweight='medium')
    n_total = summary['total_wells']
    pct_dark = summary['pct_dark']
    fig.text(0.035, 0.918,
             f'{n_total:,} wells inside the EIA Appalachian Basin polygon. '
             f'{pct_dark}% have no public digital log. The 2008+ Marcellus '
             'and Utica horizontal eras lit a thin top layer over a '
             '165-year vertical legacy that began at Titusville.',
             fontsize=11, color=MUTED, fontfamily='sans-serif')

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

    # Per-state dark share inset
    ax2 = fig.add_axes([0.52, 0.04, 0.42, 0.21])
    ax2.set_facecolor(PAPER)
    states_rows = ['Pennsylvania', 'West Virginia', 'Ohio']
    colors = [AMBER, TEAL, VIOLET]
    by_state = summary['by_state']
    pcts = [by_state['PA']['pct_dark'], by_state['WV']['pct_dark'], by_state['OH']['pct_dark']]
    totals = [by_state['PA']['total'], by_state['WV']['total'], by_state['OH']['total']]
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

    fig.text(0.035, 0.006,
             'Sources: PA DEP Conv/Unconv + Historic WPA wells. WV DEP 2016 well location + 2024 H6A '
             'horizontal production (PERMIT_ID and API do not link in WV; the state is therefore '
             'counted 100 percent dark). OH DOG_Services REST query, 242,035 wells. EIA Tight Oil + '
             'Shale Plays Dec 2021, Basin=Appalachian (Marcellus + Utica + Devonian + Chattanooga).   '
             f'Analysis: {HANDLE}',
             fontsize=6.6, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


# =========================================================================
# Figure 2: state gradient + vintage mix
# =========================================================================
def fig2_state_gradient():
    out = 'appalachia_state_gradient.png'
    fig = plt.figure(figsize=(13.5, 8), dpi=220, facecolor=PAPER)

    fig.text(0.04, 0.94,
             'Three regulators, one petroleum province.',
             fontsize=20, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.04, 0.895,
             'Pennsylvania publishes its conventional/unconventional split. '
             'Ohio publishes a slant code. West Virginia publishes a permit '
             'sequence and a separate horizontal-production roll, and the '
             'two do not link.',
             fontsize=11, color=MUTED, fontfamily='sans-serif')

    ax1 = fig.add_axes([0.05, 0.18, 0.38, 0.60])
    ax1.set_facecolor(PAPER)
    by_state = summary['by_state']
    states_ = ['PA', 'WV', 'OH']
    state_colors = [AMBER, TEAL, VIOLET]
    dark_n = [by_state[s]['dark'] for s in states_]
    lit_n  = [by_state[s]['total'] - by_state[s]['dark'] for s in states_]
    totals = [by_state[s]['total'] for s in states_]
    ax1.bar(states_, lit_n, color=state_colors, edgecolor='none',
            label='Lit', zorder=3)
    ax1.bar(states_, dark_n, bottom=lit_n, color=GHOST, edgecolor='none',
            label='Dark', zorder=3)
    for i, (s, t) in enumerate(zip(states_, totals)):
        ax1.text(i, t + max(totals) * 0.015, f'{t:,}',
                 ha='center', fontsize=10, color=INK, fontweight='bold',
                 fontfamily='sans-serif')
        pct = by_state[s]['pct_dark']
        ax1.text(i, lit_n[i] + dark_n[i] / 2, f'{pct:.1f}%\ndark',
                 ha='center', va='center', fontsize=10.5, color=INK,
                 fontweight='bold', fontfamily='sans-serif')
    ax1.set_ylabel('Wells', fontsize=9.5, color=MUTED,
                   fontfamily='sans-serif')
    ax1.set_xticklabels(['Pennsylvania', 'West Virginia', 'Ohio'],
                        fontsize=10.5, color=INK, fontfamily='sans-serif')
    ax1.tick_params(axis='y', labelsize=8, colors=MUTED)
    for sp in ['top', 'right']: ax1.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax1.spines[sp].set_color(INK); ax1.spines[sp].set_linewidth(0.5)
    ax1.set_title('Well count + dark share',
                  fontsize=10, color=INK, fontfamily='sans-serif',
                  loc='left', pad=6)

    # Right: per-state vintage mix (only PA has real vintage signal)
    ax2 = fig.add_axes([0.52, 0.18, 0.44, 0.60])
    ax2.set_facecolor(PAPER)
    buckets = [0, 1, 2, 3, 4, 5]
    labels = [VINTAGE_LABELS[b] for b in buckets]
    pa_counts = [int(((wells['s'] == 0) & (wells['v'] == b)).sum()) for b in buckets]
    wv_counts = [int(((wells['s'] == 1) & (wells['v'] == b)).sum()) for b in buckets]
    oh_counts = [int(((wells['s'] == 2) & (wells['v'] == b)).sum()) for b in buckets]
    pa_tot, wv_tot, oh_tot = sum(pa_counts), sum(wv_counts), sum(oh_counts)
    pa_pct = [100*n/pa_tot if pa_tot else 0 for n in pa_counts]
    wv_pct = [100*n/wv_tot if wv_tot else 0 for n in wv_counts]
    oh_pct = [100*n/oh_tot if oh_tot else 0 for n in oh_counts]
    x = list(range(len(buckets)))
    w = 0.26
    ax2.bar([xi - w for xi in x], pa_pct, width=w, color=AMBER,
            edgecolor='none', label=f'PA ({pa_tot:,})', zorder=3)
    ax2.bar([xi for xi in x], wv_pct, width=w, color=TEAL,
            edgecolor='none', label=f'WV ({wv_tot:,})', zorder=3)
    ax2.bar([xi + w for xi in x], oh_pct, width=w, color=VIOLET,
            edgecolor='none', label=f'OH ({oh_tot:,})', zorder=3)
    ymax = max(max(pa_pct), max(wv_pct), max(oh_pct))
    grid = list(range(10, int(ymax) + 20, 10))
    for y in grid:
        ax2.axhline(y, color=INK, lw=0.3, alpha=0.12, zorder=1)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=9, color=INK,
                        fontfamily='sans-serif')
    yt = [g for g in [0] + grid if g <= ymax + 5]
    ax2.set_yticks(yt)
    ax2.set_yticklabels([f'{g}%' if g else '0' for g in yt],
                        fontsize=8, color=MUTED, fontfamily='sans-serif')
    for sp in ['top', 'right']: ax2.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax2.spines[sp].set_color(INK); ax2.spines[sp].set_linewidth(0.5)
    ax2.legend(loc='upper right', frameon=False, fontsize=9, labelcolor=INK)
    ax2.set_title('Spud-vintage mix by state (% of in-basin wells)',
                  fontsize=10, color=INK, fontfamily='sans-serif',
                  loc='left', pad=6)

    fig.text(0.04, 0.07,
             'PA carries the only meaningful vintage signal in the basin: a real pre-1980 mountain '
             '(Drake-era + Devonian sandstone) plus a visible 2010+ Marcellus bar. WV and OH ship '
             'no spud-date column on the public well files; both states default to vintage unknown.',
             fontsize=10, color=MUTED, fontfamily='sans-serif')

    fig.text(0.04, 0.012,
             'Sources: PA DEP shapefiles (basin-clipped); WV DEP 2016 well location XLSX; OH DOG_Services REST query.   '
             f'Analysis: {HANDLE}',
             fontsize=7, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


# =========================================================================
# Figure 3: vintage with horizontal flag
# =========================================================================
def fig3_vintage_horizontals():
    out = 'appalachia_vintage_split.png'
    fig = plt.figure(figsize=(13, 7.5), dpi=220, facecolor=PAPER)

    fig.text(0.04, 0.94,
             'When did the Marcellus go horizontal? 2008.',
             fontsize=20, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.04, 0.895,
             'The 2010+ bar is real, almost entirely PA, almost entirely '
             'horizontal. Pre-1980 wells and unknown-vintage wells together '
             'are the dark mountain.',
             fontsize=11, color=MUTED, fontfamily='sans-serif')

    ax = fig.add_axes([0.07, 0.18, 0.88, 0.60])
    ax.set_facecolor(PAPER)

    buckets = [0, 1, 2, 3, 4, 5]
    labels = [VINTAGE_LABELS[b] for b in buckets]
    rows = []
    for b in buckets:
        sub = wells[wells['v'] == b]
        rows.append({
            'v': b,
            'total': len(sub),
            'dark': int((sub['d'] == 1).sum()),
            'horz_pa': int(((sub['h'] == 1) & (sub['s'] == 0)).sum()),
        })
    df = pd.DataFrame(rows)
    df['lit'] = df['total'] - df['dark']

    x = list(range(len(buckets)))
    w = 0.78
    ax.bar(x, df['dark'], width=w, color=GHOST, edgecolor='none',
           label='Dark (no log)', zorder=3)
    ax.bar(x, df['lit'], width=w, bottom=df['dark'], color=VIOLET,
           edgecolor='none', label='Lit (public log)', zorder=3)
    ax.bar(x, df['horz_pa'], width=w * 0.55, bottom=0,
           facecolor='none', edgecolor=CLAY, linewidth=2.0,
           label='of which PA horizontal', zorder=4)

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
    ax.legend(loc='upper right', frameon=False, fontsize=9.5,
              labelcolor=INK)

    unknown_n = int(df.iloc[5]['total'])
    pre1980_n = int(df.iloc[0]['total'])
    fig.text(0.04, 0.07,
             f'Pre-1980 PA: {pre1980_n:,} wells, almost all dark, including '
             f'30,527 historic WPA-mapped wells from the Drake era forward. '
             f'Unknown vintage: {unknown_n:,} wells, almost all WV + OH where '
             'the public file does not ship a spud-date column.',
             fontsize=10, color=MUTED, fontfamily='sans-serif')

    fig.text(0.04, 0.012,
             'Sources: PA DEP, WV DEP, OH DNR DOG. Vintage = spud year for PA conv/unconv; '
             'historic PA = pre-1980; WV+OH default to unknown.   '
             f'Analysis: {HANDLE}',
             fontsize=7, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


# =========================================================================
# Figure 4: top operators per state (3-panel split)
# =========================================================================
def fig4_operators():
    out = 'appalachia_operators.png'
    fig = plt.figure(figsize=(15, 9), dpi=220, facecolor=PAPER)

    fig.text(0.04, 0.95,
             'Who holds the dark inventory?',
             fontsize=20, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.04, 0.91,
             'Top operators by basin-clipped well count, after dropping '
             'historic WPA placeholders and unknown-operator buckets. Dark '
             'share split shown in the bar fill.',
             fontsize=11, color=MUTED, fontfamily='sans-serif')

    def panel(ax, ops_list, lit_color, panel_title):
        ops = [o for o in ops_list if _real_op(o['op'])][:10]
        if not ops:
            ax.text(0.5, 0.5, 'No real operators after filtering',
                    ha='center', va='center', transform=ax.transAxes,
                    color=MUTED, fontsize=10)
            return
        df_ops = pd.DataFrame(ops)
        df_ops = df_ops.sort_values('total')

        labels = df_ops['op'].astype(str).str[:30].tolist()
        totals = df_ops['total'].tolist()
        darks  = df_ops['dark'].tolist()
        lits   = [t - d for t, d in zip(totals, darks)]
        pcts   = df_ops['pct_dark'].tolist()

        y = list(range(len(labels)))
        ax.barh(y, lits, color=lit_color, edgecolor='none',
                label='Lit', zorder=3, height=0.78)
        ax.barh(y, darks, left=lits, color=GHOST, edgecolor='none',
                label='Dark', zorder=3, height=0.78)
        for i, (lbl, t, p) in enumerate(zip(labels, totals, pcts)):
            ax.text(t + max(totals) * 0.015, i, f'{t:,}  ({p:.0f}%)',
                    va='center', fontsize=8.5, color=INK,
                    fontfamily='sans-serif')
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=8.5, color=INK,
                           fontfamily='sans-serif')
        ax.tick_params(axis='x', labelsize=8, colors=MUTED)
        for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
        for sp in ['left', 'bottom']:
            ax.spines[sp].set_color(INK); ax.spines[sp].set_linewidth(0.5)
        ax.set_xlim(0, max(totals) * 1.22)
        ax.set_title(panel_title, fontsize=10.5, color=INK, loc='left',
                     pad=6, fontfamily='sans-serif', fontweight='bold')

    ax_pa = fig.add_axes([0.04, 0.13, 0.28, 0.72])
    ax_wv = fig.add_axes([0.36, 0.13, 0.28, 0.72])
    ax_oh = fig.add_axes([0.68, 0.13, 0.28, 0.72])
    panel(ax_pa, summary['top_operators_pa'], AMBER,  'PA - top in-basin operators')
    panel(ax_wv, summary['top_operators_wv'], TEAL,   'WV - top in-basin operators')
    panel(ax_oh, summary['top_operators_oh'], VIOLET, 'OH - top in-basin operators')

    fig.text(0.04, 0.04,
             'Sources: PA DEP OPERATOR field; WV DEP RESPONSIBLE_PARTY_NAME; OH DOG CO_NAME. '
             '"HISTORIC", "OPERATOR UNKNOWN", and blank-string entries excluded.   '
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
    print('all 4 figures written')
