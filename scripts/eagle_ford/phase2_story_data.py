"""
Phase 2: build the Eagle Ford basin-06 story bundle.

This basin SHIPS WITHOUT A wells.csv. That absence is the dataset. The
five cooperative basins in the series (KS, Permian, Williston, Anadarko,
Appalachia) covered the territory of "what dark data looks like at
varying levels". Eagle Ford ships the territory of "what an inaccessible
regulator looks like".

Inputs:
  data/raw/usgs_eagle_ford/EagleFordAUs.geojson  (7 AU polygons, 4269)
  data/raw/eia_dpr/dpr-data.xlsx                 (EIA monthly DPR)
  data/raw/census/cb_2024_us_county_5m.zip       (TIGER counties)
  data/raw/census/cb_2024_us_state_5m.zip        (TIGER states)

Outputs:
  darkdata/eagle_ford/data/eagle_ford_aus.json          (USGS polygons)
  darkdata/eagle_ford/data/eagle_ford_counties.json     (76 TX counties)
  darkdata/eagle_ford/data/state_outline.json           (TX outline)
  darkdata/eagle_ford/data/eia_eagle_ford_monthly.json  (DPR time series)
  darkdata/eagle_ford/data/regulatory_comparison.json   (6-regulator rank)
  darkdata/eagle_ford/data/summary.json                 (meta-summary)
"""
import warnings; warnings.filterwarnings('ignore')
import json
from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.ops import unary_union

ROOT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo')
RAW = ROOT / 'data/raw'
SITE = Path('/Users/olatunde/CoWorker/Geoworks/salamituns.github.io')
OUT = SITE / 'darkdata/eagle_ford/data'
OUT.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. USGS Eagle Ford Group AU polygons
# ============================================================
print('Loading Eagle Ford AUs...')
ef = gpd.read_file(RAW/'usgs_eagle_ford/EagleFordAUs.geojson').to_crs('EPSG:4269')
print(f'  {len(ef)} AU polygons')

# Dissolved envelope for the basin clip
ef_union = unary_union(ef.geometry.tolist())
ef_envelope = gpd.GeoDataFrame(
    {'name': ['Eagle Ford Group AU envelope (USGS, 7 AUs unioned)']},
    geometry=[ef_union],
    crs='EPSG:4269',
)

# Per-AU FeatureCollection (with assessment names) for storymap layer styling
ef_per_au = ef.copy()
ef_per_au = ef_per_au.rename(columns={'ASSESSNAME': 'au_name'})

(OUT/'eagle_ford_aus.json').write_text(ef_per_au[['au_name', 'geometry']].to_json())
print(f'  wrote {OUT/"eagle_ford_aus.json"}')

# ============================================================
# 2. Texas counties intersecting the basin
# ============================================================
print('Loading Texas counties...')
counties = gpd.read_file(f'zip://{RAW}/census/cb_2024_us_county_5m.zip')
tx = counties[counties['STATEFP'] == '48'].to_crs('EPSG:4269')
mask = tx.geometry.intersects(ef_union)
ef_counties = tx[mask][['NAME', 'GEOID', 'geometry']].copy()
print(f'  {len(ef_counties)} counties intersect the EF AU envelope')
(OUT/'eagle_ford_counties.json').write_text(ef_counties.to_json())
print(f'  wrote {OUT/"eagle_ford_counties.json"}')

# Texas state outline
print('Loading Texas state outline...')
states = gpd.read_file(f'zip://{RAW}/census/cb_2024_us_state_5m.zip')
tx_outline = states[states['STATEFP'] == '48'][['NAME', 'geometry']].to_crs('EPSG:4269')
(OUT/'state_outline.json').write_text(tx_outline.to_json())
print(f'  wrote {OUT/"state_outline.json"}')

# ============================================================
# 3. EIA DPR Eagle Ford monthly data
# ============================================================
print('Loading EIA DPR Eagle Ford...')
df = pd.read_excel(RAW/'eia_dpr/dpr-data.xlsx', sheet_name='Eagle Ford Region', header=[0, 1])
# Flatten the multi-index columns
df.columns = [
    f'{a if not str(a).startswith("Unnamed") else ""}_{b}'.strip('_').lower().replace(' ', '_')
    for a, b in df.columns
]
print(f'  Eagle Ford rows: {len(df)}')
print(f'  Eagle Ford columns: {list(df.columns)[:8]}')

