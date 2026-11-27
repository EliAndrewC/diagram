//! Where a command's writes land (`scripts/hooks/lib/hm_tree.py` - feature 449 T010 decision (a)): the effective directory walked
//! through the command's own `cd`s, variables and subshells, every write classified by where it lands - the mirror, a clone or
//! elsewhere - and a write that lands in the mirror by where the shell stands rewritten into the session's clone, the rewrite
//! re-judged so it never returns a command it would refuse. Each pattern is the Python's verbatim; the reasons stand in its
//! comments, kept in git history.

use std::collections::HashMap;
use std::path::{Component, Path, PathBuf};

use fancy_regex::{Captures, Regex};

use super::regex::Lazy;
use super::shape::strip_heredocs;

mod bind;
mod git;
mod make_dir;
pub mod program;
mod py_c;
mod python;
mod quoted;
mod split;
mod verdict;

use python::{
    carry_heredocs, program_of, program_reads, python_c, stdin_program, Program, Stdin,
    HEREDOC_WORD, PYTHON,
};
use quoted::{blanked, quotes_to_paths, strip_quote_chars, unheld};
use split::{segments, Piece};
pub use verdict::{context_line, explain, judge, Verdict};
#[cfg(test)]
use {
    python::PYTHON_C_BEFORE,
    quoted::{held, pairs_within, plain_quote_body},
};

fn re(pattern: &str) -> Regex {
    crate::regex::build(pattern).unwrap_or_else(|e| unreachable!("a guard's own pattern: {e}"))
}

const FILE_TOOLS_ALL: [&str; 12] = [
    "vim", "vi", "nano", "emacs", "tee", "touch", "mkdir", "rmdir", "rm", "mv", "chmod", "chown",
];
/// The tools whose LAST argument is what they write: `rsync`'s destination as `cp`'s (T227).
const FILE_TOOLS_LAST: [&str; 4] = ["cp", "ln", "install", "rsync"];
const WRAPPERS: [&str; 9] = [
    "sudo", "nohup", "setsid", "env", "command", "exec", "time", "nice", "builtin",
];

// Each pattern of the walk is built only for a text that could match it (`Lazy`, 451 T97): its gate a literal every match holds.
/// An assignment at a command's start - a loop's, an `if`'s and a function's body's too (451 T79's second round: `do
/// D=/tmp/k-$q; mkdir -p $D` was read as nothing known), `export`, `local`, `declare`, `typeset` and `readonly` alike. Its opening
/// was `(?:^|[;&|\n(]|(?<!\$)\{|\b(?:do|then|else)\s)`: the `(?<!\$)` and the `\b` are read by `assignments`, so the pattern runs
/// in the regex crate's automaton, not fancy-regex's backtracking machine, which takes a word boundary as it takes a lookaround
/// (451 T129; `tests/looks.rs` holds the two equal).
static ASSIGN: Lazy = Lazy::new(
    |t| t.contains('='),
    || {
        re(
            r#"(?:^|[;&|\n(]|\{|(?:do|then|else)\s)\s*(?:(?:export|local|declare|typeset|readonly)\s+(?:-\w+\s+)*)?([A-Za-z_]\w*)=(?:"([^"\n]*)"|'([^'\n]*)'|([^\s;&|)]*))"#,
        )
    },
);

/// Each assignment of `text`, in order, as `ASSIGN` with its `(?<!\$)` and `\b` read them: the leftmost match from where the last
/// ended, a match the look before its start refuses tried again a character on (its first is a `{`, `d`, `t` or `e`, one byte).
pub(super) fn assignments(text: &str) -> impl Iterator<Item = Captures<'_>> {
    let r = ASSIGN.on(text);
    let mut at = 0;
    std::iter::from_fn(move || {
        while let Some(c) = r?.captures_from_pos(text, at).ok().flatten() {
            let whole = c.get(0).map_or(text.len()..text.len(), |m| m.range());
            if look_refuses(text, whole.start, true) {
                at = whole.start + 1;
                continue;
            }
            at = whole.end;
            return Some(c);
        }
        None
    })
}

/// Whether the look before a match's start refuses it, for a pattern whose openings are a separator, a `{` and a `do`, `then` or
/// `else`, each told by the match's first character: the word's `\b`, refusing a word character before it, and with `brace` the
/// `{`'s `(?<!\$)`, refusing a `$` before it. The text's first character has nothing before it, so no look refuses there.
pub(super) fn look_refuses(text: &str, start: usize, brace: bool) -> bool {
    let before = text[..start].chars().next_back();
    match text.as_bytes().get(start) {
        Some(b'{') => brace && before == Some('$'),
        Some(b'd' | b't' | b'e') => before.is_some_and(is_word),
        _ => false,
    }
}

