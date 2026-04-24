"""
Phase 1: pull TX RRC wells, well-logs, and orphans from the live ArcGIS REST.

Endpoint: gis.rrc.texas.gov/server/rest/services/rrc_public/RRC_Public_Viewer_Srvs

Layers used:
  1 Well Locations       (~1.39M rows statewide)
  2 Orphan Wells         (~12K rows statewide)
  8 Well Logs            (~236K rows statewide)

Spatial filter: Permian bbox covering TX Permian counties. Post-filter to
actual county polygons happens in a later phase.

Outputs:
  data/raw/tx_rrc/permian_wells.csv     (API, lat, lon)
  data/raw/tx_rrc/permian_logs.csv      (API)
  data/raw/tx_rrc/permian_orphans.csv   (API)
  data/raw/tx_rrc/pull_metadata.json    (counts, timing, endpoint)

Usage:  python3 phase1_tx_rrc_pull.py
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

OUT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo/data/raw/tx_rrc')
OUT.mkdir(parents=True, exist_ok=True)

BASE = ('https://gis.rrc.texas.gov/server/rest/services/'
        'rrc_public/RRC_Public_Viewer_Srvs/MapServer')

# Permian bbox (WGS84). Slightly generous: includes edge counties we'll
# spatial-filter away later. xmin, ymin, xmax, ymax.
PERMIAN_BBOX = '-104.9,30.2,-100.3,33.7'

UA = 'darkdata-research/0.1 (Tee Salami; research; salamituns.github.io)'
PAGE_SIZE = 1000  # RRC maxRecordCount
REQUEST_SLEEP_S = 0.35  # be polite


def fetch_json(url: str, timeout: int = 90) -> dict:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def paginated_pull(layer_id: int, out_fields: list[str],
                   return_geometry: bool) -> list[dict]:
    """Pull a layer fully within PERMIAN_BBOX, paginating with resultOffset."""
    base_params = {
        'geometry': PERMIAN_BBOX,
        'geometryType': 'esriGeometryEnvelope',
        'inSR': '4326',
        'outSR': '4326',
        'spatialRel': 'esriSpatialRelIntersects',
        'where': '1=1',
        'outFields': ','.join(out_fields),
        'returnGeometry': 'true' if return_geometry else 'false',
        'f': 'json',
        'resultRecordCount': PAGE_SIZE,
    }

    count = fetch_json(
        f'{BASE}/{layer_id}/query?'
        + urllib.parse.urlencode({**base_params, 'returnCountOnly': 'true'})
    ).get('count')
    print(f'  layer {layer_id} target rows: {count:,}', file=sys.stderr, flush=True)

    all_rows: list[dict] = []
    offset = 0
    page = 0
    while True:
        params = {**base_params, 'resultOffset': offset,
                  'orderByFields': 'OBJECTID ASC'}
        url = f'{BASE}/{layer_id}/query?' + urllib.parse.urlencode(params)
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
            row = dict(feat['attributes'])
            if return_geometry and feat.get('geometry'):
                row['_x'] = feat['geometry'].get('x')
                row['_y'] = feat['geometry'].get('y')
            all_rows.append(row)
        page += 1
        offset += len(feats)
        if page % 10 == 0 or offset >= count:
            pct = 100 * offset / count if count else 100
            print(f'    page {page:>4} · offset {offset:>7,} / {count:,} '
                  f'({pct:>5.1f}%)', file=sys.stderr, flush=True)
        if not data.get('exceededTransferLimit') and len(feats) < PAGE_SIZE:
            break
        time.sleep(REQUEST_SLEEP_S)

    return all_rows


def write_csv(rows: list[dict], path: Path, columns: list[str]) -> None:
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)


def main():
    t0 = datetime.utcnow()
    meta = {
        'started_utc': t0.isoformat() + 'Z',
        'endpoint': BASE,
        'bbox_wgs84': PERMIAN_BBOX,
        'page_size': PAGE_SIZE,
    }

    print('Pulling Layer 1: Well Locations (wells w/ geometry)',
          file=sys.stderr)
    wells = paginated_pull(
        layer_id=1,
        out_fields=['API', 'GIS_API5', 'GIS_LAT83', 'GIS_LONG83',
                    'GIS_SYMBOL_DESCRIPTION'],
        return_geometry=False,  # lat/lon already in attrs
    )
    # Normalise
    for r in wells:
        r['lat'] = r.get('GIS_LAT83')
        r['lon'] = r.get('GIS_LONG83')
        r['sym'] = r.get('GIS_SYMBOL_DESCRIPTION') or ''
    write_csv(wells, OUT / 'permian_wells.csv',
              columns=['API', 'GIS_API5', 'lat', 'lon', 'sym'])
    meta['wells_count'] = len(wells)
    print(f'  wrote permian_wells.csv ({len(wells):,} rows)', file=sys.stderr)

    print('\nPulling Layer 8: Well Logs (API only, lit universe)',
          file=sys.stderr)
    logs = paginated_pull(layer_id=8, out_fields=['API'], return_geometry=False)
    write_csv(logs, OUT / 'permian_logs.csv', columns=['API'])
    meta['logs_count'] = len(logs)
    print(f'  wrote permian_logs.csv ({len(logs):,} rows)', file=sys.stderr)

    print('\nPulling Layer 2: Orphan Wells (API only)', file=sys.stderr)
    orphs = paginated_pull(layer_id=2, out_fields=['API'], return_geometry=False)
    write_csv(orphs, OUT / 'permian_orphans.csv', columns=['API'])
    meta['orphans_count'] = len(orphs)
    print(f'  wrote permian_orphans.csv ({len(orphs):,} rows)',
          file=sys.stderr)

    t1 = datetime.utcnow()
    meta['finished_utc'] = t1.isoformat() + 'Z'
    meta['duration_s'] = (t1 - t0).total_seconds()
    with (OUT / 'pull_metadata.json').open('w') as f:
        json.dump(meta, f, indent=2)
    print(f'\nDone in {meta["duration_s"]:.1f}s.', file=sys.stderr)
    print(json.dumps(meta, indent=2))


if __name__ == '__main__':
    main()
