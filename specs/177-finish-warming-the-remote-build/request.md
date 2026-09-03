# Feature 177 - the GM's request, verbatim

## The opening question (2026-09-03)

> I'd like to work on our remote AWS tests.  This is from another session:
>
> [a pasted table of local and remote timings from another session, reproduced in full in the
> session transcript: local `make quick` ~1-2 s selected / ~7 s after an edit / ~10 s ALL=1,
> `make done` 0 s short-circuit / 22 s warm best case / 137 s median of last 25 green / max 334 s,
> `make test-full` ~4:10; remote reference gate green 3 billed min $0.24, operation cold 5 min
> $0.40, operation warm 4 min $0.32, image rebuild 2 min $0.16, three diagnostic failures
> 2+6+1 min $0.72; session total $1.84, month-to-date $16.24; and the note that "the cache buys
> 31 s and one billed minute (-16% / -20%) on that shape."]
>
> So is the cache already implemented?  Like how much caching are we doing?  It sounds like there
> are some questions around how much caching to do and how much savings we get out of it.  Like
> how much faster is it even to run on AWS than locally when we factor in the image rebuild?  Or
> does the image rebuild not matter because it only happens on a dependency change, and the actual
> code itself isn't part of the image?  OR is that not what we're doing but it could be?  I'm
> trying to figure out the current state of things and what improvements we could make to the AWS
> process.

## The instruction that opened this feature (2026-09-03)

> Yes please spec the whole thing as a feature and then implement it, thanks.  Please also include
> item #4 as well as 1-3.  And also include fixing the defect you hit while doing this about
> main-tree-hooks.sh refusing the command its refusal message prescribes.

## What "items 1-4" and "the defect" refer to

The session's answer to the opening question ended with a ranked list of four improvements plus a
separately flagged defect. Reproduced here because the instruction above names them by number, and a
reviewer grading this spec against the request needs the referents:

1. **Cache the `hooks-test` stamp** (-60 s, -39% of the build). "Cheapest, safest, one buildspec
   line plus the set-aside dance in `run.sh`."
2. **Sparse or slim the checkout** (-~40 s). "Bigger win for the whole project than for CI alone."
3. **Take one post-174 remote measurement** - "with 1 and 2 in, a reference gate should land near
   60 s, and we'd finally have the FULL-scope comparison."
4. **Two things already flagged and never resolved:** "`expire-ci-junk` (prefix `''`, 14 days) also
   expires `verified/`, so skip-verified silently stops working after a fortnight and the same
   content gets re-verified at full price; and 175's FULL-scope cache timing (~92 MiB payload) is
   still owed."

**The defect:** "`main-tree-hooks.sh` refuses `( cd <clone> && <write> )`, the exact form its own
refusal message prescribes, when the session is standing in main. Its `LEAVES` regex doesn't accept
`(` as a command position, so the subshell never counts as leaving."

## The measurements the answer rested on

Taken 2026-09-03 from the CodeBuild phase records, the CloudWatch log of build `03c8ce13` (the last
green remote reference gate, 2026-08-31), and clone timings run in this container.

- The green reference build, 154 s total: PROVISIONING 16 s, DOWNLOAD_SOURCE 0 s (S3 cache restore,
  2.78 MiB), **INSTALL 43 s (the `git clone --filter=blob:none`)**, BUILD 94 s, POST_BUILD 1 s.
  Inside BUILD: wait-go/merge 2 s, lint/format/typecheck 4 s, reference roll 2 s (roll-cache HIT),
  **`hooks-test` 60 s**, pytest 26 s (2444 tests, 36 workers).
- A `--filter=blob:none` clone of this repository from GitHub, measured in this container:
  **66 s**. `--depth=50`: 52 s. `--filter=blob:limit=200k`: 45 s. **Sparse, excluding
  `wip/` and `legacy-hand-authored-pool/`: 4.0 s.**
- The checked-out tree at HEAD is **465.8 MB over 2,102 files**, of which 441 MB is 91 generated
  files: 264.0 MB of `.html` (29 files), 115.2 MB of `.svg` (31), 61.9 MB of `.png` (31). The
  largest single tracked file is a 26.0 MB `.svg`; seven `wip/*.html` are 12-17 MB each.
- Every remote number on record **predates feature 174**: build `03c8ce13`'s own log says
  `coverage floors: deferred to make done FULL=1`. The local green `make done` median since
  2026-08-31 is **227.5 s** (n=12, min 22, max 622).
