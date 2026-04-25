# Eagle Ford source probe: 2026-04-24 20:23

Reachability + response shape for each Eagle Ford source. Run before committing a pull strategy.

Scope: Texas only for v1. USGS Eagle Ford Group AU polygon as the basin clip. The play also extends into the Mexican subsurface (Burgos / Sabinas), but cross-border data is out of scope for this series.

## TX RRC: home
- URL: `https://www.rrc.texas.gov/`
- Method: GET
- Status: **200**
- Content-Type: `text/html; charset=utf-8`
- Preview:
```
<!DOCTYPE html> <html lang="en">   <head>     <meta charset="UTF-8" />     <meta name="viewport" content="width=device-width, initial-scale=1.0" />     <meta http-equiv="X-UA-Compatible" content="ie=edge" />      <link rel="image_src" href="https://www.rrc.texas.gov/media/3
```

## TX RRC: data sets for download
- URL: `https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/`
- Method: GET
- Status: **200**
- Content-Type: `text/html; charset=utf-8`
- Preview:
```
<!DOCTYPE html> <html lang="en">   <head>     <meta charset="UTF-8" />     <meta name="viewport" content="width=device-width, initial-scale=1.0" />     <meta http-equiv="X-UA-Compatible" content="ie=edge" />      <link rel="image_src" href="https://www.rrc.texas.gov/media/3
```

## TX RRC: oil & gas well download
- URL: `https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/oil-gas/`
- Method: GET
- **FAIL**: HTTPError 404 Not Found

## TX RRC GIS public viewer
- URL: `https://gis.rrc.texas.gov/GISViewer/`
- Method: GET
- Status: **200**
- Content-Type: `text/html`
- Content-Length: 39327 bytes
- Preview:
```
﻿<!DOCTYPE html> <html xmlns="https://www.w3.org/1999/html"> <head>     <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />     <meta http-equiv="X-UA-Compatible" content="IE=7,IE=9,IE=10" />     <title></title>     <script type="text/javascript" src="http
```

## TX RRC GIS REST root
- URL: `https://gis2.rrc.texas.gov/arcgis/rest/services`
- Method: GET
- **FAIL**: URLError: <urlopen error timed out>

## TX RRC GIS REST: PublicGISViewer folder
- URL: `https://gis2.rrc.texas.gov/arcgis/rest/services/PublicGISViewer?f=json`
- Method: GET
- **FAIL**: URLError: <urlopen error [Errno 51] Network is unreachable>

## TX RRC GIS REST: PublicGISViewer/MapServer
- URL: `https://gis2.rrc.texas.gov/arcgis/rest/services/PublicGISViewer/MapServer?f=json`
- Method: GET
- **FAIL**: URLError: <urlopen error [Errno 51] Network is unreachable>

## TX RRC GIS REST: Production folder
- URL: `https://gis2.rrc.texas.gov/arcgis/rest/services/Production?f=json`
- Method: GET
- **FAIL**: URLError: <urlopen error [Errno 51] Network is unreachable>

## TX RRC GIS REST: Wells folder
- URL: `https://gis2.rrc.texas.gov/arcgis/rest/services/Wells?f=json`
- Method: GET
- **FAIL**: URLError: <urlopen error timed out>

## TX RRC GIS REST: OG_Wells layer attempt
- URL: `https://gis2.rrc.texas.gov/arcgis/rest/services/OG/MapServer?f=json`
- Method: GET
- **FAIL**: URLError: <urlopen error [Errno 51] Network is unreachable>

## USGS GMC: National Map Energy Resources
- URL: `https://www.usgs.gov/programs/energy-resources-program`
- Method: GET
- Status: **200**
- Content-Type: `text/html; charset=UTF-8`
- Preview:
```
<!DOCTYPE html> <html lang="en" dir="ltr" prefix="og: https://ogp.me/ns#"> <head>   <!-- Google Tag Manager -->   <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':         new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],       j=d.createE
```

## USGS ScienceBase: Eagle Ford 2018 assessment item
- URL: `https://www.sciencebase.gov/catalog/item/5b2cd7a0e4b056a4f8b0a5e5?format=json`
- Method: GET
- **FAIL**: HTTPError 404 404

## USGS ScienceBase: Eagle Ford alternate 2018 assessment item
- URL: `https://www.sciencebase.gov/catalog/item/5a8b66d2e4b00f54eb19d39d?format=json`
- Method: GET
- **FAIL**: HTTPError 404 404

