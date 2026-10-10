# GSC Performance export — mistertranslation.com — pulled 2026-10-10

Source: Search Console → Performance → Export → Download CSV (web search, last 3 months, data through **2026-10-06**,
"last update 36.5 hours ago"). Files: `Chart.csv` (daily), `Queries.csv` (top 1,000), `Pages.csv` (top 1,000),
`Countries.csv`, `Devices.csv`. Analysed with `tools/gsc_cliff.py ... --split 2026-08-15` plus a window breakdown.

## Headline

| Window | Days | Clicks | Impressions | Median daily position |
|---|---|---|---|---|
| to 08-14 (before the collapse) | 22 | 13 | 7,417 | 56.8 (weighted) |
| 08-15 → 08-31 | 17 | 0 | 340 | 60.3 |
| 09-01 → 09-15 | 15 | 0 | 42 | 7.2 |
| 09-16 → 09-30 | 15 | 0 | 40 | 5.4 |
| 10-01 → 10-06 | 6 | 0 | 8 | 4.8 |

- **No new movement.** Impressions have sat at ~1–3 a day since mid-September. No clicks since 2026-08-02 (13 total, all in the
  first 22 days). The 08-15 collapse is confirmed again as an impressions-mix event, not a ranking penalty (position held or improved).
- **The surviving impressions are a different, tiny population:** ~84 impressions from 49 queries at position ≤ 10, almost all
  Hebrew/Greek word lookups that match `/dict/` entries (chamad, machah, syzygos, biblaridion meaning, alluf, yarad, damim).
  Example: "chamad" 7 impressions at position 7.6. Sample is far too small to act on, but it is real long-tail demand where
  we already rank top-10 with the thin pages. (The `/dict/` stubs have been `noindex` since 2026-09-17, so Google is still
  serving some until it recrawls them.)
- Queries with clicks, ever, in this window: "adonijah in the bible" (1), "chara greek" (1), "imagen en griego" (1).
- Pages.csv top entries are almost all the old stub pages (`/dict/eunouchos.es.html` 188 impr at pos 76, `/atlas/horeb`, `/ency/goshen`,
  etc.) and are from the pre-collapse flood. The home page `/` has 55 impressions at position 11.
- Off-topic noise: "cactus ya ya reviews" (24 impressions, pos 11) is not ours to chase.
- Countries (impressions): United States 3,240, United Kingdom 351, Vietnam 176, Turkey 142, Argentina 74, Venezuela 46.

## The 2026-10-10 checkpoint

The Page indexing report is **still "Last update: 10/3/26"**: 414 indexed / 2,178 not indexed (1,838 Crawled – currently not
indexed, 44 noindex, 292 Discovered – not indexed), identical to the 10-07 read. So the falsifiable test cannot be read yet;
re-export Pages once the report's "Last update" date moves past 10/3. Do not conclude anything from this snapshot.

## Next
- Re-pull Page indexing when its Last update date advances (expect it to lag ~7 days).
- Keep Performance exports monthly; the `Chart.csv` floor (~1–3 impressions/day) is the number to beat.
