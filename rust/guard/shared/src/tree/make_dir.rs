//! Where a make runs (451 T409): where its shell stands, moved by each of make's own directory options in turn. WHY: the walk
//! placed every make where its shell stood, so `make -C <another tree> tick` was the gated tree's to the gate-write guard while
//! its gate ran, and every guard reading the walk placed such a make in the wrong tree (found by 451 T307, by reading).
//!
//! The forms are GNU make 4.4.1's, measured 2026-11-26 on a scratch Makefile echoing `$(CURDIR)` (`t409-make` in the builders'
//! scratchpad): `-C D`, `-CD`, `--directory=D`, `--directory D` and an unambiguous prefix of it (`--di=D`; no other long option
//! opens `di`), each relative to the one before and an absolute one afresh, anywhere among the goals (`make x -C a`), inside a
//! cluster (`-sC a`); none past `--`. The value of another option is no directory: `-f -C a` reads `-C` as the makefile, and an
//! option whose value is optional takes only what is joined to it (`-j -C a` is `a`, `-j4C a` refuses). The option lists are
//! `make --help`'s.

use super::{path_write, Env, Known, Write};

/// The short options whose value is required: joined to it, or the next word.
const SHORT_VALUE: &str = "CEfIoW";
/// The short options whose value is optional: only what is joined to it.
const SHORT_OPTIONAL: &str = "jlO";
/// The long options whose value is required, past `directory` itself: after `=`, or the next word.
const LONG_VALUE: [&str; 10] = [
    "assume-new",
    "assume-old",
    "eval",
    "file",
    "include-dir",
    "jobserver-style",
    "makefile",
    "new-file",
    "old-file",
    "what-if",
];

/// The place a make with these words (`toks[0]` the make) runs, as a write's target: the shell's place where no directory option
/// moves it; "named" once an absolute directory frees it from where the shell stands; a directory the walk cannot read judged by
/// what it knows of it, as git's `-C` is (451 T79's one rule).
pub(super) fn make_place(toks: &[&str], env: &Env, home: &str, eff: Option<&str>) -> Write {
    let mut place: Write = (eff.map(str::to_owned), "shell", Known::Shell);
    let mut named = false;
    for dir in directories(&toks[1..]) {
        let (path, how, known) = path_write(dir, env, home, place.0.as_deref());
        named |= how == "named";
        place = (path, if named { "named" } else { "shell" }, known);
    }
    place
}

/// The values of a make's directory options, in order.
fn directories<'a>(args: &[&'a str]) -> Vec<&'a str> {
    let mut dirs = Vec::new();
    let mut words = args.iter().copied();
    while let Some(w) = words.next() {
        if w == "--" {
            break;
        }
        if let Some(long) = w.strip_prefix("--") {
            let (name, joined) = long
                .split_once('=')
                .map_or((long, None), |(n, v)| (n, Some(v)));
            let dir = name.len() >= 2 && "directory".starts_with(name);
            if dir || LONG_VALUE.contains(&name) {
                let value = joined.or_else(|| words.next());
                dirs.extend(value.filter(|_| dir));
            }
        } else if let Some(cluster) = w.strip_prefix('-') {
            let Some((k, ch)) = cluster
                .char_indices()
                .find(|(_, ch)| SHORT_VALUE.contains(*ch) || SHORT_OPTIONAL.contains(*ch))
            else {
                continue;
            };
            let rest = &cluster[k + 1..];
            let value = if !rest.is_empty() {
                Some(rest)
            } else if SHORT_VALUE.contains(ch) {
                words.next()
            } else {
                None
            };
            dirs.extend(value.filter(|_| ch == 'C'));
        }
    }
    dirs
}
