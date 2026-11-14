//! Feature 242's work list and feature 238's shares, derived from feature 238's four reader reports (feature 449 T139, from
//! `specs/242-cite-the-unfootnoted-assertions/measure/inventory_census.py` and `specs/238-unfootnoted-assertions-researched/measure/inventory_shares.py`,
//! `ask:449-phase3-remainder` Q4).
//!
//! One parser serves both, as the Python's 238 script loaded 242's by path rather than copy it: it is the one that reproduces all four
//! reports' own stated totals (171 / 203 / 153 / 168 = 695), which is what makes its marker split trustworthy at all. Where it disagrees
//! with the readers' own stated marker counts the disagreement is reported, and the wider bound is the one to plan with.

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::{repr, strip, SPACE_CLASS};
use l7r_guard::shared::pyjson::py_float;
use l7r_guard::shared::speckit::splitlines;
use serde_json::{json, Value};

use super::super::events::{re, read_text, Raised};
use super::super::turn_time::py_round;
use super::{command, record, Ran};

const REPORTS: &str = "specs/238-unfootnoted-assertions-researched/reader-reports";
const RECORD_242: &str = "specs/242-cite-the-unfootnoted-assertions/measurements.json";
const RECORD_238: &str = "specs/238-unfootnoted-assertions-researched/measurements.json";

/// What the four readers themselves stated, from feature 238's T02-T05 verify lines. The parser is only believable if it reproduces
/// these, so they are asserted rather than trusted.
const STATED_ITEMS: [(&str, usize); 4] = [
    ("religion-vegetation-and-urban-features.md", 171),
    ("the-city-pages.md", 203),
    ("water-fields-and-the-river-cities.md", 153),
    ("homesteads-buildings-and-the-hamlet-pages.md", 168),
];
const STATED_MARKED: usize = 34 + 59 + 51 + 67;

/// Closed by feature 238 in a class OTHER than the marker conversion (its research.md R7 items 2, 3, 5 and 6), so absent from the
/// successor's list though the items carry no marker. R7 item 4, the twelve defects, is deliberately not here: those were found in the
/// second reading, of material that already carried a footnote, so the two populations are disjoint by construction.
const CLOSED_BARE: [(&str, usize); 5] = [
    ("roster-hidden on urban-features", 9),
    ("roster-hidden on buildings", 5),
    ("sections disclosing with no footnote at all", 6),
    ("settlements.html, restating footnoted canon", 1),
    ("the caravan inn (one bare item, homesteads report 148)", 1),
];

/// The readers hedged some items with a compound label; those are their own tiers, since rounding a deliberate hedge in either direction
/// invents a judgment the reader declined to make.
const TIERS: [&str; 5] = ["HIGH", "MEDIUM-HIGH", "MEDIUM", "LOW-MEDIUM", "LOW"];

/// urban-features is the single heaviest page; its item count is stated in the reader's own report (238's shares).
const URBAN: usize = 103;

static SPLIT: LazyLock<Regex> = LazyLock::new(|| re(r"\n(?=\*\*[A-Z]{1,3}\d+[.*])"));
static LABEL: LazyLock<Regex> = LazyLock::new(|| re(r"\A\*\*[A-Z]{1,3}\d+[.*]"));
static NUMBERED: LazyLock<Regex> = LazyLock::new(|| re(&format!(r"\A\d+\.[{SPACE_CLASS}]")));
static CONFIDENT: LazyLock<Regex> = LazyLock::new(|| re(r"\*\*(HIGH|MEDIUM|LOW)\b"));
static TIER: LazyLock<Regex> =
    LazyLock::new(|| re(r"\*\*(HIGH|MEDIUM|LOW)(-(?:HIGH|MEDIUM|LOW))?\b"));
static PAGE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{1,3} .*?([A-Za-z0-9_/-]+\.html)"));
static NO_MARKER: LazyLock<Regex> = LazyLock::new(|| re(r"\bno marker\b"));
static MARKER_NONE: LazyLock<Regex> =
    LazyLock::new(|| re(&format!(r"marker:[{SPACE_CLASS}]*(none|no\b)")));
