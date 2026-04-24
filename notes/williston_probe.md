# Williston source probe: 2026-04-24 18:39

Reachability + response shape for each Williston data source. Run before committing a pull strategy.

Scope: ND + MT for v1. USGS Bakken-Three Forks TPS polygon as the basin clip. SK included as a probe target only so we know what a future extension would cost.

## ND GIS Hub: portal root
- URL: `https://gishubdata.nd.gov/`
- Method: GET
- **FAIL**: URLError [Errno 8] nodename nor servname provided, or not known

## ND GIS Hub: O&G well dataset landing
- URL: `https://gishubdata.nd.gov/dataset/oil-and-gas-well-map`
- Method: GET
- **FAIL**: URLError [Errno 8] nodename nor servname provided, or not known

## ND DMR: Oil & Gas home
- URL: `https://www.dmr.nd.gov/oilgas/`
- Method: GET
- Status: **200**
- Content-Type: `text/html`
- Content-Length: 27787 bytes
- Preview:
```
 <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> <html lang="en"> <head>  	<!-- Global site tag (gtag.js) - Google Analytics --> 	<script async src="https://www
```

## ND DMR: Well search (ASPX, interactive)
- URL: `https://www.dmr.nd.gov/oilgas/findwellsvw.asp`
- Method: GET
- Status: **200**
- Content-Type: `text/html`
- Content-Length: 157304 bytes
- Preview:
```
 <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> <html lang="en">  <head> <meta http-equiv="Content-Language" content="en-us"> <meta http-equiv="Content-Ty
```

## ND DMR: GIS download page
- URL: `https://gis.dmr.nd.gov/gisdownload.asp`
- Method: GET
- Status: **200**
- Content-Type: `text/html`
- Content-Length: 15951 bytes
- Preview:
```
 <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> <html lang="en"> <title>DMR GIS</title> <head> <script language="javascript" type="text/javascript" src="https:/
```

## ND DMR: GIS landing root
- URL: `https://gis.dmr.nd.gov/`
- Method: GET
- Status: **200**
- Content-Type: `text/html`
- Content-Length: 5275 bytes
- Preview:
```
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> <html lang="en"> <title>DMR GIS</title> <head> <script language="javascript" type="text/javascript" src="https://w
```

## MT BOGC: DataMiner home
- URL: `https://bogapps.dnrc.mt.gov/dataminer/`
- Method: GET
- Status: **200**
- Content-Type: `text/html`
- Content-Length: 41547 bytes
- Preview:
```
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">  <html xmlns="http://www.w3.org/1999/xhtml" > <head><title> 	Montana Board of Oil and Gas Online Data </title><lin
```

## MT BOGC: Wells search ASPX
- URL: `https://bogapps.dnrc.mt.gov/dataminer/Wells/Wells.aspx`
- Method: GET
- Status: **200**
- Content-Type: `text/html`
- Content-Length: 64469 bytes
- Preview:
```
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">  <html xmlns="http://www.w3.org/1999/xhtml" > <head><title> 	Wells Search </title><link href="../Style/Master.css"
```

## MT BOGC: Public files / GIS directory
- URL: `https://bogwebfiles.dnrc.mt.gov/GISData/`
- Method: GET
- Status: **200**
- Content-Type: `text/html`
- Preview:
```
     <!DOCTYPE html>     <html lang="en">     <head>         <meta charset="UTF-8">         <title>GIS Data Files - MBOGC Files</title>         <link rel="preload" href="https://template.mt.gov/resources/template/images/background104.jpg" a
```

## MT BOGC: Wells.zip shapefile bundle
- URL: `https://bogwebfiles.dnrc.mt.gov/GISData/WellSurface/Wells.zip`
- Method: HEAD
- **FAIL**: HTTPError 404 404

## MT BOGC: WellPaths.zip directional bundle
- URL: `https://bogwebfiles.dnrc.mt.gov/GISData/WellPaths/WellPaths.zip`
- Method: HEAD
- **FAIL**: HTTPError 404 404

## USGS ScienceBase: 2021 Bakken-Three Forks AU item (JSON)
- URL: `https://www.sciencebase.gov/catalog/item/618e90c8d34ec04fc9caa732?format=json`
- Method: GET
- Status: **200**
- Content-Type: `application/json`
- Preview:
```
{"link":{"rel":"self","url":"https://www.sciencebase.gov/catalog/item/618e90c8d34ec04fc9caa732"},"relatedItems":{"link":{"url":"https://www.sciencebase.gov/catalog/itemLinks?itemId=618e90c8d34ec04fc9caa732","rel":"related"}},"id":"618e90c8d
```

## USGS ScienceBase: ThreeForksAUs.shp direct download
- URL: `https://www.sciencebase.gov/catalog/file/get/618e90c8d34ec04fc9caa732?f=__disk__03%2Ffc%2F71%2F03fc71291ced4a7b69837d2e8d3035d51bcacc81`
- Method: HEAD
- Status: **200**
- Content-Type: `x-gis/x-shapefile`
- Content-Length: 457212 bytes

## USGS ScienceBase: bundle ZIP for item 618e90c8
- URL: `https://www.sciencebase.gov/catalog/file/get/618e90c8d34ec04fc9caa732`
- Method: HEAD
- Status: **200**

## SK GeoHub Economic Resources viewer
- URL: `https://gisappl.saskatchewan.ca/Html5Ext/Index.html?Viewer=EconomicResourceInfoMap`
- Method: GET
- Status: **200**
- Content-Type: `text/html`
- Content-Length: 2532 bytes
- Preview:
```
﻿<!doctype html> <html> <head>     <meta charset="utf-8" />     <meta name="viewport" content="width=device-width,user-scalable=no,initial-scale=1" />     <meta http-equiv="X-UA-Compatible" content="IE=edge" />     <title>Geocortex 
```
