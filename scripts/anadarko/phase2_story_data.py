"""
Phase 2: build the Anadarko story bundle (basin-clipped, two-state).

Inputs:
  data/raw/occ/RBDMS_WELLS.zip                 (455K OK wells, shapefile)
  data/raw/occ/completions-base.xlsx           (modern OK completions)
  data/raw/occ/completions-legacy.xlsx         (historical OK completions)
  data/raw/occ/orphan-well-list.xlsx           (OK orphan/abandoned wells)
  data/raw/kgs/kgs_master_wells.csv            (420K KS wells)
  data/raw/kgs/ks_las_files.txt                (KS public LAS archive list)
  data/raw/usgs_anadarko/Shapefiles/MapUnitPolys.shp (USGS basin envelope)

Outputs (mirroring Williston):
  darkdata/anadarko/data/wells.csv
    columns: lat, lon, d, v, s, h
      d = 1 if dark, 0 if lit
      v = vintage bucket (0=pre1980, 1=80s, 2=90s, 3=2000s, 4=2010+, 5=unknown)
      s = state (0=KS, 1=OK)
      h = horizontal flag (1 if drill_type indicates horizontal)
  darkdata/anadarko/data/anadarko_basin.json   (basin envelope, GeoJSON 4326)
  darkdata/anadarko/data/anadarko_states.json  (KS+OK outlines)
  darkdata/anadarko/data/summary.json          (totals + by_state + vintage)

Lit/dark logic:

  OK lit = appears in completions-base.xlsx with EITHER
            Open_Hole_Logs == 'Yes' OR Drill_Type contains 'H'
            (i.e. structured digital completion record exists,
             with either an open-hole log filed or a horizontal
             completion that necessarily produces curve data)

  OK dark = in RBDMS_WELLS but NOT lit by the above test
            (orphan/abandoned wells fall into this bucket)

  KS lit = API_NUM_NODASH appears in the KGS public LAS archive
            (same proxy used in basin 01)
  KS dark = otherwise

Vintage source:
  OK: Spud date from completions-base, fall back to COMPLETION_DATE in
      completions-legacy. Many OK wells have no completion record at
      all; those go to bucket 5 (unknown).
  KS: COMPLETION_YEAR from master CSV (existing basin 01 logic).
"""
import zipfile
import json
from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.ops import unary_union
from shapely.geometry import shape

ROOT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo')
RAW = ROOT / 'data/raw'
SITE = Path('/Users/olatunde/CoWorker/Geoworks/salamituns.github.io')
OUT = SITE / 'darkdata/anadarko/data'
OUT.mkdir(parents=True, exist_ok=True)


def vintage_bucket(year):
    if year is None or pd.isna(year):
        return 5
    try:
        y = int(year)
    except Exception:
        return 5
    if y < 1980:
        return 0
    if y < 1990:
        return 1
    if y < 2000:
        return 2
    if y < 2010:
        return 3
    return 4


# ============================================================
# 1. Load and clean OK wells
# ============================================================
print('Loading OK RBDMS_WELLS shapefile...')
ok = gpd.read_file(f'zip://{RAW}/occ/RBDMS_WELLS.zip')
ok = ok[(ok.geometry.notna()) & (ok['SH_LAT'].notna()) & (ok['SH_LON'].notna())]
ok['API'] = ok['API'].astype('Int64')
print(f'  OK wells with coords: {len(ok):,}')

# Load OK completions (Spud + drill type + open-hole-logs)
# IMPORTANT: pd.read_excel(usecols=...) returns columns in XLSX source order,
# not in the order of the usecols list. Rename via dict, not positional list.
print('Loading OK completions (modern)...')
comp_modern = pd.read_excel(
    RAW/'occ/completions-base.xlsx',
    usecols=['API_Number', 'Spud', 'Well_Completion', 'Drill_Type', 'Open_Hole_Logs'],
)
comp_modern = comp_modern.rename(columns={
    'API_Number': 'api',
    'Spud': 'spud',
    'Well_Completion': 'completion',
    'Drill_Type': 'drill_type',
    'Open_Hole_Logs': 'open_hole_logs',
})
comp_modern['api'] = pd.to_numeric(comp_modern['api'], errors='coerce').astype('Int64')

