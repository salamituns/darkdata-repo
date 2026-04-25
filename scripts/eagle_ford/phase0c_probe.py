"""
Eagle Ford probe round 3: try fallback well-header sources before
giving up on TX RRC. The TX RRC REST endpoints are unreachable from
this network and the AU polygon is in hand. Question: is there a clean
public path to Texas well-header data that doesn't require scraping
the JS GIS viewer or fighting EBCDIC mainframe dumps?

Targets:
  - HIFLD Open Data oil & gas wells (national layer, federal)
  - USGS National Map energy wells layer (if any)
  - Texas General Land Office / Texas Almanac open data
  - The TX RRC OG_Wells direct file at any reachable mirror
"""
import urllib.request
import urllib.error
import json
from pathlib import Path
from datetime import datetime

OUT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo/notes/eagle_ford_probe.md')


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
    ('HIFLD: Oil and Natural Gas Wells layer', 'https://hifld-geoplatform.opendata.arcgis.com/datasets/oil-and-natural-gas-wells/about', 'GET'),
    ('HIFLD: ArcGIS Hub item search', 'https://hifld-geoplatform.opendata.arcgis.com/api/feed/dcat-us/1.1.json?q=oil+gas+wells', 'GET'),
    ('HIFLD: known Wells FeatureServer guess', 'https://services.arcgis.com/jIL9msH9OI208GCb/arcgis/rest/services/Oil_and_Natural_Gas_Wells/FeatureServer?f=json', 'GET'),
    ('HIFLD: alt FeatureServer arcgis.com', 'https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Oil_and_Natural_Gas_Wells/FeatureServer?f=json', 'GET'),
    ('HIFLD via DHS GII', 'https://gii.dhs.gov/HIFLD', 'GET'),
    ('HIFLD search shim', 'https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services?f=json', 'GET'),
    ('USGS National Map Energy: oil & gas wells', 'https://energy.usgs.gov/Coal/Resources.aspx', 'GET'),
    ('TX RRC: known shapefile bulk OG_WELLS direct', 'https://gis.rrc.texas.gov/files/OG_WELLS.zip', 'HEAD'),
    ('TX RRC: known shapefile bulk Wells direct', 'https://gis.rrc.texas.gov/files/Wells.zip', 'HEAD'),
    ('TX RRC: GIS data via wwwGIS', 'https://wwwgisp.rrc.state.tx.us/GISViewer2/', 'GET'),
    ('TX RRC: TXOG download portal', 'https://www.rrc.texas.gov/oil-and-gas/research-and-statistics/well-information/', 'GET'),
]


lines = []
lines.append('\n---\n')
lines.append(f'# Eagle Ford probe round 3 (HIFLD + fallbacks): {datetime.now():%Y-%m-%d %H:%M}\n')

for label, url, method in PROBES:
    status, ct, cl, body = fetch(url, method=method)
    lines.append(f'### {label}')
    lines.append(f'- URL: `{url}`')
    lines.append(f'- Method: {method}')
    lines.append(f'- Status: **{status}** | CT: `{ct}` | CL: `{cl}`')
    try:
        preview = body.decode('utf-8', errors='replace').strip().replace('\n', ' ')[:500]
    except Exception:
        preview = '(binary)'
    lines.append(f'- Preview: `{preview}`')
    lines.append('')


with OUT.open('a') as f:
    f.write('\n'.join(lines))

print(f'appended round 3 to {OUT}')
