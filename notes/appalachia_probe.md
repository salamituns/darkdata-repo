# Appalachia source probe: 2026-04-24 22:16

Reachability + response shape for each Appalachia source. Run before committing a pull strategy.

Scope: PA + WV + OH for v1. The Appalachian Basin Province polygon also extends into NY, KY, TN, MD, VA. Those slivers are deferred.

## PA DEP: Oil and Gas home
- URL: `https://www.dep.pa.gov/Business/Energy/OilandGasPrograms/OilandGasMgmt/Oil-and-Gas-Reports/Pages/default.aspx`
- Method: GET
- Status: **200** | CT: `text/html;charset=utf-8` | CL: `489710`
- Preview: `<!DOCTYPE HTML> <html lang="en"> <head>     <meta charset="UTF-8"/>     <title>Department of Environmental Protection | Department of Environmental Protection | Commonwealth of Pennsylvania </title>     <meta name="copapwp-page-title" content="Department of Environmental Protection"/>                     <meta property="og:title" content="Department of Environmental Protection"/>     <meta property="og:image" content="https://www.pa.gov/content/dam/copapwp-pagov/en/dep/images/publishingimages/pi`

## PA DEP: Open Data Portal (eFACTS)
- URL: `https://www.depgreenport.state.pa.us/eFACTSWebSearch/`
- Method: GET
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

## PASDA: search "wells"
- URL: `https://www.pasda.psu.edu/PASDADescriptionFromKeyword?keyword=wells`
- Method: GET
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

## PASDA: PA DEP Oil and Gas Wells
- URL: `https://www.pasda.psu.edu/uci/SearchResults.aspx?Keyword=oil%20gas%20wells`
- Method: GET
- Status: **200** | CT: `text/html; charset=utf-8` | CL: `166449`
- Preview: `<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"> <HTML> 	<HEAD> 	    <meta charset="utf-8" />         <meta name="viewport" content="width=device-width,initial-scale=1" />         <meta name="robots" content="index, follow">         <meta name="keywords" content=""/>         <meta name="description" content=""/>         <title>Search Results - Pennsylvania Spatial Data Access</title>         <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/css/bootstrap.min.cs`

## PASDA: known DEP O&G shapefile
- URL: `https://www.pasda.psu.edu/spc/data/PADEP/PADEP_OilGas_Wells.zip`
- Method: HEAD
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

## PA DEP ArcGIS REST root
- URL: `https://gis.dep.pa.gov/arcgis/rest/services?f=json`
- Method: GET
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

## WV DEP: Oil and Gas home
- URL: `https://dep.wv.gov/oil-and-gas/Pages/default.aspx`
- Method: GET
- Status: **200** | CT: `text/html; charset=utf-8` | CL: `65659`
- Preview: `<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"> <html lang="en" __expr-val-dir="ltr" dir="ltr"> <head><title> 	 	Office of Oil and Gas  </title><meta charset="utf-8" /><meta name="GENERATOR" content="Microsoft SharePoint" /><meta http-equiv="Content-type" content="text/html; charset=utf-8" /><meta name="progid" content="SharePoint.WebPartPage.Document" /><meta name="viewport" content="width=device-width" /><meta property='og:descriptio`

## WV DEP: Office of Oil and Gas data
- URL: `https://dep.wv.gov/oil-and-gas/databaseinfo/Pages/default.aspx`
- Method: GET
- Status: **200** | CT: `text/html; charset=utf-8` | CL: `73573`
- Preview: `<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"> <html lang="en" __expr-val-dir="ltr" dir="ltr"> <head><title> 	 	Database Information  </title><meta charset="utf-8" /><meta name="GENERATOR" content="Microsoft SharePoint" /><meta http-equiv="Content-type" content="text/html; charset=utf-8" /><meta name="progid" content="SharePoint.WebPartPage.Document" /><meta name="viewport" content="width=device-width" /><meta property='og:description`

## WV GIS Tech Center
- URL: `https://wvgis.wvu.edu/`
- Method: GET
- Status: **200** | CT: `text/html; charset=UTF-8` | CL: `17230`
- Preview: `<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"> <html lang="en" xmlns="http://www.w3.org/1999/xhtml"> <head> <meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> <meta name="google-site-verification" content="aZSqlXKsJQYw1pV1TY9YI54bABLmPsAhd99aPcyax9o" /> <title>WVGISTC: Home</title>  <link href="/css/reset.css" rel="stylesheet" type="text/css" media="all" /> <link href="/css/layout.css" rel="stylesheet" type="text/css" `

## WV GIS Tech Center: data clearinghouse
- URL: `https://wvgis.wvu.edu/data/data.php`
- Method: GET
- Status: **200** | CT: `text/html; charset=UTF-8` | CL: `17248`
- Preview: `<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"> <html xmlns="http://www.w3.org/1999/xhtml"> <head> <meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> <title>WVGISTC: GIS Data Clearinghouse</title>   <link href="/css/reset.css" rel="stylesheet" type="text/css" media="all" /> <link href="/css/layout.css" rel="stylesheet" type="text/css" media="all" /> <link href="/css/print.css" rel="stylesheet" type="text/css" media="pr`