## USGS ScienceBase: National Assessment search root
- URL: `https://www.sciencebase.gov/catalog/items?q=Eagle+Ford+Group+assessment+units&format=json&max=10`
- Method: GET
- Status: **200**
- Content-Type: `application/json;charset=UTF-8`
- Preview:
```
{"total":4,"took":"520ms","selflink":{"rel":"self","url":"https://www.sciencebase.gov/catalog/items/get?q=Eagle+Ford+Group+assessment+units&format=json&max=10"},"items":[{"link":{"rel":"self","url":"https://www.sciencebase.gov/catalog/item/64f9e883d34ed30c2054ae36"},"relatedItems
```


---

# Eagle Ford probe round 2: 2026-04-24 20:41

## ScienceBase search hits resolution

Total hits: 4

- **Estimated Ultimate Recoveries of Oil Wells in the Eagle Ford Group and Associated Cenomanian–Turonian Strata, U.S. Gulf Coast, Texas, 2018**
  - ID: `64f9e883d34ed30c2054ae36`
  - Link: https://www.sciencebase.gov/catalog/item/64f9e883d34ed30c2054ae36
  - Files (2):
    - `Eagle_Ford_EURs_1mile.csv` 0.25 MB  -> https://www.sciencebase.gov/catalog/file/get/64f9e883d34ed30c2054ae36?f=__disk__7d%2F37%2F39%2F7d373935867d04bda61e4fc58cc18030452dac02
    - `Eagle_Ford_EURs_1mile.xml` 0.01 MB  -> https://www.sciencebase.gov/catalog/file/get/64f9e883d34ed30c2054ae36?f=__disk__88%2Fe5%2F3e%2F88e53ebf8f19a95a4935f9da8cecd0492d6896a7
  - WebLinks (1):
    - Whidden, K.J., Pitman, J.K., Pearson, O.N., Paxton, S.T., Kinney, S.A., Gianoutsos, N.J., Schenk, C.J., Leathers-Miller, H.M., Birdwell, J.E., Brownfield, M.E., Burke, L.A., Dubiel, R.F., French, K.L., Gaswirth, S.B., Haines, S.S., Le, P.A., Marra, K.R., Mercier, T.J., Tennyson, M.E., and Woodall, C.A., 2018, Assessment of undiscovered oil and gas resources in the Eagle Ford Group and associated Cenomanian–Turonian strata, U.S. Gulf Coast, Texas, 2018: U.S. Geological Survey Fact Sheet 2018–3033, 4 p., https://doi.org/10.3133/fs20183033.: https://doi.org/10.3133/fs20183033

- **Input forms for 2019 water and proppant assessment of the Eagle Ford Group, Gulf Coast, Texas**
  - ID: `5f11df1682ce21d4c409d281`
  - Link: https://www.sciencebase.gov/catalog/item/5f11df1682ce21d4c409d281
  - Files (6):
    - `Input_form_Eagle_Ford_Marl_Continuous_Gas.xlsx` 0.04 MB  -> https://www.sciencebase.gov/catalog/file/get/5f11df1682ce21d4c409d281?f=__disk__59%2F53%2F50%2F59535038ba86773338d298c9e34e2f78b7dc6a3c
    - `Input_form_Eagle_Ford_Marl_Continuous_Oil.xlsx` 0.04 MB  -> https://www.sciencebase.gov/catalog/file/get/5f11df1682ce21d4c409d281?f=__disk__37%2Ffa%2F45%2F37fa45d2f15f23d2cf42ff0f51a37869b4196a4d
    - `Input_form_Eagle_Ford_Submarine_Plateau-Karnes_Trough_Continuous_Gas.xlsx` 0.04 MB  -> https://www.sciencebase.gov/catalog/file/get/5f11df1682ce21d4c409d281?f=__disk__6d%2Fc5%2F44%2F6dc54480cdca80bce3c452e1cf8052d3cf6542ce
    - `Input_form_Eagle_Ford_Submarine_Plateau-Karnes_Trough_Continuous_Oil.xlsx` 0.04 MB  -> https://www.sciencebase.gov/catalog/file/get/5f11df1682ce21d4c409d281?f=__disk__fc%2F36%2Fe4%2Ffc36e406ec2d160d4db92edaf3595a723765b6e5
    - `P9NWKE6G_metadata.xml` 0.02 MB  -> https://www.sciencebase.gov/catalog/file/get/5f11df1682ce21d4c409d281?f=__disk__9e%2F71%2Fce%2F9e71ce752f0c9a0b2823bf2d506a7e1322d220d2
    - `browse_graphic_landscape.png` 0.28 MB  -> https://www.sciencebase.gov/catalog/file/get/5f11df1682ce21d4c409d281?f=__disk__d4%2F20%2Fa4%2Fd420a499c13f887feb1946d1e7838bb75fcc6509
  - WebLinks (1):
    - Assessment of water and proppant quantities associated with petroleum production from the Eagle Ford Group, Gulf Coast, Texas, 2019: https://doi.org/10.3133/fs20203037