/// A word character as a pattern's `\w` and `\b` read it - Unicode's, so `é` and a combining mark are and `²` is not.
pub(super) fn is_word(c: char) -> bool {
    if c.is_ascii() {
        c.is_ascii_alphanumeric() || c == '_'
    } else {
        WORD.is_match(c.encode_utf8(&mut [0; 4]))
    }
}
/// A word character beyond ASCII (`is_word`); no gate, a character `is_word` holds alone reaches it.
static WORD: Lazy = Lazy::new(|_| true, || re(r"^\w$"));
static VAR: Lazy = Lazy::new(|t| t.contains('$'), || re(r"\$\{(\w+)\}|\$(\w+)"));
/// A `\` and the newline after it, which bash drops so the line goes on, past an even run of `\` before it - an escaped backslash,
/// after which the newline ends the command (451 T79: the walk read `cp /tmp/a \` and the mirror's `b` on the next line as two
/// commands, the write of `b` unseen, observed 2026-11-21). It was `(?<!\\)((?:\\\\)*)\\\n`: the lookbehind is read by `joined`,
/// so the pattern runs in the regex crate's automaton (451 T129).
static CONTINUED: Lazy = Lazy::new(|t| t.contains("\\\n"), || re(r"((?:\\\\)*)\\\n"));
/// An assignment's value that is a `$(mktemp ...)` (or backquoted), its arguments the capture (451 T79). It was `...mktemp\b(...`:
/// the `\b` is read by `mktemp_call`, so the pattern runs in the regex crate's automaton (451 T129).
static MKTEMP: Lazy = Lazy::new(
    |t| t.contains("mktemp"),
    || re(r#"^["']?(?:\$\(|`)\s*mktemp([^()`\n]*?)\s*(?:\)|`)"#),
);

/// The `$(mktemp ...)` a value opens with, as `MKTEMP` with its `\b` read it: none where a word character follows `mktemp`, the
/// pattern's one start (`^`) and the word's one place in it leaving nowhere else to try.
fn mktemp_call(value: &str) -> Option<Captures<'_>> {
    let c = MKTEMP.captures(value)?;
    let after = c.get(1).and_then(|m| value[m.start()..].chars().next());
    (!after.is_some_and(is_word)).then_some(c)
}
/// An assignment's value that is a `$(dirname ...)` or `$(basename ...)`, its text the capture (451 T79's second round).
static DIR_BASE: Lazy = Lazy::new(
    |t| t.contains("dirname") || t.contains("basename"),
    || re(r#"^["']?(?:\$\(|`)\s*((?:dirname|basename)\s[^()`\n]*?)\s*(?:\)|`)"#),
);
/// A redirect's target, the capture: `(?<![<>])\d?>{1,2}\|?\s*([^\s;&|()<>]+)` with its lookbehind read by `redirects`, so the
/// pattern runs in the regex crate's automaton, not fancy-regex's backtracking machine (451 T83: 0.50 G instructions fewer over
/// T79's ux corpus, the walk's 59.81 G to 59.31 G, the scan itself 0.12 G in 41,052 calls, measured 2026-11-21 under callgrind).
static REDIRECT: Lazy = Lazy::new(
    |t| t.contains('>'),
    || re(r"\d?>{1,2}\|?\s*([^\s;&|()<>]+)"),
);

/// Each redirect target of a segment, as `(?<![<>])` and `REDIRECT` read them together: the leftmost match from where the last
/// ended whose start no `<` or `>` precedes, a match a `<` or `>` precedes tried again a character on.
fn redirects(seg: &str) -> Vec<&str> {
    let mut found = Vec::new();
    let Some(r) = REDIRECT.on(seg) else {
        return found;
    };
    let mut at = 0;
    while let Some(c) = r.captures_from_pos(seg, at).ok().flatten() {
        let whole = c.get(0).map_or(seg.len()..seg.len(), |m| m.range());
        if seg[..whole.start].ends_with(['<', '>']) {
            at = whole.start + seg[whole.start..].chars().next().map_or(1, char::len_utf8);
            continue;
        }
        found.push(c.get(1).map_or("", |g| g.as_str()));
        at = whole.end;
    }
    found
}
static FUNCTION_DEF: Lazy = Lazy::new(|t| t.contains('('), || re(r"^\s*[\w-]+\s*\(\s*\)"));
static DUP_FD: Lazy = Lazy::new(|t| t.contains(">&"), || re(r"\d*>&[0-9-]"));
static DEV_NULL: Lazy = Lazy::new(|t| t.contains("/dev/null"), || re(r"\d*>\s*/dev/null"));
static ASSIGNMENT_WORD: Lazy = Lazy::new(|t| t.contains('='), || re(r"^[A-Za-z_]\w*="));
/// A chmod mode: octal, or symbolic clauses (`u+x`, `go-w,a+r`, `-x`); no gate, a chmod's words alone reach it.
static CHMOD_MODE: Lazy = Lazy::new(
    |_| true,
    || re(r"^(?:[0-7]{1,4}|[ugoa]*[-+=][rwxXstugo]*(?:,[ugoa]*[-+=][rwxXstugo]*)*)$"),
);
/// Python's `posixpath.normpath`.
#[must_use]
pub fn normpath(path: &str) -> String {
    if path.is_empty() {
        return ".".to_owned();
    }
    let slashes = if path.starts_with("//") && !path.starts_with("///") {
        2
    } else {
        usize::from(path.starts_with('/'))
    };
    let mut out: Vec<&str> = Vec::new();
    for comp in path.split('/') {
        if comp.is_empty() || comp == "." {
            continue;
        }
        if comp != ".." || (slashes == 0 && out.is_empty()) || out.last() == Some(&"..") {
            out.push(comp);
        } else if !out.is_empty() {
            out.pop();
        }
    }
    let joined = format!("{}{}", "/".repeat(slashes), out.join("/"));
    if joined.is_empty() {
        ".".to_owned()
    } else {
        joined
    }
}

/// Python's `posixpath.join` of two parts.
fn join(a: &str, b: &str) -> String {
    if b.starts_with('/') || a.is_empty() {
        b.to_owned()
    } else if a.ends_with('/') {
        format!("{a}{b}")
    } else {
        format!("{a}/{b}")
    }
}

/// Python's `os.path.relpath` of two absolute paths.
fn relpath(path: &str, start: &str) -> String {
    let (p, s) = (normpath(path), normpath(start));
    let pc: Vec<&str> = p.split('/').filter(|c| !c.is_empty()).collect();
    let sc: Vec<&str> = s.split('/').filter(|c| !c.is_empty()).collect();
    let common = pc.iter().zip(&sc).take_while(|(a, b)| a == b).count();
    let parts: Vec<&str> = std::iter::repeat_n("..", sc.len() - common)
        .chain(pc[common..].iter().copied())
        .collect();
    if parts.is_empty() {
        ".".to_owned()
    } else {
        parts.join("/")
    }
}

/// A command whose heredoc bodies are carried out (`carry_heredocs`) as the walk splits it.
fn sanitize(carried: &str, programs: Vec<Program>) -> (String, Vec<Program>) {
    let (text, programs) = quotes_to_paths(carried, programs);
    // after the heredoc bodies and the quoted strings are out of the text, so a `\` at the end of a body's line is the body's
    let text = joined(&text);
    let text = DUP_FD.replace_all(&text, " ");
    (DEV_NULL.replace_all(&text, " ").into_owned(), programs)
}

/// The text with each `\`-continued line joined to the next, as bash reads it (451 T79): each match of `CONTINUED` whose start no
/// `\` precedes gives way to its run of escaped backslashes, a match a `\` precedes tried again a character on.
fn joined(text: &str) -> String {
    let Some(r) = CONTINUED.on(text) else {
        return text.to_owned();
    };
    let (mut out, mut from, mut at) = (String::new(), 0, 0);
    while let Some(c) = r.captures_from_pos(text, at).ok().flatten() {
        let whole = c.get(0).map_or(text.len()..text.len(), |m| m.range());
        if text[..whole.start].ends_with('\\') {
            at = whole.start + 1;
            continue;
        }
        out.push_str(&text[from..whole.start]);
        out.push_str(c.get(1).map_or("", |m| m.as_str()));
        (from, at) = (whole.end, whole.end);
    }
    out + &text[from..]
}

type Env = HashMap<String, String>;

/// Where `mktemp` with these arguments makes its file or directory (451 T79): the temp directory - `$TMPDIR`, the command's own or
/// the process's, else `/tmp` - with no template, `-p DIR` or `--tmpdir=DIR` in its place (`-t` preferring `$TMPDIR` to `-p`), a
/// template with neither the path it names; None where that is relative - it lands where the shell stands as mktemp runs, which an
/// assignment's reading does not know. Measured 2026-11-21 (coreutils `mktemp -u` on each form, `TMPDIR` set and unset): no
/// template made `$TMPDIR/tmp.XXXXXXXXXX` (`/tmp/...` unset), `-p D` with or without one `D/...`, `-t` and `--tmpdir` with one
/// `$TMPDIR/...` (`-t -p D` too), a bare relative template a name in the cwd.
fn mktemp_place(args: &str, env: &Env, home: &str) -> Option<String> {
    let mut words = args.split_whitespace().map(strip_quote_chars);
    let (mut dir, mut tmpdir, mut t_flag, mut template) = (None, false, false, None);
    while let Some(w) = words.next() {
        if let Some(d) = w.strip_prefix("--tmpdir=") {
            (dir, tmpdir) = (Some(d), true);
        } else if w == "--tmpdir" {
            tmpdir = true;
        } else if w.starts_with("--") {
        } else if let Some(cluster) = w.strip_prefix('-').filter(|c| !c.is_empty()) {
            t_flag |= cluster.contains('t');
            if let Some(k) = cluster.find('p') {
                let glued = &cluster[k + 1..];
                dir = if glued.is_empty() {
                    words.next()
                } else {
                    Some(glued)
                };
                tmpdir = true;
            }
        } else {
            template = Some(w);
        }
    }
    let temp = env
        .get("TMPDIR")
        .cloned()
        .or_else(|| crate::env::opt("TMPDIR"))
        .filter(|d| !d.is_empty());
    let dir = dir.map(str::to_owned);
    let base = if t_flag { temp.or(dir) } else { dir.or(temp) };
    let place = match template {
        Some(t) if !tmpdir && !t_flag => t.to_owned(),
        t => join(
            &base.unwrap_or_else(|| "/tmp".to_owned()),
            t.unwrap_or("tmp.XXXXXXXXXX"),
        ),
    };
    expand(&place, env, home)
        .filter(|p| p.starts_with('/'))
        .map(|p| normpath(&p))
}

/// A token with its variables and `~` substituted, or None where something in it cannot be (`_expand`).
fn expand(token: &str, env: &Env, home: &str) -> Option<String> {
    let token = substituted(token, env, home);
    (!token.contains('$') && !token.contains('`')).then_some(token)
}

/// A token with every variable the command sets, and `~`, substituted; the rest left as written.
fn substituted(token: &str, env: &Env, home: &str) -> String {
    let word = unheld(token);
    let token: &str = &word;
    let mut token = token
        .strip_prefix('~')
        .map_or_else(|| token.to_owned(), |rest| format!("{home}{rest}"));
    for _ in 0..6 {
        if !token.contains('$') {
            break;
        }
        token = VAR
            .replace_all(&token, |c: &Captures| {
                let name = c.get(1).or_else(|| c.get(2)).map_or("", |m| m.as_str());
                env.get(name)
                    .cloned()
                    .unwrap_or_else(|| c.get(0).map_or("", |m| m.as_str()).to_owned())
            })
            .into_owned();
    }
    token
}

/// What the walk knows of a place it cannot resolve (451 T79), for `settled`; a resolved place carries `Shell`, never read.
#[derive(Debug, Clone, PartialEq, Eq)]
enum Known {
    /// Its word is whole and relative: only where the shell stands is unknown (after a `cd` the walk cannot read).
    Shell,
    /// The start of it, absolute, up to the first part the walk cannot read: `$R/out.$n` with `R=/tmp/r` is `/tmp/r/out.`.
    Under(String),
    /// Nothing: its word begins with what the walk cannot read (`$X/b`, a loop's variable, `$(dirname $F)`).
    Nothing,
}

/// What the walk knows of a write word it cannot resolve (451 T79): its part before the first variable the command does not set,
/// a relative one resolved where the shell stands.
fn known_place(token: &str, env: &Env, home: &str, eff: Option<&str>) -> Known {
    let word = substituted(strip_quote_chars(token), env, home);
    let Some(cut) = word.find(['$', '`']) else {
        return Known::Shell;
    };
    let literal = &word[..cut];
    if literal.is_empty() {
        return Known::Nothing;
    }
    let (dir, partial) = literal.rsplit_once('/').map_or((".", literal), |(d, p)| {
        (if d.is_empty() { "/" } else { d }, p)
    });
    match resolve(dir, env, home, eff) {
        Some(d) if d == "/" => Known::Under(format!("/{partial}")),
        Some(d) => Known::Under(format!("{d}/{partial}")),
        None => Known::Shell,
    }
}

/// Where a place the walk knows only the start of lies: the mirror or a clone where it starts in one, elsewhere where it starts
/// outside the mirror's tree, and None where the mirror could lie under it (`/$X/b`) - nothing known of it after all.
fn class_under(start: &str, main: &str) -> Option<&'static str> {
    if start.starts_with(&format!("{main}/.clones/")) {
        Some("clone")
    } else if start.starts_with(&format!("{main}/")) {
        Some("main")
    } else if main.starts_with(start) {
        None
    } else {
        Some("elsewhere")
    }
}

