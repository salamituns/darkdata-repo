"""
Eagle Ford probe round 2: resolve ScienceBase hits + try alternate TX
endpoints. The first probe established that TX RRC's REST host
(gis2.rrc.texas.gov) is unreachable from this network and that the two
guessed ScienceBase item IDs were 404. This round:

  1. Walks the 4 ScienceBase items returned by the search query so we
     find the actual Eagle Ford Group AU polygon download.
  2. Tries the alternate TX RRC GIS host (gis.rrc.texas.gov, no '2') in
     case the REST endpoint lives there.
  3. Probes data.texas.gov as a fallback open-data path.
"""
import urllib.request
import urllib.error
import json
from pathlib import Path
from datetime import datetime

OUT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo/notes/eagle_ford_probe.md')


def fetch_json(url):
    req = urllib.request.Request(
        url, headers={'User-Agent': 'darkdata-research/0.1', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def fetch_status(url, method='GET'):
    req = urllib.request.Request(
        url, method=method,
        headers={'User-Agent': 'darkdata-research/0.1', 'Accept': '*/*'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.headers.get('Content-Type', ''), r.headers.get('Content-Length', ''), r.read(400)
    except urllib.error.HTTPError as e:
        return f'HTTPError {e.code}', '', '', b''
    except Exception as e:
        return f'FAIL {type(e).__name__}', '', '', str(e).encode()


lines = []
lines.append('\n---\n')
lines.append(f'# Eagle Ford probe round 2: {datetime.now():%Y-%m-%d %H:%M}\n')

lines.append('## ScienceBase search hits resolution\n')
search_url = 'https://www.sciencebase.gov/catalog/items?q=Eagle+Ford+Group+assessment+units&format=json&max=10'
try:
    sb = fetch_json(search_url)
    lines.append(f'Total hits: {sb.get("total")}\n')
    for it in sb.get('items', []):
        item_id = it.get('id')
        title = it.get('title', '(untitled)')
        link = it.get('link', {}).get('url', '')
        lines.append(f'- **{title}**')
        lines.append(f'  - ID: `{item_id}`')
        lines.append(f'  - Link: {link}')
        # Resolve item to find files
        try:
            full = fetch_json(f'https://www.sciencebase.gov/catalog/item/{item_id}?format=json')
            files = full.get('files', [])
            web_links = full.get('webLinks', [])
            if files:
                lines.append(f'  - Files ({len(files)}):')
                for f in files[:8]:
                    name = f.get('name', '')
                    size = f.get('size', 0)
                    url = f.get('url', '') or f.get('downloadUri', '')
                    lines.append(f'    - `{name}` {size/1e6:.2f} MB  -> {url}')
            if web_links:
                lines.append(f'  - WebLinks ({len(web_links)}):')
                for w in web_links[:5]:
                    lines.append(f'    - {w.get("title","")}: {w.get("uri","")}')
        except Exception as e:
            lines.append(f'  - resolve FAIL: {type(e).__name__}: {e}')
        lines.append('')
except Exception as e:
    lines.append(f'search FAIL: {e}')

lines.append('\n## Alternate TX RRC endpoints\n')
TX_PROBES = [
    ('TX RRC GIS (no 2): home', 'https://gis.rrc.texas.gov/'),
    ('TX RRC GIS (no 2): REST root', 'https://gis.rrc.texas.gov/arcgis/rest/services?f=json'),
    ('TX RRC GIS (no 2): PublicGISViewer', 'https://gis.rrc.texas.gov/arcgis/rest/services/PublicGISViewer?f=json'),
    ('TX RRC GIS (no 2): PublicGISViewer/MapServer', 'https://gis.rrc.texas.gov/arcgis/rest/services/PublicGISViewer/MapServer?f=json'),
    ('TX RRC GIS (no 2): OilGasFeatureService', 'https://gis.rrc.texas.gov/arcgis/rest/services/PublicGISViewer/MapServer/0?f=json'),
]
for label, url in TX_PROBES:
    status, ct, cl, body = fetch_status(url)
    lines.append(f'### {label}')
    lines.append(f'- URL: `{url}`')
    lines.append(f'- Status: **{status}** | CT: `{ct}` | CL: `{cl}`')
    try:
        preview = body.decode('utf-8', errors='replace').strip().replace('\n', ' ')[:240]
    except Exception:
        preview = '(binary)'
    lines.append(f'- Preview: `{preview}`')
    lines.append('')

lines.append('\n## Texas Open Data + alternate hosts\n')
ALT = [
    ('Texas Open Data: domain', 'https://data.texas.gov/'),
    ('Texas Open Data: search Eagle Ford', 'https://data.texas.gov/api/views.json?search=Eagle+Ford&limit=5'),
    ('TX RRC: GIS files / shapefile downloads index', 'https://gis.rrc.texas.gov/files/'),
    ('TX RRC: data sets HTML body', 'https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/'),
]
for label, url in ALT:
    status, ct, cl, body = fetch_status(url)
    lines.append(f'### {label}')
    lines.append(f'- URL: `{url}`')
    lines.append(f'- Status: **{status}** | CT: `{ct}` | CL: `{cl}`')
    try:
        preview = body.decode('utf-8', errors='replace').strip().replace('\n', ' ')[:600]
    except Exception:
        preview = '(binary)'
    lines.append(f'- Preview: `{preview}`')
    lines.append('')


with OUT.open('a') as f:
    f.write('\n'.join(lines))

print(f'appended round 2 to {OUT}')