- **USGS Gulf Coast Petroleum Systems, and National and Global Oil and Gas Assessment Projects-Eagle Ford Group and Associated Cenomanian-Turonian Strata Assessment Unit Boundaries and Assessment Input Data Forms**
  - ID: `5d1246c2e4b0941bde56e84f`
  - Link: https://www.sciencebase.gov/catalog/item/5d1246c2e4b0941bde56e84f
  - Files (21):
    - `EaglefordAUs.jpg` 0.04 MB  -> https://www.sciencebase.gov/catalog/file/get/5d1246c2e4b0941bde56e84f?f=__disk__ee%2F05%2F77%2Fee05770091d4e842a44ead8aedcc413178c686e4
    - `EagleFordAUs.gdb.zip` 0.42 MB  -> https://www.sciencebase.gov/catalog/file/get/5d1246c2e4b0941bde56e84f?f=__disk__f8%2F15%2F06%2Ff81506a7dcf2f41e94690ddfbd893b6e4db9ccfa
    - `EagleFordAUs.geojson` 3.32 MB  -> https://www.sciencebase.gov/catalog/file/get/5d1246c2e4b0941bde56e84f?f=__disk__8a%2F67%2F40%2F8a674006d02b243c47590f41df3e293cde65d19b
    - `EagleFordAUs.gml` 2.23 MB  -> https://www.sciencebase.gov/catalog/file/get/5d1246c2e4b0941bde56e84f?f=__disk__07%2Fa9%2F0e%2F07a90e437ab1faa88b094ec8be66af565a1db724
    - `EagleFordAUs.xsd` 0.00 MB  -> https://www.sciencebase.gov/catalog/file/get/5d1246c2e4b0941bde56e84f?f=__disk__02%2F73%2F19%2F0273192ab861a514512f7166111ccba4eac2e7c0
    - `u50490173_Allocations.pdf` 0.37 MB  -> https://www.sciencebase.gov/catalog/file/get/5d1246c2e4b0941bde56e84f?f=__disk__ab%2F86%2F72%2Fab8672ad5310aa37ad5ffe3191786d99496b8c33
    - `u50490173_ContinuousForm.pdf` 0.08 MB  -> https://www.sciencebase.gov/catalog/file/get/5d1246c2e4b0941bde56e84f?f=__disk__43%2F2f%2F69%2F432f69731debca65aa4f166e81265f0c9ee5e181
    - `u50490174_Allocations.pdf` 0.37 MB  -> https://www.sciencebase.gov/catalog/file/get/5d1246c2e4b0941bde56e84f?f=__disk__3f%2Ff5%2Fcf%2F3ff5cf5eb5827b20364964fb503f527a54d9ad40
  - WebLinks (2):
    - : https://doi.org/10.3133/fs20183033
    - USGS Eagle Ford Group AUs (2018): https://www.sciencebase.gov/catalog/file/get/5d1246c2e4b0941bde56e84f?f=__disk__ee%2F05%2F77%2Fee05770091d4e842a44ead8aedcc413178c686e4

