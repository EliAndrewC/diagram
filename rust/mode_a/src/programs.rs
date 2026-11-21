//! `make building-programs` (feature 449 T168; `l7r/diagram/tools/building_programs.py` ported and deleted): the required-items table
//! of every declared Mode A type, rendered into `docs/building-programs.md` between markers (feature 254, plan D11).
//!
//! WHY. The GM's rule for the second type was that a type is declared ONCE and the docs render from it. The checks read
//! `buildings/types.json`; the reviewers read the programs page. Written separately the two drift - the tub check's fill list and its
//! docstring did exactly that (2026-07-25) - so the table the reviewer reads is DERIVED from the declaration, and `--check` fails the
//! gate when it is stale, as `make glossary CHECK=1` holds the glossary asset to its source.
//!
//! Each type's block sits between `<!-- types.json:<tier> -->` and `<!-- /types.json:<tier> -->`; the prose around it (knobs, anchors,
//! staffing, the composition rules) is hand-written and untouched. Every line this writes, and every refusal, is the Python's byte for
//! byte (FR-002: a docs generator's output is bound exactly).
//!
//! Research:
//!     the programs page's tables - NONE: rendered from the declaration, deciding nothing; the page's own claims are in `docs/building-programs.md`

use std::collections::HashMap;
use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_core::Reply;
use l7r_gate_research::record::site_links::relpath;
use l7r_gate_research::Error;
use l7r_shared::py_text::{fmt_g, repr};

use crate::py::{os_error, uncaught};
use crate::types::{classification, load_types, Band, BuildingType, Kinds};

/// The programs page, from the tree's root (the Python's `PROGRAMS`).
pub const PROGRAMS: &str = "docs/building-programs.md";

/// One band as the table writes it: `presence`, or its w-by-h and its area, `:g` each.
#[must_use]
pub fn band_text(band: &Band) -> String {
    if band.presence_only() {
        return "presence".to_owned();
    }
    let mut parts = Vec::new();
    if let (Some(w), Some(h)) = (band.w, band.h) {
        parts.push(format!(
            "{}-{} by {}-{} ft",
            fmt_g(w.0),
            fmt_g(w.1),
            fmt_g(h.0),
            fmt_g(h.1)
        ));
    }
    if let Some(a) = band.area {
        parts.push(format!("{}-{} sq ft", fmt_g(a.0), fmt_g(a.1)));
    }
    parts.join("; ")
}

/// The Markdown table for one type: item, the label it is found by, its band, its class, its why; then its notes.
///
/// # Errors
/// What [`classification`] refuses of a kind item.
pub fn render(btype: &BuildingType, kinds: &mut Kinds) -> Result<String, Error> {
    let mut lines = vec![
        "| item | found by the tag or label (or declared by id) | band (feet; either orientation) | class | why |".to_owned(),
        "|---|---|---|---|---|".to_owned(),
    ];
    for it in &btype.required {
        let forms: Vec<String> = it
            .forms
            .iter()
            .map(|(f, b)| {
                format!(
                    "under `{f}`: {}",
                    b.as_ref().map_or_else(|| "absent".to_owned(), band_text)
                )
            })
            .collect();
        let mut band = band_text(&it.band);
        if !forms.is_empty() {
            let _ = write!(band, " ({})", forms.join("; "));
        }
        if it.optional {
            band += " - optional, a knob";
        }
        if let Some(site) = &it.site {
            // a SITE item (feature 257): drawn where the declared map shows its class, and only there
            let _ = write!(
                band,
                " - a site item: drawn where the sheet's declared map shows a {} inside the frame",
                site.replace('_', " ")
            );
        }
        let found = it.kind.as_ref().map_or_else(
            || format!("`/{}/`", it.label.as_deref().unwrap_or_default()),
            |k| format!("`data-kind=\"{k}\"`"),
        );
        let (cls, why) = classification(it, kinds)?;
        lines.push(format!(
            "| `{}` | {found} | {band} | {cls} | {why} |",
            it.id
        ));
    }
    if !btype.notes.is_empty() {
        lines.push(String::new());
        lines.push(btype.notes.clone());
    }
    Ok(lines.join("\n"))
}

