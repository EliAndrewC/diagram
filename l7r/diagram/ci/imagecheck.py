"""Is the pushed CodeBuild image still built from the tree's current recipe? (feature 175)

**THE DEFECT THIS EXISTS FOR, measured 2026-08-31.** The ECR image was built on 2026-08-25. Feature
142 replaced mypy with pyrefly on 2026-08-28 and updated `Dockerfile.ci` accordingly - line 26 has
verified `pyrefly --version` ever since. But `make ci-image` is a PAID, prompted target, so the image
itself was never rebuilt, and **every remote build failed at `typecheck` with Error 127 for three
days**. The gated push route was broken for every session in the container.

It could not have been noticed: remote was switched off on 2026-08-25 and stayed off the whole time
pyrefly existed, so the first dispatch after turning it back on was also the first chance to see it.

**THE CLASS OF BUG, which is the reusable part.** The image is a DERIVED ARTIFACT built from files in
this repository, but it lives in ECR with no link back - so editing the recipe cannot invalidate the
build, and nothing anywhere fails until someone spends money. This repository has met the same shape
three times in a week: gitignored path literals that stopped matching after a layout change, a phantom
`check_village/` directory that kept a deleted import resolving, and this. **A derived artifact whose
staleness nothing detects will go stale, and the detector has to be written deliberately.**

**HOW IT IS DETECTED, without changing the marker format.** `buildspec/image.yml` already writes
`image/latest.txt` as `<GIT_SHA> <timestamp>`, so the marker knows which commit the image was built
from. The image's inputs are the recipe and the two lockfiles it COPYs. If any of those differ between
that commit and HEAD, the pushed image no longer matches the tree. No rebuild is needed to adopt this -
the existing marker already carries what it needs.

**IT WARNS, IT DOES NOT REFUSE.** A stale image is usually harmless (a comment edit, a base-image note)
and rebuilding costs about a dollar of the GM's money on a prompted target that is theirs to authorize.
Refusing every dispatch until someone pays would be worse than the disease. What was missing was not a
block but the KNOWLEDGE - the three-day outage was a session having no way to be told.
"""

from __future__ import annotations

#: What the image is built from. `Dockerfile.ci` is the recipe; the two lockfiles are what it COPYs
#: into the venv (`COPY .claude/skills/diagram/requirements.txt ... requirements-dev.txt /tmp/req/`).
#: If the COPY list in the Dockerfile grows, this grows with it - `tests/tooling/ci/test_imagecheck.py`
#: derives the expected set from the Dockerfile rather than trusting this tuple.
IMAGE_INPUTS = (
    "Dockerfile.ci",
    ".claude/skills/diagram/requirements.txt",
    ".claude/skills/diagram/requirements-dev.txt",
)


def marker_commit(marker: str | None) -> str | None:
    """The commit the pushed image was built from, or None when the marker is absent or unreadable.

    The marker is `<GIT_SHA> <timestamp>`; anything else is treated as unknown rather than raising,
    because a malformed marker must not take the dispatcher down - it is a diagnostic, not a gate."""
    if not marker:
        return None
    head = marker.strip().split()
    if not head:
        return None
    sha = head[0]
    return sha if len(sha) >= 7 and all(c in "0123456789abcdef" for c in sha.lower()) else None


def stale_inputs(changed_paths: list[str]) -> list[str]:
    """Which of the image's inputs appear in `changed_paths` (the diff since the marker's commit)."""
    return sorted({p for p in changed_paths if p in IMAGE_INPUTS})


def staleness_line(stale: list[str]) -> str | None:
    """The one line a session should see, or None when the image is current.

    Names the FILES rather than saying "the image is old", because which file changed decides whether
    it matters: a lockfile means the build's Python differs from the tree's, which is the outage this
    module was written for; the Dockerfile alone may be a comment."""
    if not stale:
        return None
    return f"image STALE: {', '.join(stale)} changed since the image was built - `make ci-image` rebuilds it (~$0.16, prompts). A build may fail on a tool the tree expects and the image lacks."