- **Wireline geophysical logging curves and infrared spectral data for the USGS Gulf Coast #1 West Woodway research wellbore, McLennan County, Texas**
  - ID: `5f4555cc82ce4c3d1225195e`
  - Link: https://www.sciencebase.gov/catalog/item/5f4555cc82ce4c3d1225195e
  - Files (7):
    - `WireLine FTIR Data Release.xlsx` 3.45 MB  -> https://www.sciencebase.gov/catalog/file/get/5f4555cc82ce4c3d1225195e?f=__disk__9d%2F10%2F97%2F9d109762a511772f8509bc5b2bda25524798e5fd
    - `wireline_geophysical_welllogs.csv` 0.84 MB  -> https://www.sciencebase.gov/catalog/file/get/5f4555cc82ce4c3d1225195e?f=__disk__83%2Fa9%2Fd5%2F83a9d5f0742d8ad74cfd2736b151605df83d081c
    - `FTIR_spectra.csv` 2.76 MB  -> https://www.sciencebase.gov/catalog/file/get/5f4555cc82ce4c3d1225195e?f=__disk__bc%2F62%2F1f%2Fbc621ff6b0cb374b1e6ba038415a0c3335472daa
    - `wireline_geophysical_welllogs_datadictionary.csv` 0.00 MB  -> https://www.sciencebase.gov/catalog/file/get/5f4555cc82ce4c3d1225195e?f=__disk__11%2Faa%2Fd5%2F11aad55a7a00149e8e871c08ba8ca1af01382be6
    - `FTIR_datadictionary.csv` 0.00 MB  -> https://www.sciencebase.gov/catalog/file/get/5f4555cc82ce4c3d1225195e?f=__disk__97%2F22%2F86%2F97228636bec02a7f2e608d1ca1ad525055c465e5
    - `browse_graphic.jpg` 0.05 MB  -> https://www.sciencebase.gov/catalog/file/get/5f4555cc82ce4c3d1225195e?f=__disk__c2%2F7e%2F21%2Fc27e21aabf14446bc82a372864c5984083abb611
    - `P9KZVG7P_metadata.xml` 0.02 MB  -> https://www.sciencebase.gov/catalog/file/get/5f4555cc82ce4c3d1225195e?f=__disk__ef%2F86%2F52%2Fef8652ea722f08f639c91351fdfff2e1dfab98cc
  - WebLinks (1):
    - Multimineral petrophysics of thermally immature Eagle Ford Group and Cretaceous mudstones, U.S. Geological Survey Gulf Coast 1 research wellbore in central Texas Burke, Lauri A. et al. Interpretation (2022),10(1):T151 https://doi.org/10.1190/int-2021-0094.1: https://doi.org/10.1190/int-2021-0094.1


## Alternate TX RRC endpoints

### TX RRC GIS (no 2): home
- URL: `https://gis.rrc.texas.gov/`
- Status: **200** | CT: `text/html` | CL: `39327`
- Preview: `﻿<!DOCTYPE html> <html xmlns="https://www.w3.org/1999/html"> <head>     <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />     <meta http-equiv="X-UA-Compatible" content="IE=7,IE=9,IE=10" />     <title></title>     `

### TX RRC GIS (no 2): REST root
- URL: `https://gis.rrc.texas.gov/arcgis/rest/services?f=json`
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

### TX RRC GIS (no 2): PublicGISViewer
- URL: `https://gis.rrc.texas.gov/arcgis/rest/services/PublicGISViewer?f=json`
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

### TX RRC GIS (no 2): PublicGISViewer/MapServer
- URL: `https://gis.rrc.texas.gov/arcgis/rest/services/PublicGISViewer/MapServer?f=json`
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

### TX RRC GIS (no 2): OilGasFeatureService
- URL: `https://gis.rrc.texas.gov/arcgis/rest/services/PublicGISViewer/MapServer/0?f=json`
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``


## Texas Open Data + alternate hosts

### Texas Open Data: domain
- URL: `https://data.texas.gov/`
- Status: **200** | CT: `text/html; charset=utf-8` | CL: ``
- Preview: `<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" xmlns:og="http://opengraphprotocol.org/schema/">     <!--   Powered by Socrata   http://www.socrata.com   -->        <head>     <meta http-equiv="content-type" content="text/html;charset=utf-8" />     <meta http-equiv="X-U`

### Texas Open Data: search Eagle Ford
- URL: `https://data.texas.gov/api/views.json?search=Eagle+Ford&limit=5`
- Status: **200** | CT: `application/json; charset=utf-8` | CL: ``
- Preview: `[ {   "id" : "cerf-ms45",   "name" : "High Value Dataset: March 2026",   "assetType" : "dataset",   "averageRating" : 0,   "createdAt" : 1777035532,   "description" : "Currently incarcerated inmate population with relevant demographic, offense, and parole information.",   "diciBackend" : false,   "displayType" : "table",   "downloadCount" : 1,   "hideFromCatalog" : false,   "hideFromDataJson" : fa`

### TX RRC: GIS files / shapefile downloads index
- URL: `https://gis.rrc.texas.gov/files/`
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

### TX RRC: data sets HTML body
- URL: `https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/`
- Status: **200** | CT: `text/html; charset=utf-8` | CL: ``
- Preview: `<!DOCTYPE html> <html lang="en">   <head>     <meta charset="UTF-8" />     <meta name="viewport" content="width=device-width, initial-scale=1.0" />     <meta http-equiv="X-UA-Compatible" content="ie=edge" />      <link rel="image_src" href="https://www.rrc.texas.gov/media/343bcauv/rrcleadingenergy_640.jpg" />       <title>Data Sets Available for Download</title> <meta name="Name" conte`

