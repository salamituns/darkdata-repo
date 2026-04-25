"""
Phase 1: download the three Williston source datasets.

Idempotent: each download skips if the target file already exists and is
non-empty. Intended to be re-runnable for reproducibility without
hammering the source servers.

Targets:
  1. NDIC OGD_Wells.zip     (43K ND wells, shapefile)
  2. NDIC OGD_Horizontals.zip (directional surveys + line features)
  3. MT BOGC Wells.zip      (42K MT wells, shapefile)
  4. USGS ScienceBase bundle (Bakken + Three Forks AU boundaries)

All four are direct public HTTPS shapefile / zip downloads. No scraping,
no session tokens, no rate limiting needed.
"""
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
import sys

ROOT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo')
RAW = ROOT / 'data/raw'

TARGETS = [
    {
        'label': 'NDIC wells (surface holes)',
        'url': 'https://gis.dmr.nd.gov/downloads/oilgas/shapefile/OGD_Wells.zip',
        'out': RAW / 'ndic/OGD_Wells.zip',
    },
    {
        'label': 'NDIC horizontals (directional surveys + legs)',
        'url': 'https://gis.dmr.nd.gov/downloads/oilgas/shapefile/OGD_Horizontals.zip',
        'out': RAW / 'ndic/OGD_Horizontals.zip',
    },
    {
        'label': 'MT BOGC wells (surface holes)',
        'url': 'https://bogfiles.dnrc.mt.gov/GISData/WellSurface/Wells.zip',
        'out': RAW / 'mt_bogc/Wells.zip',
    },
    {
        'label': 'USGS ScienceBase: Bakken + Three Forks AU boundaries',
        'url': 'https://www.sciencebase.gov/catalog/file/get/618e90c8d34ec04fc9caa732',
        'out': RAW / 'usgs_bakken/bakken_three_forks_bundle.zip',
    },
]


def download(url: str, out: Path, label: str) -> tuple[str, int | None]:
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 0:
        return ('skipped (already present)', out.stat().st_size)
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'darkdata-research/0.1 (salamituns.github.io; research)',
            'Accept': '*/*',
        },
    )
    tmp = out.with_suffix(out.suffix + '.partial')
    try:
        with urllib.request.urlopen(req, timeout=120) as r, tmp.open('wb') as f:
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
    print(f'# Williston download at {t0:%Y-%m-%d %H:%M}', file=sys.stderr)
    for t in TARGETS:
        status, size = download(t['url'], t['out'], t['label'])
        size_str = f'{size/1e6:.1f} MB' if size else ''
        print(f'  {t["label"]:48s} -> {status} {size_str}', file=sys.stderr)
    dt = (datetime.now() - t0).total_seconds()
    print(f'\nDone in {dt:.1f}s. Raw data under {RAW}', file=sys.stderr)


if __name__ == '__main__':
    main()
