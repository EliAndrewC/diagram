//! Where a command's writes land (`scripts/hooks/lib/hm_tree.py` - feature 449 T010 decision (a)): the effective directory walked
//! through the command's own `cd`s, variables and subshells, every write classified by where it lands - the mirror, a clone or
//! elsewhere - and a write that lands in the mirror by where the shell stands rewritten into the session's clone, the rewrite
//! re-judged so it never returns a command it would refuse. Each pattern is the Python's verbatim; the reasons stand in its
//! comments, kept in git history.

use std::collections::HashMap;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};

use super::shape::strip_heredocs;

mod py_c;
mod python;
mod verdict;

use python::{
    carry_heredocs, program_reads, python_c, stdin_program, Program, Stdin, HEREDOC_WORD, PYTHON,
    PYTHON_C_BEFORE,
};
pub use verdict::{context_line, explain, judge, Verdict};

fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern)
        .unwrap_or_else(|e| unreachable!("a guard's own pattern: {e}"))
}

const GIT_WRITES: [&str; 17] = [
    "commit",
    "add",
    "merge",
    "rebase",
    "reset",
    "checkout",
    "restore",
    "rm",
    "mv",
    "apply",
    "am",
    "stash",
    "cherry-pick",
    "push",
    "pull",
    "clean",
    "tag",
];
const FILE_TOOLS_ALL: [&str; 12] = [
    "vim", "vi", "nano", "emacs", "tee", "touch", "mkdir", "rmdir", "rm", "mv", "chmod", "chown",
];
/// The tools whose LAST argument is what they write: `rsync`'s destination as `cp`'s (T227).
const FILE_TOOLS_LAST: [&str; 4] = ["cp", "ln", "install", "rsync"];
const WRAPPERS: [&str; 9] = [
    "sudo", "nohup", "setsid", "env", "command", "exec", "time", "nice", "builtin",
];
const BRANCH_WRITE_FLAGS: [&str; 16] = [
    "-d",
    "-D",
    "-m",
    "-M",
    "-c",
    "-C",
    "-f",
    "-u",
    "--delete",
    "--move",
    "--copy",
    "--force",
    "--set-upstream-to",
    "--unset-upstream",
    "--edit-description",
    "--track",
];
const BRANCH_LIST_FLAGS: [&str; 11] = [
    "-l",
    "--list",
    "-r",
    "--remotes",
    "-a",
    "--all",
    "--contains",
    "--no-contains",
    "--merged",
    "--no-merged",
    "--points-at",
];
const BRANCH_LIST_SHOW: &str = "--show-current";
const BRANCH_VALUE_FLAGS: [&str; 8] = [
    "--contains",
    "--no-contains",
    "--merged",
    "--no-merged",
    "--points-at",
    "--sort",
    "--format",
    "--column",
];