---

# Eagle Ford probe round 3 (HIFLD + fallbacks): 2026-04-24 20:42

### HIFLD: Oil and Natural Gas Wells layer
- URL: `https://hifld-geoplatform.opendata.arcgis.com/datasets/oil-and-natural-gas-wells/about`
- Method: GET
- Status: **200** | CT: `text/html; charset=utf-8` | CL: `14865`
- Preview: `<!DOCTYPE html><html lang="en"><head><title>ArcGIS Hub</title><meta name="twitter:title" content="ArcGIS Hub"><meta property="og:title" content="ArcGIS Hub"><meta name="description" content="Discover, analyze and download data from ArcGIS Hub. Download in CSV, KML, Zip, GeoJSON, GeoTIFF or PNG. Find API links for GeoServices, WMS, and WFS. Analyze with charts and thematic maps. Take the next step and create StoryMaps and Web Maps."><meta name="twitter:description" content="Discover, analyze and `

### HIFLD: ArcGIS Hub item search
- URL: `https://hifld-geoplatform.opendata.arcgis.com/api/feed/dcat-us/1.1.json?q=oil+gas+wells`
- Method: GET
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

### HIFLD: known Wells FeatureServer guess
- URL: `https://services.arcgis.com/jIL9msH9OI208GCb/arcgis/rest/services/Oil_and_Natural_Gas_Wells/FeatureServer?f=json`
- Method: GET
- Status: **200** | CT: `application/json; charset=utf-8` | CL: `103`
- Preview: `{"error":{"code":499,"message":"Token Required","messageCode":"GWM_0003","details":["Token Required"]}}`

### HIFLD: alt FeatureServer arcgis.com
- URL: `https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Oil_and_Natural_Gas_Wells/FeatureServer?f=json`
- Method: GET
- Status: **200** | CT: `application/json; charset=utf-8` | CL: `154`
- Preview: `{"error":{"code":400,"message":"Item does not exist or is inaccessible.","messageCode":"CONT_0001","details":["Item does not exist or is inaccessible."]}}`

### HIFLD via DHS GII
- URL: `https://gii.dhs.gov/HIFLD`
- Method: GET
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

### HIFLD search shim
- URL: `https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services?f=json`
- Method: GET
- Status: **200** | CT: `application/json; charset=utf-8` | CL: `41134`
- Preview: `{"currentVersion":12,"services":[{"name":"2013 Metro-North Railroad Accident - Hospital Routes","type":"FeatureServer","url":"https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/2013 Metro-North Railroad Accident - Hospital Routes/FeatureServer"},{"name":"Active_Article_III_Federal_Judge","type":"FeatureServer","url":"https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/Active_Article_III_Federal_Judge/FeatureServer"},{"name":"Administrative_Forest_Boundaries","type"`

### USGS National Map Energy: oil & gas wells
- URL: `https://energy.usgs.gov/Coal/Resources.aspx`
- Method: GET
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

### TX RRC: known shapefile bulk OG_WELLS direct
- URL: `https://gis.rrc.texas.gov/files/OG_WELLS.zip`
- Method: HEAD
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

### TX RRC: known shapefile bulk Wells direct
- URL: `https://gis.rrc.texas.gov/files/Wells.zip`
- Method: HEAD
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

### TX RRC: GIS data via wwwGIS
- URL: `https://wwwgisp.rrc.state.tx.us/GISViewer2/`
- Method: GET
- Status: **FAIL URLError** | CT: `` | CL: ``
- Preview: `<urlopen error [Errno 8] nodename nor servname provided, or not known>`

### TX RRC: TXOG download portal
- URL: `https://www.rrc.texas.gov/oil-and-gas/research-and-statistics/well-information/`
- Method: GET
- Status: **200** | CT: `text/html; charset=utf-8` | CL: ``
- Preview: `<!DOCTYPE html> <html lang="en">   <head>     <meta charset="UTF-8" />     <meta name="viewport" content="width=device-width, initial-scale=1.0" />     <meta http-equiv="X-UA-Compatible" content="ie=edge" />      <link rel="image_src" href="https://www.rrc.texas.gov/media/343bcauv/rrcleadingenergy_640.jpg" />       <title>Well Information</title> <meta name="Name" content="Well Information" /> <meta name="Description" content="Well Information - well counts and distribution" /> <meta`
