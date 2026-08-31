# Feature 175 - the GM's request, VERBATIM

Kept exactly as written (constitution Principle V; `house-style-hooks.sh` leaves this file on the
refusal path so a person decides). Voice-dictated, so "Amazon s three" is S3 and "part of the
future" is "part of the feature" - noted here, NOT corrected above.

## The framing (GM, 2026-08-31), which came first and is the reason the feature exists

> So regardless of whether AWS is slower, it sounds like it may be the case that there is some kind
> of caching that we are doing locally, which AWS might not have. And so rather than just saying
> that AWS is slower, we should note that that means in our current implementation, we're not
> optimizing the AWS code runs as much as we should. And then further optimization is warranted in
> order to get the time down Right?

## The instruction (GM, 2026-08-31)

> Yes. I would like you to implement that feature. Thanks. part of doing the feature would be
> figuring out exactly how much we do want to upload. And, also, I guess, making sure that we don't
> accidentally upload stuff which sticks around forever. You know, like, if we were uploading many
> megabytes worth of content to Amazon s three on every run and then never cleaning it up, then that
> would be bad. And, also, as you say, part of what we're doing will be figuring out exactly what
> needs to go there since some of what we are building up maybe doesn't have to, or maybe it does. I
> don't know. But figuring that out will be part of the future, obviously. please proceed with
> implementing that feature.

## What the GM asked for, itemized - the spec is graded against THIS, not against the plan

1. **Implement the cache** so remote runs stop paying cold-start costs the local runs do not pay.
2. **Figure out exactly how much we want to upload** - a measured answer, not a guess.
3. **Make sure nothing sticks around forever.** Named as the failure to avoid: "uploading many
   megabytes worth of content to Amazon S3 on every run and then never cleaning it up".
4. **Work out what actually needs to go there** - the GM is explicit that they do not know, and that
   determining it is part of the feature: "some of what we are building up maybe doesn't have to, or
   maybe it does. I don't know."

## What the GM did NOT ask for

- Not asked: changing what the gate VERIFIES. This is about not repeating work, never about
  skipping it. A cache that let a remote FULL check less than a local FULL would fail the request.
- Not asked: caching anything beyond what the measurement justifies. Item 4 is a question to answer,
  so shipping "cache everything" would be answering it by assertion.
- Not asked: a second opinion on whether AWS is worth using. The GM has already ruled that the
  slowness is ours to fix ("we're not optimizing the AWS code runs as much as we should").

## The measurement that motivated it (this session, 2026-08-31)

- `.gencache/` is gitignored, 0 tracked entries, and is **221 MB** locally.
- **No `cache:` block exists in any buildspec** (`buildspec/check.yml`, `merge.yml`, `image.yml`).
- CodeBuild `git clone --filter=blob:none` into a fresh container, so every `gencache.gate_obtain`
  that HITs locally MISSES there and regenerates the map for real in a coverage subprocess.
- Recorded remote runs: `full` **18.0 min / $1.44** (2026-08-25, FAILED), `reference` 8.0 min /
  $0.64. Local `make test-full` on 2026-08-31: **~4:10**. Indicative only - the remote figures
  predate this month's efficiency work.
