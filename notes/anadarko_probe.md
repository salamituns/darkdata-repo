# Anadarko source probe: 2026-04-24 20:54

Reachability + response shape for each Anadarko source. Run before committing a pull strategy.

Scope: OK + KS portions of the Anadarko Basin Province. TX Panhandle deferred (TX RRC is JSF-session blocked, same as Eagle Ford). KGS already in pipeline from basin 01.

## OCC: Oil & Gas home
- URL: `https://oklahoma.gov/occ/divisions/oil-gas.html`
- Method: GET
- Status: **200** | CT: `text/html;charset=utf-8` | CL: ``
- Preview: `<!DOCTYPE HTML> <html lang="en">     <head>     <meta charset="UTF-8"/>  <meta name="description" content="The Oil and Gas Conservation Division mission is to provide information, permitting, investigation, and compliance services to the oil and gas industry, mineral interests, landowners, and the general public so together we can develop the oil and gas resources of the state in a fair and orderly manner while protecting the environment and ensuring public safety."/> <meta name="template" conte`

## OCC: Oil & Gas Data Files
- URL: `https://oklahoma.gov/occ/divisions/oil-gas/oil-gas-data.html`
- Method: GET
- Status: **200** | CT: `text/html;charset=utf-8` | CL: ``
- Preview: `<!DOCTYPE HTML> <html lang="en">     <head>     <meta charset="UTF-8"/>  <meta name="description" content="Downloadable files that include information regarding oil, gas and underground injection wells, as well as geologic and historical data files."/> <meta name="template" content="One Column Full Width Page"/> <meta name="viewport" content="width=device-width, initial-scale=1"/> <meta http-equiv="Last-Modified" content="20-04-2026 04:21:21"/>  <meta http-equiv="X-UA-Compatible" content="ie=edg`

## OCC: Wells Database (legacy)
- URL: `https://www.occeweb.com/og/oghome.htm`
- Method: GET
- Status: **FAIL URLError** | CT: `` | CL: ``
- Preview: `<urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1006)>`

## OCC: GIS portal (legacy)
- URL: `https://gisservices.occ.ok.gov/arcgis/rest/services?f=json`
- Method: GET
- Status: **FAIL URLError** | CT: `` | CL: ``
- Preview: `<urlopen error [Errno 8] nodename nor servname provided, or not known>`

## OCC: GIS REST OG service guess
- URL: `https://gisservices.occ.ok.gov/arcgis/rest/services/OG/MapServer?f=json`
- Method: GET
- Status: **FAIL URLError** | CT: `` | CL: ``
- Preview: `<urlopen error [Errno 8] nodename nor servname provided, or not known>`

## OGS: home
- URL: `https://www.ou.edu/ogs`
- Method: GET
- Status: **200** | CT: `text/html; charset=UTF-8` | CL: `84196`
- Preview: `<!DOCTYPE HTML> <html  lang="en-US"> <head>     <meta http-equiv="X-UA-Compatible" content="IE=edge"/>     <meta http-equiv="content-type" content="text/html; charset=UTF-8">                         <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements --> <!--[if lt IE 9]>    <script src="//html5shim.googlecode.com/svn/trunk/html5.js"></script> <![endif]-->  <!-- and, for now, we go ahead and load component javascript in the head --> <script src="/etc/designs/deptB-basic/components.js"></scri`

## OGS: data downloads
- URL: `https://www.ou.edu/ogs/data`
- Method: GET
- Status: **200** | CT: `text/html; charset=UTF-8` | CL: `14906`
- Preview: `<!DOCTYPE HTML> <html  lang="en-US"> <head>     <meta http-equiv="X-UA-Compatible" content="IE=edge"/>     <meta http-equiv="content-type" content="text/html; charset=UTF-8">                         <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements --> <!--[if lt IE 9]>    <script src="//html5shim.googlecode.com/svn/trunk/html5.js"></script> <![endif]-->  <!-- and, for now, we go ahead and load component javascript in the head --> <script src="/etc/designs/deptB-basic/components.js"></scri`

