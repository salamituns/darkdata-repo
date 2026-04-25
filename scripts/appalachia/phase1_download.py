"""
Phase 1: download the Appalachia source datasets (PA + WV + OH + clip).

Idempotent. Each target skips if the file is already present and
non-empty. Re-runnable for reproducibility without hammering the
source servers.

Targets:
  PA  PADEP OilGasLocations Conv+Unconv (~24 MB, current well layer)
  PA  PADEP Historic Oil/Gas Wells (~3 MB, WPA / K Sheet / H Sheet)
  PA  PADEP Conservation Wells + Plugged (~1 MB, dark inventory)
  WV  WV DEP WellLocation 2016 shapefile (~16 MB, full state wells)
  WV  WV DEP 2024 Q4 Horizontal H6A production (~1 MB, lit proxy)
  OH  OH DOG_Services REST query, 242K wells, paginated 1000 / page
  EIA Tight Oil + Shale Plays Lower48 Dec 2021 (~0.32 MB, basin clip)
"""
import urllib.request
import urllib.error
import urllib.parse
import json
import sys
import time
from pathlib import Path
from datetime import datetime

ROOT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo')
RAW = ROOT / 'data/raw'

UA = {'User-Agent': 'darkdata-research/0.1 (salamituns.github.io; research)'}

STATIC_TARGETS = [
    {
        'label': 'PA DEP wells (Conv + Unconv)',
        'url': 'https://www.pasda.psu.edu/download/dep/OilGasLocations_ConventionalUnconventional2026_04.zip',
        'out': RAW / 'pa_dep/OilGasLocations_ConvUnconv.zip',
    },
    {
        'label': 'PA DEP historic wells (WPA + K + H Sheet)',
        'url': 'https://www.pasda.psu.edu/download/dep/PADEP_HistoricOilGasWells_ALL.zip',
        'out': RAW / 'pa_dep/PADEP_HistoricOilGasWells_ALL.zip',
    },
    {
        'label': 'PA DEP conservation wells',
        'url': 'https://www.pasda.psu.edu/download/dep/ConservationWells2026_04.zip',
        'out': RAW / 'pa_dep/ConservationWells.zip',
    },
    {
        'label': 'PA DEP conservation wells (plugged)',
        'url': 'https://www.pasda.psu.edu/download/dep/ConservationWells_Plugged2026_04.zip',
        'out': RAW / 'pa_dep/ConservationWells_Plugged.zip',
    },
    {
        'label': 'WV DEP well location 2016',
        'url': 'https://apps.dep.wv.gov/Documents/OOG/WellLocationData/WellLocation%2808-22-2016%29.zip',
        'out': RAW / 'wv_dep/WellLocation_2016.zip',
    },
    {
        'label': 'WV DEP 2024 Q4 horizontal H6A production',
        'url': 'https://apps.dep.wv.gov/Documents/OOG/ProductionReports/H6A_Production_Data/2024%20Q4%20WV%20Horizontal%20H6A%20Production%20Data%20File.xlsx',
        'out': RAW / 'wv_dep/2024Q4_Horizontal_H6A.xlsx',
    },
    {
        'label': 'EIA Tight Oil + Shale Plays Lower48',
        'url': 'https://www.eia.gov/maps/map_data/TightOil_ShaleGas_Plays_Lower48_EIA.zip',
        'out': RAW / 'eia_shale/TightOil_ShaleGas_Plays_Lower48.zip',
    },
]


def download(url, out, label):
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 0:
        return ('skipped (already present)', out.stat().st_size)
    req = urllib.request.Request(url, headers={**UA, 'Accept': '*/*'})
    tmp = out.with_suffix(out.suffix + '.partial')
    try:
        with urllib.request.urlopen(req, timeout=300) as r, tmp.open('wb') as f:
            total = 0
            while True:
                chunk = r.read(1 << 16)
                if not chunk:
                    break
                f.write(chunk)
                total += len(chunk)
        tmp.rename(out)
        return ('downloaded', total)
    except Exception as e:
        if tmp.exists():
            tmp.unlink()
        return (f'FAIL: {type(e).__name__}: {e}', None)


def fetch_oh_wells():
    """OH has no bulk ZIP. Page through the DOG_Services REST endpoint
    and write a single combined GeoJSON FeatureCollection.
    """
    out = RAW / 'oh_dnr/Oilgas_Wells_public.geojson'
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 0:
        return ('skipped (already present)', out.stat().st_size)

    base = 'https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0/query'
    # Get total count first
    count_url = base + '?' + urllib.parse.urlencode({
        'where': '1=1',
        'returnCountOnly': 'true',
        'f': 'json',
    })
    req = urllib.request.Request(count_url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        total = json.loads(r.read())['count']
    print(f'    OH wells to fetch: {total:,}', file=sys.stderr)

    features = []
    page_size = 1000
    offset = 0
    t0 = time.time()
    while offset < total:
        params = {
            'where': '1=1',
            'outFields': '*',
            'returnGeometry': 'true',
            'outSR': '4326',
            'resultOffset': str(offset),
            'resultRecordCount': str(page_size),
            'f': 'geojson',
        }
        url = base + '?' + urllib.parse.urlencode(params)
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers=UA)
                with urllib.request.urlopen(req, timeout=120) as r:
                    page = json.loads(r.read())
                break
            except Exception as e:
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
        feats = page.get('features', [])
        features.extend(feats)
        offset += page_size
        if offset % 10000 < page_size:
            elapsed = time.time() - t0
            rate = len(features) / elapsed if elapsed else 0
            print(f'    OH progress: {len(features):,} / {total:,}  ({rate:.0f}/s)', file=sys.stderr)

    fc = {'type': 'FeatureCollection', 'features': features}
    tmp = out.with_suffix(out.suffix + '.partial')
    tmp.write_text(json.dumps(fc))
    tmp.rename(out)
    return ('downloaded', out.stat().st_size)


def main():
    t0 = datetime.now()
    print(f'# Appalachia download at {t0:%Y-%m-%d %H:%M}', file=sys.stderr)
    for t in STATIC_TARGETS:
        status, size = download(t['url'], t['out'], t['label'])
        size_str = f'{size/1e6:.1f} MB' if size else ''
        print(f'  {t["label"]:46s} -> {status:18s} {size_str}', file=sys.stderr)

    print(f'  Ohio DOG REST query (paginated)...', file=sys.stderr)
    status, size = fetch_oh_wells()
    size_str = f'{size/1e6:.1f} MB' if size else ''
    print(f'  {"Ohio wells GeoJSON":46s} -> {status:18s} {size_str}', file=sys.stderr)

    dt = (datetime.now() - t0).total_seconds()
    print(f'\nDone in {dt:.1f}s. Raw data under {RAW}', file=sys.stderr)


if __name__ == '__main__':
    main()
