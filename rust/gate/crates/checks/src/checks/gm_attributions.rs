//! A ruling attributed to the GM points at his recorded words (feature 451 T233).
//!
//! WHY: page 0006's drawing page carried "the GM's ruling, 2026-07: dry plots are rectangles laid out against the canal", and the
//! hamlet's dry-field stage enforced it. The GM, 2026-11-24 (`docs/gm-rulings.md`, "NOT a ruling: dry plots as rectangles against the
//! canal"): *"I never made a ruling that dry plots are rectangles laid out against the canal. That was never at any point something
//! that I said was true about these maps. That is what a session told me the research showed."* The audit of that day found 74 of
//! 180 such comments in `research/questions` with no recorded words behind them, most of them a session's sentence or a retired rule
//! file's "(GM date)" tag reworded into a ruling.
//!
//! What is checked: an HTML comment of a research page (`research/questions/*.html`) and a CANON claim line (`<label> - CANON...`, in
//! the Rust under `rust/` the claims walk reads, `rust/parked` included, and in the two procedure docs) that names a ruling of the
//! GM's ([`NAMES`]) must name, in the same comment or line, a record that holds his words and exists: `specs/<NNN-slug>/request.md`
//! (or the `gm-request.md` gm-assistant opens for him), `docs/gm-rulings.md`, `specs/<NNN-slug>/gm-review.jsonl` (a
//! `make gm-reviewed` row, which carries `gm_words`), or a feature's dated rulings file, `specs/<NNN-slug>/rulings-YYYY-MM-DD.md`
//! (451 T265: the two there are, 269's and 280's, are headed "verbatim" and hold his rulings as block quotations, the form of a
//! `request.md`). NOT a record: a `tasks.md`, an `audit.md` or a commit message that quotes him. Each is a session's file that
//! quotes a sentence of his second-hand, beside the session's own sentences and for the session's purpose, and since the words are
//! not checked (below) a pointer at one would pass on a session's sentence, the failure this check was built on. 451 T251's brook
//! claim is the instance: his words of 2026-08-26, quoted in feature 133's `tasks.md`, were of a marsh edge and never of a brook.
//! A comment whose words stand only in such a file names the file in plain words, without calling them a ruling, as 451 T250's do.
//! Whether the record named really holds those words is not checked: the
//! comments paraphrase rather than quote, so a mechanical match of words would refuse most correct pointers; a pointer to the wrong
//! record passes, and is the reviewers' to catch (an accepted limitation, the builder's choice under the record's "where the record
//! is silent, take the algorithmically easier route", 451 T233's plan section).
//!
//! THE BASELINE (`dev/gm-attribution-baseline.jsonl`): every attribution with no pointer when the check landed, keyed by its file
//! and its whitespace-normalized text (not its line, so an edit elsewhere on the page keeps it listed). A listed one is not refused;
//! one not listed is. The baseline only shrinks: an entry the merge base's copy lacks is refused, `--prune` drops the entries no
//! longer found and adds none, and `--seed` writes the list only where there is none. Fixing a listed comment is page work, which
//! waits for the research switch (`dev/switches.json`); editing one changes its text, so the edited comment owes its pointer.
//! A run is recorded by `usage_log` under `USAGE_LOG_TOOL`.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Value};

use super::{git_text, Outcome};

pub(super) const USAGE_LOG_TOOL: &str = "check-gm-attributions";
const BASELINE: &str = "dev/gm-attribution-baseline.jsonl";
const PAGES: &str = "research/questions";
const PROCEDURES: [&str; 2] = ["docs/buildings.md", "docs/building-programs.md"];
/// The trees under `rust/` that hold no research claim: the tooling, whose tests write attributions as fixtures.
const NOT_CLAIMS: [&str; 5] = ["gate", "guard", "browser", "embed", "target"];
const FIX: &str = "name the record that holds his words - specs/<NNN-slug>/request.md, docs/gm-rulings.md, specs/<NNN-slug>/gm-review.jsonl (a make gm-reviewed row) or a dated specs/<NNN-slug>/rulings-YYYY-MM-DD.md; with none, it is not his ruling: say whose it is (docs/gm-rulings.md, 'NOT a ruling', the GM 2026-11-24)";

