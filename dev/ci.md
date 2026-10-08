# The CodeBuild dispatcher - the measurement route, the threat model and the `verified/` write path

**Load this file when:** you are changing `make ci-measure`, the buildspecs or the bucket policy, or judging whether a
new remote route or condition opens a way for a session to buy a paid run it should not have. The package index and
the conditions are [`l7r/diagram/ci/CLAUDE.md`](../l7r/diagram/ci/CLAUDE.md).

## The MEASUREMENT route (feature 177)

`make ci-measure` (add `FULL=1` for the full-scope pair). It exists because the cost of the remote gate could not be
measured otherwise: `route-is-gated` is evaluated for every mode, `delta.is_engine()` excludes `ci/` by the GM's own
FR-025 ruling, and a feature about the build's own cost touches no engine path. A debt payable only by waiting for
unrelated engine work is not a debt anyone pays.

**It bypasses exactly one condition - `route-is-gated` - and the row is still printed, saying so.** Everything else
refuses it: `green-local-since-edit` (the GM's own named case: never a paid run straight after a red gate),
`remote-enabled` (feature 132's switch), `breaker-not-tripped` (the monthly hard stop) and, for FULL,
[`door.py`](../l7r/diagram/ci/door.py)'s committed `permitted` entry. A verified record does NOT short-circuit it,
because a record says a gate PASSED and says nothing about what it cost.

**It cannot mint a push credential, and that refusal lives in the tree the build runs.**
[`buildspec/measure.yml`](../buildspec/measure.yml) sets `MODE: measure`, and [`run.sh`](../buildspec/run.sh) returns
before writing `verified/<key>.json` - which puts it before the push as well. A dispatcher flag would be a promise; a
buildspec is a diff, which is the bar `door.py` set for the FULL prompt. Its cache block and install phase are
otherwise IDENTICAL to `check.yml`'s: a measurement that ran cold while the gate runs warm would measure something
that does not happen.

It is paid and prompted, in the same class as `make ci-image` - it cancels by default and logs to `dev/bypass-log/`,
so `make audit` can tell a session's answer from the GM's. **Detach it**: a foreground run dies at the 2-minute tool
timeout while the BUILD keeps going, leaving no run-log entry.

## The threat model

Same shape as feature 127's: **a session that wants the paid run and should not have it**, and that can present any
of these as diligence -

- dispatching a docs-only or merged-in-from-main delta (condition 1 - the delta is computed, never declared);
- merging an unfinished feature because the gate is green (condition 2);
- `make done` again straight after a red one, with an edit in between (condition 3, the GM's named case);
- answering the FULL prompt from inside a build via an environment variable (the door reads only a committed entry -
  a forgery is a tracked-file diff);
- a session answering its own prompt through a pseudo-terminal: `spec-fidelity` ruled this an EXCEPTION on
  2026-08-25, and the GM authorized it in their own words later that day. A session that answers MUST record in the
  reason that it did, quoting the authorization - the entry is how `make audit` tells a session's answer from the
  GM's.

## The `verified/` write path (R8, FR-016)

The bucket policy in [`buildspec/verified-deny-policy.json`](../buildspec/verified-deny-policy.json) denies
`s3:PutObject` under `verified/` to every principal except `gm-assistant-codebuild-role`. Applied with the admin key on
2026-08-25 and verified: the session key gets `AccessDenied` there and still writes `go/`. Only a build can write a
verified record.