# Parse spud or completion year
def parse_year(s):
    if pd.isna(s) or s == '' or str(s).startswith('1900'):
        return None
    try:
        return int(str(s)[:4])
    except Exception:
        return None
comp_modern['year'] = comp_modern['spud'].apply(parse_year)
comp_modern['year'] = comp_modern['year'].fillna(comp_modern['completion'].apply(parse_year))

# Aggregate per API: take min year, any open-hole-log = Yes, any horizontal drill type
comp_modern['has_oh_log'] = (comp_modern['open_hole_logs'].astype(str).str.upper().str.strip() == 'YES')
comp_modern['is_horz'] = comp_modern['drill_type'].astype(str).str.upper().str.contains('H', na=False)

modern_agg = comp_modern.groupby('api').agg(
    year=('year', 'min'),
    has_oh_log=('has_oh_log', 'any'),
    is_horz=('is_horz', 'any'),
).reset_index()
print(f'  modern completion APIs: {len(modern_agg):,}')

# Legacy completions (just for vintage backfill)
print('Loading OK completions (legacy)...')
comp_legacy = pd.read_excel(
    RAW/'occ/completions-legacy.xlsx',
    usecols=['API', 'COMPLETION_DATE', 'SPUD_DATE', 'LOGS_RUN'],
)
comp_legacy = comp_legacy.rename(columns={
    'API': 'api',
    'COMPLETION_DATE': 'completion',
    'SPUD_DATE': 'spud',
    'LOGS_RUN': 'logs_run',
})
comp_legacy['api'] = pd.to_numeric(comp_legacy['api'], errors='coerce').astype('Int64')
comp_legacy['year'] = comp_legacy['spud'].apply(parse_year).fillna(comp_legacy['completion'].apply(parse_year))
comp_legacy['has_log'] = (comp_legacy['logs_run'].astype(str).str.upper().str.strip() == 'Y')

legacy_agg = comp_legacy.groupby('api').agg(
    year=('year', 'min'),
    has_log=('has_log', 'any'),
).reset_index()
print(f'  legacy completion APIs: {len(legacy_agg):,}')

# Join completion data onto OK wells
ok = ok.merge(modern_agg, left_on='API', right_on='api', how='left', suffixes=('', '_mod'))
ok = ok.merge(legacy_agg, left_on='API', right_on='api', how='left', suffixes=('', '_leg'))

# Compose final lit/dark and year per OK well
ok['has_oh_log'] = ok['has_oh_log'].fillna(False).astype(bool)
ok['is_horz'] = ok['is_horz'].fillna(False).astype(bool)
ok['has_log_legacy'] = ok['has_log'].fillna(False).astype(bool) if 'has_log' in ok.columns else False

# OK lit if: open-hole log filed (modern) OR horizontal completion
# (horizontal completions always carry curve data via the lateral)
ok['lit'] = ok['has_oh_log'] | ok['is_horz']
ok['dark'] = ~ok['lit']

# Vintage: use modern year first, fall back to legacy year
ok['year_final'] = ok['year']
ok['year_final'] = ok['year_final'].fillna(ok['year_leg'])
ok['v'] = ok['year_final'].apply(vintage_bucket)
ok['s'] = 1  # 1 = OK
ok['h'] = ok['is_horz'].astype(int)

# Map to surface coords
ok['lat'] = ok['SH_LAT'].astype(float)
ok['lon'] = ok['SH_LON'].astype(float)

ok_clean = ok[['lat', 'lon', 'dark', 'v', 's', 'h', 'OPERATOR', 'API']].copy()
ok_clean['d'] = ok_clean['dark'].astype(int)
ok_clean = ok_clean.rename(columns={'OPERATOR': 'op'})
print(f'  OK wells finalized: {len(ok_clean):,}  (lit {(ok_clean["d"]==0).sum():,} / dark {(ok_clean["d"]==1).sum():,})')

# ============================================================
# 2. Load and clean KS wells
# ============================================================
print('Loading KS master CSV...')
ks = pd.read_csv(RAW/'kgs/kgs_master_wells.csv', low_memory=False)
ks = ks[ks['Latitude (NAD27)'].notna() & ks['Longitude (NAD27)'].notna()]
print(f'  KS rows with coords: {len(ks):,}')

