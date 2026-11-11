//! Which record checks this delta owes, and which are still unanswered (from `record_owed.py`, feature 449 T87): the one scripted answer, read against the merge base and the working tree or between two revisions. `make record-owed`, the push's record gate and the check bundles ask it; `answers.rs` is its record of what was answered.

mod answers;

use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::{split, SPACE_CLASS};
use serde_json::{json, Value};

pub(crate) use answers::{
    answer, answered, file_outside, keep_reading, read_answer, reply_checks, reply_of, settle,
    store, unanswered, write_answer, Named, FIXED,
};

use super::args::{parse, Parsed, Spec};
use super::modals;
use super::repo::{cat_blobs, fail, git, python, read_text, tree_of, Fail};
use super::translation;
use super::units::{
    self, digest, question, re, stem_of, Keyed, Record, Unit, QUESTIONS, SOURCE_DIRS,
};
use crate::Reply;

static SOURCE_FILE: LazyLock<Regex> = LazyLock::new(|| re(r"^\d+-([a-z0-9-]+)\.html$"));
static CLASS_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"^class (\w+)\("));

/// The families of owed units, each computed by its own reader.
pub(crate) const FAMILIES: [&str; 4] = ["record", "translation", "entry-drift", "modal"];

const ENTRY_OWED: &str = r"import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1] + '/scripts/record')
import entry_owed
print(json.dumps(entry_owed.owed(Path(sys.argv[2]))[1]))";

fn usage(line: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("{line}\n"),
        code: 2,
    }
}

/// The merge base of HEAD with origin/main, else HEAD.
pub(crate) fn merge_base(root: &Path) -> String {
    if !git(root, &["rev-parse", "--verify", "-q", "origin/main"])
        .trim()
        .is_empty()
    {
        return git(root, &["merge-base", "HEAD", "origin/main"])
            .trim()
            .to_owned();
    }
    git(root, &["rev-parse", "--verify", "-q", "HEAD"])
        .trim()
        .to_owned()
}

/// The write-ups that differ between `base` and `head` (None: the working tree, untracked files included).
fn changed_sources(root: &Path, base: &str, head: Option<&str>) -> HashSet<String> {
    let mut args = vec!["diff", "--name-only", base];
    args.extend(head);
    args.push("--");
    args.extend(SOURCE_DIRS);
    let mut names: Vec<String> = split(&git(root, &args))
        .into_iter()
        .map(str::to_owned)
        .collect();
    if head.is_none() {
        let mut others = vec!["ls-files", "--others", "--exclude-standard", "--"];
        others.extend(SOURCE_DIRS);
        names.extend(split(&git(root, &others)).into_iter().map(str::to_owned));
    }
    names
        .iter()
        .filter_map(|n| n.rsplit_once('/').map(|p| p.1.to_owned()))
        .collect()
}

fn html_files(dir: &Path) -> Vec<String> {
    std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| Path::new(n).extension().is_some_and(|x| x == "html"))
        .collect()
}

