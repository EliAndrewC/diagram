//! `shell_check_hooks`'s cases. The cases moved here from `tests/hooks/test_hooks_cases.py` (feature 449 T050), each one's history kept above it.
//!
//! TWO DIRECTIONS FOR EVERY GUARD: each table carries the cases it must FIRE on and the cases it must stay QUIET on, and the quiet half is deliberately the longer one. Every false
//! positive this project has paid for is in these tables as a regression case. **A mention is not an invocation.**

use super::{cmd, Case};

pub(super) fn cases() -> Vec<Case> {
    vec![
        // (1) IT DOES NOT PARSE - and the parse uses the options the TOOL's shell can enable
        ("an unfinished construct", cmd("if true; then"), "blocked"),
        ("an unbalanced quote", cmd("echo \"one; echo two"), "blocked"),
        ("extglob enabled on one line and used on the next", cmd("shopt -s extglob\nls !(x)"), "ok"),
        ("an ordinary fold", cmd("cd /diagram && git log --oneline -3 | cat"), "ok"),
        // (2) A BACKTICK THAT WOULD RUN - valid syntax, so the parse cannot see it
        ("a code span in double quotes", cmd("echo \"use `make quick` first\""), "blocked"),
        ("a code span in an UNQUOTED heredoc", cmd("cat > a.md <<EOF\nsee `make done`\nEOF"), "blocked"),
        ("an apostrophe must not hide a later span", cmd("cat > a.md <<EOF\nit's `make done`\nEOF"), "blocked"),
        ("the same text in single quotes", cmd("echo 'use `make quick` first'"), "ok"),
        ("...and in a QUOTED heredoc", cmd("cat > a.md <<'EOF'\nsee `make done`\nEOF"), "ok"),
        ("a deliberate substitution, written the project's way", cmd("echo \"today is $(date)\""), "ok"),
        ("an escaped backtick opens nothing", cmd("echo \"a literal \\` here\""), "ok"),
        ("a backtick after an unquoted # is a comment", cmd("ls -la  # see `make quick`"), "ok"),
        // (3) `-m` FOR A MESSAGE THAT NEEDS A HEREDOC
        ("a nested double quote", cmd("git commit -m \"233: the pond's own \"center\" fixed\""), "blocked"),
        // ...REWRITTEN where the message is unambiguous (the GM, 2026-10-02: "I do indeed want that git commit rewrite")
        ("two -m flags", cmd("git commit -m \"subject\" -m \"body\""), "rewritten:git commit -F - <<'EOF'\nsubject\n\nbody\nEOF"),
        ("a newline inside -m", cmd("git commit -m \"subject\n\nbody\""), "rewritten:git commit -F - <<'EOF'\nsubject\n\nbody\nEOF"),
        ("a multi-line -am in a chain", cmd("git add -A && git commit -q -am 'subject\n\nbody' && git log -1"), "rewritten:git add -A && git commit -q -a -F - <<'EOF' && git log -1\nsubject\n\nbody\nEOF"),
        ("...but not one the shell would expand", cmd("git commit -m \"costs $5\n\nnow\""), "blocked"),
        ("...nor one beside another heredoc", cmd("git commit -m 'a\nb' && cat > f <<'X'\nx\nX"), "blocked"),
        ("a plain one-line -m", cmd("git commit -m \"236: the walker fix\""), "ok"),
        ("a plain -am", cmd("git commit -am 'a plain message'"), "ok"),
        ("the heredoc form this names", cmd("git commit -F - <<'EOF'\n236: x\n\nbody\nEOF"), "ok"),
        ("another git verb is not judged", cmd("git log --grep \"a \"b\" c\" --oneline"), "ok"),
        // (4) A CO-AUTHOR ADDRESS THAT IS NOT OURS - every route a trailer arrives by
        ("the placeholder that reached main", cmd("git commit -F - <<'EOF'\nx\n\nCo-Authored-By: Claude <duplicate@anthropic.com>\nEOF"), "blocked"),
        ("a lower-case key is the same key", cmd("git commit -F - <<'EOF'\nx\n\nco-authored-by: Someone <other@example.com>\nEOF"), "blocked"),
        ("...and by --trailer", cmd("git commit -m 'x' --trailer 'Co-authored-by: Someone <other@example.com>'"), "blocked"),
        ("the expected address", cmd("git commit -F - <<'EOF'\nx\n\nCo-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>\nEOF"), "ok"),
        ("another trailer beside it", cmd("git commit -F - <<'EOF'\nx\n\nClaude-Session: https://claude.ai/code/session_x\nEOF"), "ok"),
        // the escape, and the reason floor on it
        ("the documented escape", cmd("echo \"a `deliberate` span\"  # SHELL_CHECK_OK: quoting a transcript verbatim"), "ok"),
        ("a bare escape token", cmd("echo \"a `span`\"  # SHELL_CHECK_OK"), "blocked"),
    ]
}
