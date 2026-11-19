# Derivation - the pool pipeline's map walk and generation key (feature 449 T219)

Written 2026-11-19 in the form of `.specify/templates/derivation.md`, to be judged against `docs/work-budget-rubric.md`. The
stage is the pipeline's own work in one run over the pool: the walk that finds and classifies every map, the key each live
map is checked against, the cache lookup, and (on a miss) the publish. The engines' generation is not counted here; each engine
has its own budget.

**The form, and why.** The pool-sheet form (feature 449 T201), with the pool's two TREES as its "sheets": `pool` and
`legacy-hand-authored-pool`. The pipeline has no households, so the default form's lines at 20, 40 and 80 households would
each be a pool invented to fit them; the pool, like a Mode A sheet, is one fixed input whose sizes are read off it. The two trees
are the natural split a counter can sit on (the walk lists each tree on its own, and only the live tree's maps are keyed), each
tree's line is exact, and their sum is the run. The once-per-run terms (the engines' ids, the Mode A tier declaration, the font
set) are charged to `pool`, the tree whose maps need them. How the count grows with the pool is the formula under `## Growth`.

**Provenance (blind to the pipeline's code).** Read: the template, the rubric, T208's derivation (for its form only), T219-T222's
lines in `tasks.md`, the pipeline's index (`CLAUDE.md` of the pipeline package) and `dev/cache.md` for the cache's contract, the
form checker under `rust/gate` (the bundle's form checks), and `ls` of every map folder of both trees. The reads per map are
measured from the cache entries' recorded read lists (`.gencache/<map>/meta.json`, the `files` list alone: no key string, no
function list, no timing field read); the engines' run-time reads from the engines themselves: the hamlet binary's entry point
(`rust/phases/src/bin/hamlet.rs`, which reads its spec and nothing else at run time), the Mode A page writer's read log
(`rust/mode_a/src/reads.rs`, its header) and the raster's font loading (`rust/mode_a/src/raster/render.rs`, which loads the
system fonts). The engine ids from `readelf -n` of the two built binaries. Not read: any module of the pipeline package (its cache,
regeneration, pool listing, index, render and roll modules, and its code-id module), `scripts/gates/codeid.py`, any test, log or timing of
them. Disclosed: the hamlet entries' read lists (168 to 175 files each) were recorded on 2026-10-31 and 2026-11-07 by the deleted
Python hamlet engine and its page writer; the Rust hamlet binary reads its spec alone, so they are set aside and priced only as
the hamlet page's future reads (assumption 5). Also disclosed: the pipeline's index, `dev/cache.md` and the page writer's read-log
header describe how today's key and its read recording behave (what the key covers, how the engine walk prunes, that the page
writer lists every file it read for the cache, that publish writes the meta last); the algorithm below is derived from the
contract they state (what must re-key a map, atomic publish) and from the brief's terms (the binary's id once a run, the spec,
the reads reported), not from that behavior.

## Contract

- Sizes: pool sheets: pool, legacy-hand-authored-pool
- Reads: the two trees' directory entries (tree, tier, map folder, file names; no file's contents to classify it); the Mode A
  tier declaration (the building types declaration, `types.json`, 9,007 bytes: the tiers `magistracies` and `country-shrines`);
  each engine binary's GNU build id (the hamlet binary of `rust/phases`, `l7r-mode-a` of `rust/mode_a`); the system font set the
  Mode A raster loads (155 font files in 25 directories); per live map its cache entry's meta (its key's parts as records: the
  engine id, the spec's stat and digest, one record per read the engine reported last time, one per artifact), the spec's
  stat, each reported read's stat, and each artifact's stat; on a stat mismatch, that file's bytes.
- Writes: per folder one kind - a hamlet (`.spec.json`), a generated compound (`.compound.json`), a hand sheet (an `.svg` in a
  declared Mode A tier, with neither of the first two beside it), a frozen exhibit (a legacy `.json` alone, never keyed), or a
  report naming the folder; per live map a HIT (served) or MISS (the engine runs); on a miss the entry published atomically -
  each artifact renamed into place, the meta (its key and records) renamed LAST - and the artifacts linked into the map's folder;
  `pool/index.html` rows (T220) for every map of both trees; render-sync's stamp on main (T222), the same records.