/// The record at `rev` (None: the working tree), read with one listing and one batch; of the write-ups, only those named in `sources` (None: all).
pub(crate) fn read_at(
    root: &Path,
    rev: Option<&str>,
    sources: Option<&HashSet<String>>,
) -> Result<Record, Fail> {
    let (mut files, mut write_ups) = (Keyed::default(), Vec::new());
    let wanted = |name: &str| sources.is_none_or(|s| s.contains(name));
    if let Some(rev) = rev {
        let mut args = vec!["ls-tree", "-r", "--name-only", rev, "--", QUESTIONS];
        args.extend(SOURCE_DIRS);
        let names: Vec<String> = git(root, &args)
            .split('\n')
            .filter(|n| {
                Path::new(n).extension().is_some_and(|x| x == "html")
                    && (!is_write_up(n) || wanted(n.rsplit_once('/').map_or("", |p| p.1)))
            })
            .map(str::to_owned)
            .collect();
        let objects: Vec<String> = names.iter().map(|n| format!("{rev}:{n}")).collect();
        for (name, text) in names.iter().zip(cat_blobs(root, &objects)) {
            let base = name
                .rsplit_once('/')
                .map_or(name.as_str(), |p| p.1)
                .to_owned();
            if name.starts_with(&format!("{QUESTIONS}/")) {
                files.insert(base, text);
            } else if is_write_up(name) {
                write_ups.push((base, text));
            }
        }
    } else {
        for name in html_files(&root.join(QUESTIONS)) {
            let text = read_text(&root.join(QUESTIONS).join(&name))?;
            files.insert(name, text);
        }
        for d in SOURCE_DIRS {
            for name in html_files(&root.join(d)) {
                if wanted(&name) {
                    let text = read_text(&root.join(d).join(&name))?;
                    write_ups.push((name, text));
                }
            }
        }
    }
    let mut keyed = Keyed::default();
    for (name, text) in write_ups {
        if let Ok(Some(c)) = SOURCE_FILE.captures(&name) {
            keyed.insert(c[1].to_owned(), text);
        }
    }
    Ok(Record::of(&files, &keyed))
}

fn is_write_up(name: &str) -> bool {
    SOURCE_DIRS
        .iter()
        .any(|d| name.starts_with(&format!("{d}/")))
}

fn translation_units(root: &Path, now: &Record) -> Result<Vec<Unit>, Fail> {
    let mut found: Keyed<Unit> = Keyed::default();
    for row in translation::owed(root)? {
        let file = row
            .0
            .rsplit_once('/')
            .map_or(row.0.as_str(), |p| p.1)
            .replace(".notes.html", ".html");
        let Some((stem, _)) = stem_of(&file) else {
            continue;
        };
        let note = if row.1 == "a term's gloss" {
            "gloss"
        } else {
            row.1.as_str()
        };
        let slug = format!("translation-check:{stem}#{note}");
        let text = now
            .notes
            .get(&stem)
            .and_then(|n| n.get(&row.1))
            .map_or("", String::as_str);
        let fp = if note == "gloss" {
            let mut parts = vec![text];
            if let Some(p) = now.pages.get(&stem) {
                parts.extend(p.blocks.iter().map(|b| b.words.as_str()));
            }
            digest(&parts)
        } else {
            digest(&[text])
        };
        found.insert(
            slug.clone(),
            Unit {
                slug,
                occasion: "a translated quotation is new or changed".to_owned(),
                fingerprint: fp,
                reading: String::new(),
            },
        );
    }
    Ok(found.iter().map(|(_, u)| u.clone()).collect())
}

/// The base `entry_owed` diffs against (`entry_owed.base_of`).
pub(super) fn entry_base(root: &Path) -> String {
    let head = git(root, &["rev-parse", "--verify", "-q", "HEAD"])
        .trim()
        .to_owned();
    let origin = !head.is_empty()
        && !git(root, &["rev-parse", "--verify", "-q", "origin/main"])
            .trim()
            .is_empty();
    let mb = if origin {
        git(root, &["merge-base", "HEAD", "origin/main"])
            .trim()
            .to_owned()
    } else {
        String::new()
    };
    if mb.is_empty() {
        head
    } else {
        mb
    }
}

/// Whether `entry_owed` must run for this delta (the T065 clause, `ask:449-T87-entry-owed`): the family is asked, and a question page changed, or the engine it imports is not here (the crash the Python had then).
fn entry_drift_owed(root: &Path) -> bool {
    let base = entry_base(root);
    if base.is_empty() {
        return false;
    }
    !root
        .join("l7r/diagram/interactive/classes/__init__.py")
        .is_file()
        || git(root, &["diff", "--name-only", &base, "--", "research/"])
            .lines()
            .any(|n| {
                n.strip_prefix("research/questions/")
                    .is_some_and(|f| stem_of(f).is_some())
            })
}

