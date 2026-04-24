# Substack Launch: The Dark Data Map, Kansas

**Purpose**: Deeper companion to the LinkedIn post. Tells the operator/investor/policy audience what the map means and why it repeats across every basin.

**Status**: DRAFT. Tee to review before posting.

**Suggested title**: *Where Kansas oil data lives*
**Suggested subtitle**: *Walking the 94% dark*

**Figure order**:
1. Hero map (`kansas_dark_data_map.png`): includes vintage curve companion, so one image carries both spatial and temporal story.
2. Southeast Kansas close-up (`kansas_cherokee_closeup.png`): the 11-county Cherokee Group CBM play region, 81K drilled / 4.3K lit (5.3%), with an operator-concentration callout (River Rock owns 37% of the region's public log archive).

---

## Post body

The subsurface industry has an open secret: most of its own data is dark. Industry estimates put the share of subsurface data that is never analyzed beyond first acquisition at something like 99.5%. That number is true and useless: too abstract to act on.

Here's what it looks like when you put it on a real map of a real state.

*[HERO: kansas_dark_data_map.png]*

Kansas has 419,777 wells on the Kansas Geological Survey master list that were actually drilled: not just permitted, not cancelled. Of those, 23,897 (5.7%) have a publicly-accessible digitized log file. The LAS format. The one an analyst can actually load.

94.3% of Kansas's oil and gas history is dark.

## Why Kansas first

Because it's the cleanest public data pipeline in the United States. The Kansas Geological Survey publishes two things openly: a master well list (515K records, deduping to 477K unique wells), and a bulk archive of LAS files. Most states make you scrape per-county case-file PDFs. Kansas is a ten-minute download. That's why it's the proof-of-concept: cheap to execute, fast feedback, teaches the pipeline before we attack messier states.

## Dark is a time problem, not a scanning problem

The interesting fact isn't that 94% is dark. It's *when* the dark is.

The bar chart in the hero panel tells the story. Every decade from the 1920s through the 1990s sits at 1–3% LAS coverage. The 2000s jumps to 14%. The 2010s clears 37%. The 2020s dips back to 20%: that's reporting lag, not regression. Recent wells haven't been filed and scanned yet.

Pre-2000 Kansas averaged roughly 30,000 drilled wells per decade at about 2% coverage. That's north of 200,000 wells where no digitized log was ever produced: or if one was, it's sitting inside a company that doesn't exist anymore. The paper moved through M&A, warehouse fires, and retirements.

The east-west gradient you see on the map is the same story in space. Eastern Kansas is the old oil patch: Johnson, Miami, Franklin counties were being drilled in the 1920s and 1930s. Johnson County: 0.2% LAS coverage across 4,171 wells. Western Kansas is late-arrival drilling: Wichita County's 447 wells are 43% digitized because the drilling happened after digital was the default. Same state, two centuries of operator behavior.

Dark data in Kansas is a stratigraphy of time.

## The Cherokee close-up

Zoom into the red cluster in the southeast corner of the hero map and you get a second story. It's the Cherokee Group play: eleven counties covering the Pennsylvanian-age coalbed-methane fairway where the 2000s drilling boom concentrated.

*[FIGURE: kansas_cherokee_closeup.png]*

81,293 drilled wells across the region. 4,316 with a public LAS (5.3%). Slightly worse coverage than the state average, but the interesting detail isn't the rate: it's the ownership. **One operator, River Rock Operating LLC (successor to the Quest Cherokee CBM estate), accounts for 1,582 of the region's 4,316 publicly-accessible LAS files. 37% of the log archive for an eleven-county region belongs to a single company's historical drilling program.**

That's consolidation showing up in the data layer. When one operator owns most of the region's logging effort, the regional "public" archive effectively becomes that operator's archive by default. If the operator exits the play, the archive's fate rides with them.

Note also how geographically concentrated the lit wells are even within the CBM region: Neosho and Wilson counties carry most of the color. The other eight counties stayed mostly dark through the boom.

## Why this matters

**For operators.** Every dark offset well is pre-drill intelligence nobody extracted. A 1950 dry hole in the next section tells you what's in your rock: if anyone digitized it. If no one did, you're paying to re-learn something that's already been learned and then lost.

**For investors and basin analysts.** The first party to digitize a regional log archive has an information monopoly. Consolidation stories run on data. In brownfield M&A, the dark-data gap is the fog of war: the buyer who solves it sees the asset differently than the buyer who doesn't.

**For policy and climate work.** Orphan well remediation, groundwater contamination attribution, methane-leak source identification, carbon sequestration site selection: all of these require decades of old logs that don't exist in machine-readable form. You cannot remediate what you cannot locate.

## Next

Kansas is the easy state. Texas and New Mexico (the Permian) is where the money is, and where the dark-data picture is almost certainly worst. The Railroad Commission does not maintain a public LAS archive at the Kansas level of openness; neither does the New Mexico OCD. The next post walks the Permian with whatever we can assemble.

After that, six more basins (Appalachian, Anadarko, Gulf Coast, Williston, Arkla), same lens, stacked against the ownership map I already published last week. Dark data and ownership concentration are the same story told from two sides. Who owns the wells, and what you can see inside them.

---

*Data + code: [repo link]. Sources: Kansas Geological Survey master well list and LAS archive; Census 2010 county boundaries for the cartography.*

---

**Word count**: ~820 (substack target 400–800 range, trim if it runs long in preview).

**Tone/voice checks**:
- No marketing gloss ("leverage", "seamless", etc.)
- Names the tension directly (dark is a time problem)
- Critique-first opener (the 99.5% stat is "true and useless")
- Sharp-colleague register throughout
- Threads to prior GHGRP series in the "Next" section (same basin set, different lens)
