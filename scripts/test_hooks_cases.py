#!/usr/bin/env python3
"""Case tables for the three guards added by the 2026-08-24 enforcement audit.

WHY ONE FILE FOR THREE HOOKS. The older suites are each a bash script of `check` lines, which suits a
hook whose input is a single command string. These three take structured tool payloads - file paths,
edit anchors, whole file contents - and expressing those in bash quoting was the larger half of the
work with none of the value. The `test-<name>-hooks.sh` companions still exist and still run, because
that convention is what `make hooks-test` and the companion guard look for; they delegate here.

TWO DIRECTIONS FOR EVERY GUARD. Each table carries the cases it must FIRE on and the cases it must
stay QUIET on, and the quiet half is deliberately the longer one. Every false positive this project
has paid for is in these tables as a regression case - a commit message that quoted a blocked
command, a grep that named a path, a docstring, a fixture argument, a hook whose matcher blocked its
own repair. The shared lesson has a name now: **a mention is not an invocation.**
"""

from __future__ import annotations

import json
import re
import os
import pathlib
import tempfile
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent


def cmd(c: str) -> str:
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": c}})


def edit(path: str, old: str = "", new: str = "") -> str:
    return json.dumps({"tool_name": "Edit", "tool_input": {"file_path": path, "old_string": old, "new_string": new}})


def write(path: str, content: str) -> str:
    return json.dumps({"tool_name": "Write", "tool_input": {"file_path": path, "content": content}})


REPO_SAFETY = [
    # (label, payload, expected)
    ("force push, long flag", cmd("git push --force origin main"), "blocked"),
    ("force push, short flag", cmd("git push -f"), "blocked"),
    ("force push, with-lease", cmd("git push --force-with-lease origin HEAD:main"), "blocked"),
    ("flag before the verb", cmd("git --force push origin main"), "blocked"),
    ("an ordinary push", cmd("git -C /gm-assistant/.clones/x push origin HEAD:main"), "ok"),
    ("the stop-work procedure", cmd("./scripts/sync-with-main.sh done"), "ok"),
    # the seventh mention-versus-invocation case: a message ABOUT the rule
    ("a commit message quoting the rule", cmd('git commit -m "never git push --force here"'), "ok"),
    ("a heredoc message quoting it", cmd("git commit -F - <<MSG\nblocks git push --force\nMSG"), "ok"),
    # history is never rewritten (GM 2026-08-25, constitution VI)
    ("a rebase", cmd("git rebase origin/main"), "blocked"),
    ("a pull with --rebase", cmd("git -C /diagram/.clones/x pull --rebase origin main"), "blocked"),
    ("a squash merge", cmd("git merge --squash session/other"), "blocked"),
    ("an amend", cmd("git commit --amend --no-edit"), "blocked"),
    ("an ordinary merge", cmd("git merge --no-edit origin/main"), "ok"),
    ("the procedure's pull", cmd("git pull --no-rebase origin main"), "ok"),
    ("a commit message mentioning rebase", cmd('git commit -m "no rebase or squash here"'), "ok"),
    ("git write to the GM repo", cmd("git -C /host-l7r-repo commit -m x"), "blocked"),
    ("git add to the GM repo", cmd("cd /host-l7r-repo && git add setting/l7r.md"), "blocked"),
    # read-only git there is explicitly ALLOWED by CLAUDE.md
    ("git log on the GM repo", cmd("git -C /host-l7r-repo log --oneline -5"), "ok"),
    ("git diff on the GM repo", cmd("git -C /host-l7r-repo diff"), "ok"),
    ("the documented escape", cmd("git -C /host-l7r-repo status  # HOST_GIT_OK: read-only"), "ok"),
    # FEATURE 178 - A REAL BYPASS OF THIS GUARD, closed. Quoted strings are blanked because they are
    # PAYLOAD, and they were replaced by the literal word ` QUOTED `; an assignment whose value was
    # quoted therefore became `FOO= QUOTED  git push ...`, and that inserted word broke the
    # command-position anchor. The most absolute guard here - the one whose header says it has no
    # escape hatch on purpose - could be walked past by putting quotes round an environment variable.
    # Demonstrated before the fix: FOO=bar blocked, FOO="bar" ALLOWED.
    ("force push behind a QUOTED assignment", cmd('FOO="bar" git push --force origin main'), "blocked"),
    ("force push behind a quoted *_OK name", cmd('GATE_OK="a reason" git push --force origin main'), "blocked"),
    ("rebase behind a quoted assignment", cmd('FOO="bar" git rebase -i main'), "blocked"),
    ("host git write behind a quoted assignment", cmd('FOO="bar" git -C /host-l7r-repo commit -am x'), "blocked"),
    # ...and the unquoted form, which always worked, still does - the fix widened nothing else
    ("force push behind a plain assignment", cmd("FOO=bar git push --force origin main"), "blocked"),
]

