//! `archive_ops.py`'s five commands as `l7r-gate record archive <verb>` (feature 449 T147, phase 4's S3b): `inbox`, `consulted`, `find`,
//! `urls` and `relayout`, their flags and refusals read as its argparse read them (`ask:449-usage-text`: the refusal's words are the
//! port's, its exit 2 and empty stdout the Python's).

use std::path::Path;

use l7r_gate_core::record::args::{parse, parse_with, Spec};

use super::{raised, reply, usage, Reach};
use crate::ops::{self, find::find, py_int, relayout::relayout};
use crate::Reply;

/// An `int` flag's value, or argparse's refusal.
fn int_flag(
    p: &l7r_gate_core::record::args::Parsed,
    name: &str,
    default: i64,
) -> Result<i64, Reply> {
    if !p.has(name) {
        return Ok(default);
    }
    let raw = p.text(name, "");
    py_int(raw).ok_or_else(|| usage(&format!("argument {name}: invalid int value: '{raw}'")))
}

/// One of the five, from `root`.
#[must_use]
pub fn cli(verb: &str, rest: &[String], root: &Path, reach: &Reach<'_>) -> Reply {
    let flags: &[Spec] = match verb {
        "inbox" => &[Spec::value("--match"), Spec::value("--none")],
        "consulted" => &[Spec::value("--limit"), Spec::value("--workers")],
        "find" => &[
            Spec::value("--url"),
            Spec::value("--key"),
            Spec::value("--terms"),
        ],
        _ => &[],
    };
    let p = match if verb == "urls" {
        parse_with(rest, flags, usize::MAX)
    } else {
        parse(rest, flags)
    } {
        Ok(p) => p,
        Err(e) => return usage(&e),
    };
    match verb {
        "inbox" => {
            let raw: Vec<String> = p.all("--match").into_iter().map(str::to_owned).collect();
            let mut matched = match ops::resolve_matches(root, &raw) {
                Ok(m) => m,
                Err(why) => return reply(String::new(), format!("{}\n", why.trim()), 1),
            };
            for n in p.all("--none") {
                matched.set(n, Vec::new());
            }
            let mut out = String::new();
            match ops::inbox(root, &(reach.store)(root), &matched, &mut out) {
                Ok(()) => reply(out, String::new(), 0),
                Err(e) => raised(out, &e),
            }
        }
        "consulted" => {
            let (limit, workers) = match (int_flag(&p, "--limit", 0), int_flag(&p, "--workers", 4))
            {
                (Ok(l), Ok(w)) => (l, w),
                (Err(r), _) | (_, Err(r)) => return r,
            };
            let store = (reach.store)(root);
            let how = ops::Reach {
                start: reach.start,
                say: reach.say,
                store: &store,
            };
            match ops::consulted(root, limit, workers, &how) {
                Ok(code) => reply(String::new(), String::new(), code),
                Err(e) => raised(String::new(), &e),
            }
        }
        "find" => {
            let mut out = String::new();
            let store = (reach.store)(root);
            match find(
                root,
                &store,
                p.text("--url", ""),
                p.text("--key", ""),
                p.text("--terms", ""),
                &mut out,
            ) {
                Ok(code) => reply(out, String::new(), code),
                Err(e) => raised(out, &e),
            }
        }
        "urls" if p.positional.is_empty() => usage("the following arguments are required: urls"),
        "urls" => {
            let mut err = String::new();
            let start = |r: &Path| (reach.start)(r);
            match ops::archive_urls(root, &p.positional, &start, reach.store, &mut err) {
                Ok(()) => reply(String::new(), err, 0),
                Err(e) => reply(String::new(), format!("{err}{e}\n"), 1),
            }
        }
        _ => match relayout(root, &(reach.store)(root)) {
            Ok(n) => reply(
                format!("archive: {n} row(s) moved to the sharded layout\n"),
                String::new(),
                0,
            ),
            Err(e) => raised(String::new(), &e),
        },
    }
}

#[cfg(test)]
mod tests;
