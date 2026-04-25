"""
Phase 2: build the Appalachia story bundle (basin-clipped, three-state).

Inputs:
  data/raw/pa_dep/OilGasLocations_ConvUnconv.zip     (~224K PA wells, shapefile, EPSG:3857)
  data/raw/pa_dep/PADEP_HistoricOilGasWells_ALL.zip  (~31K PA pre-regulatory wells, EPSG:4269)
  data/raw/wv_dep/WellLocation_2016.zip              (~114K WV wells, XLSX, UTM 17N)
  data/raw/wv_dep/2024Q4_Horizontal_H6A.xlsx         (WV horizontal H6A production filings = lit list)
  data/raw/oh_dnr/Oilgas_Wells_public.geojson        (~242K OH wells, REST query, EPSG:4326)
  data/raw/eia_shale/TightOil_ShaleGas_Plays_Lower48.zip (EIA shales, Basin=Appalachian filter)

Outputs (mirror Williston/Anadarko schema):
  darkdata/appalachia/data/wells.csv    (lat,lon,d,v,s,h)
    s = 0 (PA), 1 (WV), 2 (OH)
  darkdata/appalachia/data/appalachia_basin.json   (Marcellus + Utica + Devonian (Ohio) + Chattanooga union)
  darkdata/appalachia/data/appalachia_states.json  (PA + WV + OH state outlines)
  darkdata/appalachia/data/summary.json

Lit/dark logic (state-asymmetric):
  PA  lit  = UNCONVENTI == 'Y' OR WELL_CONFI contains 'Horizontal'
  PA dark = otherwise (incl. all historic WPA wells)

  WV  lit  = API appears in 2024 Q4 H6A horizontal production filing
  WV dark = otherwise

  OH  lit  = SLANT == 'Horizontal' OR Marcellus_Shale OR Utica_Shale present
  OH dark = otherwise

Vintage source:
  PA: SPUD_DATE field on conv/unconv layer; historic wells = bucket 0
  WV: no parseable spud-date column on the 2016 well file => bucket 5
  OH: no spud-date column on the public layer => bucket 5
"""
import warnings; warnings.filterwarnings('ignore')
import zipfile
import json
import io
from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.ops import unary_union

ROOT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo')
RAW = ROOT / 'data/raw'
SITE = Path('/Users/olatunde/CoWorker/Geoworks/salamituns.github.io')
OUT = SITE / 'darkdata/appalachia/data'
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


def parse_year(s):
    if pd.isna(s) or s is None:
        return None
    s = str(s).strip()
    if not s or s.startswith(('1900-01-01', '1899')):
        return None
    try:
        return int(s[:4])
    except Exception:
        return None


# ============================================================
# 1. PA conventional + unconventional
# ============================================================
print('Loading PA Conv/Unconv shapefile...')
pa = gpd.read_file(f'zip://{RAW}/pa_dep/OilGasLocations_ConvUnconv.zip')
pa = pa[(pa.geometry.notna()) & (pa['LATITUDE'].notna())]
pa['lat'] = pd.to_numeric(pa['LATITUDE'], errors='coerce')
pa['lon'] = pd.to_numeric(pa['LONGITUDE'], errors='coerce')
pa = pa[pa['lat'].notna() & pa['lon'].notna()]

pa['lit'] = (
    (pa['UNCONVENTI'].astype(str).str.upper().str.strip() == 'Y') |
    (pa['WELL_CONFI'].astype(str).str.contains('Horizontal', case=False, na=False))
)
pa['is_horz'] = pa['WELL_CONFI'].astype(str).str.contains('Horizontal', case=False, na=False)
pa['year'] = pa['SPUD_DATE'].apply(parse_year)
pa['v'] = pa['year'].apply(vintage_bucket)
pa['s'] = 0
pa['h'] = pa['is_horz'].astype(int)
pa['d'] = (~pa['lit']).astype(int)
pa_clean = pa[['lat', 'lon', 'd', 'v', 's', 'h', 'OPERATOR', 'PRMRY_FID']].copy()
pa_clean = pa_clean.rename(columns={'OPERATOR': 'op', 'PRMRY_FID': 'fid'})
print(f'  PA conv/unconv: {len(pa_clean):,}  (lit {(pa_clean["d"]==0).sum():,} / dark {(pa_clean["d"]==1).sum():,}, horz {pa_clean["h"].sum():,})')

