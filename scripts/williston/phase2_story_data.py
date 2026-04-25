"""
Phase 2: build browser-ready Williston data bundles.

Inputs:
  data/raw/ndic/ogd_wells/OGD_Wells.shp                    (43,445 ND wells)
  data/raw/ndic/ogd_horizontals/OGD_Horizontals.shp        (22,258 unique horizontal APIs)
  data/raw/mt_bogc/wells/wells.shp                         (41,943 MT wells)
  data/raw/usgs_bakken/bundle/BakkenAUs/BakkenAUs.shp      (9 Bakken AUs)
  data/raw/usgs_bakken/bundle/ThreeForksAUs/ThreeForksAUs.shp (7 Three Forks AUs)

Classification rules (v1, documented on the StoryMap):

  Vintage bucket v (shared with Kansas/Permian):
    0 pre-1980   1 1980s   2 1990s   3 2000s   4 2010+   5 unknown

  State flag s:
    0 ND   1 MT

  Horizontal flag h (ND only; MT leaves 0):
    1 if ND well API appears in OGD_Horizontals.shp unique-API set
    MT BOGC shapefile carries no horizontal indicator in the shipped schema,
    so MT horizontals are not flagged. This is documented on the StoryMap.

  Dark flag d:
    d = 1 if (v in {0, 1, 2, 5}) AND h == 0
    i.e., dark = spud/completed pre-2000 and not a ND horizontal.
    Lit = post-2000 entry in regulator's digital era, OR horizontal
    (horizontals are logged aggressively for completion design, and the
    Bakken horizontal campaign began 2007).

Basin clip:
  Union of all Bakken + Three Forks assessment units from the 2021 USGS
  re-release (ScienceBase 618e90c8) is the basin polygon. Wells are
  reprojected to EPSG:5070 (US Albers Equal Area) for the spatial join,
  then filtered to points inside the union polygon. Lat/lon are preserved
  from the source shapefile (EPSG:4269, NAD83) so browser rendering
  matches reality.

Outputs:
  salamituns.github.io/darkdata/williston/data/wells.csv         (lat,lon,d,v,s,h)
  salamituns.github.io/darkdata/williston/data/williston_basin.json
  salamituns.github.io/darkdata/williston/data/williston_states.json
  salamituns.github.io/darkdata/williston/data/summary.json
"""
import warnings; warnings.filterwarnings('ignore')
import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import geopandas as gpd
from shapely.ops import unary_union

ROOT = Path('/Users/olatunde/CoWorker/Geoworks')
RAW = ROOT / 'darkdata-repo/data/raw'
STATES_SRC = ROOT / 'data/raw/census_boundaries/gz_2010_us_040_00_5m.json'
OUT = ROOT / 'salamituns.github.io/darkdata/williston/data'
OUT.mkdir(parents=True, exist_ok=True)


def vbucket(y) -> int:
    if y is None or pd.isna(y):
        return 5
    try:
        y = int(y)
    except (TypeError, ValueError):
        return 5
    if y < 1980: return 0
    if y < 1990: return 1
    if y < 2000: return 2
    if y < 2010: return 3
    if y <= datetime.now().year: return 4
    return 5


def parse_mt_year(s) -> int | None:
    """MT 'Completed' is 'MM/DD/YYYY' or null. Return year or None."""
    if pd.isna(s) or not s:
        return None
    try:
        return int(str(s).split('/')[-1])
    except (ValueError, IndexError):
        return None


