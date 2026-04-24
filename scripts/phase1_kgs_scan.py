"""
Phase 1: scan the KGS LAS inventory, understand what we have.

Two input files (ks_las_files.txt, las65366.txt) are both CSVs pulled
from the Kansas Geological Survey WebDocs well-log archive. Same
schema; may overlap. Each row is ONE LAS file, not one well: a single
well can have multiple logging runs.

Outputs:
  - phase1_kgs_summary.json: counts, coverage, URL-year distribution
  - phase1_kgs_wells.csv   : deduped to one row per unique well
"""
import pandas as pd
import re
import json
from pathlib import Path

RAW = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo/data/raw/kgs')
PROC = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo/data/processed')

# Load both inventory files, union them
a = pd.read_csv(RAW / 'ks_las_files.txt')
b = pd.read_csv(RAW / 'las65366.txt')
# Normalize header casing for KGS_ID
a.columns = [c.strip().replace(' ', '_') for c in a.columns]
b.columns = [c.strip().replace(' ', '_') for c in b.columns]
print(f"ks_las_files.txt: {len(a):,} rows")
print(f"las65366.txt:      {len(b):,} rows")

all_rows = pd.concat([a, b], ignore_index=True)
all_rows = all_rows.drop_duplicates(subset=['URL'])
print(f"union (unique URLs): {len(all_rows):,}")

# Extract filing year from URL where present
# Patterns observed: /kcc_logs_YYYY/... , /WellLogs/YYYY/... , /WellLogs/{TwnRng}/...
def extract_year(url: str):
    if not isinstance(url, str):
        return None
    m = re.search(r'/(?:kcc_logs_|WellLogs/)(\d{4})/', url)
    if m:
        y = int(m.group(1))
        if 1900 <= y <= 2030:
            return y
    return None

all_rows['url_year'] = all_rows['URL'].apply(extract_year)
print(f"\nRows with a year in the URL: {all_rows['url_year'].notna().sum():,}  "
      f"({100 * all_rows['url_year'].notna().mean():.1f}%)")

if all_rows['url_year'].notna().any():
    yr = all_rows['url_year'].dropna().astype(int)
    print(f"Year range: {yr.min()}–{yr.max()}")
    print("Decade distribution:")
    for decade, n in yr.map(lambda y: (y // 10) * 10).value_counts().sort_index().items():
        print(f"  {decade}s: {n:,}")

# Dedupe to one row per well (use KGS_ID + API where available)
all_rows['key'] = all_rows['KGS_ID'].astype(str) + '|' + all_rows['API_NUM_NODASH'].astype(str)
wells = all_rows.drop_duplicates(subset=['key']).copy()
print(f"\nUnique wells (KGS_ID+API dedupe): {len(wells):,}")

# Numeric coords
for col in ['Latitude', 'Longitude']:
    wells[col] = pd.to_numeric(wells[col], errors='coerce')
wells = wells[wells['Latitude'].between(36.9, 40.1)
              & wells['Longitude'].between(-102.2, -94.5)]
print(f"Wells inside Kansas bounding box: {len(wells):,}")

# Unique operators (LAS-available universe)
print(f"\nUnique operators named:         {wells['Operator'].nunique():,}")
print(f"Top 10 operators by LAS-file count in inventory:")
print(all_rows['Operator'].value_counts().head(10).to_string())

# Persist processed output
PROC.mkdir(parents=True, exist_ok=True)
wells.to_csv(PROC / 'phase1_kgs_wells.csv', index=False)
summary = {
    'las_files_rows_total': int(len(all_rows)),
    'las_files_rows_with_year': int(all_rows['url_year'].notna().sum()),
    'unique_wells': int(len(wells)),
    'unique_operators': int(wells['Operator'].nunique()),
    'year_coverage_pct': float(100 * all_rows['url_year'].notna().mean()),
}
with open(PROC / 'phase1_kgs_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f"\nWrote: {PROC}/phase1_kgs_wells.csv  ({len(wells):,} wells)")
print(f"Wrote: {PROC}/phase1_kgs_summary.json")
