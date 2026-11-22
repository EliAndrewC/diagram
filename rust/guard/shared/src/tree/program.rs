//! The files a Python program's string literals name, resolved where it runs (451 T33's reader, found by T14 on 2026-11-20:
//! `cd rust/guard/src/guards && python3 - <<'EOF' ... p='event_log_hooks.rs' ... open(p,'w')` rewrote a guard source the make-only
//! guard refused to `sed -i`). Moved here from make-only's `interp` by 451 T96, so the event log's `writes` reads the files such a
//! program writes as the guards read them (make-only's guard file, readme's README, gate-write's file the gate would see): the walk
//! places a Python program's write where the shell stands, a directory, so a heredoc's or a `-c` program's files were named nowhere
//! (T93's replay, measured 2026-11-21: 15 of the night's 51 still-missed landed files, and T84's 5 plan- and task-crate files).
//!
//! The body is the one `shared::tree`'s target carries; `py_c` has already judged it a writer. A literal joined to the next by `/`
//! or `,` (`Path('dev') / 'switches.json'`, `os.path.join(...)`) is read as one path. A literal whose every use is a read - `open(L)`,
//! `open(L, 'r')`, `Path(L).read_text()` - names nothing written (`reads`), so a program that reads one file and writes another
//! names the other alone. It fails CLOSED as `py_c` does: a literal bound to a name, or a glob, counts whatever the name is then used
//! for; a caller that wants fewer names takes only those its `wanted` keeps. A literal handed to a function the program defines,
//! whose parameter that function writes joined onto a module-level literal (`root='<dir>/'; def sub(path): open(root+path, 'w')`;
//! `sub('a.rs')`), is placed at that join too (`bound`, 451 T110).
//!
//! Three shapes are reads, or text, not writes (451 T118, found by T51 and measured 2026-11-21): a path joined by `/` and read whole,
//! `(root / 'scripts' / 'a.sh').read_text()` (`chain_read`); a literal in an argv list bound to a name only run, `old = ['<hook>',
//! ...]` then `subprocess.run(old)` (`display_run`); and a literal a test reads, `'plan.md' in cmd` (`tested`) - fail-closed, only in a
//! program that writes no path it computes (`writes_computed`), where the tested literal could name the write's landing.
//! A write through a join stays a write.
//!
//! WHAT IT BUILDS (451 T96): a hook event is a process of its own, so each pattern is a `regex::Lazy`, built only for a text that
//! could match it - its gate a necessary condition, most on the end or the start of the window a scan asks of it - and a program's
//! literals, and each literal's uses, are read by plain code. WHY: every Python program a Bash call ran built the literal pattern,
//! `TRIPLE` and `JOINED`, and a literal naming a file the scans' patterns and one more of its own on every call: 13.1 ms the first
//! read of a program naming no file against 0.11 ms a second, and 7.1 ms every read of one naming 20 files, each pattern 0.26 to
//! 6.1 ms to build first in a process (`JOINED` the most, `TAIL_BEFORE` 3.8 ms), measured 2026-11-21 (`/tmp/t96/ms`: the medians of
//! 31 fresh processes' wall time, a load near 30). The triple-quoted text `TRIPLE` matched is since read by shape's
//! `triple_quoted_spans`, which builds no pattern (451 T112).

use std::cell::OnceCell;

use fancy_regex::Regex;

use super::normpath;
use crate::regex::Lazy;
use crate::shape::triple_quoted_spans;

mod parse;
mod uses;

use parse::{closing, name, split, trimmed, word, Program};
use uses::{chain_read, only_read, tested};

fn re(pattern: &str) -> Regex {
    crate::regex::build(pattern).unwrap_or_else(|e| unreachable!("{pattern}: {e}"))
}

