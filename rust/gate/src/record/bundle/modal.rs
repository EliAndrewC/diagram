//! A modal check's BUNDLE and its PREPASS (from `modal_bundle.py`, feature 319, plan D5): what `modal-form`, `modal-research` or `modal-depiction` reads, copied OUT of the repository; refused while a check before it in the order (form, research, depiction) is owed (feature 375 amendment 3) or a unit owed only a triage is untriaged (feature 375 FR-001).
//!
//! `l7r-gate record modal-bundle KIND [--for modal-form|modal-research|modal-depiction] [--out DIR] [--root DIR] [--prepass] [--reason WHY]`.

use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use l7r_guard::shared::checks::{load, reply, state_path};
use l7r_guard::shared::html_text::unescape;
use l7r_guard::shared::py_text::{split, strip};
use serde_json::Value;

use super::earlier::{self, dispatches};
use super::{findall, head, py_path, py_repr, pyre, remove_tree, rstrip, shown, today, write, Run, DEFAULT_ROOT};
use crate::arbiter::bundle::marks::{transcript_of, transcripts};
use crate::record::args::{parse_with, Parsed, Spec};
use crate::record::modals::{self, Modal, DEPICTION_CHECK, FORM_CHECK, MODAL_DIRS, ORDER, RESEARCH_AGENT, RESEARCH_CHECKS};
use crate::record::owed::{answered, store, units as owed_units};
use crate::record::py_lines;
use crate::record::repo::{fail, read_text, Fail};
use crate::record::triage;
use crate::record::units::Unit;
use crate::Reply;

const QUESTIONS: &str = "research/questions";
const VARIANTS: &str = "research/assets/glossary-variants.txt";
const STANDARD: &str = "dev/modals.md";
const PARTICULAR: &str = "dev/modals-particular.md";
/// Record talk and the old feature-level label, barred from the About tab (`dev/modals.md` M11, M16).
const BARRED: [&str; 10] = [
    r"\bthis project\b",
    r"\bthe record\b",
    r"\bpages? (we )?read\b",
    r"\bno page\b",
    r"\bGUESS\b",
    r"\bThis is a guess\b",
    r"\bthis is a deliberate deviation\b",
    r"\bhistorically accurate\b",
    r"\ba survey (of|found)\b",
    r"\bsource(s)? (say|says|states)\b",
];
const TOP: usize = 10;
const ME: &str = "scripts/record/modal_bundle.py";

static COMMENT: LazyLock<Regex> = LazyLock::new(|| pyre(r"(?s)<!--.*?-->"));
static TAG: LazyLock<Regex> = LazyLock::new(|| pyre(r"<[^>]+>"));
static TAGS: LazyLock<Regex> = LazyLock::new(|| pyre(r"<!--\s*tags:\s*([^>]*?)-->"));
static HEAD: LazyLock<Regex> = LazyLock::new(|| pyre(r"(?s)<h[23][^>]*>(.*?)</h[23]>"));
static COND: LazyLock<Regex> =
    LazyLock::new(|| pyre(r"(?m)(^|^- )((?:\[[a-z_]+=[a-z_0-9-]+(?:\|[a-z_0-9-]+)*\])+)\s*"));
static ONE: LazyLock<Regex> = LazyLock::new(|| pyre(r"\[([a-z_]+)=([a-z_0-9-]+(?:\|[a-z_0-9-]+)*)\]"));
static SENTENCE: LazyLock<Regex> = LazyLock::new(|| pyre(r"[.!?](\s|$)"));
static BARRED_RE: LazyLock<Vec<Regex>> = LazyLock::new(|| BARRED.iter().map(|p| pyre(&format!("(?i){p}"))).collect());

/// The About tab's word band, per form (`dev/modals.md` M3, `dev/modals-particular.md` P3; raised by the GM, 2026-10-09).
fn band(form: &str) -> (usize, usize) {
    if form == "particular" {
        (80, 400)
    } else {
        (120, 500)
    }
}

