#!/usr/bin/env bash
# Tests for readme-hooks.sh (constitution XVII).
# Run: tests/hooks/test-readme-hooks.sh   (exit 0 = all green)
#
# TWO DIRECTIONS, as every guard in this repo must have. Section 2 matters most: the make-only hook
# had to learn the mention-versus-invocation lesson FOUR times (a grep, a commit message, a docstring,
# a fixture name), so this one is born knowing it - READING a README, or naming one in a git command,
# must never be blocked.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# GUARD_EDIT_OK: feature 168 - this guard records its firings now, so the suite writes its fixtures to
# a throwaway log rather than into the census `make audit` reads.
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
# GUARD_EDIT_OK: 2026-09-26 - stderr is captured in a file of THIS run's own, not a fixed /tmp path that every
# concurrent hooks-test (one per session's gate) rewrote under the others (it failed the batching suite's greps).
HOOK_ERR=$(mktemp)
trap 'rm -rf "$GUARD_LOG_ROOT" "$HOOK_ERR"' EXIT
HOOK="$HERE/readme-hooks.sh"
PASS=0; FAIL=0

tool_ev() { jq -nc '{"tool_name":$ARGS.positional[0],"tool_input":{"file_path":$ARGS.positional[1]}}' --args -- "$1" "$2"; }
bash_ev() { jq -nc '{"tool_name":"Bash","tool_input":{"command":$ARGS.positional[0]}}' --args -- "$1"; }
bash_at() { jq -nc '{"tool_name":"Bash","cwd":$ARGS.positional[1],"tool_input":{"command":$ARGS.positional[0]}}' --args -- "$1" "$2"; }
# 451 T67: the tree a Bash write is judged against, pinned - a command's relative paths resolve where its event stands (else in
# this tree), so a case means the same in a clone, the mirror or a detached worktree
export CLONE_MAIN=/repo

check() { # label expected payload
  local rc; printf '%s' "$3" | "$HOOK" pretool >/dev/null 2>"$HOOK_ERR"; rc=$?
  if { [ "$2" = ok ] && [ "$rc" -eq 0 ]; } || { [ "$2" = blocked ] && [ "$rc" -ne 0 ]; }; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else echo "  FAIL    $1 (expected $2, rc=$rc)"; FAIL=$((FAIL+1)); fi
}

echo "1. IT FIRES on any attempt to WRITE a README"
check "Write tool"                 blocked "$(tool_ev Write /repo/README.md)"
check "Edit tool"                  blocked "$(tool_ev Edit /repo/dev/README.md)"
# EVERY SPELLING, because the GM enumerated them and a case-insensitive flag is an assertion until
# it is tested. A later "tidy-up" of the regex that dropped re.I would pass every other case here.
check "README (no extension)"      blocked "$(tool_ev Write /repo/README)"
check "readme"                     blocked "$(tool_ev Write /repo/readme)"
check "Readme"                     blocked "$(tool_ev Write /repo/Readme)"
check "ReadMe"                     blocked "$(tool_ev Write /repo/ReadMe)"
check "readme.md"                  blocked "$(tool_ev Write /repo/readme.md)"
check "ReadMe.md"                  blocked "$(tool_ev Write /repo/ReadMe.md)"
check "Readme.MD"                  blocked "$(tool_ev Write /repo/Readme.MD)"
check "README.rst"                 blocked "$(tool_ev Write /repo/README.rst)"
check "README.txt"                 blocked "$(tool_ev Write /repo/README.txt)"
check "readme.markdown"            blocked "$(tool_ev Write /repo/readme.markdown)"
check "redirect"                   blocked "$(bash_ev 'cat > docs/README.md')"
check "append"                     blocked "$(bash_ev 'echo x >> docs/README.md')"
check "sed -i"                     blocked "$(bash_ev 'sed -i s/a/b/ dev/README.md')"
check "cp onto one"                blocked "$(bash_ev 'cp a.md dev/README.md')"

echo
echo "2. IT STAYS QUIET - reading, searching and versioning a README are all fine"
check "reading one"                ok "$(bash_ev 'cat README.md')"
check "grepping one"               ok "$(bash_ev 'grep -n rule dev/perf-log/README.md')"
check "git log on one"             ok "$(bash_ev 'git log --oneline README.md')"
check "writing a CLAUDE.md"        ok "$(tool_ev Write /repo/dev/CLAUDE.md)"
check "writing a normal doc"       ok "$(bash_ev 'cat > docs/session-clones.md')"
check "a filename merely starting readme-ish" ok "$(tool_ev Write /repo/readme-hooks-notes.md)"

