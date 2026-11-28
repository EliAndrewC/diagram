#!/usr/bin/env bash
# t563: can a tmpfs mounted in a user+mount namespace host the tests as uid 1000 (read-only refusal kept, exec allowed, git works)?
D=/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t563-nsdir
mkdir -p "$D"
unshare -Urm sh -c "mount -t tmpfs -o size=64m,mode=1777 tmpfs $D && unshare --map-user=1000 --map-group=1000 -U sh -c '
id; ls -ld $D
touch $D/x && chmod 444 $D/x
(echo hi > $D/x) 2>/dev/null && echo WROTE || echo REFUSED
mkdir $D/e && cp /bin/true $D/e/t && $D/e/t && echo EXEC_OK
git -C $D init -q r && echo GIT_OK
'"
ls -la "$D"