fn compiled(pattern: &str) -> Regex {
    l7r_shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// The words that name a ruling of the GM's: the four of the task ("the GM's ruling|catch|word|decision", singular or plural), "the
/// GM ruled", "GM <date>" (with or without a comma), the audit's near-twins ("the GM's rule|doctrine|correction"), and the same
/// nouns after "a GM" (451 T265: "a GM ruling of 2026-09-20" stood unread on `docs/building-programs.md`'s dedication knob).
pub(super) static NAMES: LazyLock<Regex> = LazyLock::new(|| {
    compiled(
        r"(?i)\b(?:the GM's|a GM) (?:ruling|catch|word|decision|rule|doctrine|correction)s?\b|\bthe GM ruled\b|\bGM,? \d{4}-\d{2}",
    )
});
static POINTER: LazyLock<Regex> = LazyLock::new(|| {
    compiled(
        r"specs/[A-Za-z0-9._-]+/(?:gm-)?request\.md|docs/gm-rulings\.md|specs/[A-Za-z0-9._-]+/gm-review\.jsonl|specs/[A-Za-z0-9._-]+/rulings-\d{4}-\d{2}-\d{2}\.md",
    )
});
static COMMENT: LazyLock<Regex> = LazyLock::new(|| compiled(r"(?s)<!--.*?-->"));
static CANON: LazyLock<Regex> = LazyLock::new(|| compiled(r"\s-\s+CANON\b"));

/// One attribution with no record behind it.
#[derive(Debug)]
struct Found {
    file: String,
    line: usize,
    kind: &'static str,
    says: String,
    key: String,
    excerpt: String,
    /// A pointer it names that does not exist.
    missing: Option<String>,
}

fn normalized(text: &str) -> String {
    text.split_whitespace().collect::<Vec<_>>().join(" ")
}

/// Its text where it stands: `None` when it names no ruling or names a record that exists, else what it said and the pointer
/// that does not resolve, if any.
fn unbacked(root: &Path, text: &str) -> Option<(String, Option<String>)> {
    let says = NAMES.find(text).ok().flatten()?.as_str().to_owned();
    let pointers: Vec<String> = POINTER
        .find_iter(text)
        .map_while(Result::ok)
        .map(|m| m.as_str().to_owned())
        .collect();
    if pointers.iter().any(|p| root.join(p).is_file()) {
        return None;
    }
    Some((says, pointers.into_iter().next()))
}

fn found(root: &Path, file: &str, line: usize, kind: &'static str, text: &str) -> Option<Found> {
    let (says, missing) = unbacked(root, text)?;
    let flat = normalized(text);
    Some(Found {
        file: file.to_owned(),
        line,
        kind,
        says,
        key: l7r_shared::sha256::hex(flat.as_bytes())[..16].to_owned(),
        excerpt: flat.chars().take(120).collect(),
        missing,
    })
}

fn sorted_dir(dir: &Path) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .collect();
    out.sort();
    out
}

fn page_findings(root: &Path, out: &mut Vec<Found>) {
    for path in sorted_dir(&root.join(PAGES)) {
        let name = path.file_name().unwrap_or_default().to_string_lossy();
        if !name.ends_with(".html") {
            continue;
        }
        let file = format!("{PAGES}/{name}");
        let text = std::fs::read_to_string(&path).unwrap_or_default();
        for m in COMMENT.find_iter(&text).map_while(Result::ok) {
            let line = 1 + text[..m.start()].matches('\n').count();
            out.extend(found(root, &file, line, "comment", m.as_str()));
        }
    }
}

/// Every `.rs` under `dir`, its path relative to `root`.
fn rust_files(root: &Path, dir: &Path, out: &mut Vec<String>) {
    for path in sorted_dir(dir) {
        if path.is_dir() {
            rust_files(root, &path, out);
        } else if path.extension().is_some_and(|e| e == "rs") {
            out.push(
                path.strip_prefix(root)
                    .unwrap_or(&path)
                    .to_string_lossy()
                    .into_owned(),
            );
        }
    }
}

fn claim_findings(root: &Path, out: &mut Vec<Found>) {
    let mut files = Vec::new();
    for tree in sorted_dir(&root.join("rust")) {
        let name = tree
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned();
        if tree.is_dir() && !NOT_CLAIMS.contains(&name.as_str()) {
            rust_files(root, &tree, &mut files);
        }
    }
    files.extend(PROCEDURES.iter().map(|d| (*d).to_owned()));
    for file in files {
        let text = std::fs::read_to_string(root.join(&file)).unwrap_or_default();
        for (at, line) in text.lines().enumerate() {
            if CANON.is_match(line).unwrap_or(false) {
                out.extend(found(root, &file, at + 1, "claim", line));
            }
        }
    }
}

/// Every attribution in the tree with no record behind it, pages first.
fn findings(root: &Path) -> Vec<Found> {
    let mut out = Vec::new();
    page_findings(root, &mut out);
    claim_findings(root, &mut out);
    out
}