echo
echo "3. THE REFUSAL SAYS WHERE TO PUT IT INSTEAD"
printf '%s' "$(tool_ev Write /repo/README.md)" | "$HOOK" pretool >/dev/null 2>"$HOOK_ERR" || true
if grep -q "CLAUDE.md in the directory it governs" "$HOOK_ERR"; then
  echo "  ok      names the alternative"; PASS=$((PASS+1))
else echo "  FAIL    refusal does not say where knowledge belongs"; FAIL=$((FAIL+1)); fi
# GUARD_EDIT_OK: a regression check for a defect fixed 2026-09-27 - the message's backticks were a command
# substitution in an unquoted heredoc, so the refusal RAN `make audit` and printed its output instead.
if grep -qF '`make audit` shows it' "$HOOK_ERR" && ! grep -q "Gate runs" "$HOOK_ERR"; then
  echo "  ok      the message names \`make audit\` literally and does not run it"; PASS=$((PASS+1))
else echo "  FAIL    the refusal ran \`make audit\` (or lost its name) - a backtick in an unquoted heredoc"; FAIL=$((FAIL+1)); fi

echo
echo "4. THE GM MAY DELEGATE ONE EDIT (2026-09-06): README_OK with a reason permits, a bare token does not"
check "README_OK with a reason"    ok "$(bash_ev 'sed -i s/a/b/ research/README.md  # README_OK: the GM authorized this link-table update on 2026-09-06')"
check "README_OK bare"             blocked "$(bash_ev 'sed -i s/a/b/ research/README.md  # README_OK')"
check "README_OK merely grepped"   blocked "$(bash_ev 'grep README_OK scripts/hooks/readme-hooks.sh && cat > docs/README.md')"
check "README_OK on the Edit tool (no command to carry a reason)" blocked "$(tool_ev Edit /repo/research/README.md)"

echo
echo "5. THE DESTINATION A COMMAND WRITES, IN THE TREE - never a name it merely holds (451 T67)"
C=/repo/.clones/c
# the refusal that filed T67 (2026-11-21, T58's builder), its first segments verbatim: the copy's destination /tmp/t58/readme.keep
# is a README by name, outside the tree
check "the logged cp of a hook's source to /tmp" ok "$(bash_at "cd /tmp/t58/wt && cp rust/guard/src/guards/readme_hooks.rs /tmp/t58/readme.keep && printf '\n#[allow(dead_code)]\nconst T58_PROBE: u8 = 0;\n' >> rust/guard/src/guards/readme_hooks.rs && cp /tmp/t58/readme.keep rust/guard/src/guards/readme_hooks.rs" "$C")"
check "a copy whose source is a README"           ok "$(bash_at 'cp -p docs/README.md /tmp/x.md' "$C")"
check "a copy whose source is named readme_hooks.rs" ok "$(bash_at 'cp rust/guard/src/guards/readme_hooks.rs rust/guard/x.rs' "$C")"
# 2026-11-17: the sed script names a README; the file it edits is a test's
check "sed -i whose script names a README"        ok "$(bash_at "sed -i 's/(README 1, docs 2)/(README 1)/' rust/x/tests.rs" "$C")"
# 2026-10-10: a scratch repository's README, in /tmp
check "a README in a /tmp scratch repository"     ok "$(bash_at "d=/tmp/scratch/livetest && mkdir -p \$d && cd \$d && git init -q && printf 'x\n' > README && git add README" "$C")"
check "a README's write as a heredoc's text"      ok "$(bash_at "$(printf "cat > docs/notes.md <<'EOF'\nwrite it with cat > docs/README.md\nEOF")" "$C")"
# 2026-10-30: a program writing a test whose triple-quoted text writes a fixture README
check "a program's triple-quoted text names one"  ok "$(bash_at "$(printf "python3 - <<'EOF'\nimport pathlib\ng = pathlib.Path('tests/t.py')\ng.write_text('''(tmp / \"README.md\").write_text(\"notes\")''')\nEOF")" "$C")"
check "git add of one"                            ok "$(bash_at 'git add README.md' "$C")"
check "a file tool's README outside the tree"     ok "$(tool_ev Write /tmp/scratch/README.md)"
check "a file tool's README in a clone"           blocked "$(tool_ev Edit "$C/research/README.md")"
# 2026-11-07, its shape: the one real Bash write the log holds in full, a README beside the parked stages, from rust/phases
check "a heredoc onto ../parked/README.md"        blocked "$(bash_at "$(printf "git rm -q tests/py_driver.py; cat > ../parked/README.md <<'EOF'\n# Parked Rust stages\nEOF")" "$C/rust/phases")"
check "cp onto one in a clone, absolute"          blocked "$(bash_at "cp /tmp/x.md $C/docs/README.md" /tmp)"
check "cp onto one after a cd into the tree"      blocked "$(bash_at "cd $C && cp /tmp/x.md docs/README.md" /tmp)"
check "a python program writing one"              blocked "$(bash_at "python3 -c \"import pathlib; pathlib.Path('docs/README.md').write_text('x')\"" "$C")"
check "a README past a variable never set"        blocked "$(bash_at 'echo x > $NEVER_SET_T67/README.md' "$C")"
check "rm of one (a README is the GM's to write)" blocked "$(bash_at 'rm docs/README.md' "$C")"
check "a git command's redirect onto one"         blocked "$(bash_at 'git show HEAD:a.md > docs/README.md' "$C")"
check "a shell's -c program writing one"          blocked "$(bash_at "bash -c 'echo x > docs/README.md'" "$C")"
check "a copy from one to a variable never set"   ok "$(bash_at 'cp docs/README.md $NEVER_SET_T67/x.md' "$C")"
check "a program comparing a name to one"         ok "$(bash_at "$(printf "python3 - <<'EOF'\nif name == 'README.md':\n    open('out.txt', 'w').write('x')\nEOF")" "$C")"
# a one-line string holding a README's write is the program's text, as the triple-quoted one is
check "a program's one-line string text names one" ok "$(bash_at "$(printf "python3 - <<'EOF'\nimport pathlib\npathlib.Path('t.py').write_text('(tmp / \"README.md\").write_text(1)')\nEOF")" "$C")"

