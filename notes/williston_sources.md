# Williston: data sources & methodology

## Geographic scope — basin-clipped, not state-clipped

Basin 03 departs from the Kansas (1 state) and Permian (2 states, county
union) pattern. The Williston Basin is a structural basin that crosses
three US states and one Canadian province, and it is geologically
defined by a basin margin, not a political boundary. Clipping to a
polygon matters for the story:

  > The Bakken-Three Forks petroleum system does not care where North
  > Dakota ends and Montana begins.

**Basin polygon**: USGS Bakken-Three Forks Total Petroleum System (TPS)
boundary, from the 2013 National Assessment of Undiscovered Oil and Gas
Resources of the Bakken and Three Forks Formations.

  - ScienceBase item: https://www.sciencebase.gov/catalog/item/5a8a6aade4b00f54eb19d0fa
  - Published as shapefile + GeoJSON; public, re-distributable.
  - This is the standard polygon operators and USGS use for Bakken
    resource accounting.

Wells outside the TPS but inside the structural Williston Basin
(Lodgepole, Mission Canyon, Madison plays) would be excluded by this
choice. Call that out explicitly on the StoryMap: "We show the
Bakken-Three Forks system, which is the capital-intensive slice of the
Williston."

## Jurisdictional scope — US only for v1

The Williston Basin crosses:
  - **North Dakota** (~55% of basin area, ~90% of current production)
  - **Montana** (eastern Montana: Richland, Roosevelt, Sheridan,
    McCone, Dawson, Wibaux counties — Elm Coulee field is the MT piece)
  - **South Dakota** (Harding + Butte counties — tiny sliver, <500
    wells)
  - **Saskatchewan** (Estevan, Stoughton, Weyburn area — meaningful
    well population, different regulatory regime)

**Decision**: ship v1 as US-only (ND + MT). Justification:
  1. ND alone is the story. 90%+ of basin production, the Bakken
     horizontal campaign lived here.
  2. MT adds the Elm Coulee chapter (the 2000s vertical-Bakken proof of
     concept) and the state-line gradient we need for the "basin
     doesn't care about borders" beat.
  3. SD is too small to carry a narrative step.
  4. SK is interesting but adds: foreign data portal, different schema,
     different "lit" proxy, and CAD-vs-USD / hectares-vs-acres mismatch
     on every chart. Holds v1 publication.

Flag SK explicitly in the methodology strip: "Canadian portion
(Saskatchewan) excluded from this cut. A future addendum may extend
the clip northward."

## Data sources

### North Dakota: NDIC Oil & Gas Division

ND publishes two parallel well lists:
  - **NDIC GIS Server**: shapefile + ArcGIS REST, includes coords,
    spud date, operator, well status, file number.
    - Home: https://www.dmr.nd.gov/dmr/oilgas/gis
    - ArcGIS REST (candidate): https://gis.dmr.nd.gov/arcgis/rest/services/
  - **NDIC Basic Search**: per-well scout ticket, well history, scanned
    files (log, completion report, production history).
    - Home: https://www.dmr.nd.gov/oilgas/bscfr/FindWell.asp
    - Per-well detail: file-number keyed.

ND "lit" proxy: NDIC hosts a **digital well file archive**. Every
drilled well has a file number; most have at least a scout ticket
scanned. The honest "lit" proxy is: **well file contains a scanned log
(well log, sundry, form 6)**. This can be derived from the Basic Search
page or from the NDIC data delivery service.

NDIC also publishes a **monthly production file** (bulk download,
confidential well data redacted) which gives us producers-vs-idle but
not logs. That is a different axis.

Operator / status fields: in the GIS layer attribute table.

### Montana: Montana Board of Oil and Gas Conservation (BOGC)

MT has one endpoint:
  - **BOGC online database**: https://bogc.dnrc.mt.gov/WebApps/DataMiner/
    Downloads are CSV by county + shapefile by county.
  - **GIS viewer**: https://bogc.dnrc.mt.gov/WebApps/DataMiner/Maps.aspx
  - Schema: API14, operator, field, well status, spud date, coords.

