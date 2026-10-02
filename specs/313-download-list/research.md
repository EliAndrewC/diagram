# Research - feature 313

## R1 - The seeded paywall states (plan D9a, spec FR-011)

Method (2026-10-02): a grep for paywall, subscription, institutional login, paid login and login wall over the list's
entries and over `research/sources/010-works-cited/*.html`. Each hit was read in its line and judged. Each confirmed one is
recorded with `make access-tags SET=paywalled`, dated 2026-10-02, and its reason quotes the line.

**Seeded, registry keys (9):** `kotobank-machibugyosho`, `kotobank-oimawashi`, `miles-2003`, `northampton-tannery-1996`,
`woods-westbrook-2006`, `tedori-fan-pwe`, `shixue-yuekan-louzeyuan`, `inexhaustible-treasuries` (list entry 272, keyless in
the list because it does not name its key), `skinner-marketing` (the 1964 article, from `skinner-2002-etudes-rurales`'s
write-up).

**Seeded, keyless list entries (13):** 32 (an institutional login), 113 (a paywalled chapter), and 158, 161, 163, 164, 168,
170, 178, 187, 189, 191 and 219 (each "Blocked by: paywalled.").

**Passed over:**

| hit | why not seeded |
|---|---|
| `yuan-liu-2009`, `ma-2017-fengshui-carbon` | the GM holds a full copy (`archived-gm-copy`); paywalled would hide it |
| `japanknowledge-jishibai` | "read in full ... while the site around it is subscription-gated": we read the page |
| `ma-2024-desire-paths`, `packer-2017-phragmites`, `jsslkx-002-2021` | each says the text is open |
| `lai-2003-daoism-today` | read on a library mirror; the GM holds a copy (entry 12) |
| `shirahata-jinja-tamagaki` | "raised by subscription" - a fund, not a paywall |
| entry 59 | "the subscription financing" - the subject, not the access |
| entry 60 | a whole class of works ("gazetteer collections are subscription databases or scans; no web search could be run") - nothing specific was found paywalled |
| entry 258 | HAL-SHS opens in a browser, so the copy is bot-refused, not paywalled |
| entry 304 | "403 or a login wall" over several pages, for a print monograph: not a confirmed paywall |
| H16's and H13's notes | the same works as `shixue-yuekan-louzeyuan` and `miles-2003`, seeded above |

## R2 - The access tags as they stand (SC-005)

Method: `make access-tags` on the clone, 2026-10-02, after the seeds. Counts over 2,126 registry keys and 248 keyless list
entries:

| state | count |
|---|---|
| open | 2,077 |
| gm-full | 24 |
| gm-partial | 0 |
| paywalled | 22 |
| bot-refused | 9 |
| down | 3 |
| gone | 2 |
| never-read | 237 |

Never-read is mostly the keyless entries: works asked for and never read. The rows archived `partial` because the page
"would not render whole" keep their served text and count as open. That is 22 rows (2026-10-02, a count of the manifest
by reason; the plan review re-counted it).