HOUSE_STYLE = [
    # GUARD_EDIT_OK: feature 164 - these five are CORRECTED now rather than refused (GM 2026-08-30).
    # Both rules are exact substitutions from CLAUDE.md, and a session refused for one of them simply
    # retyped the same edit with the fix - 3 firings, 3 identical re-edits. The rule is unchanged: an
    # edit the table cannot fully fix still refuses, and the GM own writing is never corrected at all.
    ("a British spelling in a spec", edit("/r/specs/x/spec.md", new="the licence is granted"), "rewritten:the license is granted"),
    ("another, in prose", edit("/r/docs/a.md", new="the centre of the map"), "rewritten:the center of the map"),
    ("the archaic territory word", edit("/r/docs/a.md", new="the lord demesne"), "rewritten:the lord domain"),
    ("an em-dash", edit("/r/docs/a.md", new="a dash \u2014 here"), "rewritten:a dash - here"),
    ("an en-dash", edit("/r/docs/a.md", new="a range 1\u20132"), "rewritten:a range 1 - 2"),
    # ...and the two the correction must NEVER touch
    ("a backticked MENTION is not a use", edit("/r/docs/a.md", new="the word `colour` is British"), "ok"),
    # GUARD_EDIT_OK: GM 2026-09-06 - A QUOTATION IS SOMEONE ELSE'S TEXT: *"The house style should not normalize
    # british spellings or em-dashes inside things we are quoting, because that requires us to edit other
    # people's quotes"*. Corner brackets, curly quotes and the HTML quotation elements are held out everywhere;
    # straight double quotes only in a prose file - in code they delimit a string. (Some words below are
    # written with \u escapes because the hook of the day corrected this file's own cases as they were typed.)
    ("a British spelling inside a footnote quotation", edit("/r/research/a.html", new="<li id=\"fn-3\">「depressional cent\u0072es」 (gloss)</li>"), "ok"),
    ("an en-dash inside curly quotes", edit("/r/docs/a.md", new="Wikipedia: \u201cTang (618\u2013907)\u201d"), "ok"),
    ("a straight-quoted passage in prose", edit("/r/docs/a.md", new="the chapter reads \"a dr\u0061ught animal\" on the page"), "ok"),
    ("an HTML <q> element", edit("/r/research/a.html", new="<q>a plain-col\u006fur sheath</q>"), "ok"),
    ("a straight-quoted string in CODE is still corrected", edit("/r/l7r/x.py", new="label = \"the col\u006fur\""), "rewritten:label = \"the color\""),
    ("a quotation beside a plain violation: only the plain one is corrected", edit("/r/docs/a.md", new="「col\u006fur」 and the col\u006fur"), "rewritten:「col\u006fur」 and the color"),
    ("the GM verbatim request is refused, not corrected", edit("/r/specs/164-x/request.md", new="fix the colour"), "blocked"),
    ("American spellings", edit("/r/docs/a.md", new="the center is gray, the color honors judgment"), "ok"),
    # the files that must QUOTE the forbidden words in order to state the rule
    ("CLAUDE.md stating the rule", edit("/r/CLAUDE.md", new="never write colour or centre"), "ok"),
    ("the constitution stating it", edit("/gm/.specify/memory/constitution.md", new="forbid licence"), "ok"),
    # the GM's own writing is theirs
    ("the GM's canonical file", edit("/host-l7r-repo/setting/l7r.md", new="the colour of the sky"), "ok"),
    ("a SOURCE block in our file", edit("/r/docs/a.md", new="<!-- SOURCE: GM NOTES - DO NOT MODIFY -->the colour<!-- END SOURCE -->"), "ok"),
    # A BASH HEREDOC IS A WRITE. The first version matched only the Edit/Write tools, and the author
    # walked straight past it minutes after shipping the guard by writing a spec with a python
    # heredoc. Same hole layer 3 had, and the same lesson: guard the ACTION, not one route to it.
    # ...and since feature 236 a Bash payload is TOLD rather than refused (spec D2): the payload is
    # often itself the spelling fix, and `make quick` is the half that fails.
    # ...and since feature 236's amendment the payload is CORRECTED like an edit (the GM 2026-09-12:
    # *"warn when it is the sed shape, and for other shapes just correct it"*). What the command only
    # NAMES is held out by `_hm_house`: a search, a path, a quoted token, a code span, a quotation.
    ("prose written by heredoc", cmd("cat > docs/a.md <<'EOF'\nthe colour is grey\nEOF"),
     "rewritten:cat > docs/a.md <<'EOF'\nthe color is gray\nEOF"),
    ("clean prose by heredoc", cmd("cat > docs/a.md <<'EOF'\nthe color is gray\nEOF"), "ok"),
    # THE WHOLE PAYLOAD, not only its heredoc bodies (feature 236 FR-007): the measured hole was a
    # write that travelled by some other route through Bash
    ("an echo append", cmd("echo 'the centre of it' >> docs/a.md"),
     "rewritten:echo 'the center of it' >> docs/a.md"),
    # THE SED SHAPE IS THE GM'S OWN EXEMPTION, and a replacement pair written any other way is the
    # same shape: correcting either would replace a word with itself and the fix would do nothing.
    ("a sed fix is left exactly as typed", cmd("sed -i 's/centre/center/g' docs/a.md"), "warned:centre"),
    ("a sed replacement that INTRODUCES one", cmd("sed -i 's/center/centre/g' docs/a.md"), "warned:centre"),
    ("a replacement pair in a Python sweep", cmd("python3 - <<'PY'\nt = t.replace(\"the centre of\", \"the center of\")\nPY"), "warned:centre"),
    # ...and the shapes where the word is NAMED rather than written, each one measured on the real
    # commands this hook had warned on (`specs/236-catch-mistakes-early-and-cheaply/research.md` R10)
    ("a sweep's own word list", cmd("python3 - <<'PY'\nWORDS = {'colour', 'centre'}\nPY"), "ok"),
    ("a regex alternation", cmd("python3 -c \"re.compile(r'(colour|centre)')\""), "ok"),
    ("a path that carries the word in its name", cmd("cat docs/colour-notes.md"), "ok"),
    ("a negated search is still a search", cmd("! grep -qiE 'colour|centre' docs/a.md"), "ok"),
    # THE SESSION STATE DIRECTORY IS OUTSIDE THE PROJECT, as `/tmp` is: the auto-memory's own index
    # line format uses an em-dash, and the correction was rewriting that format as it was written.
    ("the auto-memory index", cmd("cat >> /home/agent/.claude/projects/-diagram/memory/MEMORY.md <<'EOF'\n- [A](b.md) — the hook\nEOF"), "ok"),
    # ...and the two shapes that must stay quiet, or the guard fires on correct work
    ("searching for the word", cmd('git grep -n "centre" -- docs/'), "ok"),
    ("a code span NAMING the word", cmd("echo 'the token `colour` is British' >> docs/a.md"), "ok"),
    ("a prose quotation keeps its own characters", cmd("cat >> docs/a.md <<'EOF'\n「a plain colour sheath」\nEOF"), "ok"),
    # gm-request.md is a verbatim transcript of the GM speaking; correcting it defeats its purpose
    ("the GM's own words, by heredoc", cmd("cat > specs/128-x/gm-request.md <<'EOF'\nthey wrote colour\nEOF"), "ok"),
    ("merely GREPPING for one", cmd("grep -n colour docs/a.md"), "ok"),
    # a session scratchpad is outside the project (2026-09-06: three reader agents had verbatim page text in
    # /tmp result files rewritten and each worked around the guard)
    ("a file under /tmp is not project content", edit("/tmp/claude-1000/x/scratchpad/result.json", new="{\"t\": \"the col\u006fur\"}"), "ok"),
    # feature 236 - A FIXTURE IS A VERBATIM RECORD: `scripts/fixtures/` holds corpora of commands that
    # really ran, several of them house-style sweeps, and correcting one falsifies the measurement it
    # reproduces. The exemption is in the hook AND in the delta check; this is the hook half, which the
    # amendment review noticed had no case of its own and would have been lost silently.
    ("a recorded command corpus", write("/r/scripts/fixtures/corpus.json", "{\"command\": \"sed -i s/cent\u0072e/center/ docs/a.md\"}"), "ok"),
]


