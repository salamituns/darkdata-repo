# Eagle Ford strategy decision

## What we tried

| Path | Status | Verdict |
|---|---|---|
| TX RRC `gis2.rrc.texas.gov/arcgis/rest/...` | Network unreachable from this network | Dead |
| TX RRC `gis.rrc.texas.gov/arcgis/rest/...` | 404 on every REST path | Dead |
| TX RRC GIS Viewer scrape | JSF/PrimeFaces session app | Hostile |
| TX RRC MFT bulk-data portal | 200+ download links, each one a JSF wrapper page with 5-min session timeout | Hostile (would need Selenium/Playwright + JSF state replay) |
| HIFLD national oil/gas wells layer | `Token Required` from `services.arcgis.com/jIL9msH9OI208GCb` | Auth-walled |
| HIFLD `services1.arcgis.com/Hp6G80Pky0om7QvQ` | "Item does not exist" | Dead |
| HIFLD opendata.arcgis.com bulk ZIP | HTTP 403 | Dead |
| TX Open Data Portal `data.texas.gov` | No oil/gas well datasets in catalog | Dead |
| TX Bureau of Economic Geology | No public well shapefile | Dead |
| USGS `mrdata.usgs.gov/oilgas/` | HTTP 404 | Dead |
| USGS Eagle Ford AU ScienceBase item | `EagleFordAUs.geojson` (3.3 MB) - polygon only, no wells | **Useful** |
| EIA Drilling Productivity Report `dpr-data.xlsx` | 160 KB monthly, region aggregate | **Useful** |

## What we CAN'T ship for Eagle Ford

- Per-well lat/lon
- Per-well lit/dark classification
- Per-well vintage
- Operator-level dark inventory chart

## What we CAN ship

- USGS Eagle Ford Group AU polygon (the basin clip)
- TIGER county boundaries for the 30 South Texas Eagle Ford counties
- EIA DPR monthly Eagle Ford production / rig count / new-well count time series
- A **regulatory data-accessibility ranking** across the 5 cooperative basins +
  the 1 hostile regulator
- A storymap that frames TX RRC's data architecture as the dark-data verdict
  itself, not the absence of one

## The framing

This is the series capstone. The other five basins demonstrated WHAT dark data
looks like at varying levels (Williston 46% to Appalachia 95%). Eagle Ford
demonstrates the SOURCE: a regulator's data architecture choices ARE its
dark-data posture, irrespective of the geology and irrespective of the
operators. TX RRC's JSF/PrimeFaces session-based portal and EBCDIC mainframe
dumps are not bugs in an otherwise-modern data stack. They ARE the stack.
That choice is the dark-data outcome.

The Eagle Ford bundle ships with NO `wells.csv`. That absence IS the data.

## Bundle plan

```
darkdata/eagle_ford/
  data/
    eagle_ford_aus.json         USGS Eagle Ford Group AU polygons (in hand)
    eagle_ford_counties.json    Texas counties intersecting the AU
    state_outline.json          Texas
    regulatory_comparison.json  5 basin pulls compared
    eia_eagle_ford_monthly.json EIA DPR Eagle Ford time series
    summary.json                meta-summary, NO total_wells field
  figures/
    eagle_ford_basin_map.png    AU polygon + counties + Texas, no wells
    regulatory_accessibility.png horizontal bar chart, 6 regulators
    eia_production_curve.png    Eagle Ford 2007-2025 production / rig count
    architecture_comparison.png screen captures + commentary on each portal
  story.html                    16 scroll steps
```