fn guide(form: &str) -> &'static str {
    if form == "particular" {
        PARTICULAR
    } else {
        STANDARD
    }
}

/// `m.tags.get(name, default)`.
fn tag_or<'a>(m: &'a Modal, name: &str, default: &'a str) -> &'a str {
    m.tags.iter().find(|(k, _)| k == name).map_or(default, |(_, v)| v.as_str())
}

/// A page's reader-visible words: comments and tags out, entities unescaped, whitespace folded.
pub(crate) fn visible(text: &str) -> String {
    let bare = COMMENT.replace_all(text, " ");
    let bare = TAG.replace_all(&bare, " ");
    split(&unescape(&bare)).join(" ")
}

pub(crate) fn heading(text: &str) -> String {
    HEAD.captures(text)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map_or_else(String::new, |m| visible(m.as_str()))
}

fn subjects(text: &str) -> Vec<String> {
    let Some(m) = TAGS.captures(text).ok().flatten().and_then(|c| c.get(1)) else {
        return Vec::new();
    };
    for part in m.as_str().split(';') {
        let (k, v) = strip(part).split_once('=').unwrap_or((strip(part), ""));
        if strip(k) == "subject" {
            return v.split(',').map(strip).filter(|t| !t.is_empty()).map(str::to_owned).collect();
        }
    }
    Vec::new()
}

/// Every question and drawing page - not the notes, not the originals.
fn question_pages(root: &Path) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = std::fs::read_dir(root.join(QUESTIONS))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| {
            let n = p.file_name().map_or_else(String::new, |n| n.to_string_lossy().into_owned());
            n.ends_with(".html") && !n.ends_with(".notes.html") && !n.ends_with(".originals.html")
        })
        .collect();
    super::sort_paths(&mut out);
    out
}

/// The kind's words: its name, its key, and every glossary variant of either, longest first.
fn terms_of(root: &Path, m: &Modal) -> Result<Vec<String>, Fail> {
    let base: HashSet<String> = [m.tag("Name"), m.key.as_str()].iter().filter(|t| !t.is_empty()).map(|t| t.to_lowercase()).collect();
    let mut out = base.clone();
    if root.join(VARIANTS).is_file() {
        for line in py_lines(&read_text(&root.join(VARIANTS))?) {
            let (variant, term) = line.split_once('\t').unwrap_or((line, ""));
            if base.contains(&term.to_lowercase()) || base.contains(&variant.to_lowercase()) {
                out.insert(variant.to_lowercase());
                out.insert(term.to_lowercase());
            }
        }
    }
    let mut out: Vec<String> = out.into_iter().collect();
    out.sort_by(|a, b| b.chars().count().cmp(&a.chars().count()).then_with(|| a.cmp(b)));
    Ok(out)
}

/// One candidate: (score, file, heading, tags, term hits, first words).
pub(crate) type Candidate = (usize, String, String, Vec<String>, usize, String);

/// Every candidate, best first - the UNION rule, never cut (plan D5).
fn candidates(root: &Path, m: &Modal) -> Result<Vec<Candidate>, Fail> {
    let entry: Vec<String> = m.entry_files();
    let mut tags: HashSet<String> = HashSet::new();
    for f in &entry {
        if root.join(f).is_file() {
            tags.extend(subjects(&read_text(&root.join(f))?));
        }
    }
    let terms = terms_of(root, m)?;
    let pat = (!terms.is_empty()).then(|| {
        pyre(&format!(r"(?i)\b({})\b", terms.iter().map(|t| fancy_regex::escape(t).into_owned()).collect::<Vec<_>>().join("|")))
    });
    let mut out = Vec::new();
    for p in question_pages(root) {
        let rel = super::relative(&p, root);
        if entry.contains(&rel) {
            continue;
        }
        let text = read_text(&p)?;
        let words = visible(&text);
        let page_tags = subjects(&text);
        let shared = page_tags.iter().filter(|t| tags.contains(*t)).collect::<HashSet<_>>().len();
        let hits = pat.as_ref().map_or(0, |p| findall(p, &words, 0).len());
        if shared == 0 && hits == 0 {
            continue;
        }
        out.push((3 * hits.min(20) + 5 * shared, rel, heading(&text), page_tags, hits, head(&words, 280).to_owned()));
    }
    out.sort_by(|a, b| b.0.cmp(&a.0).then_with(|| a.1.cmp(&b.1)));
    Ok(out)
}