echo
echo "6. A COPY OF THIS PROJECT ANYWHERE IS THE TREE, known by what the directory is, never by its path (451 T67)"
# a mirror whose origin is a neutral URL (the rule reads the mirror's own, never a written one), a clone in it, and outside both:
# a builder's worktree of the clone (T58's and T11's /tmp/t58/wt), a clone of the clone, a clone of that, a repository whose
# origin is the mirror's by another scheme, a file:// clone - and, not copies, a repository whose origin only shares the mirror's
# prefix, a scratch repository of its own (2026-10-10's `git init` in a /tmp scratchpad) and a directory in no repository
P=$(mktemp -d); trap 'rm -rf "$GUARD_LOG_ROOT" "$HOOK_ERR" "$P"' EXIT
g() { git -c user.email=t@t -c user.name=t -c init.defaultBranch=main "$@" >/dev/null 2>&1; }
g init "$P/main" && g -C "$P/main" remote add origin https://example.invalid/owner/project && g -C "$P/main" commit --allow-empty -m base
g clone "$P/main" "$P/main/.clones/c" && g -C "$P/main/.clones/c" worktree add --detach "$P/t58/wt"
g clone "$P/main/.clones/c" "$P/copy" && g clone "$P/copy" "$P/copy2"
g init "$P/gh" && g -C "$P/gh" remote add origin git@example.invalid:owner/project.git
g init "$P/sibling" && g -C "$P/sibling" remote add origin https://example.invalid/owner/project-research
g clone "file://$P/main" "$P/fileclone"
g init "$P/scratch"; mkdir -p "$P/plain"
# the fixture is git's own: a case passing because a repository failed to appear would pass for nothing
for f in main/.git/config t58/wt/.git copy/.git copy2/.git gh/.git sibling/.git fileclone/.git scratch/.git; do
  if [ -e "$P/$f" ]; then PASS=$((PASS+1)); else echo "  FAIL    the fixture's $f is missing"; FAIL=$((FAIL+1)); fi
