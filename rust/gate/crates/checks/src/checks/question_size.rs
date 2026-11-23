//! A research question's prose stays under a size cap, on the questions a change touches (feature 250 D14; prose only since feature 292; feature 449 T065, from `check-question-size.py`). The cap is the record's 90th percentile of
//! question plus notes; each question over it is split along its topics by the session that works its page. A run is recorded by `usage_log` under `USAGE_LOG_TOOL`.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use super::moves::moved_only;
use super::{git_text, Outcome};

pub(super) const USAGE_LOG_TOOL: &str = "check-question-size";
const CAP: usize = 20_000;
const RECORD: &str = "research";
const COMPANIONS: [&str; 2] = [".notes.html", ".originals.html"];

fn with_commas(n: usize) -> String {
    let digits = n.to_string();
    digits
        .chars()
        .enumerate()
        .fold(String::new(), |mut out, (at, c)| {
            if at > 0 && (digits.len() - at) % 3 == 0 {
                out.push(',');
            }
            out.push(c);
            out
        })
}

fn is_question(rel: &str) -> bool {
    let (dirs, name) = rel.rsplit_once('/').unwrap_or(("", rel));
    let pattern = l7r_shared::regex::build(r"^[0-9]{4}-[^.]+(?:\.drawing)?\.html$").unwrap();
    pattern.is_match(name).unwrap_or(false) && dirs.split('/').any(|p| p == "questions")
}

/// A question's notes or originals file names the question it belongs to; a question is itself.
fn question_of(rel: &str) -> String {
    COMPANIONS
        .iter()
        .find_map(|s| rel.strip_suffix(s).map(|head| format!("{head}.html")))
        .unwrap_or_else(|| rel.to_owned())
}

