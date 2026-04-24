"""
Phase 2: pull NM OCD wells for Permian counties from the live ArcGIS REST.

Endpoint: gis.emnrd.nm.gov/arcgis/rest/services/OCDView/API_Export/MapServer/0

NM Permian counties (FIPS):
    Lea = 25, Eddy = 15, Chaves = 5, Roosevelt = 41

NM has no separate "well log inventory" layer (unlike TX RRC Layer 8).
Every NM well has a `files` URL into the OCD imaging portal: but it's
boilerplate, not a lit proxy. Lit/dark classification is deferred to Phase 3
using year_spudded >= 2002 as a digital-filing-era floor (per OCD methodology).

Output:
  data/raw/nm_ocd/permian_wells.csv
    API, name, status, operator, county, lat, lon, year_spudded,
    spud_date_ms, md, tvd, directional, plug_date_ms, files_url
  data/raw/nm_ocd/pull_metadata.json

Usage:  python3 phase2_nm_ocd_pull.py
"""
import csv
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

OUT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo/data/raw/nm_ocd')
OUT.mkdir(parents=True, exist_ok=True)

BASE = ('https://gis.emnrd.nm.gov/arcgis/rest/services/'
        'OCDView/API_Export/MapServer/0')

# NM Permian counties: FIPS codes
NM_PERMIAN_FIPS = [5, 15, 25, 41]  # Chaves, Eddy, Lea, Roosevelt
WHERE = f'county_code IN ({",".join(str(c) for c in NM_PERMIAN_FIPS)})'

OUT_FIELDS = [
    'id', 'name', 'status', 'status_code', 'ogrid_name',
    'county_code', 'county', 'latitude', 'longitude',
    'year_spudded', 'spud_date', 'measured_vertical_depth',
    'true_vertical_depth', 'directional_status', 'plug_date',
    'files',
]

UA = 'darkdata-research/0.1 (Tee Salami; research; salamituns.github.io)'
PAGE_SIZE = 3000  # API_Export maxRecordCount
REQUEST_SLEEP_S = 0.35


def fetch_json(url: str, timeout: int = 90) -> dict:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def paginated_pull() -> list[dict]:
    base_params = {
        'where': WHERE,
        'outFields': ','.join(OUT_FIELDS),
        'returnGeometry': 'false',
        'outSR': '4326',
        'f': 'json',
        'resultRecordCount': PAGE_SIZE,
    }
    count = fetch_json(
        f'{BASE}/query?'
        + urllib.parse.urlencode({**base_params, 'returnCountOnly': 'true'})
    ).get('count')
    print(f'  target rows: {count:,}', file=sys.stderr, flush=True)

    rows: list[dict] = []
    offset = 0
    page = 0
    while True:
        params = {**base_params, 'resultOffset': offset,
                  'orderByFields': 'OBJECTID ASC'}
        url = f'{BASE}/query?' + urllib.parse.urlencode(params)
        try:
            data = fetch_json(url)
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504):
                print(f'    retrying after {e.code}...', file=sys.stderr)
                time.sleep(5)
                data = fetch_json(url)
            else:
                raise
        feats = data.get('features', [])
        if not feats:
            break
        for feat in feats:
            rows.append(dict(feat['attributes']))
        page += 1
        offset += len(feats)
        if page % 5 == 0 or offset >= count:
            pct = 100 * offset / count if count else 100
            print(f'    page {page:>3} · offset {offset:>7,} / {count:,} '
                  f'({pct:>5.1f}%)', file=sys.stderr, flush=True)
        if not data.get('exceededTransferLimit') and len(feats) < PAGE_SIZE:
            break
        time.sleep(REQUEST_SLEEP_S)
    return rows


def normalise(rows: list[dict]) -> list[dict]:
    """Rename to the CSV schema."""
    out = []
    for r in rows:
        out.append({
            'API': r.get('id'),
            'name': r.get('name'),
            'status': r.get('status'),
            'status_code': (r.get('status_code') or '').strip(),
            'operator': r.get('ogrid_name'),
            'county_fips': r.get('county_code'),
            'county': r.get('county'),
            'lat': r.get('latitude'),
            'lon': r.get('longitude'),
            'year_spudded': r.get('year_spudded'),
            'spud_date_ms': r.get('spud_date'),
            'md': r.get('measured_vertical_depth'),
            'tvd': r.get('true_vertical_depth'),
            'directional': r.get('directional_status'),
            'plug_date_ms': r.get('plug_date'),
            'files_url': r.get('files'),
        })
    return out


def write_csv(rows: list[dict], path: Path) -> None:
    cols = ['API', 'name', 'status', 'status_code', 'operator',
            'county_fips', 'county', 'lat', 'lon', 'year_spudded',
            'spud_date_ms', 'md', 'tvd', 'directional', 'plug_date_ms',
            'files_url']
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)


def main():
    t0 = datetime.utcnow()
    meta = {
        'started_utc': t0.isoformat() + 'Z',
        'endpoint': BASE,
        'where': WHERE,
        'nm_permian_fips': NM_PERMIAN_FIPS,
        'page_size': PAGE_SIZE,
    }
    print('Pulling NM OCD wells (Permian counties)', file=sys.stderr)
    raw = paginated_pull()
    rows = normalise(raw)
    write_csv(rows, OUT / 'permian_wells.csv')
    meta['wells_count'] = len(rows)

    # Quick-look: county breakdown + spud-year buckets
    by_county: dict[str, int] = {}
    pre_2002 = post_2002 = unknown_year = 0
    for r in rows:
        c = r.get('county') or 'unknown'
        by_county[c] = by_county.get(c, 0) + 1
        y = r.get('year_spudded')
        try:
            yi = int(y) if y else 0
        except (TypeError, ValueError):
            yi = 0
        if yi >= 2002 and yi < 2100:
            post_2002 += 1
        elif yi > 1800 and yi < 2002:
            pre_2002 += 1
        else:
            unknown_year += 1
    meta['by_county'] = by_county
    meta['spud_buckets'] = {
        'pre_2002': pre_2002,
        'post_2002': post_2002,
        'unknown_or_bad': unknown_year,
    }

    t1 = datetime.utcnow()
    meta['finished_utc'] = t1.isoformat() + 'Z'
    meta['duration_s'] = (t1 - t0).total_seconds()
    with (OUT / 'pull_metadata.json').open('w') as f:
        json.dump(meta, f, indent=2)
    print(f'\n  wrote permian_wells.csv ({len(rows):,} rows)', file=sys.stderr)
    print(f'Done in {meta["duration_s"]:.1f}s.', file=sys.stderr)
    print(json.dumps(meta, indent=2))


if __name__ == '__main__':
    main()
