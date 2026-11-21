//! The Python programs a command runs, as the walk carries and judges them (451 T31, T42): a `python3 -c` program and a
//! heredoc's body carried out beside the command's text, the `-c` found past the interpreter's flags, and the program a Python
//! segment runs from its stdin - its own heredoc or `< file`, or what a `cat` it is piped from prints - each judged by `py_c`.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};

use super::{found, py_c, re, resolve, words, Env};

/// The interpreter's name, a minor version included (`python3.12`; 451 T31 - before it, only `python`, `python3`).
pub(super) static PYTHON: LazyLock<Regex> = LazyLock::new(|| re(r"^python(?:3(?:\.\d+)?)?$"));
/// Python's flags that take no argument, any of which may stand before `-c` or cluster with it (`-I -c`, `-Ic`; 451 T31).
const PY_FLAGS: &str = "bBdEhiIOPqRsSuvVx";
/// The text before a quote that `python3 -c` runs, in the shape `writes_in` reads as one: the interpreter, then `-c` (451 T31).
pub(super) static PYTHON_C_BEFORE: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"(?:^|[\s;&|(])(?:[^\s;&|()]*/)?python(?:3(?:\.\d+)?)?(?:[ \t]+(?:-[{PY_FLAGS}]*[WX][ \t]*[^\s;&|()'\x22]+|-[{PY_FLAGS}]+))*[ \t]+-[{PY_FLAGS}]*c[ \t]+$"
    ))
});
/// The word a `python3 -c` program is carried as through the walk: its index among the walk's programs (451 T31).
static PROGRAM: LazyLock<Regex> = LazyLock::new(|| re(r"^__py_c_(\d+)__$"));
/// A heredoc, `shape::strip_heredocs`'s pattern with the opener's quote and the body captured, so a body standing at the same
/// span is carried out as a program (451 T42): 1 the quote before the delimiter, 2 the delimiter, 3 the opener's words after
/// it, 4 the body.
static HEREDOC: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?sm)<<-?[ \t]*(['"\\]?)(\w+)['"]?([^\n]*)\n(.*?)^[ \t]*\2\b"#));
/// The word a heredoc's body is carried as (`<<__py_h_<n>__`, its index among the walk's programs), and its `<<BODY` as a
/// target's segment shows it, as before (451 T42).
pub(super) static HEREDOC_WORD: LazyLock<Regex> = LazyLock::new(|| re(r"<<__py_h_(\d+)__"));

/// A program the walk may judge - a `python3 -c` program or a heredoc's body: its quote (`'h'` an unquoted heredoc's, whose body
/// the shell expands; `'\''` a quoted one's) and its body as the command line holds it.
pub(super) type Program = (char, String);

/// The command with each heredoc's body carried out beside it, `<<__py_h_<n>__` and the opener's words standing in its place
/// (`strip_heredocs`' ` <<BODY ` with an index, 451 T42), so the Python program a heredoc feeds can be judged.
pub(super) fn carry_heredocs(cmd: &str, programs: &mut Vec<Program>) -> String {
    HEREDOC
        .replace_all(cmd, |c: &Captures| {
            let quoted = c.get(1).is_some_and(|m| !m.as_str().is_empty());
            let body = c.get(4).map_or("", |m| m.as_str()).to_owned();
            programs.push((if quoted { '\'' } else { 'h' }, body));
            let rest = c.get(3).map_or("", |m| m.as_str());
            format!(" <<__py_h_{}__ {rest}", programs.len() - 1)
        })
        .into_owned()
}

/// The index of the `-c` that makes a Python command line run a program, past the flags before it (`python3 -I -W x -c`, `-Ic`;
/// 451 T31 - before it only a `-c` second word was read, so `python3 -I -c` was never judged at all); None where it runs a file,
/// a module or stdin.
pub(super) fn python_c(toks: &[&str]) -> Option<usize> {
    let mut i = 1;
    while let Some(t) = toks.get(i) {
        let flags = t.strip_prefix('-').filter(|f| !f.starts_with('-'))?;
        let cluster = flags.trim_start_matches(|c| PY_FLAGS.contains(c));
        match cluster {
            "c" => return Some(i),
            "" if !flags.is_empty() => {}
            "W" | "X" => i += 1, // its argument the next word
            _ if cluster.starts_with(['W', 'X']) => {} // its argument glued on
            _ => return None,
        }
        i += 1;
    }
    None
}

/// Whether a Python command line runs a program from its stdin - `python3 -`, `python3 <<BODY`, `python3 < p.py`, `| python3` -
/// rather than a `-c` program, a module or a script (451 T31).
fn python_stdin(toks: &[&str]) -> bool {
    let mut i = 1;
    while let Some(t) = toks.get(i) {
        if *t == "-" || t.starts_with('<') {
            return true;
        }
        let Some(flags) = t.strip_prefix('-').filter(|f| !f.starts_with('-')) else {
            return false; // a script, or a long option (`--version`)
        };
        let cluster = flags.trim_start_matches(|c| PY_FLAGS.contains(c));
        match cluster {
            "" => {}
            "W" | "X" => i += 1, // its argument the next word
            _ if cluster.starts_with(['W', 'X']) => {}
            _ => return false, // `-c`, `-m`
        }
        i += 1;
    }
    true
}

/// The program the word after `python3 -c` carries (451 T31; T33 hands its body to the guards on the walk's target).
pub(super) fn program_of<'a>(word: Option<&&str>, programs: &'a [Program]) -> Option<&'a Program> {
    word.and_then(|w| PROGRAM.captures(w).ok().flatten())
        .and_then(|c| c.get(1)?.as_str().parse::<usize>().ok())
        .and_then(|n| programs.get(n))
}