/// A knob condition opening a modal item shown as "(only where <knob> is <value>)" (FR-015, plan D14).
fn conditions_shown(text: &str) -> String {
    COND.replace_all(text, |c: &Captures<'_>| {
        let parts: Vec<String> = ONE
            .captures_iter(&c[2])
            .flatten()
            .map(|o| format!("{} is {}", &o[1], o[2].split('|').collect::<Vec<_>>().join(" or ")))
            .collect();
        format!("{}(only where {}) ", &c[1], parts.join(" and "))
    })
    .into_owned()
}

fn page_heading(root: &Path, f: &str) -> Result<String, Fail> {
    let p = root.join(f);
    Ok(if p.is_file() { heading(&read_text(&p)?) } else { "(MISSING FILE)".to_owned() })
}

fn paragraphs(text: &str) -> Vec<&str> {
    text.split("\n\n").filter(|p| !strip(p).is_empty()).collect()
}

fn guesses(m: &Modal) -> Vec<String> {
    py_lines(m.tag("Guesses"))
        .into_iter()
        .filter(|g| !strip(g).is_empty())
        .map(|g| g.chars().skip(2).collect())
        .collect()
}

/// The modal as its reader meets it: the heading, each tab's text, and the questions the References tab lists.
fn render(root: &Path, m: &Modal) -> Result<String, Fail> {
    let mut lines = vec![
        format!("# {}", tag_or(m, "Name", &m.key)),
        String::new(),
        format!("class `{}` (key `{}`), form `{}`, origin `{}`", m.cls, m.key, m.form(), m.origin),
        String::new(),
        "## About".to_owned(),
        String::new(),
    ];
    lines.extend(paragraphs(m.tag("About")).iter().map(|p| format!("{p}\n")));
    lines.push("(The page adds the generated sibling line - 'Not to be confused with ...' - at the foot of About.)\n".to_owned());
    let g = guesses(m);
    lines.extend(["## Guesses".to_owned(), String::new()]);
    if g.is_empty() {
        lines.push("(no Guesses tab - nothing guessed)".to_owned());
    } else {
        lines.extend(g.iter().map(|x| format!("- {x}")));
    }
    lines.push(String::new());
    let dep = paragraphs(m.tag("Depiction"));
    lines.extend(["## Depiction".to_owned(), String::new()]);
    if dep.is_empty() {
        lines.push("(no Depiction paragraphs)\n".to_owned());
    } else {
        lines.extend(dep.iter().map(|p| format!("{p}\n")));
    }
    for f in m.drawing_files() {
        lines.push(format!("- {}  - `{f}`", page_heading(root, &f)?));
    }
    if dep.is_empty() && m.drawing_files().is_empty() {
        lines.push("(no Depiction tab - nothing to say and no drawing page)".to_owned());
    }
    lines.extend([String::new(), "## References".to_owned(), String::new()]);
    for f in m.entry_files() {
        lines.push(format!("- {}  - `{f}`", page_heading(root, &f)?));
    }
    lines.extend([String::new(), format!("Sources: {}", m.tag("Sources")), String::new()]);
    Ok(conditions_shown(&lines.join("\n")))
}