/// THE ONE RULE for a place the walk cannot resolve, the same for every tool - a redirect's, a `cp`'s and a git form's alike (451
/// T79; before, a `cp`'s went where the shell was last known whatever the walk knew of it, and one of T50's twelve git forms was
/// not placed at all): what the walk knows of it decides. A place it knows the start of lies where that start does; what it knows
/// nothing of - a word led by a substitution it cannot run, a name read from input, a start the mirror lies under (`/$X`) - lands
/// where the shell was last KNOWN to be (spec 204's D6, so the precision cannot become a bypass: `cd $(somewhere) && git commit`,
/// and `R=$(git rev-parse --show-toplevel); echo x > $R/f`, its plan review's probe of 2026-11-21). T79's first round read a word
/// nothing is known of as not the mirror's, which let five of its review's probes write the mirror standing in it; the scratch
/// writes it rescued are resolved from the text instead (`bind`: a loop's values, a name no one assigns empty, `$(dirname X)`).
fn settled(path: Option<&str>, known: &Known, hint: &'static str, main: &str) -> &'static str {
    let last_known = if hint == "main" { "main" } else { "elsewhere" };
    match (classify(path, main), known) {
        ("unknown", Known::Under(start)) => class_under(start, main).unwrap_or(last_known),
        ("unknown", _) => last_known,
        (class, _) => class,
    }
}

/// Where a `cd` leaves the shell, for the hint (451 T79's one rule for the shell's own place): where it resolves, under the start
/// the walk knows, or None - nothing known of it - which leaves the hint where the shell was last known (spec 204's D6).
fn cd_class(eff: Option<&str>, known: Option<Known>, main: &str) -> Option<&'static str> {
    match (eff, known) {
        (Some(_), _) => Some(classify(eff, main)),
        (None, Some(Known::Under(start))) => class_under(&start, main),
        _ => None,
    }
}

