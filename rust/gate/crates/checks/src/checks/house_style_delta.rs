//! American spellings in what this change wrote (feature 236; feature 449 T065, from `check-house-style-delta.py`): the delta's added lines and untracked files, where a moved line, a quotation, a code span, a line the base already
//! held and the middle of a proper name are all someone else's. The word table is the guard's own. A run is recorded by `usage_log` under `USAGE_LOG_TOOL`.

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;
use std::process::Command;

use fancy_regex::Regex;

use super::moves::moved_only;
use super::{git_text, Outcome};

pub(super) const USAGE_LOG_TOOL: &str = "check-house-style-delta";
const WORDS: &str = include_str!("../../../../../guard/src/guards/house_style_words.tsv");
const EXEMPT_DIRS: [&str; 3] = ["/.clones/", "/host-l7r-repo/", "/tests/hooks/fixtures/"];

fn pattern(text: &str) -> Regex {
    Regex::new(text).unwrap()
}

fn british() -> Vec<&'static str> {
    WORDS
        .lines()
        .filter_map(|l| l.split('\t').next())
        .filter(|w| !w.is_empty())
        .collect()
}

fn exempt_path(path: &str) -> bool {
    let names = pattern(
        r"(^|/)(CLAUDE\.md|constitution\.md|l7r-style\.md|house-style-hooks\.sh|test-house-style-hooks\.sh|house_style_cases\.rs|house_style_delta\.rs|house_style_delta/tests\.rs|test_guard_firing_log\.py|hm_house\.py|house_style_hooks\.rs|house_style_words\.tsv|l7r\.md|gm-request\.md)$",
    );
    let verbatim = pattern(r"specs/[^/]+/request\.md$");
    let dump = pattern(r"(^|/)specs/[^/]+/measure/[^/]+_(?:cells_by_address|rows_raw)\.txt$");
    let slashed = format!("/{path}");
    [names, verbatim, dump]
        .iter()
        .any(|p| p.is_match(path).unwrap_or(false))
        || EXEMPT_DIRS.iter().any(|d| slashed.contains(d))
}

/// The byte ranges of the whole file a house-style rule does not reach.
fn exempt_spans(text: &str, path: &str) -> Vec<(usize, usize)> {
    let mut body = "```.*?```|`[^`]*`|「[^」]*」|『[^』]*』|“[^”]*”|<q(?:[^\\w>][^>]*)?>.*?</q>|<blockquote(?:[^\\w>][^>]*)?>.*?</blockquote>|<!--\\s*SOURCE: GM NOTES.*?<!--\\s*END SOURCE\\s*-->".to_owned();
    if super::has_ext(path, "md") || super::has_ext(path, "html") || super::has_ext(path, "txt") {
        body += "|\"[^\"\n]*\"";
    }
    pattern(&format!("(?si){body}"))
        .find_iter(text)
        .flatten()
        .map(|m| (m.start(), m.end()))
        .collect()
}

type Added = BTreeMap<String, Vec<(usize, String)>>;

/// Each path's added lines with their numbers, and every removed line's text, for the delta and untracked files.
fn delta_lines(root: &Path, base: &str) -> (Added, BTreeSet<String>) {
    let (mut added, mut removed): (Added, BTreeSet<String>) = (BTreeMap::new(), BTreeSet::new());
    let (mut path, mut line_no) = (String::new(), 0_usize);
    let hunk = pattern(r"\+(\d+)");
    for raw in git_text(root, &["diff", "-U0", base]).split('\n') {
        if let Some(rest) = raw.strip_prefix("+++ b/") {
            rest.clone_into(&mut path);
        } else if raw.starts_with("@@") {
            line_no = hunk
                .captures(raw)
                .ok()
                .flatten()
                .and_then(|c| c.get(1).and_then(|m| m.as_str().parse().ok()))
                .unwrap_or(0);
        } else if let Some(text) = raw.strip_prefix('+').filter(|_| !raw.starts_with("+++")) {
            added
                .entry(path.clone())
                .or_default()
                .push((line_no, text.to_owned()));
            line_no += 1;
        } else if let Some(text) = raw.strip_prefix('-').filter(|_| !raw.starts_with("---")) {
            removed.insert(text.trim().to_owned());
        }
    }
    let names: Vec<String> = added.keys().cloned().collect();
    for moved in moved_only(root, base, &names) {
        added.remove(&moved);
    }
    for name in git_text(root, &["ls-files", "--others", "--exclude-standard"])
        .split('\n')
        .filter(|n| !n.trim().is_empty())
    {
        let p = root.join(name);
        if p.is_file() && p.metadata().is_ok_and(|m| m.len() < 2_000_000) {
            let body = String::from_utf8_lossy(&std::fs::read(&p).unwrap_or_default()).into_owned();
            added.entry(name.to_owned()).or_default().extend(
                body.split('\n')
                    .enumerate()
                    .map(|(i, t)| (i + 1, t.to_owned())),
            );
        }
    }
    (added, removed)
}

/// Does this exact line already stand in the tree the change began from? A copy leaves the original in place, so the moved exemption misses it (feature 258).
fn already_in_base(root: &Path, line: &str, base: &str) -> bool {
    let stripped = line.trim();
    stripped.chars().count() >= 12
        && Command::new("git")
            .arg("-C")
            .arg(root)
            .args(["grep", "-q", "-F", "--", stripped, base])
            .output()
            .is_ok_and(|o| o.status.success())
}

