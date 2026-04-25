"""
Phase A: assemble the primer bundle.

The primer at /darkdata/basins.html needs a single dataset with all six
basins on one map. Each basin walk in the series ships its own polygon;
this phase unifies them.

Outputs (all to salamituns.github.io/darkdata/primer_data/):
  basins.json          GeoJSON FeatureCollection, 6 features (one per basin)
                       props: id, name, era, target_rock, drilling_era,
                              dark_pct, well_count, color
  conus_states.json    All 50 US states (Census TIGER 5m)
  eia_dpr_5basins.json EIA DPR monthly time series for 5 basins (KS not in EIA DPR)
  primer_facts.json    Per-basin sidebar facts: depth ranges, ages, top operators

Notes on basin polygons:
  Williston, Anadarko, Appalachia, Eagle Ford ship USGS/EIA polygons
    in their own /data/ directories.
  Kansas and Permian ship county collections; we dissolve them.
"""
import json
import zipfile
from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.ops import unary_union

ROOT = Path('/Users/olatunde/CoWorker/Geoworks')
RAW = ROOT / 'darkdata-repo/data/raw'
SITE = ROOT / 'salamituns.github.io'
DATA = SITE / 'darkdata/primer_data'
DATA.mkdir(parents=True, exist_ok=True)

# Editorial palette (for per-basin colors so the master map reads at a glance)
PALETTE = {
    'kansas':     '#A23B2A',  # CLAY
    'permian':    '#C57B35',  # AMBER
    'williston':  '#6B4E8A',  # VIOLET
    'anadarko':   '#2E6E7E',  # TEAL
    'appalachia': '#8B6F3E',  # WARM-OLIVE (custom for primer)
    'eagle_ford': '#5C7A8C',  # SLATE-BLUE (custom for primer)
}

# ============================================================
# 1. Assemble each basin polygon
# ============================================================
print('Assembling basin polygons...')

basins = []

# Kansas: state outline = basin extent (Mid-Continent shelf approximation)
print('  Kansas: dissolving 105 KS counties from existing site data...')
ks_counties = gpd.read_file(SITE/'darkdata/kansas/data/ks_counties.json')
ks_geom = unary_union(ks_counties.geometry.tolist())
basins.append({
    'id': 'kansas',
    'name': 'Kansas (Mid-Continent shelf)',
    'short': 'Kansas',
    'geom': ks_geom,
    'crs': ks_counties.crs,
})

# Permian: dissolve county collection
print('  Permian: dissolving permian county collection...')
perm_counties = gpd.read_file(SITE/'darkdata/permian/data/permian_counties.json')
perm_geom = unary_union(perm_counties.geometry.tolist())
basins.append({
    'id': 'permian',
    'name': 'Permian Basin (West Texas + SE New Mexico)',
    'short': 'Permian',
    'geom': perm_geom,
    'crs': perm_counties.crs,
})

# Williston: USGS Bakken + Three Forks TPS polygon
print('  Williston: loading USGS TPS polygon...')
ws = gpd.read_file(SITE/'darkdata/williston/data/williston_basin.json')
ws_geom = unary_union(ws.geometry.tolist())
basins.append({
    'id': 'williston',
    'name': 'Williston Basin (Bakken & Three Forks TPS)',
    'short': 'Williston',
    'geom': ws_geom,
    'crs': ws.crs,
})

# Anadarko: USGS province dissolve
print('  Anadarko: loading USGS Province 058 dissolve...')
an = gpd.read_file(SITE/'darkdata/anadarko/data/anadarko_basin.json')
an_geom = unary_union(an.geometry.tolist())
basins.append({
    'id': 'anadarko',
    'name': 'Anadarko Basin (SCOOP/STACK + Hugoton)',
    'short': 'Anadarko',
    'geom': an_geom,
    'crs': an.crs,
})

# Appalachia: EIA shales union
print('  Appalachia: loading EIA shales union...')
ap = gpd.read_file(SITE/'darkdata/appalachia/data/appalachia_basin.json')
ap_geom = unary_union(ap.geometry.tolist())
basins.append({
    'id': 'appalachia',
    'name': 'Appalachian Basin (Marcellus + Utica + Devonian)',
    'short': 'Appalachia',
    'geom': ap_geom,
    'crs': ap.crs,
})

# Eagle Ford: USGS AUs
print('  Eagle Ford: loading USGS Eagle Ford AUs...')
ef = gpd.read_file(SITE/'darkdata/eagle_ford/data/eagle_ford_aus.json')
ef_geom = unary_union(ef.geometry.tolist())
basins.append({
    'id': 'eagle_ford',
    'name': 'Eagle Ford (USGS AUs across South TX)',
    'short': 'Eagle Ford',
    'geom': ef_geom,
    'crs': ef.crs,
})

