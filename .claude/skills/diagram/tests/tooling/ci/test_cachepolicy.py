"""Feature 175 FR-006 - the lifecycle rule, asserted without an AWS call."""

from __future__ import annotations

import pytest

from l7r.diagram.ci import cachepolicy

pytestmark = pytest.mark.tooling


def test_the_rule_expires_the_cache_prefix_and_nothing_else() -> None:
    """The CI bucket also holds `verified/` - the records a BUILD writes, which are evidence and must
    outlive any cache - plus `go/`, `image/` and the mailbox. A lifecycle rule without a prefix filter
    expires all of them, which would delete the audit trail to save disk. So the filter is the load-
    bearing part of this document, not the expiry."""
    rules = cachepolicy.lifecycle_configuration()["Rules"]
    assert len(rules) == 1, "one rule; a second would need its own prefix argument here"
    rule = rules[0]
    assert rule["Filter"] == {"Prefix": "cache/"}, "the rule MUST be scoped to the cache prefix"
    assert rule["Status"] == "Enabled", "a disabled rule is the same as no rule, and looks configured"
    for evidence in ("verified/", "go/", "image/"):
        assert not evidence.startswith(rule["Filter"]["Prefix"]), f"{evidence} must not fall under the expiry"


def test_objects_expire_and_dead_multipart_uploads_do_too() -> None:
    """The GM's failure is "never cleaning it up", and there are two ways to fail it. The obvious one
    is an object nobody deletes. The quiet one is an ABORTED multipart upload: its parts are billed
    and do not appear in a normal listing, so nobody would ever see them. The cache goes up as a
    multipart at ~110 MB, so this is a real path rather than a hypothetical."""
    rule = cachepolicy.lifecycle_configuration()["Rules"][0]
    assert rule["Expiration"]["Days"] == cachepolicy.EXPIRE_AFTER_DAYS == 30
    assert rule["AbortIncompleteMultipartUpload"]["DaysAfterInitiation"] == 7


def test_the_expiry_outlives_the_gap_between_runs() -> None:
    """WHY 30 AND NOT 7 (spec D3). The rule must not expire a cache still in use: each build rewrites
    its object and resets the clock, so the expiry only has to exceed the gap between builds of the
    SAME scope. At the 24 runs/month this was written under, a week would start expiring live caches
    during a quiet fortnight - turning a warm build cold for nothing - while a quarter would leave an
    abandoned ~110 MB object sitting most of that quarter. This test pins the reasoning to the number
    so that changing one without the other fails."""
    assert cachepolicy.EXPIRE_AFTER_DAYS > 7, "a week expires caches that are merely between builds"
    assert cachepolicy.EXPIRE_AFTER_DAYS <= 30, "past a month an abandoned key is just sitting there"
