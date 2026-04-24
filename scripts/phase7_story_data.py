"""
Phase 7: Export minimal data bundles for the /darkdata/story.html experience.

Two outputs, both small enough to ship over HTTPS:
  data/wells.csv        : lat, lon, d (dark flag), v (vintage bucket)
  data/ks_counties.json : county polygons + pct_lit + total + lit

Vintage buckets:
  0 pre-1980   1 1980s   2 1990s   3 2000s   4 2010+   5 unknown
"""
import warnings; warnings.filterwarnings('ignore')
import json
import pandas as pd
import geopandas as gpd

ROOT = '/Users/olatunde/CoWorker/Geoworks'
PROC = f'{ROOT}/darkdata-repo/data/processed'
COUNTIES = f'{ROOT}/data/raw/census_boundaries/gz_2010_us_050_00_5m.json'
OUT = f'{ROOT}/salamituns.github.io/darkdata/data'

import os; os.makedirs(OUT, exist_ok=True)

# ---- Wells ---------------------------------------------------------------
df = pd.read_csv(f'{PROC}/phase2_kgs_master_with_las.csv', low_memory=False)
df = df[~df['is_paper']].copy()
df = df.dropna(subset=['latitude','longitude'])
df = df[df['latitude'].between(36.9, 40.1) & df['longitude'].between(-102.2, -94.4)]

def vbucket(y):
    if pd.isna(y): return 5
    if y < 1980:  return 0
    if y < 1990:  return 1
    if y < 2000:  return 2
    if y < 2010:  return 3
    return 4
df['v'] = df['spud_year'].apply(vbucket).astype('int8')
df['d'] = (~df['has_las']).astype('int8')
df['lat'] = df['latitude'].round(4)
df['lon'] = df['longitude'].round(4)

wells = df[['lat','lon','d','v']]
print(f'wells rows: {len(wells):,}')
print(wells['d'].value_counts().to_string())
print(wells['v'].value_counts().sort_index().to_string())

path_csv = f'{OUT}/wells.csv'
wells.to_csv(path_csv, index=False, float_format='%.4f')
size_mb = os.path.getsize(path_csv) / 1e6
print(f'wrote {path_csv}  ({size_mb:.1f} MB)')

# ---- County aggregation + polygons --------------------------------------
county = (df.groupby('County')
            .agg(total=('api_key','size'), lit=('has_las','sum'))
            .assign(pct_lit=lambda d: 100*d['lit']/d['total'])
            .reset_index())
county['KEY'] = county['County'].str.upper().str.strip()

counties = gpd.read_file(COUNTIES, encoding='latin-1')
ks = counties[counties['STATE'] == '20'].copy()
ks['KEY'] = ks['NAME'].str.upper().str.strip()
ks = ks.merge(county[['KEY','total','lit','pct_lit']], on='KEY', how='left')
ks['total'] = ks['total'].fillna(0).astype(int)
ks['lit']   = ks['lit'].fillna(0).astype(int)
ks['pct_lit'] = ks['pct_lit'].fillna(0).round(2)

# Simplify geometry for web (1 km tolerance in degrees ≈ 0.01)
ks['geometry'] = ks['geometry'].simplify(0.01, preserve_topology=True)
ks = ks[['NAME','total','lit','pct_lit','geometry']].rename(columns={'NAME':'name'})

path_geo = f'{OUT}/ks_counties.json'
ks.to_file(path_geo, driver='GeoJSON')
size_kb = os.path.getsize(path_geo) / 1e3
print(f'wrote {path_geo}  ({size_kb:.0f} KB)')

# ---- Summary stats (for JS injection / sanity) --------------------------
summary = {
    'total_drilled': int(len(df)),
    'lit': int(df['has_las'].sum()),
    'dark': int((~df['has_las']).sum()),
    'pct_lit': float(round(100*df['has_las'].sum()/len(df), 2)),
    'orphan_total': int((df['Current Operator'].fillna('').str.strip() == '').sum()),
    'orphan_dark': int(((df['Current Operator'].fillna('').str.strip() == '') & ~df['has_las']).sum()),
    'counties_below_5pct': int((county.query('total >= 50')['pct_lit'] < 5).sum()),
    'counties_total_50plus': int((county['total'] >= 50).sum()),
}
summary['orphan_share_of_dark'] = round(100*summary['orphan_dark']/summary['dark'], 1)
path_json = f'{OUT}/summary.json'
with open(path_json, 'w') as f: json.dump(summary, f, indent=2)
print(f'wrote {path_json}')
print(json.dumps(summary, indent=2))