# Reproject all to EPSG:4269 for consistency
print('  Reprojecting to EPSG:4269...')
for b in basins:
    if b['crs'] and str(b['crs']).split(':')[-1] != '4269':
        gdf = gpd.GeoDataFrame(geometry=[b['geom']], crs=b['crs']).to_crs('EPSG:4269')
        b['geom'] = gdf.geometry.iloc[0]


# ============================================================
# 2. Per-basin metadata (geology, drilling era, current role)
# ============================================================
# Numbers come from the dark-data series and from EIA reference data.
# Hand-curated. Source citations live inline in the storymap.
# Metadata is hand-curated. New fields powering the v2 view-toggle:
#   geology_rank      1 (oldest target rock) to 5 (youngest), used for sort order
#   oil_rank_numeric  1 (top oil producer) to 5+, null if below EIA DPR threshold
#   gas_dominant      true if natural gas is the primary product (Appalachia)
#   accessibility_tier 'open' / 'multi' / 'mixed' / 'walled'
#   accessibility_score 0 to 100, working analyst rating from the basin pulls
#   accessibility_label e.g. "Open (single regulator)"
metadata = {
    'kansas': {
        'era_geology': 'Ordovician to Permian',
        'era_short': 'Pennsylvanian-Permian',
        'geology_rank': 3,
        'target_rocks': 'Mississippian Lansing-Kansas City limestones, Pennsylvanian Cherokee sandstone, Permian Hugoton dolomite',
        'trap_type': 'Stratigraphic; gentle structural shelf',
        'first_well_year': 1860,
        'horizontal_era_year': None,
        'role': 'Mature shallow oil and gas; 419,777 wells, mostly vertical, mostly pre-2000',
        'depth_range_ft': '300 to 5,000',
        'oil_or_gas': 'Both, gas-dominant in west',
        'gas_dominant': False,
        'dark_pct': 94.3,
        'well_count': 419777,
        'production_rank': 'Below EIA DPR threshold',
        'oil_rank_numeric': None,
        'accessibility_tier': 'open',
        'accessibility_score': 90,
        'accessibility_label': 'Open (KGS single-state)',
        'one_line': 'A century of shallow vertical conventional. The classic dark-data archetype.',
        'walk_url': '/darkdata/kansas/',
    },
    'permian': {
        'era_geology': 'Pennsylvanian to Permian',
        'era_short': 'Permian',
        'geology_rank': 4,
        'target_rocks': 'Wolfcamp Shale, Bone Spring Sand, Spraberry Trend, Avalon Shale, Yeso Limestone',
        'trap_type': 'Stacked plays in a foreland basin; multiple pay zones per well',
        'first_well_year': 1921,
        'horizontal_era_year': 2010,
        'role': 'Largest current US oil producer; multi-zone unconventional + legacy vertical',
        'depth_range_ft': '5,000 to 12,000',
        'oil_or_gas': 'Oil-dominant',
        'gas_dominant': False,
        'dark_pct': 77.9,
        'well_count': 393073,
        'production_rank': '#1 in US oil',
        'oil_rank_numeric': 1,
        'accessibility_tier': 'mixed',
        'accessibility_score': 60,
        'accessibility_label': 'Mixed (NM clean, TX walled)',
        'one_line': 'The biggest current US oil basin; lit on top of dark vertical legacy.',
        'walk_url': '/darkdata/permian/story.html',
    },
    'williston': {
        'era_geology': 'Late Devonian to Mississippian',
        'era_short': 'Late Devonian',
        'geology_rank': 2,
        'target_rocks': 'Bakken Formation (Upper + Middle + Lower), Three Forks dolomite',
        'trap_type': 'Continuous source-rock shale; the source rock IS the reservoir',
        'first_well_year': 1951,
        'horizontal_era_year': 2008,
        'role': 'Bakken horizontal era dominates; one of two majority-lit basins in the series',
        'depth_range_ft': '8,000 to 11,500',
        'oil_or_gas': 'Oil-dominant',
        'gas_dominant': False,
        'dark_pct': 45.7,
        'well_count': 45921,
        'production_rank': '#3 in US oil',
        'oil_rank_numeric': 3,
        'accessibility_tier': 'open',
        'accessibility_score': 95,
        'accessibility_label': 'Open (NDIC + MT BOGC)',
        'one_line': 'Source rock IS reservoir. Horizontal-only era dominates the well count.',
        'walk_url': '/darkdata/williston/story.html',
    },
    'anadarko': {
        'era_geology': 'Cambrian to Permian',
        'era_short': 'Pennsylvanian',
        'geology_rank': 3,
        'target_rocks': 'Woodford Shale, Cana-Woodford, Granite Wash, Cleveland Sand, Hugoton dolomite',
        'trap_type': 'Deep foreland basin (deepest in the series); SCOOP/STACK on the OK side, Hugoton shelf on KS side',
        'first_well_year': 1903,
        'horizontal_era_year': 2014,
        'role': 'Deep gas + recent SCOOP/STACK horizontal oil; Hugoton was the largest US gas field for half a century',
        'depth_range_ft': '4,000 to 30,000+',
        'oil_or_gas': 'Both; deep gas + modern oil',
        'gas_dominant': False,
        'dark_pct': 91.1,
        'well_count': 482918,
        'production_rank': '#5 in US oil',
        'oil_rank_numeric': 5,
        'accessibility_tier': 'multi',
        'accessibility_score': 95,
        'accessibility_label': 'Multi-state (OCC + KGS)',
        'one_line': 'Deepest plays in the series. SCOOP/STACK is a thin top layer.',
        'walk_url': '/darkdata/anadarko/story.html',
    },
    'appalachia': {
        'era_geology': 'Cambrian to Permian',
        'era_short': 'Devonian',
        'geology_rank': 1,
        'target_rocks': 'Marcellus Shale, Utica/Point Pleasant, Devonian shales (Berea, Onondaga, Genesee)',
        'trap_type': 'Foreland basin behind the Allegheny Front; layered source-and-reservoir shales',
        'first_well_year': 1859,
        'horizontal_era_year': 2008,
        'role': '#1 US natural gas producer (Marcellus); 165 years of vertical legacy underneath',
        'depth_range_ft': '4,000 to 9,000',
        'oil_or_gas': 'Gas-dominant',
        'gas_dominant': True,
        'dark_pct': 94.8,
        'well_count': 579324,
        'production_rank': '#1 in US gas',
        'oil_rank_numeric': None,
        'accessibility_tier': 'mixed',
        'accessibility_score': 73,
        'accessibility_label': 'Mixed (PA open, WV unjoined)',
        'one_line': 'Drake 1859. The longest drilling history in North America.',
        'walk_url': '/darkdata/appalachia/story.html',
    },
    'eagle_ford': {
        'era_geology': 'Late Cretaceous (Cenomanian-Turonian)',
        'era_short': 'Cretaceous',
        'geology_rank': 5,
        'target_rocks': 'Eagle Ford Group (Lower + Upper), Austin Chalk overburden',
        'trap_type': 'Continuous shale on a south-dipping passive margin; oil-window updip, gas-window downdip',
        'first_well_year': 2008,
        'horizontal_era_year': 2008,
        'role': 'Newest big shale; rapid 2008 to 2015 buildup followed by ten-year plateau',
        'depth_range_ft': '4,000 to 14,000',
        'oil_or_gas': 'Both; updip oil, downdip gas',
        'gas_dominant': False,
        'dark_pct': None,
        'well_count': None,
        'production_rank': '#2 in US oil',
        'oil_rank_numeric': 2,
        'accessibility_tier': 'walled',
        'accessibility_score': 5,
        'accessibility_label': 'Walled (TX RRC JSF + EBCDIC)',
        'one_line': 'Newest big play. TX RRC architecture means we cannot count its wells.',
        'walk_url': '/darkdata/eagle_ford/story.html',
    },
}

