# Writing up kept uncited sources (feature 312, FR-012)

You draft registry write-ups for pages a research session read, which the `source-filter` judged worth keeping and no
entry of the record cites yet. The GM, 2026-10-02: *"it would be worth creating a source write-up for each source that we
don't use, which is basically just exactly the same as what we have for our existing sources. So, for instance, we tag
them with whether they are pre-modern, or contemporary, whether they are reference, or academic, etc. We also have a
summary of what they are. And then we talk about why we think it is applicable and what the limitations are."* A
`source-applicability` check reads every write-up against the page afterwards, so write only what the page shows.

Read `MANIFEST.md` in your bundle, then EVERY page file it lists, whole. Read nothing else - no file under `/diagram`,
no web.

## What you write, per page: one JSON line in `entries.jsonl` in the bundle directory

    {"id": "p00012", "key": "kotobank-goningumi", "citation": "...", "what": "...", "why": "...", "tags": "period=premodern; region=japan; kind=reference"}

- `key`: lower-case ASCII, hyphens, unique and readable - the work's subject in romanization plus its site:
  `<subject>-jawiki`, `<subject>-zhwiki`, `<subject>-enwiki`, `kotobank-<term>`, `<author>-<year>` for a paper,
  `<institution>-<subject>` for an institution's page. No key the MANIFEST lists as taken.
- `citation`: the citation line as the model entries write it - author or institution where the page names one, the
  title (an original-language title quoted as written, then a translation in parentheses marked as one: `("...", title
  translated)`), the work or site it is part of, then `(in Japanese; <url>)` / `(in Chinese; <url>)` / `(<url>)` with the
  URL EXACTLY as the MANIFEST gives it.
- `what`: the text of `What it is:` (without the label) - one to three sentences: what the page is (an encyclopedia article, a dictionary entry, a
  municipal page on a designated site, a paper's full text...) and what it covers. Concrete: name the place, the period,
  the thing.
- `why`: the text of `Why it applies, and its limits:` (without the label) - one to three sentences on what the page could carry for a premodern East
  Asian setting and what it cannot: its date (when is its evidence from?), its place, its method, what it leaves out.
  State only what is SPECIFIC to this work - never the generic limits of its category ("it is a tertiary source", "a
  tourism page citing no study"); the tag's label carries those. Never invent a figure or a claim the page does not make.
- `tags`: `period=<one or more>; region=<one or more>; kind=<one>` from the vocabulary below, the first value of each
  facet primary. PERIOD follows the EVIDENCE, not the publication: a modern dictionary's entry on an Edo custom is
  `premodern`; a present-day survey of a surviving old village takes the period of the form it records.

House style: hyphens only, never an em-dash or en-dash; American spellings. Your reply is one count line.

## Three model entries (from the works cited; an uncited entry has no `Used for:` line)

    Tsutsui Michio and Hashimoto Yoshiyuki, "鎮守の森" ("chinju no mori", the tutelary shrine's wood), in the revised edition of the Heibonsha World Encyclopedia (改訂新版 世界大百科事典), on Kotobank (in Japanese; https://kotobank.jp/word/%E9%8E%AE%E5%AE%88%E3%81%AE%E6%A3%AE-569966)
    What it is: A signed entry in Japan's standard general encyclopedia, reproduced on the Kotobank dictionary site, defining the wood that stands in a tutelary shrine's precinct.
    Why it applies, and its limits: It says in general terms where a Japanese village's tutelary shrine stands - within the village or at its edge - and that the shrine ground is where the village gathers for its main observances. It gives no date or region, and names both sites without saying which was commoner or why a village chose one.
    tags: period=premodern; region=japan; kind=reference

    ja.wikipedia 弘道館 ("the Kodokan", the Mito domain school, title translated) (https://ja.wikipedia.org/wiki/弘道館)
    What it is: The Japanese Wikipedia article on the Kodokan, the domain school of Mito founded by its ninth lord inside the castle's third bailey, with its site area.
    Why it applies, and its limits: It is the upper bound of a domain school's ground and says where one stood against the castle. The article itself calls it the largest domain school site in Japan, built by one of the three Tokugawa branch houses, so it is not a typical school, and it was founded late, in 1841.
    tags: period=premodern; region=japan; kind=reference

    Joetsu City, "Yoneoka no hasagi michi" (The Yoneoka road of rice-drying trees), one of the city's local treasures (in Japanese; https://www.city.joetsu.niigata.jp/soshiki/bunkagyousei/chiikinotakara-r4-no107.html)
    What it is: A city page on a row of rice-drying trees beside a school path in Joetsu, Niigata, replanted there when the surrounding paddies were consolidated.
    Why it applies, and its limits: It says that drying trees were an ordinary sight of Niigata's paddy country "until around the end of Showa" (the 1980s), which supports the drying tree as a regional form; that is the neighbors' memory of the twentieth century, and the page does not say how old the practice is or whether it was common before Meiji.
    tags: period=modern-preindustrial,present-day; region=japan; kind=institutional

## The tag vocabulary (derived from `research/source-tags.json`)

