"""
Anadarko source probe. Reachability + response shape only.

Targets:
  Oklahoma Corporation Commission (OCC) — primary regulator.
  Oklahoma Geological Survey (OGS) — sometimes mirrors OCC data.
  KGS bulk well export — already in our pipeline (basin 01).
  USGS ScienceBase: Anadarko Basin Province / Cana-Woodford / Woodford
    Shale assessment unit boundaries.

Scope: OK + KS portions of the Anadarko Basin for v1. TX Panhandle
deferred (TX RRC portal is JSF/PrimeFaces session-based — same blocker
that pushed Eagle Ford to basin 06).
"""
import urllib.request
import urllib.error
import json
from pathlib import Path
from datetime import datetime

OUT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo/notes/anadarko_probe.md')


def fetch(url, method='GET', timeout=30):
    req = urllib.request.Request(
        url, method=method,
        headers={'User-Agent': 'darkdata-research/0.1', 'Accept': '*/*'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.headers.get('Content-Type', ''), r.headers.get('Content-Length', ''), r.read(800)
    except urllib.error.HTTPError as e:
        return f'HTTPError {e.code}', '', '', b''
    except Exception as e:
        return f'FAIL {type(e).__name__}', '', '', str(e).encode()


PROBES = [
    # Oklahoma Corporation Commission
    ('OCC: Oil & Gas home', 'https://oklahoma.gov/occ/divisions/oil-gas.html', 'GET'),
    ('OCC: Oil & Gas Data Files', 'https://oklahoma.gov/occ/divisions/oil-gas/oil-gas-data.html', 'GET'),
    ('OCC: Wells Database (legacy)', 'https://www.occeweb.com/og/oghome.htm', 'GET'),
    ('OCC: GIS portal (legacy)', 'https://gisservices.occ.ok.gov/arcgis/rest/services?f=json', 'GET'),
    ('OCC: GIS REST OG service guess', 'https://gisservices.occ.ok.gov/arcgis/rest/services/OG/MapServer?f=json', 'GET'),
    # Oklahoma Geological Survey
    ('OGS: home', 'https://www.ou.edu/ogs', 'GET'),
    ('OGS: data downloads', 'https://www.ou.edu/ogs/data', 'GET'),
    ('OGS: well data', 'https://www.ou.edu/ogs/data/wells', 'GET'),
    # OK State Open Data + ArcGIS Hub
    ('OK Open Data: ArcGIS Hub', 'https://hub.arcgis.com/search?collection=Dataset&q=oklahoma%20wells', 'GET'),
    ('OK Geospatial Clearinghouse', 'https://csa.ou.edu/clearinghouse/', 'GET'),
    # USGS ScienceBase: Anadarko AU items
    ('USGS SB: search Anadarko Basin Province assessment units', 'https://www.sciencebase.gov/catalog/items?q=Anadarko+Basin+Province+assessment+units&format=json&max=10', 'GET'),
    ('USGS SB: search Woodford Shale assessment', 'https://www.sciencebase.gov/catalog/items?q=Woodford+Shale+assessment+continuous&format=json&max=10', 'GET'),
    ('USGS SB: search Cana Woodford', 'https://www.sciencebase.gov/catalog/items?q=Cana+Woodford+assessment+unit&format=json&max=10', 'GET'),
    # OK Drilling permit data (sometimes via the OCC Imaging system)
    ('OCC: Imaging / Public Records', 'https://imaging.occ.ok.gov/imaging/og.aspx', 'GET'),
    ('OCC: Pollution remediation data', 'https://oklahoma.gov/occ/divisions/oil-gas/oil-gas-data/oil-gas-data-files.html', 'GET'),
]


lines = []
lines.append(f'# Anadarko source probe: {datetime.now():%Y-%m-%d %H:%M}\n')
lines.append('Reachability + response shape for each Anadarko source. Run before committing a pull strategy.\n')
lines.append('Scope: OK + KS portions of the Anadarko Basin Province. TX Panhandle deferred (TX RRC is JSF-session blocked, same as Eagle Ford). KGS already in pipeline from basin 01.\n')

for label, url, method in PROBES:
    status, ct, cl, body = fetch(url, method=method)
    lines.append(f'## {label}')
    lines.append(f'- URL: `{url}`')
    lines.append(f'- Method: {method}')
    lines.append(f'- Status: **{status}** | CT: `{ct}` | CL: `{cl}`')
    try:
        preview = body.decode('utf-8', errors='replace').strip().replace('\n', ' ')[:500]
    except Exception:
        preview = '(binary)'
    lines.append(f'- Preview: `{preview}`')
    lines.append('')


with OUT.open('w') as f:
    f.write('\n'.join(lines))

print(f'wrote {OUT}')
