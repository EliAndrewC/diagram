//! How a literal of a Python program is used - read whole (opened, `Path(..).read_text()`, a `/` join read whole), run (an
//! element of a subprocess argv, a list bound to a name only run) or tested (`'x' in s`, `.endswith((..))`) - each naming no file
//! the program writes (451 T96, T118; split out of `program.rs` by 451 T118, file-scale's 1,000-line bar).

use std::cell::OnceCell;

use super::parse::{mask, name, split, word};
use super::{
    ARGV_BEFORE, OPEN_AFTER, OPEN_BEFORE, PATH_AFTER, PATH_BEFORE, SPEC_BEFORE, VALUE_BEFORE,
};

/// Whether every use of the literal `lit` in `body` is a read: opened to read, read through `Path`, an element of a subprocess's
/// argv (a hook RUN, not written: window#56, #299, #312, each running `scripts/hooks/house-style-hooks.sh` - refused on T33's first
/// replay, measured 2026-11-20), or a value in a dict (a hook payload's `file_path`: window#267). Each use is `'lit'` or `"lit"`,
/// found as two plain searches where a pattern was built for each literal on every call (451 T96): what `(['"])lit\1` finds, as a
/// literal holds no quote and so no use of the one kind overlaps one of the other. A part of a path joined by `/` and read whole
/// (`chain_read`) and an element of an argv list bound to a name only run (`display_run`) are reads too (451 T118), read as plain code
/// on the program's `mask`, made once a program and only when one of them is asked.
pub(super) fn only_read(body: &str, lit: &str, masked: &OnceCell<String>) -> bool {
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
                || chain_read(body, masked, (start, start + m.len()))
                || display_run(body, masked, start, false)
        })
}

/// The innermost bracket open at `at` on its line, read on the mask: where it stands.
fn open_at(mask: &str, at: usize) -> Option<usize> {
    let mut depth = 0_usize;
    for (i, c) in mask.as_bytes()[..at].iter().enumerate().rev() {
        match c {
            b'\n' => return None,
            b')' | b']' | b'}' => depth += 1,
            b'(' | b'[' | b'{' if depth == 0 => return Some(i),
            b'(' | b'[' | b'{' => depth -= 1,
            _ => {}
        }
    }
    None
}

