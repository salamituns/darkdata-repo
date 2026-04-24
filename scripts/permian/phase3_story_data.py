"""
Phase 3: build browser-ready data bundles for /darkdata/permian/.

Inputs:
  data/raw/tx_rrc/permian_wells.csv     (wells in TX Permian bbox)
  data/raw/tx_rrc/permian_logs.csv      (TX scanned-log inventory)
  data/raw/tx_rrc/permian_orphans.csv   (TX orphan wells)
  data/raw/nm_ocd/permian_wells.csv     (NM wells in Permian FIPS counties)
  Geoworks/data/raw/census_boundaries/gz_2010_us_050_00_500k.json

Classification rules (V1: asymmetric, documented on the StoryMap):
  TX: d = 1 if API not in log inventory (scanned TIFF in RRC imaged system);
      v = 5 unknown (no spud date on live REST feed)
  NM: d = 1 if year_spudded < 2002 or unknown
          (OCD digital-filing-era floor; every NM well has a boilerplate
          `files` URL, so that field is not a lit proxy);
      v from spud_year buckets

Vintage buckets (shared with Kansas):
  0 pre-1980   1 1980s   2 1990s   3 2000s   4 2010+   5 unknown

State flag:
  s = 0 TX   s = 1 NM

Outputs:
  salamituns.github.io/darkdata/permian/data/wells.csv
  salamituns.github.io/darkdata/permian/data/permian_counties.json
  salamituns.github.io/darkdata/permian/data/summary.json
"""
import warnings; warnings.filterwarnings('ignore')
import json
import os
from pathlib import Path

import pandas as pd
import geopandas as gpd

ROOT = Path('/Users/olatunde/CoWorker/Geoworks')
RAW = ROOT / 'darkdata-repo/data/raw'
COUNTIES_SRC = ROOT / 'data/raw/census_boundaries/gz_2010_us_050_00_500k.json'
OUT = ROOT / 'salamituns.github.io/darkdata/permian/data'
OUT.mkdir(parents=True, exist_ok=True)

# Permian counties: FIPS
TX_STATE_FIPS = '48'
NM_STATE_FIPS = '35'

# TX Permian (28 counties: see notes/permian_sources.md)
TX_PERMIAN = {
    'Andrews', 'Borden', 'Crane', 'Crockett', 'Culberson', 'Dawson',
    'Ector', 'Gaines', 'Glasscock', 'Hockley', 'Howard', 'Irion',
    'Jeff Davis', 'Kent', 'Loving', 'Lynn', 'Martin', 'Midland',
    'Pecos', 'Reagan', 'Reeves', 'Scurry', 'Sterling', 'Terry',
    'Upton', 'Ward', 'Winkler', 'Yoakum',
}
# NM Permian
NM_PERMIAN = {'Chaves', 'Eddy', 'Lea', 'Roosevelt'}


def vbucket(y) -> int:
    if y is None or pd.isna(y):
        return 5
    try:
        yi = int(y)
    except (TypeError, ValueError):
        return 5
    if yi < 1900 or yi >= 2100:
        return 5
    if yi < 1980:
        return 0
    if yi < 1990:
        return 1
    if yi < 2000:
        return 2
    if yi < 2010:
        return 3
    return 4


def load_counties() -> gpd.GeoDataFrame:
    """Load Permian county polygons (TX + NM subset) from Census TIGER."""
    g = gpd.read_file(COUNTIES_SRC, encoding='latin-1')
    tx = g[(g['STATE'] == TX_STATE_FIPS) & (g['NAME'].isin(TX_PERMIAN))].copy()
    nm = g[(g['STATE'] == NM_STATE_FIPS) & (g['NAME'].isin(NM_PERMIAN))].copy()
    print(f'  TX county polygons: {len(tx)} / {len(TX_PERMIAN)} expected')
    print(f'  NM county polygons: {len(nm)} / {len(NM_PERMIAN)} expected')
    missing_tx = TX_PERMIAN - set(tx['NAME'].tolist())
    missing_nm = NM_PERMIAN - set(nm['NAME'].tolist())
    if missing_tx:
        print(f'  WARN: missing TX counties: {missing_tx}')
    if missing_nm:
        print(f'  WARN: missing NM counties: {missing_nm}')
    tx['state'] = 'TX'; nm['state'] = 'NM'
    return pd.concat([tx, nm], ignore_index=True)