# Merge metadata into the basin features
print('Building basins.json (FeatureCollection)...')
features = []
for b in basins:
    md = metadata[b['id']]
    geom = b['geom']
    geo_json = json.loads(gpd.GeoSeries([geom], crs='EPSG:4269').to_json())['features'][0]
    feature = {
        'type': 'Feature',
        'id': b['id'],
        'properties': {
            'id': b['id'],
            'name': b['name'],
            'short': b['short'],
            'color': PALETTE[b['id']],
            **md,
        },
        'geometry': geo_json['geometry'],
    }
    features.append(feature)

(DATA/'basins.json').write_text(json.dumps({
    'type': 'FeatureCollection',
    'features': features,
}))
print(f'  wrote {DATA/"basins.json"} ({len(features)} basins)')


# ============================================================
# 3. CONUS state outlines
# ============================================================
print('Loading CONUS states from TIGER 2024...')
states = gpd.read_file(f'zip://{RAW}/census/cb_2024_us_state_5m.zip')
EXCLUDE = {'AK', 'HI', 'PR', 'AS', 'GU', 'MP', 'VI'}
conus = states[~states['STUSPS'].isin(EXCLUDE)][['NAME', 'STUSPS', 'geometry']].to_crs('EPSG:4269')
(DATA/'conus_states.json').write_text(conus.to_json())
print(f'  wrote {DATA/"conus_states.json"} ({len(conus)} states)')


