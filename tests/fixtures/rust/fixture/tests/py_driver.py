"""The fixture module's Python caller (feature 444 T17): what Python reaches through the extension, counted by `rust_checks.py
cover` beside the crate's own tests."""

import l7r_fixture

assert l7r_fixture.stage_total([1, 2, 3]) == 6
