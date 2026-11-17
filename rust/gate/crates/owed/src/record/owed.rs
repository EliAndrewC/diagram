//! Which record checks this delta owes, and which are still unanswered (from `record_owed.py`, feature 449 T87): the one scripted answer, read against the merge base and the working tree or between two revisions. `make record-owed`, the push's record gate and the check bundles ask it; `answers.rs` is its record of what was answered.

pub mod answers;
pub mod reply;

use std::collections::{HashMap, HashSet};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::split;
use serde_json::{json, Value};

pub use answers::{
    answer, answered, file_outside, keep_reading, read_answer, reply_checks, reply_of, settle,
    store, unanswered, write_answer, Named, FIXED,
};

use super::args::{parse, Parsed, Spec};
use super::delta::Delta;
use super::modals;
use super::repo::{git, read_text, Fail};
use super::translation;
use super::units::{
    self, digest, question, re, stem_of, Keyed, Record, Unit, QUESTIONS, SOURCE_DIRS,
};
use crate::Reply;

static SOURCE_FILE: LazyLock<Regex> = LazyLock::new(|| re(r"^\d+-([a-z0-9-]+)\.html$"));

/// The families of owed units, each computed by its own reader.
pub const FAMILIES: [&str; 4] = ["record", "translation", "entry-drift", "modal"];

fn usage(line: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("{line}\n"),
        code: 2,
    }
}

