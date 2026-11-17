//! `make open-questions` - every guess and every unfound source, read from where they are marked (`scripts/record/open_questions.py`,
//! feature 285; ported by feature 449 T149 under `ask:449-phase4-slices` Q5, the registry's reader).
//!
//! WHY DERIVED. The GM, 2026-09-28: "a make target which assembles a list of guesses that could use a research pass is better than trying
//! to assemble something by hand, which then will drift out of date due to repeating ourselves in multiple places." The record already
//! labels each GUESS and writes an absence note for each source not found, so the list is those labels, collected.
//!
//! WHAT IT READS (specs/285 plan): the record's question pages and the notes beside each - never a built page (D1), comments stripped as
//! session notes (D2) - and every other tracked text file outside `research/` and `tests/` for a whole-word GUESS (D7), the tooling's own
//! logs skipped. A question's map features come by three routes (D3): a class's `Entry:` or `Drawing:` names it, a question a class names
//! links to it (one hop), or an engine `.py` file quotes its anchor or its heading.

use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::sources::{question_text, research_questions};
use l7r_gate_research::Result;
use l7r_guard::shared::py_text::{collapse, strip};

use crate::about::classes;

static FRAGMENT: LazyLock<Regex> = LazyLock::new(|| py(r"^\d{4}-[^.]+(?:\.drawing)?\.html$"));
static TAGS: LazyLock<Regex> = LazyLock::new(|| py(r"<!-- tags: subject=([a-z0-9-]+)"));
static COMMENT: LazyLock<Regex> = LazyLock::new(|| py(r"(?s)<!--.*?-->"));
static TAG: LazyLock<Regex> = LazyLock::new(|| py(r"<[^>]+>"));
static HEADING: LazyLock<Regex> = LazyLock::new(|| py(r#"(?s)<h2 id="([^"]+)">(.*?)</h2>"#));
/// the label and its plural ("the shares are GUESSES")
static GUESS: LazyLock<Regex> = LazyLock::new(|| py(r"\bGUESS(?:ES)?\b"));

/// Does `text` carry the label? Its letters first: the pattern's word boundaries are Python's, lookarounds the backtracking engine runs
/// slowly over the whole tree's text, and no text without the letters can match.
fn guessed(text: &str) -> bool {
    text.contains("GUESS") && GUESS.is_match(text).unwrap_or(false)
}
const ABSENCE: &str = "no publicly readable source";
static SETTLED: LazyLock<Regex> = LazyLock::new(|| py(r"\bsettled \d{4}-\d{2}-\d{2}\b"));
static NOTE_LI: LazyLock<Regex> =
    LazyLock::new(|| py(r#"(?s)<li data-note="([^"]+)"[^>]*>(.*?)</li>"#));
static LINK: LazyLock<Regex> = LazyLock::new(|| py(r##"href="[^"#]*#([^"]+)""##));
/// a block boundary: text on either side is a separate passage
static BOUNDARY: LazyLock<Regex> = LazyLock::new(|| {
    py(r"</?(?:p|li|ul|ol|h[1-6]|td|th|tr|table|dd|dt|dl|blockquote|div|section)\b[^>]*>")
});
static SENTENCE_END: LazyLock<Regex> = LazyLock::new(|| py(r#"(?<=[.?!])\s+(?=[A-Z("'])"#));
/// tracked files outside the record that repeat a source or are the tooling's own logs (D7)
static SKIP_OUTSIDE: LazyLock<Regex> =
    LazyLock::new(|| py(r"^(research|tests)/|^dev/(bypass-log|run-log|perf-log)/"));
static RUN: LazyLock<Regex> = LazyLock::new(|| py(r"[A-Za-z0-9_-]+"));

fn drop(pattern: &Regex, text: &str) -> String {
    pattern.replace_all(text, "").into_owned()
}

fn finds<'t>(pattern: &Regex, text: &'t str) -> Vec<&'t str> {
    pattern
        .find_iter(text)
        .flatten()
        .map(|m| m.as_str())
        .collect()
}

fn splits<'t>(pattern: &Regex, text: &'t str) -> Vec<&'t str> {
    pattern.split(text).flatten().collect()
}

/// The text a reader sees: comments dropped, tags dropped, whitespace folded.
#[must_use]
pub fn visible(html: &str) -> String {
    collapse(&drop(&TAG, &drop(&COMMENT, html)))
}

fn sentences(text: &str) -> Vec<String> {
    splits(&SENTENCE_END, text)
        .into_iter()
        .map(strip)
        .filter(|s| !s.is_empty())
        .map(str::to_owned)
        .collect()
}

/// The question's text split at block boundaries, comments dropped, tags still in (a note's marker is a tag).
fn passages(html: &str) -> Vec<String> {
    let text = drop(&COMMENT, html);
    splits(&BOUNDARY, &text)
        .into_iter()
        .filter(|p| !strip(p).is_empty())
        .map(str::to_owned)
        .collect()
}

/// Each sentence of the question's visible text carrying a GUESS label, once however many it carries.
fn guess_sentences(html: &str) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for inner in passages(html) {
        for s in sentences(&visible(&inner)) {
            if guessed(&s) && !out.contains(&s) {
                out.push(s);
            }
        }
    }
    out
}

/// The sentence of the question that carries the note `key`, or "" when none does.
fn claim_of(html: &str, key: &str) -> String {
    let mark = format!("data-note=\"{key}\"");
    for inner in passages(html) {
        let Some(at) = inner.find(&mark) else {
            continue;
        };
        let before = &inner[..inner[..at].rfind('<').unwrap_or(0)];
        let text = visible(before);
        return sentences(&text).pop().unwrap_or(text);
    }
    String::new()
}

/// One open item: a guess, an absence, or an absence searched twice and settled.
#[derive(Debug, Clone, PartialEq, Eq)]
struct Item {
    kind: &'static str,
    text: String,
    claim: String,
}

/// One question page and what it holds open.
#[derive(Debug, Clone, PartialEq, Eq)]
struct Question {
    page: String,
    anchor: String,
    heading: String,
    path: String,
    links: BTreeSet<String>,
    items: Vec<Item>,
}

/// What a report groups a question by: its primary subject, read from its own tags or, for a drawing page, from the research page of its
/// stem; `untagged` when neither states one.
fn subject_of(path: &Path) -> String {
    let name = path
        .file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
    let research = path.with_file_name(name.replace(".drawing.html", ".html"));
    for candidate in [path, research.as_path()] {
        if let Some(text) = read(candidate) {
            if let Ok(Some(m)) = TAGS.captures(&text) {
                return m[1].to_owned();
            }
        }
    }
    "untagged".to_owned()
}

/// A file's text as Python's `read_text` gives it, or None where it is no UTF-8 file.
fn read(path: &Path) -> Option<String> {
    path.is_file()
        .then(|| l7r_gate_core::record::read_text(path).ok())
        .flatten()
}

fn read_question(path: &Path, root: &Path) -> Option<Question> {
    let html = read(path).unwrap_or_default();
    let m = HEADING.captures(&html).ok().flatten()?;
    let plain = drop(&COMMENT, &html);
    let mut q = Question {
        page: subject_of(path),
        anchor: m[1].to_owned(),
        heading: visible(&m[2]),
        path: path
            .strip_prefix(root)
            .unwrap_or(path)
            .to_string_lossy()
            .into_owned(),
        links: LINK
            .captures_iter(&plain)
            .flatten()
            .map(|c| c[1].to_owned())
            .collect(),
        items: guess_sentences(&html)
            .into_iter()
            .map(|text| Item {
                kind: "guess",
                text,
                claim: String::new(),
            })
            .collect(),
    };
    let name = path
        .file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
    let notes = path.with_file_name(format!(
        "{}.notes.html",
        &name[..name.len() - ".html".len()]
    ));
    if let Some(text) = read(&notes) {
        for c in NOTE_LI.captures_iter(&drop(&COMMENT, &text)).flatten() {
            let item = visible(&c[2]);
            if item.contains(ABSENCE) {
                let kind = if SETTLED.is_match(&item).unwrap_or(false) {
                    "absence-settled"
                } else {
                    "absence"
                };
                q.items.push(Item {
                    kind,
                    claim: claim_of(&html, &c[1]),
                    text: item,
                });
            }
        }
    }
    Some(q)
}

fn questions(root: &Path) -> Vec<Question> {
    let base = root.join("research").join("questions");
    let mut names: Vec<String> = std::fs::read_dir(&base)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| {
            std::path::Path::new(n)
                .extension()
                .is_some_and(|x| x == "html")
        })
        .collect();
    names.sort();
    names
        .into_iter()
        .filter(|n| {
            !n.ends_with(".notes.html")
                && !n.ends_with(".originals.html")
                && FRAGMENT.is_match(n).unwrap_or(false)
        })
        .filter_map(|n| read_question(&base.join(n), root))
        .collect()
}

/// anchor -> the classes a question feeds: its own (`Entry:` names it) and, one hop, those of a question that links to it.
fn class_routes(
    entries: &BTreeMap<String, Vec<String>>,
    qs: &[Question],
) -> HashMap<String, Vec<String>> {
    let mut direct: Vec<(String, Vec<String>)> = Vec::new();
    for (key, anchors) in entries {
        for a in anchors {
            match direct.iter_mut().find(|(d, _)| d == a) {
                Some(slot) => slot.1.push(key.clone()),
                None => direct.push((a.clone(), vec![key.clone()])),
            }
        }
    }
    let by_anchor: HashMap<&str, &Question> = qs.iter().map(|q| (q.anchor.as_str(), q)).collect();
    let mut out: HashMap<String, Vec<String>> = direct.iter().cloned().collect();
    for (a, ks) in &direct {
        let Some(src) = by_anchor.get(a.as_str()) else {
            continue;
        };
        for target in &src.links {
            if target == a || !by_anchor.contains_key(target.as_str()) {
                continue;
            }
            for k in ks {
                let label = format!("{k} (through '{}')", src.heading);
                let have = out.entry(target.clone()).or_default();
                if !have.contains(k) && !have.contains(&label) {
                    have.push(label);
                }
            }
        }
    }
    out
}

/// What a code comment quotes of a heading: the question up to its first '?'.
fn heading_key(question: &str) -> String {
    match question.split_once('?') {
        Some((head, _)) => format!("{head}?"),
        None => question.to_owned(),
    }
}

/// `file:line` of every engine line quoting the question's anchor or its heading.
fn code_citations(sources: &[(&str, &str)], anchor: &str, key: &str) -> Vec<String> {
    let mut out = Vec::new();
    for (path, text) in sources {
        if !text.contains(anchor) && (key.is_empty() || !text.contains(key)) {
            continue;
        }
        for (n, line) in l7r_gate_core::record::py_lines(text)
            .into_iter()
            .enumerate()
        {
            if line.contains(anchor) || (!key.is_empty() && line.contains(key)) {
                out.push(format!("{path}:{}", n + 1));
            }
        }
    }
    out
}

/// [`code_citations`] of every question without scanning the whole engine once per question (feature 321, 2026-10-04: that scan was
/// memory-bound and took the target past its bound). Exact: a needle's occurrence holds its longest identifier run, so only the files
/// holding that run may quote it; a needle with no run is looked for in every file.
fn cite_all(
    sources: &[(String, String)],
    qs: &[&Question],
    keys: &HashMap<String, String>,
) -> HashMap<String, Vec<String>> {
    let mut run_files: HashMap<&str, BTreeSet<usize>> = HashMap::new();
    for (i, (_, t)) in sources.iter().enumerate() {
        for r in finds(&RUN, t) {
            run_files.entry(r).or_default().insert(i);
        }
    }
    // the distinct runs joined by a newline, as the Python joined them: one scan of the blob per needle finds every run holding it
    let runs: Vec<&str> = run_files.keys().copied().collect();
    let mut blob = String::new();
    let mut starts = Vec::with_capacity(runs.len());
    for r in &runs {
        starts.push(blob.len());
        blob.push_str(r);
        blob.push('\n');
    }
    let may_hold = |needle: &str| -> HashSet<usize> {
        let words = finds(&RUN, needle);
        let Some(longest) = words
            .iter()
            .copied()
            .reduce(|a, b| if b.len() > a.len() { b } else { a })
        else {
            return (0..sources.len()).collect();
        };
        blob.match_indices(longest)
            .map(|(at, _)| starts.partition_point(|s| *s <= at) - 1)
            .flat_map(|i| run_files[runs[i]].iter().copied())
            .collect()
    };
    let mut out = HashMap::new();
    for q in qs {
        let key = keys.get(&q.anchor).cloned().unwrap_or_default();
        let mut files = may_hold(&q.anchor);
        if !key.is_empty() {
            files.extend(may_hold(&key));
        }
        let subset: Vec<(&str, &str)> = sources
            .iter()
            .enumerate()
            .filter(|(i, _)| files.contains(i))
            .map(|(_, (p, t))| (p.as_str(), t.as_str()))
            .collect();
        out.insert(q.anchor.clone(), code_citations(&subset, &q.anchor, &key));
    }
    out
}

fn outside_guesses(files: &[(String, String)]) -> Vec<(String, usize, String)> {
    let mut sorted: Vec<&(String, String)> = files.iter().collect();
    sorted.sort_by(|a, b| a.0.cmp(&b.0));
    let mut out = Vec::new();
    for (path, text) in sorted {
        if !guessed(text) {
            continue;
        }
        for (n, line) in l7r_gate_core::record::py_lines(text)
            .into_iter()
            .enumerate()
        {
            if guessed(line) {
                out.push((path.clone(), n + 1, strip(line).to_owned()));
            }
        }
    }
    out
}

/// The tracked files, as `git ls-files -z` lists them.
fn tracked(root: &Path) -> Vec<String> {
    let done = std::process::Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["ls-files", "-z"])
        .output();
    done.map(|d| {
        String::from_utf8_lossy(&d.stdout)
            .split('\0')
            .filter(|p| !p.is_empty())
            .map(str::to_owned)
            .collect()
    })
    .unwrap_or_default()
}

/// One question's lines in the report: the map features it touches, then each open item.
fn question_lines(
    q: &Question,
    routes: &HashMap<String, Vec<String>>,
    cites: &HashMap<String, Vec<String>>,
    lines: &mut Vec<String>,
) {
    let mut feeds: Vec<String> = routes.get(&q.anchor).cloned().unwrap_or_default();
    feeds.extend(cites.get(&q.anchor).cloned().unwrap_or_default());
    lines.push(format!(
        "   map features: {}",
        if feeds.is_empty() {
            "no map feature found depending on it".to_owned()
        } else {
            feeds.join("; ")
        }
    ));
    for it in &q.items {
        if it.kind == "guess" {
            lines.push(format!("   - GUESS: {}", it.text));
        } else {
            let tag = if it.kind == "absence-settled" {
                "UNSOURCED (searched twice, settled)"
            } else {
                "UNSOURCED"
            };
            let claim = if it.claim.is_empty() {
                "(the claim is not marked in the text)"
            } else {
                &it.claim
            };
            lines.push(format!("   - {tag}: {claim}"));
            lines.push(format!("       {}", it.text));
        }
    }
}

fn report(
    qs: &[Question],
    routes: &HashMap<String, Vec<String>>,
    cites: &HashMap<String, Vec<String>>,
    outside: &[(String, usize, String)],
) -> String {
    let mut pages: BTreeMap<&str, Vec<&Question>> = BTreeMap::new();
    for q in qs.iter().filter(|q| !q.items.is_empty()) {
        pages.entry(q.page.as_str()).or_default().push(q);
    }
    let mut lines: Vec<String> = vec![
        "OPEN RESEARCH QUESTIONS - read from the record and the tracked files now (feature 285)"
            .to_owned(),
        String::new(),
        format!(
            "{:<34} {:>9} {:>8} {:>9} {:>8}",
            "page", "questions", "guesses", "absences", "settled"
        ),
    ];
    let count = |pqs: &[&Question], kind: &str| {
        pqs.iter()
            .map(|q| q.items.iter().filter(|i| i.kind == kind).count())
            .sum::<usize>()
    };
    let mut tot = [0usize; 4];
    for (page, pqs) in &pages {
        let c = [
            count(pqs, "guess"),
            count(pqs, "absence"),
            count(pqs, "absence-settled"),
        ];
        lines.push(format!(
            "{page:<34} {:>9} {:>8} {:>9} {:>8}",
            pqs.len(),
            c[0],
            c[1],
            c[2]
        ));
        tot[0] += pqs.len();
        for (t, n) in tot[1..].iter_mut().zip(c) {
            *t += n;
        }
    }
    lines.push(format!(
        "{:<34} {:>9} {:>8} {:>9} {:>8}",
        "TOTAL", tot[0], tot[1], tot[2], tot[3]
    ));
    let mut areas: BTreeMap<&str, usize> = BTreeMap::new();
    for (path, _, _) in outside {
        *areas
            .entry(path.split('/').next().unwrap_or(path))
            .or_default() += 1;
    }
    lines.push(String::new());
    let listed: Vec<String> = areas.iter().map(|(a, n)| format!("{a} {n}")).collect();
    lines.push(format!(
        "GUESS lines outside the record: {} ({})",
        outside.len(),
        listed.join(", ")
    ));
    let rule = "=".repeat(100);
    for (page, pqs) in &pages {
        lines.extend([
            String::new(),
            rule.clone(),
            format!("subject: {page}"),
            rule.clone(),
        ]);
        for q in pqs {
            lines.extend([
                String::new(),
                format!("## {}", q.heading),
                format!("   {}", q.path),
            ]);
            question_lines(q, routes, cites, &mut lines);
        }
    }
    lines.extend([
        String::new(),
        rule.clone(),
        "GUESSES MARKED OUTSIDE THE RECORD".to_owned(),
        rule,
    ]);
    let mut last: Option<&str> = None;
    for (path, n, text) in outside {
        if last != Some(path.as_str()) {
            lines.extend([String::new(), path.clone()]);
            last = Some(path);
        }
        lines.push(format!("   {n}: {text}"));
    }
    lines.join("\n") + "\n"
}

/// The report over the tree at `root`.
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "the Python's `rel.endswith(\".py\")`, which this port keeps, is case-sensitive"
)]
///
/// # Errors
/// The hamlet registry not loading (the Python's import error).
pub fn run(root: &Path) -> Result<String> {
    let classes = classes(root)?;
    let research = root.join("research");
    let qs = questions(root);
    // a question's link is its small page in the record's site, named for its anchor (feature 301), and the DRAWING pages a modal rests
    // on, listed under `Drawing:` since feature 319 (plan D13): reading the entry alone left every drawing page unrouted
    let entries: BTreeMap<String, Vec<String>> = classes
        .iter()
        .map(|fc| {
            let named: Vec<&str> = [fc.entry.as_str(), fc.drawing.as_str()]
                .into_iter()
                .filter(|p| !p.is_empty())
                .collect();
            let anchors = research_questions(&named.join(", "), &research)
                .into_iter()
                .map(|q| {
                    let tail = q.url.rsplit_once('/').map_or(q.url.as_str(), |p| p.1);
                    tail.strip_suffix(".html").unwrap_or(tail).to_owned()
                })
                .collect();
            (fc.key.clone(), anchors)
        })
        .collect();
    let routes = class_routes(&entries, &qs);
    let names = tracked(root);
    let engine: Vec<(String, String)> = names
        .iter()
        .filter(|r| r.starts_with("l7r/") && r.ends_with(".py"))
        .filter_map(|r| read(&root.join(r)).map(|t| (r.clone(), t)))
        .collect();
    let open: Vec<&Question> = qs.iter().filter(|q| !q.items.is_empty()).collect();
    let keys: HashMap<String, String> = open
        .iter()
        .map(|q| (q.anchor.clone(), heading_key(&question_text(&q.heading))))
        .collect();
    let cites = cite_all(&engine, &open, &keys);
    let outside: Vec<(String, String)> = names
        .iter()
        .filter(|r| !SKIP_OUTSIDE.is_match(r).unwrap_or(false))
        .filter_map(|r| read(&root.join(r)).map(|t| (r.clone(), t)))
        .collect();
    Ok(report(&qs, &routes, &cites, &outside_guesses(&outside)))
}

/// `l7r-gate record open-questions --root <dir>`: the report on stdout (`open_questions.py`'s own command line).
#[must_use]
pub fn cli(args: &[String]) -> l7r_gate_core::Reply {
    let reply = |stdout: String, stderr: String, code: i32| l7r_gate_core::Reply {
        stdout,
        stderr,
        code,
    };
    let root = match args {
        [flag, root] if flag == "--root" => root.as_str(),
        [one] if one.starts_with("--root=") => &one["--root=".len()..],
        _ => return reply(
            String::new(),
            "usage: l7r-gate record open-questions: the following arguments are required: --root\n"
                .to_owned(),
            2,
        ),
    };
    match run(&l7r_gate_research::resolve(Path::new(root))) {
        Ok(text) => reply(text, String::new(), 0),
        Err(e) => {
            let mut err = String::new();
            let _ = writeln!(err, "{}: {}", e.kind, e.message);
            reply(String::new(), err, 1)
        }
    }
}

#[cfg(test)]
mod tests;
