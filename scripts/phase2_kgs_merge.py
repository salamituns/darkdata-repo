"""
Phase 2: join the 'wells with public LAS' universe into the master well list.

Master inventory (KGS ArcGIS bulk export, 515K rows) is the full universe of
permitted/drilled/plugged Kansas wells. A subset have been drilled and a subset
of those have a publicly-accessible digitized LAS file in the KGS log archive.

This script:
  1. Loads both files
  2. Normalises the API key on both sides
  3. Flags each master-list row with has_las (bool)
  4. Parses spud year and builds vintage buckets
  5. Computes coverage stats by status, vintage decade, and county
  6. Writes a merged geo-ready CSV for the mapping phase.

Outputs:
  data/processed/phase2_kgs_master_with_las.csv   (one row per well, geo + LAS flag)
  data/processed/phase2_coverage_summary.json     (headline stats)
"""
import pandas as pd
import json
from pathlib import Path

RAW = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo/data/raw/kgs')
PROC = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo/data/processed')
PROC.mkdir(parents=True, exist_ok=True)

# Decide the "drilled universe" by status. Exclude paper wells + cancelled.
PAPER_STATUSES = {
    'Approved Intent to Drill',
    'Expired Intent to Drill (C-1)',
    'Cancelled API Number',
    '',  # unpopulated status
}

# ---- Load master list ----------------------------------------------------
master = pd.read_csv(RAW / 'kgs_master_wells.csv', low_memory=False)
print(f"master rows: {len(master):,}")
print(f"master unique API_NUM_NODASH: {master['API_NUM_NODASH'].nunique():,}")

# Normalise API: strip whitespace, drop '.0' suffix, cast to string
def clean_api(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    if s.endswith('.0'):
        s = s[:-2]
    return s if s else None

master['api_key'] = master['API_NUM_NODASH'].apply(clean_api)
master = master.dropna(subset=['api_key']).copy()
master = master.drop_duplicates(subset=['api_key']).copy()
print(f"master unique wells after clean+dedupe: {len(master):,}")

# Parse spud year
master['spud_year'] = pd.to_datetime(master['Spud Date'], errors='coerce').dt.year
print(f"master wells with spud year: {master['spud_year'].notna().sum():,}  "
      f"({100 * master['spud_year'].notna().mean():.1f}%)")

# Drilled universe: exclude paper/cancelled
master['Status'] = master['Status'].fillna('').astype(str)
master['is_paper'] = master['Status'].isin(PAPER_STATUSES)
drilled = master[~master['is_paper']].copy()
print(f"drilled-universe (non-paper) wells: {len(drilled):,}")

# ---- Load LAS universe --------------------------------------------------
las_wells = pd.read_csv(PROC / 'phase1_kgs_wells.csv', low_memory=False)
las_wells['api_key'] = las_wells['API_NUM_NODASH'].apply(clean_api)
las_wells = las_wells.dropna(subset=['api_key']).drop_duplicates('api_key')
print(f"LAS-available unique wells: {len(las_wells):,}")

las_keys = set(las_wells['api_key'])

# ---- Merge --------------------------------------------------------------
master['has_las'] = master['api_key'].isin(las_keys)
drilled['has_las'] = drilled['api_key'].isin(las_keys)

match_in_master = master['has_las'].sum()
print(f"\nLAS keys that match a master-list well: {match_in_master:,} / "
      f"{len(las_keys):,}  ({100 * match_in_master / len(las_keys):.1f}%)")

# ---- Coverage stats -----------------------------------------------------
def pct(n, d):
    return 100 * n / d if d else 0.0

summary = {
    'denominators': {
        'master_unique_wells': int(len(master)),
        'drilled_universe_wells': int(len(drilled)),
        'paper_wells_excluded': int(master['is_paper'].sum()),
        'las_available_wells': int(len(las_wells)),
    },
    'headline': {
        'pct_of_master_with_las': round(pct(master['has_las'].sum(), len(master)), 2),
        'pct_of_drilled_with_las': round(pct(drilled['has_las'].sum(), len(drilled)), 2),
    },
}

# By decade
drilled['decade'] = (drilled['spud_year'] // 10 * 10).astype('Int64')
by_decade = (drilled[drilled['spud_year'].notna()]
             .groupby('decade')
             .agg(total=('api_key', 'size'), with_las=('has_las', 'sum'))
             .reset_index())
by_decade['pct_with_las'] = (100 * by_decade['with_las'] / by_decade['total']).round(1)
summary['by_decade'] = by_decade.to_dict(orient='records')

# By county
by_county = (drilled
             .groupby('County')
             .agg(total=('api_key', 'size'), with_las=('has_las', 'sum'))
             .reset_index())
by_county['pct_with_las'] = (100 * by_county['with_las'] / by_county['total']).round(1)
by_county = by_county.sort_values('total', ascending=False)
summary['county_top20_by_well_count'] = by_county.head(20).to_dict(orient='records')
summary['county_best_coverage_top10'] = (by_county[by_county['total'] >= 200]
                                         .sort_values('pct_with_las', ascending=False)
                                         .head(10).to_dict(orient='records'))
summary['county_worst_coverage_top10'] = (by_county[by_county['total'] >= 200]
                                          .sort_values('pct_with_las', ascending=True)
                                          .head(10).to_dict(orient='records'))

# ---- Console report ------------------------------------------------------
print('\n' + '='*70)
print('COVERAGE HEADLINE')
print('='*70)
print(f"Master unique wells:        {len(master):,}")
print(f"Drilled universe:           {len(drilled):,}  "
      f"(excluded {master['is_paper'].sum():,} paper/cancelled)")
print(f"LAS-available wells:        {len(las_wells):,}")
print()
print(f"LAS / master:               {summary['headline']['pct_of_master_with_las']:.2f}%  "
      f"(i.e. {100 - summary['headline']['pct_of_master_with_las']:.2f}% dark)")
print(f"LAS / drilled:              {summary['headline']['pct_of_drilled_with_las']:.2f}%  "
      f"(i.e. {100 - summary['headline']['pct_of_drilled_with_las']:.2f}% dark)")
print()
print("By decade (drilled wells):")
for row in summary['by_decade']:
    if pd.notna(row['decade']):
        print(f"  {int(row['decade'])}s:  {int(row['total']):>7,}  "
              f"with LAS {int(row['with_las']):>6,}  ({row['pct_with_las']:>5.1f}%)")

# ---- Persist -------------------------------------------------------------
keep_cols = ['api_key', 'Status', 'WELL_TYPE', 'Current Operator', 'County',
             'spud_year', 'Latitude (NAD27)', 'Longitude (NAD27)',
             'has_las', 'is_paper']
master[keep_cols].rename(columns={
    'Latitude (NAD27)': 'latitude',
    'Longitude (NAD27)': 'longitude',
}).to_csv(PROC / 'phase2_kgs_master_with_las.csv', index=False)

with open(PROC / 'phase2_coverage_summary.json', 'w') as f:
    json.dump(summary, f, indent=2, default=str)

print(f"\nWrote: {PROC}/phase2_kgs_master_with_las.csv  ({len(master):,} rows)")
print(f"Wrote: {PROC}/phase2_coverage_summary.json")