/// The text `window` characters either side of the byte range `start..end` of `text`.
fn around(text: &str, start: usize, end: usize, window: usize) -> String {
    let (before, after) = (text[..start].chars().count(), text[..end].chars().count());
    text.chars().skip(before.saturating_sub(window)).take(after + window - before.saturating_sub(window)).collect()
}

/// The mechanical half of the modal checks: the About band, barred phrases, long guesses, Entry files.
pub(crate) fn prepass(root: &Path, m: &Modal) -> String {
    let about = m.tag("About");
    let n = split(about).len();
    let (lo, hi) = band(m.form());
    let mut out = vec![
        format!("prepass - {} ({})", m.cls, m.form()),
        format!("- About words: {n} (band {lo}-{hi}){}", if (lo..=hi).contains(&n) { "" } else { "  <- OUTSIDE THE BAND" }),
    ];
    for pat in BARRED_RE.iter() {
        for hit in pat.find_iter(about).flatten() {
            out.push(format!("- barred phrase in About (M11/M16): {} - ...{}...", py_repr(hit.as_str()), around(about, hit.start(), hit.end(), 50)));
        }
    }
    for g in guesses(m) {
        if findall(&SENTENCE, &g, 0).len() > 2 {
            out.push(format!("- a guess past two sentences (M3): {}...", head(&g, 90)));
        }
    }
    for f in m.entry_files() {
        if !root.join(&f).is_file() {
            out.push(format!("- Entry names no file: {f}"));
        }
    }
    if m.entry_files().is_empty() {
        out.push("- Entry names no question file".to_owned());
    }
    if out.len() == 2 {
        out.push("- nothing else found".to_owned());
    }
    out.join("\n") + "\n"
}

/// The wording `modal-research` rounds fixed on the pop-up `uid` that still stands in `text` (343's border-court ruling): `apply_edits.py` refuses a modal-form EDIT that drops one.
pub(crate) fn research_held(root: &Path, uid: &str, text: &str) -> Vec<String> {
    let state = load(&state_path(&root.to_string_lossy()).unwrap_or_else(|| PathBuf::from("/nonexistent")));
    let subject = format!("modal:{uid}");
    let mut out: Vec<String> = Vec::new();
    for v in dispatches(&state) {
        let mine = v.get("check").and_then(Value::as_str) == Some("modal-research")
            && v.get("subjects").and_then(Value::as_array).is_some_and(|s| s.iter().any(|x| x.as_str() == Some(subject.as_str())));
        if !mine {
            continue;
        }
        let kept = v.get("reply").and_then(Value::as_str).filter(|r| !r.is_empty()).map(Path::new);
        let mut text_of = kept.filter(|p| p.is_file()).map_or_else(String::new, |p| read_text(p).unwrap_or_default());
        let aid = v.get("aid").map(super::py_str).filter(|a| !l7r_guard::shared::checks::falsy(v.get("aid")) && !a.is_empty());
        if text_of.is_empty() {
            if let Some(aid) = aid {
                text_of = transcript_of(&transcripts(), &aid).map_or_else(String::new, |t| reply::reply_of(&t.to_string_lossy(), ""));
            }
        }
        for (_, _, new) in reply::blocks(&text_of) {
            if !strip(&new).is_empty() && text.contains(&new) && !out.contains(&new) {
                out.push(new);
            }
        }
    }
    out
}

/// Why `for_` must wait on `m`: a check BEFORE it in the order has a unit owed and unanswered (feature 375 amendment 3, FR-019a).
fn order_hold(root: &Path, m: &Modal, for_: &str, rows: &[Unit]) -> String {
    let s = store(root);
    let at = ORDER.iter().position(|a| *a == for_).unwrap_or(0);
    for agent in &ORDER[..at] {
        for c in modals::agent_units(agent) {
            let slug = format!("{c}:{}", m.uid());
            if let Some(u) = rows.iter().find(|u| u.slug == slug) {
                if !answered(&s, &u.slug, &u.fingerprint, &u.reading) {
                    return format!(
                        "{} is owed and unanswered - a pop-up's checks run in order, form, then research, then depiction (feature 375 amendment 3: run together, each one's edits re-owed the others). First: make modal-bundle KIND=\"{}\" FOR={agent}",
                        u.slug,
                        m.uid()
                    );
                }
            }
        }
    }
    String::new()
}