done
in_p() { CLONE_MAIN="$P/main" check "$@"; }
in_p "a README written in a builder's worktree, after a cd"   blocked "$(bash_at "cd $P/t58/wt && printf 'x\n' > docs/README.md" "$P/main/.clones/c")"
in_p "... by its absolute path"                                blocked "$(bash_at "cp /tmp/x.md $P/t58/wt/README.md" /tmp)"
in_p "... standing in it"                                      blocked "$(bash_at 'echo x > README' "$P/t58/wt")"
in_p "... by a file tool"                                      blocked "$(tool_ev Write "$P/t58/wt/research/README.md")"
in_p "... by a python program standing in it"                  blocked "$(bash_at "python3 -c \"open('README.md', 'w').write('x')\"" "$P/t58/wt")"
in_p "a README in a clone of a clone outside the tree"         blocked "$(bash_at "echo x > $P/copy/docs/README.md" /tmp)"
in_p "... and in a clone of that"                              blocked "$(bash_at "echo x > $P/copy2/README.md" /tmp)"
in_p "a README in a repository whose origin is the mirror's"   blocked "$(bash_at "echo x > $P/gh/README.md" /tmp)"
in_p "a README in a file:// clone of the mirror"               blocked "$(bash_at "echo x > $P/fileclone/README.md" /tmp)"
in_p "a README in a repository whose origin shares a prefix"   ok "$(bash_at "echo x > $P/sibling/README.md" /tmp)"
# a work tree the command itself makes is not on disk when the guard reads: judged by what it is a work tree of
in_p "a README in a worktree the same command adds"            blocked "$(bash_at "git worktree add --detach $P/t99/wt && cd $P/t99/wt && echo x > README.md" "$P/main/.clones/c")"
in_p "a README in a clone of a clone the same command makes"   blocked "$(bash_at "git clone -q $P/main/.clones/c $P/new && echo x > $P/new/README.md" /tmp)"
# the plan review's (b)3c, round 2: a work tree the command makes holds only the READMEs under its place, so T67's own cp beside it
# passes while a README in it, by its path or after a cd, is refused; a clone of this repository likewise
in_p "the logged cp beside a worktree the same command adds"   ok "$(bash_at "git worktree add /tmp/t58/wt && cp rust/guard/src/guards/readme_hooks.rs /tmp/t58/readme.keep" "$P/main/.clones/c")"
in_p "a README in that worktree, by its path"                  blocked "$(bash_at "git worktree add /tmp/t58/wt && echo x > /tmp/t58/wt/README.md" "$P/main/.clones/c")"
in_p "... after a cd into it"                                  blocked "$(bash_at "git worktree add /tmp/t58/wt && cd /tmp/t58/wt && echo x > README.md" "$P/main/.clones/c")"
in_p "a README in a clone of this repository the command makes" blocked "$(bash_at "git clone $P/main /tmp/x && echo x > /tmp/x/README.md" /tmp)"
in_p "... and one written elsewhere outside it"                ok "$(bash_at "git clone $P/main /tmp/x && echo x > /tmp/y/README.md" /tmp)"
in_p "a README in a worktree a shell's -c program adds"        blocked "$(bash_at "bash -c 'git worktree add /tmp/t58/wt && echo x > /tmp/t58/wt/README.md'" "$P/main/.clones/c")"
in_p "... and the write after the program"                     blocked "$(bash_at "bash -c 'git worktree add /tmp/t58/wt' && echo x > /tmp/t58/wt/README.md" "$P/main/.clones/c")"
in_p "a README in a worktree whose place is a variable"        blocked "$(bash_at "d=/tmp/t58 && git worktree add \$d/wt && echo x > \$d/wt/README.md" "$P/main/.clones/c")"
in_p "... the logged cp beside it"                             ok "$(bash_at "d=/tmp/t58 && git worktree add \$d/wt && cp rust/guard/src/guards/readme_hooks.rs \$d/readme.keep" "$P/main/.clones/c")"
in_p "a clone of a variable's source with no directory"        blocked "$(bash_at "S=$P/main && git clone \$S && echo x > main/README.md" /tmp)"
in_p "a place the walk cannot resolve fails closed"            blocked "$(bash_at "git worktree add \$NEVER_SET_T67/wt && echo x > /tmp/y/README.md" "$P/main/.clones/c")"
# a commit message naming the clone step is no clone: T67's own cp after it still passes
in_p "a commit message naming clone, then the logged cp"       ok "$(bash_at "git commit -qm 'the clone step' && cp rust/guard/src/guards/readme_hooks.rs /tmp/t58/readme.keep" "$P/main/.clones/c")"
# the corpus's shape (2026-11, twice): a scratch clone of a bare repository of its own, in a mktemp directory
in_p "a README in a scratch clone the same command makes"      ok "$(bash_at "d=\$(mktemp -d -p $P) && cd \$d && git init -q --bare remote.git && git clone -q remote.git seed; cd seed; echo seed > README" "$P/main/.clones/c")"
in_p "a README in a scratch repository of its own"             ok "$(bash_at "cd $P/scratch && printf 'x\n' > README && git add README" "$P/main/.clones/c")"
in_p "a README in a directory in no repository"                ok "$(bash_at "echo x > $P/plain/README.md" /tmp)"
in_p "a file tool's README in the scratch repository"          ok "$(tool_ev Write "$P/scratch/README.md")"
# 2026-10-10, the entry's whole command (its `command` field), in a scratchpad `git init` repository: not a copy
in_p "the 2026-10-10 command, whole"                           ok "$(bash_at "d=$P/scratchpad/livetest && rm -rf \$d && mkdir -p \$d/specs/399-live-test && cd \$d && git init -q && printf 'x\\n' > README && git add README && git -c user.email=t@t -c user.name=t commit -qm base && printf '# 399\\n\\n**Status**: Filed\\n' > specs/399-live-test/spec.md && git add specs; echo \"exit \$?\"" "$P/main/.clones/c")"

echo
echo "passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