/// Whether the word after `python3 -c` carries a program that only reads, run in `eff` (451 T31; anything else is D5's write).
pub(super) fn program_reads(word: Option<&&str>, programs: &[Program], eff: Option<&str>) -> bool {
    program_of(word, programs).is_some_and(|(quote, body)| py_c::reads(body, *quote, eff))
}

/// The Python program a segment runs from its stdin (451 T42).
pub(super) enum Stdin {
    /// The segment runs no Python program from stdin.
    None,
    /// It runs one the walk cannot read: a variable, a here-string, a missing or unreadable file, any other upstream.
    Unread,
    /// It runs this one: a heredoc's body, or a readable file's text.
    Program(char, String),
}

/// A readable file's text as a program (literal, `'\''`), the path resolved where the shell stands; a missing file, a directory
/// or a device (`/dev/tty`, which would wait) is one the walk cannot read.
fn file_program(token: Option<&&str>, env: &Env, home: &str, eff: Option<&str>) -> Stdin {
    token
        .and_then(|t| resolve(t, env, home, eff))
        .filter(|p| Path::new(p).is_file())
        .and_then(|p| std::fs::read_to_string(p).ok())
        .map_or(Stdin::Unread, |text| Stdin::Program('\'', text))
}

/// The program a heredoc word (`<<__py_h_<n>__`) carries.
fn heredoc_program(token: &str, programs: &[Program]) -> Option<Stdin> {
    let n = HEREDOC_WORD
        .captures(token)
        .ok()
        .flatten()?
        .get(1)?
        .as_str()
        .parse::<usize>()
        .ok()?;
    programs
        .get(n)
        .map(|(q, body)| Stdin::Program(*q, body.clone()))
}

/// The program a Python segment runs from stdin: its own heredoc or `< file`, else what a `cat` it is piped from (`upstream`)
/// prints - one heredoc or one readable file; anything else the walk cannot read (451 T42).
pub(super) fn stdin_program(
    toks: &[&str],
    upstream: Option<&str>,
    programs: &[Program],
    env: &Env,
    home: &str,
    eff: Option<&str>,
) -> Stdin {
    let is_python = toks
        .first()
        .is_some_and(|h| found(&PYTHON, h.rsplit('/').next().unwrap_or(h)));
    if !is_python || !python_stdin(toks) {
        return Stdin::None;
    }
    for (i, t) in toks.iter().enumerate() {
        if t.starts_with("<<<") {
            return Stdin::Unread;
        }
        if let Some(p) = heredoc_program(t, programs) {
            return p;
        }
        if *t == "<" {
            return file_program(toks.get(i + 1), env, home, eff);
        }
        if let Some(f) = t.strip_prefix('<').filter(|f| !f.starts_with('<')) {
            return file_program(Some(&f), env, home, eff);
        }
    }
    let up: Vec<&str> = upstream.map(words).unwrap_or_default();
    let args: Vec<&str> = up.iter().skip(1).copied().filter(|a| *a != "--").collect();
    match (up.first(), &args[..]) {
        (Some(&"cat"), [a]) => {
            heredoc_program(a, programs).unwrap_or_else(|| file_program(Some(a), env, home, eff))
        }
        (Some(&"cat"), ["<", a]) => file_program(Some(a), env, home, eff),
        _ => Stdin::Unread,
    }
}
