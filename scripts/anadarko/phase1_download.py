"""
Phase 1: download Anadarko Basin source datasets.

Idempotent: each download skips if the target file already exists and is
non-empty. Re-runnable for reproducibility without hammering the source
servers.

Targets (OK + USGS only; KS reused from basin 01):
  1. OCC RBDMS_WELLS.zip       (~46 MB, OK wells shapefile)
  2. OCC rbdms-wells.csv       (~126 MB, OK well metadata)
  3. OCC orphan-well-list.xlsx (~2 MB, OK orphan/abandoned wells - dark side)
  4. OCC completions-wells-formations-base.xlsx (~76 MB, OK lit-proxy)
  5. OCC completions-wells-legacy.xlsx (~97 MB, OK lit-proxy historical)
  6. OCC operator-list.xlsx    (~1 MB, operator names)
  7. USGS Anadarko 3D-model Shapefiles.zip (basin envelope via dissolve)

KS portion is already in data/raw/kgs/ from basin 01.
TX panhandle deferred to basin 06 (TX RRC JSF/EBCDIC infrastructure debt).
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
        'label': 'OCC RBDMS wells (shapefile)',
        'url': 'https://www.oklahoma.gov/content/dam/ok/en/occ/documents/og/esri/files/RBDMS_WELLS.zip',
        'out': RAW / 'occ/RBDMS_WELLS.zip',
    },
    {
        'label': 'OCC RBDMS wells (CSV metadata)',
        'url': 'https://www.oklahoma.gov/content/dam/ok/en/occ/documents/og/ogdatafiles/rbdms-wells.csv',
        'out': RAW / 'occ/rbdms-wells.csv',
    },
    {
        'label': 'OCC orphan well list',
        'url': 'https://www.oklahoma.gov/content/dam/ok/en/occ/documents/og/ogdatafiles/orphan-well-list.xlsx',
        'out': RAW / 'occ/orphan-well-list.xlsx',
    },
    {
        'label': 'OCC well completions (base, modern)',
        'url': 'https://www.oklahoma.gov/content/dam/ok/en/occ/documents/og/ogdatafiles/completions-wells-formations-base.xlsx',
        'out': RAW / 'occ/completions-base.xlsx',
    },
    {
        'label': 'OCC well completions (legacy historical)',
        'url': 'https://www.oklahoma.gov/content/dam/ok/en/occ/documents/og/ogdatafiles/completions-wells-legacy.xlsx',
        'out': RAW / 'occ/completions-legacy.xlsx',
    },
    {
        'label': 'OCC operator list',
        'url': 'https://www.oklahoma.gov/content/dam/ok/en/occ/documents/og/ogdatafiles/operator-list.xlsx',
        'out': RAW / 'occ/operator-list.xlsx',
    },
    {
        'label': 'USGS Anadarko 3D model shapefiles (basin envelope)',
        'url': 'https://www.sciencebase.gov/catalog/file/get/6410e613d34e22162d3e1774?f=__disk__3f%2F77%2Fb4%2F3f77b4d38c4f7f8be48b66441877dcdee05af944',
        'out': RAW / 'usgs_anadarko/Shapefiles.zip',
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
    print(f'# Anadarko download at {t0:%Y-%m-%d %H:%M}', file=sys.stderr)
    for t in TARGETS:
        status, size = download(t['url'], t['out'], t['label'])
        size_str = f'{size/1e6:.1f} MB' if size else ''
        print(f'  {t["label"]:50s} -> {status:18s} {size_str}', file=sys.stderr)
    dt = (datetime.now() - t0).total_seconds()
    print(f'\nDone in {dt:.1f}s. Raw data under {RAW}', file=sys.stderr)


if __name__ == '__main__':
    main()
