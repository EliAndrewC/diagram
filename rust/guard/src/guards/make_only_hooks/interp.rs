//! What a command writes through an interpreter, as the make-only guard reads it for a guard file (451 T33, found by T14 on
//! 2026-11-20: `cd rust/guard/src/guards && python3 - <<'EOF' ... p='event_log_hooks.rs' ... open(p,'w')` rewrote a guard source the
//! guard refused to `sed -i`). Three readers, each over a part of the command the walk does not read as a file written:
//!
//! - a Python program's body (`shared::tree`'s target carries it; `py_c` has already judged it a writer): the files its string
//!   literals name, resolved where the shell stands, a literal joined to the next by `/` or `,` (`Path('dev') / 'switches.json'`,
//!   `os.path.join(...)`) read as one path, and a guard directory named counts (`Path('rust/guard/src/guards') / name`). A
//!   literal whose every use is a read - `open(L)`, `open(L, 'r')`, `Path(L).read_text()` - names nothing written, so a program
//!   that reads a guard file and writes elsewhere runs (the replay's rows of that shape, measured 2026-11-20). Fails CLOSED as `py_c`
//!   does: a literal bound to a name, or a glob, counts whatever the name is then used for.
//! - a shell's body (`bash -c '...'`, `bash <<EOF`, `cat <<EOF | bash`): judged as a command of its own.
//! - a Perl, Ruby or Node body (`-e '...'` or a heredoc): no reader of its own, so the Python literal reading, with no read exempted.
//!
//! And a `for` loop's variable is read once per word it takes, so `for f in Makefile; do tee $f` writes the Makefile.

use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};

use crate::guards::guard_file_hooks::held;
use crate::shared::tree::normpath;

fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{pattern}: {e}"))
}