static ASSIGN: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"(?:^|[;&|\n(]|&&|\|\|)\s*(?:export\s+)?([A-Za-z_]\w*)=(?:"([^"\n]*)"|'([^'\n]*)'|([^\s;&|)]*))"#,
    )
});
static VAR: LazyLock<Regex> = LazyLock::new(|| re(r"\$\{(\w+)\}|\$(\w+)"));
static QUOTED: LazyLock<Regex> = LazyLock::new(|| re(r#"(?s)(["'])((?:\\.|(?!\1).)*)\1"#));
static PLAIN_QUOTE_BODY: LazyLock<Regex> = LazyLock::new(|| re(r"^[^\s;|&()<>`\n]*$"));
static REDIRECT: LazyLock<Regex> = LazyLock::new(|| re(r"(?<![<>])\d?>{1,2}\|?\s*([^\s;&|()<>]+)"));
static FUNCTION_DEF: LazyLock<Regex> = LazyLock::new(|| re(r"^\s*[\w-]+\s*\(\s*\)"));
static DUP_FD: LazyLock<Regex> = LazyLock::new(|| re(r"\d*>&[0-9-]"));
static DEV_NULL: LazyLock<Regex> = LazyLock::new(|| re(r"\d*>\s*/dev/null"));
static ASSIGNMENT_WORD: LazyLock<Regex> = LazyLock::new(|| re(r"^[A-Za-z_]\w*="));
fn found(p: &Regex, text: &str) -> bool {
    p.is_match(text).unwrap_or(false)
}

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

/// A quoted string kept as its body where it is one plain word (a path), else blanked to an empty pair (`_quotes_to_paths`); a
/// program `python3 -c` runs is carried out beside the text, the word `__py_c_<n>__` standing in its place, so `writes_in` can
/// judge whether it only reads without the program's own `;`, `(` and `|` splitting the walk (451 T31).
fn quotes_to_paths(cmd: &str, mut programs: Vec<Program>) -> (String, Vec<Program>) {
    let text = QUOTED
        .replace_all(cmd, |c: &Captures| {
            let body = c.get(2).map_or("", |m| m.as_str());
            let quote = c.get(1).map_or("", |m| m.as_str());
            let at = c.get(0).map_or(0, |m| m.start());
            if found(&PYTHON_C_BEFORE, &cmd[..at]) {
                programs.push((quote.chars().next().unwrap_or('"'), body.to_owned()));
                format!("__py_c_{}__", programs.len() - 1)
            } else if found(&PLAIN_QUOTE_BODY, body) {
                body.to_owned()
            } else {
                quote.repeat(2)
            }
        })
        .into_owned();
    (text, programs)
}

fn sanitize(cmd: &str) -> (String, Vec<Program>) {
    let mut programs = Vec::new();
    let carried = carry_heredocs(cmd, &mut programs);
    let (text, programs) = quotes_to_paths(&carried, programs);
    let text = DUP_FD.replace_all(&text, " ");
    (DEV_NULL.replace_all(&text, " ").into_owned(), programs)
}

type Env = HashMap<String, String>;

/// A token with its variables and `~` substituted, or None where something in it cannot be (`_expand`).
fn expand(token: &str, env: &Env, home: &str) -> Option<String> {
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
    (!token.contains('$') && !token.contains('`')).then_some(token)
}

/// `NAME=value` assignments at command positions, resolved through each other in order (`_env_from`).
fn env_from(cmd: &str, start: Option<&str>, home: &str) -> Env {
    let mut env = Env::from([("HOME".to_owned(), home.to_owned())]);
    if let Some(c) = start {
        env.insert("PWD".to_owned(), c.to_owned());
    }
    let text = strip_heredocs(cmd);
    for c in ASSIGN.captures_iter(&text).map_while(Result::ok) {
        let name = c.get(1).map_or("", |m| m.as_str()).to_owned();
        let value = (2..=4)
            .find_map(|i| c.get(i))
            .map_or("", |m| m.as_str())
            .to_owned();
        let expanded = expand(&value, &env, home).unwrap_or(value);
        env.insert(name, expanded);
    }
    env
}

fn strip_quote_chars(token: &str) -> &str {
    token.trim_matches(|c| c == '"' || c == '\'')
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

/// One piece of a command split at its separators: a segment, or a subshell's opening or closing (`_segments`).
#[derive(Debug, PartialEq, Eq)]
enum Piece {
    /// A segment, and whether a pipe feeds it the stdout of the segment before (451 T42: `cat <<'PY' | python3`).
    Seg(String, bool),
    Push,
    Pop,
}

fn segments(text: &str) -> Vec<Piece> {
    let chars: Vec<char> = text.chars().collect();
    let (mut out, mut buf, mut i, mut piped) = (Vec::new(), String::new(), 0, false);
    let flush = |buf: &mut String, out: &mut Vec<Piece>, piped: bool| {
        let seg = buf.trim().to_owned();
        buf.clear();
        if !seg.is_empty() {
            out.push(Piece::Seg(seg, piped));
        }
    };
    while i < chars.len() {
        let ch = chars[i];
        let next = chars.get(i + 1).copied();
        if (ch == '&' && next == Some('&')) || (ch == '|' && next == Some('|')) {
            flush(&mut buf, &mut out, piped);
            piped = false;
            i += 2;
        } else if ch == '$' && next == Some('(') {
            flush(&mut buf, &mut out, piped);
            out.push(Piece::Push);
            piped = false;
            i += 2;
        } else if (ch == '|' || ch == '&') && buf.ends_with('>') {
            buf.push(ch); // `>|` and `>&` belong to the redirection, not a separator (feature 429)
            i += 1;
        } else if matches!(ch, ';' | '|' | '&' | '\n') {
            // a pipe at a line's end still feeds the next line's segment
            if !(ch == '\n' && buf.trim().is_empty()) {
                flush(&mut buf, &mut out, piped);
                piped = ch == '|';
            }
            i += 1;
        } else if ch == '(' {
            flush(&mut buf, &mut out, piped);
            out.push(Piece::Push);
            i += 1;
        } else if ch == ')' {
            flush(&mut buf, &mut out, piped);
            out.push(Piece::Pop);
            piped = false;
            i += 1;
        } else if ch == '{' || ch == '}' {
            flush(&mut buf, &mut out, piped);
            i += 1;
        } else {
            buf.push(ch);
            i += 1;
        }
    }
    flush(&mut buf, &mut out, piped);
    out
}

/// The segment's words with leading wrappers and `VAR=value` prefixes removed (`_words`).
fn words(seg: &str) -> Vec<&str> {
    let mut toks: Vec<&str> = seg.split_whitespace().collect();
    while let Some(t) = toks.first() {
        if WRAPPERS.contains(t) || found(&ASSIGNMENT_WORD, t) {
            toks.remove(0);
        } else if *t == "timeout" && toks.len() > 1 {
            toks.drain(..2);
        } else {
            break;
        }
    }
    toks
}

fn branch_writes(args: &[&str]) -> bool {
    let flags: Vec<&str> = args
        .iter()
        .filter(|a| a.starts_with('-'))
        .map(|a| a.split('=').next().unwrap_or(a))
        .collect();
    if flags.iter().any(|f| BRANCH_WRITE_FLAGS.contains(f))
        || args.iter().any(|a| a.starts_with("--set-upstream-to="))
    {
        return true;
    }
    let (mut names, mut skip) = (0, false);
    for a in args {
        if skip {
            skip = false;
        } else if a.starts_with('-') {
            skip = BRANCH_VALUE_FLAGS.contains(a);
        } else {
            names += 1;
        }
    }
    names > 0
        && !flags
            .iter()
            .any(|f| BRANCH_LIST_FLAGS.contains(f) || *f == BRANCH_LIST_SHOW)
}

/// A write's target and whether the command named it (`named`) or it lands where the shell stands (`shell`).
type Write = (Option<String>, &'static str);

/// (target, how) where a git invocation writes (`_git_write`).
fn git_write(toks: &[&str], env: &Env, home: &str, eff: Option<&str>) -> Option<Write> {
    let (mut i, mut c_path) = (1, None);
    while i < toks.len() {
        let t = toks[i];
        if (t == "-C" || t == "-c") && i + 1 < toks.len() {
            if t == "-C" {
                c_path = Some(toks[i + 1]);
            }
            i += 2;
        } else if t.starts_with('-') {
            i += 1;
        } else {
            break;
        }
    }
    let sub = *toks.get(i)?;
    if !(GIT_WRITES.contains(&sub) || (sub == "branch" && branch_writes(&toks[i + 1..]))) {
        return None;
    }
    let Some(c) = c_path else {
        return Some((eff.map(str::to_owned), "shell"));
    };
    let how = if strip_quote_chars(c).starts_with('/') {
        "named"
    } else {
        "shell"
    };
    Some((resolve(c, env, home, eff), how))
}

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
        // a quoted script that held a space or a shell character reaches here blanked to '': it is still the script (or the
        // argument of -e), never a path - dropped before this loop, it made the file the script (T227)
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
    // `truncate -s 0 F` and `-r REF F` empty or resize F: the size and the reference file are its options' values, not files written (T227)
    let mut value_next = false;
    let args: Vec<&str> = args
        .into_iter()
        .filter(|t| {
            let value = std::mem::replace(
                &mut value_next,
                tool == "truncate" && matches!(*t, "-s" | "-r"),
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
        Some(e) if e.starts_with('/') => (Some(normpath(&e)), "named"),
        None => (
            None,
            if bare.starts_with('/') {
                "named"
            } else {
                "shell"
            },
        ),
        Some(_) => (resolve(bare, env, home, eff), "shell"),
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
        let base = head.rsplit('/').next().unwrap_or(head);
        if *head == "git" {
            found_writes.extend(git_write(&toks, env, home, eff));
        } else if base == "make" {
            found_writes.push((eff.map(str::to_owned), "shell"));
        } else if let Some(at) = python_c(&toks).filter(|_| found(&PYTHON, base)) {
            // 451 T31: a program that only reads stays in the walk MARKED "read" - no guard's verdict counts it a write, and the
            // guards that read a walk's targets for where a command lands (house style, gm-tree) see what they saw before
            // (`walk` makes it D5's write again beside a stdin program it cannot read, 451 T42)
            let how = if program_reads(toks.get(at + 1), programs, eff) {
                "read"
            } else {
                "shell"
            };
            found_writes.push((eff.map(str::to_owned), how));
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
    for c in REDIRECT.captures_iter(seg).map_while(Result::ok) {
        found_writes.push(path_write(
            c.get(1).map_or("", |m| m.as_str()),
            env,
            home,
            eff,
        ));
    }
    found_writes
}

/// One write found by the walk: where it lands, its class, how it was reached, and the segment it is in.
#[derive(Debug, Clone)]
pub struct Target {
    pub path: Option<String>,
    pub class: &'static str,
    pub how: &'static str,
    pub segment: String,
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

fn walk_in(cmd: &str, start: Option<&str>, main: &str, home: &str, stdin_writes: bool) -> Walk {
    let env = env_from(cmd, start, home);
    let (text, programs) = sanitize(cmd);
    let mut eff: Option<String> = start.map(str::to_owned);
    let mut hint = classify(eff.as_deref(), main); // where the shell was last KNOWN to be (spec D6)
    let (mut stack, mut targets, mut cd_into_main) = (Vec::new(), Vec::new(), false);
    let (mut prev, mut unread) = (None::<String>, false);
    for piece in segments(&text) {
        let (seg, piped) = match piece {
            Piece::Push => {
                stack.push((eff.clone(), hint));
                continue;
            }
            Piece::Pop => {
                if let Some((e, h)) = stack.pop() {
                    (eff, hint) = (e, h);
                }
                continue;
            }
            Piece::Seg(s, piped) => (s, piped),
        };
        let upstream = prev.replace(seg.clone()).filter(|_| piped);
        let toks = words(&seg);
        if matches!(toks.first(), Some(&"cd" | &"pushd")) {
            eff = match toks.get(1) {
                None | Some(&"--") => Some(home.to_owned()),
                Some(&"-") => None,
                Some(t) => resolve(t, &env, home, eff.as_deref()),
            };
            if eff.is_some() {
                hint = classify(eff.as_deref(), main);
                cd_into_main |= hint == "main";
            }
            continue;
        }
        if toks.first() == Some(&"popd") {
            eff = None;
            continue;
        }
        let mut writes = writes_in(&seg, &programs, &env, home, eff.as_deref());
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
                writes.insert(0, (eff.clone(), "shell"));
            }
            Stdin::None | Stdin::Program(..) => {}
        }
        for (path, how) in writes {
            let mut class = classify(path.as_deref(), main);
            if class == "unknown" {
                class = if hint == "main" { "main" } else { "elsewhere" }; // D6: unknown resolves toward main
            }
            targets.push(Target {
                path,
                class,
                how,
                segment: HEREDOC_WORD
                    .replace_all(&seg, "<<BODY")
                    .chars()
                    .take(120)
                    .collect(),
            });
        }
    }
    if unread {
        for t in targets.iter_mut().filter(|t| t.how == "read") {
            t.how = "shell";
        }
    }
    Walk {
        targets,
        final_dir: eff,
        cd_into_main,
        standing: classify(start, main),
    }
}

#[cfg(test)]
mod tests;
