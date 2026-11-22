//! What a command writes through an interpreter, as the make-only guard reads it for a guard file (451 T33, found by T14 on
//! 2026-11-20: `cd rust/guard/src/guards && python3 - <<'EOF' ... p='event_log_hooks.rs' ... open(p,'w')` rewrote a guard source the
//! guard refused to `sed -i`). Three readers, each over a part of the command the walk does not read as a file written:
//!
//! - a Python program's body (`shared::tree`'s target carries it; `py_c` has already judged it a writer): the files its string
//!   literals name, `shared::tree::program`'s reader (moved there by 451 T96, so the event log's `writes` reads it too; re-exported
//!   here for readme's and gate-write's guards), a guard directory named counting (`Path('rust/guard/src/guards') / name`).
//! - a shell's body (`bash -c '...'`, `bash <<EOF`, `cat <<EOF | bash`): judged as a command of its own.
//! - a Perl, Ruby or Node body (`-e '...'` or a heredoc): no reader of its own, so the Python literal reading, with no read exempted.
//!
//! And a `for` loop's variable is read once per word it takes, so `for f in Makefile; do tee $f` writes the Makefile.

use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};

use crate::guards::guard_file_hooks::{held, named};
pub(crate) use crate::shared::tree::program::program_names;

fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{pattern}: {e}"))
}