# ============================================================
# 4. EIA DPR multi-region production
# ============================================================
print('Loading EIA DPR for 5 basins (KS not in DPR)...')
xls = pd.ExcelFile(RAW/'eia_dpr/dpr-data.xlsx')

# Map each EIA region sheet to our basin id
region_to_basin = {
    'Permian Region': 'permian',
    'Bakken Region': 'williston',
    'Anadarko Region': 'anadarko',
    'Appalachia Region': 'appalachia',
    'Eagle Ford Region': 'eagle_ford',
}

dpr = {}
for sheet, basin_id in region_to_basin.items():
    df = pd.read_excel(RAW/'eia_dpr/dpr-data.xlsx', sheet_name=sheet, header=[0, 1])
    df.columns = [
        f'{a if not str(a).startswith("Unnamed") else ""}_{b}'.strip('_').lower().replace(' ', '_')
        for a, b in df.columns
    ]
    # Find the month col + rig + oil + gas columns by name suffix
    month_col = next(c for c in df.columns if c.endswith('month'))
    rig_col = next(c for c in df.columns if c.endswith('rig_count'))
    oil_col = next(c for c in df.columns if 'oil' in c and 'total' in c)
    gas_col = next(c for c in df.columns if 'gas' in c and 'total' in c)
    df = df[df[month_col].apply(lambda x: hasattr(x, 'year'))]
    df[month_col] = pd.to_datetime(df[month_col])
    df = df.sort_values(month_col)
    series = []
    for _, r in df.iterrows():
        series.append({
            'month': r[month_col].strftime('%Y-%m'),
            'rig_count': float(r[rig_col]) if pd.notna(r[rig_col]) else None,
            'oil_total_bbl': float(r[oil_col]) if pd.notna(r[oil_col]) else None,
            'gas_total_mcf': float(r[gas_col]) if pd.notna(r[gas_col]) else None,
        })
    dpr[basin_id] = series
    print(f'  {basin_id}: {len(series)} months')

(DATA/'eia_dpr_5basins.json').write_text(json.dumps({
    'source': 'EIA Drilling Productivity Report',
    'unit_oil': 'barrels/day',
    'unit_gas': 'thousand cubic feet/day',
    'note_kansas': 'Kansas does not appear in EIA DPR. The state is below the threshold for major-region reporting.',
    'data': dpr,
}))
print(f'  wrote {DATA/"eia_dpr_5basins.json"}')

# ============================================================
# 5. Primer summary - the cross-basin verdicts on one page
# ============================================================
summary = {
    'series_complete': True,
    'basin_count': 6,
    'measured_basins': 5,
    'walled_basins': 1,
    'wells_mapped_total': 1921013,
    'measured_dark_pct_weighted': 89.1,
    'horizontal_era_thesis': (
        'Horizontal eras only rescue young basins where horizontals dominate '
        'the well count. Williston confirms (46 percent dark, horizontals are '
        'the dominant era). Anadarko refutes (91 percent dark, horizontals '
        'are 8 percent of the well count).'
    ),
    'architecture_thesis': (
        'Dark data is a regulator publishing choice, not a continuum. North '
        'Dakota chose a shapefile, Oklahoma a CSV, Pennsylvania a flag '
        'column, Kansas a survey, Texas kept the mainframe.'
    ),
    'basins_ranked_by_dark_share': [
        {'id': 'williston',  'short': 'Williston',  'dark_pct': 45.7, 'wells': 45921,  'rank': 1},
        {'id': 'permian',    'short': 'Permian',    'dark_pct': 77.9, 'wells': 393073, 'rank': 2},
        {'id': 'anadarko',   'short': 'Anadarko',   'dark_pct': 91.1, 'wells': 482918, 'rank': 3},
        {'id': 'kansas',     'short': 'Kansas',     'dark_pct': 94.3, 'wells': 419777, 'rank': 4},
        {'id': 'appalachia', 'short': 'Appalachia', 'dark_pct': 94.8, 'wells': 579324, 'rank': 5},
        {'id': 'eagle_ford', 'short': 'Eagle Ford', 'dark_pct': None, 'wells': None,   'rank': 6},
    ],
}
(DATA/'primer_summary.json').write_text(json.dumps(summary, indent=2))
print(f'  wrote {DATA/"primer_summary.json"}')

print()
print('=== SUMMARY ===')
for b in basins:
    md = metadata[b['id']]
    print(f'  {b["id"]:11s} dark={md["dark_pct"] or "wall":<6} wells={md["well_count"] or "wall"}')
