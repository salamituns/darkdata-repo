"""
Phase 3: Anadarko basin static figures.

Four hero figures, same editorial palette as Kansas + Williston + GHGRP.
All carry `Analysis: @salamituns` attribution per the figure-attribution
rule.

Outputs (written to both repo/figures/ and salamituns.github.io/darkdata/anadarko/figures/):
  1. anadarko_basin_map.png      hero map: KS+OK wells inside basin polygon
  2. anadarko_state_gradient.png KS vs OK dark share + per-state vintage mix
  3. anadarko_vintage_split.png  vintage distribution with horizontal flag (OK)
  4. anadarko_operators.png      split top-operators view per state
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
DATA = ROOT / 'salamituns.github.io/darkdata/anadarko/data'
FIG_REPO = ROOT / 'darkdata-repo/figures'
FIG_SITE = ROOT / 'salamituns.github.io/darkdata/anadarko/figures'
STATES_SRC = ROOT / 'data/raw/census_boundaries/gz_2010_us_040_00_5m.json'

FIG_REPO.mkdir(parents=True, exist_ok=True)
FIG_SITE.mkdir(parents=True, exist_ok=True)

# ---- Editorial palette (matches Kansas + Williston + GHGRP) -------------
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
with open(DATA / 'anadarko_basin.json') as f:
    basin_gj = json.load(f)
with open(DATA / 'summary.json') as f:
    summary = json.load(f)

basin_geom = shape(basin_gj['features'][0]['geometry'])
basin_gdf = gpd.GeoDataFrame(geometry=[basin_geom], crs='EPSG:4269')
states = gpd.read_file(STATES_SRC)
ks_ok = states[states['NAME'].isin(['Kansas', 'Oklahoma'])]

VINTAGE_LABELS = {
    0: 'pre-1980',
    1: '1980s',
    2: '1990s',
    3: '2000s',
    4: '2010+',
    5: 'unknown',
}
# In wells.csv: s=0 -> KS, s=1 -> OK. Color OK amber (the horizontal-rich
# state, like ND in Williston) and KS teal (the legacy state, like MT).
STATE_LABELS = {0: 'Kansas', 1: 'Oklahoma'}
STATE_COLORS = {0: TEAL, 1: AMBER}

print(f'wells={len(wells):,}  basin_bounds={basin_geom.bounds}')


# Operator filtering: drop placeholder rows (OTC/OCC NOT ASSIGNED, blank, etc.)
def _real_op(op):
    if op is None or pd.isna(op):
        return False
    s = str(op).strip()
    if not s:
        return False
    if 'NOT ASSIGNED' in s.upper():
        return False
    return True


# =========================================================================
# Figure 1: basin hero map
# =========================================================================
def fig1_basin_map():
    out = 'anadarko_basin_map.png'
    WEST, SOUTH, EAST, NORTH = basin_geom.bounds
    WEST -= 0.4; EAST += 0.4; SOUTH -= 0.3; NORTH += 0.3

    fig = plt.figure(figsize=(14, 10.6), dpi=220, facecolor=PAPER)
    ax = fig.add_axes([0.02, 0.30, 0.96, 0.60])
    ax.set_facecolor(PAPER)

    ks_ok.plot(ax=ax, color=FAINT, edgecolor=INK, linewidth=0.35, zorder=1)
    basin_gdf.plot(ax=ax, facecolor='none', edgecolor=INK,
                   linewidth=1.6, linestyle='-', zorder=2)

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

    # State labels (KS north, OK south)
    ax.text(-99.5, 38.7, 'KANSAS', fontsize=13, color=INK,
            fontfamily='sans-serif', fontweight='bold', alpha=0.45,
            ha='center', zorder=9)
    ax.text(-99.5, 35.4, 'OKLAHOMA', fontsize=13, color=INK,
            fontfamily='sans-serif', fontweight='bold', alpha=0.45,
            ha='center', zorder=9)

    # US locator inset
    ax_us = fig.add_axes([0.83, 0.78, 0.14, 0.09])
    ax_us.set_facecolor(PAPER)
    conus = states[~states['NAME'].isin(
        ['Alaska', 'Hawaii', 'Puerto Rico', 'District of Columbia'])]
    conus.plot(ax=ax_us, facecolor=FAINT, edgecolor=INK,
               linewidth=0.25, alpha=0.9)
    ks_ok.plot(ax=ax_us, facecolor=CLAY, edgecolor=INK, linewidth=0.35)
    basin_gdf.plot(ax=ax_us, facecolor='none', edgecolor=INK, linewidth=0.6)
    ax_us.set_xticks([]); ax_us.set_yticks([])
    for sp in ax_us.spines.values(): sp.set_visible(False)
    ax_us.text(0.5, -0.18, 'ANADARKO BASIN', transform=ax_us.transAxes,
               ha='center', va='top', fontsize=7.5, color=INK,
               fontfamily='sans-serif', fontweight='bold')

    # City anchors
    cities = [
        ('Liberal',     -100.92, 37.04),
        ('Dodge City',  -100.02, 37.75),
        ('Hugoton',     -101.34, 37.18),
        ('Woodward OK', -99.40,  36.43),
        ('Elk City',    -99.41,  35.41),
        ('Weatherford', -98.71,  35.53),
        ('Watonga',     -98.41,  35.86),
        ('Calumet',     -98.12,  35.58),
        ('Anadarko',    -98.24,  35.07),
        ('Oklahoma City', -97.51, 35.47),
    ]
    for name, lon, lat in cities:
        ax.scatter([lon], [lat], s=24, facecolor=PAPER,
                   edgecolor=INK, lw=0.9, zorder=8, marker='s')
        ax.text(lon + 0.10, lat + 0.06, name, fontsize=8.4, color=INK,
                fontfamily='sans-serif', fontweight='medium',
                ha='left', va='bottom', zorder=9)

    # Play labels
    ax.text(-101.0, 37.4, 'Hugoton\nEmbayment', fontsize=9.5, color=INK,
            alpha=0.6, fontfamily='serif', fontstyle='italic',
            ha='center', va='center', zorder=7)
    ax.text(-98.6, 35.8, 'SCOOP / STACK\n(Cana Woodford)', fontsize=9.5,
            color=INK, alpha=0.6, fontfamily='serif', fontstyle='italic',
            ha='center', va='center', zorder=7)

    ax.set_xlim(WEST, EAST); ax.set_ylim(SOUTH, NORTH)
    ax.set_aspect(1.25)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)

    fig.text(0.035, 0.955,
             'A basin geology drew, sliced by a state line.',
             fontsize=22, color=INK, fontfamily='serif', fontweight='medium')
    n_total = summary['total_wells']
    pct_dark = summary['pct_dark']
    fig.text(0.035, 0.918,
             f'{n_total:,} wells drilled inside the USGS Anadarko Basin '
             f'Province. {pct_dark}% have no public digital log. The 2010+ '
             'SCOOP and STACK horizontal campaigns light up the south half. '
             'Everything older is dark.',
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

    # Companion inset: per-state dark share
    ax2 = fig.add_axes([0.52, 0.07, 0.42, 0.18])
    ax2.set_facecolor(PAPER)
    states_rows = ['Kansas', 'Oklahoma']
    colors = [TEAL, AMBER]
    by_state = summary['by_state']
    pcts = [by_state['KS']['pct_dark'], by_state['OK']['pct_dark']]
    totals = [by_state['KS']['total'], by_state['OK']['total']]
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
             'Different proxies, similar verdicts. KS lights a well only if '
             'the KGS public LAS archive carries it. OK lights a well only '
             'if its OCC completion record marks an open-hole log filed.',
             transform=ax2.transAxes, fontsize=8.5, color=MUTED,
             fontfamily='sans-serif', ha='left', va='top', wrap=True)

    fig.text(0.035, 0.006,
             'Sources: OK OCC RBDMS_WELLS shapefile (455K OK wells) + RBDMS completions '
             '(modern + legacy XLSX). KGS bulk well export (476K KS wells) + KGS '
             'public LAS archive (~24K logs). USGS GMC Anadarko Basin Province '
             '(MapUnitPolys dissolve). Wells joined in EPSG:4269.   '
             f'Analysis: {HANDLE}',
             fontsize=7, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


# =========================================================================
# Figure 2: state-line gradient (KS vs OK detailed split)
# =========================================================================
def fig2_state_gradient():
    out = 'anadarko_state_gradient.png'
    fig = plt.figure(figsize=(13, 8), dpi=220, facecolor=PAPER)

    fig.text(0.04, 0.94,
             'Two regulators, one petroleum province.',
             fontsize=20, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.04, 0.895,
             'Kansas catalogs digital logs only when its survey can scan a '
             'paper file. Oklahoma flags an open-hole log on the completion '
             'record itself. Same basin, different filing protocols, '
             'similar dark verdict.',
             fontsize=11, color=MUTED, fontfamily='sans-serif')

    ax1 = fig.add_axes([0.07, 0.20, 0.36, 0.56])
    ax1.set_facecolor(PAPER)
    by_state = summary['by_state']
    states_ = ['KS', 'OK']
    dark_n = [by_state[s]['dark'] for s in states_]
    lit_n  = [by_state[s]['total'] - by_state[s]['dark'] for s in states_]
    totals = [by_state[s]['total'] for s in states_]
    ax1.bar(states_, lit_n, color=VIOLET, edgecolor='none',
            label='Lit (public digital log)', zorder=3)
    ax1.bar(states_, dark_n, bottom=lit_n, color=GHOST, edgecolor='none',
            label='Dark', zorder=3)
    for i, (s, t) in enumerate(zip(states_, totals)):
        ax1.text(i, t + max(totals) * 0.015, f'{t:,}',
                 ha='center', fontsize=10, color=INK, fontweight='bold',
                 fontfamily='sans-serif')
        pct = by_state[s]['pct_dark']
        ax1.text(i, lit_n[i] + dark_n[i] / 2, f'{pct:.1f}%\ndark',
                 ha='center', va='center', fontsize=11, color=INK,
                 fontweight='bold', fontfamily='sans-serif')
    ax1.set_ylabel('Wells', fontsize=9.5, color=MUTED,
                   fontfamily='sans-serif')
    ax1.set_xticklabels(['Kansas', 'Oklahoma'],
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

    # Right panel: vintage distribution by state
    ax2 = fig.add_axes([0.52, 0.20, 0.44, 0.56])
    ax2.set_facecolor(PAPER)
    buckets = [0, 1, 2, 3, 4, 5]
    labels = [VINTAGE_LABELS[b] for b in buckets]
    ks_counts = [int(((wells['s'] == 0) & (wells['v'] == b)).sum()) for b in buckets]
    ok_counts = [int(((wells['s'] == 1) & (wells['v'] == b)).sum()) for b in buckets]
    ks_tot = sum(ks_counts); ok_tot = sum(ok_counts)
    ks_pct = [100 * n / ks_tot for n in ks_counts]
    ok_pct = [100 * n / ok_tot for n in ok_counts]
    x = list(range(len(buckets)))
    w = 0.38
    ax2.bar([xi - w/2 for xi in x], ks_pct, width=w, color=TEAL,
            edgecolor='none', label=f'KS ({ks_tot:,})', zorder=3)
    ax2.bar([xi + w/2 for xi in x], ok_pct, width=w, color=AMBER,
            edgecolor='none', label=f'OK ({ok_tot:,})', zorder=3)
    ymax = max(max(ks_pct), max(ok_pct))
    grid = [10, 20, 30, 40, 50, 60, 70]
    for y in grid:
        if y <= ymax + 5:
            ax2.axhline(y, color=INK, lw=0.3, alpha=0.12, zorder=1)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=9, color=INK,
                        fontfamily='sans-serif')
    yticks = [g for g in [0] + grid if g <= ymax + 5]
    ax2.set_yticks(yticks)
    ax2.set_yticklabels([f'{g}%' if g else '0' for g in yticks],
                        fontsize=8, color=MUTED, fontfamily='sans-serif')
    for sp in ['top', 'right']: ax2.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax2.spines[sp].set_color(INK); ax2.spines[sp].set_linewidth(0.5)
    ax2.legend(loc='upper right', frameon=False, fontsize=9, labelcolor=INK)
    ax2.set_title('Spud-vintage mix by state (% of in-basin wells)',
                  fontsize=10, color=INK, fontfamily='sans-serif',
                  loc='left', pad=6)

    fig.text(0.04, 0.08,
             'KS: a pre-1980 vertical-conventional mountain. The Hugoton gas '
             'field and the Anadarko Shelf were drilled before digitization. '
             'OK: the only state in this series where the 2010+ bar is '
             'genuinely visible, courtesy of SCOOP and STACK.',
             fontsize=10, color=MUTED, fontfamily='sans-serif')

    fig.text(0.04, 0.012,
             'Sources: OCC RBDMS (OK), KGS bulk well export (KS), basin-clipped to '
             'USGS GMC Anadarko Basin Province polygon.   '
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
    out = 'anadarko_vintage_split.png'
    fig = plt.figure(figsize=(13, 7.5), dpi=220, facecolor=PAPER)

    fig.text(0.04, 0.94,
             'When did Oklahoma go horizontal? 2014.',
             fontsize=20, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.04, 0.895,
             'The SCOOP and STACK plays put a 30,000-well horizontal campaign '
             'inside the basin, all logged digitally. Every other vintage '
             'class is overwhelmingly dark.',
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
            'horz_ok': int(((sub['h'] == 1) & (sub['s'] == 1)).sum()),
        })
    df = pd.DataFrame(rows)
    df['lit'] = df['total'] - df['dark']

    x = list(range(len(buckets)))
    w = 0.78
    ax.bar(x, df['dark'], width=w, color=GHOST, edgecolor='none',
           label='Dark (no log)', zorder=3)
    ax.bar(x, df['lit'], width=w, bottom=df['dark'], color=VIOLET,
           edgecolor='none', label='Lit (public log)', zorder=3)
    ax.bar(x, df['horz_ok'], width=w * 0.55, bottom=0,
           facecolor='none', edgecolor=CLAY, linewidth=2.0,
           label='of which OK horizontal', zorder=4)

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

    fig.text(0.04, 0.07,
             f'Pre-1980 alone holds {df.iloc[0]["total"]:,} wells, the basin’s '
             'biggest vintage. Almost none of them carry a public digital log. '
             f'The 2010+ bar is smaller ({df.iloc[4]["total"]:,}) but its lit '
             'share is the only one that gets above the floor.',
             fontsize=10, color=MUTED, fontfamily='sans-serif')

    fig.text(0.04, 0.012,
             'Sources: OCC RBDMS + completions (OK), KGS bulk well export (KS), '
             'basin-clipped.   Vintage = spud year if known, else completion year.   '
             f'Analysis: {HANDLE}',
             fontsize=7, color=MUTED, fontfamily='sans-serif')

    for path in (FIG_REPO / out, FIG_SITE / out):
        fig.savefig(path, facecolor=PAPER, dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {out}')


# =========================================================================
# Figure 4: top operators, split by state
# =========================================================================
def fig4_operators():
    out = 'anadarko_operators.png'
    fig = plt.figure(figsize=(14, 9), dpi=220, facecolor=PAPER)

    fig.text(0.04, 0.95,
             'Who holds the dark inventory?',
             fontsize=20, color=INK, fontfamily='serif', fontweight='medium')
    fig.text(0.04, 0.91,
             'Top operators by basin-clipped well count, after dropping the '
             'OCC unassigned-well bucket and unattributed KS legacy headers. '
             'Dark share split shown in the bar fill.',
             fontsize=11, color=MUTED, fontfamily='sans-serif')

    def panel(ax, ops_list, title_color, panel_title):
        # Filter out placeholder operators
        ops = [o for o in ops_list if _real_op(o['op'])][:12]
        if not ops:
            ax.text(0.5, 0.5, 'No real operators after filtering',
                    ha='center', va='center', transform=ax.transAxes,
                    color=MUTED, fontsize=10)
            return
        df_ops = pd.DataFrame(ops)
        df_ops = df_ops.sort_values('total')

        labels = df_ops['op'].tolist()
        totals = df_ops['total'].tolist()
        darks  = df_ops['dark'].tolist()
        lits   = [t - d for t, d in zip(totals, darks)]
        pcts   = df_ops['pct_dark'].tolist()

        y = list(range(len(labels)))
        ax.barh(y, lits, color=title_color, edgecolor='none',
                label='Lit', zorder=3, height=0.78)
        ax.barh(y, darks, left=lits, color=GHOST, edgecolor='none',
                label='Dark', zorder=3, height=0.78)
        for i, (lbl, t, p) in enumerate(zip(labels, totals, pcts)):
            ax.text(t + max(totals) * 0.015, i, f'{t:,}  ({p:.0f}%)',
                    va='center', fontsize=8.5, color=INK,
                    fontfamily='sans-serif')
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=9, color=INK,
                           fontfamily='sans-serif')
        ax.tick_params(axis='x', labelsize=8, colors=MUTED)
        for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
        for sp in ['left', 'bottom']:
            ax.spines[sp].set_color(INK); ax.spines[sp].set_linewidth(0.5)
        ax.set_xlim(0, max(totals) * 1.22)
        ax.set_title(panel_title, fontsize=11, color=INK, loc='left',
                     pad=6, fontfamily='sans-serif', fontweight='bold')

    ax_ok = fig.add_axes([0.34, 0.13, 0.32, 0.72])
    ax_ks = fig.add_axes([0.05, 0.13, 0.27, 0.72])
    panel(ax_ks, summary['top_operators_ks'], TEAL, 'Kansas — top in-basin operators')
    panel(ax_ok, summary['top_operators_ok'], AMBER, 'Oklahoma — top in-basin operators')

    # Legend
    handles = [
        Line2D([0],[0], marker='s', color='w', markerfacecolor=AMBER,
               markersize=10, label='Lit (OK)'),
        Line2D([0],[0], marker='s', color='w', markerfacecolor=TEAL,
               markersize=10, label='Lit (KS)'),
        Line2D([0],[0], marker='s', color='w', markerfacecolor=GHOST,
               markersize=10, label='Dark'),
    ]
    fig.legend(handles=handles, loc='upper right', frameon=False,
               bbox_to_anchor=(0.97, 0.92),
               fontsize=10, labelcolor=INK)

    # Side commentary
    fig.text(0.69, 0.83,
             'The dark inventory clusters with two operator types:',
             fontsize=10, color=INK, fontfamily='sans-serif',
             fontweight='bold')
    fig.text(0.69, 0.66,
             '1. Plug-and-abandon majors with deep vintage exposure '
             '(Oxy, ConocoPhillips, Cities Service, Chesapeake) carry '
             'thousands of dark wells per name.\n\n'
             '2. Mid-size legacy operators (Citation, Diversified, '
             'Scout) have dark-rates in the 60-80% range — wells acquired '
             'as packages, original log filings lost in transfer.',
             fontsize=9.5, color=MUTED, fontfamily='sans-serif',
             va='top', wrap=True)
    fig.text(0.69, 0.34,
             'Modern operators built on horizontals (SandRidge, Devon, '
             'Ovintiv) post much lower dark rates — a structural artifact '
             'of when they drilled, not how careful they were with paper.',
             fontsize=9.5, color=MUTED, fontfamily='sans-serif',
             va='top', wrap=True)

    fig.text(0.04, 0.04,
             'Sources: OCC RBDMS_WELLS + completions (OK operator field), '
             'KGS bulk well export (KS Original Operator field). '
             '“OTC/OCC NOT ASSIGNED” (67,025 OK wells) and unattributed KS '
             'rows excluded.   '
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