/// `NAME=value` assignments at command positions, resolved through each other in order (`_env_from`).
fn env_from(cmd: &str, start: Option<&str>, home: &str) -> Env {
    // `OLDPWD` is unset in the Bash tool's shell until a `cd` sets it, which the walk does (read 2026-11-21)
    let mut env = Env::from([
        ("HOME".to_owned(), home.to_owned()),
        ("OLDPWD".to_owned(), String::new()),
    ]);
    if let Some(c) = start {
        env.insert("PWD".to_owned(), c.to_owned());
    }
    // shape's heredoc pattern built only where a heredoc could open: every match of it holds `<<` (451 T97)
    let text = joined(&if cmd.contains("<<") {
        strip_heredocs(cmd)
    } else {
        cmd.to_owned()
    });
    for c in assignments(&text) {
        let Some(named) = c.get(1) else { continue };
        let value = (2..=4)
            .find_map(|i| c.get(i))
            .map_or("", |m| m.as_str())
            .to_owned();
        // a `$(mktemp ...)` is the place mktemp makes (451 T79: `T=$(mktemp -d); git clone -q . $T/clone` standing in the mirror,
        // T50's tx#63, was read toward the mirror, observed 2026-11-21)
        let made = mktemp_call(&text[named.end() + 1..])
            .and_then(|k| mktemp_place(k.get(1).map_or("", |m| m.as_str()), &env, home))
            .or_else(|| {
                DIR_BASE
                    .captures(&text[named.end() + 1..])
                    .and_then(|k| bind::dir_base(k.get(1).map_or("", |m| m.as_str()), &env, home))
            });
        let expanded = made.unwrap_or_else(|| expand(&value, &env, home).unwrap_or(value));
        env.insert(named.as_str().to_owned(), expanded);
    }
    env
}