/// A capitalized word with a capitalized word on each side: the middle of a proper name (feature 267).
fn inside_a_name(text: &str, start: usize, end: usize) -> bool {
    if !text[start..end]
        .chars()
        .next()
        .is_some_and(char::is_uppercase)
    {
        return false;
    }
    let before = text[..start].strip_suffix(' ').map_or("", |h| {
        h.trim_end_matches(' ')
            .rsplit(' ')
            .next()
            .unwrap_or_default()
    });
    let after = text[end..].strip_prefix(' ').map_or("", |t| {
        t.trim_start_matches(' ')
            .split(' ')
            .next()
            .unwrap_or_default()
    });
    pattern(r"^[A-Z][\w'-]*$").is_match(before).unwrap_or(false)
        && pattern(r"^[A-Z][\w'-]*").is_match(after).unwrap_or(false)
}

/// Every British spelling this change wrote, as `path:line: word`.
fn findings(root: &Path) -> Vec<String> {
    let words = pattern(&format!(r"(?i)\b({})\b", british().join("|")));
    let base_text = git_text(root, &["merge-base", "HEAD", "origin/main"]);
    let base = if base_text.trim().is_empty() {
        "HEAD"
    } else {
        base_text.trim()
    };
    let (added, removed) = delta_lines(root, base);
    let mut out = Vec::new();
    let mut known: BTreeMap<String, bool> = BTreeMap::new();
    for (path, lines) in added.iter().filter(|(p, _)| !exempt_path(p)) {
        let data = std::fs::read(root.join(path)).unwrap_or_default();
        let body = String::from_utf8_lossy(&data)
            .replace("\r\n", "\n")
            .replace('\r', "\n");
        // asked only when a word is found: on a Unicode file this pattern is the scan's whole cost
        let spans = std::cell::OnceCell::new();
        let mut offsets = Vec::new();
        let mut at = 0;
        for text in body.split('\n') {
            offsets.push(at);
            at += text.len() + 1;
        }
        for (n, text) in lines.iter().filter(|(_, t)| !removed.contains(t.trim())) {
            for hit in words.find_iter(text).flatten() {
                let start = offsets.get(n.wrapping_sub(1)).copied().unwrap_or(0) + hit.start();
                let exempt: &Vec<(usize, usize)> = spans.get_or_init(|| exempt_spans(&body, path));
                if exempt.iter().any(|(a, b)| *a <= start && start < *b) {
                    continue;
                }
                let copied = *known
                    .entry(text.clone())
                    .or_insert_with(|| already_in_base(root, text, base));
                if !copied && !inside_a_name(text, hit.start(), hit.end()) {
                    out.push(format!(
                        "{path}:{n}: '{}' - CLAUDE.md: American spellings, project-wide",
                        hit.as_str()
                    ));
                }
            }
        }
    }
    out
}

/// The whole thing over a real git tree: a word this change wrote fires, a pre-existing line and a copied line do not.
fn selftest() -> Outcome {
    let root = super::scratch("house-style");
    let git = |args: &[&str]| {
        let _ = Command::new("git").arg("-C").arg(&root).args(args).output();
    };
    let write = |name: &str, text: &str| {
        let _ = std::fs::write(root.join(name), text);
    };
    git(&["init", "-q", "-b", "main"]);
    git(&["config", "user.email", "x@y"]);
    git(&["config", "user.name", "x"]);
    write("base.md", "the pre-existing colour stays\n");
    git(&["add", "-A"]);
    git(&["commit", "-qm", "base"]);
    git(&["update-ref", "refs/remotes/origin/main", "HEAD"]);
    write("new.md", "a fresh centre here\n");
    write(
        "base.md",
        "the pre-existing colour stays\nan added behaviour line\n",
    );
    write("copied.md", "the pre-existing colour stays\n");
    let found = findings(&root);
    let _ = std::fs::remove_dir_all(&root);
    let has = |s: &str| found.iter().any(|x| x.contains(s));
    let spans = exempt_spans(
        "a `colour` span\n<blockquote>\nthe colour there\n</blockquote>\nplain colour\n",
        "docs/a.md",
    );
    Outcome::selftest(
        has("new.md:1")
            && has("base.md:2")
            && !has("base.md:1")
            && !has("copied.md")
            && british().len() > 40
            && spans.len() == 2
            && exempt_path("CLAUDE.md")
            && exempt_path("specs/236-x/request.md")
            && !exempt_path("docs/a.md"),
        "check-house-style-delta selftest ok\n",
        format!("check-house-style-delta SELFTEST FAILED: {found:?}\n"),
    )
}

/// `l7r-gate check house-style-delta [ROOT]`.
pub(super) fn cli(args: &[String]) -> Outcome {
    if args.iter().any(|a| a == "--selftest") {
        return selftest();
    }
    let root = std::fs::canonicalize(
        args.first()
            .filter(|a| !a.starts_with("--"))
            .map_or(".", String::as_str),
    )
    .unwrap_or_default();
    let bad = findings(&root);
    if bad.is_empty() {
        return Outcome::out(String::new());
    }
    Outcome { stdout: format!("{}\n\nhouse style: {} British spelling(s) in what this change wrote. CLAUDE.md is project-wide - American spellings, hyphens only. A quotation of someone else's text keeps its own characters (GM 2026-09-06): put it inside 「」, “”, <q> or <blockquote>, or in a backtick span if the word is being NAMED rather than used.\n", bad.join("\n"), bad.len()), stderr: String::new(), code: 1 }
}

#[cfg(test)]
mod tests;