# Identify and rename canonical columns
col_map = {
    'eagle_ford_region_month': 'month',
    'eagle_ford_region_rig_count': 'rig_count',
    'oil_(bbl/d)_production_per_rig': 'oil_per_rig_bbl',
    'oil_(bbl/d)_legacy_production_change': 'oil_legacy_change_bbl',
    'oil_(bbl/d)_total_production': 'oil_total_bbl',
    'natural_gas_(mcf/d)_production_per_rig': 'gas_per_rig_mcf',
    'natural_gas_(mcf/d)_legacy_production_change': 'gas_legacy_change_mcf',
    'natural_gas_(mcf/d)_total_production': 'gas_total_mcf',
}
# Rename only the columns we recognize
df = df.rename(columns=col_map)
df = df[df['month'].apply(lambda x: hasattr(x, 'year') or (isinstance(x, str) and x[:4].isdigit()))]
df['month'] = pd.to_datetime(df['month'])
df = df.sort_values('month').reset_index(drop=True)

monthly = []
for _, r in df.iterrows():
    monthly.append({
        'month': r['month'].strftime('%Y-%m'),
        'rig_count': float(r.get('rig_count', 0)) if pd.notna(r.get('rig_count')) else None,
        'oil_total_bbl': float(r.get('oil_total_bbl', 0)) if pd.notna(r.get('oil_total_bbl')) else None,
        'gas_total_mcf': float(r.get('gas_total_mcf', 0)) if pd.notna(r.get('gas_total_mcf')) else None,
    })

(OUT/'eia_eagle_ford_monthly.json').write_text(json.dumps({
    'source': 'EIA Drilling Productivity Report (DPR), Eagle Ford Region',
    'unit_oil': 'barrels/day',
    'unit_gas': 'thousand cubic feet/day',
    'data': monthly,
}, indent=2))
print(f'  wrote {OUT/"eia_eagle_ford_monthly.json"} ({len(monthly)} months)')

# ============================================================
# 4. Regulatory comparison: data accessibility ranking across the 6 basins
# ============================================================
# Numbers come from the actual phase 0/1 experience of each basin pull.
# This is a ranking, not a clinical measurement.
print('Building regulatory comparison...')
regulators = [
    {
        'state': 'OK',
        'agency': 'OK Corporation Commission (OCC)',
        'basin': 'Anadarko',
        'access_score': 100,
        'method': 'Direct CMS URLs',
        'time_to_first_byte_s': 0.4,
        'wells_per_minute': 600000,
        'notes': 'RBDMS shapefile, completion XLSX, orphan list, all on oklahoma.gov. 348 MB pulled in 11 seconds.',
    },
    {
        'state': 'ND',
        'agency': 'NDIC Oil & Gas Division',
        'basin': 'Williston',
        'access_score': 100,
        'method': 'Direct shapefile',
        'time_to_first_byte_s': 0.5,
        'wells_per_minute': 200000,
        'notes': 'OGD_Wells.zip + OGD_Horizontals.zip, single click each. Cleanest per-state shapefile in the series.',
    },
    {
        'state': 'PA',
        'agency': 'PA DEP via PASDA',
        'basin': 'Appalachia',
        'access_score': 95,
        'method': 'Direct shapefile + UNCONVENTI flag',
        'time_to_first_byte_s': 0.7,
        'wells_per_minute': 60000,
        'notes': 'Conv/Unconv shapefile + Historic WPA wells, single click each. The only state that publishes its own dark/lit verdict (UNCONVENTI Y/N).',
    },
    {
        'state': 'KS',
        'agency': 'Kansas Geological Survey (KGS)',
        'basin': 'Kansas + Anadarko',
        'access_score': 90,
        'method': 'Bulk CSV + LAS archive',
        'time_to_first_byte_s': 1.0,
        'wells_per_minute': 50000,
        'notes': 'Bulk well CSV (183 MB) + KGS public LAS archive (24K logs). Survey-driven, research-friendly.',
    },
    {
        'state': 'OH',
        'agency': 'OH DNR DOG_Services',
        'basin': 'Appalachia',
        'access_score': 75,
        'method': 'ArcGIS REST, paginated',
        'time_to_first_byte_s': 1.2,
        'wells_per_minute': 90000,
        'notes': 'No bulk ZIP. Public REST endpoint with maxRecordCount 1000. 242K wells in 243 paginated requests, ~3 minutes total.',
    },
    {
        'state': 'WV',
        'agency': 'WV DEP Office of Oil and Gas',
        'basin': 'Appalachia',
        'access_score': 50,
        'method': 'Direct XLSX, but unjoined',
        'time_to_first_byte_s': 0.9,
        'wells_per_minute': 200000,
        'notes': '2016 well-location XLSX downloads cleanly. But its PERMIT_ID does not link to the H6A horizontal-production API. The data exists; it is not joined.',
    },
    {
        'state': 'MT',
        'agency': 'MT BOGC',
        'basin': 'Williston',
        'access_score': 75,
        'method': 'Direct shapefile, no horizontal flag',
        'time_to_first_byte_s': 1.0,
        'wells_per_minute': 200000,
        'notes': 'WellSurface shapefile downloads, but ships no horizontal-well indicator. Half the lit/dark proxy is unreachable.',
    },
    {
        'state': 'NM',
        'agency': 'NM OCD',
        'basin': 'Permian',
        'access_score': 80,
        'method': 'Direct shapefile + ONGARD',
        'time_to_first_byte_s': 0.8,
        'wells_per_minute': 80000,
        'notes': 'New Mexico OCD ONGARD wells download, plus PRE-ONGARD placeholder for legacy operators that never migrated.',
    },
    {
        'state': 'TX',
        'agency': 'TX Railroad Commission',
        'basin': 'Eagle Ford + Permian (TX) + Anadarko (TX)',
        'access_score': 5,
        'method': 'JSF/PrimeFaces session portal + EBCDIC mainframe',
        'time_to_first_byte_s': None,
        'wells_per_minute': 0,
        'notes': 'Bulk well-data downloads live behind a Java Server Faces session portal with 5-minute timeouts. Older records are EBCDIC mainframe dumps. Per-well lat/lon, vintage, and dark/lit are not pullable without browser automation. The state did not migrate.',
    },
]

