//! Every `fancy_regex` pattern of the Rust tools is built with no step limit, and every scan ends on its first error (feature 449 T185).
//!
//! WHY: `fancy_regex` 0.14 gives up a backtracking search past its step limit - a million by default - with an `Err` its iterators
//! repeat without advancing, so a `.flatten()` over a `find_iter` retried forever at 100% CPU (`make quick` on a 157 KB one-line file,
//! T151; `make decide` and `make task-add` on 449's 1 MB of plan, T194), and a single search past the limit quietly read as no match.
//! T185 built every pattern through `l7r_shared::regex` (the limit lifted, its comment has the measurements) and ended every
//! scan with `.map_while(Result::ok)`; this check refuses a new site of either kind, its message the compliant call.

use std::path::Path;

use super::{files_under, read, rel, root};

/// The files the rules do not read, each with its reason.
const EXEMPT: [(&str, &str); 2] = [
    (
        "rust/guard/shared/src/regex.rs",
        "the shared constructor itself, and its test of the bounded default",
    ),
    (
        "rust/gate/crates/checks/src/checks/documents/regex_scans.rs",
        "this check, whose self-test seeds each refused form",
    ),
];

/// What a scan's iterator may be followed by: the adapter that ends on the first error (spelled in full where a crate's own `Result`
/// shadows the standard one), or one item taken.
const SCAN_ENDS: [&str; 3] = [
    ".map_while(Result::ok)",
    ".map_while(std::result::Result::ok)",
    ".next()",
];

/// What a regex split's iterator may not be followed by: the adapters that skip an error and ask again.
const SKIPS: [&str; 4] = [
    ".flatten()",
    ".filter_map(Result::ok)",
    ".filter_map(std::result::Result::ok)",
    ".filter_map(|r| r.ok())",
];

const BUILD_FIX: &str = "keeps fancy_regex's 1,000,000-step limit, past which a search errs (a scan spins, a single search reads as no match) - build it with `l7r_shared::regex::build(pattern)` (in the guard crate `crate::shared::regex::build`), or `regex::builder(pattern)` to set another option first";
const SCAN_FIX: &str = "an error at the regex engine's limit repeats without advancing, so the scan can spin forever - end it on its first error with `.map_while(Result::ok)` (`.map_while(std::result::Result::ok)` where the crate's own `Result` shadows the standard one)";

/// The index of the `)` that closes the `(` at `open`, string and character literals skipped; None where it never closes.
fn closing(src: &[u8], open: usize) -> Option<usize> {
    let (mut depth, mut i) = (0usize, open);
    while i < src.len() {
        match src[i] {
            b'(' => depth += 1,
            b')' => {
                depth -= 1;
                if depth == 0 {
                    return Some(i);
                }
            }
            b'"' => {
                i += 1;
                while i < src.len() && src[i] != b'"' {
                    i += if src[i] == b'\\' { 2 } else { 1 };
                }
            }
            b'\'' if src.get(i + 2) == Some(&b'\'') => i += 2,
            _ => {}
        }
        i += 1;
    }
    None
}

fn line_of(src: &str, at: usize) -> usize {
    src[..at].matches('\n').count() + 1
}

/// Each refused construction or scan in one source file, named by `name` and its line, with its fix.
fn of_source(name: &str, src: &str) -> Vec<String> {
    let mut out: Vec<(usize, String)> = Vec::new();
    for (at, _) in src.match_indices("::new(") {
        let head = &src[..at];
        let built = ["Regex", "RegexBuilder"].into_iter().find(|t| {
            head.ends_with(t)
                && !head[..head.len() - t.len()]
                    .ends_with(|c: char| c.is_alphanumeric() || c == '_')
        });
        if let Some(t) = built {
            let line = line_of(src, at);
            out.push((line, format!("{name}:{line}: `{t}::new` {BUILD_FIX}")));
        }
    }
    let bytes = src.as_bytes();
    for call in [".find_iter(", ".captures_iter(", ".split(", ".splitn("] {
        for (at, _) in src.match_indices(call) {
            let Some(end) = closing(bytes, at + call.len() - 1) else {
                continue;
            };
            let next = src[end + 1..].trim_start();
            let scan = call.ends_with("iter(");
            let refused = if scan {
                !SCAN_ENDS.iter().any(|ok| next.starts_with(ok))
            } else {
                SKIPS.iter().any(|skip| next.starts_with(skip))
            };
            if refused {
                let shown: String = next.chars().take_while(|c| *c != '\n').take(40).collect();
                let line = line_of(src, at);
                let what = &call[1..call.len() - 1];
                out.push((
                    line,
                    format!("{name}:{line}: `{what}(..)` followed by `{shown}`: {SCAN_FIX}"),
                ));
            }
        }
    }
    out.sort_by_key(|(line, _)| *line);
    out.into_iter().map(|(_, problem)| problem).collect()
}

/// Every refused site under `rust/` of the tree at `top`.
fn problems(top: &Path) -> Vec<String> {
    files_under(&top.join("rust"), ".rs")
        .iter()
        .map(|p| (rel(p, top), p))
        .filter(|(name, _)| !EXEMPT.iter().any(|(e, _)| e == name))
        .flat_map(|(name, p)| of_source(&name, &read(p)))
        .collect()
}

#[test]
fn every_regex_is_built_unlimited_and_every_scan_ends_on_its_error() {
    assert_eq!(problems(&root()), Vec::<String>::new());
}

#[test]
fn each_refused_form_is_caught_with_its_fix() {
    let seeded = concat!(
        "static A: LazyLock<Regex> = LazyLock::new(|| Regex::new(r\"\\bx\").unwrap());\n",
        "let b = fancy_regex::RegexBuilder::new(p).build();\n",
        "let c = MyRegex::new(p); let d = LazyLock::new(f);\n",
        "for m in A.find_iter(&format!(\"(\")).flatten() {}\n",
        "let n = A.captures_iter(t)\n    .filter_map(Result::ok).count();\n",
        "let k = A.find_iter(t).count();\n",
        "for w in A.split(t).flatten() {}\n",
        "let fine = A.find_iter(t).map_while(Result::ok).count() + A.captures_iter(t).next().is_some() as usize;\n",
        "let full = A.find_iter(t).map_while(std::result::Result::ok);\n",
        "let words = text.split(' ').filter(|w| !w.is_empty()); let q = A.split(t).map_while(Result::ok);\n",
        "let c = ')'; let open = A.find_iter(t",
    );
    let got = of_source("x.rs", seeded);
    assert_eq!(got.len(), 6, "{got:#?}");
    assert!(got[0].starts_with("x.rs:1: `Regex::new` keeps fancy_regex's 1,000,000-step limit"));
    assert!(got[0].ends_with("or `regex::builder(pattern)` to set another option first"));
    assert!(got[1].starts_with("x.rs:2: `RegexBuilder::new` keeps"));
    assert!(got[2].starts_with("x.rs:4: `find_iter(..)` followed by `.flatten() {}`: an error"));
    assert!(got[2].ends_with("`.map_while(std::result::Result::ok)` where the crate's own `Result` shadows the standard one)"));
    assert!(got[3]
        .starts_with("x.rs:5: `captures_iter(..)` followed by `.filter_map(Result::ok).count();`"));
    assert!(got[4].starts_with("x.rs:7: `find_iter(..)` followed by `.count();`"));
    assert!(got[5].starts_with("x.rs:8: `split(..)` followed by `.flatten() {}`"));
    assert_eq!(closing(b"(\"a\\\"b\"", 0), None);
}
