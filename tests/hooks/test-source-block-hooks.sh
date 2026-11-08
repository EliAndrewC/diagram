#!/usr/bin/env bash
# Tests for source_block_hooks.rs. Run: tests/hooks/test-source-block-hooks.sh   (exit 0 = all green)
#
# TWO DIRECTIONS, always (the project's standing rule for a guard): it must FIRE on the case it
# exists to catch, and STAY QUIET on correct work. The second half is the one that matters most -
# every guard in this repo that fired on legitimate work taught a session to reach for the escape,
# which is the habit these guards exist to break.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$HERE/guard-cases.sh" source_block_cases