SHELL_CHECK = [
    # (1) IT DOES NOT PARSE - and the parse uses the options the TOOL's shell can enable
    ("an unfinished construct", cmd("if true; then"), "blocked"),
    ("an unbalanced quote", cmd('echo "one; echo two'), "blocked"),
    ("extglob enabled on one line and used on the next", cmd("shopt -s extglob\nls !(x)"), "ok"),
    ("an ordinary fold", cmd("cd /diagram && git log --oneline -3 | cat"), "ok"),
    # (2) A BACKTICK THAT WOULD RUN - valid syntax, so the parse cannot see it
    ("a code span in double quotes", cmd('echo "use `make quick` first"'), "blocked"),
    ("a code span in an UNQUOTED heredoc", cmd("cat > a.md <<EOF\nsee `make done`\nEOF"), "blocked"),
    ("an apostrophe must not hide a later span", cmd("cat > a.md <<EOF\nit's `make done`\nEOF"), "blocked"),
    ("the same text in single quotes", cmd("echo 'use `make quick` first'"), "ok"),
    ("...and in a QUOTED heredoc", cmd("cat > a.md <<'EOF'\nsee `make done`\nEOF"), "ok"),
    ("a deliberate substitution, written the project's way", cmd('echo "today is $(date)"'), "ok"),
    ("an escaped backtick opens nothing", cmd('echo "a literal \\` here"'), "ok"),
    ("a backtick after an unquoted # is a comment", cmd("ls -la  # see `make quick`"), "ok"),
    # (3) `-m` FOR A MESSAGE THAT NEEDS A HEREDOC
    ("a nested double quote", cmd('git commit -m "233: the pond\'s own "center" fixed"'), "blocked"),
    ("two -m flags", cmd('git commit -m "subject" -m "body"'), "blocked"),
    ("a newline inside -m", cmd('git commit -m "subject\n\nbody"'), "blocked"),
    ("a plain one-line -m", cmd('git commit -m "236: the walker fix"'), "ok"),
    ("a plain -am", cmd("git commit -am 'a plain message'"), "ok"),
    ("the heredoc form this names", cmd("git commit -F - <<'EOF'\n236: x\n\nbody\nEOF"), "ok"),
    ("another git verb is not judged", cmd('git log --grep "a "b" c" --oneline'), "ok"),
    # (4) A CO-AUTHOR ADDRESS THAT IS NOT OURS - every route a trailer arrives by
    ("the placeholder that reached main", cmd("git commit -F - <<'EOF'\nx\n\nCo-Authored-By: Claude <duplicate@anthropic.com>\nEOF"), "blocked"),
    ("a lower-case key is the same key", cmd("git commit -F - <<'EOF'\nx\n\nco-authored-by: Someone <other@example.com>\nEOF"), "blocked"),
    ("...and by --trailer", cmd("git commit -m 'x' --trailer 'Co-authored-by: Someone <other@example.com>'"), "blocked"),
    ("the expected address", cmd("git commit -F - <<'EOF'\nx\n\nCo-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>\nEOF"), "ok"),
    ("another trailer beside it", cmd("git commit -F - <<'EOF'\nx\n\nClaude-Session: https://claude.ai/code/session_x\nEOF"), "ok"),
    # the escape, and the reason floor on it
    ("the documented escape", cmd("echo \"a `deliberate` span\"  # SHELL_CHECK_OK: quoting a transcript verbatim"), "ok"),
    ("a bare escape token", cmd('echo "a `span`"  # SHELL_CHECK_OK'), "blocked"),
]