# KS lit proxy: API_NUM_NODASH appears in the KGS LAS archive CSV
# The file is a CSV with a header row, not a list of LAS path names.
# The key column is 'API_NUM_NODASH' (14-digit form, e.g. '15131202340000').
las_path = RAW/'kgs/ks_las_files.txt'
las_df = pd.read_csv(las_path, dtype=str)
las_apis = set(las_df['API_NUM_NODASH'].dropna().str.strip())
las_apis.discard('')
print(f'  KS LAS APIs (14-digit form): {len(las_apis):,}')

# Normalize KS API_NUM_NODASH to 14-digit string for direct match
def ks_api14(v):
    if pd.isna(v):
        return None
    s = str(v).split('.')[0]  # strip float suffix
    return s if s and s.isdigit() else None

ks['api14'] = ks['API_NUM_NODASH'].apply(ks_api14)
ks['lit'] = ks['api14'].isin(las_apis)
ks['dark'] = ~ks['lit']
ks['v'] = ks['COMPLETION_YEAR'].apply(vintage_bucket)
ks['s'] = 0  # 0 = KS
ks['h'] = 0  # KS master CSV does not expose horizontal flag
ks['lat'] = ks['Latitude (NAD27)'].astype(float)
ks['lon'] = ks['Longitude (NAD27)'].astype(float)
ks_clean = ks[['lat', 'lon', 'dark', 'v', 's', 'h', 'Original Operator', 'api14']].copy()
ks_clean['d'] = ks_clean['dark'].astype(int)
ks_clean = ks_clean.rename(columns={'Original Operator': 'op', 'api14': 'API'})
print(f'  KS wells finalized: {len(ks_clean):,}  (lit {(ks_clean["d"]==0).sum():,} / dark {(ks_clean["d"]==1).sum():,})')

# ============================================================
# 3. Build basin envelope (dissolve MapUnitPolys to single polygon)
# ============================================================
print('Building Anadarko basin envelope...')
extract = RAW/'usgs_anadarko/extracted'
if not (extract/'Shapefiles/MapUnitPolys.shp').exists():
    extract.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(RAW/'usgs_anadarko/Shapefiles.zip') as z:
        z.extractall(extract)

mu = gpd.read_file(extract/'Shapefiles/MapUnitPolys.shp')
mu = mu.to_crs('EPSG:4269')  # NAD83 lon/lat
basin_poly = unary_union(mu.geometry.tolist())
basin_gdf = gpd.GeoDataFrame({'name': ['Anadarko Basin Province (USGS GMC 058)']}, geometry=[basin_poly], crs='EPSG:4269')
print(f'  basin envelope bounds: {basin_gdf.total_bounds}')

# ============================================================
# 4. Spatial clip wells to basin
# ============================================================
print('Clipping OK + KS wells to basin envelope...')
ok_g = gpd.GeoDataFrame(
    ok_clean, geometry=gpd.points_from_xy(ok_clean['lon'], ok_clean['lat']), crs='EPSG:4269'
)
ks_g = gpd.GeoDataFrame(
    ks_clean, geometry=gpd.points_from_xy(ks_clean['lon'], ks_clean['lat']), crs='EPSG:4269'
)

# spatial join (within)
ok_in = gpd.sjoin(ok_g, basin_gdf, predicate='within', how='inner').drop(columns=['index_right', 'name'])
ks_in = gpd.sjoin(ks_g, basin_gdf, predicate='within', how='inner').drop(columns=['index_right', 'name'])
print(f'  OK in basin: {len(ok_in):,}  / KS in basin: {len(ks_in):,}')

# ============================================================
# 5. Emit wells.csv, polygon, summary
# ============================================================
print('Writing outputs...')
combined = pd.concat([
    ok_in[['lat', 'lon', 'd', 'v', 's', 'h']].assign(_op=ok_in['op'].fillna('UNKNOWN')),
    ks_in[['lat', 'lon', 'd', 'v', 's', 'h']].assign(_op=ks_in['op'].fillna('UNKNOWN')),
], ignore_index=True)
# Round coords for size
combined['lat'] = combined['lat'].round(4)
combined['lon'] = combined['lon'].round(4)
# write csv
wells_csv = combined[['lat', 'lon', 'd', 'v', 's', 'h']]
wells_csv.to_csv(OUT/'wells.csv', index=False)
print(f'  wrote {OUT/"wells.csv"} ({len(wells_csv):,} rows)')