/// A string literal of a program (one line, no whitespace inside: a path).
static LITERAL: LazyLock<Regex> = LazyLock::new(|| re(r#"(['"])([^'"\s\\]+)\1"#));
/// Two literals joined into one path: `'a' / 'b'` past a closing `)` (`Path('a') / 'b'`), or `join('a', 'b'` (`os.path.join`) -
/// a bare `'a', 'b'` is an argument list (`open(p, 'w')`), not a path.
static JOINED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"(?:\bjoin\(\s*(['"])([^'"\s\\]+)\1\s*,|(['"])([^'"\s\\]+)\3\s*\)?\s*/)\s*(['"])([^'"\s\\]+)\5"#,
    )
});
/// A triple-quoted string of a program.
static TRIPLE: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?s)"""(?:\\.|(?!""").)*"""|'''(?:\\.|(?!''').)*'''"#));
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

/// A literal resolved where the program runs.
fn resolve(lit: &str, base: &str) -> String {
    if lit.starts_with('/') {
        normpath(lit)
    } else {
        normpath(&format!("{base}/{lit}"))
    }
}

/// A guard file, or a directory holding guard sources (a last part with no extension: `.../tests.rs` names a file, not a directory).
fn guard_path(p: &str) -> bool {
    let dir = !p.rsplit('/').next().unwrap_or(p).contains('.');
    held(p) || (dir && held(&format!("{p}/_")))
}

/// The program with its triple-quoted strings blanked: text a program carries (a suite's body being written, a docstring) names
/// files it does not open - the refusal corpus's 2026-09-05 row writes a suite whose text names a Makefile.
fn without_text(body: &str) -> String {
    TRIPLE.replace_all(body, "\"\"").into_owned()
}

/// Whether every use of the literal `lit` in `body` is a read: opened to read, read through `Path`, an element of a subprocess's
/// argv (a hook RUN, not written: window#56, #299, #312, each running `scripts/hooks/house-style-hooks.sh` - refused on T33's first
/// replay, measured 2026-11-20), or a value in a dict (a hook payload's `file_path`: window#267).
fn only_read(body: &str, lit: &str) -> bool {
    let q = fancy_regex::escape(lit);
    let any = re(&format!(r#"(['"]){q}\1"#));
    any.find_iter(body).map_while(Result::ok).all(|m| {
        // the 300 characters before it are context enough, and keep each scan short on a long program
        let from = body[..m.start()]
            .char_indices()
            .rev()
            .nth(299)
            .map_or(0, |(i, _)| i);
        let (before, after) = (&body[from..m.start()], &body[m.end()..]);
        (hit(&OPEN_BEFORE, before) && hit(&OPEN_AFTER, after))
            || (hit(&PATH_BEFORE, before) && hit(&PATH_AFTER, after))
            || hit(&ARGV_BEFORE, before)
            || hit(&VALUE_BEFORE, before)
            || hit(&SPEC_BEFORE, before)
    })
}

/// Whether a literal can be a file's path as the program spells it (451 T33's round-3 gate replay, measured 2026-11-20): an
/// f-string's placeholder (`{C}/x.py`), a glob, a URL, an anchor (`a.md#fn-3`) and the text between two literals
/// (`)[0].split(`) are not, and each was refused there as a write where the shell stood.
fn shaped(lit: &str) -> bool {
    lit.chars()
        .all(|ch| ch.is_alphanumeric() || matches!(ch, '_' | '.' | '/' | '~' | '@' | '+' | '-'))
}

/// Whether the literal at `at` is joined onto a base the program computes (`Path(sys.argv[1]) / 'spec.md'`, `d / 'a.py'`,
/// `R + '/x.html'`, `Path(RESEARCH_DIR, 'SOURCES.html')`): where it lands is not where the shell stands. A base that is itself a
/// literal is `JOINED`'s. A literal a regex or a string method takes is text, and answers the same (`TAIL_BEFORE`).
fn joined_on(body: &str, at: usize) -> bool {
    let from = body[..at]
        .char_indices()
        .rev()
        .nth(199)
        .map_or(0, |(i, _)| i);
    hit(&TAIL_BEFORE, &body[from..at])
}

fn hit(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

static OPEN_BEFORE: LazyLock<Regex> = LazyLock::new(|| re(r"\bopen\(\s*$"));
static OPEN_AFTER: LazyLock<Regex> =
    LazyLock::new(|| re(r#"^\s*(?:\)|,\s*(?:mode\s*=\s*)?['"]r[bt]?['"]\s*[,)])"#));
static PATH_BEFORE: LazyLock<Regex> = LazyLock::new(|| re(r"\bPath\(\s*$"));
static PATH_AFTER: LazyLock<Regex> = LazyLock::new(|| re(r"^\s*\)\s*\.read_(?:text|bytes)\("));
/// Inside the argv list a subprocess call opens, no `]` since.
static ARGV_BEFORE: LazyLock<Regex> =
    LazyLock::new(|| re(r"\b(?:run|call|check_call|check_output|Popen)\(\s*\[[^\]\n]*$"));
/// A dict's value: `'key': ` before it.
static VALUE_BEFORE: LazyLock<Regex> = LazyLock::new(|| re(r#"['"][\w-]+['"]\s*:\s*$"#));
/// A module's file, loaded to run (window#53: `spec_from_file_location('m', 'specs/.../measure.py')`, a read).
static SPEC_BEFORE: LazyLock<Regex> =
    LazyLock::new(|| re(r#"\bspec_from_file_location\(\s*['"][^'"]*['"]\s*,\s*$"#));
/// A literal after `/` or `+`, or a later argument of `Path(`/`join(` (no parenthesis between); or text, not a path: the first
/// argument of a `re.` function or of a string method (window#280's `re.findall(r"summary.only", ...)`, window#358's
/// `f.endswith(".html")`, a `replace`'s words - round 4 of T33's replay, measured 2026-11-20), or a comparison's (`f ==
/// "SOURCES.html"`, window#358, after5).
static TAIL_BEFORE: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?:[/+]\s*|[=!]=\s*|\b(?:Path|join)\([^()\n]*,\s*|(?:\bre\.\w+|\.(?:endswith|startswith|replace|split|rsplit|index|rindex|find|rfind|count|strip|lstrip|rstrip|removeprefix|removesuffix))\([^()\n]*?[rbu]?)$",
    )
});

/// Whether a program's string literals name a guard file it could write, run in `dir` (`/` when unknown); `reads` exempts the
/// literals a Python program only reads.
pub(super) fn program_names_guard(body: &str, dir: Option<&str>, reads: bool) -> bool {
    program_names(body, dir, reads, false, &guard_path).is_some()
}

/// The first path a program's literals name, resolved in `dir`, that `wanted` takes - the make-only guard's guard file, the
/// gate-write guard's file the gate would see (451 T33). `placed` (the gate's) takes only a literal that is a path where the shell
/// stands: `shaped`, and not `joined_on` a base the program computes - the gate fails open on a path it cannot resolve, where
/// make-only, fail-closed, counts any literal naming a guard file.
pub(crate) fn program_names(
    body: &str,
    dir: Option<&str>,
    reads: bool,
    placed: bool,
    wanted: &dyn Fn(&str) -> bool,
) -> Option<String> {
    let (base, body) = (dir.unwrap_or("/"), without_text(body));
    // a literal holding `$` is a shell variable's text, which the program never expands (and could not be resolved here if it did)
    let path = |lit: &str| !lit.contains('$') && (!placed || shaped(lit));
    let single = LITERAL
        .captures_iter(&body)
        .map_while(Result::ok)
        .find_map(|c| {
            let m = c.get(2)?;
            let lit = m.as_str();
            let at = resolve(lit, base);
            let tail = placed && joined_on(&body, m.start() - 1);
            (path(lit) && !tail && wanted(&at) && !(reads && only_read(&body, lit))).then_some(at)
        });
    single.or_else(|| {
        JOINED
            .captures_iter(&body)
            .map_while(Result::ok)
            .find_map(|c| {
                let (a, b) = (
                    c.get(2).or_else(|| c.get(4)).map_or("", |m| m.as_str()),
                    c.get(6).map_or("", |m| m.as_str()),
                );
                let at = resolve(&format!("{a}/{b}"), base);
                (path(a) && path(b) && !b.starts_with('/') && wanted(&at)).then_some(at)
            })
    })
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