- Keeps: (1) a map is regenerated when its spec, any read its engine reported, its engine binary, or (Mode A) the font set
  changed, and served from the cache otherwise (`dev/cache.md`); (2) never a stale map, the contract's expensive failure: a
  file's stored digest is reused only while its size, mtime (ns), ctime and inode all match the record AND its mtime is older
  than the record's own write (the racy-file rule: a file changed within the clock's tick of its hashing is re-hashed); any
  mismatch re-hashes the file and the verdict rests on the digest; a read gone from disk is a mismatch; (3) the engine's identity
  is its binary, taken once per run, never its sources per map (T219); (4) publish is atomic, meta last, so a reader sees a whole
  entry or none; (5) the frozen exhibits are never keyed or regenerated, only listed; (6) one walk serves every consumer (T220),
  each folder classified exactly once; (7) a spec edit alone re-keys its map (T222's stale compound).
- Bounds (measured 2026-11-19 on the pool as it is, a session clone with its renders present):

| tree | tiers D | folders M | live maps K | entries listed (roots, tiers, folders) | file entries F | index rows |
|---|---|---|---|---|---|---|
| pool | 3 | 11 | 11: 5 hamlets, 2 generated compounds, 4 hand sheets | 5 + 11 + 67 = 83 | 67 | 11 |
| legacy-hand-authored-pool | 5 | 19 | 0: 19 frozen exhibits | 5 + 19 + 39 = 63 | 39 | 19 |

| live map | kind | spec bytes (64-byte blocks) | reads R (spec apart) | artifacts A |
|---|---|---|---|---|
| inashiro | hamlet | 128 (2) | 0 | 2 |
| kashikawa | hamlet | 118 (2) | 0 | 2 |
| kuwabata | hamlet | 171 (3) | 0 | 2 |
| mizuguchi | hamlet | 96 (2) | 0 | 2 |
| sawada | hamlet | 159 (3) | 0 | 2 |
| county-magistracy-example | generated compound | 8,115 (127) | 196 | 3 |
| ochiba-roundtrip-test | generated compound | 7,378 (116) | 246 | 3 |
| hayakawa-magistracy | hand sheet | 73,164 (1,144) | 269 | 2 |
| ochiba-magistracy | hand sheet | 60,220 (941) | 259 | 2 |
| ubame-magistracy | hand sheet | 75,530 (1,181) | 211 | 2 |
| hoshigaoka-shrine | hand sheet | 100,362 (1,569) | 224 | 2 |
| all | | 5,090 blocks | sum R = 1,405; U = 297 distinct | sum A = 24 |

A hamlet's reads: the hamlet binary reads its spec alone (all else is compiled in), so R = 0 and its key is the binary's id and
the spec. A sheet's reads: what the page writer reported (the page's assets, the building types declaration, the knobs, 160 or
so modal texts, 55 to 104 research fragments its modals link, the sheet's own notes); the 297 distinct paths hold 2,658,248
bytes (41,683 blocks, 140.3 a file on average), each read by 4.73 sheets on average. Artifacts: a hamlet's driver svg and json;
a generated compound's svg, page and png; a hand sheet's page and png.

## The algorithm

    once per run:
        tiers  <- the Mode A tiers of the building types declaration          (one read, parsed)
        ids    <- for each engine binary, its GNU build id                     (one ELF note each; no source read)
        fonts  <- the font set's (path, size, mtime, inode) list               (only when a Mode A map is live)
        paths  <- an empty table: path -> (stat, digest when hashed)           (the run's memo)
    walk:  for tree in (pool, legacy-hand-authored-pool):
               list tree; for tier in it: list tier; for folder in it:
                   list folder; classify each entry by suffix (.spec.json, .compound.json, .svg, .json, else ignored)
                   kind <- spec ? hamlet : compound ? compound : (svg and tier in tiers) ? hand sheet
                           : (tree is legacy and .json) ? frozen : REPORT
                   index row (T220)
    key:   for each live map m (hamlet, compound, hand sheet):
               meta <- m's cache entry (or main's stamp, for render-sync); none -> MISS
               ids[engine(m)] == meta.engine_id, else MISS                    (and the font set's id, Mode A)
               stat the spec; compare with meta.spec record                     (mismatch -> hash it, compare digests)
               for each read record r in meta:                                  (R records)
                   s <- paths[r.path], stat-ing the path on its first touch this run
                   s == r.stat, else hash the file once this run (memo) and compare digests; differ -> MISS
               for each artifact record: stat the map folder's copy; absent or different -> link it back from the entry
               HIT when every record held
    miss:  run the engine (its own budget); it reports its reads
           key <- H(engine id, spec digest, [font-set id], each read's (path digest, content digest))  (one 64-byte block each)
           rename each artifact into the entry; write the records; rename the meta LAST; link the artifacts into the folder

The verdict is the same as computing the full key and comparing it with the stored one: the key is a function of exactly
the records compared, each equal. Render-sync on main walks the same way and holds each live map against main's stamp, which
stores the same records, so its all-hit run is the same count.

## The count, factor by factor

The run counted is the ALL-HIT run: nothing changed since every entry was published, so every live map is served. It is the run
a counter reproduces exactly on the pool as it is (S8: the typical case of a sweep after the cache is warm; a change's work is
priced per change under `## The work a change adds`). A counter reads it on the SECOND of two consecutive runs with nothing
changed between them, after the first has published every entry: a fresh clone's or worktree's first run is the cold run (about
56,200 by that table), never this one. Values are given per tree, `pool, legacy-hand-authored-pool`.

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | over the run | N = 11, 19 (30 maps) | every map folder of the two trees is walked once; the 11 live ones are keyed | 30 here; grows one a map |
| tree and tier listings | once | 4, 6 | each tree's root and each of its tiers listed once (1 + 3, 1 + 5) | fixed by the tiers |
| map folder listings | per item | 11, 19 | each map folder listed once, never globbed again by a consumer | one a folder |
| entries listed | over the run | 83, 63 | roots 5 + 5, tiers 11 + 19, folders 67 + 39: each name read once from its directory | a clean checkout: folders 33 + 39 (tracked files only), 33 fewer on pool |
| entries classified | over the run | 67, 39 | each file entry of a map folder matched once against the kinds' suffixes (F) | one an entry |
| folder kinds decided | per item | 11, 19 | the precedence above, from the flags the classification set | one a folder |
| tier lookups | once | 3, 5 | each tier's name asked once of the declared Mode A tiers | one a tier |
| tracked lookups | once | 0, 0 | a hand sheet's svg is told by precedence (no spec, no compound, a declared tier), so no git index is read: reading it would cost its 28,194 tracked entries a run, about 5x this whole budget | 0 |
| types declaration read | once | 1, 0 | the tier list, one file | 1 |
| types declaration parsed | once | 141, 0 | 9,007 bytes in 64-byte blocks | grows only with the declaration |
| engine ids | once | 2, 0 | one GNU build-id note a binary (present on both today); never a source file | 2; a binary built without the note: hashed whole, assumption 4 |
| font set listings | once | 25, 0 | the Mode A raster loads the system fonts, so their identity is part of a sheet's key; each font directory listed once a run | 0 when no Mode A map is live |
| font set entries | once | 422, 0 | the names those 25 directories hold | as installed |
| font set stats | once | 155, 0 | each font file stat-ed once a run | as installed |
| font set records | once | 155, 0 | each font file's record (path, size, mtime, ctime, inode) parsed from the font-set record the last rendering run left | as installed |
| font set compares | once | 155, 0 | each stat against its record; all held, the set's id is the recorded one | as installed |
| index rows | per item | 11, 19 | one row a map, compared with the last run's row; the file rewritten only on a difference (T220) | one a map |
| cache entries read | per item, on the keyed maps | 11, 0 | the cache lookup: each live map's meta opened once | one a live map |
| engine id compared | per item, on the keyed maps | 11, 0 | the entry's engine id against the run's, looked up in a two-entry table | one a live map |
| font set id compared | per item, on the Mode A maps | 6, 0 | a sheet's entry's font-set id against the run's (a hamlet renders no png) | one a sheet |
| spec records | per item, on the keyed maps | 33, 0 (11 parsed + 11 stats + 11 compares) | the spec's record held against its stat; its bytes hashed only on a mismatch (none on this run) | 3 a live map |
| reads per keyed map | per item, on the keyed maps | 0 a hamlet; 196 to 269 a sheet; sum R = 1,405 | what each engine reported reading last time (Bounds) | 0 (a hamlet) to 269 (hayakawa) |
| read records | per read | 4,215, 0 (1,405 parsed + 1,405 path lookups + 1,405 stat compares) | each record parsed, its path looked up in the run's path table, its stat compared: no read hashed while its stat holds | 3 a read |
| distinct reads stat-ed | over the run | 297, 0 | each distinct path stat-ed once a run however many sheets read it (U = 297 of 1,405) | U at most sum R |
| artifact records | per item, on the keyed maps | 72, 0 (24 parsed + 24 stats + 24 compares) | each artifact in the map's folder held against its record; nothing linked while it holds | 3 an artifact; a clean checkout links back the 24 |
| bytes hashed | over the run | 0, 0 | the all-hit run: every stat holds, so no file is hashed (`## The work a change adds` prices a mismatch) | 0 here |
| slack | over the run | 1 | nothing is searched: every factor is read off the pool as it is, so nothing varies around a mean at a fixed pool | 1 |

So: the walk (listings, entries, classification, kinds, tier lookups, index rows), plus the once terms (types declaration,
engine ids, font set), plus 2 a live map (lookup, engine id) and 1 a sheet (font-set id), 3 a spec, 3 a read and 1 a distinct
read, 3 an artifact; times a slack of 1.

- pruning: a map's check stops at its first record that fails (a MISS), but the all-hit run must confirm every record of every
  live map to serve it, so nothing prunes the run counted here; what keeps it small is that a record is held by its stat, never
  by re-hashing the file, and a read shared by several sheets is stat-ed once.

## Totals

- at pool: (4 + 11 + 83 + 67 + 11 + 3 + 0 + 1 + 141 + 2 + 25 + 422 + 155 + 155 + 155 + 11 + 11 + 11 + 6 + 33 + 4215 + 297 + 72 + 0) x 1 = 5891
- at legacy-hand-authored-pool: (6 + 19 + 63 + 39 + 19 + 5 + 0 + 19) x 1 = 170
- all sheets: 5891 + 170 = 6061

About 202 a map walked (6,061 over 30), or 536 a live map (5,891 over 11), against the reference's 4,000 a thing.

## The budget by counted kind

Each kind is one counter, bumped where the work happens (S5). The all-hit run:

| kind | what one is | pool | legacy-hand-authored-pool | both |
|---|---|---|---|---|
| dir_list | a directory opened and listed (4 + 11 + 25 font; 6 + 19) | 40 | 25 | 65 |
| dir_entry | one name read from a listing (83 + 422 font; 63) | 505 | 63 | 568 |
| classify | a map folder's entry matched against the kinds' suffixes | 67 | 39 | 106 |
| folder_kind | a folder's kind decided by precedence | 11 | 19 | 30 |
| tier_lookup | a tier asked of the declared Mode A tiers | 3 | 5 | 8 |
| tracked_lookup | a path asked of the git index | 0 | 0 | 0 |
| file_read | a configuration file opened (the types declaration) | 1 | 0 | 1 |
| parse_block | 64 bytes of the types declaration parsed | 141 | 0 | 141 |
| engine_id | an engine binary's build-id note read | 2 | 0 | 2 |
| index_row | a map's index row composed and compared | 11 | 19 | 30 |
| meta_read | a cache entry's meta opened (the lookup) | 11 | 0 | 11 |
| id_compare | an entry's engine id (11) or font-set id (6) compared with the run's | 17 | 0 | 17 |
| meta_record | a record parsed (155 font + 11 spec + 1,405 read + 24 artifact) | 1595 | 0 | 1595 |
| path_lookup | a read's path looked up in the run's path table | 1405 | 0 | 1405 |
| stat | a file stat-ed (155 font + 297 read + 11 spec + 24 artifact) | 487 | 0 | 487 |
| stat_compare | a stat compared with its record (155 font + 1,405 read + 11 spec + 24 artifact) | 1595 | 0 | 1595 |
| hash_block | 64 bytes hashed | 0 | 0 | 0 |
| total | | 5891 | 170 | 6061 |

On a change, four kinds more: `digest_compare` (a fresh digest against its record), `key_fold` (one 64-byte block folded into a
new key), `rename` (an artifact or a meta renamed into its entry) and `link` (an artifact linked into its map's folder), with
`hash_block` and `meta_record` (written) counting there too.

## The work a change adds

Not in the Totals (the run counted changes nothing); each is the increment on top of the all-hit run, in the same kinds.

| change | added | figure here |
|---|---|---|
| a read whose stat moved | its bytes hashed once a run (140.3 blocks on average, one file) + 1 digest compare; content equal: its records refreshed in the entries that hold it | about 141 |
| a spec whose stat moved | its bytes hashed (2 or 3 blocks a hamlet, 116 or 127 a compound, 941 to 1,569 a hand sheet) + 1 digest compare | 3 to 1,570 |
| a miss on a sheet (its engine's work apart) | key folds 3 + R (engine, font set, spec, each read) + records written 1 + R + A + renames A + 1 (meta last) + links A | 196 to 269 reads: 406 to 549; 480 on average |
| a miss on a hamlet | key folds 2 + records 3 + renames 3 + links 2 | 10 |
| a changed read shared by sheets | its hash, then a miss on each sheet that read it (4.73 on average) | about 141 + 4.73 x 480 = 2,411 |
| the Mode A binary rebuilt | all 6 sheets miss, no read re-hashed (their stats hold): folds 1,423 + records 1,425 + renames 20 + links 14 | 2,882 |
| the hamlet binary rebuilt | all 5 hamlets miss | 50 |
| the font set changed | all 6 sheets miss (as a rebuild) + its 155 records rewritten | about 3,037 |
| a cold run (no entries: a fresh clone) | every live map misses; every distinct read and spec hashed once: 41,683 + 5,090 blocks + 396 path-digest blocks + every miss 2,932, on top of the walk and the stats | at most 6,061 + 50,101 = 56,162 |

## Growth

In the input sizes, with M folders (30), D tiers (8), the tree roots (2), N listed entries (146), F file entries (106), K live
maps (11) of which S are Mode A sheets (6), E engines (2), B the types declaration's blocks (141), the font set's L directories,
n entries and f files (25, 422, 155), sum R reads over the live maps (1,405), U distinct reads (297) and sum A artifacts (24):

    all-hit run = (2 + D + M) + N + F + M + D + M + 1 + B + E + (L + n + 3f) + 2K + S + 3K + 3 sum R + U + 3 sum A
                = 40 + 146 + 106 + 30 + 8 + 30 + 1 + 141 + 2 + 912 + 22 + 6 + 33 + 4215 + 297 + 72 = 6,061

The spec's bytes enter on a change, not on the all-hit run: a run with c files whose stat moved adds the sum of their blocks
(bytes / 64; a spec's 2 to 1,569, a read's 140.3 on average) and one digest compare each, and each map that misses adds
(2 + R + [1 on a sheet]) key folds + (1 + R + A) records written + (A + 1) renames + A links (`## The work a change adds`).

Every term is linear in the pool's size: one listing and one kind a folder, one entry check a file, and per live map a fixed
three records plus three a read. The reads a map has are bounded by its kind (a hamlet 0; a sheet by the page's modal texts and
the fragments they link, 196 to 269 today), so sum R grows as K times that bound, and U grows slower than sum R (each distinct
read is shared by 4.73 sheets now). The once terms do not grow with the pool. No term multiplies the maps by the engine's
sources: the engine is one build id a run, where today's key re-reads and hashes every engine source for every map (T157's
scoping). A pool of twice the maps at the same mix costs about twice the run.

## How far over is "far over"

S10 applies: a rebuilt pipeline counting up to twice a tree's line, the excess named and reasonable, is LEEWAY; past twice, OVER.
For scale, priced on the same pool:

- Each read re-hashed on every run instead of held by its stat: 1,405 x 140.3 blocks, about 197,000 hash blocks, 32x the run.
- Each distinct read hashed once a run (memoized within the run, no stat record): 41,683 blocks, about 7x the run.
- The engine keyed on its sources per map instead of its build id: every engine source file read and hashed for each of the 11
  maps, a term growing with the maps times the engine's size.
- The git index read to tell a tracked svg: 28,194 entries a run, about 5x the run.

## Cheaper algorithms considered

- sweep: not used. Nothing is ordered along an axis: the walk visits each directory once in its own order, and a map's records
  are checked independently.
- grid or spatial index: not used. There is no geometry; the run's path table is a hash map from a path to its stat and digest,
  each probe counted as a `path_lookup`.
- priority queue: not used. Nothing is ranked: every map is decided, and none is preferred to another.
- incremental update: used for the files (a digest is updated only for a file whose stat moved; a change touches only the
  entries whose records name it). A persistent cross-map table (each distinct path's stat and digest once, with the set of maps
  that read it, so the all-hit run checks 297 paths and not 1,405 records) was priced and not used: about 1,416 (the walk and
  once terms) + 11 + 2 + 1 + 3 x 297 + 33 + 72 = 2,426 at this pool instead of 6,061, 2.5x less. It can be made sound (each
  invalidation made durable, its maps' entries removed, before the table records a new digest), but it is a second shared file
  that must move in step with every entry under the contract's atomic publish, across concurrent runs in one clone. The tie to
  the contract is T221's: `make map MAP=<folder|spec>` runs one map, and the bundle door asks the cache in process whether a map is current,
  each about one map; a self-contained entry answers that from itself (about 4 a read of that map: 800 to 1,090 for a sheet)
  without reading or locking the shared table, though the table would answer it for about the same (its 297 paths, then 2 a read). The tie is weak, so
  the choice is the judge's: per-entry records are budgeted here (who chose: this derivation), and assumption 1 says what the
  table would change.
- memoizing what a scan does not change: used. Each engine's id once a run, not its sources per map; each distinct read stat-ed
  once a run however many sheets read it; a file's digest kept with its stat and re-hashed only when the stat moves; the font
  set's identity once a run; the types declaration read once for every folder's classification.

## Assumptions, and the ones least sure

1. **Per-entry records, not a cross-map table (least sure: the likeliest finding).** 3 x sum R = 4,215 is 70% of the run. A
   persistent table of the distinct reads would hold the all-hit run to about 2,426 (`## Cheaper algorithms considered`,
   incremental update), past S11's factor of 2 below this budget. It is declined for the shared file's consistency under atomic
   publish and concurrent runs, not for its count; if the judge rules that no tie, the derivation is re-written on the table and
   the budget is about 2,426.
2. **Stat-held digests are sound (least sure).** The all-hit run hashes nothing because a record's size, mtime (ns), ctime and
   inode hold for the file. A tool that rewrites a file in place to the same size within the clock's tick of its hashing is
   caught by the racy-file rule (a file whose mtime is not older than its record is re-hashed); a copy that preserves mtime (a
   `cp -p` or `rsync -t`) changes the ctime and usually the inode, which the record also holds. What it cannot see: a file
   restored with its old size, mtime, ctime and inode, which no ordinary tool does. If the judge or an empirical audit rules
   stat-holding unsound, the fallback is hashing each distinct read once a run: 41,683 blocks more, the run about 8x as costly.
3. **The engine reports every read (a hole found).** The Mode A page writer's read log notes a path only when it is a file
   that exists, so a probe for a file it found ABSENT (a modal text a feature has none of yet) is not a read; creating that file
   later leaves the sheet cached and stale. The key here can only be as complete as the reads reported: the engine owes its
   absent probes as reads too (each a record whose stat is "absent"), or its directory listings. Not fixed here (the brief edits
   nothing else); reported.
4. **The build id identifies the engine.** The GNU build id is a hash over the linked output, present on both binaries today, so
   any change to the engine or anything compiled into it (the hamlet's knobs and tables) moves it. Shared libraries loaded at run
   time are outside it, as the interpreter's installed packages were outside the old key; the system fonts are the one such
   input known to change a map, priced as the font set. A binary built without the note would be hashed whole once a run (21,600
   blocks the hamlet binary, 218,143 the Mode A one, 1,382,384 and 13,961,120 bytes).
5. **The hamlets' reads.** The hamlet binary reads its spec alone today, so a hamlet's key is its build id and spec. When a
   hamlet's page is written again (T222 records it against feature 444's open row), its reads come back: the deleted Python
   writer's records show 168 to 175 a hamlet (854 for the five), which would add about 3 x 854 = 2,562 record checks and their
   new distinct paths to the run, and the budget would be re-derived for it.
6. **The artifacts per kind.** A hamlet's 2 (the driver svg and json), a generated compound's 3, a hand sheet's 2, from today's
   entries and folders; T221 may rename them, not change their count much. In a clean checkout (renders absent) a hit links the
   24 back and the folders list 72 entries, not 106.
7. **Render-sync is the same run.** Its stamp on main is assumed to hold the same records the cache entry does, so its all-hit
   run counts the same; the record site's own staleness stamp (T222's "the record site") is not part of this stage.