/// Each `$(mktemp ...)` that stands inside a word, its place under the name of the `$__sub_<n>__` that stands for it (451 T79).
fn mktemp_words(env: &mut Env, subs: &[String], home: &str) {
    for (n, sub) in subs.iter().enumerate() {
        let args = sub
            .trim_start()
            .strip_prefix("mktemp")
            .filter(|a| a.is_empty() || a.starts_with(char::is_whitespace));
        let place = args.map_or_else(
            || bind::dir_base(sub, env, home),
            |a| mktemp_place(a, env, home),
        );
        if let Some(place) = place {
            env.insert(format!("__sub_{n}__"), place);
        }
    }
}

/// A path token as an absolute, normalized path, or None where it cannot be known (`_resolve`).
fn resolve(token: &str, env: &Env, home: &str, effective: Option<&str>) -> Option<String> {
    let expanded = expand(strip_quote_chars(token), env, home).filter(|e| !e.is_empty())?;
    if expanded.starts_with('/') {
        return Some(normpath(&expanded));
    }
    effective.map(|e| normpath(&join(e, &expanded)))
}

/// The mirror outside its `.clones`, a clone, elsewhere, or unknown (`classify`).
#[must_use]
pub fn classify(path: Option<&str>, main: &str) -> &'static str {
    let Some(path) = path else {
        return "unknown";
    };
    let clones = format!("{main}/.clones");
    if path == clones || path.starts_with(&format!("{clones}/")) {
        "clone"
    } else if path == main || path.starts_with(&format!("{main}/")) {
        "main"
    } else {
        "elsewhere"
    }
}

/// The segment's words with leading wrappers and `VAR=value` prefixes removed (`_words`).
fn words(seg: &str) -> Vec<&str> {
    let mut toks: Vec<&str> = seg.split_whitespace().collect();
    while let Some(t) = toks.first() {
        // a loop's, an `if`'s or a `while`'s keyword leads its body's command (`bind::KEYWORDS`)
        // a wrapper spelled by its path is the wrapper (`/usr/bin/env git`, 451 T295)
        let name = crate::spelled::name_of(t);
        if crate::spelled::lookup(name, toks.get(1).copied()) {
            break;
        }
        if WRAPPERS.contains(&name) || name == "timeout" {
            // with its own options (`env -i git`, `sudo -u x git`), and `timeout`'s duration (451 T295)
            let own = 1 + crate::spelled::options(name, &toks[1..]);
            let own = own + usize::from(name == "timeout" && toks.len() > own);
            toks.drain(..own);
        } else if ASSIGNMENT_WORD.is_match(t) || bind::KEYWORDS.contains(t) {
            toks.remove(0);
        } else {
            break;
        }
    }
    toks
}

/// A write's target, whether the command named it (`named`) or it lands where the shell stands (`shell`), and for a target the
/// walk cannot resolve what it knows of it (451 T79's `Known`).
type Write = (Option<String>, &'static str, Known);

/// The paths a file tool writes (`_tool_paths`): `sed`'s files past its script, the last argument of a copy, else every argument.
fn tool_paths<'a>(tool: &str, toks: &[&'a str]) -> Vec<&'a str> {
    let blank = |t: &str| matches!(t, "''" | "\"\"");
    let args: Vec<&str> = toks[1..]
        .iter()
        .copied()
        .filter(|t| *t != "--" && !t.contains("<<"))
        .collect();
    if tool == "sed" {
        let (mut keep, mut skip_next) = (Vec::new(), false);
        let mut script_seen = args.contains(&"-e") || args.contains(&"--expression");
        // a quoted script that held a space or a shell character reaches here as one held word (451 T83; blanked to '' where its
        // parentheses do not pair): it is still the script (or the argument of -e), never a path - dropped before this loop, it
        // made the file the script (T227)
        for t in args {
            if skip_next {
                skip_next = false;
            } else if matches!(t, "-e" | "--expression" | "-f" | "--file") {
                skip_next = true;
            } else if t.starts_with('-') {
            } else if !script_seen {
                script_seen = true; // the first bare argument is the sed script, not a file
            } else if !blank(t) {
                keep.push(t);
            }
        }
        return keep;
    }
    // `chmod`'s mode and `chown`'s owner are its first operand, not a file, unless `--reference` stands for it (451 T33: its round-3
    // gate replay refused `chmod +x $C/a.sh` as a write of `+x` where the shell stood, measured 2026-11-20); a mode may lead with
    // `-` (`chmod -x F`), which no option of chmod's spells
    let mut args = args;
    if matches!(tool, "chmod" | "chown") && !args.iter().any(|t| t.starts_with("--reference")) {
        if let Some(k) = args
            .iter()
            .position(|t| !t.starts_with('-') || (tool == "chmod" && CHMOD_MODE.is_match(t)))
        {
            args.remove(k);
        }
    }
    // `truncate -s 0 F` and `-r REF F` empty or resize F: the size and the reference file are its options' values, not files written (T227);
    // so are `touch -d DATE`, `-t STAMP` and `-r REF` (451 T83: `touch -d "2 hours ago" $D/f.log`, its date held as one word, was a
    // write of `2 hours ago` where the shell stood)
    let mut value_next = false;
    let args: Vec<&str> = args
        .into_iter()
        .filter(|t| {
            let value = std::mem::replace(
                &mut value_next,
                (tool == "truncate" && matches!(*t, "-s" | "-r"))
                    || (tool == "touch" && matches!(*t, "-d" | "-t" | "-r")),
            );
            !value && !t.starts_with('-') && !blank(t)
        })
        .collect();
    if FILE_TOOLS_LAST.contains(&tool) {
        return args.last().copied().into_iter().collect();
    }
    args
}

