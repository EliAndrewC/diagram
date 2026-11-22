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
//! WHAT IT BUILDS (451 T96): a hook event is a process of its own, so each pattern is a `regex::Lazy`, built only for a text that
//! could match it - its gate a necessary condition, most on the end or the start of the window a scan asks of it - and a program's
//! literals, and each literal's uses, are read by plain code. WHY: every Python program a Bash call ran built the literal pattern,
//! `TRIPLE` and `JOINED`, and a literal naming a file the scans' patterns and one more of its own on every call: 13.1 ms the first
//! read of a program naming no file against 0.11 ms a second, and 7.1 ms every read of one naming 20 files, each pattern 0.26 to
//! 6.1 ms to build first in a process (`JOINED` the most, `TAIL_BEFORE` 3.8 ms), measured 2026-11-21 (`/tmp/t96/ms`: the medians of
//! 31 fresh processes' wall time, a load near 30). The triple-quoted text `TRIPLE` matched is since read by shape's
//! `triple_quoted_spans`, which builds no pattern (451 T112).

use fancy_regex::Regex;

use super::normpath;
use crate::regex::Lazy;
use crate::shape::triple_quoted_spans;

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

/// Whether every use of the literal `lit` in `body` is a read: opened to read, read through `Path`, an element of a subprocess's
/// argv (a hook RUN, not written: window#56, #299, #312, each running `scripts/hooks/house-style-hooks.sh` - refused on T33's first
/// replay, measured 2026-11-20), or a value in a dict (a hook payload's `file_path`: window#267). Each use is `'lit'` or `"lit"`,
/// found as two plain searches where a pattern was built for each literal on every call (451 T96): what `(['"])lit\1` finds, as a
/// literal holds no quote and so no use of the one kind overlaps one of the other.
fn only_read(body: &str, lit: &str) -> bool {
    let (single, double) = (format!("'{lit}'"), format!("\"{lit}\""));
    body.match_indices(&single)
        .chain(body.match_indices(&double))
        .all(|(start, m)| {
            // the 300 characters before it are context enough, and keep each scan short on a long program
            let from = body[..start]
                .char_indices()
                .rev()
                .nth(299)
                .map_or(0, |(i, _)| i);
            let (before, after) = (&body[from..start], &body[start + m.len()..]);
            (OPEN_BEFORE.is_match(before) && OPEN_AFTER.is_match(after))
                || (PATH_BEFORE.is_match(before) && PATH_AFTER.is_match(after))
                || ARGV_BEFORE.is_match(before)
                || VALUE_BEFORE.is_match(before)
                || SPEC_BEFORE.is_match(before)
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
    for (start, lit) in literals(&body) {
        let at = resolve(lit, base);
        // the caller's test before the two scans, so a literal naming no file reaches neither scan's patterns: `joined_on` asked
        // first reached `TAIL_BEFORE` on nearly every literal of every program (see the module's note on what it builds)
        if path(lit)
            && !(placed && bound.iter().any(|(at, _)| *at == start))
            && wanted(&at)
            && !(placed && joined_on(&body, start - 1))
            && !(reads && only_read(&body, lit))
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
        if path(a) && path(b) && !b.starts_with('/') && wanted(&at) && !found(at) {
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

/// One piece of a path a function builds: a literal's text (the root's, or one the program spells) or the parameter.
#[derive(Clone)]
enum Part {
    Text(String),
    Param,
}

/// How a function builds the path it writes from its parameter: its parts, concatenated (`+`, an f-string) or joined as a path (`/`,
/// `os.path.join`, `Path(a, b)`: a part starting with `/` restarts it).
#[derive(Clone)]
struct Place {
    slash: bool,
    parts: Vec<Part>,
}

impl Place {
    /// The path, the parameter bound to the call's literal `lit`.
    fn with(&self, lit: &str) -> String {
        let mut out = String::new();
        for part in &self.parts {
            let v = match part {
                Part::Text(t) => t.as_str(),
                Part::Param => lit,
            };
            if self.slash && v.starts_with('/') {
                out.clear();
            } else if self.slash && !out.is_empty() && !out.ends_with('/') {
                out.push('/');
            }
            out.push_str(v);
        }
        out
    }
}

/// A function the program defines: its name, each parameter a call can bind (its name and its position, `None` keyword-only), and the
/// span of its body.
struct Def<'a> {
    name: &'a str,
    params: Vec<(&'a str, Option<usize>)>,
    body: (usize, usize),
}

/// A program read for its functions: its text (`without_text`'s copy), the same with each string's content `~` and each comment
/// blank (`mask`), and its roots - each top-level name bound once, to a literal, and that literal.
struct Program<'a> {
    text: &'a str,
    mask: String,
    roots: Vec<(&'a str, &'a str)>,
}

/// Whether `c` can be in a Python name.
fn word(c: char) -> bool {
    c.is_alphanumeric() || c == '_'
}

/// Whether `s` is a Python name.
fn name(s: &str) -> bool {
    s.chars().next().is_some_and(|c| !c.is_numeric()) && s.chars().all(word)
}

/// The program byte for byte with each string's content `~` and each comment blank, so its brackets, commas, `def`s and calls are
/// its code's alone (a parenthesis or a `def` inside a string or a comment is neither; gate-write's `masked`, read here as plain code):
/// quotes single, double and triple, a backslash's escape, and a single-quoted string the line ends before it closes.
fn mask(body: &str) -> String {
    let b = body.as_bytes();
    let mut out = b.to_vec();
    let mut i = 0;
    while let Some(&ch) = b.get(i) {
        match ch {
            b'#' => {
                while let Some(o) = out.get_mut(i).filter(|o| **o != b'\n') {
                    *o = b' ';
                    i += 1;
                }
            }
            q @ (b'\'' | b'"') => {
                let triple = b.get(i + 1..i + 3) == Some(&[q, q][..]);
                i += if triple { 3 } else { 1 };
                while let Some(&c) = b.get(i) {
                    let closes = c == q && (!triple || b.get(i + 1..i + 3) == Some(&[q, q][..]));
                    if closes || (!triple && c == b'\n') {
                        i += if closes && triple { 2 } else { 0 };
                        break;
                    }
                    let skip = if c == b'\\' { 2 } else { 1 };
                    for o in out.iter_mut().skip(i).take(skip) {
                        *o = b'~';
                    }
                    i += skip;
                }
            }
            _ => {}
        }
        i += 1;
    }
    // every byte replaced is ASCII and every one replaced is a whole character's, so the copy stays UTF-8
    String::from_utf8(out).unwrap_or_else(|e| unreachable!("{e}"))
}

/// The index of the bracket closing the one at `open`.
fn closing(mask: &str, open: usize) -> Option<usize> {
    let mut depth = 0;
    for (i, c) in mask.bytes().enumerate().skip(open) {
        match c {
            b'(' | b'[' | b'{' => depth += 1,
            b')' | b']' | b'}' => {
                depth -= 1;
                if depth == 0 {
                    return Some(i);
                }
            }
            _ => {}
        }
    }
    None
}

/// The spans of `mask[from..to]` between its `sep` bytes outside brackets.
fn split(mask: &str, (from, to): (usize, usize), sep: &[u8]) -> Vec<(usize, usize)> {
    let (mut out, mut depth, mut at) = (Vec::new(), 0, from);
    for (i, c) in mask.bytes().enumerate().take(to).skip(from) {
        match c {
            b'(' | b'[' | b'{' => depth += 1,
            b')' | b']' | b'}' => depth -= 1,
            _ if depth == 0 && sep.contains(&c) => {
                out.push((at, i));
                at = i + 1;
            }
            _ => {}
        }
    }
    out.push((at, to));
    out
}

/// The span with the whitespace at its ends dropped, read on the mask, so a comment ends a statement as a blank does.
fn trimmed(text: &str, (from, to): (usize, usize)) -> (usize, usize) {
    let s = &text[from..to];
    let start = from + (s.len() - s.trim_start().len());
    (start, start + s.trim().len())
}

impl<'a> Program<'a> {
    fn new(text: &'a str) -> Self {
        let mut p = Program {
            text,
            mask: mask(text),
            roots: Vec::new(),
        };
        for (s, e) in p.statements((0, text.len())) {
            let at_line = s == 0 || p.mask[..s].ends_with('\n');
            let Some((n, rhs)) = p.assigned((s, e)).filter(|_| at_line) else {
                continue;
            };
            let value = p.literal(rhs).or_else(|| {
                p.call(rhs, &["Path", "pathlib.Path"])
                    .filter(|args| args.len() == 1)
                    .and_then(|args| p.literal(args[0]))
            });
            if let Some(v) = value.filter(|_| p.binds((0, text.len()), n) == 1) {
                p.roots.push((n, v));
            }
        }
        p
    }

    /// The statements of a span: its pieces between newlines and `;`, outside brackets, each trimmed, none empty.
    fn statements(&self, span: (usize, usize)) -> Vec<(usize, usize)> {
        split(&self.mask, span, b"\n;")
            .into_iter()
            .map(|s| trimmed(&self.mask, s))
            .filter(|(s, e)| s < e)
            .collect()
    }

    /// `NAME = <rhs>`: the name and the span of what it is bound to.
    fn assigned(&self, (s, e): (usize, usize)) -> Option<(&'a str, (usize, usize))> {
        let eq = s + self.mask[s..e].find('=')?;
        let n = self.text[s..eq].trim_end();
        (name(n) && !self.mask[eq + 1..e].starts_with('='))
            .then(|| (n, trimmed(&self.mask, (eq + 1, e))))
    }

    /// The literal a span is, whole (a quote, a path's characters, the same quote).
    fn literal(&self, (s, e): (usize, usize)) -> Option<&'a str> {
        let t = &self.text[s..e];
        (literal_at(t) == Some(t.len())).then(|| &t[1..t.len() - 1])
    }

    /// The arguments of a span that is wholly a call of one of `callees`.
    fn call(&self, (s, e): (usize, usize), callees: &[&str]) -> Option<Vec<(usize, usize)>> {
        let open = s + self.mask[s..e].find('(')?;
        let callee = self.text[s..open].trim_end();
        (callees.contains(&callee) && closing(&self.mask, open) == Some(e - 1)).then(|| {
            split(&self.mask, (open + 1, e - 1), b",")
                .into_iter()
                .map(|a| trimmed(&self.mask, a))
                .collect()
        })
    }

    /// How many times `n` is bound in a span: assigned (`n =`, `n +=`, `n :=`; a keyword argument `n=` too, failing open), or named
    /// after `def`, `class`, `for`, `as`, `import`, `global` or `nonlocal`.
    fn binds(&self, (from, to): (usize, usize), n: &str) -> usize {
        self.mask[from..to]
            .match_indices(n)
            .filter(|&(i, _)| {
                let (before, after) = (&self.mask[..from + i], &self.mask[from + i + n.len()..]);
                if before.ends_with(|c: char| word(c) || c == '.') || after.starts_with(word) {
                    return false;
                }
                let prior = before.trim_end().rsplit(|c: char| !word(c)).next();
                let rest = after.trim_start().trim_start_matches([
                    '+', '-', '*', '/', '%', '&', '|', '^', '@', '<', '>', ':', '!',
                ]);
                matches!(
                    prior,
                    Some("def" | "class" | "for" | "as" | "import" | "global" | "nonlocal")
                ) || (rest.starts_with('=') && !rest.starts_with("=="))
            })
            .count()
    }

    /// The functions the program defines once (`def NAME(..):` beginning a line), each with its parameters and its body: the rest of
    /// its line, or the lines indented past it.
    fn defs(&self) -> Vec<Def<'a>> {
        let mut out = Vec::new();
        for (s, e) in self.statements((0, self.text.len())) {
            let Some(rest) = self.mask[s..e].strip_prefix("def") else {
                continue;
            };
            let Some(open) = rest
                .starts_with([' ', '\t'])
                .then(|| rest.find('('))
                .flatten()
                .map(|i| s + 3 + i)
            else {
                continue;
            };
            let n = self.text[s + 3..open].trim();
            let Some(close) = closing(&self.mask, open) else {
                continue;
            };
            let colon = split(&self.mask, (close + 1, e), b":")[0].1;
            if !name(n) || colon == e || self.binds((0, self.text.len()), n) != 1 {
                continue;
            }
            let mut params = Vec::new();
            let mut position = Some(0);
            for a in split(&self.mask, (open + 1, close), b",") {
                let a = trimmed(&self.mask, a);
                let t = &self.text[a.0..a.1];
                if t.starts_with('*') {
                    position = None;
                    continue;
                }
                let p = t.split([':', '=']).next().unwrap_or(t).trim();
                if name(p) {
                    params.push((p, position));
                    position = position.map(|p| p + 1);
                }
            }
            out.push(Def {
                name: n,
                params,
                body: self.body_of(s, colon),
            });
        }
        out
    }

    /// A def's body: the rest of its line past the colon if it holds code (its `;`s' statements too), else every line after it indented
    /// past the def's own.
    fn body_of(&self, s: usize, colon: usize) -> (usize, usize) {
        let eol = split(&self.mask, (colon + 1, self.text.len()), b"\n")[0].1;
        if !self.mask[colon + 1..eol].trim().is_empty() {
            return (colon + 1, eol);
        }
        let indent = s - self.mask[..s].rfind('\n').map_or(0, |i| i + 1);
        let mut end = eol;
        for (ls, le) in split(&self.mask, (eol, self.text.len()), b"\n")
            .into_iter()
            .skip(1)
        {
            let line = &self.mask[ls..le];
            if !line.trim().is_empty() && line.len() - line.trim_start().len() <= indent {
                break;
            }
            end = le;
        }
        (eol, end)
    }

    /// Each place `def` writes its parameter `param` onto a root: each write in its body whose path is the parameter joined onto a
    /// root, or a name the body binds once to that join. A parameter the body rebinds counts only as the name of its one join.
    fn places(&self, def: &Def, param: &str) -> Vec<Place> {
        let mut names: Vec<(&str, Place)> = Vec::new();
        for st in self.statements(def.body) {
            if let Some((n, rhs)) = self.assigned(st) {
                if let Some(place) = self
                    .join(rhs, Some(param), &def.params)
                    .filter(|_| self.binds(def.body, n) == 1)
                {
                    names.push((n, place));
                }
            }
        }
        let rebound = self.binds(def.body, param) > 0;
        let local = |n: &str| names.iter().find(|(m, _)| *m == n).map(|(_, p)| p.clone());
        let mut out = Vec::new();
        for path in self.writes(def.body) {
            let t = &self.text[path.0..path.1];
            let place = if name(t) {
                local(t)
            } else if rebound {
                None
            } else {
                self.join(path, Some(param), &def.params)
            };
            out.extend(place);
        }
        out
    }

    /// Each write whose path joins a root and literals alone, no parameter (`open(root+'x.rs', 'w')`): where its path starts, and the
    /// path. The literal's own reading drops it as a tail on a base it cannot see (`joined_on`), so here is where `placed` names it.
    /// A name the program binds once to such a join, and no parameter's, stands for it (`p = root + 'x.rs'; open(p, 'w')`: 18 writes
    /// in 8 of the session's commands, 0 of T93's, measured 2026-11-21, `/tmp/t110/scripts/toplevel-named.py`).
    fn constants(&self, shadow: &[(&str, Option<usize>)]) -> Vec<(usize, String)> {
        let all = (0, self.text.len());
        let mut names: Vec<(&str, Place)> = Vec::new();
        for st in self.statements(all) {
            if let Some((n, rhs)) = self.assigned(st) {
                // the join first: the count of its bindings scans the whole program
                let free =
                    |_: &Place| self.binds(all, n) == 1 && !shadow.iter().any(|(p, _)| *p == n);
                names.extend(self.join(rhs, None, shadow).filter(free).map(|p| (n, p)));
            }
        }
        let mut out = Vec::new();
        for path in self.writes(all) {
            let t = &self.text[path.0..path.1];
            let place = if name(t) {
                names.iter().find(|(m, _)| *m == t).map(|(_, p)| p.clone())
            } else {
                self.join(path, None, shadow)
            };
            out.extend(place.map(|p| (path.0, p.with(""))));
        }
        out
    }

    /// The span of each path a write in `span` writes: `open(X, <w, a or x>)`, `X.write_text(`, `X.write_bytes(`.
    fn writes(&self, span: (usize, usize)) -> Vec<(usize, usize)> {
        let m = &self.mask[span.0..span.1];
        let mut out = Vec::new();
        for (i, _) in m.match_indices("open(") {
            let at = span.0 + i;
            if self.mask[..at].ends_with(|c: char| word(c) || c == '.') {
                continue;
            }
            let Some(close) = closing(&self.mask, at + 4) else {
                continue;
            };
            let args: Vec<_> = split(&self.mask, (at + 5, close), b",")
                .into_iter()
                .map(|a| trimmed(&self.mask, a))
                .collect();
            let mode = args.iter().skip(1).find_map(|&(s, e)| {
                let t = &self.text[s..e];
                let t = t
                    .strip_prefix("mode")
                    .map_or(Some(t), |r| r.trim_start().strip_prefix('='));
                t.and_then(|t| literal_at(t.trim()).map(|_| t.trim()))
            });
            if mode.is_some_and(|t| t.contains(['w', 'a', 'x'])) {
                out.push(args[0]);
            }
        }
        for (i, _) in m
            .match_indices(".write_text(")
            .chain(m.match_indices(".write_bytes("))
        {
            out.extend(self.receiver(span.0 + i));
        }
        out
    }

    /// What a method is called on, ending at `dot`: a name, a parenthesized expression, or a call of `Path` - none for another call.
    fn receiver(&self, dot: usize) -> Option<(usize, usize)> {
        let end = self.mask[..dot].trim_end().len();
        if self.mask[..end].ends_with(')') {
            let mut depth = 0;
            let (open, _) = self.mask[..end].char_indices().rev().find(|&(_, c)| {
                depth += match c {
                    ')' | ']' | '}' => 1,
                    '(' | '[' | '{' => -1,
                    _ => 0,
                };
                depth == 0
            })?;
            // the dotted name the parenthesis follows with nothing between: none is a parenthesized expression
            let start = self.mask[..open]
                .trim_end_matches(|c: char| word(c) || c == '.')
                .len();
            return match &self.text[start..open] {
                "" | "Path" | "pathlib.Path" => Some((start, end)),
                _ => None,
            };
        }
        let start = self.mask[..end].trim_end_matches(word).len();
        (start < end && !self.mask[..start].ends_with('.')).then_some((start, end))
    }

    /// The place a span builds from `param` (none: from no parameter) and a root: a join of operands, one the parameter where there is
    /// one, and one or more a root or a literal. `shadow` holds the parameters whose names are no root's here.
    fn join(
        &self,
        span: (usize, usize),
        param: Option<&str>,
        shadow: &[(&str, Option<usize>)],
    ) -> Option<Place> {
        let (s, e) = trimmed(&self.mask, span);
        let m = &self.mask[s..e];
        if m.starts_with('(') && closing(&self.mask, s) == Some(e - 1) {
            return self.join((s + 1, e - 1), param, shadow);
        }
        let (slash, operands) = if let Some(args) = self.call((s, e), &["Path", "pathlib.Path"]) {
            if let [one] = args[..] {
                return self.join(one, param, shadow);
            }
            (true, args)
        } else if let Some(args) = self.call((s, e), &["os.path.join", "path.join", "join"]) {
            (true, args)
        } else if let Some(parts) = self.fstring((s, e), param, shadow) {
            return Some(parts);
        } else {
            let plus = split(&self.mask, (s, e), b"+");
            let slash = split(&self.mask, (s, e), b"/");
            match (plus.len(), slash.len()) {
                (1, n) if n > 1 && !m.contains("//") => (true, slash),
                (n, 1) if n > 1 => (false, plus),
                _ => return None,
            }
        };
        let parts = operands
            .into_iter()
            .map(|o| self.operand(o, param, shadow))
            .collect::<Option<Vec<_>>>()?;
        Self::valid(Place { slash, parts }, param.is_some())
    }

    /// A place of two parts or more, one of them the parameter where there is one (`param`), else none.
    fn valid(place: Place, param: bool) -> Option<Place> {
        let params = place
            .parts
            .iter()
            .filter(|p| matches!(p, Part::Param))
            .count();
        (params == usize::from(param) && place.parts.len() > 1).then_some(place)
    }

    /// One operand of a join: the parameter, a root (no parameter in `shadow` of its name), a literal, or `Path(` one of them `)`.
    fn operand(
        &self,
        span: (usize, usize),
        param: Option<&str>,
        shadow: &[(&str, Option<usize>)],
    ) -> Option<Part> {
        let (s, e) = trimmed(&self.mask, span);
        let t = &self.text[s..e];
        if param == Some(t) {
            return Some(Part::Param);
        }
        if let Some(v) = self.root(t, shadow) {
            return Some(Part::Text(v.to_owned()));
        }
        if let Some(lit) = self.literal((s, e)) {
            return Some(Part::Text(lit.to_owned()));
        }
        match self.call((s, e), &["Path", "pathlib.Path"])?[..] {
            [one] => self.operand(one, param, shadow),
            _ => None,
        }
    }

    /// The literal a root name is bound to, where no parameter in `shadow` has that name.
    fn root(&self, n: &str, shadow: &[(&str, Option<usize>)]) -> Option<&'a str> {
        let shadowed = shadow.iter().any(|(p, _)| *p == n);
        self.roots
            .iter()
            .find(|(r, _)| *r == n && !shadowed)
            .map(|(_, v)| *v)
    }

    /// An f-string the span wholly is, each placeholder a bare name - the parameter or a root - and its text between: a concatenation.
    fn fstring(
        &self,
        (s, e): (usize, usize),
        param: Option<&str>,
        shadow: &[(&str, Option<usize>)],
    ) -> Option<Place> {
        let t = &self.text[s..e];
        let quote = t
            .strip_prefix(['f', 'F'])?
            .chars()
            .next()
            .filter(|q| matches!(q, '\'' | '"'))?;
        let inner = t[2..].strip_suffix(quote)?;
        if self.mask[s + 2..e - 1].contains(['\'', '"']) {
            return None;
        }
        let mut parts = Vec::new();
        let mut rest = inner;
        while let Some(open) = rest.find('{') {
            let close = open + rest[open..].find('}')?;
            let (text, n) = (&rest[..open], &rest[open + 1..close]);
            if text.contains('}') {
                return None;
            }
            if !text.is_empty() {
                parts.push(Part::Text(text.to_owned()));
            }
            parts.push(if param == Some(n) {
                Part::Param
            } else {
                Part::Text(self.root(n, shadow)?.to_owned())
            });
            rest = &rest[close + 1..];
        }
        if rest.contains('}') {
            return None;
        }
        if !rest.is_empty() {
            parts.push(Part::Text(rest.to_owned()));
        }
        Self::valid(
            Place {
                slash: false,
                parts,
            },
            param.is_some(),
        )
    }

    /// Each call of the function `f` that hands its parameter `param` (at `pos`, or by keyword) a literal: the literal's start and the
    /// path `place` builds from it.
    fn calls(
        &self,
        f: &str,
        param: &str,
        pos: Option<usize>,
        place: &Place,
    ) -> Vec<(usize, String)> {
        let mut out = Vec::new();
        for (i, _) in self.mask.match_indices(f) {
            let before = &self.mask[..i];
            let after = self.mask[i + f.len()..].trim_start();
            if before.ends_with(|c: char| word(c) || c == '.')
                || before.trim_end().ends_with("def")
                || !after.starts_with('(')
            {
                continue;
            }
            let open = self.mask.len() - after.len();
            let Some(close) = closing(&self.mask, open) else {
                continue;
            };
            let mut at = Some(0);
            for a in split(&self.mask, (open + 1, close), b",") {
                let (s, e) = trimmed(&self.mask, a);
                let value = match self.assigned((s, e)) {
                    Some((kw, v)) => (kw == param).then_some(v),
                    None if self.text[s..e].starts_with('*') => {
                        at = None;
                        None
                    }
                    None => {
                        let here = at.is_some() && at == pos;
                        at = at.map(|n| n + 1);
                        here.then_some((s, e))
                    }
                };
                if let Some((v, lit)) = value.and_then(|v| Some((v, self.literal(v)?))) {
                    out.push((v.0 + 1, place.with(lit)));
                }
            }
        }
        out
    }
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
