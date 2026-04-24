# Permian: data sources & methodology

## Geographic scope

**Permian Basin**: treating this as the union of USGS Permian Basin Province (province code 5044) and the standard operator-defined counties. Two states, ~40 counties.

**TX Permian counties** (27): Andrews, Borden, Crane, Crockett, Culberson, Dawson, Ector, Gaines, Glasscock, Hockley, Howard, Irion, Jeff Davis, Kent, Loving, Lynn, Martin, Midland, Pecos, Reagan, Reeves, Scurry, Sterling, Terry, Upton, Ward, Winkler, Yoakum.

**NM Permian counties** (4): Lea, Eddy, Chaves, Roosevelt.

Decision to confirm: basin boundary vs. county union. I'm defaulting to the county union: simpler, defensible, easier for a reader to audit. ("These are the Permian counties" is less contested than "this is the basin outline.")

## Data sources

### Texas: Railroad Commission (TX RRC)

Master drilled-well list: **resolved endpoints**

Two valid paths. Prefer (1) for bulk, (2) for iterative discovery.

1. **Statewide API ASCII dump** (RRC Managed File Transfer):
   - https://mft.rrc.texas.gov/link/701db9a3-32b5-488d-812b-cd6ff7d0fe85 (ASCII)
   - https://mft.rrc.texas.gov/link/1eb94d66-461d-4114-93f7-b4bc04a70674 (dBase)
   - Refreshed twice weekly. Fields: API, survey name, well number, lease name/ID, completion date, plug date.
   - **No coordinates** in this file → must join against the shapefile for lat/lon.

2. **Per-county well shapefile bundles** (MFT):
   - https://mft.rrc.texas.gov/link/d551fb20-442e-4b67-84fa-ac3f23ecabb4
   - Contains surface wells, bottom wells, bottom-well-lines as .shp per county.
   - **Point-and-click portal**: not a stable URL pattern. Manual download step.

3. **ArcGIS REST (Harris County Public ID hosting of RRC layers)**:
   - Base: `https://www.gis.hctx.net/arcgishcpid/rest/services/TXRRC/Wells/MapServer`
   - Layer 0 = Surface Wells (Point, 2000 max records per query, supports SQL where clause)
   - Fields: `API` (8 chars: county code prefix + well ID), `SYMNUM`, `RELIAB`, `LAT27`/`LONG27`, `LAT83`/`LONG83`, `WELLID`
   - No County name field: must filter by API prefix.
   - **This is the live-query option.** Paginate with `resultOffset` + `resultRecordCount=2000`.

**Operator / status / spud date** are NOT on the shapefile or ArcGIS layer: only in the ASCII dump. Plan: pull (3) for geometry, join to (1) for attributes.

Log / "lit" universe: **resolved**

RRC publishes a **monthly well-log inventory** as Excel (compressed), 2006–present:
- Catalog page: https://www.rrc.texas.gov/oil-and-gas/research-and-statistics/obtaining-commission-records/oil-gas-well-records-gis-well-logs/
- ~240 monthly files; each lists wells whose scanned logs were newly added to RRC's imaged-well-log system that month.
- Union + dedupe by API = the "lit" universe for TX.

**Caveats that must go on the methodology strip:**
1. This inventory only covers logs *added to the electronic system since 2006*. Pre-2006 scans may not appear: true TX "lit" count is a lower bound.
2. "Lit" in TX = **scanned TIFF exists in RRC's imaged log system**. "Lit" in KS = **digitized LAS exists in KGS WebDocs**. Different operational floors. The series treats both as "lit" with the note that LAS is a stricter standard; a well is "lit" at either level if a reader could recover its log from the public record without paying.
3. Commercial proxies (TGS / IHS / Enverus) are off-limits: we don't have access and wouldn't publish from private sources.

Operator-of-record
- RRC W-1 well permit database has current operator.
- Orphan equivalent: wells with status = P-5 inactive / no currently-bonded operator. TX's "orphan" definition is the RRC State Managed Orphan Well Program.

### New Mexico: Oil Conservation Division (NM OCD)

Master drilled-well list
- **Primary**: OCD well database → https://wwwapps.emnrd.nm.gov/ocd/ocdpermitting/Data/Wells/Wells.aspx
- Bulk CSV exports available per county.
- OCD GIS: https://wwwapps.emnrd.nm.gov/ocd/ocdpermitting/Reporting/GIS/GIS.aspx
- Schema: API, operator, county, spud date, well status, surface coords.

Log / "lit" universe
- OCD hosts a **digital log archive**: logs filed electronically since ~2002 are available. Pre-2002 generally scanned-only.
- This is the closest NM equivalent to KGS's LAS archive. Use it as-is; note the 2002-ish floor.

Operator-of-record
- OCD database has current operator.
- Orphan wells: OCD maintains an orphan well list (public).

## Scope of the "dark" count

Same as Kansas:
- Include drilled wells only (exclude permits that never spudded, cancelled APIs).
- Include all statuses: producing, plugged, shut-in, abandoned.
- Exclude injection/disposal wells? **Decision**: include them. They still have logged hole. Noted in methodology strip.

## Vintage buckets: keep identical to Kansas

```
0 pre-1980   1 1980s   2 1990s   3 2000s   4 2010+   5 unknown
```

Kansas's peak was the 2000s+ CBM boom. Permian's peak is the 2010s horizontal campaign. Same buckets, different shape: that's the point of a series.

## The tell

Kansas: *where is the data missing?* → 94% dark, orphan-heavy, shallow old plays.

Permian (hypothesis to test): *is the biggest producing basin in North America still mostly dark?* Betting yes on the full universe, no on post-2010.

## Known risks & constraints

1. **TX data volume**: Permian counties alone probably hold 500K+ drilled wells. Must pre-filter by county before downloading.
2. **Log universe definition asymmetry** (TX vs. KS vs. NM): must be documented honestly on the page.
3. **Scraping RRC log search**: likely slow, rate-limited, possibly requires user-agent rotation. Budget several hours of crawl time at minimum.
4. **OCD's ASP.NET forms**: older state portals often have viewstate tokens that make static fetch break. May need headless browser for bulk.

## Outputs (match Kansas schema)

Target final shape for the browser:
```
darkdata/permian/data/wells.csv          # lat,lon,d,v,s(tate)
darkdata/permian/data/permian_counties.json
darkdata/permian/data/summary.json
```

Adding `s` to the wells schema (0=TX, 1=NM) lets the StoryMap highlight the state line on scroll.
