"""
Phase 0: probe NDIC, MT BOGC, and USGS Bakken-Three Forks TPS endpoints.

Goal: before committing to a data pull strategy, verify which Williston
sources are programmatically reachable and what their response shape
looks like.

Writes a status report to notes/williston_probe.md with:
  - which endpoints responded
  - content-type / size hints
  - whether a county / field / API-range query is supported
  - which ones need manual download vs. crawling vs. ArcGIS REST

Run: python3 phase0_source_probe.py
"""
import urllib.request
import urllib.error
import urllib.parse
import json
import sys
from pathlib import Path
from datetime import datetime

OUT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo/notes/williston_probe.md')

PROBES = [
    # --- North Dakota: ND GIS Hub (ArcGIS Hub) + DMR ------------------------
    {
        'label': 'ND GIS Hub: portal root',
        'url': 'https://gishubdata.nd.gov/',
        'method': 'GET',
    },
    {
        'label': 'ND GIS Hub: O&G well dataset landing',
        'url': 'https://gishubdata.nd.gov/dataset/oil-and-gas-well-map',
        'method': 'GET',
    },
    {
        'label': 'ND DMR: Oil & Gas home',
        'url': 'https://www.dmr.nd.gov/oilgas/',
        'method': 'GET',
    },
    {
        'label': 'ND DMR: Well search (ASPX, interactive)',
        'url': 'https://www.dmr.nd.gov/oilgas/findwellsvw.asp',
        'method': 'GET',
    },
    {
        'label': 'ND DMR: GIS download page',
        'url': 'https://gis.dmr.nd.gov/gisdownload.asp',
        'method': 'GET',
    },
    {
        'label': 'ND DMR: GIS landing root',
        'url': 'https://gis.dmr.nd.gov/',
        'method': 'GET',
    },
    # --- Montana: BOGC (real hostname is bogapps.dnrc.mt.gov, not bogc.*) ---
    {
        'label': 'MT BOGC: DataMiner home',
        'url': 'https://bogapps.dnrc.mt.gov/dataminer/',
        'method': 'GET',
    },
    {
        'label': 'MT BOGC: Wells search ASPX',
        'url': 'https://bogapps.dnrc.mt.gov/dataminer/Wells/Wells.aspx',
        'method': 'GET',
    },
    {
        'label': 'MT BOGC: Public files / GIS directory',
        'url': 'https://bogwebfiles.dnrc.mt.gov/GISData/',
        'method': 'GET',
    },
    {
        'label': 'MT BOGC: Wells.zip shapefile bundle',
        'url': 'https://bogwebfiles.dnrc.mt.gov/GISData/WellSurface/Wells.zip',
        'method': 'HEAD',
    },
    {
        'label': 'MT BOGC: WellPaths.zip directional bundle',
        'url': 'https://bogwebfiles.dnrc.mt.gov/GISData/WellPaths/WellPaths.zip',
        'method': 'HEAD',
    },
    # --- USGS Bakken-Three Forks TPS polygon --------------------------------
    {
        'label': 'USGS ScienceBase: 2021 Bakken-Three Forks AU item (JSON)',
        'url': 'https://www.sciencebase.gov/catalog/item/618e90c8d34ec04fc9caa732?format=json',
        'method': 'GET',
    },
    {
        'label': 'USGS ScienceBase: ThreeForksAUs.shp direct download',
        'url': 'https://www.sciencebase.gov/catalog/file/get/618e90c8d34ec04fc9caa732?f=__disk__03%2Ffc%2F71%2F03fc71291ced4a7b69837d2e8d3035d51bcacc81',
        'method': 'HEAD',
    },
    {
        'label': 'USGS ScienceBase: bundle ZIP for item 618e90c8',
        'url': 'https://www.sciencebase.gov/catalog/file/get/618e90c8d34ec04fc9caa732',
        'method': 'HEAD',
    },
    # --- Saskatchewan (future-optional) -------------------------------------
    {
        'label': 'SK GeoHub Economic Resources viewer',
        'url': 'https://gisappl.saskatchewan.ca/Html5Ext/Index.html?Viewer=EconomicResourceInfoMap',
        'method': 'GET',
    },
]


def probe(url: str, method: str = 'GET', timeout: int = 15) -> dict:
    """Return {status, content_type, length, preview, error}."""
    req = urllib.request.Request(
        url,
        method=method,
        headers={
            'User-Agent': 'darkdata-research/0.1 (Tee Salami; research; '
                         'salamituns.github.io)',
            'Accept': '*/*',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            status = r.status
            ctype = r.headers.get('Content-Type', '').split(';')[0]
            clen = r.headers.get('Content-Length')
            body = b''
            if method == 'GET':
                body = r.read(2048)
            preview = None
            if ctype.startswith('application/json') and body:
                try:
                    obj = json.loads(body)
                    preview = json.dumps(obj, indent=2)[:800]
                except Exception:
                    preview = body[:240].decode('utf-8', 'replace')
            elif body:
                preview = body[:240].decode('utf-8', 'replace').replace('\n', ' ')
            return {
                'status': status,
                'content_type': ctype,
                'length': clen,
                'preview': preview,
                'error': None,
            }
    except urllib.error.HTTPError as e:
        return {'status': e.code, 'content_type': None, 'length': None,
                'preview': None, 'error': f'HTTPError {e.code} {e.reason}'}
    except urllib.error.URLError as e:
        return {'status': None, 'content_type': None, 'length': None,
                'preview': None, 'error': f'URLError {e.reason}'}
    except Exception as e:
        return {'status': None, 'content_type': None, 'length': None,
                'preview': None, 'error': f'{type(e).__name__}: {e}'}


def main():
    lines = []
    lines.append(f'# Williston source probe: {datetime.now():%Y-%m-%d %H:%M}')
    lines.append('')
    lines.append('Reachability + response shape for each Williston data source. '
                 'Run before committing a pull strategy.')
    lines.append('')
    lines.append('Scope: ND + MT for v1. USGS Bakken-Three Forks TPS polygon as '
                 'the basin clip. SK included as a probe target only so we know '
                 'what a future extension would cost.')
    lines.append('')
    for p in PROBES:
        print(f'-> {p["label"]} ...', file=sys.stderr, flush=True)
        r = probe(p['url'], p['method'])
        lines.append(f'## {p["label"]}')
        lines.append(f'- URL: `{p["url"]}`')
        lines.append(f'- Method: {p["method"]}')
        if r['error']:
            lines.append(f'- **FAIL**: {r["error"]}')
        else:
            lines.append(f'- Status: **{r["status"]}**')
            if r['content_type']:
                lines.append(f'- Content-Type: `{r["content_type"]}`')
            if r['length']:
                lines.append(f'- Content-Length: {r["length"]} bytes')
            if r['preview']:
                lines.append('- Preview:')
                lines.append('```')
                lines.append(r['preview'])
                lines.append('```')
        lines.append('')

    OUT.write_text('\n'.join(lines))
    print(f'\nWrote report: {OUT}', file=sys.stderr)


if __name__ == '__main__':
    main()