# Basin polygon GeoJSON
basin_gdf.to_file(OUT/'anadarko_basin.json', driver='GeoJSON')
print(f'  wrote {OUT/"anadarko_basin.json"}')

# State outlines (KS + OK only)
# Use Natural Earth via geopandas or pull from existing CB shapefile if we have one
# Quick approach: use US Census cartographic boundary states via online URL, or
# build minimal rectangles. For now, query a minimal source.
states_url = 'https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json'
import urllib.request
try:
    with urllib.request.urlopen(states_url, timeout=30) as r:
        states_geo = json.loads(r.read())
    keep = [f for f in states_geo['features'] if f['properties']['name'] in ('Kansas', 'Oklahoma')]
    states_geo['features'] = keep
    (OUT/'anadarko_states.json').write_text(json.dumps(states_geo))
    print(f'  wrote {OUT/"anadarko_states.json"} ({len(keep)} states)')
except Exception as e:
    print(f'  state fetch FAIL: {e}')

# Summary stats
total = int(len(combined))
dark = int((combined['d'] == 1).sum())
lit = total - dark
ok_total = int(len(ok_in))
ks_total = int(len(ks_in))

ok_dark = int((ok_in['d'] == 1).sum())
ks_dark = int((ks_in['d'] == 1).sum())
ok_horz = int(ok_in['h'].sum())

vintage_global = combined['v'].value_counts().to_dict()

# Top OK operators by dark wells
ok_op = ok_in.groupby('op', dropna=False).agg(total=('d', 'count'), dark=('d', 'sum')).reset_index()
ok_op['pct_dark'] = (100.0 * ok_op['dark'] / ok_op['total']).round(1)
ok_op = ok_op.sort_values('total', ascending=False).head(15)
top_operators_ok = ok_op.to_dict(orient='records')

ks_op = ks_in.groupby('op', dropna=False).agg(total=('d', 'count'), dark=('d', 'sum')).reset_index()
ks_op['pct_dark'] = (100.0 * ks_op['dark'] / ks_op['total']).round(1)
ks_op = ks_op.sort_values('total', ascending=False).head(15)
top_operators_ks = ks_op.to_dict(orient='records')

summary = {
    'total_wells': total,
    'dark': dark,
    'lit': lit,
    'pct_dark': round(100.0 * dark / total, 1) if total else 0,
    'by_state': {
        'KS': {
            'total': ks_total,
            'dark': ks_dark,
            'horizontal_flagged': 0,
            'pct_dark': round(100.0 * ks_dark / ks_total, 1) if ks_total else 0,
        },
        'OK': {
            'total': ok_total,
            'dark': ok_dark,
            'horizontal_flagged': ok_horz,
            'pct_dark': round(100.0 * ok_dark / ok_total, 1) if ok_total else 0,
        },
    },
    'vintage_distribution': {str(k): int(v) for k, v in vintage_global.items()},
    'top_operators_ok': top_operators_ok,
    'top_operators_ks': top_operators_ks,
    'notes': [
        'Basin clip: USGS GMC Anadarko Basin Province 3D-model MapUnitPolys dissolve.',
        'Lit/dark proxies are state-asymmetric: OK uses Open_Hole_Logs flag + horizontal drill type from OCC RBDMS completions; KS uses public LAS archive presence (basin 01 logic).',
        'TX panhandle portion of the Anadarko Basin Province is excluded from v1 (TX RRC bulk data lives behind a JSF/PrimeFaces session portal; deferred to basin 06).',
    ],
}
(OUT/'summary.json').write_text(json.dumps(summary, indent=2))
print(f'  wrote {OUT/"summary.json"}')
print()
print(f'TOTAL: {total:,} wells in basin  | dark {dark:,} ({summary["pct_dark"]}%)')
print(f'  KS in basin: {ks_total:,}  ({summary["by_state"]["KS"]["pct_dark"]}% dark)')
print(f'  OK in basin: {ok_total:,}  ({summary["by_state"]["OK"]["pct_dark"]}% dark, {ok_horz:,} horizontals)')