## OGS: well data
- URL: `https://www.ou.edu/ogs/data/wells`
- Method: GET
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

## OK Open Data: ArcGIS Hub
- URL: `https://hub.arcgis.com/search?collection=Dataset&q=oklahoma%20wells`
- Method: GET
- Status: **200** | CT: `text/html; charset=utf-8` | CL: `40651`
- Preview: `<!DOCTYPE html><html lang="en-us"><head>     <title>ArcGIS Hub</title><meta name="twitter:title" content="ArcGIS Hub"><meta property="og:title" content="ArcGIS Hub"><meta name="description" content="Enterprise-class geospatial collaboration platform enabling secure and open data sharing, multi-stakeholder collaboration, and community engagement across government, non-profits, academia, and private sectors."><meta name="twitter:description" content="Enterprise-class geospatial collaboration platf`

## OK Geospatial Clearinghouse
- URL: `https://csa.ou.edu/clearinghouse/`
- Method: GET
- Status: **FAIL URLError** | CT: `` | CL: ``
- Preview: `<urlopen error [Errno 8] nodename nor servname provided, or not known>`

## USGS SB: search Anadarko Basin Province assessment units
- URL: `https://www.sciencebase.gov/catalog/items?q=Anadarko+Basin+Province+assessment+units&format=json&max=10`
- Method: GET
- Status: **200** | CT: `application/json;charset=UTF-8` | CL: ``
- Preview: `{"total":1,"took":"91ms","selflink":{"rel":"self","url":"https://www.sciencebase.gov/catalog/items/get?q=Anadarko+Basin+Province+assessment+units&format=json&max=10"},"items":[{"link":{"rel":"self","url":"https://www.sciencebase.gov/catalog/item/60c8c47ed34e86b9389dc628"},"relatedItems":{"link":{"url":"https://www.sciencebase.gov/catalog/itemLinks?itemId=60c8c47ed34e86b9389dc628","rel":"related"}},"id":"60c8c47ed34e86b9389dc628","title":"National Assessment of Oil and Gas Project Anadarko Basin `

## USGS SB: search Woodford Shale assessment
- URL: `https://www.sciencebase.gov/catalog/items?q=Woodford+Shale+assessment+continuous&format=json&max=10`
- Method: GET
- Status: **200** | CT: `application/json;charset=UTF-8` | CL: ``
- Preview: `{"total":1,"took":"32ms","selflink":{"rel":"self","url":"https://www.sciencebase.gov/catalog/items/get?q=Woodford+Shale+assessment+continuous&format=json&max=10"},"items":[{"link":{"rel":"self","url":"https://www.sciencebase.gov/catalog/item/694ab444d4be023a64292c12"},"relatedItems":{"link":{"url":"https://www.sciencebase.gov/catalog/itemLinks?itemId=694ab444d4be023a64292c12","rel":"related"}},"id":"694ab444d4be023a64292c12","title":"USGS National and Global Oil and Gas Assessment Project—Permia`

## USGS SB: search Cana Woodford
- URL: `https://www.sciencebase.gov/catalog/items?q=Cana+Woodford+assessment+unit&format=json&max=10`
- Method: GET
- Status: **200** | CT: `application/json;charset=UTF-8` | CL: ``
- Preview: `{"total":0,"took":"17ms","selflink":{"rel":"self","url":"https://www.sciencebase.gov/catalog/items/get?q=Cana+Woodford+assessment+unit&format=json&max=10"},"items":[]}`

## OCC: Imaging / Public Records
- URL: `https://imaging.occ.ok.gov/imaging/og.aspx`
- Method: GET
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``

## OCC: Pollution remediation data
- URL: `https://oklahoma.gov/occ/divisions/oil-gas/oil-gas-data/oil-gas-data-files.html`
- Method: GET
- Status: **HTTPError 404** | CT: `` | CL: ``
- Preview: ``
