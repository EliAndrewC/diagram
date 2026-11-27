#!/bin/bash
# t388: the cause arms, one after another, 20 counted rounds each. Table: t388-causes.tsv
cd "$(dirname "$0")" || exit 1
python3 t388-time.py t388-causes.tsv 20 gp.PreToolUse:only=pair,check-bundle gp.PreToolUse:only=pair,check-bundle+fresh gp.PreToolUse:only=pair,check-bundle+small gp.PreToolUse:only=pair,check-bundle+none gp.PreToolUse:only=pair+shortlog || echo "FAILED gp"
python3 t388-time.py t388-causes.tsv 20 sf.PreToolUse:only=check-bundle,review-round sf.PreToolUse:only=check-bundle,review-round+small sf.PreToolUse:only=check-bundle,review-round+none sf.PreToolUse:only=review-round+fresh || echo "FAILED sf"
python3 t388-time.py t388-causes.tsv 20 rf.PreToolUse:only=check-bundle rf.PreToolUse:only=check-bundle+small rf.PreToolUse:only=check-bundle+none rf.PreToolUse:only=check-bundle+fresh || echo "FAILED rf"
python3 t388-time.py t388-causes.tsv 20 gp.PostToolUse:only=checks gp.PostToolUse:only=checks+small gp.PostToolUse:only=checks+none || echo "FAILED post"
python3 t388-time.py t388-causes.tsv 20 gp.PreToolUse:hook gp.PreToolUse:hook+fresh gp.PostToolUse:hook gp.PostToolUse:hook+small || echo "FAILED hooks"
echo done
