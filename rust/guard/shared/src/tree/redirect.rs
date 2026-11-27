//! A segment's redirects as the walk reads them (moved out of `tree.rs` by 451 T433 for file-scale): each target a redirect writes,
//! after `sanitize` has taken out what writes no file - a `>&` onto an fd (`2>&1`, `>& 2`, `3>&1-`), a closed fd (`>&-`) and a
//! redirect to `/dev/null` by any spelling.
//!
//! The spellings are bash 5.3's, measured 2026-11-27 in a scratch directory (`t433-sh` in the builders' scratchpad): `>& FILE`,
//! `>&FILE` and `1>&FILE` write FILE, as `&> FILE` does; `>&2.log` writes `2.log`, its word no fd; `echo z >& 2` made no file;
//! `echo a >&-x` closed stdout, `x` an argument. A `>&$NAME` is read as a file, the walk unable to tell a variable's fd from a name
//! (no call spelled one in the 73,482 Bash calls of 2026-11-20 to 27).

use super::re;
use crate::regex::Lazy;

/// A redirect's target, the capture: `(?<![<>])\d?(?:>{1,2}|>&)\|?\s*([^\s;&|()<>]+)` with its lookbehind read by `redirects`, so
/// the pattern runs in the regex crate's automaton, not fancy-regex's backtracking machine (451 T83: 0.50 G instructions fewer over
/// T79's ux corpus, the walk's 59.81 G to 59.31 G, the scan itself 0.12 G in 41,052 calls, measured 2026-11-21 under callgrind).
/// A `>&` too (451 T433: `>& FILE` and `>&FILE` were no write); `sanitize` takes out each `>&` an fd follows first, so what one
/// leaves is a file.
static REDIRECT: Lazy = Lazy::new(
    |t| t.contains('>'),
    || re(r"\d?(?:>{1,2}|>&)\|?\s*([^\s;&|()<>]+)"),
);

/// Each redirect target of a segment, as `(?<![<>])` and `REDIRECT` read them together: the leftmost match from where the last
/// ended whose start no `<` or `>` precedes, a match a `<` or `>` precedes tried again a character on.
pub(super) fn redirects(seg: &str) -> Vec<&str> {
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

/// A `>&` an fd follows (`2>&1`, `>& 2`, `3>&1-`), or a `-` (`>&-`, which closes the fd whatever follows). An fd is a whole word:
/// `no_file_out` keeps a match a word goes on after (`>&2.log`). Read in code, not by a lookahead, so the pattern runs in the regex
/// crate's automaton (451 T129).
static DUP_FD: Lazy = Lazy::new(|t| t.contains(">&"), || re(r"\d*>&\s*(?:-|\d+-?)"));
/// `/dev/null` by `>`, `>>`, `>&` or `&>` (451 T433: `>& /dev/null` is no write, as `> /dev/null` is not).
static DEV_NULL: Lazy = Lazy::new(
    |t| t.contains("/dev/null"),
    || re(r"(?:\d+|&)?>>?&?\s*/dev/null"),
);

/// The text with each redirect that writes no file taken out: to `/dev/null`, then onto an fd or closing one, a `DUP_FD` match
/// ending in a digit that a word goes on after being a file's name and kept (451 T433).
pub(super) fn no_file_out(text: &str) -> String {
    let text = DEV_NULL.replace_all(text, " ");
    let Some(r) = DUP_FD.on(&text) else {
        return text.into_owned();
    };
    let (mut out, mut from) = (String::new(), 0);
    for m in r.find_iter(&text).map_while(Result::ok) {
        let goes_on = text[m.end()..]
            .chars()
            .next()
            .is_some_and(|c| !c.is_whitespace() && !";&|()<>".contains(c));
        if m.as_str().ends_with(|c: char| c.is_ascii_digit()) && goes_on {
            continue;
        }
        out.push_str(&text[from..m.start()]);
        out.push(' ');
        from = m.end();
    }
    out + &text[from..]
}