fn path_write(p: &str, env: &Env, home: &str, eff: Option<&str>) -> Write {
    let bare = strip_quote_chars(p);
    match expand(bare, env, home) {
        Some(e) if e.starts_with('/') => (Some(normpath(&e)), "named", Known::Shell),
        // a word whose known part is absolute names its place, a variable the command sets included (451 T79: `$R/out.$n`)
        None => (
            None,
            if substituted(bare, env, home).starts_with('/') {
                "named"
            } else {
                "shell"
            },
            known_place(bare, env, home, eff),
        ),
        Some(_) => (resolve(bare, env, home, eff), "shell", Known::Shell),
    }
}

/// Whether a perl switch cluster edits in place (`-i`, `-pi`, `-i.bak`, `-pi.orig`): the switches before its `i` take no argument, so
/// `-Ilib` (an include path) and `-Mstrict` (a module) are not one (T227: `perl -pi -e` rewrote a file the walk never saw).
fn perl_in_place(token: &str) -> bool {
    let Some(cluster) = token.strip_prefix('-').filter(|c| !c.starts_with('-')) else {
        return false;
    };
    cluster
        .trim_start_matches(|c| "pnlaswWtTcuU0".contains(c))
        .starts_with('i')
}

/// Every write in one segment (`_writes_in`).
fn writes_in(
    seg: &str,
    programs: &[Program],
    env: &Env,
    home: &str,
    eff: Option<&str>,
) -> Vec<Write> {
    let mut found_writes = Vec::new();
    let toks = words(seg);
    if let Some(head) = toks.first() {
        // the program by its name, however the command spells it (451 T295: git was read by its bare word alone, so
        // `/usr/bin/git worktree add` and `\git checkout` wrote nothing the walk saw, and every guard reading it passed them)
        let base = crate::spelled::name_of(head);
        if base == "git" {
            found_writes.extend(git::git_write(&toks, env, home, eff));
        } else if base == "make" {
            // where its own `-C`s put it (451 T409)
            found_writes.push(make_dir::make_place(&toks, env, home, eff));
        } else if let Some(at) = python_c(&toks).filter(|_| PYTHON.is_match(base)) {
            // 451 T31: a program that only reads stays in the walk MARKED "read" - no guard's verdict counts it a write, and the
            // guards that read a walk's targets for where a command lands (house style, gm-tree) see what they saw before
            // (`walk` makes it D5's write again beside a stdin program it cannot read, 451 T42)
            let how = if program_reads(toks.get(at + 1), programs, eff) {
                "read"
            } else {
                "shell"
            };
            // 451 T89: a program writing only through `sys.argv` reads where it stands and writes each word it names
            let placed = (how == "shell")
                .then(|| py_c::argv_places(&toks, at, programs, env, home, eff))
                .flatten();
            let how = if placed.is_some() { "read" } else { how };
            found_writes.push((eff.map(str::to_owned), how, Known::Shell));
            found_writes.extend(placed.into_iter().flatten());
        } else if (base == "sed"
            && toks[1..]
                .iter()
                .any(|t| t.starts_with("-i") || t.starts_with("--in-place")))
            || (base == "perl" && toks[1..].iter().any(|t| perl_in_place(t)))
        {
            found_writes.extend(
                tool_paths("sed", &toks)
                    .into_iter()
                    .map(|p| path_write(p, env, home, eff)),
            );
        } else if base == "dd" {
            // `dd of=F` writes F, named in its operand (T227)
            found_writes.extend(
                toks[1..]
                    .iter()
                    .filter_map(|t| t.strip_prefix("of="))
                    .map(|p| path_write(p, env, home, eff)),
            );
        } else if FILE_TOOLS_ALL.contains(&base)
            || FILE_TOOLS_LAST.contains(&base)
            || base == "truncate"
        {
            found_writes.extend(
                tool_paths(base, &toks)
                    .into_iter()
                    .map(|p| path_write(p, env, home, eff)),
            );
        }
    }
    for target in redirects(seg) {
        found_writes.push(path_write(target, env, home, eff));
    }
    found_writes
}

/// One write found by the walk: where it lands, its class, how it was reached, the segment it is in, and the Python program it
/// comes from (a `-c` program or one run from stdin, its body as the command line holds it; 451 T33: make-only reads which files a
/// writer names), None for any other write. `head` is the segment from its command on (`command_head`): `segment` is cut at 120
/// characters, so a command behind more than that of `VAR=value` prefixes was lost from it (451 T90).
#[derive(Debug, Clone)]
pub struct Target {
    pub path: Option<String>,
    pub class: &'static str,
    pub how: &'static str,
    pub segment: String,
    pub program: Option<String>,
    pub head: String,
    /// Whether a redirect (`> f`, `>> f`) is the write, not its program (451 T427: the context cap's wrap-up band judges where a
    /// redirect lands, while `make`'s own write where it stands is the stop point's).
    pub redirect: bool,
}

/// The walk's answer (`walk`).
#[derive(Debug, Clone)]
pub struct Walk {
    pub targets: Vec<Target>,
    pub final_dir: Option<String>,
    pub cd_into_main: bool,
    pub standing: &'static str,
}

/// The effective directory through the command, and every write with where it lands (`walk`), as the guards that read a walk's
/// paths see it (house style, make-only, the bench): a Python program run from stdin is no target, as before 451 T42 - house
/// style's D11 holds a program heredoc's writes unknowable, its case table pinning that one beside a `/tmp` log is left alone.
#[must_use]
pub fn walk(cmd: &str, start: Option<&str>, main: &str, home: &str) -> Walk {
    walk_in(cmd, start, main, home, false)
}

