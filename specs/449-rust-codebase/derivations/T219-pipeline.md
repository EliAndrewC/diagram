# Derivation - the pool pipeline's map walk and generation key (feature 449 T219)

Written 2026-11-19 in the form of `.specify/templates/derivation.md`, to be judged against `docs/work-budget-rubric.md`. The
stage is the pipeline's own work in one run over the pool: the walk that finds and classifies every map, the key each live
map is checked against, the cache lookup, and (on a miss) the publish. The engines' generation is not counted here; each engine
has its own budget. Revised the same day on the `work-budget` agent's first verdict (LOOSE; `## Earlier findings`): the reads
are held in one persistent table of distinct paths, not in each map's entry.

**The form, and why.** The pool-sheet form (feature 449 T201), with the pool's two TREES as its "sheets": `pool` and
`legacy-hand-authored-pool`. The pipeline has no households, so the default form's lines at 20, 40 and 80 households would
each be a pool invented to fit them; the pool, like a Mode A sheet, is one fixed input whose sizes are read off it. The two trees
are the natural split a counter can sit on (the walk lists each tree on its own, and only the live tree's maps are keyed), each
tree's line is exact, and their sum is the run. The once-per-run terms (the engines' ids, the Mode A tier declaration, the read
table and its font rows) are charged to `pool`, the tree whose maps need them. How the count grows with the pool is the formula
under `## Growth`.

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
  each engine binary's GNU build id (the hamlet binary of `rust/phases`, `l7r-mode-a` of `rust/mode_a`); the READ TABLE, one
  persistent file per clone (main's for render-sync): one row per distinct path any live map's engine reported reading (297), and
  one per font directory (25) and font file (155) the Mode A raster loads, each row its path, stat (size, mtime ns, ctime,
  inode), digest (none for a font row) and the maps that read it; per live map its cache entry's meta (engine id, the spec's
  record, one record per artifact, the key); the stat of each row's path, of each spec and of each artifact; on a stat mismatch,
  that file's bytes, and that row's map list.
- Writes: per folder one kind - a hamlet (`.spec.json`), a generated compound (`.compound.json`), a hand sheet (an `.svg` in a
  declared Mode A tier, with neither of the first two beside it), a frozen exhibit (a legacy `.json` alone, never keyed), or a
  report naming the folder; per live map a HIT (served) or MISS (the engine runs); on a changed read the entries of the maps
  its row names removed; on a miss the entry published atomically - each artifact renamed into place, the meta (its key and
  records) renamed LAST - and the artifacts linked into the map's folder; the read table rewritten (temp, then rename) when a
  row changed; `pool/index.html` rows (T220) for every map of both trees; render-sync's stamp on main (T222), the same table and
  entries.