def corpus_replay() -> int:
    """Every Bash command the motivating session ran, driven through the hook itself (SC-002).

    This is the guard's false-positive rate, MEASURED rather than asserted, and it is the reason the
    parse is `bash -O extglob -n` rather than `bash -n`: the corpus is what showed the check refuses
    exactly the two commands that had also failed at run time, and the hand-added extglob case is what
    showed a default parse refusing work the tool runs (`specs/236-.../research.md` R6).
    """
    import concurrent.futures

    data = json.loads((HERE / "fixtures" / "bash-parse-corpus-2026-09.json").read_text())
    expected, rows = data["expected"], data["commands"]
    script = str(HERE / "shell-check-hooks.sh")
    env = dict(os.environ, GUARD_LOG_DIR=str(LOGDIR))

    def drive(row: dict) -> tuple[dict, str]:
        proc = subprocess.run([script, "pretool"], input=cmd(row["command"]),
                              capture_output=True, text=True, check=False, env=env)
        if not proc.returncode:
            return row, ""
        m = re.search(r'rule "([a-z-]+)"', proc.stderr or "")
        return row, (m.group(1) if m else "unknown")

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        outcomes = list(pool.map(drive, rows))
    by_rule: dict[str, list[dict]] = {}
    for row, rule in outcomes:
        if rule:
            by_rule.setdefault(rule, []).append(row)
    parse = by_rule.get("parse", [])
    # A FALSE POSITIVE IS A PARSE REFUSAL OF A COMMAND THAT RAN. The other rules refusing a corpus
    # command is not a false positive but the measurement of what they catch: every one of the
    # `commit-dash-m` refusals below is a multi-line or misquoted `-m` message of exactly the kind
    # item 3 bans, which is that ban's own evidence rather than a cost.
    false_positives = [r["command"][:70] for r in parse if not r.get("runtime_syntax_error")]
    n_real = len([r for r in rows if r.get("runtime_syntax_error")])
    bad = 0
    print("  the R6 corpus, replayed through the hook")
    for label, got, want in (
        ("commands replayed", len(rows) - 1, expected["commands"]),         # the extglob case is added by hand
        ("refused by the PARSE", len(parse), expected["refused_by_the_check"]),
        ("of those, real run-time failures", len(parse) - len(false_positives), expected["refused_that_also_failed_at_run_time"]),
        ("parse false positives", len(false_positives), expected["false_positives"]),
        ("run-time syntax errors in the corpus", n_real, expected["refused_that_also_failed_at_run_time"]),
        ("caught by the -m ban", len(by_rule.get("commit-dash-m", [])), expected["refused_by_the_commit_ban"]),
        ("caught by the backtick rule", len(by_rule.get("executing-backtick", [])), expected["refused_by_the_backtick_rule"]),
        ("caught by the co-author rule", len(by_rule.get("coauthor-address", [])), expected["refused_by_the_coauthor_rule"]),
        ("the hand-added extglob case refused", int(bool(rows[-1] in parse)), 0),
    ):
        ok = got == want
        bad += 0 if ok else 1
        print(f"  {'ok    ' if ok else 'FAIL  '} {label}: {got}" + ("" if ok else f" (expected {want})"))
    if false_positives:
        print("        " + "\n        ".join(false_positives[:5]))
    return bad