MT "lit" proxy: BOGC has a **scanned well file system** accessible via
the DataMiner per-well detail page. Similar to NDIC. Proxy: well file
contains a log scan.

### USGS Bakken-Three Forks TPS polygon

  - Direct download candidates:
    - ScienceBase parent: https://www.sciencebase.gov/catalog/item/5a8a6aade4b00f54eb19d0fa
    - USGS 2013 National Assessment assessment-unit boundaries:
      https://www.sciencebase.gov/catalog/item/56cb6dfce4b0849ccc3cc3c8

  - Fallback: USGS Mineral Resources Online Spatial Data (MRDS):
    https://mrdata.usgs.gov/assessment/

Need to confirm the exact ScienceBase item in phase 0.

## Lit vs. dark proxy (asymmetric, documented)

Matching the Permian pattern of asymmetric proxies per jurisdiction:

  - **ND**: dark = 1 if NDIC well file does **not** contain a scanned
    log document (well log, e-log, or sundry with log attachment).
    Sourced from the Basic Search scrape or NDIC data-delivery index.
  - **MT**: dark = 1 if BOGC well file does **not** contain a scanned
    log document. Sourced from the DataMiner per-well page scrape.

For both: vintage bucket `v` from spud year, same 6-bucket schema as
Kansas/Permian (0 pre-1980, 1 1980s, 2 1990s, 3 2000s, 4 2010+, 5
unknown). State flag `s` = 0 ND, 1 MT.

## Outputs (match Kansas/Permian schema)

```
darkdata/williston/data/wells.csv            # lat,lon,d,v,s(tate)
darkdata/williston/data/williston_basin.json # USGS TPS polygon
darkdata/williston/data/williston_counties.json  # county ref for tooltips
darkdata/williston/data/summary.json
```

## The tell

Kansas: *where is the data missing?* → 94% dark, orphan-heavy, shallow old plays.

Permian: *is the biggest producing basin in North America still mostly dark?*
→ 78% dark. Post-2010 horizontal campaign is mostly lit; pre-boom legacy is not.

Williston (hypothesis to test): *does the Bakken horizontal campaign
buy a lit basin, or did the pre-2007 legacy leave most of the rock
record dark?* Betting the post-2007 Bakken is lit (operators log
horizontals aggressively for completion design) but the pre-2000 MT
legacy + ND shallow producers drag the basin-wide dark share to ~60%.

## Known risks & constraints

1. **NDIC Basic Search is ASPX-stateful**: session tokens, VIEWSTATE.
   Cannot be scraped with plain requests; need headless browser or
   discovered REST alternative. Check for a CSV export or data service.
2. **BOGC DataMiner CSV export**: should be straightforward per-county
   download, but per-well file metadata may require the detail page.
3. **Basin clip must happen in equal-area projection**: both states
   pre-project wells to EPSG:5070 for the spatial join, then reproject
   the final filtered set to WGS84 for the browser.
4. **Coord completeness**: some ND legacy wells have only PLSS
   footages, not lat/lon. Need to exclude those (document the
   exclusion) or transform the footages. Permian treated this with a
   "~% of reporters without coordinates excluded from view" footnote.
5. **Data volume**: ND ~18K Bakken + ~17K conventional = ~35K wells.
   MT ~5K Williston-clipped. Manageable.

## Phase plan (mirrors Permian 0-3 pattern)

  - `phase0_source_probe.py`: probe NDIC GIS REST, MT BOGC DataMiner,
    ScienceBase TPS item. Writes `notes/williston_probe.md`.
  - `phase1_nd_pull.py`: pull NDIC GIS well layer → cache raw CSV.
  - `phase2_mt_pull.py`: pull MT BOGC per-county well CSV → cache raw.
  - `phase3_story_data.py`: (a) load USGS TPS polygon; (b) clip
    ND+MT wells to polygon in EPSG:5070; (c) classify dark/light per
    state; (d) emit `wells.csv`, `williston_basin.json`,
    `williston_counties.json`, `summary.json`.

Phase 3 also renders the four static figures that back the StoryMap
scroll steps (basin-extent map, vintage-split map, state-line gradient,
operator concentration).