/// A baseline's rows and their `(file, key)`s, in its order.
fn rows(text: &str) -> Vec<(Value, (String, String))> {
    text.lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .map(|v| {
            let id = (
                v["file"].as_str().unwrap_or("").to_owned(),
                v["key"].as_str().unwrap_or("").to_owned(),
            );
            (v, id)
        })
        .collect()
}

fn row(f: &Found) -> String {
    json!({"file": f.file, "key": f.key, "kind": f.kind, "says": f.says, "excerpt": f.excerpt})
        .to_string()
        + "\n"
}

/// The merge base's baseline, where the base has one; at a hand-in, the baseline of the base it names (`l7r_gate_core::delta_base`,
/// 461 T37).
fn base_ids(root: &Path) -> Option<BTreeSet<(String, String)>> {
    let base = l7r_gate_core::delta_base::named(root)
        .unwrap_or_else(|| git_text(root, &["merge-base", "HEAD", "origin/main"]));
    let spec = format!("{}:{BASELINE}", base.trim());
    if base.trim().is_empty() || git_text(root, &["cat-file", "-t", &spec]).trim() != "blob" {
        return None;
    }
    Some(
        rows(&git_text(root, &["show", &spec]))
            .into_iter()
            .map(|(_, id)| id)
            .collect(),
    )
}

fn refusals(root: &Path, listed: &[(Value, (String, String))], found: &[Found]) -> String {
    let ids: BTreeSet<(String, String)> = listed.iter().map(|(_, id)| id.clone()).collect();
    let mut out = String::new();
    for f in found
        .iter()
        .filter(|f| !ids.contains(&(f.file.clone(), f.key.clone())))
    {
        let pointer = f
            .missing
            .as_ref()
            .map_or_else(String::new, |p| format!(" ({p} does not exist)"));
        let _ = writeln!(out, "check-gm-attributions: {}:{}: a {} names a ruling of the GM's (\"{}\") with no pointer to his recorded words{pointer} - {FIX}", f.file, f.line, f.kind, f.says);
    }
    let now: BTreeSet<(String, String)> = found
        .iter()
        .map(|f| (f.file.clone(), f.key.clone()))
        .collect();
    for (file, key) in ids.difference(&now) {
        let _ = writeln!(out, "check-gm-attributions: {BASELINE} lists {file} {key}, no longer found (fixed or edited) - drop it: scripts/gates/l7r-gate.sh check gm-attributions --prune");
    }
    if let Some(base) = base_ids(root) {
        for (file, key) in ids.difference(&base) {
            let _ = writeln!(out, "check-gm-attributions: {BASELINE} gained {file} {key}, which the merge base's copy does not list - the baseline only shrinks: take the entry out and give the attribution its pointer ({FIX})");
        }
    }
    out
}

fn write(root: &Path, text: &str) -> Outcome {
    match std::fs::write(root.join(BASELINE), text) {
        Ok(()) => Outcome::out(String::new()),
        Err(e) => Outcome::refuse(format!(
            "check-gm-attributions: cannot write {BASELINE}: {e}\n"
        )),
    }
}

/// `check gm-attributions [--prune | --seed] [ROOT]`.
pub(super) fn cli(args: &[String]) -> Outcome {
    let (mode, rest) = match args.first().map(String::as_str) {
        Some(m @ ("--prune" | "--seed")) => (m, &args[1..]),
        _ => ("", args),
    };
    if rest.len() > 1 || rest.first().is_some_and(|a| a.starts_with("--")) {
        return Outcome::usage("usage: l7r-gate check gm-attributions [--prune | --seed] [ROOT]\n");
    }
    let root = PathBuf::from(rest.first().map_or(".", String::as_str));
    let have = std::fs::read_to_string(root.join(BASELINE)).ok();
    let found = findings(&root);
    match (mode, have) {
        ("--seed", Some(_)) => Outcome::refuse(format!("check-gm-attributions: {BASELINE} exists and only shrinks - --prune drops the entries no longer found\n")),
        ("--seed", None) => write(&root, &found.iter().map(row).collect::<String>()),
        ("--prune", None) => Outcome::out(String::new()),
        ("--prune", Some(have)) => {
            let now: BTreeSet<(String, String)> = found.iter().map(|f| (f.file.clone(), f.key.clone())).collect();
            let kept: String = rows(&have)
                .into_iter()
                .filter(|(_, id)| now.contains(id))
                .map(|(v, _)| v.to_string() + "\n")
                .collect();
            write(&root, &kept)
        }
        (_, have) => {
            let said = refusals(&root, &rows(&have.unwrap_or_default()), &found);
            if said.is_empty() {
                Outcome::out(String::new())
            } else {
                Outcome::refuse(said)
            }
        }
    }
}

#[cfg(test)]
mod tests;
