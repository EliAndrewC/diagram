# T01 evidence - the semantic index built, timed and asked the trial's 17 questions

Run 2026-10-29/30 on this machine (22 cores, the build held to half of them), BGE-M3's 8-bit build (`Xenova/bge-m3`,
`onnx/model_int8.onnx`).

## 1. The cost

**The build** - `/usr/bin/time -v make semantic-index`, started 2026-10-29T15:34:07Z, ended 2026-10-30T00:16:29Z:

```
semantic-index: 261 shard(s) written
semantic-index: committed and pushed
	Elapsed (wall clock) time (h:mm:ss or m:ss): 8:42:22
	Percent of CPU this job got: 1097%
	Maximum resident set size (kbytes): 2846436
	Exit status: 0
```

120,669 passages (the archive's texts and the record's pages, 900 characters at most), so about 231 a minute over the whole run
(the 15-minute readings of `si-progress.py` reported to the GM in the session, not kept: their running averages since the start went from 110 to 232 a minute, the machine shared with other containers). Committed to the archive as
`d8881575 the semantic index (Xenova/bge-m3-int8): 261 shard(s) - 00, 01, 02, 03, 04, 05, 06, 07 ...`.

**The size on disk** - `du -sb .specify/source-archive/semantic-index/bge-m3-int8`: 288,338,260 bytes (275 MiB) in 261 shards, the
largest `gm-copies.npz` at 27 MB (under GitHub's 100 MB file limit).

**An update** - `time make semantic-index` with nothing changed, then `time make semantic-index SHARD=record-04`:

```
semantic-index: 0 shard(s) written
real	0m3.026s
semantic-index: 0 shard(s) written
real	0m2.388s
```

Three seconds to fingerprint the whole corpus and find nothing to do, the model loaded included. A changed passage costs its
embedding beside that, at the build's rate about a quarter of a second each: a record page's edit of a few passages is seconds, a
new capture of 50 passages about 15 seconds.

**A search** - `time make semantic-find Q="有田の登り窯の長さ" K=3`, end to end:

```
0.564  97/97072989a527/20261002T155209Z/text.txt [5299:5877]
0.563  b5/b597771536b4/20261002T162509Z/text.txt [2:902]
0.558  97/97072989a527/20261002T155209Z/text.txt [0:893]
real	0m3.515s
```

In-process (`deep.py`, the model loaded once; its two timings printed once on 2026-10-30 and not kept in `deep-out.json`): embedding a question 0.012 s; loading all 261 shards 0.62 s; a whole `find` 0.73 to
1.45 s (`trial.py`'s `seconds`, below), because `find` reloads every shard on each question. So a command-line search is about 3.5
s, nearly all of it loading the model and the shards. With both already loaded (`warm.py` beside the spec, every shard stacked into
one matrix):

```
load and stack 2.5 (120669, 1024)
warm search 0.024
warm search 0.099
warm search 0.059
```

So a search kept loaded (a long-running helper, which does not exist) would take under a tenth of a second. The rule is judged on
the command a session runs today: `make semantic-find`, 3.5 s.

## 2. The comparison

`python3 specs/447-semantic-index/trial.py research/trial-out.json` (25.7 s for all 17, 1.0 GB peak). Each question's answering
capture is known from the record (the capture the record page's footnote cites). `text` is today's search with the English terms a
session would try first (every term required, as `make archive-find` does), `hits` the folders it returns, unranked; `sem` the
capture's rank among the index's first ten passages; `page` the record page's rank there.

| # | question (answer's language) | text terms | hits | text holds it | sem | page |
|---|---|---|---|---|---|---|
| 1 | fish ponds of a dike-pond district (en) | fish pond, depth | 12 | yes | 7 | 1 |
| 2 | moat of a Chinese county town (en) | moat, width | 44 | yes | 10 | 1 |
| 3 | water a hard-working horse needs (en) | horse, water | 106 | yes | 1 | 4 |
| 4 | Japanese earthen compound walls (en) | earthen wall | 17 | yes | 2 | 3 |
| 5 | a ditch across a slope (en) | ditch, slope | 34 | yes | 6 | 1 |
| 6 | Beijing's alleys between lanes (en) | alley, Beijing | 27 | yes | 1 | 8 |
| 7 | bridges along a canal towpath (en) | towpath, bridge | 3 | yes | 2 | 6 |
| 8 | the first torii on an approach (en) | torii, first | 15 | yes | 5 | 1 |
| 9 | labor of ramie cloth (en) | ramie, labour | 5 | yes | - | 3 |
| 10 | pigs beneath the privy (en) | pig, toilet | 15 | yes | - | 1 |
| 11 | Edo back-row tenement alleys (ja) | alley, tenement | 6 | no | - | - |
| 12 | a farmhouse's threshing yard (ja) | threshing yard, mat | 0 | no | - | 1 |
| 13 | Edo's public bathhouses (ja) | bathhouse, Edo | 5 | no | - | 1 |
| 14 | cedars of a Tonami grove (ja) | cedar, Tonami | 5 | no | - | 5 |
| 15 | Arita's climbing kilns (ja) | climbing kiln, Arita | 2 | no | - | 1 |
| 16 | draining the paddy before harvest (ja) | drain, harvest | 78 | no | - | 1 |
| 17 | a Matsue samurai house (ja) | Matsue, samurai | 3 | no | - | 10 |

**Deeper, and in Japanese** - `python3 specs/447-semantic-index/deep.py research/deep-out.json`: each question's capture by rank in
the first 200 passages (and by file, a file's passages counted once), and the seven Japanese-answered ones asked again in Japanese:

| # | asked in English: passage / file | asked in Japanese | Japanese question: passage / file |
|---|---|---|---|
| 9 | 24 / 10 | | |
| 10 | 11 / 9 | | |
| 11 | - / - | 江戸の裏長屋の路地の幅はどれくらいか | 1 / 1 |
| 12 | - / - | 農家の庭(脱穀場)の広さはどう決められたか | - / - |
| 13 | 58 / 37 | 江戸時代後期の江戸に銭湯はいくつあったか | 1 / 1 |
| 14 | - / - | 砺波の散居村の屋敷林に杉は何本あるか | 15 / 9 |
| 15 | - / - | 有田の登り窯の長さ | 2 / 2 |
| 16 | 41 / 23 | 稲刈りの何日前に田の水を落とすか | 1 / 1 |
| 17 | - / - | 松江の武家屋敷の主屋の広さ | 8 / 5 |

**Today's search in Japanese**, for the same seven, two terms each, every term required (the shell loop of this session, `grep
-rlIF --include=*.txt` over the archive):

```
67/67dc5aaf3516 路地 長屋 hits=28 holds=yes
05/052e5a087064 庭 脱穀 hits=15 holds=yes
3e/3e64bd55f251 銭湯 江戸 hits=32 holds=yes
4a/4a0919d8aa81 屋敷林 砺波 hits=32 holds=yes
b5/b597771536b4 登り窯 有田 hits=5 holds=yes
f4/f4285e6ee539 落水 稲刈 hits=0 holds=no
3c/3c4a00e776c7 武家屋敷 松江 hits=19 holds=yes
```

## 3. What it shows

- **English question, English source** (1-10): today's search held every answer, among 3 to 106 unranked folders (median 16). The
  index put the answering capture in its first ten on 8 of 10, first or second on 4, and the record page that answered it in its
  first ten on all 10. It found nothing today's search missed; it RANKED what today's search found.
- **English question, Japanese source** (11-17): today's search in English found none of the seven, as it cannot. Neither did the
  index: none in its first ten, two in its first 200 (ranks 41 and 58). An English question is matched by English passages first,
  and the archive's English text crowds the Japanese out. What it did find is the record page that already answered six of the
  seven - but a past question's page is what a new question would not have.
- **Japanese question, Japanese source**: the index put the capture first on 3 of 7 and in its first fifteen on 6. Today's search
  in Japanese held 6 of 7, among 5 to 32 folders. The one it missed (16, 落水 and 稲刈: the source has 落水 five times but says 収穫
  and 刈り取り for the harvest, never 稲刈) the index ranked first.

## 4. The rule, applied

**Not met: the trial is set down by its rule.** Its three tests:

- Finds passages today's search missed on a fair share of the questions - NO: one of 17 (16), and that one a term-choice miss
  that a second try with the source's own words (収穫, 刈り取り) would have caught. The cross-language reach the trial was built to
  test - an English question finding a Japanese passage - was not there: none of seven in the first ten.
- An update in seconds - YES: 3 s with nothing changed, about a quarter of a second for each passage changed.
- A search under a second - NO from the command line (`make semantic-find`, 3.5 s); yes only kept loaded (0.02 to 0.1 s), which no
  tool does today.

Not part of the rule, recorded for the GM: on the ten English questions the index RANKED what today's search found - the answer
first or second of ten on four, where the text search returned 3 to 106 folders unranked.

## 5. What each search hands a session to read (asked by the GM 2026-10-30: token use)

One-shot, 2026-10-30: each of the 17 questions through `make archive-find TERMS="<the trial's English terms>"` and `make
semantic-find Q="<the question>" K=10`, the characters each printed (a token is about four English characters, about one
Japanese one). `archive-find` names files and their download history, no passage; `semantic-find` prints ten passages' opening
words. "answer in it" is whether the answering capture is among the ten.

```
2b/2b106432097b en archive-find    9946 chars,  12 files | semantic-find   3506 chars, answer in it: True
5c/5c56a8ffcc30 en archive-find   39691 chars,  44 files | semantic-find   3609 chars, answer in it: True
7e/7ea522445c8c en archive-find  113039 chars, 106 files | semantic-find   3199 chars, answer in it: True
6e/6e2b3e8f080c en archive-find   21712 chars,  17 files | semantic-find   3190 chars, answer in it: True
1d/1d6eded5f7e6 en archive-find   54213 chars,  34 files | semantic-find   3383 chars, answer in it: True
fd/fd80f6d7ed33 en archive-find   20445 chars,  26 files | semantic-find   3190 chars, answer in it: True
71/71b5f74369cc en archive-find     947 chars,   3 files | semantic-find   3148 chars, answer in it: True
1e/1e4316f6bb18 en archive-find   13522 chars,  15 files | semantic-find   3370 chars, answer in it: True
42/4288c884928c en archive-find    9896 chars,   5 files | semantic-find   3416 chars, answer in it: False
f4/f4eeeca27b8b en archive-find   30400 chars,  15 files | semantic-find   3249 chars, answer in it: False
67/67dc5aaf3516 ja archive-find   13212 chars,   6 files | semantic-find   3649 chars, answer in it: False
05/052e5a087064 ja archive-find     187 chars,   1 files | semantic-find   3204 chars, answer in it: False
3e/3e64bd55f251 ja archive-find    5508 chars,   5 files | semantic-find   3457 chars, answer in it: False
4a/4a0919d8aa81 ja archive-find    2964 chars,   4 files | semantic-find   3429 chars, answer in it: False
b5/b597771536b4 ja archive-find     628 chars,   2 files | semantic-find   3252 chars, answer in it: False
f4/f4285e6ee539 ja archive-find   99533 chars,  78 files | semantic-find   3424 chars, answer in it: False
3c/3c4a00e776c7 ja archive-find     773 chars,   2 files | semantic-find   3489 chars, answer in it: False
```

The text search printed 187 to 113,039 characters (median 13,212) before a session opens any file; the index printed 3,148 to
3,649 every time, the passage text included. What a session then reads to reach the answer is not measured here.