# -- 1. TX ----------------------------------------------------------------
print('== TX ==')
tx = pd.read_csv(RAW / 'tx_rrc/permian_wells.csv', dtype={'API': str})
before_tx = len(tx)
tx = tx.drop_duplicates(subset=['API'])
tx = tx.dropna(subset=['lat', 'lon'])
tx['lat'] = pd.to_numeric(tx['lat'], errors='coerce')
tx['lon'] = pd.to_numeric(tx['lon'], errors='coerce')
tx = tx.dropna(subset=['lat', 'lon'])
print(f'  wells: {before_tx:,} rows → {len(tx):,} unique APIs with coords')

tx_logs = pd.read_csv(RAW / 'tx_rrc/permian_logs.csv', dtype={'API': str})
tx_log_set = set(tx_logs['API'].dropna().unique())
print(f'  log APIs: {len(tx_log_set):,} unique (from {len(tx_logs):,} rows)')

tx['d'] = (~tx['API'].isin(tx_log_set)).astype('int8')
tx['v'] = 5  # unknown for all TX V1
tx['s'] = 0

tx_orphans = pd.read_csv(RAW / 'tx_rrc/permian_orphans.csv', dtype={'API': str})
tx_orphan_set = set(tx_orphans['API'].dropna().unique())


# -- 2. NM ----------------------------------------------------------------
print('\n== NM ==')
nm = pd.read_csv(RAW / 'nm_ocd/permian_wells.csv', dtype={'API': str})
before_nm = len(nm)
nm = nm.drop_duplicates(subset=['API'])
nm = nm.dropna(subset=['lat', 'lon'])
nm['lat'] = pd.to_numeric(nm['lat'], errors='coerce')
nm['lon'] = pd.to_numeric(nm['lon'], errors='coerce')
nm = nm.dropna(subset=['lat', 'lon'])
print(f'  wells: {before_nm:,} rows → {len(nm):,} unique APIs with coords')

nm['year_int'] = pd.to_numeric(nm['year_spudded'], errors='coerce')
nm['v'] = nm['year_int'].apply(vbucket).astype('int8')
# Dark = not explicitly post-2002. Unknown treated as dark by default.
nm['d'] = (~((nm['year_int'] >= 2002) & (nm['year_int'] < 2100))).astype('int8')
nm['s'] = 1


# -- 3. Spatial clip (TX by PIP, NM by county name already filtered) -----
print('\n== Spatial clip ==')
counties = load_counties()

# TX: point-in-polygon against TX Permian county polygons
tx_gdf = gpd.GeoDataFrame(
    tx, geometry=gpd.points_from_xy(tx['lon'], tx['lat']), crs='EPSG:4326'
)
tx_polys = counties[counties['state'] == 'TX'][['NAME', 'geometry']].rename(
    columns={'NAME': 'county'}
)
tx_clipped = gpd.sjoin(tx_gdf, tx_polys, how='inner', predicate='within')
print(f'  TX after county clip: {len(tx_clipped):,} / {len(tx):,} '
      f'({100*len(tx_clipped)/len(tx):.1f}% retained)')

# NM: verify (county field already used in pull)
nm_gdf = gpd.GeoDataFrame(
    nm, geometry=gpd.points_from_xy(nm['lon'], nm['lat']), crs='EPSG:4326'
)
nm_polys = counties[counties['state'] == 'NM'][['NAME', 'geometry']].rename(
    columns={'NAME': 'county_geom'}
)
nm_clipped = gpd.sjoin(nm_gdf, nm_polys, how='inner', predicate='within')
print(f'  NM after county clip: {len(nm_clipped):,} / {len(nm):,} '
      f'({100*len(nm_clipped)/len(nm):.1f}% retained)')