/// The walk as the tree guards judge it (main-tree, gm-tree; 451 T42): a Python program run from stdin whose body can write is a
/// write where the shell stands.
#[must_use]
pub fn walk_judged(cmd: &str, start: Option<&str>, main: &str, home: &str) -> Walk {
    walk_in(cmd, start, main, home, true)
}

/// The walk of each binding of the command's variables (`bind::bound_texts`), their writes together: a command judged by every
/// value its names take, a write landing in several places in each (451 T79's second round).
fn walk_in(cmd: &str, start: Option<&str>, main: &str, home: &str, stdin_writes: bool) -> Walk {
    let mut programs = Vec::new();
    let carried = carry_heredocs(cmd, &mut programs);
    let mut texts = bind::bound_texts(&carried).into_iter().peekable();
    // a target shows its segment as the command holds it, which guards find in the command (`readme_hooks`), not as bound
    let shown = if texts.peek().is_some_and(|t| *t != carried) {
        let (text, _) = sanitize(&carried, programs.clone());
        seg_texts(&segments(&text, &mut Vec::new()))
    } else {
        Vec::new()
    };
    let first = texts.next().unwrap_or_default();
    let walk_of = |text: &str| {
        walk_text(
            text,
            programs.clone(),
            &shown,
            start,
            main,
            home,
            stdin_writes,
        )
    };
    let mut walk = walk_of(&first);
    for text in texts {
        let more = walk_of(&text);
        for t in more.targets {
            if !walk
                .targets
                .iter()
                .any(|w| (&w.path, w.class, w.how) == (&t.path, t.class, t.how))
            {
                walk.targets.push(t);
            }
        }
        walk.cd_into_main |= more.cd_into_main;
        if walk.final_dir != more.final_dir {
            walk.final_dir = None;
        }
    }
    walk
}

/// Where a `cd` moved the shell, for `$PWD` and `$OLDPWD` (451 T79's second round: `cd /tmp && echo x > $OLDPWD/f` writes where the
/// shell stood); a place the walk cannot resolve is unknown.
fn moved(env: &mut Env, pwd: Option<String>, oldpwd: Option<String>) {
    for (name, place) in [("PWD", pwd), ("OLDPWD", oldpwd)] {
        env.insert(
            name.to_owned(),
            place.unwrap_or_else(|| bind::UNREAD.to_owned()),
        );
    }
}

/// Every simple command `cmd` runs, as the walk splits it (451 T417, the context cap's wrap-up band): heredoc bodies carried out and
/// quoted strings stood in for, so neither a body's lines nor a quoted `make decide` is a command; a subshell's and a `$(...)`'s
/// commands among them. Each is its segment's text, its words as the walk reads them.
#[must_use]
pub fn commands(cmd: &str) -> Vec<String> {
    let mut programs = Vec::new();
    let carried = carry_heredocs(cmd, &mut programs);
    let (text, _) = sanitize(&carried, programs);
    seg_texts(&segments(&text, &mut Vec::new()))
}

/// One of [`commands`] as its command wrote it, for a message: the quoted text its stand-ins hold shown again (451 T417).
#[must_use]
pub fn shown(command: &str) -> String {
    quoted::shown(command)
}

fn seg_texts(pieces: &[Piece]) -> Vec<String> {
    pieces
        .iter()
        .filter_map(|p| match p {
            Piece::Seg(s, _) => Some(s.clone()),
            _ => None,
        })
        .collect()
}

/// Where a `cd` or `pushd` moves the shell, `$PWD` and `$OLDPWD` with it, and the class the hint takes where the walk knows it.
fn cd_to(
    toks: &[&str],
    env: &mut Env,
    home: &str,
    eff: Option<String>,
    main: &str,
) -> (Option<String>, Option<&'static str>) {
    let known = toks
        .get(1)
        .filter(|t| !matches!(**t, "--" | "-"))
        .map(|t| known_place(t, env, home, eff.as_deref()));
    let to = match toks.get(1) {
        None | Some(&"--") => Some(home.to_owned()),
        Some(&"-") => None,
        Some(t) => resolve(t, env, home, eff.as_deref()),
    };
    moved(env, to.clone(), eff);
    let class = cd_class(to.as_deref(), known, main);
    (to, class)
}