/// The question's prose in bytes: a money mark is markup around words already counted (feature 413), and an item tag is data no
/// reader of the page reads, its label and its pop-up bullet (feature 451 T192: tagging 0196 put it over the cap by 1,838 bytes).
fn size(path: &Path) -> usize {
    let text = std::fs::read_to_string(path).unwrap_or_default();
    let money = l7r_shared::regex::build(r#"(?s)<span class="money"[^>]*>(.*?)</span>"#).unwrap();
    l7r_gate_research::record::items::strip(&money.replace_all(&text, "$1")).len()
}

fn merge_base(root: &Path) -> String {
    git_text(root, &["merge-base", "HEAD", "origin/main"])
        .trim()
        .to_owned()
}

#[cfg(test)]
fn changed(root: &Path) -> Vec<String> {
    changed_from(root, &merge_base(root))
}

fn changed_from(root: &Path, base: &str) -> Vec<String> {
    let against = if base.is_empty() { "HEAD" } else { base };
    let mut names = git_text(root, &["diff", "--name-only", against, "--", RECORD]);
    names += &git_text(
        root,
        &["ls-files", "--others", "--exclude-standard", "--", RECORD],
    );
    let all: Vec<String> = names.split_whitespace().map(str::to_owned).collect();
    let moved = moved_only(root, base, &all);
    let wanted: BTreeSet<String> = all
        .iter()
        .filter(|n| !moved.contains(*n))
        .map(|n| question_of(n))
        .filter(|q| is_question(q) && root.join(q).is_file())
        .collect();
    wanted.into_iter().collect()
}

fn every(root: &Path) -> Vec<String> {
    let mut found: Vec<PathBuf> = std::fs::read_dir(root.join(RECORD).join("questions"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .collect();
    found.sort();
    found
        .iter()
        .map(|p| {
            format!(
                "{RECORD}/questions/{}",
                p.file_name().unwrap_or_default().to_string_lossy()
            )
        })
        .filter(|q| is_question(q))
        .collect()
}

fn report(root: &Path) -> Outcome {
    let limits = limits::read(root, CAP).unwrap_or_default();
    let mut over: Vec<(usize, String)> = every(root)
        .into_iter()
        .map(|q| (size(&root.join(&q)), q))
        .filter(|(n, q)| *n > limits.get(q).copied().unwrap_or(CAP))
        .collect();
    over.sort_by(|a, b| b.cmp(a));
    let mut out = String::new();
    for (n, q) in &over {
        let _ = writeln!(out, "{:>7}  {q}", with_commas(*n));
    }
    let _ = writeln!(
        out,
        "{} question(s) over {} bytes of prose",
        over.len(),
        with_commas(CAP)
    );
    Outcome::out(out)
}

const SPLIT: &str = "split it along its topics (a finding stays with its decision; each part its own question and heading; the joins point, they do not restate). Why and how: docs/research-record-rules.md, 'A question has a size'";

/// 451 T184: a size edit of `q` (the page over its limit at `base`, or the words it removed putting it back over) that
/// drops a claim-bearing token the page and the pages its split pointers (`<a class="moved">`) name no longer hold.
fn size_edit_refusal(root: &Path, base: &str, q: &str, limit: usize) -> Option<String> {
    let old = git_text(root, &["show", &format!("{base}:{q}")]);
    let new = std::fs::read_to_string(root.join(q)).unwrap_or_default();
    if old.is_empty() || old == new {
        return None;
    }
    let removed = size_edit::removed_bytes(&old, &new);
    if !size_edit::is_size_edit(old.len(), new.len(), removed, limit) {
        return None;
    }
    // Only a split's pointer, T185's `<a class="moved" href=...>`, carries a token: the triage (owed's `triage/change.rs`, POINTER)
    // follows no other link, so a section kept behind a plain link would pass here and be owed as removed there (gap audit item 4).
    let link = l7r_shared::regex::build(
        r#"<a\s+class="moved"\s+href="(\d{4}-[a-z0-9-]+(?:\.drawing)?\.html)(?:#[^"]*)?""#,
    )
    .unwrap();
    let dir = root.join(RECORD).join("questions");
    let linked: Vec<String> = link
        .captures_iter(&new)
        .map_while(Result::ok)
        .filter_map(|c| c.get(1).map(|m| m.as_str().to_owned()))
        .filter_map(|name| std::fs::read_to_string(dir.join(name)).ok())
        .collect();
    let lost = size_edit::lost(&old, &new, &linked);
    if lost.is_empty() {
        return None;
    }
    let mut out = format!("question-size: {q} is a SIZE EDIT ({} bytes at the base, {} now, {removed} removed, against its {} limit) and it drops claim-bearing words the page no longer holds:\n", with_commas(old.len()), with_commas(new.len()), with_commas(limit));
    for l in &lost {
        let _ = writeln!(out, "  [{}] {} `{}`", l.block, l.kind.word(), l.token);
    }
    let _ = writeln!(out, "  No edit to fit the cap may change a claim (the GM 2026-11-23). Put the words back and split the page instead: a new question (`make reserve KIND=question KEY=\"<heading>\"`) takes a section whole, and the source page keeps a sentence where the section was, pointing to it in the split's form `<a class=\"moved\" href=\"NNNN-<slug>.html\">` - a token standing on that page counts as kept; a plain link does not, as the pop-up and claims triage follow only that form. A page that is one indivisible topic: a limit of its own in research/size-limits.json, with the size-exception check's INDIVISIBLE verdict (.claude/agents/size-exception.md). A correction, not a fit to the cap: SIZE_EDIT_OK=\"<why>\".");
    Some(out)
}

/// `l7r-gate check question-size [--report | --all] [--base <rev>]`: the questions a change touched (`make quick`), each held
/// to its limit and, if the change is a size edit, to keeping every claim (451 T184); or with `--all` every question of the
/// record held to its limit (`make static`, 449 T385: 0059 and 0009 stood over the cap while no change touched them).
/// `--base` names the base a delta run diffs against, the merge base with `origin/main` by default.
pub(super) fn cli(args: &[String], root: &Path) -> Outcome {
    cli_with(args, root, std::env::var("SIZE_EDIT_OK").ok().as_deref())
}

fn cli_with(args: &[String], root: &Path, escape: Option<&str>) -> Outcome {
    if args.iter().any(|a| a == "--report") {
        return report(root);
    }
    let limits = match limits::read(root, CAP) {
        Ok(l) => l,
        Err(bad) => return Outcome::refuse(bad.join("\n") + "\n"),
    };
    let limit = |q: &str| limits.get(q).copied().unwrap_or(CAP);
    let all = args.iter().any(|a| a == "--all");
    let base = args
        .iter()
        .position(|a| a == "--base")
        .and_then(|i| args.get(i + 1))
        .map_or_else(
            || merge_base(root),
            |b| git_text(root, &["rev-parse", b]).trim().to_owned(),
        );
    let pages = if all {
        every(root)
    } else {
        changed_from(root, &base)
    };
    let mut err = String::new();
    for q in &pages {
        let n = size(&root.join(q));
        if n > limit(q) {
            let _ = writeln!(
                err,
                "question-size: {q} is {} bytes of prose, over the {} {} - {SPLIT}.",
                with_commas(n),
                with_commas(limit(q)),
                if limit(q) == CAP {
                    "cap"
                } else {
                    "limit recorded for it"
                }
            );
        }
    }
    let mut note = String::new();
    if !all {
        for q in &pages {
            if let Some(refusal) = size_edit_refusal(root, &base, q, limit(q)) {
                match escape {
                    Some(why) if l7r_shared::escape::enough(why) => {
                        let _ = writeln!(note, "question-size: {q}: a size edit's claim check stood aside - SIZE_EDIT_OK: {why}");
                    }
                    _ => err.push_str(&refusal),
                }
            }
        }
    }
    if err.is_empty() {
        return Outcome::out(note);
    }
    if all {
        let _ = writeln!(err, "question-size: every question is held to its limit, whoever touched it last - `make question-sizes` lists them largest first; split each by page session (make page-session), never cut a claim to fit.");
    }
    Outcome::refuse(err)
}

mod limits;
mod size_edit;
#[cfg(test)]
mod tests;