(OUT/'regulatory_comparison.json').write_text(json.dumps({
    'source': 'darkdata series experience report (basins 01-06)',
    'access_score_definition': '0 = inaccessible, 100 = direct CMS download',
    'time_to_first_byte_s_definition': 'seconds from issuing HEAD to first response byte (representative)',
    'regulators': regulators,
}, indent=2))
print(f'  wrote {OUT/"regulatory_comparison.json"} ({len(regulators)} regulators)')

# ============================================================
# 5. Summary
# ============================================================
print('Building summary...')

# Compute a couple of useful aggregates from the EIA data
oil_2014 = next((m for m in monthly if m['month'].startswith('2014-12')), None)
oil_2024 = next((m for m in monthly if m['month'].startswith('2024-12')), None)
oil_peak_month = max((m for m in monthly if m['oil_total_bbl']), key=lambda m: m['oil_total_bbl']) if monthly else None
rig_peak_month = max((m for m in monthly if m['rig_count']), key=lambda m: m['rig_count']) if monthly else None

summary = {
    'total_wells': None,
    'pct_dark': None,
    'series_position': '06 of 06 (finale)',
    'reason_no_wells_csv': (
        'TX RRC publishes its bulk well data through a JSF/PrimeFaces session '
        'portal with 5-minute timeouts, backed by EBCDIC mainframe dumps. '
        'Per-well lat/lon, vintage, and dark/lit are not extractable without '
        'browser automation we do not perform. Eagle Ford ships without per-well '
        'data on purpose.'
    ),
    'basin_au_count': int(len(ef)),
    'tx_counties_intersected': int(len(ef_counties)),
    'eia_dpr_months': len(monthly),
    'eia_dpr_period_start': monthly[0]['month'] if monthly else None,
    'eia_dpr_period_end': monthly[-1]['month'] if monthly else None,
    'eagle_ford_oil_peak': {
        'month': oil_peak_month['month'] if oil_peak_month else None,
        'bbl_per_day': oil_peak_month['oil_total_bbl'] if oil_peak_month else None,
    },
    'eagle_ford_rig_peak': {
        'month': rig_peak_month['month'] if rig_peak_month else None,
        'rig_count': rig_peak_month['rig_count'] if rig_peak_month else None,
    },
    'oil_2014_dec_bbl_per_day': oil_2014['oil_total_bbl'] if oil_2014 else None,
    'oil_2024_dec_bbl_per_day': oil_2024['oil_total_bbl'] if oil_2024 else None,
    'notes': [
        'Basin clip: USGS Eagle Ford Group Assessment Unit boundaries (2018), 7 AUs unioned.',
        'No per-well data is published. The basin map shows only the AU polygon and the 76 Texas counties that intersect it.',
        'EIA Drilling Productivity Report provides aggregate monthly Eagle Ford production and rig count, January 2007 to present.',
        'The regulatory_comparison.json file ranks 9 state regulators by data accessibility based on the actual experience of pulling each basin in this series.',
        'Per-well dark/lit cannot be measured for Texas. The regulatory architecture itself is the dark-data verdict.',
    ],
}
(OUT/'summary.json').write_text(json.dumps(summary, indent=2))
print(f'  wrote {OUT/"summary.json"}')
print()
print('=== SUMMARY ===')
print(f'  AU polygons: {len(ef)}')
print(f'  TX counties intersecting: {len(ef_counties)}')
print(f'  EIA months: {len(monthly)}')
if oil_peak_month:
    print(f'  Oil peak: {oil_peak_month["month"]} at {oil_peak_month["oil_total_bbl"]:,.0f} bbl/d')
if rig_peak_month:
    print(f'  Rig peak: {rig_peak_month["month"]} at {rig_peak_month["rig_count"]:.0f} rigs')