/// The MANIFEST's owed section: `owed-checks:`, a `unit:` line each, the pages kept as blobs (feature 375 plan D1), what owed each.
fn owed_lines(root: &Path, m: &Modal, for_: &str, owed: &[Unit]) -> Result<String, Fail> {
    let (fp_form, fp_research) = modals::fingerprints(root, m)?;
    let units: Vec<(String, String)> = if for_ == FORM_CHECK {
        vec![(format!("{FORM_CHECK}:{}", m.uid()), fp_form)]
    } else if for_ == DEPICTION_CHECK {
        vec![(format!("{DEPICTION_CHECK}:{}", m.uid()), modals::depiction_fingerprint(root, m)?)]
    } else {
        RESEARCH_CHECKS.iter().map(|c| (format!("{c}:{}", m.uid()), fp_research.clone())).collect()
    };
    let files = if for_ == DEPICTION_CHECK {
        m.drawing_files()
    } else if for_ == RESEARCH_AGENT {
        m.entry_files()
    } else {
        Vec::new()
    };
    let mut text = format!("## Owed (feature 311)\n\nowed-checks: {for_}\n");
    for (s, fp) in &units {
        text += &format!("unit: {s} {fp}\n");
    }
    for f in &files {
        let b = triage::keep(root, f);
        if !b.is_empty() {
            text += &format!("page: {f} {b}\n");
        }
    }
    for (s, _) in &units {
        if let Some(u) = owed.iter().rev().find(|u| &u.slug == s).filter(|u| !u.occasion.is_empty()) {
            text += &format!("owed: {s} - {}\n", u.occasion);
        }
    }
    Ok(text)
}

/// What a bundle copies, in its MANIFEST's order.
pub(crate) struct Put {
    pub(crate) out: PathBuf,
    pub(crate) rows: Vec<(String, String, String)>,
}

impl Put {
    pub(crate) fn put(&mut self, name: &str, text: &str, origin: &str, what: &str) -> Result<(), Fail> {
        write(&self.out.join(name), text)?;
        self.rows.push((name.to_owned(), origin.to_owned(), what.to_owned()));
        Ok(())
    }
}

fn research_parts(root: &Path, m: &Modal, put: &mut Put, grep_targets: &mut Vec<String>) -> Result<(), Fail> {
    for f in m.entry_files() {
        let p = root.join(&f);
        if p.is_file() {
            let name = format!("entry/{}", p.file_name().map_or_else(String::new, |n| n.to_string_lossy().into_owned()));
            put.put(&name, &read_text(&p)?, &f, "a page the modal's Entry names - what its statements must rest on")?;
        }
    }
    let cands = if m.form() == "standard" { candidates(root, m)? } else { Vec::new() };
    let mut listing = vec![format!("# Candidates for {} - {}, best first (the UNION rule; never cut)", m.cls, cands.len()), String::new()];
    for (i, (score, rel, head_, tags, hits, first)) in cands.iter().enumerate() {
        let tags = if tags.is_empty() { "-".to_owned() } else { tags.join(",") };
        listing.push(format!("{}. `{rel}` - {head_}  [tags {tags}; term hits {hits}; score {score}]", i + 1));
        if i < 30 {
            listing.push(format!("   {first}"));
        }
    }
    put.put("candidates.md", &(listing.join("\n") + "\n"), ME, "every question that may answer what the modal leaves open (gaps) - the top ten are files under cand/, every page under record/")?;
    std::fs::create_dir(put.out.join("cand")).map_err(fail)?;
    for (_, rel, ..) in cands.iter().take(TOP) {
        let name = Path::new(rel).file_name().map_or_else(String::new, |n| n.to_string_lossy().into_owned());
        std::fs::copy(root.join(rel), put.out.join("cand").join(name)).map_err(fail)?;
    }
    grep_targets.push("cand/".to_owned());
    std::fs::create_dir(put.out.join("record")).map_err(fail)?;
    for p in question_pages(root) {
        std::fs::copy(&p, put.out.join("record").join(p.file_name().unwrap_or_default())).map_err(fail)?;
    }
    grep_targets.push("record/".to_owned());
    Ok(())
}

