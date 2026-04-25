"""
Phase 1: download the Eagle Ford basin-06 source datasets.

Eagle Ford ships without per-well data. The five cooperative basins
(Kansas, Permian, Williston, Anadarko, Appalachia) cover that territory.
This basin is the series capstone: TX RRC publishes its bulk well data
through a JSF/PrimeFaces session portal with 5-minute timeouts,
backed by EBCDIC mainframe dumps. We do not scrape that.

Targets:
  USGS Eagle Ford AU geojson (polygon only)
  EIA Drilling Productivity Report (monthly Eagle Ford production)
  Census TIGER state + county boundaries (for South TX overlay)
"""
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
import sys

ROOT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo')
RAW = ROOT / 'data/raw'

UA = {'User-Agent': 'darkdata-research/0.1 (salamituns.github.io; research)'}

TARGETS = [
    {
        'label': 'USGS Eagle Ford AU geojson',
        'url': 'https://www.sciencebase.gov/catalog/file/get/5d1246c2e4b0941bde56e84f?f=__disk__8a%2F67%2F40%2F8a674006d02b243c47590f41df3e293cde65d19b',
        'out': RAW / 'usgs_eagle_ford/EagleFordAUs.geojson',
    },
    {
        'label': 'EIA Drilling Productivity Report',
        'url': 'https://www.eia.gov/petroleum/drilling/xls/dpr-data.xlsx',
        'out': RAW / 'eia_dpr/dpr-data.xlsx',
    },
    # Census TIGER cartographic boundary 2024: states (5m) + counties (5m)
    {
        'label': 'Census TIGER states 5m (cb_2024_us_state_5m)',
        'url': 'https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_5m.zip',
        'out': RAW / 'census/cb_2024_us_state_5m.zip',
    },
    {
        'label': 'Census TIGER counties 5m (cb_2024_us_county_5m)',
        'url': 'https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_5m.zip',
        'out': RAW / 'census/cb_2024_us_county_5m.zip',
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


def main():
    t0 = datetime.now()
    print(f'# Eagle Ford download at {t0:%Y-%m-%d %H:%M}', file=sys.stderr)
    for t in TARGETS:
        status, size = download(t['url'], t['out'], t['label'])
        size_str = f'{size/1e6:.1f} MB' if size else ''
        print(f'  {t["label"]:42s} -> {status:18s} {size_str}', file=sys.stderr)
    dt = (datetime.now() - t0).total_seconds()
    print(f'\nDone in {dt:.1f}s. Raw data under {RAW}', file=sys.stderr)


if __name__ == '__main__':
    main()
