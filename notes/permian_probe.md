# Permian source probe: 2026-04-24 16:23

Reachability + response shape for each Permian data source. Run before committing a pull strategy.

## TX RRC: Data Sets Available for Download (HTML index)
- URL: `https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/`
- Method: HEAD
- Status: **200**
- Content-Type: `text/html`

## TX RRC: GIS Viewer (HTML)
- URL: `https://www.rrc.texas.gov/resource-center/research/gis-viewer/`
- Method: HEAD
- Status: **200**
- Content-Type: `text/html`

## TX RRC: ArcGIS REST services root
- URL: `https://gis.rrc.texas.gov/arcgis/rest/services?f=json`
- Method: GET
- **FAIL**: HTTPError 404 Not Found

## TX RRC: Public GIS Viewer Surface Hole Locations (ArcGIS REST)
- URL: `https://gis.rrc.texas.gov/arcgis/rest/services/Public_GIS_Viewer/MapServer?f=json`
- Method: GET
- **FAIL**: HTTPError 404 Not Found

## NM OCD: Permitting home (HTML)
- URL: `https://wwwapps.emnrd.nm.gov/ocd/ocdpermitting/`
- Method: HEAD
- Status: **200**
- Content-Type: `text/html`
- Content-Length: 77091 bytes

## NM OCD: GIS page (HTML)
- URL: `https://wwwapps.emnrd.nm.gov/ocd/ocdpermitting/Reporting/GIS/GIS.aspx`
- Method: HEAD
- Status: **200**
- Content-Type: `text/html`
- Content-Length: 70847 bytes

## NM OCD: Wells search (HTML)
- URL: `https://wwwapps.emnrd.nm.gov/ocd/ocdpermitting/Data/Wells/Wells.aspx`
- Method: HEAD
- Status: **200**
- Content-Type: `text/html`
- Content-Length: 68516 bytes

## USGS: Permian Basin province boundary (ScienceBase item page)
- URL: `https://www.sciencebase.gov/catalog/item/5a3c7c2ce4b00f54eb1e85b3`
- Method: HEAD
- **FAIL**: HTTPError 404 404
