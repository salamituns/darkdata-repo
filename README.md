# darkdata-repo

Pipeline and figure code for the "Where US Oil Data Lives" series at
[salamituns.github.io/darkdata](https://salamituns.github.io/darkdata/).
A basin-by-basin walk through what the US subsurface industry can
actually see of its own history. Built by
[Olatunde Salami](https://linkedin.com/in/salamituns).

## Status

| # | Basin | Wells | Dark | Published |
|---|---|---:|---:|---|
| 01 | Kansas | 419,777 | 94.3% | [story](https://salamituns.github.io/darkdata/kansas/) |
| 02 | Permian (TX + NM) | 393,073 | 77.9% | [story](https://salamituns.github.io/darkdata/permian/story.html) |
| 03 | Williston / Bakken | | | queued |
| 04 | Denver-Julesburg | | | queued |
| 05 | Appalachia | | | queued |
| 06 | San Juan | | | queued |

Two basins live, 812,850 drilled wells catalogued, 86.4% classified dark
by the basin-appropriate public-data proxy.

## What is "dark" here

A well is "dark" if a determined analyst cannot pull its log record
from a public regulator archive without paying a commercial data
vendor. The exact proxy is basin-specific because the regulators file
asymmetrically:

- **Kansas**: dark = no LAS file in the KGS WebDocs bulk archive.
- **Permian (TX)**: dark = no scanned well-log TIFF listed in RRC
  Layer 8 (`RRC_Public_Viewer_Srvs` MapServer).
- **Permian (NM)**: dark = `year_spudded < 2002`. NM has no separate
  log-inventory layer; OCD treats 2002 as the digital-filing-era
  floor.

Every StoryMap is explicit about its proxy and its limits.

## Layout

```
scripts/
  phase1_kgs_scan.py                  Kansas: parse LAS inventory
  phase2_kgs_merge.py                 Kansas: join master list + LAS
  phase3_kansas_map.py                Kansas: Fig 01 hero map
  phase4_kansas_cherokee.py           Kansas: Fig 02 close-up
  phase5_operators.py                 Kansas: Fig 03 operator bars
  phase6_county_choropleth.py         Kansas: Fig 04 county view
  phase7_story_data.py                Kansas: wells.csv for the scrolly
  permian/
    phase0_source_probe.py            Permian: sanity-check RRC/OCD endpoints
    phase1_tx_rrc_pull.py             Permian: pull TX wells + logs + orphans
    phase2_nm_ocd_pull.py             Permian: pull NM OCD wells (Lea, Eddy, Chaves, Roosevelt)
    phase3_story_data.py              Permian: build wells.csv + counties.json + summary.json

data/
  raw/                                (gitignored, reproducible)
    kgs/                              KGS master list + LAS inventory
    tx_rrc/                           Texas RRC Layer 0/2/8 pulls
    nm_ocd/                           New Mexico OCD MapServer/0 pulls
  processed/
    phase1_kgs_summary.json           headline numbers, vintage distribution
    phase1_kgs_wells.csv              Kansas: well-level lit/dark table
    phase2_coverage_summary.json      Kansas: merged-coverage stats
    phase2_kgs_master_with_las.csv    (gitignored, regeneratable)

figures/                              PNG outputs for the long-form posts
notes/                                methodology + headline-number derivation
posts/                                LinkedIn + Substack launch drafts
```

## Reproducing the data

The scripts pull directly from live regulator endpoints. No API keys
needed. Total pull time: about 20 minutes on a home connection.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install pandas geopandas shapely requests

# Kansas (KGS bulk archive)
python3 scripts/phase1_kgs_scan.py
python3 scripts/phase2_kgs_merge.py

# Permian (TX RRC + NM OCD)
python3 scripts/permian/phase0_source_probe.py
python3 scripts/permian/phase1_tx_rrc_pull.py
python3 scripts/permian/phase2_nm_ocd_pull.py
python3 scripts/permian/phase3_story_data.py
```

Each script writes its output path to stderr and emits a
`pull_metadata.json` alongside the data for provenance.

## Methodology notes

- [`notes/headline_numbers.md`](notes/headline_numbers.md): Kansas
  dedupe, LAS match rate, orphan definition.
- [`notes/permian_probe.md`](notes/permian_probe.md): Why TX and NM
  required different lit/dark proxies.
- [`notes/permian_sources.md`](notes/permian_sources.md): Regulator
  endpoint catalogue, rate limits, field semantics.

## Attribution

Analysis: [@salamituns](https://linkedin.com/in/salamituns).
Source data per file: KGS, Texas RRC, New Mexico OCD. Pulled via each
regulator's public ArcGIS REST or bulk archive; no paywalled feeds.

If you work any side of this (operator, acquirer, underwriter,
regulator, policy team), or want to fund a basin,
[LinkedIn](https://linkedin.com/in/salamituns) is the fastest way to
reach me.
