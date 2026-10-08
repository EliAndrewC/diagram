"""The CI bucket's WHOLE lifecycle document (feature 175 FR-006; rewritten by feature 177 FR-013).

THE GM'S NAMED FAILURE, which this module exists to make impossible: *"making sure that we don't
accidentally upload stuff which sticks around forever. You know, like, if we were uploading many
megabytes worth of content to Amazon S3 on every run and then never cleaning it up, then that would
be bad."*

**TWO INDEPENDENT GUARDS, because either alone is not enough.**

1. **The key is bounded** (`dispatch.cache_location`): CodeBuild writes one archive per cache
   location, and the location is keyed on (project, scope, registered operation), so the count is
   finite however many builds run. That bounds the COUNT.
2. **These rules bound the AGE.** A bounded count still leaves an ABANDONED key sitting for ever - a
   scope we stop using, a project we rename - and nothing would ever notice, because the thing that
   would notice is a bill nobody reads per-line.

## What feature 177 changed, and why it had to

Feature 175 owned ONE rule and left the bucket's pre-existing catch-all alone:

    expire-ci-junk   Enabled   Filter {'Prefix': ''}   Expiration {'Days': 14}

and then recorded, as an open question it could not settle, that **S3 applies the SHORTEST
expiration among overlapping rules**, so that catch-all also expired **`verified/`** at 14 days.
Those records are what `tree-not-already-verified` reads to skip a build that already passed - so
the optimization that exists to avoid paying twice silently stopped working after a fortnight, and
the same engine content was re-verified at full price. Read back from the bucket on 2026-09-03 with
the admin key, the rule was still live and the oldest `verified/` records (2026-08-25) were nine
days from deletion.

So this module now owns the WHOLE document rather than one rule of it. That is the substantive fix:
`put_bucket_lifecycle_configuration` OVERWRITES, so a module owning one rule of a document it did
not write is a hazard by construction - the previous version had to tell its applier to read first
and merge by ID, which is a procedure someone has to remember rather than a property of the code.

## The four rules, and the horizon each carries

1. **`expire-generation-cache`** - `cache/`, **30 days**. Unchanged from 175, including its reasoning
   (D3): the rule must not expire a cache still in use, each build rewrites its object and resets the
   clock, so the expiry only has to exceed the gap between builds of the same scope. Shorter (7 days)
   would turn a warm build cold during a quiet fortnight for nothing; longer (90) leaves an abandoned
   ~110 MB object most of a quarter. Its multipart abort moved to rule 4, which GENERALIZES it - see
   there; nothing about the cache lost a guard.

2. **`expire-verified-records`** - `verified/`, **365 days**. A verified record is EVIDENCE that a
   paid build passed, and it is ~200 bytes; nine of them exist. It is keyed by engine content, so a
   stale one cannot mislead - the only thing it can do is fail to match. The horizon is therefore
   chosen for what the records are FOR rather than inherited from a rule written for junk: long
   enough that no plausible re-verification window falls outside it, finite so that nothing in this
   bucket is immortal.

3. **`expire-large-objects`** - **`ObjectSizeGreaterThan` 1 MiB, 30 days**. This REPLACES
   `expire-ci-junk`, and the change from a prefix filter to a SIZE filter is the point rather than a
   detail. S3 lifecycle has no negative filter: a rule on prefix `''` cannot be told to skip
   `verified/`, so while the net is expressed as a prefix, "take `verified/` out of its reach" is not
   expressible at all. Expressed as a SIZE, it is - and it lands closer to the GM's words, which are
   about *megabytes*, not about prefixes. Any unforeseen prefix that starts accumulating megabytes is
   caught, and a 200-byte evidence record is not reachable by it at any horizon.

4. **`abort-dead-multipart-uploads`** - prefix `''`, a 7-day multipart abort and **no `Expiration` at
   all**. A dead multipart's parts are billed while invisible in a normal listing: the quietest form
   of the GM's "sticks around forever", and a real path at ~110 MB. 175 guarded it on `cache/` only.
   **This rule exists as a separate rule because S3 REFUSED the alternative**, measured on the live
   bucket 2026-09-03 while applying this very document:

       InvalidRequest: AbortIncompleteMultipartUpload cannot be specified with Object Size.

   which makes sense once stated - an upload still in flight has no final size to filter on. The
   fourth rule is therefore not a workaround but the correct shape, and it is strictly better than
   what it replaces: the abort is now universal rather than cache-only, so a dead multipart under a
   prefix nobody foresaw is caught too. Carrying no `Expiration`, it CANNOT delete an object, so it
   cannot reach `verified/` however long a record sits there - which is why a bare prefix is safe
   here and nowhere else in this document.

**THE LIMITATION THIS ACCEPTS, stated rather than discovered later.** A SMALL object under a prefix
nobody foresaw now has no expiry at all, where the 14-day catch-all would have taken it. The cost is
kilobytes: today that is `go/` (0 objects - the dispatcher and the build both delete their own),
`image/latest.txt` (one object, overwritten in place) and `artifacts/` (5 objects, 0.01 MiB total).
The alternative - keeping a bare-prefix net - puts `verified/` back under a horizon chosen for junk,
which is the defect being fixed. If small objects ever do accumulate, the answer is a fourth rule
with its own prefix, not a return to a net that reaches the evidence.

**A note for whoever tunes these numbers next**: the constants below are now the effective expiry
for their prefixes, which was NOT true of the version this replaces. `cache/` objects are over 1 MiB
so rule 3 also reaches them; both say 30 days, deliberately, so the shortest-overlap rule changes
nothing. Move one and you move the cache's real expiry - which is exactly the trap 175 documented.
"""