fn entry_units(root: &Path, now: &Record) -> Result<Vec<Unit>, Fail> {
    let tree = tree_of(root);
    let (tree, top) = (tree.to_string_lossy(), root.to_string_lossy());
    let said = python(ENTRY_OWED, &[&tree, &top], "")?;
    let lines: Vec<String> = serde_json::from_str(&said).map_err(fail)?;
    let about = modals::about_keys(root)?;
    let mut out = Vec::new();
    for line in lines {
        let (key, rest) = line.split_once(" - ").unwrap_or((line.as_str(), ""));
        if about.contains(key) {
            continue;
        }
        let hits = split(rest.split(" - ").next().unwrap_or(""));
        let mut parts: Vec<&str> = vec![key];
        for h in &hits {
            if let Some((s, _)) = stem_of(h) {
                if let Some(p) = now.pages.get(&s) {
                    parts.extend(
                        p.blocks
                            .iter()
                            .filter(|b| !b.intro)
                            .map(|b| b.words.as_str()),
                    );
                }
            }
        }
        out.push(Unit {
            slug: format!("entry-drift:{key}"),
            occasion: format!("its section's findings moved ({})", hits.join(" ")),
            fingerprint: digest(&parts),
            reading: String::new(),
        });
    }
    Ok(out)
}

/// Every owed unit, against the merge base and the working tree, or between two revisions; `families` and, for the pop-ups, `uid` scope it.
pub(crate) fn units(
    root: &Path,
    base: Option<&str>,
    head: Option<&str>,
    families: &[&str],
    uid: &str,
) -> Result<Vec<Unit>, Fail> {
    let base = base
        .filter(|b| !b.is_empty())
        .map_or_else(|| merge_base(root), str::to_owned);
    let mut out: Vec<Unit> = Vec::new();
    let has = |f: &str| families.contains(&f);
    let touched = if base.is_empty() {
        None
    } else {
        Some(changed_sources(root, &base, head))
    };
    let entry = head.is_none() && has("entry-drift") && entry_drift_owed(root);
    let now = if has("record") || (head.is_none() && has("translation")) || entry {
        Some(read_at(root, head, touched.as_ref())?)
    } else {
        None
    };
    if let (true, Some(current)) = (has("record"), now.as_ref()) {
        let was = if base.is_empty() {
            Record::default()
        } else {
            read_at(root, Some(&base), touched.as_ref())?
        };
        out = units::owed(current, &was);
    }
    if head.is_none() {
        if let (true, Some(now)) = (has("translation"), now.as_ref()) {
            out.extend(translation_units(root, now)?);
        }
        if let (true, Some(now)) = (entry, now.as_ref()) {
            out.extend(entry_units(root, now)?);
        }
        if has("modal") {
            out.extend(modals::owed(root, &base, uid)?.into_iter().map(
                |(slug, occasion, fingerprint)| Unit {
                    slug,
                    occasion,
                    fingerprint,
                    reading: String::new(),
                },
            ));
        }
    }
    out.sort_by(|a, b| a.slug.cmp(&b.slug));
    Ok(out)
}