/// The merge base of HEAD with origin/main, else HEAD.
#[must_use]
pub fn merge_base(root: &Path) -> String {
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
fn changed_sources(delta: &mut Delta, base: &str, head: Option<&str>) -> HashSet<String> {
    let mut names: Vec<String> = split(&delta.changed(base, head, &SOURCE_DIRS))
        .into_iter()
        .map(str::to_owned)
        .collect();
    if head.is_none() {
        names.extend(
            split(&delta.others(&SOURCE_DIRS))
                .into_iter()
                .map(str::to_owned),
        );
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
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
#[expect(
    clippy::implicit_hasher,
    reason = "every caller passes the std set, and a hasher parameter would have each None caller name one"
)]
pub fn read_at(
    root: &Path,
    rev: Option<&str>,
    sources: Option<&HashSet<String>>,
) -> Result<Record, Fail> {
    read_at_in(&mut Delta::new(root), rev, sources)
}

/// The record's files [`read_at`] reads at `rev`: its question pages and, of the write-ups, those named in `sources`.
fn record_names(delta: &mut Delta, rev: &str, sources: Option<&HashSet<String>>) -> Vec<String> {
    let mut specs = vec![QUESTIONS];
    specs.extend(SOURCE_DIRS);
    let wanted = |name: &str| sources.is_none_or(|s| s.contains(name));
    delta
        .listing(rev, &specs)
        .split('\n')
        .filter(|n| {
            Path::new(n).extension().is_some_and(|x| x == "html")
                && (!is_write_up(n) || wanted(n.rsplit_once('/').map_or("", |p| p.1)))
        })
        .map(str::to_owned)
        .collect()
}

/// [`read_at`], on one computation's reads.
fn read_at_in(
    delta: &mut Delta,
    rev: Option<&str>,
    sources: Option<&HashSet<String>>,
) -> Result<Record, Fail> {
    let root = delta.root().to_path_buf();
    let (mut files, mut write_ups) = (Keyed::default(), Vec::new());
    let wanted = |name: &str| sources.is_none_or(|s| s.contains(name));
    if let Some(rev) = rev {
        let names = record_names(delta, rev, sources);
        for (name, text) in names.iter().zip(delta.texts(rev, &names)) {
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

fn translation_units(delta: &mut Delta, now: &Record) -> Result<Vec<Unit>, Fail> {
    let mut found: Keyed<Unit> = Keyed::default();
    for row in translation::owed_in(delta)? {
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

/// What the entry-drift report reads (`entry.rs`, `entry_owed.py` ported by feature 449 T149): the record's question pages, the registry's
/// modal files and sibling table under `l7r/diagram/interactive/`, and the gate's own sources and wrapper, which build the binary that
/// answers it. A change to any of them starts it (the T065 clause, `ask:449-T87-entry-owed`); the Python's own scripts and doors, which
/// it read before the port, left with it.
pub(crate) const ENTRY_READS: [&str; 4] = [
    "l7r/diagram/interactive/",
    "research/",
    "scripts/gates/l7r-gate.sh",
    "rust/gate/",
];

/// Whether the entry-drift report must run for this delta: the family is asked, and a file it reads changed against the base, untracked
/// files included, or the tree holds no modal files - the tree with no engine, where the Python's import failed and the run with it.
fn entry_drift_owed(delta: &mut Delta) -> bool {
    let base = delta.entry_base();
    if base.is_empty() {
        return false;
    }
    let names = delta.changed(&base, None, &ENTRY_READS) + &delta.others(&ENTRY_READS);
    !delta.root().join(modals::MODALS).is_dir() || names.lines().any(|n| !n.trim().is_empty())
}

fn entry_units(root: &Path, now: &Record) -> Result<Vec<Unit>, Fail> {
    if !root.join(modals::MODALS).is_dir() {
        return Err(format!(
            "ImportError: no engine here - {} holds no {} (the import the Python made of it failed)",
            root.display(),
            modals::MODALS
        ));
    }
    entry_units_of(root, now, entry_lines(root)?)
}

/// The entry-drift report's lines, in process (feature 449 T149).
#[cfg(not(any(test, feature = "testkit")))]
fn entry_lines(root: &Path) -> Result<Vec<String>, Fail> {
    super::entry::owed(root).map(|(_, lines)| lines)
}

/// The tests' seam, as the stub of `entry_owed.py` was before the port (this crate's tests, and those of the crates above it through the
/// `testkit` feature, whose scratch records hold a few modals and not the whole registry): a scratch record names its lines in
/// `entry-lines.json`, or asks for the real report with `entry-real`; else none. The report itself is `entry.rs`'s, tested there on a
/// tree holding every kind.
#[cfg(any(test, feature = "testkit"))]
fn entry_lines(root: &Path) -> Result<Vec<String>, Fail> {
    if root.join("entry-real").exists() {
        return super::entry::owed(root).map(|(_, lines)| lines);
    }
    match std::fs::read_to_string(root.join("entry-lines.json")) {
        Ok(text) => serde_json::from_str(&text).map_err(|e| e.to_string()),
        Err(_) => Ok(Vec::new()),
    }
}

/// The entry-drift units of the report's lines: a key that is an About-form modal owes the modal checks instead, and is left out.
fn entry_units_of(root: &Path, now: &Record, lines: Vec<String>) -> Result<Vec<Unit>, Fail> {
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
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn units(
    root: &Path,
    base: Option<&str>,
    head: Option<&str>,
    families: &[&str],
    uid: &str,
) -> Result<Vec<Unit>, Fail> {
    units_in(&mut Delta::new(root), base, head, families, uid)
}

/// Reads every file at `base` the asked families will read of it, by one `git cat-file --batch`: the record's pages and
/// touched write-ups, translation's question pages where its base is this one, the pop-ups' files.
fn prefetch(
    delta: &mut Delta,
    base: &str,
    touched: Option<&HashSet<String>>,
    asked: (bool, bool, bool),
) {
    let (record, translation, modal) = asked;
    let mut names = Vec::new();
    if record || (translation && delta.translation_base() == base) {
        names.extend(record_names(delta, base, touched));
    }
    if modal {
        names.extend(modals::rev_names(delta, base));
    }
    delta.fetch(base, &names);
}

/// [`units`], on one computation's reads.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn units_in(
    delta: &mut Delta,
    base: Option<&str>,
    head: Option<&str>,
    families: &[&str],
    uid: &str,
) -> Result<Vec<Unit>, Fail> {
    let base = base
        .filter(|b| !b.is_empty())
        .map_or_else(|| delta.merge_base(), str::to_owned);
    let mut out: Vec<Unit> = Vec::new();
    let has = |f: &str| families.contains(&f);
    let touched = if base.is_empty() {
        None
    } else {
        Some(changed_sources(delta, &base, head))
    };
    let entry = head.is_none() && has("entry-drift") && entry_drift_owed(delta);
    if head.is_none() && !base.is_empty() {
        let asked = (has("record"), has("translation"), has("modal"));
        prefetch(delta, &base, touched.as_ref(), asked);
    }
    let now = if has("record") || (head.is_none() && has("translation")) || entry {
        Some(read_at_in(delta, head, touched.as_ref())?)
    } else {
        None
    };
    if let (true, Some(current)) = (has("record"), now.as_ref()) {
        let was = if base.is_empty() {
            Record::default()
        } else {
            read_at_in(delta, Some(&base), touched.as_ref())?
        };
        out = units::owed(current, &was);
    }
    if head.is_none() {
        if let (true, Some(now)) = (has("translation"), now.as_ref()) {
            out.extend(translation_units(delta, now)?);
        }
        if let (true, Some(now)) = (entry, now.as_ref()) {
            out.extend(entry_units(delta.root(), now)?);
        }
        if has("modal") {
            out.extend(modals::owed_in(delta, &base, uid)?.into_iter().map(
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

/// The modal class(es) whose `key` is this one (the map's Well and the sheet's), as `make check-bundle KIND=` takes them: the registry's
/// kinds (feature 449 T149), in the order the lexing of `classes/*.py` then `compound_kinds/*.py` met them, `module.Class` where two match.
fn modal_classes(key: &str) -> Vec<String> {
    let hits: Vec<(&str, &str)> = l7r_gate_registry::kinds::REGISTRIES
        .iter()
        .flat_map(l7r_gate_registry::kinds::by_file)
        .filter(|(_, k)| k.key == key)
        .map(|(m, k)| (m, k.class))
        .collect();
    let many = hits.len() > 1;
    hits.into_iter()
        .map(|(m, c)| {
            if many {
                format!("{m}.{c}")
            } else {
                c.to_owned()
            }
        })
        .collect()
}

/// Owed only by a moved page and not yet marked touched at its fingerprint.
fn triage_first(u: &Unit, triaged: &HashMap<String, String>) -> bool {
    u.occasion.starts_with("a page its ") && triaged.get(&u.slug) != Some(&u.fingerprint)
}

/// What builds the bundle for a unit.
fn command(u: &Unit, now: &Record, triaged: &HashMap<String, String>) -> String {
    let (q, check) = (question(u.subject()), u.check());
    if check == "source-applicability" {
        return format!("make check-bundle KEY={}", u.subject());
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
        return format!(
            "{}  then  make record-checked CHECK=source-reader Q={q} NOTES={note}",
            keys.iter()
                .map(|k| format!("make check-bundle KEY={k} WHOLE=1"))
                .collect::<Vec<_>>()
                .join(" ; ")
        );
    }
    if check.starts_with("modal-") && triage_first(u, triaged) {
        return "make modal-triage  then  make modal-triaged BUNDLE=<its bundle> REPLY=<the reply>  (a kind it names is then bundled as below)".to_owned();
    }
    if check.starts_with("modal-") {
        let agent = if check == "modal-form" || check == "modal-depiction" {
            check
        } else {
            "modal-research"
        };
        return format!(
            "make modal-bundle KIND=\"{}\" FOR={agent}  then  make record-checked CHECK={check} BUNDLE=<its bundle> RESULT=...",
            u.subject()
        );
    }
    if check == "entry-drift" {
        static FOUND: LazyLock<Regex> = LazyLock::new(|| re(r"\b(\d{4})-"));
        let qq = FOUND
            .captures(&u.occasion)
            .ok()
            .flatten()
            .map_or_else(|| "<its section>".to_owned(), |c| c[1].to_owned());
        let mut classes = modal_classes(u.subject());
        if classes.is_empty() {
            classes.push(format!("<the class of {}>", u.subject()));
        }
        return format!(
            "{}  then  make record-checked CHECK=entry-drift KIND=\"{}\" BUNDLE=<its bundle> RESULT=<verdict>",
            classes.iter().map(|k| format!("make check-bundle Q={qq} FOR=entry-drift KIND=\"{k}\"")).collect::<Vec<_>>().join(" ; "),
            u.subject()
        );
    }
    format!("make check-bundle Q={q} FOR={check}")
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
) -> String {
    if rows.is_empty() {
        return "record-owed: no record check is owed\n".to_owned();
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
                command(u, now, triaged)
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
    lines.join("\n") + "\n"
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
#[must_use]
pub fn cli(args: &[String]) -> Reply {
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
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn listing(root: &Path, parsed: &Parsed) -> Result<Reply, Fail> {
    let between = parsed.pair("--between");
    let delta = &mut Delta::new(root);
    let all = match between {
        Some((a, b)) => units_in(delta, Some(a), Some(b), &FAMILIES, "")?,
        None => units_in(delta, None, None, &FAMILIES, "")?,
    };
    let mut rows = if between.is_none() && parsed.on("--unanswered") {
        answers::unanswered_in(delta, all.clone())?
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
        // the units of this same tree, computed once above: `unanswered` would compute them again (feature 449 T107)
        let still: HashSet<String> = answers::unanswered_in(delta, all.clone())?
            .into_iter()
            .map(|u| u.slug)
            .collect();
        rows.iter()
            .filter(|u| !still.contains(&u.slug))
            .map(|u| u.slug.clone())
            .collect()
    };
    let named = touched_of(&delta.store())?;
    let now = read_at(root, between.map(|p| p.1), None)?;
    let text = report(&rows, &now, &done, &named);
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
#[must_use]
pub fn zfill4(q: &str) -> String {
    format!("{q:0>4}")
}

/// The units a door caller asks for with the common modes (`units(root, families=, uid=)`).
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn fingerprints(root: &Path, wanted: &[String]) -> Result<Vec<(String, String)>, Fail> {
    Ok(units(root, None, None, &FAMILIES, "")?
        .into_iter()
        .filter(|u| wanted.iter().any(|c| c == u.check()))
        .map(|u| (u.slug, u.fingerprint))
        .collect())
}

/// What a stem's notes hold and cite, for a Record read at a revision.
#[must_use]
pub fn notes_of(rec: &Record) -> (Value, Value) {
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
