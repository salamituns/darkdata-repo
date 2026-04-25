# darkdata-repo

Pipeline and figure code for **Where US Oil Data Lives**, a six-basin
walk through what the US subsurface industry can actually see of its
own history.

Live: [salamituns.github.io/darkdata](https://salamituns.github.io/darkdata/) ·
Primer: [salamituns.github.io/darkdata/basins.html](https://salamituns.github.io/darkdata/basins.html)

Built by [Olatunde Salami](https://linkedin.com/in/salamituns).

## Status — series complete

Six basins shipped. **1,921,013 wells mapped.** **89.1 percent dark
measured** across the five basins where the regulator publishes per-well
data. One basin (Eagle Ford) is unmeasured because TX RRC's data
architecture does not let an outside analyst pull it.

| # | Basin | States | Wells | Dark | Walk |
|---|---|---|---:|---:|---|
| 01 | Kansas | KS | 419,777 | 94.3% | [walk](https://salamituns.github.io/darkdata/kansas/) |
| 02 | Permian | TX + NM | 393,073 | 77.9% | [walk](https://salamituns.github.io/darkdata/permian/story.html) |
| 03 | Williston | ND + MT | 45,921 | 45.7% | [walk](https://salamituns.github.io/darkdata/williston/story.html) |
| 04 | Anadarko | OK + KS | 482,918 | 91.1% | [walk](https://salamituns.github.io/darkdata/anadarko/story.html) |
| 05 | Appalachia | PA + WV + OH | 579,324 | 94.8% | [walk](https://salamituns.github.io/darkdata/appalachia/story.html) |
| 06 | Eagle Ford | TX | unmeasured | — | [walk](https://salamituns.github.io/darkdata/eagle_ford/story.html) |

## The two theses

The series writes one falsifiable claim and one structural one.

**1. Horizontal eras only rescue young basins.** Williston is the only
basin where horizontals dominate the well count, and it is the only
basin in the lit majority (46 percent dark). Anadarko, Appalachia, and
Kansas all sit above 90 percent dark because their pre-2008 vertical
legacy overwhelms the modern era. The cross-basin matrix figure in
[`figures/primer_cross_basin_matrix.png`](figures/primer_cross_basin_matrix.png)
plots dark percentage against horizontal-era share of well count and
shows the relationship is monotonic.

**2. Dark data is also a regulator publishing choice.** Five regulators
chose to ship per-well data as direct shapefiles, CSVs, or REST
endpoints. One (TX RRC) chose JSF/PrimeFaces session-state portals
backed by EBCDIC mainframe dumps. The first five let us measure dark
percentage at varying levels (46 to 95 percent). The sixth lets us
prove that the dark-data problem is not a technology gap or an
operator failure — it is the regulator's published posture. The Eagle
Ford walk ships **without a wells.csv on purpose** to make this point
visible.

## What "dark" means per basin

A well is dark if a determined analyst cannot pull its log record
from a public regulator archive without paying a commercial data
vendor. The exact proxy is basin-specific because every regulator
files asymmetrically. Each basin walk states its proxy in step 5 of
its scrollytelling story.

| Basin | Lit definition | Dark = otherwise |
|---|---|---|
| Kansas | API in KGS public LAS archive | no LAS in KGS bulk archive |
| Permian (TX) | RRC well-log TIFF listed in Layer 8 | no scanned log TIFF |
| Permian (NM) | spud year ≥ 2002 (NM OCD digital-filing floor) | spudded before 2002 |
| Williston (ND) | spud year ≥ 2000 OR horizontal flag in OGD_Horizontals | older + no horizontal record |
| Williston (MT) | completion year ≥ 2000 (no horizontal flag available) | older completion |
| Anadarko (OK) | OCC RBDMS Open_Hole_Logs = Yes OR Drill_Type = horizontal | otherwise |
| Anadarko (KS) | API in KGS public LAS archive (basin 01 logic reused) | otherwise |
| Appalachia (PA) | UNCONVENTI = Y OR WELL_CONFI contains "Horizontal" | otherwise (incl. historic WPA) |
| Appalachia (WV) | (none — see note) | 100% dark by data architecture |
| Appalachia (OH) | SLANT = H OR Marcellus_Shale / Utica_Shale flag set | otherwise |
| Eagle Ford | (cannot measure) | 100% unmeasured by data architecture |

WV is a special case: its 2016 well-location file uses a 6-digit
`PERMIT_ID`, its 2024 H6A horizontal-production roll uses 10-digit
APIs, and the two do not link without a cross-reference table the WV
DEP does not publish. We therefore count WV at 100 percent dark by
data architecture rather than by paper records.

## Reproducing the data

The scripts pull directly from live regulator endpoints. No API keys
needed. Total pull time: ~30 minutes on a home connection (the OH
DOG_Services REST query paginates 242,035 wells which dominates).

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install pandas geopandas shapely requests openpyxl matplotlib pyproj

# Per-basin pipelines (each basin is independent)
python3 scripts/phase1_kgs_scan.py             # KS
python3 scripts/phase2_kgs_merge.py            # KS

python3 scripts/permian/phase0_source_probe.py # Permian
python3 scripts/permian/phase1_tx_rrc_pull.py
python3 scripts/permian/phase2_nm_ocd_pull.py
python3 scripts/permian/phase3_story_data.py

python3 scripts/williston/phase1_download.py   # Williston
python3 scripts/williston/phase2_story_data.py
python3 scripts/williston/phase3_figures.py

python3 scripts/anadarko/phase1_download.py    # Anadarko
python3 scripts/anadarko/phase2_story_data.py
python3 scripts/anadarko/phase3_figures.py

python3 scripts/appalachia/phase1_download.py  # Appalachia
python3 scripts/appalachia/phase2_story_data.py
python3 scripts/appalachia/phase3_figures.py

python3 scripts/eagle_ford/phase1_download.py  # Eagle Ford (no wells.csv)
python3 scripts/eagle_ford/phase2_story_data.py
python3 scripts/eagle_ford/phase3_figures.py

python3 scripts/primer/phase_a_bundle.py       # The cross-basin primer
python3 scripts/primer/phase_b_figures.py
python3 scripts/primer/phase_b_social_card.py
```

Each phase 0/1 script writes a `*_probe.md` to `notes/` documenting the
regulator endpoints it tried and what came back. Re-runs are idempotent
(every download skips if the target file already exists).

## Layout

```
scripts/
  phase1_kgs_scan.py            KS: parse LAS inventory
  phase2_kgs_merge.py           KS: join master list + LAS
  phase3_kansas_map.py          KS: hero map
  phase4_kansas_cherokee.py     KS: Cherokee close-up
  phase5_operators.py           KS: operator bars
  phase6_county_choropleth.py   KS: county view
  phase7_story_data.py          KS: wells.csv for the scrolly

  permian/                      Permian (TX RRC + NM OCD)
  williston/                    Williston (NDIC + MT BOGC + USGS TPS)
  anadarko/                     Anadarko (OCC RBDMS + KGS + USGS Province 058)
  appalachia/                   Appalachia (PA DEP + WV DEP + OH DOG + EIA shales)
  eagle_ford/                   Eagle Ford (USGS AUs + EIA DPR; ships no wells.csv)
  primer/                       Cross-basin field guide (basins.html data)

data/raw/                       (gitignored, reproducible)
data/processed/                 small per-basin summary JSON

figures/                        per-basin static PNG figures + primer figures
notes/                          methodology + per-basin probe results
```

## The primer

The series ships a reader's primer at
[/darkdata/basins.html](https://salamituns.github.io/darkdata/basins.html)
that fits all six basins on a single CONUS map with five view modes:

- **Dark %** — gradient by dark fraction
- **Geology** — palette by target rock era
- **Output** — palette by US oil rank (EIA DPR)
- **Era** — palette by horizontal-era start year
- **Access** — palette by data architecture tier (Open / Multi / Mixed / Walled)

Each mode also re-sorts the basin list, swaps the per-card metric
badge, and updates the legend strip. Click a basin to fly the camera
in and open a side panel with full geology + production facts. Built
on deck.gl (GeoJsonLayer + TextLayer) over a maplibre-gl basemap.

## Attribution

Analysis: [@salamituns](https://linkedin.com/in/salamituns). Source
data per file from KGS, Texas RRC, New Mexico OCD, NDIC, MT BOGC,
OK OCC, PA DEP via PASDA, WV DEP, OH DNR DOG, USGS ScienceBase, EIA
Drilling Productivity Report, EIA Tight Oil + Shale Plays Lower 48,
US Census TIGER 2024. Pulled via each regulator's public archive or
REST endpoint; no paywalled feeds.

If you work any side of this — operator, acquirer, underwriter,
regulator, policy team — or you want to fund a 7th basin,
[LinkedIn](https://linkedin.com/in/salamituns) is the fastest way to
reach me.