static BLOCK: LazyLock<Regex> = LazyLock::new(|| {
    l7r_shared::regex::build(
        r"(?s)<!-- types\.json:([a-z0-9-]+) -->\n(.*?)\n<!-- /types\.json:\1 -->",
    )
    .unwrap_or_else(|e| unreachable!("{e}"))
});

/// Each tier's block body, by byte span; a tier marked twice keeps its last block, as the Python's dict did.
fn blocks(text: &str) -> HashMap<String, (usize, usize)> {
    BLOCK
        .captures_iter(text)
        .map_while(Result::ok)
        .filter_map(|m| {
            Some((
                m.get(1)?.as_str().to_owned(),
                m.get(2).map(|g| (g.start(), g.end()))?,
            ))
        })
        .collect()
}

/// The page with every marked block rewritten from its declaration, and the tiers that have no block (`apply`). The blocks are
/// rewritten last first, so each span still holds; a type with no block renders nothing.
///
/// # Errors
/// What [`render`] refuses.
pub fn apply(
    text: &str,
    types: &[BuildingType],
    kinds: &mut Kinds,
) -> Result<(String, Vec<String>), Error> {
    let spans = blocks(text);
    let missing = types
        .iter()
        .filter(|t| !spans.contains_key(&t.tier))
        .map(|t| t.tier.clone())
        .collect();
    let mut order: Vec<&BuildingType> = types.iter().collect();
    // a stable sort, descending, as Python's `sorted(..., reverse=True)` keeps equal keys in their order
    order.sort_by(|a, b| {
        let at = |t: &BuildingType| spans.get(&t.tier).map_or(0, |s| s.0);
        at(b).cmp(&at(a))
    });
    let mut out = text.to_owned();
    for t in order {
        if let Some(&(a, b)) = spans.get(&t.tier) {
            out.replace_range(a..b, &render(t, kinds)?);
        }
    }
    Ok((out, missing))
}

const USAGE: &str = "usage: l7r-mode-a building-programs [-h] [--check] [--path PATH]\n";
const PROG: &str = "l7r-mode-a building-programs";

/// argparse's `--help` for the Python's parser, wrapped as it wrapped it at 80 columns.
const HELP: &str = "
`make building-programs`: the required-items table of every declared Mode A
type, rendered into

options:
  -h, --help   show this help message and exit
  --check      exit 1 if the rendered blocks are stale or a declared type has
               no block
  --path PATH
";

/// What the command line asked.
#[derive(Debug, PartialEq, Eq)]
enum Ask {
    Run { check: bool, path: Option<String> },
    Help,
    Refused(String),
}

/// argparse's taking of an argument as an option: a dash and more, not a negative number, not a phrase with a space.
fn optional(arg: &str) -> bool {
    let negative = arg.strip_prefix('-').is_some_and(|n| {
        let (int, frac) = n.split_once('.').unwrap_or((n, ""));
        let digits = |s: &str| s.bytes().all(|b| b.is_ascii_digit());
        digits(int) && digits(frac) && (!frac.is_empty() || (!int.is_empty() && !n.contains('.')))
    });
    let known = arg.starts_with("--")
        && arg.len() > 2
        && long(arg.split('=').next().unwrap_or(arg)).is_some();
    arg.starts_with('-') && arg.len() > 1 && (known || !(negative || arg.contains(' ')))
}

/// A long option, exact or by a unique prefix (argparse's `allow_abbrev`): the three never share one past `--`.
fn long(word: &str) -> Option<&'static str> {
    ["--check", "--help", "--path"]
        .into_iter()
        .find(|o| word.len() > 2 && o.starts_with(word))
}