- Keeps: (1) a map is regenerated when its spec, any read its engine reported, its engine binary, or (Mode A) the font set
  changed, and served from the cache otherwise (`dev/cache.md`); (2) never a stale map, the contract's expensive failure: a
  file's stored digest is reused only while its size, mtime (ns), ctime and inode all match its row AND its mtime is older than
  the row's own write (the racy-file rule: a file changed within the clock's tick of its hashing is re-hashed); any mismatch
  re-hashes the file and the verdict rests on the digest; a read gone from disk is a mismatch; a font row has no digest, so any
  move of its stat removes the sheets' entries; (3) THE ORDER that makes the shared table safe: a row's digest or stat is
  replaced only after every entry its map list names is removed, durably; and a published map is in the map list of a row for
  each of its reads before its meta is renamed - the run writes the table before it renames the metas of the maps it
  published - so an entry that exists has every read it depends on watched by the table; (4) the engine's identity is its
  binary, taken once per run, never its sources per map (T219); (5) publish is atomic, meta last, so a reader sees a whole entry
  or none; (6) the frozen exhibits are never keyed or regenerated, only listed; (7) one walk serves every consumer (T220), each
  folder classified exactly once; (8) a spec edit alone re-keys its map (T222's stale compound).
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
bytes (41,683 blocks, 140.3 a file on average), each read by 4.73 sheets on average. The font set: 155 font files in 25
directories (422 entries listed, when a directory is listed). Artifacts: a hamlet's driver svg and json; a generated compound's
svg, page and png; a hand sheet's page and png.

## The algorithm

    once per run:
        lock the read table                                                   (one run writes it at a time)
        tiers  <- the Mode A tiers of the building types declaration          (one read, parsed)
        ids    <- for each engine binary, its GNU build id                     (one ELF note each; no source read)
        table  <- the read table: rows (path, stat, digest, maps)              (one file; a row's map list read only on need)
    hold the table:
        for each row: stat its path; equal to the row -> held, nothing more
            a read row that moved: hash the file; digest equal -> the row's stat refreshed
                                   digest differs or file gone -> read its map list; remove each named map's entry (durable);
                                                                  then the row takes the new stat and digest
            a font row that moved: read its map list; remove those entries (durable); a directory row's directory listed
                                   again and its file rows added or dropped
    walk:  for tree in (pool, legacy-hand-authored-pool):
               list tree; for tier in it: list tier; for folder in it:
                   list folder; classify each entry by suffix (.spec.json, .compound.json, .svg, .json, else ignored)
                   kind <- spec ? hamlet : compound ? compound : (svg and tier in tiers) ? hand sheet
                           : (tree is legacy and .json) ? frozen : REPORT
                   index row (T220)
    key:   for each live map m (hamlet, compound, hand sheet):
               meta <- m's cache entry (or main's stamp, for render-sync); none (never made, or removed above) -> MISS
               ids[engine(m)] == meta.engine_id, else MISS
               stat the spec; compare with meta.spec record                     (mismatch -> hash it, compare digests)
               for each artifact record: stat the map folder's copy; absent or different -> link it back from the entry
               HIT when every record held (its reads were held by the table above)
    miss:  run the engine (its own budget); it reports its reads
           key <- H(engine id, spec digest, [font-set id], each read's (path digest, content digest))  (one 64-byte block each)
           each read: its row (added if new, its digest from this run's hash or the row) lists m
           rename each artifact into the entry; write the meta's records
    end:   if a row changed: write the table (temp, then rename); THEN rename each published meta (meta last); unlock

The verdict is the same as computing the full key and comparing it with the stored one: the key is a function of the engine id,
the spec and the reads' digests, and an entry survives the table's hold only while every read it depends on held. The key is
kept in the meta as the entry's identity, so a lost table is rebuilt by re-hashing the reads and comparing keys, not by
regenerating. Render-sync on main walks the same way and holds each live map against main's table and stamp, so its all-hit run
is the same count.

## The count, factor by factor

The run counted is the ALL-HIT run: nothing changed since every entry was published, so every live map is served. It is the run
a counter reproduces exactly on the pool as it is (S8: the typical case of a sweep after the cache is warm; a change's work is
priced per change under `## The work a change adds`). A counter reads it on the SECOND of two consecutive runs with nothing
changed between them, after the first has published every entry: a fresh clone's or worktree's first run is the cold run (about
53,100 by that table), never this one. Values are given per tree, `pool, legacy-hand-authored-pool`.

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | over the run | N = 11, 19 (30 maps) | every map folder of the two trees is walked once; the 11 live ones are keyed | 30 here; grows one a map |
| tree and tier listings | once | 4, 6 | each tree's root and each of its tiers listed once (1 + 3, 1 + 5) | fixed by the tiers |
| map folder listings | per item | 11, 19 | each map folder listed once, never globbed again by a consumer | one a folder |
| entries listed | over the run | 83, 63 | roots 5 + 5, tiers 11 + 19, folders 67 + 39: each name read once from its directory | a clean checkout: folders 33 + 39 (tracked files only), 33 fewer on pool |
| entries classified | over the run | 67, 39 | each file entry of a map folder matched once against the kinds' suffixes (F) | one an entry |
| folder kinds decided | per item | 11, 19 | the precedence above, from the flags the classification set | one a folder |
| tier lookups | once | 3, 5 | each tier's name asked once of the declared Mode A tiers | one a tier |
| tracked lookups | once | 0, 0 | a hand sheet's svg is told by precedence (no spec, no compound, a declared tier), so no git index is read: reading it would cost its 28,194 tracked entries a run, about 14x this whole budget | 0 |
| types declaration read | once | 1, 0 | the tier list, one file | 1 |
| types declaration parsed | once | 141, 0 | 9,007 bytes in 64-byte blocks | grows only with the declaration |
| engine ids | once | 2, 0 | one GNU build-id note a binary (present on both today); never a source file | 2; a binary built without the note: hashed whole, assumption 4 |
| read table opened | once | 1, 0 | the one file holding every row | 1 |
| read table locked | once | 1, 0 | one run writes the table at a time (assumption 1) | 1 |
| font rows | once | 540, 0 (180 parsed + 180 stats + 180 compares) | the Mode A raster loads the system fonts, so their identity is part of a sheet's key: 25 directory rows and 155 file rows, each held by its stat; a directory is listed again only when its own stat moved, so the 422 entries are not read | 0 when no Mode A map is live; as installed |
| read rows | over the run | 891, 0 (297 parsed + 297 stats + 297 compares) | each distinct path any live map read, held once a run however many maps read it (U = 297 of sum R = 1,405); no file hashed while its stat holds; the row's map list is not read | U at most sum R |
| map lists read | over the run | 0, 0 | a row's map list is read only when its row moved (none on this run) | 0 here |
| index rows | per item | 11, 19 | one row a map, compared with the last run's row; the file rewritten only on a difference (T220) | one a map |
| cache entries read | per item, on the keyed maps | 11, 0 | the cache lookup: each live map's meta opened once (no read records in it) | one a live map |
| engine id compared | per item, on the keyed maps | 11, 0 | the entry's engine id against the run's, looked up in a two-entry table | one a live map |
| spec records | per item, on the keyed maps | 33, 0 (11 parsed + 11 stats + 11 compares) | the spec's record held against its stat; its bytes hashed only on a mismatch (none on this run) | 3 a live map |
| artifact records | per item, on the keyed maps | 72, 0 (24 parsed + 24 stats + 24 compares) | each artifact in the map's folder held against its record; nothing linked while it holds | 3 an artifact; a clean checkout links back the 24 |
| bytes hashed | over the run | 0, 0 | the all-hit run: every stat holds, so no file is hashed (`## The work a change adds` prices a mismatch) | 0 here |
| slack | over the run | 1 | nothing is searched: every factor is read off the pool as it is, so nothing varies around a mean at a fixed pool | 1 |

So: the walk (listings, entries, classification, kinds, tier lookups, index rows), plus the once terms (types declaration,
engine ids, the table opened and locked), plus 3 a row of the read table (its 297 reads and 180 font rows), plus 2 a live map
(lookup, engine id), 3 a spec and 3 an artifact; times a slack of 1.

- pruning: the table is held row by row and a row's map list is read only when the row moved, so the all-hit run touches each
  distinct path once and no map's read list at all; every row must still be held, since any one of them moving can make a map
  stale, so nothing prunes the rows themselves.

## Totals

- at pool: (4 + 11 + 83 + 67 + 11 + 3 + 0 + 1 + 141 + 2 + 1 + 1 + 540 + 891 + 0 + 11 + 11 + 11 + 33 + 72 + 0) x 1 = 1894
- at legacy-hand-authored-pool: (6 + 19 + 63 + 39 + 19 + 5 + 0 + 19) x 1 = 170
- all sheets: 1894 + 170 = 2064

About 69 a map walked (2,064 over 30), or 172 a live map (1,894 over 11), against the reference's 4,000 a thing.

## The budget by counted kind

Each kind is one counter, bumped where the work happens (S5). The all-hit run:

| kind | what one is | pool | legacy-hand-authored-pool | both |
|---|---|---|---|---|
| dir_list | a directory opened and listed (4 + 11; 6 + 19) | 15 | 25 | 40 |
| dir_entry | one name read from a listing | 83 | 63 | 146 |
| classify | a map folder's entry matched against the kinds' suffixes | 67 | 39 | 106 |
| folder_kind | a folder's kind decided by precedence | 11 | 19 | 30 |
| tier_lookup | a tier asked of the declared Mode A tiers | 3 | 5 | 8 |
| tracked_lookup | a path asked of the git index | 0 | 0 | 0 |
| file_read | a file opened whole (the types declaration, the read table) | 2 | 0 | 2 |
| lock | the read table locked for the run | 1 | 0 | 1 |
| parse_block | 64 bytes of the types declaration parsed | 141 | 0 | 141 |
| engine_id | an engine binary's build-id note read | 2 | 0 | 2 |
| index_row | a map's index row composed and compared | 11 | 19 | 30 |
| meta_read | a cache entry's meta opened (the lookup) | 11 | 0 | 11 |
| id_compare | an entry's engine id compared with the run's | 11 | 0 | 11 |
| record | a row or record parsed (180 font + 297 read + 11 spec + 24 artifact) | 512 | 0 | 512 |
| stat | a file or directory stat-ed (180 font + 297 read + 11 spec + 24 artifact) | 512 | 0 | 512 |
| stat_compare | a stat compared with its row or record | 512 | 0 | 512 |
| list_read | a row's map list read | 0 | 0 | 0 |
| hash_block | 64 bytes hashed | 0 | 0 | 0 |
| total | | 1894 | 170 | 2064 |

On a change, more kinds: `digest_compare` (a fresh digest against its row or record), `entry_remove` (a map's entry removed,
durably), `key_fold` (one 64-byte block folded into a new key), `row_update` (a map added to a row's list, or a row added),
`row_write` (a row written when the table is rewritten), `rename` (an artifact, a meta or the table renamed into place) and
`link` (an artifact linked into its map's folder), with `hash_block`, `list_read`, `record` (written) and, for a font
directory, `dir_list` and `dir_entry` counting there too.

## The work a change adds

Not in the Totals (the run counted changes nothing); each is the increment on top of the all-hit run, in the same kinds. The
table is rewritten at most once a run, whatever changed: its 477 rows written and one rename, 478.

| change | added | figure here |
|---|---|---|
| a read whose stat moved, content equal | its bytes hashed (140.3 blocks on average) + 1 digest compare + the table rewritten | about 141 + 478 = 619 |
| a read whose content changed | its hash and compare + its map list read (4.73 maps on average) + their entries removed (4.73) + the table rewritten + a miss on each of those sheets | about 141 + 4.73 + 4.73 + 478 + 4.73 x 481 = 2,904 |
| a spec whose stat moved | its bytes hashed (2 or 3 blocks a hamlet, 116 or 127 a compound, 941 to 1,569 a hand sheet) + 1 digest compare (its record is in the entry, not the table) | 3 to 1,570 |
| a miss on a sheet (its engine's work apart) | key folds 3 + R (engine, font set, spec, each read) + row updates R (the map in each read's row) + records written 2 + A (spec, key, artifacts) + renames A + 1 (meta last) + links A: 6 + 2R + 3A | 196 to 269 reads: 407 to 550; 481 on average |
| a miss on a hamlet | key folds 2 + records 4 + renames 3 + links 2 | 11 |
| the Mode A binary rebuilt | all 6 sheets miss, no read re-hashed (their rows hold) and no row changes (the same maps read them) | 2,888 |
| the hamlet binary rebuilt | all 5 hamlets miss | 55 |
| a font file or directory moved | its map list read (6) + 6 entries removed + a directory listed again (about 17 entries) + all 6 sheets miss + the table rewritten | about 6 + 6 + 18 + 2,888 + 478 = 3,396 |
| a cold run (no table, no entries: a fresh clone) | every live map misses; every distinct read and spec hashed once: 41,683 + 5,090 blocks + 396 path-digest blocks + the font directories listed (25 + 422) + every miss 2,943 + the table written 478, on top of the walk and the stats | at most 2,064 + 51,037 = 53,101 |

## Growth

In the input sizes, with M folders (30), D tiers (8), the tree roots (2), N listed entries (146), F file entries (106), K live
maps (11), E engines (2), B the types declaration's blocks (141), the font set's L directories and f files (25, 155), U distinct
reads (297) and sum A artifacts (24):

    all-hit run = (2 + D + M) + N + F + M + D + M + 3 + B + E + 3(L + f) + 3U + 2K + 3K + 3 sum A
                = 40 + 146 + 106 + 30 + 8 + 30 + 3 + 141 + 2 + 540 + 891 + 22 + 33 + 72 = 2,064

(the 3: the types declaration and the table opened, and the lock.) The spec's bytes and the reads per map enter on a change,
not on the all-hit run: a run with c files whose stat moved adds the sum of their blocks (bytes / 64; a spec's 2 to 1,569, a
read's 140.3 on average) and one digest compare each, the table's rewrite once (477 rows + 1), and for each changed read its map
list and the removal of those entries; each map that misses adds (2 + R + [1 on a sheet]) key folds + R row updates +
(2 + A) records + (A + 1) renames + A links (`## The work a change adds`).

Every term is linear in the pool's size: one listing and one kind a folder, one entry check a file, a fixed 5 + 3A a live map,
and 3 a DISTINCT read. The reads term grows with U, not with the maps times their reads: a read shared by several sheets (4.73
now, the modal texts and the research fragments they link) is held once, so as sheets are added U grows only by the paths no
earlier sheet read. The once terms do not grow with the pool. No term multiplies the maps by the engine's sources: the engine is
one build id a run, where today's key re-reads and hashes every engine source for every map (T157's scoping). A pool of twice
the maps at the same mix costs at most about twice the run, and less where the new maps share reads.

## How far over is "far over"

S10 applies: a rebuilt pipeline counting up to twice a tree's line, the excess named and reasonable, is LEEWAY; past twice, OVER.
For scale, priced on the same pool:

- The reads held per entry instead of in the table (the first derivation): 3 x 1,405 + 297 = 4,512 in place of 891, about
  5,685 for the run, 2.8x.
- Each read re-hashed on every run instead of held by its stat: 1,405 x 140.3 blocks, about 197,000 hash blocks, 95x the run.
- Each distinct read hashed once a run (memoized within the run, no stat held): 41,683 blocks, about 20x the run.
- The font set listed every run (its 25 directories and 422 entries) instead of held by its directories' stats: about 370 more.
- The engine keyed on its sources per map instead of its build id: every engine source file read and hashed for each of the 11
  maps, a term growing with the maps times the engine's size.
- The git index read to tell a tracked svg: 28,194 entries a run, about 14x the run.

## Cheaper algorithms considered

- sweep: not used. Nothing is ordered along an axis: the walk visits each directory once in its own order, and the table's rows
  are held independently.
- grid or spatial index: not used. There is no geometry; the table is keyed by path, and a published map's reads find their
  rows by that key, each a `row_update`.
- priority queue: not used. Nothing is ranked: every map is decided, and none is preferred to another.
- incremental update: used. The read table holds each distinct path once with the maps that read it, so the all-hit run holds
  297 rows and not 1,405 records, and a change touches only the row that moved and the entries its map list names; a digest is
  updated only for a file whose stat moved; the table is rewritten only in a run where a row changed (the `work-budget` agent's
  ruling on the first derivation).
- memoizing what a scan does not change: used. Each engine's id once a run, not its sources per map; each distinct read held once
  a run however many maps read it; a file's digest kept with its stat and re-hashed only when the stat moves; the font set held
  by its 25 directories' and 155 files' stats, a directory listed again only when its own stat moved; the types declaration
  read once for every folder's classification.

## Assumptions, and the ones least sure

1. **The table's order and its one writer (least sure).** The shared table is safe by the order in Keeps (3): an entry is removed,
   durably, before the row it depends on records a new digest, and a published map is in its reads' rows (the table written)
   before its meta is renamed. A crash between the two leaves an entry with no meta (a miss next run) or a row still naming a
   removed map (a spurious miss), never a served stale map. Concurrent runs in one clone are not in the contract's Keeps (the
   agent's ruling); the one hazard they would bring - a run rewriting the table from an older read of it and dropping the rows
   another run added for a map it published - is closed by the lock, one a run. A row may keep naming a map that no longer reads
   it (a read the engine dropped); that costs only a spurious miss when the row moves, and the row is not pruned here. A single
   map's check (T221's `make map MAP=<folder|spec>`, or the bundle door asking whether a map is current) reads the table whole
   (477 rows) but holds only the rows naming that map: about 490 a hamlet, 1,240 to 1,390 a sheet.
2. **Stat-held digests are sound.** The all-hit run hashes nothing because a row's size, mtime (ns), ctime and inode hold for the
   file. A tool that rewrites a file in place to the same size within the clock's tick of its hashing is caught by the racy-file
   rule (a file whose mtime is not older than its row is re-hashed); a copy that preserves mtime (a `cp -p` or `rsync -t`)
   changes the ctime and usually the inode, which the row also holds. What it cannot see: a file restored with its old size,
   mtime, ctime and inode, which no ordinary tool does. If the judge or an empirical audit rules stat-holding unsound, the
   fallback is hashing each distinct read once a run: 41,683 blocks more, the run about 21x as costly.
3. **The engine reports every read (a hole found).** The Mode A page writer's read log notes a path only when it is a file
   that exists, so a probe for a file it found ABSENT (a modal text a feature has none of yet) is not a read; creating that file
   later leaves the sheet cached and stale. The key here can only be as complete as the reads reported: the engine owes its
   absent probes as reads too (each a row whose stat is "absent"), or its directory listings. Not fixed here (the brief edits
   nothing else); reported.
4. **The build id identifies the engine.** The GNU build id is a hash over the linked output, present on both binaries today, so
   any change to the engine or anything compiled into it (the hamlet's knobs and tables) moves it. Shared libraries loaded at run
   time are outside it, as the interpreter's installed packages were outside the old key; the system fonts are the one such
   input known to change a map, held as the font rows. A binary built without the note would be hashed whole once a run (21,600
   blocks the hamlet binary, 218,143 the Mode A one, 1,382,384 and 13,961,120 bytes).
5. **The hamlets' reads.** The hamlet binary reads its spec alone today, so a hamlet's key is its build id and spec. When a
   hamlet's page is written again (T222 records it against feature 444's open row), its reads come back: the deleted Python
   writer's records show 168 to 175 a hamlet, 240 distinct paths of which 211 no sheet reads, so the table would grow by about
   211 rows, about 3 x 211 = 633 more on the all-hit run (not the 3 x 854 a per-entry layout would add), and the budget would be
   re-derived for it.
6. **The artifacts per kind.** A hamlet's 2 (the driver svg and json), a generated compound's 3, a hand sheet's 2, from today's
   entries and folders; T221 may rename them, not change their count much. In a clean checkout (renders absent) a hit links the
   24 back and the folders list 72 entries, not 106.
7. **Render-sync is the same run.** Its table and stamp on main are assumed to hold the same rows and records the clone's do, so
   its all-hit run counts the same; the record site's own staleness stamp (T222's "the record site") is not part of this stage.

## Earlier findings

- verdict-1, finding 1: fixed - LOOSE on the per-entry read records (3 x sum R = 4,215 of the first 6,061): the reads are now one
  persistent table of distinct paths, 3 x U = 891, its safety by the order in Keeps (3) and a lock a run; the font set is held by
  its 25 directories' and 155 files' stats as rows of the same table, its 422 entries not listed (the agent's optional note,
  taken: about 370 saved). The run is 2,064, from 6,061.