/// The refusals before a bundle is written; Some(exit) where one stands.
fn held_back(run: &mut Run, root: &Path, m: &Modal, for_: &str, reason: &str, rows: &[Unit]) -> Result<Result<(bool, String), i32>, Fail> {
    let modal_rows: Vec<(String, String, String)> = rows
        .iter()
        .filter(|u| u.check() == FORM_CHECK || u.check() == DEPICTION_CHECK || RESEARCH_CHECKS.contains(&u.check()))
        .map(|u| (u.slug.clone(), u.occasion.clone(), u.fingerprint.clone()))
        .collect();
    let refused = triage::refusal(root, m, for_, Some(&modal_rows))?;
    if !refused.is_empty() && split(reason).len() < 2 {
        run.warn(&format!("modal-bundle: {refused}. A check the GM asked for, or a backfill: REASON=\"<why>\""));
        return Ok(Err(3));
    }
    if !refused.is_empty() {
        run.say(&format!("modal-bundle: bundled without its triage, because: {reason}"));
    }
    let held = order_hold(root, m, for_, rows);
    let first_raw = std::env::var("CHECK_ORDER_OK").unwrap_or_default();
    let first = strip(&first_raw).to_owned();
    if !held.is_empty() && split(&first).len() < 2 {
        run.warn(&format!("modal-bundle: {held}. To bundle it anyway: CHECK_ORDER_OK=\"<why>\" (two words or more; the MANIFEST records it)"));
        return Ok(Err(3));
    }
    if !held.is_empty() {
        run.say(&format!("modal-bundle: bundled out of order, because: {first}"));
    }
    Ok(Ok((!held.is_empty(), first)))
}