fn walk_text(
    carried: &str,
    programs: Vec<Program>,
    shown: &[String],
    start: Option<&str>,
    main: &str,
    home: &str,
    stdin_writes: bool,
) -> Walk {
    let mut env = env_from(carried, start, home);
    let (text, programs) = sanitize(carried, programs);
    let mut subs = Vec::new();
    let pieces = segments(&text, &mut subs);
    let bound_segs = seg_texts(&pieces);
    let mut shown = Some(shown)
        .filter(|s| s.len() == bound_segs.len())
        .unwrap_or(&bound_segs)
        .iter();
    mktemp_words(&mut env, &subs, home);
    let mut eff: Option<String> = start.map(str::to_owned);
    let mut hint = classify(eff.as_deref(), main); // where the shell was last KNOWN to be (spec D6)
    let (mut stack, mut targets, mut cd_into_main) = (Vec::new(), Vec::new(), false);
    let (mut prev, mut unread) = (None::<String>, false);
    for piece in pieces {
        let (seg, piped) = match piece {
            // a substitution's segments are no upstream of its word's command: the segment before it is (451 T79)
            Piece::Push | Piece::SubPush => {
                let feeds = matches!(piece, Piece::SubPush).then(|| prev.clone());
                let dirs = (env.get("PWD").cloned(), env.get("OLDPWD").cloned());
                stack.push((eff.clone(), hint, feeds, dirs));
                continue;
            }
            Piece::Pop | Piece::SubPop => {
                if let Some((e, h, feeds, (pwd, oldpwd))) = stack.pop() {
                    (eff, hint) = (e, h);
                    moved(&mut env, pwd, oldpwd);
                    if let Some(p) = feeds {
                        prev = p;
                    }
                }
                continue;
            }
            Piece::Seg(s, piped) => (s, piped),
        };
        let upstream = prev.replace(seg.clone()).filter(|_| piped);
        let showing = shown.next().unwrap_or(&seg).clone();
        let toks = words(&seg);
        bind::read_where_it_stands(&seg, &mut env, home);
        if matches!(toks.first(), Some(&"cd" | &"pushd")) {
            let class;
            (eff, class) = cd_to(&toks, &mut env, home, eff.take(), main);
            if let Some(class) = class {
                hint = class;
                cd_into_main |= hint == "main";
            }
            continue;
        }
        if toks.first() == Some(&"popd") {
            moved(&mut env, None, eff.take());
            continue;
        }
        let mut writes = writes_in(&seg, &programs, &env, home, eff.as_deref());
        // the `-c` program's write is the segment's first, as `writes_in` finds it (451 T33)
        let mut program = python_c(&toks)
            .filter(|_| {
                toks.first()
                    .is_some_and(|h| PYTHON.is_match(h.rsplit('/').next().unwrap_or(h)))
            })
            .and_then(|at| program_of(toks.get(at + 1), &programs))
            .map(|(_, body)| body.clone());
        // 451 T42: a Python program run from stdin is judged by T31's reader as a `-c` program is - a writer is a write where
        // the shell stands; a read is no target, as no stdin program was before; one the walk cannot read keeps every `-c`
        // read of the command D5's write (T31's stdin rule, now for that case alone), since that write was what refused
        // parse#72's and window#61's heredoc writers before their bodies were judged
        match stdin_program(
            &toks,
            upstream.as_deref(),
            &programs,
            &env,
            home,
            eff.as_deref(),
        ) {
            Stdin::Unread => unread = true,
            Stdin::Program(q, body) if stdin_writes && !py_c::reads(&body, q, eff.as_deref()) => {
                writes.insert(0, (eff.clone(), "shell", Known::Shell));
                program = Some(body);
            }
            Stdin::None | Stdin::Program(..) => {}
        }
        let first_redirect = writes.len() - redirects(&seg).len(); // `writes_in` puts them last (451 T427)
        for (k, (path, how, known)) in writes.into_iter().enumerate() {
            let class = settled(path.as_deref(), &known, hint, main);
            let blank = blanked(&showing);
            let shown = HEREDOC_WORD.replace_all(bind::from_command(&blank), "<<BODY");
            targets.push(Target {
                path,
                class,
                how,
                segment: shown.chars().take(120).collect(),
                program: if k == 0 { program.take() } else { None },
                head: command_head(&shown),
                redirect: k >= first_redirect,
            });
        }
    }
    for t in targets.iter_mut().filter(|t| unread && t.how == "read") {
        t.how = "shell";
    }
    Walk {
        targets,
        final_dir: eff,
        cd_into_main,
        standing: classify(start, main),
    }
}

/// The wrappers a segment's command can stand behind, which a reader of its head reads past: the walk's own and `timeout`, with its
/// duration (451 T79).
pub const HEAD_WRAPPERS: [&str; 10] = crate::spelled::WRAPPERS;

/// A segment from its command on, cut at 120 characters: its leading `VAR=value` words dropped, among the wrappers too, which are
/// kept (451 T90: T79's `L7R_FEATURE_DIRECTORY=... L7R_PAGE_SESSION=... make rust-test` lost its `make` to the segment's cut and
/// was refused as a shell write of `.` under a running gate, measured 2026-11-21).
#[must_use]
pub fn command_head(segment: &str) -> String {
    let mut kept: Vec<&str> = Vec::new();
    let mut rest = segment.trim_start();
    let mut duration = false;
    while let Some(w) = rest.split_whitespace().next() {
        if duration || HEAD_WRAPPERS.contains(&crate::spelled::name_of(w)) {
            kept.push(w);
        } else if !w.contains('=') {
            break;
        }
        duration = crate::spelled::name_of(w) == "timeout";
        rest = rest[w.len()..].trim_start();
    }
    kept.push(rest);
    kept.join(" ").trim().chars().take(120).collect()
}

/// `os.path.realpath`: a path that need not exist, its existing part's symlinks resolved.
#[must_use]
pub fn realpath(p: &Path) -> PathBuf {
    let mut clean = PathBuf::new();
    for c in p.components() {
        match c {
            Component::ParentDir => {
                clean.pop();
            }
            Component::CurDir => {}
            other => clean.push(other.as_os_str()),
        }
    }
    let mut rest = Vec::new();
    let mut at = clean.as_path();
    loop {
        if let Ok(real) = std::fs::canonicalize(at) {
            return rest
                .iter()
                .rev()
                .fold(real, |acc: PathBuf, n: &&std::ffi::OsStr| acc.join(n));
        }
        let (Some(up), Some(name)) = (at.parent(), at.file_name()) else {
            return clean.clone();
        };
        rest.push(name);
        at = up;
    }
}

#[cfg(test)]
mod tests;