# PA historic
print('Loading PA Historic wells...')
pa_hist = gpd.read_file(f'zip://{RAW}/pa_dep/PADEP_HistoricOilGasWells_ALL.zip')
pa_hist = pa_hist[pa_hist.geometry.notna()]
pa_hist['lat'] = pd.to_numeric(pa_hist['LATITUDE'], errors='coerce')
pa_hist['lon'] = pd.to_numeric(pa_hist['LONGITUDE'], errors='coerce')
pa_hist = pa_hist[pa_hist['lat'].notna() & pa_hist['lon'].notna()]
pa_hist_clean = pd.DataFrame({
    'lat': pa_hist['lat'].astype(float),
    'lon': pa_hist['lon'].astype(float),
    'd': 1,            # all historic WPA wells are dark by definition
    'v': 0,            # all pre-1980 vintage
    's': 0,            # PA
    'h': 0,            # never horizontal
    'op': 'HISTORIC (WPA / K Sheet / H Sheet)',
    'fid': pa_hist['ID'] if 'ID' in pa_hist.columns else range(len(pa_hist)),
})
print(f'  PA historic: {len(pa_hist_clean):,} (all dark, pre-regulatory)')

# Combine PA
pa_all = pd.concat([pa_clean, pa_hist_clean], ignore_index=True)
print(f'  PA combined: {len(pa_all):,}')


# ============================================================
# 2. WV well location 2016 + H6A horizontal lit list
# ============================================================
print('Loading WV well location 2016...')
with zipfile.ZipFile(RAW/'wv_dep/WellLocation_2016.zip') as z:
    with z.open('WellLocation(08-22-2016).xlsx') as f:
        wv = pd.read_excel(f)
print(f'  WV total rows: {len(wv):,}')

# Reproject UTM 17N (EPSG:26917) -> 4269
import pyproj
utm_to_geo = pyproj.Transformer.from_crs('EPSG:26917', 'EPSG:4269', always_xy=True)
wv['valid_utm'] = (wv['WELL_HEAD_UTM_EAST'] > 100000) & (wv['WELL_HEAD_UTM_NORTH'] > 1000000)
# Filter out the placeholder (500000, 4000000) origin coords commonly used for unknown locations
wv['placeholder'] = (wv['WELL_HEAD_UTM_EAST'] == 500000) & (wv['WELL_HEAD_UTM_NORTH'] == 4000000)
wv = wv[wv['valid_utm'] & ~wv['placeholder']].copy()
lon, lat = utm_to_geo.transform(wv['WELL_HEAD_UTM_EAST'].values, wv['WELL_HEAD_UTM_NORTH'].values)
wv['lon'] = lon
wv['lat'] = lat
# WV bbox sanity: roughly 37.2-40.7 N, -82.6 - -77.7 W
wv = wv[(wv['lat'] > 37) & (wv['lat'] < 41) & (wv['lon'] > -83) & (wv['lon'] < -77)]
print(f'  WV after coord clean: {len(wv):,}')

# Lit proxy: WV's 2016 well location file uses PERMIT_ID (a 6-digit
# permit-issuance sequence), while the 2024 Q4 H6A horizontal production
# file uses 10-digit API numbers (47-CCC-NNNNN). These do not link
# without a separate cross-reference table that WV DEP does not publish.
# Plus the 2016 file pre-dates the bulk of the Marcellus campaign, so
# even a perfect join would miss most lit wells.
#
# We treat WV as 100 percent dark for v1 and surface this asymmetry as
# part of the story: the state has both well-location data and
# horizontal-production data, but they are unjoined. That IS the dark
# data verdict for the state.
wv['lit'] = False
wv['s'] = 1
wv['h'] = 0  # cannot identify horizontals in the well location file alone
wv['v'] = 5  # no spud date in this file
wv['d'] = 1
wv_clean = wv[['lat', 'lon', 'd', 'v', 's', 'h']].copy()
wv_clean['op'] = wv['RESPONSIBLE_PARTY_NAME'].fillna('UNKNOWN').astype(str)
wv_clean['fid'] = wv['PERMIT_ID']
print(f'  WV finalized: {len(wv_clean):,} (lit {(wv_clean["d"]==0).sum():,} / dark {(wv_clean["d"]==1).sum():,})')