# -- 4. Unified wells.csv -------------------------------------------------
tx_out = pd.DataFrame({
    'lat': tx_clipped['lat'].round(4),
    'lon': tx_clipped['lon'].round(4),
    'd': tx_clipped['d'].astype('int8'),
    'v': tx_clipped['v'].astype('int8'),
    's': tx_clipped['s'].astype('int8'),
})
nm_out = pd.DataFrame({
    'lat': nm_clipped['lat'].round(4),
    'lon': nm_clipped['lon'].round(4),
    'd': nm_clipped['d'].astype('int8'),
    'v': nm_clipped['v'].astype('int8'),
    's': nm_clipped['s'].astype('int8'),
})
wells = pd.concat([tx_out, nm_out], ignore_index=True)
print(f'\n  unified wells rows: {len(wells):,}')
print('  d value_counts:\n', wells['d'].value_counts().to_string())
print('  v value_counts:\n', wells['v'].value_counts().sort_index().to_string())
print('  s value_counts:\n', wells['s'].value_counts().to_string())

path_csv = OUT / 'wells.csv'
wells.to_csv(path_csv, index=False, float_format='%.4f')
print(f'  wrote {path_csv}  ({os.path.getsize(path_csv)/1e6:.1f} MB)')


# -- 5. Per-county aggregation -------------------------------------------
print('\n== County aggregation ==')
tx_clipped['lit'] = 1 - tx_clipped['d']
nm_clipped['lit'] = 1 - nm_clipped['d']

tx_agg = (tx_clipped.groupby('county')
          .agg(total=('lit', 'size'), lit=('lit', 'sum'))
          .assign(pct_lit=lambda d: (100 * d['lit'] / d['total']).round(2),
                  state='TX').reset_index())
nm_agg = (nm_clipped.groupby('county_geom')
          .agg(total=('lit', 'size'), lit=('lit', 'sum'))
          .assign(pct_lit=lambda d: (100 * d['lit'] / d['total']).round(2),
                  state='NM').reset_index()
          .rename(columns={'county_geom': 'county'}))
agg = pd.concat([tx_agg, nm_agg], ignore_index=True)

# Attach to polygons
counties['KEY'] = counties['state'] + '|' + counties['NAME']
agg['KEY'] = agg['state'] + '|' + agg['county']
counties_out = counties.merge(
    agg[['KEY', 'total', 'lit', 'pct_lit']], on='KEY', how='left'
)
counties_out['total'] = counties_out['total'].fillna(0).astype(int)
counties_out['lit'] = counties_out['lit'].fillna(0).astype(int)
counties_out['pct_lit'] = counties_out['pct_lit'].fillna(0)
counties_out['geometry'] = counties_out['geometry'].simplify(
    0.01, preserve_topology=True)
counties_out = counties_out[['NAME', 'state', 'total', 'lit', 'pct_lit',
                             'geometry']].rename(columns={'NAME': 'name'})
path_geo = OUT / 'permian_counties.json'
if path_geo.exists():
    path_geo.unlink()
counties_out.to_file(path_geo, driver='GeoJSON')
print(f'  wrote {path_geo}  ({os.path.getsize(path_geo)/1e3:.0f} KB)')


# -- 6. Summary ----------------------------------------------------------
print('\n== Summary ==')
total = len(wells)
lit = int((wells['d'] == 0).sum())
dark = int((wells['d'] == 1).sum())

# TX orphan intersection (APIs still in clipped set)
tx_clipped_apis = set(tx_clipped['API'])
tx_orphan_in_scope = tx_orphan_set & tx_clipped_apis
# NM orphans: not explicitly pulled; use status_code as a proxy
nm_orphan_like = int(nm_clipped['status_code'].fillna('').str.upper()
                     .str.startswith(('P', 'A')).eq(False).sum())
# Simpler: NM has no formal orphan list in this pull; leave as null

