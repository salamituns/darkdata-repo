"""
Phase B addendum: render a 1200x630 Open Graph / Twitter social card.

The existing primer_conus_hero.png is irregular aspect ratio and gets
letterboxed or cropped on LinkedIn / Twitter previews. This script
generates a dedicated social card sized to the OG spec (1200x630 = 1.91:1).

Layout: left two-thirds is the CONUS basin map; right third is title +
headline numbers + the dark-data thesis in a small-stack of stats.
"""
import warnings; warnings.filterwarnings('ignore')
import json
from pathlib import Path
import geopandas as gpd
from shapely.geometry import shape
import matplotlib.pyplot as plt

ROOT = Path('/Users/olatunde/CoWorker/Geoworks')
DATA = ROOT / 'salamituns.github.io/darkdata/primer_data'
FIG_REPO = ROOT / 'darkdata-repo/figures'
FIG_SITE = DATA / 'figures'
FIG_REPO.mkdir(parents=True, exist_ok=True)
FIG_SITE.mkdir(parents=True, exist_ok=True)

PAPER  = '#F6F3EB'
INK    = '#0E0E0E'
ACCENT = '#A23B2A'
MUTED  = '#7A7368'
FAINT  = '#EDE6D4'

with open(DATA/'basins.json') as f:
    basins = json.load(f)
conus = gpd.read_file(DATA/'conus_states.json')

DISPLAY_ORDER = ['kansas', 'permian', 'williston', 'anadarko', 'appalachia', 'eagle_ford']
basin_by_id = {f['properties']['id']: f for f in basins['features']}

# OG card is 1200x630 inches at 100 DPI = 12 x 6.3 inches.
# Use 200 DPI for crisp rendering: 6 x 3.15 inches at 200 DPI.
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=PAPER)

# Left: CONUS map (~62% of width)
ax = fig.add_axes([0.02, 0.06, 0.62, 0.86])
ax.set_facecolor(PAPER)
conus.plot(ax=ax, facecolor=FAINT, edgecolor=INK, linewidth=0.4, zorder=1)

# Basin polygons
for f in basins['features']:
    color = f['properties']['color']
    geom = shape(f['geometry'])
    gpd.GeoDataFrame(geometry=[geom], crs='EPSG:4269').plot(
        ax=ax, facecolor=color, edgecolor=INK, linewidth=0.6,
        alpha=0.70, zorder=3,
    )

LABEL_ANCHORS = {
    'kansas':     (-99.0, 37.5),
    'permian':    (-103.5, 31.0),
    'williston':  (-103.5, 47.7),
    'anadarko':   (-98.0, 35.5),
    'appalachia': (-78.0, 39.5),
    'eagle_ford': (-99.0, 28.4),
}

for f in basins['features']:
    bid = f['properties']['id']
    short = f['properties']['short']
    if bid not in LABEL_ANCHORS:
        continue
    lon, lat = LABEL_ANCHORS[bid]
    ax.text(lon, lat, short,
            fontsize=10, color=INK, fontfamily='sans-serif',
            fontweight='bold', ha='center', va='center', zorder=8,
            bbox=dict(boxstyle='round,pad=0.32',
                      facecolor=PAPER, edgecolor=INK, linewidth=0.6,
                      alpha=0.95))

ax.set_xlim(-126, -66)
ax.set_ylim(24, 50)
ax.set_aspect(1.30)
ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values(): sp.set_visible(False)

# Right: title + numbers
fig.text(0.665, 0.86, 'THE BASINS  ·  A DARK-DATA FIELD GUIDE',
         fontsize=10, color=ACCENT, fontfamily='sans-serif',
         fontweight='bold')
fig.text(0.665, 0.69,
         'Six basins drilled\nthe United States.',
         fontsize=32, color=INK, fontfamily='serif',
         fontweight='medium', linespacing=1.05)
fig.text(0.665, 0.585,
         'Where the wells are. What rock they target.\n'
         'When they were drilled. One US map, six\nlinks to the full dark-data series.',
         fontsize=12, color=MUTED, fontfamily='sans-serif',
         linespacing=1.4)

# Stat strip: 4 numbers, 2-column grid
def stat(x, y, num, label, accent=False):
    fig.text(x, y, num, fontsize=22, color=ACCENT if accent else INK,
             fontfamily='serif', fontweight='medium',
             font='serif')
    fig.text(x, y - 0.05, label, fontsize=9, color=MUTED,
             fontfamily='sans-serif',
             fontweight='medium')

stat(0.665, 0.36, '6',         'BASINS')
stat(0.78,  0.36, '1.92M',     'WELLS MAPPED', accent=True)
stat(0.665, 0.23, '89.1%',     'DARK MEASURED')
stat(0.78,  0.23, '165',       'YEARS SINCE DRAKE', accent=True)

# Footer
fig.text(0.665, 0.07,
         'salamituns.github.io / darkdata',
         fontsize=10, color=INK, fontfamily='sans-serif',
         fontweight='medium')
fig.text(0.665, 0.04,
         'Analysis: @salamituns  ·  deck.gl + maplibre',
         fontsize=8, color=MUTED, fontfamily='sans-serif')

# Save at exactly 1200x630 (12x6.3 in @ 100 DPI). Use 200 dpi for sharper
# render; matplotlib will scale image dimensions accordingly. Specify
# the exact pixel size via dpi.
out = 'primer_social_card.png'
for path in (FIG_REPO / out, FIG_SITE / out):
    fig.savefig(path, facecolor=PAPER, dpi=100, bbox_inches=None,
                pad_inches=0)
plt.close(fig)
print(f'wrote {out} at 1200x630')