from __future__ import annotations

from typing import Any

CACHE_PREFIX = "cache/"
VERIFIED_PREFIX = "verified/"
EXPIRE_AFTER_DAYS = 30
VERIFIED_EXPIRE_AFTER_DAYS = 365
LARGE_OBJECT_BYTES = 1024 * 1024
LARGE_OBJECT_EXPIRE_AFTER_DAYS = 30
RULE_ID = "expire-generation-cache"
VERIFIED_RULE_ID = "expire-verified-records"
LARGE_RULE_ID = "expire-large-objects"
MULTIPART_RULE_ID = "abort-dead-multipart-uploads"
# The rule feature 177 REMOVED. Named here so the applier can say what it is dropping and so a reader
# who finds it still on the bucket knows the document was applied from an older tree.
RETIRED_RULE_ID = "expire-ci-junk"

# A multipart upload that dies mid-flight leaves parts that are billed and invisible in a normal
# listing - the quietest version of the GM's "sticks around forever". ~110 MB goes up as a multipart,
# so this is not hypothetical, and it is the one thing the catch-all this replaces never had. It gets
# its OWN rule (rule 4): S3 refuses `AbortIncompleteMultipartUpload` alongside an object-size filter,
# and an in-flight upload has no final size to filter on, so the two nets cannot be one rule.
ABORT_MULTIPART_AFTER_DAYS = 7


def lifecycle_configuration() -> dict[str, Any]:
    """The `put_bucket_lifecycle_configuration` document for the CI bucket - ALL of it.

    Returned rather than applied so it can be asserted on without an AWS call (Principle X's fixture
    rule) and read in a diff like every other guard here. It is the whole document on purpose: the
    API overwrites, so returning a fragment makes correctness depend on the applier remembering to
    merge."""
    return {
        "Rules": [
            {
                "ID": RULE_ID,
                "Status": "Enabled",
                "Filter": {"Prefix": CACHE_PREFIX},
                "Expiration": {"Days": EXPIRE_AFTER_DAYS},
            },
            {
                "ID": VERIFIED_RULE_ID,
                "Status": "Enabled",
                "Filter": {"Prefix": VERIFIED_PREFIX},
                "Expiration": {"Days": VERIFIED_EXPIRE_AFTER_DAYS},
            },
            {
                "ID": LARGE_RULE_ID,
                "Status": "Enabled",
                # SIZE, not prefix - the only filter S3 offers that can be a net over every future
                # prefix while being structurally unable to reach a 200-byte evidence record.
                "Filter": {"ObjectSizeGreaterThan": LARGE_OBJECT_BYTES},
                "Expiration": {"Days": LARGE_OBJECT_EXPIRE_AFTER_DAYS},
            },
            {
                "ID": MULTIPART_RULE_ID,
                "Status": "Enabled",
                # A BARE PREFIX IS SAFE HERE AND NOWHERE ELSE IN THIS DOCUMENT, because this rule
                # carries no `Expiration`: it can abort an upload that never finished, and it cannot
                # delete an object that did. So it reaches `verified/` and cannot harm it.
                "Filter": {"Prefix": ""},
                "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": ABORT_MULTIPART_AFTER_DAYS},
            },
        ]
    }


def rule(document: dict[str, Any], rule_id: str) -> dict[str, Any]:
    """One rule of a lifecycle document, BY ID.

    Every consumer addresses rules this way rather than by `Rules[0]`, which is what the tests did
    before this feature added a second and a third rule - an index is a claim about ORDER that
    nothing in the document guarantees, and it goes silently wrong the moment the order changes."""
    for r in document.get("Rules", []):
        if r.get("ID") == rule_id:
            return dict(r)
    raise KeyError(rule_id)
