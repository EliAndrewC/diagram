"""Feature 175 FR-006 and feature 177 FR-013/FR-014 - the lifecycle document, asserted without an AWS call.

WHAT CHANGED, and why these tests had to change with it. Until feature 177 this module owned ONE
rule and these tests pinned that: `len(rules) == 1`, `Rules[0]`, and a docstring assertion demanding
the module keep naming the 14-day catch-all as the effective expiry. All three were correct then and
all three block the fix now - 177 makes the module own the WHOLE document, retires that catch-all,
and takes `verified/` out of any net's reach. The invariant is still CLOSED (it is not "and `.git`
is allowed too"): exactly three rules, named, each addressed BY ID.
"""

from __future__ import annotations

import pytest

from l7r.diagram.ci import cachepolicy

pytestmark = pytest.mark.tooling


def _doc() -> dict:
    return cachepolicy.lifecycle_configuration()


def test_the_document_is_exactly_these_four_rules_and_nothing_else() -> None:
    """The CLOSED invariant. `put_bucket_lifecycle_configuration` OVERWRITES the whole document, so
    what this function returns is what the bucket gets - a fifth rule appearing here is a change to
    live infrastructure and must be deliberate."""
    ids = [r["ID"] for r in _doc()["Rules"]]
    assert ids == [cachepolicy.RULE_ID, cachepolicy.VERIFIED_RULE_ID, cachepolicy.LARGE_RULE_ID, cachepolicy.MULTIPART_RULE_ID]
    assert cachepolicy.RETIRED_RULE_ID not in ids, "expire-ci-junk is retired; it is what expired the evidence"
    for r in _doc()["Rules"]:
        assert r["Status"] == "Enabled", "a disabled rule is the same as no rule, and looks configured"


def test_the_cache_rule_expires_the_cache_prefix() -> None:
    """175's rule, with its multipart abort GENERALIZED into rule 4 rather than removed."""
    r = cachepolicy.rule(_doc(), cachepolicy.RULE_ID)
    assert r["Filter"] == {"Prefix": cachepolicy.CACHE_PREFIX}
    assert r["Expiration"]["Days"] == cachepolicy.EXPIRE_AFTER_DAYS == 30


def test_dead_multipart_uploads_are_aborted_EVERYWHERE_and_that_rule_can_delete_nothing() -> None:
    """The GM's failure is "never cleaning it up" and there are two ways to fail it: an object nobody
    deletes, and an ABORTED multipart whose parts are billed and do not appear in a normal listing.
    The cache goes up as a multipart at ~110 MB.

    THIS IS A SEPARATE RULE BECAUSE S3 REFUSED THE ALTERNATIVE, measured on the live bucket while
    applying this document: `AbortIncompleteMultipartUpload cannot be specified with Object Size` -
    an upload in flight has no final size to filter on. The result is better than the arrangement it
    replaces: 175 aborted multiparts under `cache/` only, and this reaches every prefix.

    And it may carry a bare prefix precisely because it has NO `Expiration`: it can abort an upload
    that never finished and cannot delete an object that did, so it reaches `verified/` harmlessly.
    That absence is load-bearing, so it is asserted rather than assumed."""
    r = cachepolicy.rule(_doc(), cachepolicy.MULTIPART_RULE_ID)
    assert r["Filter"] == {"Prefix": ""}, "the multipart net is universal"
    assert r["AbortIncompleteMultipartUpload"]["DaysAfterInitiation"] == cachepolicy.ABORT_MULTIPART_AFTER_DAYS == 7
    assert "Expiration" not in r, "an Expiration here would put verified/ back under a bare-prefix net - the whole defect"


def test_the_cache_expiry_still_outlives_the_gap_between_runs() -> None:
    """WHY 30 AND NOT 7 (175's D3), pinned to the number so changing one without the other fails."""
    assert cachepolicy.EXPIRE_AFTER_DAYS > 7, "a week expires caches that are merely between builds"
    assert cachepolicy.EXPIRE_AFTER_DAYS <= 30, "past a month an abandoned key is just sitting there"