static MARKER: LazyLock<Regex> = LazyLock::new(|| re(r"\bmarker:"));

fn hit(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

/// One block per inventory item. Two shapes: a bold label, or a numbered list.
fn items(text: &str) -> Vec<String> {
    let (mut parts, mut last) = (Vec::new(), 0);
    for m in SPLIT.find_iter(text).flatten() {
        parts.push(&text[last..m.start()]);
        last = m.end();
    }
    parts.push(&text[last..]);
    let labeled: Vec<String> = parts
        .into_iter()
        .filter(|p| hit(&LABEL, p))
        .map(str::to_owned)
        .collect();
    if !labeled.is_empty() {
        return labeled;
    }
    let (mut out, mut cur): (Vec<String>, Option<String>) = (Vec::new(), None);
    for line in splitlines(text) {
        if hit(&NUMBERED, line) {
            out.extend(cur.replace(line.to_owned()));
        } else if let Some(block) = cur.as_mut().filter(|_| {
            !strip(line).is_empty() && !line.starts_with('#') && !line.starts_with("---")
        }) {
            block.push(' ');
            block.push_str(line);
        } else {
            out.extend(cur.take());
        }
    }
    out.extend(cur);
    // In the numbered reports a real inventory item always carries a confidence label; a numbered line in a closing summary does not.
    out.into_iter().filter(|b| hit(&CONFIDENT, b)).collect()
}

/// The research page an item belongs to: the nearest `# ` heading above it that names an `.html`.
fn page_of(text: &str) -> String {
    PAGE.captures_iter(text)
        .flatten()
        .last()
        .and_then(|c| c.get(1))
        .map(|g| {
            g.as_str()
                .rsplit("research/")
                .next()
                .unwrap_or_default()
                .to_owned()
        })
        .unwrap_or_default()
}

/// A block's tier: "HIGH-MEDIUM" named once as "MEDIUM-HIGH"; an unrecognized compound returned as it is, for the census to refuse.
fn confidence(block: &str) -> String {
    let Some(c) = TIER.captures(block).ok().flatten() else {
        return "unlabeled".to_owned();
    };
    let label = format!("{}{}", &c[1], c.get(2).map_or("", |g| g.as_str()));
    if TIERS.contains(&label.as_str()) {
        return label;
    }
    let reversed: Vec<&str> = label.split('-').rev().collect();
    let reversed = reversed.join("-");
    if TIERS.contains(&reversed.as_str()) {
        reversed
    } else {
        label
    }
}

/// Did the assertion carry an inline unsourced-class marker in the prose the reader quoted?
fn carries_marker(block: &str) -> bool {
    let low = block.to_lowercase();
    if hit(&NO_MARKER, &low) || hit(&MARKER_NONE, &low) {
        return false;
    }
    hit(&MARKER, &low)
        || low.contains("unsourced")
        || low.contains("is a guess")
        || low.contains("they are a guess")
}

/// `sorted(REPORTS.glob("*.md"))`, each with its text.
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "`glob(\"*.md\")` is case-sensitive and matches a file named `.md`, which `Path::extension` would not"
)]
fn reports(root: &Path) -> Result<Vec<(String, String)>, Raised> {
    let mut paths: Vec<PathBuf> = std::fs::read_dir(root.join(REPORTS))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| {
            p.file_name()
                .and_then(|n| n.to_str())
                .is_some_and(|n| n.ends_with(".md"))
        })
        .collect();
    paths.sort();
    paths
        .iter()
        .map(|p| {
            let name = p.file_name().unwrap_or_default().to_string_lossy();
            Ok((name.into_owned(), read_text(p)?))
        })
        .collect()
}

/// A tally in first-seen order, as a `Counter` keeps it.
#[derive(Default)]
struct Tally(Vec<(String, usize)>);

