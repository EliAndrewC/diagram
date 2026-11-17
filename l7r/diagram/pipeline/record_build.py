"""The record's site, built on the main checkout when - and only when - something it is built from changed (feature 301).

The GM, 2026-10-01: *"I do want these files to end up on main. Like on the main checkout, I mean, just not checked into
main ... that's the same thing that we are doing with our generated map files ... when something lands on the main, then
we regenerate ... if they would change, but we do not regenerate them otherwise."* So render-sync calls this after the
map renders (`render_cache.main`), on the map renders' model: a STAMP of every input, written beside the site, and a
build only when the stamp differs (spec FR-010).

A FORWARDER since feature 449 T148 (phase 4's S5, `ask:449-phase4-slices`): the stamp and the build are the Rust's,
`l7r-gate record site-stale` (`rust/gate/crates/research/src/record/site/write.rs`), the site's one writer (FR-003). It
stays for its one importer, `render_cache.py`, and goes with it in S12.
"""

from __future__ import annotations

import os
import subprocess


class RecordBuildError(RuntimeError):
    """The Rust build refused or failed: its words, as the Python build's uncaught refusal stopped render-sync."""


def rebuild_if_stale(skill_dir: str) -> bool:
    """Build the site when its stamp differs from its inputs; True when it built."""
    gate = os.path.join(skill_dir, "scripts", "gates", "l7r-gate.sh")
    done = subprocess.run([gate, "record", "site-stale", "--root", skill_dir], capture_output=True, text=True, check=False)
    if done.returncode != 0 or done.stdout.strip() not in ("rebuilt", "fresh"):
        raise RecordBuildError(done.stderr.strip() or done.stdout.strip() or f"l7r-gate record site-stale exited {done.returncode}")
    return done.stdout.strip() == "rebuilt"