/// Each string literal of a program (one line, no whitespace inside: a path), in order, its text and where that starts: what
/// `(['"])([^'"\s\\]+)\1` finds - a quote, one or more characters that are no quote, no whitespace (Unicode's `White_Space`, as
/// `\s` and `char::is_whitespace` read it) and no backslash, then the same quote - read as plain code, as T97 read `plain_quote_body`
/// (451 T96): that pattern, reached by every program holding a quote, was the one build left on most Python programs' Bash ends.
fn literals(body: &str) -> impl Iterator<Item = (usize, &str)> {
    let mut at = 0;
    std::iter::from_fn(move || {
        while let Some(open) = body[at..].find(['\'', '"']).map(|i| at + i) {
            let start = open + 1;
            let end = body[start..]
                .find(|c: char| !in_literal(c))
                .map_or(body.len(), |i| start + i);
            // no match at a quote whose run ends otherwise, and none inside the run: the next try is where it ended
            at = end;
            if end > start && body[end..].starts_with(&body[open..start]) {
                at = end + 1;
                return Some((start, &body[start..end]));
            }
        }
        None
    })
}

/// Two literals joined into one path: `'a' / 'b'` past a closing `)` (`Path('a') / 'b'`), or `join('a', 'b'` (`os.path.join`) -
/// a bare `'a', 'b'` is an argument list (`open(p, 'w')`), not a path.
static JOINED: Lazy = Lazy::new(joined_could, || {
    re(
        r#"(?:\bjoin\(\s*(['"])([^'"\s\\]+)\1\s*,|(['"])([^'"\s\\]+)\3\s*\)?\s*/)\s*(['"])([^'"\s\\]+)\5"#,
    )
});

/// Whether `JOINED` could match `text`: a `join(` whose first argument is a literal before a `,`, or a `/` with a literal ending
/// before it (past a `)`) and one starting after it. A bare quote was not enough: `'/'.join(`, `split('/')` and a Rust `.join("x")`
/// in a program's text passed on 83 of the corpus's 1,225 Python programs, the pattern matching 8 (measured 2026-11-21,
/// `/tmp/t96/gates.py`, a Python `re` run over each whole command, an estimate).
fn joined_could(text: &str) -> bool {
    text.match_indices("join(").any(|(i, m)| {
        let rest = text[i + m.len()..].trim_start();
        literal_at(rest).is_some_and(|n| rest[n..].trim_start().starts_with(','))
    }) || text.match_indices('/').any(|(i, _)| {
        let back = text[..i].trim_end();
        let back = back.strip_suffix(')').map_or(back, str::trim_end);
        literal_ends(back) && literal_at(text[i + 1..].trim_start()).is_some()
    })
}

/// Whether `c` can be inside a literal: no quote, no whitespace, no backslash (`literals`' reading).
fn in_literal(c: char) -> bool {
    !matches!(c, '\'' | '"' | '\\') && !c.is_whitespace()
}

/// The length of the literal `s` starts with - a quote, one or more characters `in_literal`, the same quote - if it starts with one.
fn literal_at(s: &str) -> Option<usize> {
    let quote = s.chars().next().filter(|c| matches!(c, '\'' | '"'))?;
    let run = s[1..].find(|c: char| !in_literal(c)).unwrap_or(s.len() - 1);
    (run > 0 && s[1 + run..].starts_with(quote)).then_some(run + 2)
}

/// Whether `s` ends with a literal, read from its end as `literal_at` reads from its start.
fn literal_ends(s: &str) -> bool {
    let Some(quote) = s.chars().next_back().filter(|c| matches!(c, '\'' | '"')) else {
        return false;
    };
    let inner = &s[..s.len() - 1];
    inner
        .rfind(|c: char| !in_literal(c))
        .is_some_and(|open| open + 1 < inner.len() && inner[open..].starts_with(quote))
}

/// A literal resolved where the program runs.
fn resolve(lit: &str, base: &str) -> String {
    if lit.starts_with('/') {
        normpath(lit)
    } else {
        normpath(&format!("{base}/{lit}"))
    }
}

/// The program with its triple-quoted strings blanked: text a program carries (a suite's body being written, a docstring) names
/// files it does not open - the refusal corpus's 2026-09-05 row writes a suite whose text names a Makefile. The strings are shape's
/// `triple_quoted_spans` (451 T112), where the pattern `(?s)"""(?:\\.|(?!""").)*"""|'''(?:\\.|(?!''').)*'''` tried 2^n readings of
/// the n escapes after a triple quote nothing closes: a heredoc's program holding one and forty escapes held make-only, readme,
/// gate-write and the event log's end past 10 s (measured 2026-11-21, the T112 plan section); a test holds the two equal on every
/// text of up to 5 pieces (`tests.rs`).
fn without_text(body: &str) -> String {
    let (mut text, mut from) = (String::with_capacity(body.len()), 0);
    for (open, close) in triple_quoted_spans(body) {
        text.push_str(&body[from..open]);
        text.push_str("\"\"");
        from = close + 1;
    }
    text + &body[from..]
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
    TAIL_BEFORE.is_match(&body[from..at])
}

