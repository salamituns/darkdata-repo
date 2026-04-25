"""
Appalachia source probe. Reachability + response shape only.

Targets:
  PA DEP / PASDA:    PA wells + spud + permit data (PA is the most
                     transparent oil/gas regulator in the US)
  WV DEP:            West Virginia oil/gas wells (Marcellus south,
                     deep Devonian)
  Ohio DNR DOG:      Ohio Utica + legacy oil/gas wells (ArcGIS Hub)
  USGS ScienceBase:  Appalachian Basin Province / Marcellus AU /
                     Utica AU polygons for the basin clip

Scope: PA + WV + OH for v1. The Appalachian Basin Province polygon
also extends into NY, KY, TN, MD, VA. Those slivers are deferred.
"""
import urllib.request
import urllib.error
import json
from pathlib import Path
from datetime import datetime

OUT = Path('/Users/olatunde/CoWorker/Geoworks/darkdata-repo/notes/appalachia_probe.md')


def fetch(url, method='GET', timeout=30):
    req = urllib.request.Request(
        url, method=method,
        headers={'User-Agent': 'darkdata-research/0.1', 'Accept': '*/*'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.headers.get('Content-Type', ''), r.headers.get('Content-Length', ''), r.read(700)
    except urllib.error.HTTPError as e:
        return f'HTTPError {e.code}', '', '', b''
    except Exception as e:
        return f'FAIL {type(e).__name__}', '', '', str(e).encode()


PROBES = [
    # Pennsylvania
    ('PA DEP: Oil and Gas home', 'https://www.dep.pa.gov/Business/Energy/OilandGasPrograms/OilandGasMgmt/Oil-and-Gas-Reports/Pages/default.aspx', 'GET'),
    ('PA DEP: Open Data Portal (eFACTS)', 'https://www.depgreenport.state.pa.us/eFACTSWebSearch/', 'GET'),
    ('PASDA: search "wells"', 'https://www.pasda.psu.edu/PASDADescriptionFromKeyword?keyword=wells', 'GET'),
    ('PASDA: PA DEP Oil and Gas Wells', 'https://www.pasda.psu.edu/uci/SearchResults.aspx?Keyword=oil%20gas%20wells', 'GET'),
    ('PASDA: known DEP O&G shapefile', 'https://www.pasda.psu.edu/spc/data/PADEP/PADEP_OilGas_Wells.zip', 'HEAD'),
    ('PA DEP ArcGIS REST root', 'https://gis.dep.pa.gov/arcgis/rest/services?f=json', 'GET'),
    # West Virginia
    ('WV DEP: Oil and Gas home', 'https://dep.wv.gov/oil-and-gas/Pages/default.aspx', 'GET'),
    ('WV DEP: Office of Oil and Gas data', 'https://dep.wv.gov/oil-and-gas/databaseinfo/Pages/default.aspx', 'GET'),
    ('WV GIS Tech Center', 'https://wvgis.wvu.edu/', 'GET'),
    ('WV GIS Tech Center: data clearinghouse', 'https://wvgis.wvu.edu/data/data.php', 'GET'),
    ('WV ArcGIS Hub: search wells', 'https://hub.arcgis.com/search?collection=Dataset&q=west%20virginia%20oil%20gas%20wells', 'GET'),
    # Ohio
    ('OH DNR: Oil and Gas Resources home', 'https://ohiodnr.gov/discover-and-learn/safety-conservation/about-odnr/oil-gas/oil-gas-resources', 'GET'),
    ('OH DNR: Open Data Portal', 'https://gis.ohiodnr.gov/maps3/oilgaswelllocator/', 'GET'),
    ('OH DNR: ArcGIS REST root', 'https://gis.ohiodnr.gov/arcgis/rest/services?f=json', 'GET'),
    ('OH DNR: ArcGIS Hub search', 'https://gis.ohiodnr.gov/portal/sharing/rest/search?q=oil+gas+wells&f=json', 'GET'),
    # USGS Appalachian Province
    ('USGS SB: search Appalachian Basin Province', 'https://www.sciencebase.gov/catalog/items?q=Appalachian+Basin+Province+assessment&format=json&max=10', 'GET'),
    ('USGS SB: search Marcellus Shale assessment', 'https://www.sciencebase.gov/catalog/items?q=Marcellus+Shale+assessment+unit+boundaries&format=json&max=10', 'GET'),
    ('USGS SB: search Utica Shale assessment', 'https://www.sciencebase.gov/catalog/items?q=Utica+Shale+assessment+unit&format=json&max=10', 'GET'),
]


lines = []
lines.append(f'# Appalachia source probe: {datetime.now():%Y-%m-%d %H:%M}\n')
lines.append('Reachability + response shape for each Appalachia source. Run before committing a pull strategy.\n')
lines.append('Scope: PA + WV + OH for v1. The Appalachian Basin Province polygon also extends into NY, KY, TN, MD, VA. Those slivers are deferred.\n')

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