/// One pop-up's bundle (`bundle`).
pub(crate) fn bundle(run: &mut Run, root: &Path, kind: &str, for_: &str, out_arg: &str, reason: &str) -> Result<i32, Fail> {
    let now = modals::modals_now(root, true)?;
    let Some(m) = modals::find(&now, kind).cloned() else {
        run.warn(&format!("modal-bundle: no About-form modal {} (a class name or key) under {}", py_repr(kind), MODAL_DIRS.join(", ")));
        return Ok(2);
    };
    let rows = owed_units(root, None, None, &["modal"], &m.uid())?;
    let (held, first) = match held_back(run, root, &m, for_, reason, &rows)? {
        Ok(got) => got,
        Err(code) => return Ok(code),
    };
    let out = if out_arg.is_empty() { Path::new(DEFAULT_ROOT).join(format!("modal-{}-{for_}", m.uid().replace('/', "-"))) } else { py_path(out_arg) };
    if out.exists() {
        if !out.join("MANIFEST.md").is_file() {
            run.warn(&format!("modal-bundle: {} exists and is not a bundle - choose another OUT", shown(&out)));
            return Ok(2);
        }
        remove_tree(&out)?;
    }
    std::fs::create_dir_all(&out).map_err(fail)?;
    let mut put = Put { out: out.clone(), rows: Vec::new() };
    put.put("modal.md", &render(root, &m)?, &m.origin, "the modal as its reader meets it - the thing you judge")?;
    put.put("text.md", &format!("{}\n", rstrip(&m.doc)), &m.origin, "the modal's file line for line - an EDIT block's old text is one of these lines (or part of one), exactly, and its target is this origin")?;
    let g = guide(m.form());
    put.put(
        "guidelines.txt",
        &format!("This modal is of the {} form: rule on it by the guidelines from `{g}` at the end of your agent file (`make agent-sync` writes them from that source).\n", if g == PARTICULAR { "particular" } else { "standard" }),
        g,
        "which guidelines govern this modal - the rules are in your contract; name a rule (M#/P#) in every finding",
    )?;
    put.put("prepass.txt", &prepass(root, &m), ME, "the mechanical findings - rule on each")?;
    let mut grep_targets: Vec<String> = Vec::new();
    if for_ == DEPICTION_CHECK {
        super::depiction::parts(run, root, &m, &mut put, &mut grep_targets)?;
    }
    // the Python rebound `held` here to the research-held wording, so a form bundle's escape line follows that list (kept as it ran)
    let mut held_escape = held;
    if for_ == FORM_CHECK {
        let held = research_held(root, &m.uid(), &m.doc);
        held_escape = !held.is_empty();
        if held_escape {
            let list: Vec<String> = held.iter().map(|h| format!("- {}", py_repr(h))).collect();
            put.put("research-held.md", &format!("# Wording the research rounds fixed - keep it\n\n{}\n", list.join("\n")), ME, "what modal-research rounds wrote and the record backs: a form EDIT never drops or widens these words")?;
        }
    }
    if for_ == RESEARCH_AGENT {
        research_parts(root, &m, &mut put, &mut grep_targets)?;
    }
    let mut manifest = vec![
        format!("# Check bundle - modal {}, for {for_}", m.cls),
        String::new(),
        format!("Written {} by `make modal-bundle`. Every file here is a COPY. Read these and nothing under the repository (feature 250). A finding names the ORIGIN column - the file the session will edit.", today()),
        String::new(),
        format!(
            "**Everything you need is in THIS file**, each copy under its origin below; read it once.{}",
            if grep_targets.is_empty() { "" } else { " Beside it, NOT inlined: `cand/` (the top ten candidates, each a file to Read when its line in `candidates.md` looks like an answer) and `record/` (every question page - a GREP target; never read it whole)." }
        ),
        String::new(),
        "| file | origin | what it is for |".to_owned(),
        "|---|---|---|".to_owned(),
    ];
    manifest.extend(put.rows.iter().map(|(f, o, w)| format!("| `{f}` | `{o}` | {w} |")));
    manifest.push(String::new());
    for (name, origin, _) in &put.rows {
        manifest.push(format!("## `{name}` - origin `{origin}`\n\n```\n{}\n```\n", rstrip(&read_text(&out.join(name))?)));
    }
    manifest.push("Reply with your report: the counts on the first line, then only what the session must act on (your contract gives the form).\n".to_owned());
    let escape = if held_escape { format!("check-order-escape: {first}\n") } else { String::new() };
    let text = manifest.join("\n") + "\n" + &owed_lines(root, &m, for_, &rows)? + &escape;
    let full = format!("{text}{}", earlier::section(root, &out, &text)?);
    write(&out.join("MANIFEST.md"), &full)?;
    run.say(&format!("modal-bundle: {} file(s) in {} - hand the {for_} agent {}", put.rows.len(), shown(&out), shown(&out.join("MANIFEST.md"))));
    Ok(0)
}