// Each `..._BEFORE` pattern ends at `$` past `\s*`, Unicode's `White_Space` as `str::trim_end` drops it, and each `..._AFTER` starts at
// `^`: so each gate reads the end, or the start, of the window it is asked of (451 T96).
static OPEN_BEFORE: Lazy = Lazy::new(|t| t.trim_end().ends_with("open("), || re(r"\bopen\(\s*$"));
static OPEN_AFTER: Lazy = Lazy::new(
    |t| t.trim_start().starts_with([')', ',']),
    || re(r#"^\s*(?:\)|,\s*(?:mode\s*=\s*)?['"]r[bt]?['"]\s*[,)])"#),
);
static PATH_BEFORE: Lazy = Lazy::new(|t| t.trim_end().ends_with("Path("), || re(r"\bPath\(\s*$"));
static PATH_AFTER: Lazy = Lazy::new(
    |t| t.trim_start().starts_with(')'),
    || re(r"^\s*\)\s*\.read_(?:text|bytes)\("),
);
/// Inside the argv list a subprocess call opens, no `]` since: the last line holds a `[` past its last `]`.
static ARGV_BEFORE: Lazy = Lazy::new(
    |t| {
        let line = t.rsplit('\n').next().unwrap_or(t);
        line.rfind('[') > line.rfind(']')
    },
    || re(r"\b(?:run|call|check_call|check_output|Popen)\(\s*\[[^\]\n]*$"),
);
/// A dict's value: `'key': ` before it.
static VALUE_BEFORE: Lazy = Lazy::new(
    |t| t.trim_end().ends_with(':'),
    || re(r#"['"][\w-]+['"]\s*:\s*$"#),
);
/// A module's file, loaded to run (window#53: `spec_from_file_location('m', 'specs/.../measure.py')`, a read).
static SPEC_BEFORE: Lazy = Lazy::new(
    |t| t.trim_end().ends_with(',') && t.contains("spec_from_file_location("),
    || re(r#"\bspec_from_file_location\(\s*['"][^'"]*['"]\s*,\s*$"#),
);
/// A literal after `/` or `+`, or a later argument of `Path(`/`join(` (no parenthesis between); or text, not a path: the first
/// argument of a `re.` function or of a string method (window#280's `re.findall(r"summary.only", ...)`, window#358's
/// `f.endswith(".html")`, a `replace`'s words - round 4 of T33's replay, measured 2026-11-20), or a comparison's (`f ==
/// "SOURCES.html"`, window#358, after5).
static TAIL_BEFORE: Lazy = Lazy::new(tail_could, || {
    re(&format!(
        r"(?:[/+]\s*|[=!]=\s*|\b(?:Path|join)\([^()\n]*,\s*|(?:\bre\.\w+|\.(?:{}))\([^()\n]*?[rbu]?)$",
        METHODS.join("|")
    ))
});
/// The string methods whose first argument is text, not a path: `TAIL_BEFORE`'s, one list for its pattern and its gate.
const METHODS: [&str; 15] = [
    "endswith",
    "startswith",
    "replace",
    "split",
    "rsplit",
    "index",
    "rindex",
    "find",
    "rfind",
    "count",
    "strip",
    "lstrip",
    "rstrip",
    "removeprefix",
    "removesuffix",
];

/// Whether `TAIL_BEFORE` could match `text`: its end a `/`, `+`, `==` or `!=`, or its last line's last parenthesis an open one - a
/// call's argument begun, `Path(`'s or `join(`'s past a `,`, a string method's, or a `re.` function's (`re.` and a word: no
/// whitespace and no ASCII punctuation but `_`, as `\w` holds none).
fn tail_could(text: &str) -> bool {
    let t = text.trim_end();
    if t.ends_with(['/', '+']) || t.ends_with("==") || t.ends_with("!=") {
        return true;
    }
    let line = t.rsplit('\n').next().unwrap_or(t);
    let Some(open) = line.rfind('(').filter(|&i| !line[i..].contains(')')) else {
        return false;
    };
    let name = &line[..open];
    let word = |w: &str| {
        !w.is_empty()
            && !w.contains(|c: char| c.is_whitespace() || (c.is_ascii_punctuation() && c != '_'))
    };
    (t.ends_with(',') && (name.ends_with("Path") || name.ends_with("join")))
        || METHODS
            .iter()
            .any(|m| name.strip_suffix(m).is_some_and(|n| n.ends_with('.')))
        || name.rsplit_once("re.").is_some_and(|(_, w)| word(w))
}

/// Each path a program's literals name, resolved in `dir` (`/` when unknown), that `wanted` takes, handed to `found` in order - every
/// single literal, then every joined pair, then every literal a function of the program's own writes onto a root (`bound`) - until
/// `found` answers false. `wanted` is asked before a literal's uses are read, so a caller's cheap test spares the scan. `placed`
/// (gate-write's and the event log's) takes only a literal that is a path where the shell stands: `shaped`, and not `joined_on` a base
/// the program computes - a reader failing open on a path it cannot resolve, where make-only, fail-closed, counts any literal naming a
/// guard file - and names a literal `bound` places only where it places it, not where the shell stands too.
fn each(
    body: &str,
    dir: Option<&str>,
    reads: bool,
    placed: bool,
    wanted: &dyn Fn(&str) -> bool,
    found: &mut dyn FnMut(String) -> bool,
) {
    let (base, body) = (dir.unwrap_or("/"), without_text(body));
    // a literal holding `$` is a shell variable's text, which the program never expands (and could not be resolved here if it did)
    let path = |lit: &str| !lit.contains('$') && (!placed || shaped(lit));
    let bound = bound(&body);
    // the program with its strings' content and comments blanked, made only when a plain scan of 451 T118 asks for it
    let masked = OnceCell::new();
    // a tested literal is text under `placed`; fail-closed, a read (`reads`) only where the program writes no computed path it
    // could be the landing of (451 T118's plan review: T58's `commits.py`, `f.startswith('rust/guard/src/')` in a program writing nothing)
    let computed = OnceCell::new();
    let text = |quoted| {
        tested(&body, &masked, quoted)
            && (placed || reads && !*computed.get_or_init(|| writes_computed(&body)))
    };
    for (start, lit) in literals(&body) {
        let at = resolve(lit, base);
        let quoted = (start - 1, start + lit.len() + 1);
        // the caller's test before the two scans, so a literal naming no file reaches neither scan's patterns: `joined_on` asked
        // first reached `TAIL_BEFORE` on nearly every literal of every program (see the module's note on what it builds)
        if path(lit)
            && !(placed && bound.iter().any(|(at, _)| *at == start))
            && wanted(&at)
            && !(placed && joined_on(&body, start - 1))
            && !text(quoted)
            && !(reads && only_read(&body, lit, &masked))
            && !found(at)
        {
            return;
        }
    }
    for c in JOINED.captures_iter(&body).map_while(Result::ok) {
        let (a, b) = (
            c.get(2).or_else(|| c.get(4)).map_or("", |m| m.as_str()),
            c.get(6).map_or("", |m| m.as_str()),
        );
        let at = resolve(&format!("{a}/{b}"), base);
        // the pair read whole through its join is a read (451 T118); written, it is named as before
        let quoted = c.get(6).map_or((0, 0), |m| (m.start() - 1, m.end() + 1));
        if path(a)
            && path(b)
            && !b.starts_with('/')
            && wanted(&at)
            && !(reads && chain_read(&body, &masked, quoted))
            && !found(at)
        {
            return;
        }
    }
    for (_, made) in bound {
        let at = resolve(&made, base);
        if path(&made) && wanted(&at) && !found(at) {
            return;
        }
    }
}

/// Each string literal a call hands to a function the program defines once, whose parameter that function writes joined onto a
/// module-level literal root, and the path it writes: its start in `body` (as `literals` gives it) and the path as the program builds
/// it, unresolved (451 T110, found at T92's landing on 2026-11-21: its builder's heredoc `root='<clone>/rust/gate/crates/'`, `def
/// sub(path, ...): p=root+path; ... open(p,'w')`, `sub('plan/src/plan.rs', ...)` wrote three files no event line named, so land-alone's
/// list missed them). The forms: the root a top-level `NAME = '<literal>'` (or `Path('<literal>')`) the program binds nowhere else;
/// the join `+` (the string's own concatenation), `/` (a path's join, as `Path` joins), `os.path.join(..)`, `Path(.., ..)`, or an
/// f-string whose every placeholder is the root or the parameter, each operand the root, the parameter or a literal; the write
/// `open(X, <a mode holding w, a or x>)`, `X.write_text(`, `X.write_bytes(` or `Path(X).write_..(`, X that join or a name the body
/// assigns it once. Everything else fails open, as before: a root the program computes or binds twice, a function defined twice, a
/// `*args` parameter, a parameter the body rebinds to anything but its join, a parameter handed on to another function, another
/// sink. Measured 2026-11-21 (`/tmp/t110/scripts/measure.py`): 0 of T93's 9,646 commands take the shape, all 10 of T92's command's
/// calls do, and 82 literals in 22 of the session's 34,785 subagent Bash calls since 2026-11-12, every one by `+`. Plain code behind a
/// `def ` gate: it builds no pattern (the module's note on what it builds). Beside them, each write whose path joins a root and
/// literals alone (`open(root+'docs/guards.md', 'w')`), which `joined_on` drops as a tail on a base it cannot see: 3 writes in 1 of
/// T93's commands, 36 in 27 of the session's, measured 2026-11-21 (`/tmp/t110/scripts/toplevel.py`); its gate a top-level line that
/// could bind a root.
fn bound(body: &str) -> Vec<(usize, String)> {
    if !body.contains("def ") && !body.lines().any(could_root) {
        return Vec::new();
    }
    let p = Program::new(body);
    let mut out = Vec::new();
    let defs = p.defs();
    for def in &defs {
        for (param, pos) in &def.params {
            for place in p.places(def, param) {
                out.extend(p.calls(def.name, param, *pos, &place));
            }
        }
    }
    // a root any function's parameter shadows is no root of a write the scan cannot place inside or outside that function
    let shadow: Vec<_> = defs.iter().flat_map(|d| d.params.iter().copied()).collect();
    out.extend(p.constants(&shadow));
    out.sort_by_key(|(at, _)| *at);
    out
}

/// Whether a line could bind a root: a name at its start, then `=` and a quote or a `Path`.
fn could_root(line: &str) -> bool {
    line.split_once('=').is_some_and(|(n, v)| {
        name(n.trim_end()) && v.trim_start().starts_with(['\'', '"', 'P', 'p'])
    })
}

/// The first path a program's literals name, resolved in `dir`, that `wanted` takes - the make-only guard's guard file, readme's
/// README, the gate-write guard's file the gate would see (451 T33); `reads` exempts the literals it only reads, `placed` as [`each`].
#[must_use]
pub fn program_names(
    body: &str,
    dir: Option<&str>,
    reads: bool,
    placed: bool,
    wanted: &dyn Fn(&str) -> bool,
) -> Option<String> {
    let mut first = None;
    each(body, dir, reads, placed, wanted, &mut |at| {
        first = Some(at);
        false
    });
    first
}

/// Whether a program writes a path it computes: the target of a write `Program::writes` reads (`open(X, <w, a or x>)`, `X.write_text(`,
/// `X.write_bytes(`) holding a name, or a method write whose receiver it cannot read (`a.b.write_text(`) - so a directory the program
/// names can hold that write (451 T118: window#170's `R = pathlib.Path("research")`, `p = R / path`, `p.write_text(..)`, and
/// refusals#144's `for p in pathlib.Path("l7r").rglob("*.py"): p.write_text(new)`, true writes into the tree that gate-write refuses
/// only by the directory's literal). A writer it does not read - one of `UNREAD_WRITERS`, a dotted `open` with a write mode - counts
/// as one, failing closed (451 T118's plan review: `shutil.copy(a, 'l7r/')` beside a directory literal, refused at HEAD); an `open`
/// whose mode is computed does not.
#[must_use]
pub fn writes_computed(body: &str) -> bool {
    let body = without_text(body);
    let unread = |text: &str| UNREAD_WRITERS.iter().any(|w| text.contains(w));
    if !body.contains("open(") && !body.contains(".write_") && !unread(&body) {
        return false;
    }
    let p = Program::new(&body);
    if unread(&p.mask) || dotted_open_writes(&p) {
        return true;
    }
    let methods = p
        .mask
        .match_indices(".write_text(")
        .chain(p.mask.match_indices(".write_bytes("))
        .any(|(i, _)| p.receiver(i).is_none_or(|at| holds_name(&p, at)));
    methods
        || p.writes((0, body.len()))
            .into_iter()
            .any(|at| holds_name(&p, at))
}

/// The writers whose destination [`writes_computed`] does not read, each a computed write wherever it writes: a copy, a move, a
/// rename, an archive's extraction, a link - CONVENTION, Python's own names, read on the mask so a string naming one is none.
const UNREAD_WRITERS: [&str; 10] = [
    "shutil.copy",
    "shutil.move",
    "copytree(",
    "copyfile(",
    "os.replace(",
    "os.rename(",
    "os.renames(",
    ".extractall(",
    ".rename(",
    ".symlink_to(",
];

/// Whether a dotted `open` takes a literal write mode - `io.open(P, "w")`, `gzip.open(p, 'wt')`, `Path(p).open('w')`, which
/// `Program::writes` leaves to its module - counted a computed write whatever its path (a literal of mode letters alone, with `w`,
/// `a` or `x`: a path holding them, `'/tmp/wax.gz'`, is none).
fn dotted_open_writes(p: &Program) -> bool {
    p.mask.match_indices(".open(").any(|(i, _)| {
        closing(&p.mask, i + 5).is_some_and(|close| {
            split(&p.mask, (i + 6, close), b",").into_iter().any(|at| {
                let (s, e) = trimmed(&p.mask, at);
                let arg = p.text[s..e]
                    .strip_prefix("mode")
                    .map_or(&p.text[s..e], |r| {
                        r.trim_start().trim_start_matches('=').trim_start()
                    });
                let mode = literal_at(arg)
                    .filter(|&n| n == arg.len())
                    .map(|n| &arg[1..n - 1]);
                mode.is_some_and(|m| {
                    m.chars().all(|c| "rwaxbt+".contains(c)) && m.contains(['w', 'a', 'x'])
                })
            })
        })
    })
}

/// Whether a span of a program holds a name, read on its mask: `Path` and `pathlib` are none, nor a string's prefix (`r'..'`,
/// `b'..'`) unless an f-string's whose text holds a placeholder (`f"{M}/x"`; a `{{` read as one, failing closed).
fn holds_name(program: &Program, (start, end): (usize, usize)) -> bool {
    let span = &program.mask[start..end];
    let mut from = 0;
    while let Some(off) = span[from..].find(word) {
        let first = from + off;
        let after = span[first..]
            .find(|c: char| !word(c))
            .map_or(span.len(), |n| first + n);
        let run = &span[first..after];
        let quote = span[after..]
            .chars()
            .next()
            .filter(|&c| c == '\'' || c == '"');
        let prefix = run.len() <= 2 && run.chars().all(|c| "rRbBuUfF".contains(c));
        let name = match quote.filter(|_| prefix) {
            Some(quote) => {
                let opened = start + after + 1;
                let close = span[after + 1..]
                    .find(quote)
                    .unwrap_or(span.len() - after - 1);
                run.contains(['f', 'F']) && program.text[opened..opened + close].contains('{')
            }
            None => !matches!(run, "Path" | "pathlib"),
        };
        if name {
            return true;
        }
        from = after;
    }
    false
}

/// Every path [`program_names`] would name, once each, in its order (451 T96: the event log's `writes`).
#[must_use]
pub fn all_program_names(
    body: &str,
    dir: Option<&str>,
    reads: bool,
    placed: bool,
    wanted: &dyn Fn(&str) -> bool,
) -> Vec<String> {
    let mut all: Vec<String> = Vec::new();
    each(body, dir, reads, placed, wanted, &mut |at| {
        if !all.contains(&at) {
            all.push(at);
        }
        true
    });
    all
}

#[cfg(test)]
mod tests;