def main():
    print('Loading NDIC wells...')
    nd = gpd.read_file(RAW / 'ndic/ogd_wells/OGD_Wells.shp')
    print(f'  {len(nd):,} ND wells, crs={nd.crs}')

    print('Loading NDIC horizontals (unique APIs)...')
    nd_horz_pts = gpd.read_file(RAW / 'ndic/ogd_horizontals/OGD_Horizontals.shp')
    horz_apis = set(nd_horz_pts['api_wellno'].dropna().astype(str).unique())
    print(f'  {len(horz_apis):,} unique ND horizontal APIs')
    del nd_horz_pts  # free memory

    print('Loading MT BOGC wells...')
    mt = gpd.read_file(RAW / 'mt_bogc/wells/wells.shp')
    print(f'  {len(mt):,} MT wells, crs={mt.crs}')

    print('Loading USGS Bakken + Three Forks AUs...')
    bk_aus = gpd.read_file(RAW / 'usgs_bakken/bundle/BakkenAUs/BakkenAUs.shp')
    tf_aus = gpd.read_file(RAW / 'usgs_bakken/bundle/ThreeForksAUs/ThreeForksAUs.shp')
    print(f'  {len(bk_aus)} Bakken AUs, {len(tf_aus)} Three Forks AUs')

    basin_poly_4269 = unary_union(
        list(bk_aus.geometry.values) + list(tf_aus.geometry.values)
    )
    basin_gdf_4269 = gpd.GeoDataFrame(
        {'name': ['Bakken-Three Forks TPS']},
        geometry=[basin_poly_4269], crs='EPSG:4269'
    )
    print(f'  basin polygon bounds (lon/lat): {basin_gdf_4269.total_bounds}')

    # ---- Normalise ND schema -------------------------------------------------
    nd_clean = pd.DataFrame({
        'lat': nd['latitude'].astype(float),
        'lon': nd['longitude'].astype(float),
        'api': nd['api'].astype(str),
        'spud_year': nd['spud_date'].dt.year if hasattr(nd['spud_date'], 'dt') else pd.to_datetime(nd['spud_date'], errors='coerce').dt.year,
        'operator': nd['operator'].astype(str),
        'field': nd['field_name'].astype(str),
        'state': 'ND',
    })
    nd_clean = nd_clean.dropna(subset=['lat', 'lon'])
    nd_clean = nd_clean[(nd_clean['lat'].between(-90, 90)) & (nd_clean['lon'].between(-180, 180))]
    nd_clean['h'] = nd_clean['api'].isin(horz_apis).astype(int)
    print(f'  ND after coord filter: {len(nd_clean):,}  (horizontals: {nd_clean["h"].sum():,})')

    # ---- Normalise MT schema -------------------------------------------------
    # MT has no lat/lon fields; extract from geometry (shapefile crs is EPSG:4269)
    mt_clean = pd.DataFrame({
        'lat': mt.geometry.y,
        'lon': mt.geometry.x,
        'api': mt['API_WellNo'].astype(str),
        'spud_year': mt['Completed'].apply(parse_mt_year),
        'operator': mt['CoName'].astype(str),
        'field': mt['Reg_Field'].astype(str),
        'state': 'MT',
    })
    mt_clean = mt_clean.dropna(subset=['lat', 'lon'])
    mt_clean = mt_clean[(mt_clean['lat'].between(-90, 90)) & (mt_clean['lon'].between(-180, 180))]
    mt_clean['h'] = 0  # not derivable from MT shipped schema
    print(f'  MT after coord filter: {len(mt_clean):,}')

    # ---- Combine + basin clip -----------------------------------------------
    all_wells = pd.concat([nd_clean, mt_clean], ignore_index=True)
    print(f'Combined wells: {len(all_wells):,}')

    wells_gdf = gpd.GeoDataFrame(
        all_wells,
        geometry=gpd.points_from_xy(all_wells['lon'], all_wells['lat']),
        crs='EPSG:4269',
    )

    # reproject both to EPSG:5070 for accurate spatial join
    wells_albers = wells_gdf.to_crs('EPSG:5070')
    basin_albers = basin_gdf_4269.to_crs('EPSG:5070')

    wells_albers['_in_basin'] = wells_albers.within(basin_albers.geometry.iloc[0])
    clipped = wells_albers[wells_albers['_in_basin']].drop(columns=['_in_basin', 'geometry'])
    clipped = pd.DataFrame(clipped)
    print(f'Basin-clipped wells: {len(clipped):,}')

    # ---- Classify -----------------------------------------------------------
    clipped['v'] = clipped['spud_year'].apply(vbucket)
    clipped['s'] = (clipped['state'] == 'MT').astype(int)
    clipped['d'] = (clipped['v'].isin([0, 1, 2, 5]) & (clipped['h'] == 0)).astype(int)

    # ---- Summary stats ------------------------------------------------------
    total = len(clipped)
    dark = int(clipped['d'].sum())
    lit = total - dark
    pct_dark = 100 * dark / total if total else 0

    by_state = clipped.groupby('state').agg(
        total=('api', 'count'),
        dark=('d', 'sum'),
        horz=('h', 'sum'),
    )
    by_state['pct_dark'] = 100 * by_state['dark'] / by_state['total']

    vintage = clipped['v'].value_counts().sort_index()

    top_operators = (
        clipped.groupby('operator').agg(total=('api', 'count'), dark=('d', 'sum'))
        .sort_values('total', ascending=False).head(15)
    )
    top_operators['pct_dark'] = 100 * top_operators['dark'] / top_operators['total']

    top_fields = (
        clipped[clipped['field'].notna() & (clipped['field'] != 'nan') & (clipped['field'] != 'WILDCAT')]
        .groupby('field').agg(total=('api', 'count'), dark=('d', 'sum'))
        .sort_values('total', ascending=False).head(10)
    )

    summary = {
        'basin': 'Williston (Bakken-Three Forks TPS)',
        'clip_polygon': 'USGS 2021 Bakken + Three Forks Assessment Unit union',
        'jurisdictions': ['North Dakota', 'Montana'],
        'excluded_jurisdictions': ['South Dakota (<500 wells in TPS)', 'Saskatchewan (future extension)'],
        'total_wells': int(total),
        'dark': dark,
        'lit': lit,
        'pct_dark': round(pct_dark, 1),
        'by_state': {
            state: {
                'total': int(row['total']),
                'dark': int(row['dark']),
                'horizontal_flagged': int(row['horz']),
                'pct_dark': round(float(row['pct_dark']), 1),
            }
            for state, row in by_state.iterrows()
        },
        'vintage_distribution': {
            str(k): int(v) for k, v in vintage.items()
        },
        'vintage_labels': {
            '0': 'pre-1980', '1': '1980s', '2': '1990s',
            '3': '2000s', '4': '2010+', '5': 'unknown',
        },
        'top_operators': [
            {
                'operator': op,
                'total': int(row['total']),
                'dark': int(row['dark']),
                'pct_dark': round(float(row['pct_dark']), 1),
            }
            for op, row in top_operators.iterrows()
        ],
        'top_fields': [
            {'field': f, 'total': int(row['total']), 'dark': int(row['dark'])}
            for f, row in top_fields.iterrows()
        ],
        'notes': {
            'dark_definition': (
                'd = 1 if spud/completed year < 2000 AND well is not flagged as a '
                'horizontal. NDIC and BOGC digital filing systems went live around '
                '2000; pre-2000 wells rely on paper scans that are not '
                'systematically public.'
            ),
            'mt_vintage_note': (
                'MT BOGC ships completion date (not spud date); we use the '
                'completion year as a vintage proxy. Completion typically lags '
                'spud by 30-90 days in conventional wells.'
            ),
            'mt_horizontal_note': (
                'MT BOGC shapefile ships no horizontal indicator. MT horizontals '
                'are counted as non-horizontal in this cut, biasing MT dark share '
                'upward by a few points relative to ND. Documented on StoryMap.'
            ),
        },
        'generated_at': datetime.now().isoformat(timespec='seconds'),
    }

    # ---- Emit wells.csv -----------------------------------------------------
    out_wells = clipped[['lat', 'lon', 'd', 'v', 's', 'h']].copy()
    out_wells['lat'] = out_wells['lat'].round(5)
    out_wells['lon'] = out_wells['lon'].round(5)
    out_wells.to_csv(OUT / 'wells.csv', index=False)
    print(f'wrote {OUT / "wells.csv"}  ({len(out_wells):,} rows)')

    # ---- Emit basin polygon as GeoJSON --------------------------------------
    basin_geojson = json.loads(basin_gdf_4269.to_json())
    with (OUT / 'williston_basin.json').open('w') as f:
        json.dump(basin_geojson, f, separators=(',', ':'))
    print(f'wrote {OUT / "williston_basin.json"}')

    # ---- Emit state outlines clipped to bbox --------------------------------
    states = gpd.read_file(STATES_SRC)
    states = states[states['NAME'].isin(['North Dakota', 'Montana', 'South Dakota'])].copy()
    states = states.to_crs('EPSG:4269')
    states_geojson = json.loads(states[['NAME', 'geometry']].to_json())
    with (OUT / 'williston_states.json').open('w') as f:
        json.dump(states_geojson, f, separators=(',', ':'))
    print(f'wrote {OUT / "williston_states.json"}')

    # ---- Emit summary -------------------------------------------------------
    with (OUT / 'summary.json').open('w') as f:
        json.dump(summary, f, indent=2)
    print(f'wrote {OUT / "summary.json"}')

    print('\n--- Summary ---')
    print(f'Basin-clipped wells: {total:,}')
    print(f'Dark: {dark:,} ({pct_dark:.1f}%)')
    print(f'Lit: {lit:,} ({100-pct_dark:.1f}%)')
    print()
    print(by_state)
    print()
    print('Vintage distribution:')
    for k, v in vintage.items():
        print(f'  {summary["vintage_labels"][str(k)]:10s}: {v:,}')
    print()
    print('Top 10 operators by basin well count:')
    print(top_operators.head(10))


if __name__ == '__main__':
    main()