impl Tally {
    fn add(&mut self, key: &str) {
        match self.0.iter_mut().find(|(k, _)| k == key) {
            Some(row) => row.1 += 1,
            None => self.0.push((key.to_owned(), 1)),
        }
    }

    fn of(&self, key: &str) -> usize {
        self.0.iter().find(|(k, _)| k == key).map_or(0, |r| r.1)
    }

    fn hedged(&self) -> usize {
        self.0
            .iter()
            .filter(|(k, _)| k.contains('-'))
            .map(|r| r.1)
            .sum()
    }
}

#[expect(
    clippy::cast_precision_loss,
    reason = "an item count as Python's true division converts it"
)]
fn share(n: usize, total: usize) -> Result<f64, Raised> {
    if total == 0 {
        return Err("ZeroDivisionError: division by zero".to_owned());
    }
    Ok(py_round((100 * n) as f64 / total as f64, 1))
}

/// `--per-page`: bare items per research page, the shape feature 242's task file is written from.
fn per_page(root: &Path, out: &mut String) -> Ran {
    let mut pages = Tally::default();
    for (_, text) in reports(root)? {
        for block in items(&text) {
            if carries_marker(&block) {
                continue;
            }
            let head: String = block.chars().take(120).collect();
            let upto = text
                .find(&head)
                .ok_or_else(|| "ValueError: substring not found".to_owned())?;
            pages.add(&page_of(&text[..upto]));
        }
    }
    let mut rows = pages.0;
    rows.sort_by(|a, b| b.1.cmp(&a.1));
    for (page, n) in &rows {
        let _ = writeln!(out, "{n:5}  {page}");
    }
    let _ = writeln!(out, "{:5}  TOTAL", rows.iter().map(|r| r.1).sum::<usize>());
    Ok(0)
}

fn entry(cmd: &str, note: &str, unit: &str, value: impl Into<Value>) -> Value {
    json!({"command": cmd, "note": note, "taken": "2026-09-13", "unit": unit, "value": value.into()})
}