## WV ArcGIS Hub: search wells
- URL: `https://hub.arcgis.com/search?collection=Dataset&q=west%20virginia%20oil%20gas%20wells`
- Method: GET
- Status: **200** | CT: `text/html; charset=utf-8` | CL: `40651`
- Preview: `<!DOCTYPE html><html lang="en-us"><head>     <title>ArcGIS Hub</title><meta name="twitter:title" content="ArcGIS Hub"><meta property="og:title" content="ArcGIS Hub"><meta name="description" content="Enterprise-class geospatial collaboration platform enabling secure and open data sharing, multi-stakeholder collaboration, and community engagement across government, non-profits, academia, and private sectors."><meta name="twitter:description" content="Enterprise-class geospatial collaboration platf`

## OH DNR: Oil and Gas Resources home
- URL: `https://ohiodnr.gov/discover-and-learn/safety-conservation/about-odnr/oil-gas/oil-gas-resources`
- Method: GET
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

## OH DNR: Open Data Portal
- URL: `https://gis.ohiodnr.gov/maps3/oilgaswelllocator/`
- Method: GET
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

## OH DNR: ArcGIS REST root
- URL: `https://gis.ohiodnr.gov/arcgis/rest/services?f=json`
- Method: GET
- Status: **200** | CT: `application/json; charset=UTF-8` | CL: `349`
- Preview: `{"currentVersion":11.5,"folders":["Custom_Tools","DGS_Services","DNAP_Services","DNR_Services","DOE_Services","DOG_Services","DOW_Services","DSP_Services","DSW_Services","DWC_Services","FOR_Services","MRM_Services","OCM_Services","OIT_Services","RLM_Services","testing","Utilities"],"services":[{"name":"PheasantRelease_Fields","type":"MapServer"}]}`

## OH DNR: ArcGIS Hub search
- URL: `https://gis.ohiodnr.gov/portal/sharing/rest/search?q=oil+gas+wells&f=json`
- Method: GET
- Status: **200** | CT: `application/json; charset=utf-8` | CL: ``
- Preview: `{"total":14,"start":1,"num":10,"nextStart":11,"results":[{"id":"e70354355823425593512f3e7f7ad9b5","owner":"dnr-gisappdev","created":1748951894730,"modified":1748951894831,"guid":null,"name":"","title":"Oil/Gas Horizontal Drilling Units in Ohio","type":"Document Link","typeKeywords":["Data","Document"],"description":"<font color='#0000ff'><p><a href='https://gis.ohiodnr.gov/geodata/Statewide/HorizontalDrillingUnits.zip' rel='nofollow ugc'><strong>Download .zip<\/strong><\/a><\/font><br />This dat`

## USGS SB: search Appalachian Basin Province
- URL: `https://www.sciencebase.gov/catalog/items?q=Appalachian+Basin+Province+assessment&format=json&max=10`
- Method: GET
- Status: **FAIL TimeoutError** | CT: `` | CL: ``
- Preview: `The read operation timed out`

## USGS SB: search Marcellus Shale assessment
- URL: `https://www.sciencebase.gov/catalog/items?q=Marcellus+Shale+assessment+unit+boundaries&format=json&max=10`
- Method: GET
- Status: **FAIL TimeoutError** | CT: `` | CL: ``
- Preview: `The read operation timed out`

## USGS SB: search Utica Shale assessment
- URL: `https://www.sciencebase.gov/catalog/items?q=Utica+Shale+assessment+unit&format=json&max=10`
- Method: GET
- Status: **FAIL RemoteDisconnected** | CT: `` | CL: ``
- Preview: `Remote end closed connection without response`

---

## Round 2 conclusions (2026-04-24 22:25)

State-level downloads all HEAD-probe clean:

| State | File | Size | URL |
|---|---|---:|---|
| PA | OilGasLocations_ConventionalUnconventional2026_04 | 24 MB | pasda.psu.edu/download/dep/ |
| PA | PADEP_HistoricOilGasWells_ALL (WPA mines, K + H sheets) | 2.8 MB | pasda.psu.edu/download/dep/ |
| PA | ConservationWells2026_04 + Plugged | 0.9 MB | pasda.psu.edu/download/dep/ |
| WV | WellLocation(08-22-2016) | 15.5 MB | apps.dep.wv.gov/Documents/OOG/WellLocationData/ |
| WV | 2024 Q4 Horizontal H6A Production | 1.2 MB | apps.dep.wv.gov/Documents/OOG/ProductionReports/H6A_Production_Data/ |
| OH | DOG_Services/Oilgas_Wells_public REST query | n/a | gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0 |

USGS ScienceBase keeps timing out. EIA fallback for the basin polygon:
- `https://www.eia.gov/maps/map_data/TightOil_ShaleGas_Plays_Lower48_EIA.zip` (0.32 MB) — `ShalePlays_US_EIA_Dec2021.shp` includes Marcellus + Utica + Devonian Shale polygons. Filter to Appalachian plays for the clip envelope.

## Lit/dark proxy strategy (state-asymmetric)

  PA lit  = Unconventional well type (post-2008 Marcellus + Utica)
  PA dark = Conventional well type OR Historic-WPA-mapped pre-regulatory well

  WV lit  = API appears in 2024 Q4 H6A horizontal production filing
  WV dark = otherwise

  OH lit  = SLANT == 'Horizontal' OR Marcellus_Shale/Utica_Shale flag non-null
  OH dark = otherwise

## Vintage source

  PA: SPUD_DATE field on the Conv/Unconv shapefile (per PASDA metadata)
  WV: API_NUMBER prefix sequence + production-record cross-reference
  OH: API_WELLNO sequence (no spud-date column on the public layer)

State-line story: PA has the most lit signal (Marcellus core), WV the
deepest legacy floor (Burning Springs 1859, deep Devonian), OH the
sharpest play overlay (Utica-only horizontal era starting 2011).