/// A shell's `-c` program, single- or double-quoted.
static SHELL_C: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"(?:^|[\s;&|(])(?:\S*/)?(?:ba|da|z)?sh\s+(?:-[a-zA-Z]+\s+)*-[a-zA-Z]*c\s+(?:'([^']*)'|"((?:\\.|[^"\\])*)")"#,
    )
});
/// A Perl, Ruby or Node `-e` program.
static OTHER_E: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"(?:^|[\s;&|(])(?:\S*/)?(?:perl|ruby|node)\s+(?:-[a-zA-Z0-9]+\s+)*-[a-zA-Z]*e\s+(?:'([^']*)'|"((?:\\.|[^"\\])*)")"#,
    )
});
/// A heredoc: 1 the opener's words after the delimiter, 2 the body (`shared::tree::python`'s shape).
static HEREDOC: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?sm)<<-?[ \t]*['"\\]?(\w+)['"]?([^\n]*)\n(.*?)^[ \t]*\1\b"#));
/// An interpreter a heredoc's text is piped to (`cat <<EOF | bash`).
static PIPED_TO: LazyLock<Regex> =
    LazyLock::new(|| re(r"\|\s*(?:\S*/)?(bash|sh|dash|zsh|perl|ruby|node)\b"));
/// A `for` loop's variable and its words.
static FOR_LOOP: LazyLock<Regex> =
    LazyLock::new(|| re(r"\bfor\s+([A-Za-z_]\w*)\s+in\s+([^;\n]*?)\s*(?:;|\n)\s*do\b"));
const SHELLS: [&str; 4] = ["bash", "sh", "dash", "zsh"];
const OTHERS: [&str; 3] = ["perl", "ruby", "node"];
/// How deep a body inside a body is read (`bash -c "bash -c ..."`): CONVENTION, past any shape the corpora hold.
pub(super) const DEPTH: usize = 3;

/// A guard file, or a directory holding guard sources (a last part with no extension: `.../tests.rs` names a file, not a directory).
fn guard_path(p: &str) -> bool {
    let dir = !p.rsplit('/').next().unwrap_or(p).contains('.');
    held(p) || (dir && held(&format!("{p}/_")))
}

/// Whether a program's string literals name a guard file it could write, run in `dir` (`/` when unknown); `reads` exempts the
/// literals a Python program only reads.
pub(super) fn program_names_guard(body: &str, dir: Option<&str>, reads: bool) -> bool {
    let dir = dir.filter(|_| !moves(body));
    program_names(body, dir, reads, false, &guard_path).is_some()
}

/// Whether a program changes its own directory (`os.chdir`, `os.fchdir`, `contextlib.chdir`), so where it stands says nothing of where
/// its relative literals land: it is read from `/`, as one whose place is unknown, and never freed as scratch (451 T87: `cd /tmp/q &&
/// python3 -c "import os; os.chdir('/diagram/.clones/s'); open('Makefile','w')"` passed the first scratch rule).
fn moves(body: &str) -> bool {
    body.contains("chdir")
}

/// Whether a program run in `dir` names a guard file it could write by its name, and none that is held - each such name lands in
/// scratch (451 T87), so the Python patterns over its body overrule nothing the walk judged.
pub(super) fn program_names_scratch(body: &str, dir: Option<&str>) -> bool {
    !moves(body) && program_names_named(body, dir) && !program_names_guard(body, dir, true)
}

/// Whether a program run in `dir` names a guard file it could write by its name alone, wherever it lands - HEAD's reading before 451
/// T87, which a command naming a `CDPATH` or a `worktree add` keeps.
pub(super) fn program_names_named(body: &str, dir: Option<&str>) -> bool {
    let by_name = |p: &str| {
        let dir = !p.rsplit('/').next().unwrap_or(p).contains('.');
        named(p) || (dir && named(&format!("{p}/_")))
    };
    let dir = dir.filter(|_| !moves(body));
    program_names(body, dir, true, false, &by_name).is_some()
}

/// The interpreter a heredoc feeds: the command before its `<<` on the opener's line, else one the opener pipes it to.
fn fed(cmd: &str, start: usize, rest: &str) -> Option<String> {
    let line = cmd[..start].rsplit('\n').next().unwrap_or("");
    let part = line.rsplit(['|', ';', '&', '(']).next().unwrap_or("");
    let head = part
        .split_whitespace()
        .find(|w| !w.contains('=') && !matches!(*w, "sudo" | "env" | "exec" | "command"))
        .map(|h| h.rsplit('/').next().unwrap_or(h).to_owned());
    head.filter(|h| SHELLS.contains(&h.as_str()) || OTHERS.contains(&h.as_str()))
        .or_else(|| {
            PIPED_TO
                .captures(rest)
                .ok()
                .flatten()
                .and_then(|c| c.get(1))
                .map(|m| m.as_str().to_owned())
        })
}

/// The bodies a command hands an interpreter that is not Python: (a shell's, the body).
pub(super) fn bodies(cmd: &str) -> Vec<(bool, String)> {
    let text = |c: &Captures, a: usize, b: usize| {
        c.get(a)
            .or_else(|| c.get(b))
            .map_or("", |m| m.as_str())
            .to_owned()
    };
    let mut out: Vec<(bool, String)> = SHELL_C
        .captures_iter(cmd)
        .map_while(Result::ok)
        .map(|c| (true, text(&c, 1, 2)))
        .collect();
    out.extend(
        OTHER_E
            .captures_iter(cmd)
            .map_while(Result::ok)
            .map(|c| (false, text(&c, 1, 2))),
    );
    for c in HEREDOC.captures_iter(cmd).map_while(Result::ok) {
        let (start, rest) = (c.get(0).map_or(0, |m| m.start()), text(&c, 2, 2));
        if let Some(head) = fed(cmd, start, &rest) {
            out.push((SHELLS.contains(&head.as_str()), text(&c, 3, 3)));
        }
    }
    out
}

/// The command once per word of each `for` loop, the loop's variable replaced by the word (`$f`, `${f}`, `"$f"`).
pub(super) fn loop_expansions(cmd: &str) -> Vec<String> {
    let mut out = Vec::new();
    for c in FOR_LOOP.captures_iter(cmd).map_while(Result::ok) {
        let name = c.get(1).map_or("", |m| m.as_str());
        let var = re(&format!(
            r#""\$\{{{name}\}}"|"\${name}"|\$\{{{name}\}}|\${name}\b"#
        ));
        for word in c
            .get(2)
            .map_or("", |m| m.as_str())
            .split_whitespace()
            .take(20)
        {
            let word = word.trim_matches(|ch| ch == '"' || ch == '\'');
            let expanded = var.replace_all(cmd, word).into_owned();
            if expanded != cmd {
                out.push(expanded);
            }
        }
    }
    out
}
