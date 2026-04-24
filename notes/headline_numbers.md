# The Dark Data Map: Kansas phase 1 headline numbers

*Generated 2026-04-24 from KGS ArcGIS bulk export + KGS LAS archive*

## Denominators

| Bucket | Count |
|---|---:|
| Master list, all records | 515,495 |
| Unique wells (API_NUM_NODASH) | 476,869 |
| Paper / cancelled (Approved Intent, Expired Intent, Cancelled API) | 57,092 |
| **Drilled universe** | **419,777** |
| Drilled wells inside KS bbox with coords | 419,777 |
| Public-LAS wells (KGS WebDocs archive) | 23,955 |
| Public-LAS wells matching a master-list well | 23,897 (99.8%) |

## Headline

**5.7% of Kansas drilled wells have a publicly-accessible digitized log.**
**94.3% are dark.**

## Vintage curve (drilled wells by spud decade)

| Decade | Drilled | With LAS | Coverage |
|---|---:|---:|---:|
| 1910s | 352 | 3 | 0.9% |
| 1920s | 3,549 | 1 | 0.0% |
| 1930s | 10,803 | 50 | 0.5% |
| 1940s | 22,307 | 168 | 0.8% |
| 1950s | 42,869 | 632 | 1.5% |
| 1960s | 30,387 | 742 | 2.4% |
| 1970s | 33,886 | 974 | 2.9% |
| 1980s | 63,285 | 1,725 | 2.7% |
| 1990s | 23,747 | 739 | 3.1% |
| **2000s** | **30,542** | **4,390** | **14.4%** |
| **2010s** | **33,702** | **12,693** | **37.7%** |
| 2020s | 7,628 | 1,497 | 19.6%¹ |

¹ 2020s coverage depressed by reporting lag (recent wells not yet filed/scanned).

**Key inflection: 2000s → 2010s.** Pre-2000 Kansas averages 2% LAS coverage; the 2010s jump to 37.7%. Dark isn't a scanning backlog: it's a pre-digital stratigraphy.

## Geography

### Dark (by absolute count)
Barton, Montgomery, Ellis, Allen, Butler, Russell: each has 13–17K drilled wells at 1.6–7.5% coverage. These are the volume graveyards.

### Dark (by rate)
Johnson 0.2%, Jefferson 0.2%, Franklin 0.7%, Miami 0.9%, McPherson 1.0%. Eastern third of the state: old oil patch, pre-digital.

### Lit (by rate)
Wichita 43.4%, Logan 32.6%, Gray 28.5%, Scott 26.3%, Thomas 23.2%. Western third: late-arrival drilling, post-2000.

**The east/west divide IS a time divide.**

## Join key

`API_NUM_NODASH`: 10-digit numeric string. Cleaned of `.0` suffixes from float coercion. 100% of LAS-archive keys matched a master-list record.

## Sources

- Master list: `https://hub.arcgis.com/api/download/v1/items/514428df866b46c893b6834ff0bf303d/csv?redirect=true&layers=0`
- LAS inventory: `ks_las_files.txt` + `las65366.txt` (KGS WebDocs exports)
- Coordinates: NAD27 from KGS master list
- County boundaries: Census 2010 500k (latin-1 encoding required)

## Next candidate extensions

1. **Permian:** TX RRC + NM OCD. Messier (ad-hoc PDF archives, per-county scans), bigger prize (more recent, more valuable).
2. **County choropleth** as a companion: % dark by county, to make the east/west divide explicit beyond dot density.
3. **Vintage curve** as inset: 94% dark + "pre-2000 = 2%, post-2010 = 38%" side-by-side.
