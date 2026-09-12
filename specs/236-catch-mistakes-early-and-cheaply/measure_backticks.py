"""The record of how R8 was measured - so its count can be re-run rather than re-argued.

Round 4 of this feature's review found three quote-state walkers over the same transcripts giving 18, 42
and about 100 executing backtick spans: a count that depends on the walker is not a finding. What held
under all three was that NONE was a deliberate substitution. This file fixes the walker so the count is
reproducible, and `selftest()` pins every rule it applies.

A backtick span EXECUTES when it is read in no quote or in double quotes. It does NOT execute inside:
  - single quotes '...' and ANSI-C quotes $'...'
  - a quoted heredoc body: <<'X', <<"X", <<\\X (the delimiter quoted in any of the three ways)
An escaped backtick \\` never opens a span. $(...) is substitution too, but it is not the hazard FR-004a
names (it does not arrive as a markdown habit), so it is skipped over rather than counted.
"""

from __future__ import annotations

import re

_QUOTED_HEREDOC = re.compile(r"<<-?\s*(?:'(\w+)'|\"(\w+)\"|\\(\w+)).*?^\s*(?:\1|\2|\3)\s*$", re.S | re.M)
#: an UNQUOTED heredoc: a bare delimiter. Its body is expanded like double-quoted text, so a backtick span in
#: it EXECUTES and the quote characters in it are literal - an apostrophe there must not hide a later span.
_UNQUOTED_HEREDOC = re.compile(r"<<-?\s*([A-Za-z_]\w*)[^\n]*\n(.*?)^\s*\1\s*$", re.S | re.M)
_SPAN = re.compile(r"(?<!\\)`[^`\n]*(?<!\\)`")


def executing_backticks(cmd: str) -> list[str]:
    """Every backtick span in `cmd` that bash would execute, in order.

    KNOWN OVER-COUNT, disclosed rather than hidden because it cannot flip the finding: a backtick inside a
    `#` comment is counted though it does not run. The finding R8 rests on is that NO span is a deliberate
    substitution, and a comment cannot contain one either.
    """
    cmd = _QUOTED_HEREDOC.sub("", cmd)
    spans: list[str] = []
    # unquoted heredoc bodies first: every span in them executes, and the quote walk below would mis-read
    # their apostrophes as shell quotes (spec-fidelity round 5 found `cat <<EOF / it's `date` / EOF` hidden)
    def _take(m: re.Match[str]) -> str:
        spans.extend(_SPAN.findall(m.group(2)))
        return ""
    cmd = _UNQUOTED_HEREDOC.sub(_take, cmd)
    st: str | None = None  # None, "'", '"', or "$'"
    i, n = 0, len(cmd)
    while i < n:
        ch = cmd[i]
        if st in (None, '"') and ch == "\\":
            i += 2
            continue
        if st is None:
            if cmd.startswith("$'", i):
                st = "$'"
                i += 2
                continue
            if ch == "'":
                st = "'"
            elif ch == '"':
                st = '"'
            elif ch == "`":
                j = cmd.find("`", i + 1)
                if j > 0:
                    spans.append(cmd[i : j + 1])
                    i = j
        elif st in ("'", "$'"):
            if st == "$'" and ch == "\\":
                i += 2
                continue
            if ch == "'":
                st = None
        elif st == '"':
            if ch == '"':
                st = None
            elif ch == "`":
                j = cmd.find("`", i + 1)
                if j > 0:
                    spans.append(cmd[i : j + 1])
                    i = j
        i += 1
    return spans


def selftest() -> None:
    assert executing_backticks('echo "use `make quick` first"') == ["`make quick`"], "double quotes execute"
    assert executing_backticks("echo 'use `make quick` first'") == [], "single quotes do not"
    assert executing_backticks("echo $'a `b` c'") == [], "ANSI-C quotes do not"
    assert executing_backticks('echo "a \\`b\\` c"') == [], "an escaped backtick opens no span"
    assert executing_backticks("cat <<'X'\nsee `make done`\nX") == [], "a quoted heredoc body is literal"
    assert executing_backticks('cat <<"X"\nsee `make done`\nX') == [], "a double-quoted delimiter is literal too"
    assert executing_backticks("cat <<\\X\nsee `make done`\nX") == [], "a backslashed delimiter is literal too"
    assert executing_backticks("echo `date`") == ["`date`"], "a bare backtick executes"
    assert executing_backticks("cat <<EOF\nsee `make done`\nEOF") == ["`make done`"], "an UNQUOTED heredoc body executes"
    assert executing_backticks("cat <<EOF\nit's `date`\nEOF") == ["`date`"], "an apostrophe in an unquoted body does not hide a later span"
    print("measure_backticks selftest ok")


if __name__ == "__main__":
    import glob
    import json
    import os
    import sys

    selftest()
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.claude/projects/-diagram")
    files = sorted(glob.glob(os.path.join(root, "*.jsonl")), key=os.path.getmtime)[-60:]
    total, found = 0, []
    for f in files:
        for line in open(f, encoding="utf-8", errors="replace"):
            try:
                o = json.loads(line)
            except ValueError:
                continue
            cont = (o.get("message") or {}).get("content")
            if not isinstance(cont, list):
                continue
            for c in cont:
                if c.get("type") == "tool_use" and c.get("name") == "Bash":
                    total += 1
                    found += executing_backticks(c["input"].get("command", ""))
    print(f"transcripts {len(files)}, Bash commands {total}, executing backtick spans {len(found)}")
    for s in sorted(set(found))[:40]:
        print("  ", s[:80])
