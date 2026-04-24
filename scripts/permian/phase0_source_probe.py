"""
Phase 0: probe TX RRC and NM OCD endpoints.

Goal: before committing to a data pull strategy, verify which sources are
programmatically reachable and what their response shape looks like.

Writes a status report to notes/permian_probe.md with:
  - which endpoints responded
  - content-type / size hints
  - whether a county-filtered query is supported
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

OUT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo/notes/permian_probe.md')

PROBES = [
    # --- TX RRC -------------------------------------------------------------
    {
        'label': 'TX RRC: Data Sets Available for Download (HTML index)',
        'url': 'https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/',
        'method': 'HEAD',
    },
    {
        'label': 'TX RRC: GIS Viewer (HTML)',
        'url': 'https://www.rrc.texas.gov/resource-center/research/gis-viewer/',
        'method': 'HEAD',
    },
    {
        'label': 'TX RRC: ArcGIS REST services root',
        'url': 'https://gis.rrc.texas.gov/arcgis/rest/services?f=json',
        'method': 'GET',
    },
    {
        'label': 'TX RRC: Public GIS Viewer Surface Hole Locations (ArcGIS REST)',
        'url': 'https://gis.rrc.texas.gov/arcgis/rest/services/Public_GIS_Viewer/MapServer?f=json',
        'method': 'GET',
    },
    # --- NM OCD -------------------------------------------------------------
    {
        'label': 'NM OCD: Permitting home (HTML)',
        'url': 'https://wwwapps.emnrd.nm.gov/ocd/ocdpermitting/',
        'method': 'HEAD',
    },
    {
        'label': 'NM OCD: GIS page (HTML)',
        'url': 'https://wwwapps.emnrd.nm.gov/ocd/ocdpermitting/Reporting/GIS/GIS.aspx',
        'method': 'HEAD',
    },
    {
        'label': 'NM OCD: Wells search (HTML)',
        'url': 'https://wwwapps.emnrd.nm.gov/ocd/ocdpermitting/Data/Wells/Wells.aspx',
        'method': 'HEAD',
    },
    # --- USGS Permian Basin province boundary -------------------------------
    {
        'label': 'USGS: Permian Basin province boundary (ScienceBase item page)',
        'url': 'https://www.sciencebase.gov/catalog/item/5a3c7c2ce4b00f54eb1e85b3',
        'method': 'HEAD',
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
                body = r.read(2048)  # peek only
            preview = None
            if ctype.startswith('application/json') and body:
                try:
                    obj = json.loads(body)
                    preview = json.dumps(obj, indent=2)[:600]
                except Exception:
                    preview = body[:200].decode('utf-8', 'replace')
            elif body:
                preview = body[:200].decode('utf-8', 'replace').replace('\n', ' ')
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
    lines.append(f'# Permian source probe: {datetime.now():%Y-%m-%d %H:%M}')
    lines.append('')
    lines.append('Reachability + response shape for each Permian data source. '
                 'Run before committing a pull strategy.')
    lines.append('')
    for p in PROBES:
        print(f'→ {p["label"]} ...', file=sys.stderr, flush=True)
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