/// `l7r-gate measure spec 242 inventory-census [--record | --per-page]`.
pub(super) fn census(args: &[String], root: &Path, out: &mut String) -> Ran {
    if args.iter().any(|a| a == "--per-page") {
        return per_page(root, out);
    }
    let mut per_report: BTreeMap<String, (usize, usize)> = BTreeMap::new();
    let (mut bare_conf, mut all_conf) = (Tally::default(), Tally::default());
    let (mut total, mut marked, mut hedged_and_closed) = (0, 0, 0);
    for (name, text) in reports(root)? {
        let blocks = items(&text);
        let m = blocks.iter().filter(|b| carries_marker(b)).count();
        for b in &blocks {
            let tier = confidence(b);
            all_conf.add(&tier);
            if !carries_marker(b) {
                bare_conf.add(&tier);
                // of the closures, only the caravan inn is identifiable in the reports, so the hedged share is bounded, not fixed
                if b.to_lowercase().contains("caravan inn") && tier.contains('-') {
                    hedged_and_closed += 1;
                }
            }
        }
        per_report.insert(name, (blocks.len(), m));
        total += blocks.len();
        marked += m;
    }
    for (name, want) in STATED_ITEMS {
        let got = per_report
            .get(name)
            .ok_or_else(|| format!("KeyError: {}", repr(name)))?
            .0;
        if got != want {
            let _ = writeln!(
                out,
                "PARSE DISAGREES with the report's own total: {name} {got} != {want}"
            );
            return Ok(1);
        }
    }
    let bare_parsed = total - marked;
    let bare_stated = signed(total) - signed(STATED_MARKED);
    let closed: usize = CLOSED_BARE.iter().map(|c| c.1).sum();
    let _ = writeln!(
        out,
        "{:46}{:>6}{:>8}{:>6}",
        "report", "items", "marked", "bare"
    );
    for (name, (n, m)) in &per_report {
        let cut: String = name.chars().take(44).collect();
        let _ = writeln!(out, "{cut:46}{n:6}{m:8}{:6}", n - m);
    }
    let _ = writeln!(out, "{}", "-".repeat(66));
    let _ = writeln!(out, "{:46}{total:6}{marked:8}{bare_parsed:6}", "TOTAL");
    let _ = writeln!(out);
    let _ = writeln!(
        out,
        "bare by the readers' own marker counts ({STATED_MARKED} marked): {bare_stated}"
    );
    let _ = writeln!(
        out,
        "bare by this parse ({marked} marked):                {bare_parsed}"
    );
    // over EVERY item, not just the bare ones: the hedged total is taken over all of them, so a stray tier on a marked item would
    // corrupt a recorded figure just as silently. (The Python's next check, that the tiers sum to the bare count, cannot fail once no
    // tier is stray, every bare tier being one of TIERS, so it is not carried.)
    let mut stray: Vec<&str> = all_conf
        .0
        .iter()
        .map(|r| r.0.as_str())
        .filter(|t| !TIERS.contains(t))
        .collect();
    if !stray.is_empty() {
        stray.sort_unstable();
        let shown: Vec<String> = stray.iter().map(|t| repr(t)).collect();
        let _ = writeln!(
            out,
            "UNRECOGNIZED confidence tier(s) [{}] - the printed composition would drop them",
            shown.join(", ")
        );
        return Ok(1);
    }
    let closures: Vec<String> = CLOSED_BARE
        .iter()
        .map(|(k, v)| format!("{k} {v}"))
        .collect();
    let _ = writeln!(
        out,
        "closed by 238 in a non-marker class:                 {closed} ({})",
        closures.join(", ")
    );
    let (hedged_all, hedged_bare) = (all_conf.hedged(), bare_conf.hedged());
    let counted = Counted {
        total,
        marked,
        bare_parsed,
        bare_stated,
        closed,
        bare_conf,
        hedged_all,
        hedged_bare,
        hedged_and_closed,
    };
    summary(&counted, args, root, out)
}

/// What the census counted, for its closing lines and its figures.
struct Counted {
    total: usize,
    marked: usize,
    bare_parsed: usize,
    bare_stated: i64,
    closed: usize,
    bare_conf: Tally,
    hedged_all: usize,
    hedged_bare: usize,
    hedged_and_closed: usize,
}

