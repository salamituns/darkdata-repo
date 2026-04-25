"""
Eagle Ford source probe. Reachability + response shape only.

Targets:
  TX RRC public GIS / bulk data portals (Texas's regulator is famously
  awkward about bulk well downloads).
  USGS ScienceBase Eagle Ford Group AU (basin clip polygon).
  USGS GMC oil & gas well-header layer (state-level coverage layer, in
  case TX RRC is impossible to ingest cleanly).
"""
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

OUT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo/notes/eagle_ford_probe.md')

PROBES = [
    ('TX RRC: home', 'https://www.rrc.texas.gov/', 'GET'),
    ('TX RRC: data sets for download', 'https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/', 'GET'),
    ('TX RRC: oil & gas well download', 'https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/oil-gas/', 'GET'),
    ('TX RRC GIS public viewer', 'https://gis.rrc.texas.gov/GISViewer/', 'GET'),
    ('TX RRC GIS REST root', 'https://gis2.rrc.texas.gov/arcgis/rest/services', 'GET'),
    ('TX RRC GIS REST: PublicGISViewer folder', 'https://gis2.rrc.texas.gov/arcgis/rest/services/PublicGISViewer?f=json', 'GET'),
    ('TX RRC GIS REST: PublicGISViewer/MapServer', 'https://gis2.rrc.texas.gov/arcgis/rest/services/PublicGISViewer/MapServer?f=json', 'GET'),
    ('TX RRC GIS REST: Production folder', 'https://gis2.rrc.texas.gov/arcgis/rest/services/Production?f=json', 'GET'),
    ('TX RRC GIS REST: Wells folder', 'https://gis2.rrc.texas.gov/arcgis/rest/services/Wells?f=json', 'GET'),
    ('TX RRC GIS REST: OG_Wells layer attempt', 'https://gis2.rrc.texas.gov/arcgis/rest/services/OG/MapServer?f=json', 'GET'),
    ('USGS GMC: National Map Energy Resources', 'https://www.usgs.gov/programs/energy-resources-program', 'GET'),
    ('USGS ScienceBase: Eagle Ford 2018 assessment item', 'https://www.sciencebase.gov/catalog/item/5b2cd7a0e4b056a4f8b0a5e5?format=json', 'GET'),
    ('USGS ScienceBase: Eagle Ford alternate 2018 assessment item', 'https://www.sciencebase.gov/catalog/item/5a8b66d2e4b00f54eb19d39d?format=json', 'GET'),
    ('USGS ScienceBase: National Assessment search root', 'https://www.sciencebase.gov/catalog/items?q=Eagle+Ford+Group+assessment+units&format=json&max=10', 'GET'),
]


def probe(label, url, method):
    print(f'## {label}', file=md)
    print(f'- URL: `{url}`', file=md)
    print(f'- Method: {method}', file=md)
    req = urllib.request.Request(
        url, method=method,
        headers={'User-Agent': 'darkdata-research/0.1 (salamituns.github.io; research)', 'Accept': '*/*'},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            ct = r.headers.get('Content-Type', '')
            cl = r.headers.get('Content-Length', '')
            body = r.read(400)
            print(f'- Status: **{r.status}**', file=md)
            print(f'- Content-Type: `{ct}`', file=md)
            if cl:
                print(f'- Content-Length: {cl} bytes', file=md)
            try:
                preview = body.decode('utf-8', errors='replace').strip().replace('\n', ' ')
            except Exception:
                preview = '(binary)'
            print(f'- Preview:', file=md)
            print('```', file=md)
            print(preview[:280], file=md)
            print('```', file=md)
    except urllib.error.HTTPError as e:
        print(f'- **FAIL**: HTTPError {e.code} {e.reason}', file=md)
    except Exception as e:
        print(f'- **FAIL**: {type(e).__name__}: {e}', file=md)
    print('', file=md)


with OUT.open('w') as md:
    print(f'# Eagle Ford source probe: {datetime.now():%Y-%m-%d %H:%M}\n', file=md)
    print('Reachability + response shape for each Eagle Ford source. Run before committing a pull strategy.\n', file=md)
    print('Scope: Texas only for v1. USGS Eagle Ford Group AU polygon as the basin clip. The play also extends into the Mexican subsurface (Burgos / Sabinas), but cross-border data is out of scope for this series.\n', file=md)
    for label, url, method in PROBES:
        probe(label, url, method)

print(f'wrote {OUT}')