# ============================================================
# 3. Ohio wells from REST GeoJSON
# ============================================================
print('Loading OH wells GeoJSON...')
oh = gpd.read_file(RAW/'oh_dnr/Oilgas_Wells_public.geojson')
print(f'  OH rows: {len(oh):,}')
print(f'  OH CRS: {oh.crs}')
# Filter to valid coords
oh = oh[oh.geometry.notna() & oh['WH_LAT'].notna() & oh['WH_LONG'].notna()]
oh = oh[(oh['WH_LAT'] > 30) & (oh['WH_LAT'] < 50) & (oh['WH_LONG'] > -90) & (oh['WH_LONG'] < -75)]
print(f'  OH after coord filter: {len(oh):,}')

# SLANT values in the OH layer are single-letter codes:
#   'V' = Vertical, 'H' = Horizontal, 'D' = Directional, 'O' = Other
oh['is_horz'] = oh['SLANT'].astype(str).str.strip().str.upper() == 'H'
oh['has_marcellus'] = oh['Marcellus_Shale'].notna() & (oh['Marcellus_Shale'] != 0)
oh['has_utica'] = oh['Utica_Shale'].notna() & (oh['Utica_Shale'] != 0)
oh['lit'] = oh['is_horz'] | oh['has_marcellus'] | oh['has_utica']
oh['s'] = 2
oh['h'] = oh['is_horz'].astype(int)
oh['v'] = 5  # no spud-date column
oh['d'] = (~oh['lit']).astype(int)
oh['lat'] = oh['WH_LAT'].astype(float)
oh['lon'] = oh['WH_LONG'].astype(float)
oh_clean = oh[['lat', 'lon', 'd', 'v', 's', 'h']].copy()
oh_clean['op'] = oh['CO_NAME'].fillna('UNKNOWN').astype(str)
oh_clean['fid'] = oh['API_WELLNO'].astype(str)
print(f'  OH finalized: {len(oh_clean):,} (lit {(oh_clean["d"]==0).sum():,} / dark {(oh_clean["d"]==1).sum():,})')


# ============================================================
# 4. Basin clip envelope from EIA Appalachian shales
# ============================================================
print('Building basin envelope from EIA Appalachian shales...')
eia = gpd.read_file(f'zip://{RAW}/eia_shale/TightOil_ShaleGas_Plays_Lower48.zip')
ap = eia[eia['Basin'].str.contains('Appalach', case=False, na=False)]
print(f'  Appalachian polygons: {len(ap)} - {list(ap["Shale_play"])}')
basin_geom = unary_union(ap.geometry.tolist())
basin_gdf = gpd.GeoDataFrame(
    {'name': ['Appalachian Basin (EIA Marcellus + Utica + Devonian + Chattanooga union)']},
    geometry=[basin_geom],
    crs=ap.crs,
).to_crs('EPSG:4269')
print(f'  basin envelope bounds: {basin_gdf.total_bounds}')


# ============================================================
# 5. Spatial clip wells to basin
# ============================================================
print('Clipping all states to basin...')
combined = pd.concat([pa_all, wv_clean, oh_clean], ignore_index=True)
combined_g = gpd.GeoDataFrame(
    combined,
    geometry=gpd.points_from_xy(combined['lon'], combined['lat']),
    crs='EPSG:4269',
)
in_basin = gpd.sjoin(combined_g, basin_gdf, predicate='within', how='inner').drop(columns=['index_right', 'name'])
print(f'  in-basin wells: {len(in_basin):,}')
print(f'  by state in basin: PA {(in_basin["s"]==0).sum():,} | WV {(in_basin["s"]==1).sum():,} | OH {(in_basin["s"]==2).sum():,}')