/// ONE AGENT FOR SEVERAL POP-UPS OF ONE CHECK (feature 385 T02, plan D12): each its own bundle, one top MANIFEST.
fn bundles(run: &mut Run, root: &Path, kinds: &[&str], for_: &str, out_arg: &str, reason: &str) -> Result<i32, Fail> {
    let out = if out_arg.is_empty() { Path::new(DEFAULT_ROOT).join(format!("modal-batch-{for_}")) } else { py_path(out_arg) };
    if out.exists() {
        remove_tree(&out)?;
    }
    std::fs::create_dir_all(&out).map_err(fail)?;
    let mut subs: Vec<PathBuf> = Vec::new();
    for (n, kind) in kinds.iter().enumerate() {
        let sub = out.join(format!("{:02}-{}", n + 1, super::dash_runs(kind, char::is_ascii_alphanumeric)));
        let code = bundle(run, root, kind, for_, &shown(&sub), reason)?;
        if code != 0 {
            return Ok(code);
        }
        subs.push(sub);
    }
    let mut units = Vec::new();
    let mut held = Vec::new();
    for s in &subs {
        let text = read_text(&s.join("MANIFEST.md"))?;
        units.extend(py_lines(&text).into_iter().filter(|l| l.starts_with("unit: ")).map(str::to_owned));
        if text.contains(earlier::HEAD) {
            held.push(format!("`{}`", s.file_name().unwrap_or_default().to_string_lossy()));
        }
    }
    let mut parts = vec![
        format!("# {} pop-ups for {for_}, one agent (feature 385, plan D12)\n", subs.len()),
        format!("owed-checks: {for_}\n"),
        "Judge EACH pop-up below from its own bundle, as your contract says, and reply with one section per pop-up, headed by its `unit:` line. The drawing pages repeat from bundle to bundle: read each page once.\n".to_owned(),
    ];
    parts.extend(subs.iter().map(|s| format!("- `{}`", shown(&s.join("MANIFEST.md")))));
    parts.push(String::new());
    if !held.is_empty() {
        parts.push(format!("Earlier rounds: {} - each MANIFEST's `{}` section.", held.join(", "), earlier::HEAD));
        parts.push(String::new());
    }
    parts.extend(units);
    write(&out.join("MANIFEST.md"), &(parts.join("\n") + "\n"))?;
    run.say(&format!("modal-bundle: {} pop-ups in one bundle - dispatch ONE {for_} agent on {}; record each with make record-checked CHECK={for_} BUNDLE=<its own bundle>", subs.len(), shown(&out.join("MANIFEST.md"))));
    Ok(0)
}

fn specs() -> [Spec; 5] {
    [Spec::value("--for"), Spec::value("--out"), Spec::value("--root"), Spec::flag("--prepass"), Spec::value("--reason")]
}

/// `record modal-bundle ...`.
pub(crate) fn cli(args: &[String]) -> Reply {
    let p = match parse_with(args, &specs(), 1) {
        Ok(p) if p.positional.is_empty() => return super::usage("modal-bundle", "the following arguments are required: kind"),
        Ok(p) if ORDER.contains(&p.text("--for", FORM_CHECK)) => p,
        Ok(p) => return super::usage("modal-bundle", &format!("argument --for: invalid choice: {}", py_repr(p.text("--for", "")))),
        Err(complaint) => return super::usage("modal-bundle", &complaint),
    };
    let root = super::resolve(p.text("--root", "."));
    let mut run = Run::new(&root);
    let done = main(&mut run, &root, &p);
    run.reply(done)
}

fn main(run: &mut Run, root: &Path, p: &Parsed) -> Result<i32, Fail> {
    let kind = p.positional[0].as_str();
    let (for_, out, reason) = (p.text("--for", FORM_CHECK), p.text("--out", ""), p.text("--reason", ""));
    if p.on("--prepass") {
        let now = modals::modals_now(root, true)?;
        let Some(m) = modals::find(&now, kind) else {
            run.warn(&format!("modal-prepass: no About-form modal {}", py_repr(kind)));
            return Ok(2);
        };
        run.out.push_str(&prepass(root, m));
        return Ok(0);
    }
    let kinds = split(kind);
    if kinds.len() > 1 {
        return bundles(run, root, &kinds, for_, out, reason);
    }
    bundle(run, root, kind, for_, out, reason)
}

#[cfg(test)]
mod tests;