def source_block_cases(tmp: pathlib.Path) -> list[tuple[str, str, str]]:
    doc = tmp / "doc.md"
    doc.write_text(
        "intro\n<!-- SOURCE: GM NOTES - DO NOT MODIFY -->\n"
        "The colour of the sky was grey.\n<!-- END SOURCE -->\nours: the color is gray.\n",
        encoding="utf-8",
    )
    keep = (
        "intro\n<!-- SOURCE: GM NOTES - DO NOT MODIFY -->\n"
        "The colour of the sky was grey.\n<!-- END SOURCE -->\nnew tail\n"
    )
    return [
        # the exact interaction that makes this guard necessary: house style WANTS to fix these
        ("editing the GM's words", edit(str(doc), "The colour of the sky was grey.", "The color was gray."), "blocked"),
        ("a Write that drops the block", write(str(doc), "intro\nrewritten\n"), "blocked"),
        ("editing OUR text in the same file", edit(str(doc), "ours: the color is gray.", "ours: the color is slate."), "ok"),
        ("a Write that preserves it verbatim", write(str(doc), keep), "ok"),
        ("the documented escape", edit(str(doc), "The colour of the sky was grey.", "SOURCE_EDIT_OK - the GM asked"), "ok"),
        ("a file with no SOURCE block", edit(str(tmp / "none.md"), "x", "y"), "ok"),
    ]


