"""The Mode A sibling pairs: two kinds a reader could mistake for each other, and what tells them apart
(feature 262). The page renders each as a LINK in both modals when both kinds are on the map (hover lights the
other, click opens it); the text is the record of the distinction. Symmetric by construction
(`install_siblings`)."""

from __future__ import annotations

PAIRS: dict[tuple[str, str], str] = {}