/// The census's work list, its tiers and hedges, and under `--record` its twelve figures.
fn summary(c: &Counted, args: &[String], root: &Path, out: &mut String) -> Ran {
    let Counted {
        total,
        marked,
        bare_parsed,
        bare_stated,
        closed,
        ref bare_conf,
        hedged_all,
        hedged_bare,
        hedged_and_closed,
    } = *c;
    let _ = writeln!(
        out,
        "WORK LIST: {} to {} items",
        bare_stated - signed(closed),
        signed(bare_parsed) - signed(closed)
    );
    let tiers: Vec<String> = TIERS
        .iter()
        .map(|t| format!("{t} {}", bare_conf.of(t)))
        .collect();
    let _ = writeln!(
        out,
        "  of the parsed remainder, by the readers' own confidence tiers: {}",
        tiers.join(", ")
    );
    let _ = writeln!(out, "  hedged with a compound label: {hedged_all} of the {total} inventoried, {hedged_bare} of the {bare_parsed} bare, at most {} on the work list (the caravan inn is hedged and is one of the {closed} closures)", hedged_bare - hedged_and_closed);
    if args.iter().any(|a| a == "--record") {
        let cmd = command("242", "inventory-census", " --record");
        let path = root.join(RECORD_242);
        let disagree = marked.abs_diff(STATED_MARKED);
        record(&path, vec![
            ("inventory-items", entry(&cmd, "every sentence the four readers named; reproduces each report's own stated total", "items", total)),
            ("worklist-low", entry(&cmd, "the remainder using the readers' own marker counts, less the classes 238 closed by hand", "items", bare_stated - signed(closed))),
            ("worklist-high", entry(&cmd, "the same, using this parser's marker classification - the wider bound", "items", signed(bare_parsed) - signed(closed))),
            ("worklist-high-confidence", entry(&cmd, "of the parsed remainder, the readers' HIGH confidence share", "items", bare_conf.of("HIGH"))),
            ("worklist-medium-high-confidence", entry(&cmd, "the readers' hedged MEDIUM-HIGH share, reported as its own tier rather than rounded", "items", bare_conf.of("MEDIUM-HIGH"))),
            ("worklist-medium-confidence", entry(&cmd, "the MEDIUM share", "items", bare_conf.of("MEDIUM"))),
            ("worklist-low-medium-confidence", entry(&cmd, "the readers' hedged LOW-MEDIUM share", "items", bare_conf.of("LOW-MEDIUM"))),
            ("worklist-low-confidence", entry(&cmd, "the LOW share", "items", bare_conf.of("LOW"))),
            ("marker-classifier-disagreement", entry(&cmd, "items this parser and the readers' own stated splits classify differently", "items", disagree)),
            ("hedged-items", entry(&cmd, "inventoried items the readers gave a compound confidence label, over all of them", "items", hedged_all)),
            ("hedged-bare", entry(&cmd, "the hedged share of the bare population", "items", hedged_bare)),
            ("hedged-worklist-max", entry(&cmd, "an upper bound on the hedged share of the work list: only the caravan inn is identifiable among the closures, so the other twenty-one cannot be checked for hedges", "items", hedged_bare - hedged_and_closed)),
        ])?;
        let _ = writeln!(out, "\nrecorded to {}", path.display());
    }
    Ok(0)
}

/// A count as Python's int, which goes below zero where a difference does (the readers' stated marker total is not asserted).
fn signed(n: usize) -> i64 {
    i64::try_from(n).unwrap_or(i64::MAX)
}

/// `l7r-gate measure spec 238 inventory-shares [--record]`: the shares feature 238's research record states, derived, since R3b stated
/// them by hand and three of the four were wrong.
pub(super) fn shares(args: &[String], root: &Path, out: &mut String) -> Ran {
    let mut tiers = Tally::default();
    let (mut total, mut bare) = (0, 0);
    for (_, text) in reports(root)? {
        for block in items(&text) {
            total += 1;
            tiers.add(&confidence(&block));
            if !carries_marker(&block) {
                bare += 1;
            }
        }
    }
    let shares = [
        ("urban-features-share", share(URBAN, total)?),
        ("high-share", share(tiers.of("HIGH"), total)?),
        (
            "high-share-with-hedged",
            share(tiers.of("HIGH") + tiers.of("MEDIUM-HIGH"), total)?,
        ),
        ("unmarked-share", share(bare, total)?),
    ];
    let _ = writeln!(out, "{total} inventoried items, {bare} carrying no marker");
    for tier in TIERS {
        let _ = writeln!(out, "  {tier:12} {:4}", tiers.of(tier));
    }
    for (name, value) in shares {
        let _ = writeln!(out, "  {name:24} {}%", py_float(value));
    }
    if args.iter().any(|a| a == "--record") {
        let cmd = command("238", "inventory-shares", " --record");
        let urban = format!("urban-features.html's {URBAN} items as a share of all {total}");
        let notes = [
            urban.as_str(),
            "items the readers rated HIGH, as a share of all of them",
            "the same counting the hedged MEDIUM-HIGH tier as HIGH - the upper reading, and why the hedge is reported rather than rounded",
            "items carrying no inline marker of any kind",
        ];
        let path = root.join(RECORD_238);
        record(
            &path,
            shares
                .iter()
                .zip(notes)
                .map(|((name, value), note)| (*name, entry(&cmd, note, "%", *value)))
                .collect(),
        )?;
        let _ = writeln!(out, "\nrecorded to {}", path.display());
    }
    Ok(0)
}

#[cfg(test)]
mod tests;
