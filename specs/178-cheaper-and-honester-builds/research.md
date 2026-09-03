# Feature 178 - research

## R1 - The per-minute rates, VERIFIED against actual billing (FR-015)

The AWS Pricing API returns nothing with these credentials (`get_products` on `AWSCodeBuild` yields
0 products, no error - presumably `pricing:GetProducts` is not granted). Cost Explorer is the better
instrument anyway: a price list says what AWS charges in general, and this says what THIS ACCOUNT was
charged. Read with the `[aws_admin]` key, 14 days to 2026-09-03:

| day | usage type | minutes | cost | derived rate |
|---|---|---|---|---|
| 2026-08-24 | `g1.xlarge` | 2.0 | $0.1596 | **$0.0798/min** |
| 2026-08-25 | `g1.2xlarge` | 18.0 | $3.6000 | **$0.2000/min** |
| 2026-08-25 | `g1.medium` | 5.0 | $0.0500 | **$0.0100/min** |
| 2026-08-25 | `g1.xlarge` | 130.0 | $10.3740 | $0.0798/min |
| 2026-08-31 | `g1.medium` | 2.0 | $0.0200 | $0.0100/min |
| 2026-08-31 | `g1.xlarge` | 22.0 | $1.7556 | $0.0798/min |
| 2026-09-03 | `g1.xlarge` | 69.0 | $5.5062 | $0.0798/min |

**`config.RATES` is accurate**: `XLARGE` 0.08 against a billed 0.0798 (0.25% high, and rounding UP is
the safe direction for an estimate the GM reads before spending), `2XLARGE` 0.20 exact, `MEDIUM` 0.01
exact. **`LARGE` (`g1.large`, 0.02) has never been billed in this account and is therefore
UNVERIFIED** - item 5's own measurement will produce the first row for it, and this table is where the
check gets closed.

Source: AWS Cost Explorer `get_cost_and_usage`, `SERVICE = CodeBuild`, grouped by `USAGE_TYPE`, read
2026-09-03. Not a published price list - the account's own invoice lines.

## R2 - A CORRECTION to feature 177's reported spend

Feature 177's closing report told the GM *"$7.44 across eight builds"*. **The true figure is $5.51.**
Cost Explorer for 2026-09-03 shows 69.0 billed minutes at $5.5062, and the six builds that day account
for exactly 69 minutes: `19ff1147` 1, `cf341865` 9, `3937fe7c` 15, `9f760907` 8, `76087221` 24,
`ab43bfac` 12. The per-build figures reported were each correct; the total was added wrong, and no
record carried the error - it was stated in conversation only.

The lesson is the one this repository already applies to timings: a number that can be read off an
artifact should be, rather than accumulated by hand. `make ci-status` sums the run log for exactly
this reason, and the run log agrees with the invoice.

## R3 - The purge, REHEARSED (FR-011, T30)

A throwaway mirror clone of `EliAndrewC/diagram`, `git filter-repo` with a filename callback, then
`reflog expire` + `gc --prune=now --aggressive`. Nothing of this repository was touched.

| | before | after |
|---|---|---|
| pack size | **345.71 MiB** | **38.68 MiB** |
| objects in pack | 36,801 | 36,412 |
| clone from GitHub | 25.8 s | (measurable only after the real push) |

**An 89% reduction.** Note the object COUNT barely moves - 389 fewer - which is the shape of the
problem: the renders were few and enormous, not many and small. That is also why the earlier estimate
built from HEAD would have been wrong in the useful direction: 441 MB is what HEAD carries, and
history holds every superseded version of the same files.

**A callback, not `--path-glob`, and that mattered.** The renders lived at different paths before
feature 161's per-map reorganization and before the `tests/` reorganization. A path list built from
HEAD would have missed them, leaving the bytes in history while appearing to succeed. The census
across all history found **179 generated paths ever added**, including `test_fixtures/ochiba-*.svg`
and a flat `pool/magistracies/ubame-magistracy.svg` that exist at neither of those paths today.

**The 13 survivors are exactly the two classes FR-010a names**: 5 magistracy `.svg` (Mode A hand-drawn
source) and 8 `tests/fixtures/*-red.svg` (hand-broken negative fixtures the gate reads at twelve call
sites). Nothing generated survived.

**One classification the rehearsal forced, which round 4 flagged as unclassified (its aside A4)**:
`pool/magistracies/ochiba-roundtrip-test/ochiba-roundtrip-test.svg` was KEPT by the
`magistracies/`-and-`.svg` rule. It should be kept deliberately or not at all - see D4.

## R4 - The `.gitignore`'s Mode A exception is STALE, and the spec repeated it

The GM asked what `ochiba-roundtrip-test` is. Its own notes answer plainly: *"the OUTPUT of feeding
the EXISTING hand-authored Ochiba's real program ... back through the perimeter-first placer"*, a
*"scaffold/test artifact"*, carrying its own regenerate command. Generated output, so it goes.

**But checking it forced the same question about the other four, and the answer is the same.** The
root `.gitignore` un-ignores `pool/magistracies/*/*.svg` with this reason:

    The one exception inside the live tree: a Mode A compound plan has no generator that draws it
    from data - its .svg IS the source, KB-sized - so magistracy .svg stays tracked...

**Every one of the five HAS a generator that draws it, and every one reproduces byte-for-byte.**
Regenerated through `make map` and compared by MD5:

| magistracy | md5 before | after |
|---|---|---|
| county-magistracy-example | 28a853de… | 28a853de… |
| hayakawa-magistracy | 0c1e126a… | 0c1e126a… |
| ochiba-magistracy | 2ae706eb… | 2ae706eb… |
| ochiba-roundtrip-test | 44484ab2… | 44484ab2… |
| ubame-magistracy | a5640b10… | a5640b10… |

`git diff --stat` over `pool/magistracies/` is empty after regenerating all five. The SOURCE is the
`.gen.py`; the `.svg` is its output. So under the GM's rule - *"in general, the generated html pages
should not be tracked just like the generated svg and png files should not be tracked"* - all five are
generated `.svg` and are untracked with everything else.

**The spec asserted the opposite and I should say why that happened.** FR-010a called them "tracked
SOURCE" and cited the `.gitignore` comment as its evidence - and its own last sentence demands
*"Membership MUST be shown per path, not asserted."* I quoted a comment instead of running the
generator. Round 3 had already corrected a size figure in that same FR for the same reason.

**What this changes downstream, and it is self-correcting**: `render_cache.is_cache_managed` decides
Mode A from Mode B by asking `git check-ignore` - *"a generator's svg is cache-managed iff it is
gitignored"*. Once these are ignored they become cache-managed and stamped like every other derived
render, which is the behavior their generators already deserve. The mechanism reads gitignore rather
than a list, so nothing else has to be told.

**The survivors are now ONE class, not two**: the eight `tests/fixtures/*-red.svg`, hand-broken by a
person to prove a check fires, with no generator anywhere. That is a cleaner rule than the one the
spec started with - no generated render is tracked, full stop.