LOGDIR = pathlib.Path(tempfile.mkdtemp(prefix="guardlog-fixtures-"))


def run(hook: str, cases: list[tuple[str, str, str]]) -> int:
    script = HERE / f"{hook}-hooks.sh"
    bad = 0
    print(f"{hook}-hooks.sh")
    for label, payload, want in cases:
        # GUARD_EDIT_OK: feature 164 - fixtures never reach the real firing log; `make audit` exists
        # to price a guard from what it really did, and a suite writing into it destroys that.
        env = dict(os.environ, GUARD_LOG_DIR=str(LOGDIR))
        proc = subprocess.run([str(script), "pretool"], input=payload, capture_output=True, text=True, check=False, env=env)
        # GUARD_EDIT_OK: feature 164 - a guard has a THIRD verdict now. `rewritten:<text>` expects the
        # hook to correct the payload rather than refuse it: exit 0 with a `updatedInput` whose edit
        # carries <text>. A guard that can produce the compliant form spends no round trip asking for
        # it, and the case file has to be able to say so.
        got = "blocked" if proc.returncode else "ok"
        out = (proc.stdout or "").strip()
        if not proc.returncode and out.startswith("{"):
            try:
                spoke = json.loads(out)["hookSpecificOutput"]
                fixed = spoke.get("updatedInput")
                if fixed:
                    got = "rewritten:" + (fixed.get("new_string") or fixed.get("content") or fixed.get("command") or "")
                elif spoke.get("additionalContext"):
                    # feature 236: a fourth verdict - the hook TELLS the session and the command runs
                    # as typed. `warned:<word>` asks that the context name that word.
                    got = "warned:" + spoke["additionalContext"]
            except Exception:
                pass
        ok = got == want or (want.startswith("warned:") and got.startswith("warned:") and want[7:] in got)
        bad += 0 if ok else 1
        print(f"  {'ok    ' if ok else 'FAIL  '} {label}" + ("" if ok else f"  (expected {want}, got {got[:120]})"))
    print(f"  {len(cases) - bad} passed, {bad} failed\n")
    return bad


def main() -> int:
    which = sys.argv[1] if len(sys.argv) > 1 else ""
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        (tmp / "none.md").write_text("no blocks here\n", encoding="utf-8")
        tables = {
            "repo-safety": REPO_SAFETY,
            "house-style": HOUSE_STYLE,
            "source-block": source_block_cases(tmp),
            "shell-check": SHELL_CHECK,
        }
        if which not in tables:
            print(f"usage: {sys.argv[0]} <{'|'.join(tables)}>")
            return 2
        bad = run(which, tables[which])
        if which == "shell-check":
            bad += corpus_replay()          # the false-positive rate, measured on every run (SC-002)
        return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
