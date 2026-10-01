# Feature 280, group F3 handoff (session 1: research and write, 2026-09-28)

- SECTION=fields/050
- SECTION=fields/610
- KEY=shinden-shuraku-kotobank
- KEY=ishizue-musashino
- KEY=ishizue-kojima
- KEY=yashio-kenchi
- KEY=komonjyo-kenchi
- KEY=maff-kodomo-kabuma

## Items

M06 MODERN-ONLY - fields/050 now says the 20-30 cm hill spacing is today's advice (the ministry's present-day answer: about 30 cm each way, 20-25 cm for short seedlings), that even spacing of any kind came in with the Meiji ruled rows, that no readable source gives a pre-Meiji hill spacing, and that a Ming manual (Ma Yilong's 農說) is reported at 7,200 to over 10,000 hills a mu (about 25-29 cm) but could not be read, so nothing rests on it - no change to what the generator draws: the Paddy surface mottle never drew a spacing (it is a declared SAMPLE, a drawing choice), so the comb and polder maps and the Millet, Buckwheat, Barley and Soy Entries that name 050 keep their mottle; only the prose claim changed; if the GM later wants a calibrated density, the 農說 figure (TO-DOWNLOAD 281, 282) is the premodern candidate - searched 2026-09-28: Japanese (農業全書, 会津農書, 株間, 尺, 寸, 乱雑植え; kotobank, MAFF history pages, Hasuda museum leaflet, Kubota), Chinese (農說, 沈氏農書, 補農書, 株距, 每亩 科; ctext access notice, guoxue and up18 and zhonghuadiancang timed out or refused, zh.wikisource 404), English (Ma Yilong Nongshuo density; the MPIWG Husemann chapter has nothing on spacing). GM ruling: the polder's denser sample (4.5 ft pitch) was the GM's knowing choice as a drawing sample, not a spacing; nothing ruled the 20-30 cm figure in.

M07 MIXED - new fields/610 says an Edo new-field village was laid out on a plan, its land behind each house in strips of equal area (Nipponica and Heibonsha on kotobank; Musashino's strips, dry field and woodland, running with the canals), but no readable page puts an Edo reclamation's paddies in a checkerboard (Ariake's diked stages say nothing of the inside; Kojo's Edo-reclaimed fields were subdivided and consolidated into blocks only before the war; the 1-tan 30x10-ken block is the 1902 Konosu standard) - for the `plot_regularity = "grid"` knob (269's module, waits for 269): keep it for a planned field origin only if it reads as equal strips laid off a road or canal (its present effect, collapsing the row-step spread, is close to that); it must never draw a checkerboard of equal rectangular paddies unless the ground is jori ground; the 610 spec line states the rule; no pool map rolls "grid" today - searched 2026-09-28: Japanese (新田 with 地割, 碁盤目, 整然, 区画, 短冊, 干拓; 干潟八万石/椿新田, 鴻池新田, 紫雲寺潟新田, 見沼新田, 興除新田; kotobank, ja.wikipedia, 水土の礎, ARIC, JSIDRE, Chiba prefecture, Kodaira city), English (Edo reclaimed land field layout); two J-STAGE PDFs on new-field village form had no readable text. GM ruling: nothing in the record or the knob's note shows the GM ruled "grid" in; the typing gate to a planned origin was the engine's own grounding.

M08 PREMODERN-ATTESTED - new fields/610 says survey registers measured parcels of a few se: a 1684 Kami-Baba paddy parcel of 16 x 10.5 ken, 5 se 18 bu (about 555 m2, 0.14 acre), and 1678 Yaho dry fields of 3 se 20 bu to 1 tan 3 se 20 bu, with the caveat that a register parcel may hold more than one bunded sheet - `plot_size = "large_block"` (about 0.0675 acre, 2.8 se, at ftpx >= 2; about 70 x 37 ft on a 1 ft/px hamlet) is within that premodern range and stays; nothing to stop drawing; its name and the houses.py docstring ("large regular blocks ... signal a later planned reclamation") are the modern framing and could be reworded when 269 lands; the rule is that a paddy is never drawn at the Meiji 1-tan block or larger (610 spec line). GM ruling: none found for large_block; the ft/px=1 hamlet grain was left untouched at the GM's request (houses.py docstring), which covers the hamlet sizes knowingly.

## Left open, and why

- fields/050 was treated as NOT held: `git log origin/main..HEAD` in diagram-supplemental names only the 269 merge-from-main commit 0b2a4566f for it, and the file is byte-identical in both clones, so 269 has not rewritten it. A check session that reads the rule literally may disagree.
- The assembled pages (research/contents.json#fields, research/contents.json#fields and fields.js) were rebuilt by `make record` / `make citations` but NOT committed, because they also carry another session's uncommitted F1 check-a edits to fields 070 and 600; SOURCES.html was committed. The check session should run `make record && make citations` after F1 check-a commits.
- Ma Yilong's 農說 and the 中国稻作史 chapter (TO-DOWNLOAD 281, 282) would give a premodern hill density if the GM fetches them.
- Record checks (quote-check, record-format, source-applicability on the 6 new keys) are owed.
