#!/bin/sh
# A `then:` step between groups (feature 269): merge main into the clone so the next session sees what the other
# research sessions landed. Prints nothing (queues no briefs). A conflict is aborted and the queue carries on.
C=/diagram/.clones/diagram-supplemental
[ -z "$(git -C $C status --porcelain --untracked-files=no)" ] || exit 0
git -C $C pull -q --no-rebase --no-edit origin main >/dev/null 2>&1 || git -C $C merge --abort >/dev/null 2>&1
exit 0