summary = {
    'scope': 'Permian Basin: TX (28 counties) + NM (4 counties)',
    'total_wells': total,
    'lit': lit,
    'dark': dark,
    'pct_lit': round(100 * lit / total, 2),
    'pct_dark': round(100 * dark / total, 2),
    'by_state': {
        'TX': {
            'wells': int((wells['s'] == 0).sum()),
            'lit': int(((wells['s'] == 0) & (wells['d'] == 0)).sum()),
            'dark': int(((wells['s'] == 0) & (wells['d'] == 1)).sum()),
            'orphans_in_scope': len(tx_orphan_in_scope),
            'pct_lit': round(
                100 * int(((wells['s'] == 0) & (wells['d'] == 0)).sum())
                / max(1, int((wells['s'] == 0).sum())), 2),
        },
        'NM': {
            'wells': int((wells['s'] == 1).sum()),
            'lit': int(((wells['s'] == 1) & (wells['d'] == 0)).sum()),
            'dark': int(((wells['s'] == 1) & (wells['d'] == 1)).sum()),
            'pct_lit': round(
                100 * int(((wells['s'] == 1) & (wells['d'] == 0)).sum())
                / max(1, int((wells['s'] == 1).sum())), 2),
        },
    },
    'by_vintage': {str(b): int((wells['v'] == b).sum()) for b in range(6)},
    'by_vintage_nm_only': {
        str(b): int(((wells['s'] == 1) & (wells['v'] == b)).sum())
        for b in range(6)
    },
    'nm_top_operators': None,  # filled below
    'extremes': None,           # filled below
    'method_notes': [
        "TX lit = API present in RRC Well Logs layer (scanned-TIFF inventory).",
        "TX vintage = unknown (v=5) for all TX wells: live REST doesn't "
        "expose spud dates.",
        "NM lit = year_spudded >= 2002 (OCD digital-filing-era floor). "
        "Unknown/junk years counted as dark.",
        "NM `files` URL is boilerplate on every well and is NOT a lit proxy.",
        "Lit-universe definitions are asymmetric: TX = scanned TIFF, "
        "NM = digital-era spud. Documented on methodology strip.",
    ],
}
# NM operator concentration (needs the raw NM dataframe, post-clip)
nm_clipped['is_lit'] = 1 - nm_clipped['d']
op_agg = (nm_clipped.groupby('operator')
          .agg(total=('is_lit', 'size'), lit=('is_lit', 'sum'))
          .assign(pct_lit=lambda d: (100 * d['lit'] / d['total']).round(1))
          .sort_values('total', ascending=False))
# Top 10 operators by well count, plus their lit share
top_ops = op_agg.head(10).reset_index()
# Handle missing/blank operator
top_ops['operator'] = top_ops['operator'].fillna('(no operator of record)').astype(str)
summary['nm_top_operators'] = [
    {'name': r['operator'],
     'wells': int(r['total']),
     'lit': int(r['lit']),
     'pct_lit': float(r['pct_lit'])}
    for _, r in top_ops.iterrows()
]

# County extremes (for storytelling)
county_scope = agg[agg['total'] >= 500].copy()
county_scope = county_scope.sort_values('pct_lit', ascending=False)
summary['extremes'] = {
    'highest_lit': [
        {'county': r['county'], 'state': r['state'], 'pct_lit': float(r['pct_lit']),
         'total': int(r['total']), 'lit': int(r['lit'])}
        for _, r in county_scope.head(5).iterrows()
    ],
    'lowest_lit': [
        {'county': r['county'], 'state': r['state'], 'pct_lit': float(r['pct_lit']),
         'total': int(r['total']), 'lit': int(r['lit'])}
        for _, r in county_scope.tail(5).iloc[::-1].iterrows()
    ],
}

path_json = OUT / 'summary.json'
with path_json.open('w') as f:
    json.dump(summary, f, indent=2)
print(f'  wrote {path_json}')
print(json.dumps(summary, indent=2))