/// The modal class(es) whose `key` is this one (the map's Well and the sheet's), as `make check-bundle KIND=` takes them.
fn modal_classes(key: &str, base: &Path) -> Result<Vec<String>, Fail> {
    let keyed = re(&format!(
        "^[{SPACE_CLASS}]+key = ['\"]{}['\"][{SPACE_CLASS}]*$",
        fancy_regex::escape(key)
    ));
    let mut paths: Vec<PathBuf> = Vec::new();
    for sub in ["classes", "compound_kinds"] {
        let dir = base.join(sub);
        paths.extend(
            std::fs::read_dir(&dir)
                .into_iter()
                .flatten()
                .flatten()
                .map(|e| e.path())
                .filter(|p| p.extension().is_some_and(|x| x == "py")),
        );
    }
    paths.sort();
    let mut hits: Vec<(String, String)> = Vec::new();
    for path in &paths {
        let text = read_text(path)?;
        let stem = path
            .file_stem()
            .map_or_else(String::new, |s| s.to_string_lossy().into_owned());
        let mut cls = String::new();
        for line in super::py_lines(&text) {
            if let Ok(Some(c)) = CLASS_LINE.captures(line) {
                cls = c[1].to_owned();
            } else if !cls.is_empty() && keyed.is_match(line).unwrap_or(false) {
                hits.push((stem.clone(), cls.clone()));
            }
        }
    }
    let many = hits.len() > 1;
    Ok(hits
        .into_iter()
        .map(|(m, c)| if many { format!("{m}.{c}") } else { c })
        .collect())
}

/// Owed only by a moved page and not yet marked touched at its fingerprint.
fn triage_first(u: &Unit, triaged: &HashMap<String, String>) -> bool {
    u.occasion.starts_with("a page its ") && triaged.get(&u.slug) != Some(&u.fingerprint)
}

/// What builds the bundle for a unit.
fn command(
    u: &Unit,
    now: &Record,
    triaged: &HashMap<String, String>,
    kinds: &Path,
) -> Result<String, Fail> {
    let (q, check) = (question(u.subject()), u.check());
    if check == "source-applicability" {
        return Ok(format!("make check-bundle KEY={}", u.subject()));
    }
    if check == "source-reader" {
        let (stem, note) = u.subject().split_once('#').unwrap_or((u.subject(), ""));
        let mut keys: Vec<String> = Vec::new();
        for k in now
            .cites
            .get(stem)
            .and_then(|c| c.get(note))
            .into_iter()
            .flatten()
        {
            if !keys.contains(k) {
                keys.push(k.clone());
            }
        }
        if keys.is_empty() {
            keys.push("<the note's key>".to_owned());
        }
        return Ok(format!(
            "{}  then  make record-checked CHECK=source-reader Q={q} NOTES={note}",
            keys.iter()
                .map(|k| format!("make check-bundle KEY={k} WHOLE=1"))
                .collect::<Vec<_>>()
                .join(" ; ")
        ));
    }
    if check.starts_with("modal-") && triage_first(u, triaged) {
        return Ok("make modal-triage  then  make modal-triaged BUNDLE=<its bundle> REPLY=<the reply>  (a kind it names is then bundled as below)".to_owned());
    }
    if check.starts_with("modal-") {
        let agent = if check == "modal-form" || check == "modal-depiction" {
            check
        } else {
            "modal-research"
        };
        return Ok(format!(
            "make modal-bundle KIND=\"{}\" FOR={agent}  then  make record-checked CHECK={check} BUNDLE=<its bundle> RESULT=...",
            u.subject()
        ));
    }
    if check == "entry-drift" {
        static FOUND: LazyLock<Regex> = LazyLock::new(|| re(r"\b(\d{4})-"));
        let qq = FOUND
            .captures(&u.occasion)
            .ok()
            .flatten()
            .map_or_else(|| "<its section>".to_owned(), |c| c[1].to_owned());
        let mut classes = modal_classes(u.subject(), kinds)?;
        if classes.is_empty() {
            classes.push(format!("<the class of {}>", u.subject()));
        }
        return Ok(format!(
            "{}  then  make record-checked CHECK=entry-drift KIND=\"{}\" BUNDLE=<its bundle> RESULT=<verdict>",
            classes.iter().map(|k| format!("make check-bundle Q={qq} FOR=entry-drift KIND=\"{k}\"")).collect::<Vec<_>>().join(" ; "),
            u.subject()
        ));
    }
    Ok(format!("make check-bundle Q={q} FOR={check}"))
}

