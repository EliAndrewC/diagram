"""The lifecycle rule that stops the generation cache accumulating (feature 175, FR-006).

THE GM'S NAMED FAILURE, which this module exists to make impossible: *"making sure that we don't
accidentally upload stuff which sticks around forever. You know, like, if we were uploading many
megabytes worth of content to Amazon S3 on every run and then never cleaning it up, then that would
be bad."*

**TWO INDEPENDENT GUARDS, because either alone is not enough.**

1. **The key is bounded** (`dispatch.cache_location`): CodeBuild writes one archive per cache
   location, and the location is keyed on (project, scope), so the cache can ever hold FOUR objects
   however many builds run. That bounds the COUNT.
2. **This rule bounds the AGE.** A bounded count still leaves an ABANDONED key sitting for ever - a
   scope we stop using, a project we rename - and nothing would ever notice, because the thing that
   would notice is a bill nobody reads per-line. So objects under the cache prefix expire.

**WHY 30 DAYS** (spec D3, a reasoned choice rather than a measured one - labeled a GUESS, per
constitution XII, because the record has no number to find). The rule must never expire a cache that
is still in use, and must not leave an abandoned one indefinitely. Remote runs are infrequent - 24 in
the month this was written - so a live scope is rebuilt well inside 30 days, and each rebuild rewrites
the object and resets its clock. An abandoned key therefore disappears about a month after the last
build that touched it. Shorter (7 days) would start expiring live caches during a quiet fortnight,
turning a warm build cold for no reason; longer (90 days) leaves a stale ~110 MB object most of a
quarter. If remote runs become rare enough that a month passes between builds of the same scope, the
cost of being wrong is one cold build, not a failure - the cache is an optimization (FR-007).

**SCOPED TO THE CACHE PREFIX, AND NOTHING ELSE.** The CI bucket also holds `verified/` (the records a
build writes, which are evidence), `go/` (build release signals), `image/` (the custom-image marker)
and the mailbox. A rule without a prefix filter would delete all of them. The prefix is asserted in
`tests/tooling/ci/test_cachepolicy.py`.

**THE 30 DAYS ABOVE IS NOT THE EFFECTIVE EXPIRY, and the reason is worth knowing before anyone tunes
it.** When this rule was applied (2026-08-31) the bucket already carried a catch-all:

    expire-ci-junk   Enabled   Filter {'Prefix': ''}   Expiration {'Days': 14}

**S3 applies the SHORTEST expiration among overlapping rules**, so a cache object actually dies at 14
days, not 30, and changing the constant above alone will not move it. That rule was PRESERVED rather
than replaced - `put_bucket_lifecycle_configuration` overwrites the whole document, so the applying
script reads first and merges by rule ID.

**This rule still earns its place at 14 days**: the catch-all has no `AbortIncompleteMultipartUpload`,
and a dead multipart's parts are billed while invisible in a normal listing - the quietest form of the
GM's "sticks around forever", and a real path at ~110 MB.

**Two open questions for the GM, raised and NOT decided here** (they concern a rule that reaches
prefixes this feature does not own):

1. 14 days may expire a cache that is merely between builds during a quiet fortnight - the exact
   argument used above to reject a 7-day expiry. The cost is one cold build, not a failure (FR-007).
2. `expire-ci-junk` also expires **`verified/`** at 14 days. Those records are what
   `tree-not-already-verified` reads to avoid paying for a build that already passed, so after a
   fortnight the same engine content is re-verified at full price. That may well be deliberate; it is
   recorded here because nothing else in the repository mentions it.
"""

from __future__ import annotations

from typing import Any

CACHE_PREFIX = "cache/"
EXPIRE_AFTER_DAYS = 30
RULE_ID = "expire-generation-cache"


def lifecycle_configuration() -> dict[str, Any]:
    """The `put_bucket_lifecycle_configuration` document for the CI bucket's cache prefix.

    Returned rather than applied so it can be asserted on without an AWS call (Principle X's fixture
    rule) and read in a diff like every other guard here."""
    return {
        "Rules": [
            {
                "ID": RULE_ID,
                "Status": "Enabled",
                "Filter": {"Prefix": CACHE_PREFIX},
                "Expiration": {"Days": EXPIRE_AFTER_DAYS},
                # A multipart upload that dies mid-flight leaves parts that are billed and invisible
                # in a normal listing - the quietest version of the GM's "sticks around forever".
                # ~110 MB goes up as a multipart, so this is not hypothetical.
                "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7},
            }
        ]
    }