/// The Python's `argparse` over `--check` and `--path`: an unknown argument is collected and refused at the end, a malformed known one
/// at once; `-h` anywhere before a refusal asks for the help.
fn parse(args: &[String]) -> Ask {
    let (mut check, mut path, mut extras) = (false, None, Vec::new());
    let ignored = |name: &str, v: &str| {
        Ask::Refused(format!(
            "argument {name}: ignored explicit argument {}",
            repr(v)
        ))
    };
    let mut rest = args.iter();
    while let Some(arg) = rest.next() {
        if arg == "--" {
            extras.extend(std::iter::once(arg).chain(rest.by_ref()).cloned());
            break;
        }
        if !optional(arg) {
            extras.push(arg.clone());
            continue;
        }
        let (name, inline) = if arg.starts_with("--") {
            let (word, inline) = arg
                .split_once('=')
                .map_or((arg.as_str(), None), |(w, v)| (w, Some(v)));
            (long(word), inline)
        } else {
            // one dash: only `-h` is a short option, and a word it opens (`-hx`, `-help`) is short flags run together, whose first,
            // `-h`, prints the help before the rest is read (observed 2026-11-17 in CPython 3.14.4's argparse, T168's differential)
            (arg.starts_with("-h").then_some("--help"), None)
        };
        match (name, inline) {
            (None, _) => extras.push(arg.clone()),
            (Some("--help"), None) => return Ask::Help,
            (Some("--help"), Some(v)) => return ignored("-h/--help", v),
            (Some("--check"), None) => check = true,
            (Some("--check"), Some(v)) => return ignored("--check", v),
            (_, Some(v)) => path = Some(v.to_owned()),
            (_, None) => match rest.as_slice().first() {
                Some(v) if !optional(v) && v != "--" => {
                    path = Some(v.clone());
                    rest.next();
                }
                _ => return Ask::Refused("argument --path: expected one argument".to_owned()),
            },
        }
    }
    if extras.is_empty() {
        Ask::Run { check, path }
    } else {
        Ask::Refused(format!("unrecognized arguments: {}", extras.join(" ")))
    }
}

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// The command (`main`): render the blocks; with `--check`, refuse a stale page rather than write it.
#[must_use]
pub fn main(args: &[String], tree: &Path) -> Reply {
    let (check, path) = match parse(args) {
        Ask::Help => return reply(format!("{USAGE}{HELP}"), String::new(), 0),
        Ask::Refused(why) => {
            return reply(String::new(), format!("{USAGE}{PROG}: error: {why}\n"), 2)
        }
        Ask::Run { check, path } => (
            check,
            path.unwrap_or_else(|| format!("{}/{PROGRAMS}", tree.display())),
        ),
    };
    match run(check, &path, tree) {
        Ok(r) => r,
        Err(e) => reply(String::new(), uncaught(&e), 1),
    }
}

fn run(check: bool, path: &str, tree: &Path) -> Result<Reply, Error> {
    let text = l7r_gate_core::record::read_text(Path::new(path)).map_err(|e| os_error(&e, path))?;
    let (new, missing) = apply(&text, &load_types(tree)?, &mut Kinds::new(tree))?;
    let shown = relpath(path, "");
    if !missing.is_empty() {
        let why = format!(
            "building-programs: no `<!-- types.json:<tier> -->` block in {path} for: {}\n",
            missing.join(", ")
        );
        return Ok(reply(String::new(), why, 1));
    }
    if new == text {
        return Ok(reply(
            format!("building-programs: {shown} is current\n"),
            String::new(),
            0,
        ));
    }
    if check {
        let why = format!("building-programs: {shown} is STALE - run `make building-programs`\n");
        return Ok(reply(String::new(), why, 1));
    }
    std::fs::write(path, new).map_err(|e| os_error(&e, path))?;
    Ok(reply(
        format!("building-programs: wrote {shown}\n"),
        String::new(),
        0,
    ))
}

#[cfg(test)]
mod tests;