/// {pop-up agent: [kinds]} for each agent two or more unanswered pop-ups owe; a pop-up owed only by a moved page goes to `make modal-triage` first.
fn modal_batches(
    rows: &[Unit],
    answered_slugs: &HashSet<String>,
    triaged: &HashMap<String, String>,
) -> Vec<(String, Vec<String>)> {
    let mut out: Vec<(String, Vec<String>)> = Vec::new();
    for u in rows {
        if answered_slugs.contains(&u.slug)
            || !u.check().starts_with("modal-")
            || triage_first(u, triaged)
        {
            continue;
        }
        let agent = if u.check() == "modal-form" || u.check() == "modal-depiction" {
            u.check()
        } else {
            "modal-research"
        };
        let at = out.iter().position(|(a, _)| a == agent).unwrap_or_else(|| {
            out.push((agent.to_owned(), Vec::new()));
            out.len() - 1
        });
        if !out[at].1.iter().any(|k| k == u.subject()) {
            out[at].1.push(u.subject().to_owned());
        }
    }
    out.retain(|(_, kinds)| kinds.len() >= 2);
    out
}

/// The listing.
fn report(
    rows: &[Unit],
    now: &Record,
    answered_slugs: &HashSet<String>,
    triaged: &HashMap<String, String>,
    kinds: &Path,
) -> Result<String, Fail> {
    if rows.is_empty() {
        return Ok("record-owed: no record check is owed\n".to_owned());
    }
    let left = rows
        .iter()
        .filter(|u| !answered_slugs.contains(&u.slug))
        .count();
    let tail = if answered_slugs.is_empty() {
        String::new()
    } else {
        format!(" by the delta, {left} still unanswered")
    };
    let mut lines = vec![format!("record-owed: {} unit(s) owed{tail}", rows.len())];
    for u in rows {
        if answered_slugs.contains(&u.slug) {
            lines.push(format!("  [answered] {}  - {}", u.slug, u.occasion));
        } else {
            lines.push(format!(
                "  {}  - {}\n      {}",
                u.slug,
                u.occasion,
                command(u, now, triaged, kinds)?
            ));
        }
    }
    for (agent, kinds) in modal_batches(rows, answered_slugs, triaged) {
        lines.push(format!(
            "  batched: make modal-bundle KIND=\"{}\" FOR={agent}  - ONE {agent} agent for these {} pop-ups",
            kinds.join(" "),
            kinds.len()
        ));
    }
    lines.push("Answer each with `make record-checked CHECK=<check> BUNDLE=<its bundle> RESULT=\"<counts>\"` when its check returns.".to_owned());
    lines.push("Apply a round's own EDITs with `make apply-edits FROM=<the agent's reply or its transcript>` - its unit then settles, owing no round to re-read its own words - the same command settles an EDIT you already applied by hand, word for word (feature 385 T21).".to_owned());
    Ok(lines.join("\n") + "\n")
}

fn touched_of(store_dir: &Path) -> Result<HashMap<String, String>, Fail> {
    super::triage::touched(store_dir)
}

fn flags() -> [Spec; 15] {
    [
        Spec::value("--root"),
        Spec::value("--q"),
        Spec::flag("--unanswered"),
        Spec::flag("--slugs"),
        Spec::value("--skip-check"),
        Spec::pair("--between"),
        Spec::value("--answer"),
        Spec::value("--result"),
        Spec::value("--bundle"),
        Spec::value("--notes"),
        Spec::value("--key"),
        Spec::value("--kind"),
        Spec::value("--reason"),
        Spec::value("--reply"),
        Spec::value("--fixed-by"),
    ]
}

