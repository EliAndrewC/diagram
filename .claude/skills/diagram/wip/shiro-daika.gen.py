#!/usr/bin/env python3
"""Shiro Daika - the DOMAIN CAPITAL of the Daika house (diagram skill, Mode B, 1px = 3ft).

THE DRIVER ONLY. The map itself is `wip/shiro_daika/`, split out by feature 173 when the ~1,000-line
bar became a gate (constitution Principle X clause 13): at 1,592 lines this was the second-largest
file in the skill, and 346 of its statements are drawing calls at module level, so it is the one
member of that split that is a linear SCRIPT rather than a library.

The parts execute in order at import, each importing from the one above it. Read
`wip/shiro_daika/CLAUDE.md` for which part holds what; a session resuming feature 021's housing work
loads `housing.py` and `civic.py` and none of the rest.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import shiro_daika  # noqa: E402,F401 - importing it DRAWS the map, part by part
