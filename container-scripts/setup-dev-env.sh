#!/bin/bash
# Install every dependency this repo needs, INSIDE the dev container. Idempotent - safe to re-run.
#
#   container-scripts/setup-dev-env.sh          install anything missing, then verify
#   container-scripts/setup-dev-env.sh --check  verify only (fast, no network), exit 1 if anything is missing
#
# Run this on a fresh container, and any time something that used to work stops working with a
# "command not found" / "No module named" / "resvg not found" error. A container rebuild does NOT
# preserve apt or pip state (only the bind-mounted repo and ~/.claude survive), so a rebuilt
# container looks subtly broken until this has run: the symptom on 2026-07-25 was three diagram
# tests failing because `resvg` had vanished, which cost a full gate run to diagnose.
#
# This lives in container-scripts/, NOT scripts/. scripts/ is for things run OUTSIDE the container
# (launch-container.sh creates the container; sync-with-main.sh is run by a session but manages the
# host-side clone/main relationship). Anything here assumes it is running inside the container and
# may freely apt-get install.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECK_ONLY=0
[ "${1:-}" = "--check" ] && CHECK_ONLY=1

in_container() { [ -f /run/.containerenv ] || [ -f /.dockerenv ]; }

if ! in_container && [ "${SETUP_ALLOW_HOST:-}" != 1 ]; then
    echo "ERROR: this installs system packages and is meant to run INSIDE the dev container."
    echo "Start one with scripts/launch-container.sh, then run this from the repository root."
    echo "(Override on a machine you are sure about: SETUP_ALLOW_HOST=1)"
    exit 1
fi

# ---- what "installed" means, as testable facts ------------------------------------------------
# Each is (label, test command). The SAME list drives --check and the post-install verification, so
# the script can never report success for something it did not actually establish.
ITALIC_FONT=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf
check_all() {
    local bad=0
    _t() { # label, test
        if eval "$2" >/dev/null 2>&1; then
            [ "$CHECK_ONLY" = 1 ] && echo "  ok      $1"
        else
            echo "  MISSING $1"
            bad=1
        fi
    }
    # the diagram renderer. resvg is required (no rsvg-convert fallback - see diagram/SKILL.md for
    # the profile), and the DejaVu ITALIC face matters because resvg does not synthesize oblique:
    # without it every italic map label silently renders upright.
    _t "resvg (diagram PNG renderer)"            "command -v resvg"
    _t "DejaVu Serif italic face"                "[ -f $ITALIC_FONT ]"
    # the engine's runtime deps (feature 131: THIS repository's lockfiles under the skill, beside
    # pyproject.toml - the webapp's cherrypy/playwright set stayed in gm-assistant with the webapp).
    # shapely backs the /diagram seam-closing pass (waterfields/seams.py) - the one place the
    # field engine needs real polygon booleans, so a missing wheel breaks map generation, not a test
    _t "python: shapely (diagram field engine)"  "python3 -c 'import shapely'"
    _t "python: pillow (render_cache, crop_map)" "python3 -c 'import PIL'"
    # dev deps - the quality gate itself
    _t "python: pytest + cov + xdist"            "python3 -c 'import pytest, pytest_cov, xdist'"
    _t "python: ruff mypy"                       "python3 -m ruff --version; python3 -m mypy --version"
    # the claude() wrapper that appends this repo's standing authorizations to the system prompt.
    # ~/.bashrc is NOT on a bind mount (only the repo and ~/.claude survive a rebuild), so this has
    # to be re-established on every fresh container exactly like the apt and pip state.
    _t "claude() system-prompt wrapper"          "grep -qF 'gm-assistant append-system-prompt' $HOME/.bashrc"
    return $bad
}

if [ "$CHECK_ONLY" = 1 ]; then
    echo "checking dev environment..."
    if check_all; then
        echo "dev environment OK"
        exit 0
    fi
    echo
    echo "run container-scripts/setup-dev-env.sh (no arguments) to install the missing pieces"
    exit 1
fi

# ---- install ----------------------------------------------------------------------------------
# Passwordless sudo is available in this container precisely so a session can install what it needs
# without asking. Never work around a missing dependency - install it.
echo "==> system packages (apt)"
if ! command -v resvg >/dev/null 2>&1 || [ ! -f "$ITALIC_FONT" ]; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq resvg fonts-dejavu-core fonts-dejavu-extra
else
    echo "    already present"
fi

echo "==> python packages (pip)"
# --break-system-packages: this container's python is the system python and there is no venv by
# design (the skill's tools and its gate share one interpreter). The lockfiles live beside the
# skill's pyproject.toml (feature 131): the first session in the split repository found this line
# still reading webapp/requirements.txt from gm-assistant, which does not exist here, so a fresh
# container could not be provisioned at all.
SKILL="$REPO/.claude/skills/diagram"
pip install --quiet --break-system-packages \
    -r "$SKILL/requirements.txt" \
    -r "$SKILL/requirements-dev.txt"

# ---- the claude() wrapper ----------------------------------------------------------------------
# WHY a system-prompt append and not a CLAUDE.md line: CLAUDE.md sits BELOW the system prompt in the
# instruction hierarchy, so Claude Code's default "do not call the Agent tool unless the user
# requested it" outranks this project's own mandate to run a review subagent before declaring work
# done. On 2026-07-27 that silently suppressed the required settlement-review pass on three city
# maps - nothing broke and nothing warned, the mandate just lost. --append-system-prompt lands
# after that line with the same authority. The TEXT lives in container-scripts/append-system-prompt.md
# (version-controlled and reviewable); this only installs the loader.
echo "==> claude() system-prompt wrapper"
# rewrite rather than append-if-absent, so editing the block below actually reaches an existing container
touch "$HOME/.bashrc"
if grep -qF '>>> gm-assistant append-system-prompt >>>' "$HOME/.bashrc"; then
    sed -i '/# >>> gm-assistant append-system-prompt >>>/,/# <<< gm-assistant append-system-prompt <<</d' "$HOME/.bashrc"
fi
cat >> "$HOME/.bashrc" <<'BASHRC_BLOCK'
# >>> gm-assistant append-system-prompt >>>
# Appends this repo's standing authorizations to every session's system prompt.
# Edit the text in container-scripts/append-system-prompt.md - this only loads it.
claude() {
    # THIS repo's copy, wherever the repo is mounted (feature 131): the wrapper is per container,
    # and each repository's container mounts it at its own workdir.
    local _asp="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/container-scripts/append-system-prompt.md"
    if [ -r "$_asp" ]; then
        command claude --append-system-prompt "$(cat "$_asp")" "$@"
    else
        command claude "$@"
    fi
}
# <<< gm-assistant append-system-prompt <<<
BASHRC_BLOCK
echo "    installed - takes effect in NEW shells (or run: source ~/.bashrc)"

echo "==> verifying"
if check_all; then
    echo
    echo "dev environment ready. Next: cd .claude/skills/diagram && make quick"
    echo "(from a .clones/<session> workspace, never main; \`make map\` first on a fresh clone so"
    echo "the reference hamlet has a render for the pool-artifact tests to check)"
else
    echo
    echo "ERROR: something is still missing after install - see MISSING lines above"
    exit 1
fi