/// `record record-owed ...`.
pub(crate) fn cli(args: &[String]) -> Reply {
    let parsed = match parse(args, &flags()) {
        Ok(p) => p,
        Err(complaint) => {
            return usage(&format!("usage: l7r-gate record record-owed: {complaint}"))
        }
    };
    let root_arg = parsed.text("--root", ".");
    let top = git(Path::new(root_arg), &["rev-parse", "--show-toplevel"])
        .trim()
        .to_owned();
    if top.is_empty() {
        return Reply {
            stdout: String::new(),
            stderr: format!("_record_owed: {root_arg} is not a git repository\n"),
            code: 1,
        };
    }
    answers::run(Path::new(&top), &parsed).unwrap_or_else(|why| Reply {
        stdout: String::new(),
        stderr: why + "\n",
        code: 1,
    })
}

/// The listing and answer modes of `record owed`, after the answer modes returned.
pub(crate) fn listing(root: &Path, parsed: &Parsed) -> Result<Reply, Fail> {
    let between = parsed.pair("--between");
    let all = match between {
        Some((a, b)) => units(root, Some(a), Some(b), &FAMILIES, "")?,
        None => units(root, None, None, &FAMILIES, "")?,
    };
    let mut rows = if between.is_none() && parsed.on("--unanswered") {
        answers::unanswered_of(root, all.clone())?
    } else {
        all.clone()
    };
    let q = parsed.text("--q", "");
    if !q.is_empty() {
        rows.retain(|u| question(u.subject()) == zfill4(q));
    }
    let skip = parsed.text("--skip-check", "");
    if !skip.is_empty() {
        rows.retain(|u| u.check() != skip);
    }
    if parsed.on("--slugs") {
        let body: String = rows.iter().map(|u| u.slug.clone() + "\n").collect();
        return Ok(Reply {
            stdout: body,
            stderr: String::new(),
            code: 0,
        });
    }
    let done: HashSet<String> = if parsed.on("--unanswered") || between.is_some() {
        HashSet::new()
    } else {
        let still: HashSet<String> = answers::unanswered(root)?
            .into_iter()
            .map(|u| u.slug)
            .collect();
        rows.iter()
            .filter(|u| !still.contains(&u.slug))
            .map(|u| u.slug.clone())
            .collect()
    };
    let named = touched_of(&store(root))?;
    let now = read_at(root, between.map(|p| p.1), None)?;
    let kinds = tree_of(root).join("l7r/diagram/interactive");
    let text = report(&rows, &now, &done, &named, &kinds)?;
    if between.is_none() {
        let batches: serde_json::Map<String, Value> = modal_batches(&rows, &done, &named)
            .into_iter()
            .map(|(a, k)| (a, json!(k)))
            .collect();
        crate::checks_door::keep_batches(root, &Value::Object(batches))?;
    }
    Ok(Reply {
        stdout: text,
        stderr: String::new(),
        code: 0,
    })
}

/// `q.zfill(4)`.
pub(crate) fn zfill4(q: &str) -> String {
    format!("{q:0>4}")
}

/// The units a door caller asks for with the common modes (`units(root, families=, uid=)`).
pub(crate) fn fingerprints(root: &Path, wanted: &[String]) -> Result<Vec<(String, String)>, Fail> {
    Ok(units(root, None, None, &FAMILIES, "")?
        .into_iter()
        .filter(|u| wanted.iter().any(|c| c == u.check()))
        .map(|u| (u.slug, u.fingerprint))
        .collect())
}

/// What a stem's notes hold and cite, for a Record read at a revision.
pub(crate) fn notes_of(rec: &Record) -> (Value, Value) {
    let notes: serde_json::Map<String, Value> = rec
        .notes
        .iter()
        .map(|(s, n)| {
            (
                s.clone(),
                Value::Object(n.iter().map(|(k, v)| (k.clone(), json!(v))).collect()),
            )
        })
        .collect();
    let cites: serde_json::Map<String, Value> = rec
        .cites
        .iter()
        .map(|(s, n)| {
            (
                s.clone(),
                Value::Object(n.iter().map(|(k, v)| (k.clone(), json!(v))).collect()),
            )
        })
        .collect();
    (Value::Object(notes), Value::Object(cites))
}

#[cfg(test)]
mod tests;