# ============================================================
# 6. Emit outputs
# ============================================================
print('Writing outputs...')
in_basin['lat'] = in_basin['lat'].round(4)
in_basin['lon'] = in_basin['lon'].round(4)
wells_csv = in_basin[['lat', 'lon', 'd', 'v', 's', 'h']]
wells_csv.to_csv(OUT/'wells.csv', index=False)
print(f'  wrote {OUT/"wells.csv"} ({len(wells_csv):,} rows)')

basin_gdf.to_file(OUT/'appalachia_basin.json', driver='GeoJSON')
print(f'  wrote {OUT/"appalachia_basin.json"}')

# State outlines (PA, WV, OH)
import urllib.request
states_url = 'https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json'
try:
    with urllib.request.urlopen(states_url, timeout=30) as r:
        states_geo = json.loads(r.read())
    keep = [f for f in states_geo['features']
            if f['properties']['name'] in ('Pennsylvania', 'West Virginia', 'Ohio')]
    states_geo['features'] = keep
    (OUT/'appalachia_states.json').write_text(json.dumps(states_geo))
    print(f'  wrote {OUT/"appalachia_states.json"} ({len(keep)} states)')
except Exception as e:
    print(f'  state fetch FAIL: {e}')

# Summary
total = int(len(in_basin))
dark = int((in_basin['d'] == 1).sum())
lit = total - dark

def state_summary(s_code):
    sub = in_basin[in_basin['s'] == s_code]
    return {
        'total': int(len(sub)),
        'dark': int((sub['d'] == 1).sum()),
        'horizontal_flagged': int(sub['h'].sum()),
        'pct_dark': round(100.0 * (sub['d'] == 1).sum() / len(sub), 1) if len(sub) else 0,
    }

vintage_global = in_basin['v'].value_counts().to_dict()


def top_ops(state_code, n=15):
    sub = in_basin[in_basin['s'] == state_code]
    if 'op' not in sub.columns or len(sub) == 0:
        return []
    df = sub.groupby('op', dropna=False).agg(total=('d', 'count'), dark=('d', 'sum')).reset_index()
    df['pct_dark'] = (100.0 * df['dark'] / df['total']).round(1)
    df = df.sort_values('total', ascending=False).head(n)
    return df.to_dict(orient='records')

summary = {
    'total_wells': total,
    'dark': dark,
    'lit': lit,
    'pct_dark': round(100.0 * dark / total, 1) if total else 0,
    'by_state': {
        'PA': state_summary(0),
        'WV': state_summary(1),
        'OH': state_summary(2),
    },
    'vintage_distribution': {str(k): int(v) for k, v in vintage_global.items()},
    'top_operators_pa': top_ops(0),
    'top_operators_wv': top_ops(1),
    'top_operators_oh': top_ops(2),
    'notes': [
        'Basin clip: EIA Tight Oil + Shale Plays Lower48 (Dec 2021), filtered to Basin=Appalachian. Union of Marcellus + Utica + Devonian (Ohio) + Chattanooga shale polygons.',
        'Lit/dark proxies are state-asymmetric. PA uses UNCONVENTI flag + horizontal well config (the cleanest of the three). OH uses SLANT field (V/H/D/O codes) + Marcellus/Utica formation depth flags. WV is a special case: its 2016 well location file uses PERMIT_ID while its 2024 H6A horizontal production file uses 10-digit API numbers; the two do not link without a cross-reference table WV DEP does not publish. WV is therefore counted 100 percent dark; that is the dark-data verdict for the state.',
        'PA Historic Oil and Gas Wells (WPA-mapped pre-regulatory wells, 30,527) are pre-1860 to ca. 1900s. All counted dark, all bucketed pre-1980.',
        'WV and OH have no parseable spud-date column on the public well files. Both states default to vintage bucket 5 (unknown). Vintage signal lives mostly in PA.',
    ],
}
(OUT/'summary.json').write_text(json.dumps(summary, indent=2))
print(f'  wrote {OUT/"summary.json"}')
print()
print(f'TOTAL: {total:,} basin-clipped wells | dark {dark:,} ({summary["pct_dark"]}%)')
for st in ['PA', 'WV', 'OH']:
    s = summary['by_state'][st]
    print(f'  {st}: {s["total"]:,}  ({s["pct_dark"]}% dark, {s["horizontal_flagged"]:,} horizontals)')