/// The bracket closing the one at `open`, on its line, read on the mask.
fn close_at(mask: &str, open: usize) -> Option<usize> {
    let mut depth = 0_usize;
    for (i, c) in mask.bytes().enumerate().skip(open) {
        match c {
            b'\n' => return None,
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

/// Whether the literal quoted at `(from, to)` (its quotes too) is a part of a path joined by `/` and read whole: the join alone in
/// its own parenthesis or `Path(`'s, on one line, closed by `.read_text(` or `.read_bytes(` - `(root / 'scripts' /
/// 'house-style-hooks.sh').read_text()` (451 T118: window#305, #306 and #309 read the house-style hook so, refused by make-only and
/// gate-write as its write). A join bound to a name, opened, written, or in a tuple is not read here, and fails closed as before.
pub(super) fn chain_read(
    body: &str,
    masked: &OnceCell<String>,
    (from, to): (usize, usize),
) -> bool {
    // the gate: a `/` beside the literal
    if !(body[..from].trim_end().ends_with('/') || body[to..].trim_start().starts_with('/')) {
        return false;
    }
    let mask = masked.get_or_init(|| mask(body));
    let Some(open) = open_at(mask, from).filter(|&o| mask.as_bytes()[o] == b'(') else {
        return false;
    };
    let Some(close) = close_at(mask, open) else {
        return false;
    };
    let callee = mask[..open].trim_end();
    let grouped = !callee.ends_with(|c: char| word(c) || c == '.');
    let path = callee
        .strip_suffix("Path")
        .is_some_and(|n| !n.ends_with(word));
    let read = body[close + 1..]
        .trim_start()
        .strip_prefix('.')
        .is_some_and(|r| r.starts_with("read_text(") || r.starts_with("read_bytes("));
    let inner = (open + 1, close);
    (grouped || path)
        && read
        && split(mask, inner, b",").len() == 1
        && split(mask, inner, b"/").len() > 1
}

/// The functions whose first argument is a subprocess's argv: `ARGV_BEFORE`'s.
const RUNS: [&str; 5] = ["run", "call", "check_call", "check_output", "Popen"];

/// Each place the name `n` stands in the mask as a whole name: no name character, or a `.`, before it; no name character after.
fn uses<'m>(mask: &'m str, n: &'m str) -> impl Iterator<Item = usize> + 'm {
    mask.match_indices(n).map(|(i, _)| i).filter(move |&i| {
        !mask[..i].ends_with(|c: char| word(c) || c == '.')
            && !mask[i + n.len()..].starts_with(word)
    })
}

/// Whether the name `n` at `at` is a subprocess's whole argv: the first argument of one of `RUNS` (`subprocess.run(old, ...)`).
fn run_arg(mask: &str, at: usize, n: &str) -> bool {
    let run = mask[..at].trim_end().strip_suffix('(').is_some_and(|f| {
        RUNS.iter()
            .any(|r| f.strip_suffix(r).is_some_and(|x| !x.ends_with(word)))
    });
    run && mask[at + n.len()..].trim_start().starts_with([',', ')'])
}

/// Whether `x` ends with a `for`'s targets (`for a`, `for a, b`), so an `in` after it iterates and tests nothing.
fn for_targets(x: &str) -> bool {
    let mut y = x.trim_end();
    loop {
        let z = y.trim_end_matches(word);
        if z.len() == y.len() {
            return false;
        }
        let z = z.trim_end();
        match z.strip_suffix(',') {
            Some(w) => y = w,
            None => return z.strip_suffix("for").is_some_and(|p| !p.ends_with(word)),
        }
    }
}

/// Whether `before` ends with a membership test's `in` (`w in`, `w not in`), not a `for`'s (`for w in`).
fn tests_in(before: &str) -> bool {
    before
        .trim_end()
        .strip_suffix("in")
        .filter(|x| x.ends_with(char::is_whitespace))
        .is_some_and(|x| !for_targets(x))
}

/// The variable of the `for` iterating a tuple or list on one line, its elements names alone, that holds the name `n` at `at`, and
/// where the variable stands: `g` of `for g in (old, new)`.
fn for_var<'m>(mask: &'m str, at: usize, n: &str) -> Option<(&'m str, usize)> {
    let open = open_at(mask, at).filter(|&o| matches!(mask.as_bytes()[o], b'(' | b'['))?;
    let close = close_at(mask, open)?;
    let names = &mask[open + 1..close];
    if !names.contains(n)
        || !names
            .chars()
            .all(|c| word(c) || c == ',' || c.is_whitespace())
    {
        return None;
    }
    let head = mask[..open]
        .trim_end()
        .strip_suffix("in")
        .filter(|h| h.ends_with(char::is_whitespace))?
        .trim_end();
    let start = head.rfind(|c: char| !word(c)).map_or(0, |i| i + 1);
    let v = &head[start..];
    let keyword = head[..start]
        .trim_end()
        .strip_suffix("for")
        .is_some_and(|p| !p.ends_with(word));
    (name(v) && keyword).then_some((v, start))
}

/// Whether the name `n` stands in a string's `{` with no `}` after it before the name: an f-string's placeholder, code the mask blanks.
fn placeholder(body: &str, mask: &str, n: &str) -> bool {
    body.match_indices(n).any(|(i, _)| {
        mask.as_bytes()[i] == b'~' && {
            let quote = mask[..i].rfind(|c: char| c != '~').unwrap_or(0);
            let inside = &body[quote + 1..i];
            inside
                .rfind('{')
                .is_some_and(|o| !inside[o..].contains('}'))
        }
    })
}

/// Whether every use of the name `n`, bound at `bind`, is a subprocess's argv - `run_arg`, or an element of what a `for` iterates
/// whose variable is only so used (`for g in (old, new)` and `run(g, ...)`, one level) - or, with `tests`, what `in` tests (`w in
/// AB`); a program that never uses it again uses it for nothing. Its text in a string is text, but not in an f-string's placeholder.
/// A name bound again, or used any other way - an element taken, the list grown, handed on - is not.
fn only_run(body: &str, mask: &str, (n, bind): (&str, usize), tests: bool, deep: bool) -> bool {
    uses(mask, n).all(|at| {
        at == bind
            || run_arg(mask, at, n)
            || (tests && tests_in(&mask[..at]))
            || (!deep
                && for_var(mask, at, n).is_some_and(|var| only_run(body, mask, var, false, true)))
    }) && !placeholder(body, mask, n)
}

/// The name a display holding the literal quoted at `from` is bound to - `NAME = [`, `(` or `{` on its line, the literal among the
/// display's elements on that line with no bracket, `:` or `=` between - and where the name stands.
fn display_name(mask: &str, from: usize) -> Option<(&str, usize)> {
    let line = mask[..from].rfind('\n').map_or(0, |i| i + 1);
    let (lhs, rhs) = mask[line..from].split_once('=')?;
    let inner = rhs.trim_start().strip_prefix(['[', '(', '{'])?;
    let n = lhs.trim();
    (name(n) && !rhs.starts_with('=') && !inner.contains(['[', ']', '(', ')', '{', '}', ':', '=']))
        .then(|| (n, line + lhs.len() - lhs.trim_start().len()))
}

/// Whether the literal quoted at `from` is an element of a display bound to a name only run as a subprocess's argv or, with `tests`,
/// only tested (`only_run`): `old = ['<clone>/scripts/hooks/l7r-guard.sh', '--only', ...]` then `subprocess.run(old, ...)` (451 T118:
/// t67's `corpus.py` and `replay-log.py`, 12 rows of T93's corpus on T51's script route, refused by make-only and gate-write as the
/// hook's write), read as plain code behind a gate: an `=` and an open bracket on the line before it.
fn display_run(body: &str, masked: &OnceCell<String>, from: usize, tests: bool) -> bool {
    let line = &body[body[..from].rfind('\n').map_or(0, |i| i + 1)..from];
    if !line.contains('=') || !line.contains(['[', '(', '{']) {
        return false;
    }
    let mask = masked.get_or_init(|| mask(body));
    display_name(mask, from).is_some_and(|bound| only_run(body, mask, bound, tests, false))
}

/// Whether the literal quoted at `(from, to)` is what a test reads, text and not a path (451 T118, found by T51 on 2026-11-21: T93's
/// `moved.py`, `variants.py`, `reds.py`, `measure.py` and `resid.py` and T33's window#305 and #309, each refused by gate-write as the
/// write of a dotted word): `'plan.md' in cmd`, `'static.log' not in t`, an element of the display `in` tests (`w in {"e.g", ...}`) or
/// of a tuple `endswith` or `startswith` tests (`s.endswith(('.log', '.out'))`), on its line with no bracket between; or an element
/// of a display bound to a name only tested, run or never used (`display_run`). A `for`'s `in` iterates, and tests nothing. Placed
/// alone: make-only, fail-closed, counts a literal tested, as it counts one compared, since the name tested may be the name written.
pub(super) fn tested(body: &str, masked: &OnceCell<String>, (from, to): (usize, usize)) -> bool {
    let after = body[to..].trim_start();
    let after = after
        .strip_prefix("not")
        .filter(|r| r.starts_with(char::is_whitespace))
        .map_or(after, str::trim_start);
    if after
        .strip_prefix("in")
        .is_some_and(|r| !r.starts_with(word))
    {
        return true;
    }
    let line = &body[body[..from].rfind('\n').map_or(0, |i| i + 1)..from];
    let display = line
        .rfind(['[', '(', '{'])
        .filter(|&o| !line[o + 1..].contains(['[', ']', '(', ')', '{', '}']));
    // an affix test: the literal an argument of `.startswith(`/`.endswith(` (451 T118's plan review: T58's `commits.py`,
    // `f.startswith('rust/guard/src/')`), or an element of the tuple one takes
    let affix = |f: &str| {
        let f = f.trim_end();
        f.ends_with(".endswith") || f.ends_with(".startswith")
    };
    let tests = display.is_some_and(|o| {
        let head = line[..o].trim_end();
        tests_in(head)
            || (line[o..].starts_with('(') && affix(head))
            || head.strip_suffix('(').is_some_and(affix)
    });
    tests || display_run(body, masked, from, true)
}