def test_the_evidence_is_not_expired_by_a_rule_written_for_junk() -> None:
    """FEATURE 177, FR-013 - the GM's item 4. `verified/` records are what
    `tree-not-already-verified` reads to avoid paying for a build that already passed. Under the old
    document a bare-prefix catch-all took them at 14 days, so after a fortnight the same engine
    content was re-verified at full price. Their horizon is now chosen for what they ARE."""
    r = cachepolicy.rule(_doc(), cachepolicy.VERIFIED_RULE_ID)
    assert r["Filter"] == {"Prefix": cachepolicy.VERIFIED_PREFIX}
    assert r["Expiration"]["Days"] == cachepolicy.VERIFIED_EXPIRE_AFTER_DAYS == 365
    assert cachepolicy.VERIFIED_EXPIRE_AFTER_DAYS > 14, "14 days is the defect, not the fix"
    assert cachepolicy.VERIFIED_EXPIRE_AFTER_DAYS >= 12 * cachepolicy.EXPIRE_AFTER_DAYS, "evidence outlives an optimization by an order of magnitude"


def test_nothing_can_accumulate_for_ever_and_the_net_cannot_reach_the_evidence() -> None:
    """FR-014 and the reason the net is a SIZE rather than a prefix.

    S3 has no negative filter, so a rule on prefix `''` cannot be told to skip `verified/` - and S3
    applies the SHORTEST overlapping expiration, so such a net IS the evidence's horizon whatever
    else the document says. Expressed as a size it is not, and it lands closer to the GM's own words:
    *"if we were uploading many megabytes worth of content to Amazon S3 on every run and then never
    cleaning it up, then that would be bad."*"""
    r = cachepolicy.rule(_doc(), cachepolicy.LARGE_RULE_ID)
    assert "Prefix" not in r["Filter"], "a prefix net would reach verified/ - that is the defect being fixed"
    assert r["Filter"] == {"ObjectSizeGreaterThan": cachepolicy.LARGE_OBJECT_BYTES}
    assert r["Expiration"]["Days"] == cachepolicy.LARGE_OBJECT_EXPIRE_AFTER_DAYS
    assert "AbortIncompleteMultipartUpload" not in r, "S3 refuses the combination; rule 4 owns multiparts"
    # A verified record is ~200 bytes; the cache archive measured 2.78 MiB. The net must sit between
    # them by a wide margin in both directions, or it is either useless or dangerous.
    assert 1024 < cachepolicy.LARGE_OBJECT_BYTES < 2_500_000


def test_the_net_does_not_secretly_shorten_the_cache() -> None:
    """The trap 175 documented, applied to this document's own two overlapping rules: `cache/`
    objects are over 1 MiB, so the size net reaches them too and the SHORTEST wins. They agree at 30
    deliberately - move one and you move the cache's real expiry."""
    assert cachepolicy.LARGE_OBJECT_EXPIRE_AFTER_DAYS == cachepolicy.EXPIRE_AFTER_DAYS


def test_a_rule_is_addressed_by_id_and_a_missing_one_is_loud() -> None:
    """`Rules[0]` is a claim about ORDER that nothing in the document guarantees; it is what these
    tests used to do, and it is why adding a rule broke them."""
    assert cachepolicy.rule(_doc(), cachepolicy.LARGE_RULE_ID)["ID"] == cachepolicy.LARGE_RULE_ID
    with pytest.raises(KeyError):
        cachepolicy.rule(_doc(), "no-such-rule")


def test_the_module_documents_the_state_that_is_now_TRUE() -> None:
    """The old version of this test demanded the docstring keep naming `expire-ci-junk` and
    `SHORTEST` as live facts. Both statements are now false - the rule is retired - so the assertion
    is RE-PINNED rather than deleted: the docstring must still carry the overlap hazard (it applies to
    this document's own two 30-day rules) and must record what was retired and why."""
    doc = cachepolicy.__doc__ or ""
    assert "SHORTEST" in doc, "the S3 overlap rule still decides two of these three rules"
    assert cachepolicy.RETIRED_RULE_ID in doc, "a reader who finds the retired rule still on the bucket must be able to look it up"
    assert "verified/" in doc and "365" in doc, "the horizon chosen for the evidence, and its reasoning, live here"
    assert "no negative filter" in doc, "why the net is a size rather than a prefix is the whole design"
