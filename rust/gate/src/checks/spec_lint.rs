//! The things a review round kept finding in a spec that a script can find for nothing (feature 236; feature 449 T066, from
//! `spec-lint.py`). Twenty `spec-fidelity` rounds over two features cost 91 minutes (observed 2026-09-12, method: the review ledger),
//! and at least eight of their findings were mechanical.
//!
//! Check 1 is a measured figure with no pointer to the research; check 2 a withdrawn figure still standing anywhere in the tree (the reach is the
//! tree, feature 236's amendment: *"You should do the tree wide scan instead of leaving this half done"*); check 3 an orphaned
//! requirement; check 4 a stale task list; check 5 a measured figure not derived from its record (`spec_figures`); check 6 a feature
//! numbered 377 or above with no approval line, in the commit guard's own form; check 7 a task id on two task lines.
//!
//! Checks 1, 3, 4 and 7 need a `tasks.md`: a freshly claimed spec has none, and the protocol requires pushing that shape.

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use l7r_guard::guards::feature_approval_hooks::{
    form_problem, FIRST as APPROVAL_FIRST, FORM as APPROVAL_FORM,
};
use serde_json::Value;

use super::spec_figures::{check_measured_figures, figure_source, is_check5, FIGURE};
use super::{git_text, py_lines, py_repr, scratch, Outcome};

/// Each run is recorded for `make tool-yield`, as `usage_log` records a Python tool's.
pub(super) const USAGE_LOG_TOOL: &str = "spec-lint";
const CHECK6_MARK: &str = "the GM's approval line";
const BINARY_SUFFIXES: [&str; 15] = [
    "png", "jpg", "jpeg", "webp", "pdf", "gif", "ico", "woff", "woff2", "ttf", "zip", "gz", "prof",
    "pyc", "svg",
];
const FIGURE_SECTIONS: [&str; 4] = [
    "summary",
    "functional requirements",
    "success criteria",
    "decisions recorded",
];
const NARRATING_SECTIONS: [&str; 2] = ["decisions recorded", "review history"];

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static POINTER: LazyLock<Regex> =
    LazyLock::new(|| re(r"\bR\d+\b|research\.md|research/[\w.-]+\.md"));
static ID: LazyLock<Regex> = LazyLock::new(|| re(r"\b(FR|SC)-(\d{3}[a-z]?)\b"));
static RANGE: LazyLock<Regex> =
    LazyLock::new(|| re(r"\bFR-(\d{3})[a-z]?\s*(?:-|to)\s*FR-(\d{3})[a-z]?\b"));
static DEF: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^(?:[-*+]\s+)?\*\*(FR|SC)-(\d{3}[a-z]?)(?=\*\*|[ .:])[^*]*\*\*"));
static HEADING: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^##+\s+(.*?)\s*$"));
static WITHDRAWN: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^\s*(?:[-*+]\s+)?WITHDRAWN:\s*(.+?)\s*$"));
static RECORDS: LazyLock<Regex> =
    LazyLock::new(|| re(r"(^|/)(tests/hooks/fixtures|dev/[\w-]*-log)/"));
static CRITERION: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^(?:[-*+]\s+)?\*\*(SC-\d{3}[a-z]?)(?=\*\*|[ .:])[^*]*\*\*(.*)$"));
static NAMED_ELSEWHERE: LazyLock<Regex> = LazyLock::new(|| re(r"\b\d{3}(?:'s)?\s+$"));
static TASK_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"^- \[[ xX]\] (T\d+[a-z]?)\b"));
static LOCATION: LazyLock<Regex> = LazyLock::new(|| re(r"\S+:\d+:?\s?"));

fn read(path: &Path) -> String {
    std::fs::read_to_string(path).unwrap_or_default()
}

fn line_at(text: &str, at: usize) -> usize {
    text[..at].matches('\n').count() + 1
}

fn level_of(heading: &str) -> usize {
    heading.len() - heading.trim_start_matches('#').len()
}

fn def_id(c: &Captures<'_>) -> String {
    format!("{}-{}", &c[1], &c[2])
}

/// Each heading's name (a sub-heading carries its parent's in front, so a section reaches its subtree), its line, and its body.
fn sections(text: &str) -> Vec<(String, usize, &str)> {
    let marks: Vec<Captures<'_>> = HEADING.captures_iter(text).flatten().collect();
    let mut top = String::new();
    let mut out = Vec::new();
    for (i, m) in marks.iter().enumerate() {
        let whole = m.get(0).map_or((0, 0), |g| (g.start(), g.end()));
        let name = m[1].to_lowercase();
        let level = level_of(&m[0]);
        if level <= 2 {
            top.clone_from(&name);
        }
        let end = marks
            .get(i + 1)
            .and_then(|n| n.get(0))
            .map_or(text.len(), |g| g.start());
        let shown = if level <= 2 || top.is_empty() {
            name
        } else {
            format!("{top} > {name}")
        };
        out.push((
            shown,
            text[..whole.1].matches('\n').count() + 1,
            &text[whole.1..end],
        ));
    }
    out
}

/// Check 1: a measured figure whose method the reader cannot reach.
fn check_figures(spec: &Path) -> Vec<String> {
    let text = read(spec);
    let mut bad = Vec::new();
    for (name, start, body) in sections(&text) {
        if !FIGURE_SECTIONS.iter().any(|s| name.starts_with(s)) {
            continue;
        }
        let mut line = start;
        for para in body.split("\n\n") {
            if let Ok(Some(found)) = FIGURE.find(para) {
                if !POINTER.is_match(para).unwrap_or(false) {
                    let n = line + para[..found.start()].matches('\n').count();
                    bad.push(format!("{}:{n}: the figure {} states a measurement with no pointer to the research (`R<k>` or `research.md`) in its paragraph", spec.display(), py_repr(&Value::from(found.as_str().trim()))));
                }
            }
            line += para.matches('\n').count() + 2;
        }
    }
    bad
}

/// The ranges of the sections that exist to narrate a reversal, each to the next heading of its level or above.
fn exempt_spans(text: &str) -> Vec<(usize, usize)> {
    let marks: Vec<Captures<'_>> = HEADING.captures_iter(text).flatten().collect();
    let mut spans = Vec::new();
    for (i, m) in marks.iter().enumerate() {
        let title = m[1].to_lowercase();
        if !NARRATING_SECTIONS.iter().any(|s| title.starts_with(s)) {
            continue;
        }
        let level = level_of(&m[0]);
        let end = marks[i + 1..]
            .iter()
            .find(|n| level_of(&n[0]) <= level)
            .and_then(|n| n.get(0))
            .map_or(text.len(), |g| g.start());
        spans.push((m.get(0).map_or(0, |g| g.start()), end));
    }
    spans
}

fn walk(dir: &Path, out: &mut Vec<PathBuf>) {
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let path = entry.path();
        if path.is_dir() && !path.is_symlink() {
            if entry.file_name() != ".clones" {
                walk(&path, out);
            }
        } else {
            out.push(path);
        }
    }
}

/// Every text file a withdrawn figure could be standing in: what git tracks or would keep, or, off a git tree, a walk.
fn scanned_files(tree_root: &Path) -> Vec<PathBuf> {
    let listed = git_text(
        tree_root,
        &["ls-files", "--cached", "--others", "--exclude-standard"],
    );
    let mut paths: Vec<PathBuf> = listed
        .lines()
        .filter(|n| !n.is_empty())
        .map(|n| tree_root.join(n))
        .collect();
    if paths.is_empty() {
        walk(tree_root, &mut paths);
        paths.sort();
    }
    paths.retain(|p| {
        let suffix = p
            .extension()
            .map(|e| e.to_string_lossy().to_lowercase())
            .unwrap_or_default();
        !BINARY_SUFFIXES.contains(&suffix.as_str())
            && !RECORDS.is_match(&p.to_string_lossy()).unwrap_or(true)
            && p.is_file()
    });
    paths
}

/// What a marker's own text must be: twelve characters and a letter, so a bare number can never be banned.
fn marker_text(raw: &str) -> &str {
    raw.trim().trim_matches(['`', '"', '\''])
}

/// Check 2: text this feature withdrew, still standing anywhere in the tree. One read per file, every marker asked of it.
fn check_withdrawn(spec_dir: &Path, tree_root: &Path) -> Vec<String> {
    let research = spec_dir.join("research.md");
    if !research.is_file() {
        return Vec::new();
    }
    let source = read(&research);
    let (mut bad, mut marked) = (Vec::new(), Vec::new());
    for m in WITHDRAWN.captures_iter(&source).flatten() {
        let text = marker_text(&m[1]);
        let n = line_at(&source, m.get(0).map_or(0, |g| g.start()));
        if text.chars().count() < 12 || !text.chars().any(|c| c.is_ascii_alphabetic()) {
            bad.push(format!("{}:{n}: `WITHDRAWN:` needs at least twelve characters and a letter - {} would ban a bare figure from the whole record", research.display(), py_repr(&Value::from(text))));
        } else {
            marked.push((text.to_owned(), n));
        }
    }
    let files = if marked.is_empty() {
        Vec::new()
    } else {
        scanned_files(tree_root)
    };
    for path in files.iter().filter(|p| **p != research) {
        let data = std::fs::read(path).unwrap_or_default();
        let body = String::from_utf8_lossy(&data);
        if body.chars().take(8192).any(|c| c == '\0') {
            continue;
        }
        let spans = std::cell::OnceCell::new();
        for (text, n) in &marked {
            for (at, _) in body.match_indices(text.as_str()) {
                let narrated: &Vec<(usize, usize)> = spans.get_or_init(|| exempt_spans(&body));
                if !narrated.iter().any(|(a, b)| *a <= at && at < *b) {
                    bad.push(format!(
                        "{}:{}: withdrawn text still standing here - {}:{n} marks {} as superseded",
                        path.display(),
                        line_at(&body, at),
                        research.display(),
                        py_repr(&Value::from(text.as_str()))
                    ));
                }
            }
        }
    }
    bad.sort();
    bad
}

/// Check 3: a requirement no criterion covers, or a criterion covering nothing.
fn check_orphans(spec: &Path) -> Vec<String> {
    let text = read(spec);
    let frs: BTreeSet<String> = DEF
        .captures_iter(&text)
        .flatten()
        .filter(|c| &c[1] == "FR")
        .map(|c| def_id(&c))
        .collect();
    let mut bad = Vec::new();
    let mut covered: BTreeSet<String> = BTreeSet::new();
    for (name, start, body) in sections(&text) {
        if !name.starts_with("success criteria") {
            continue;
        }
        let mut line = start;
        for para in body.split("\n\n") {
            for sc in CRITERION.captures_iter(para).flatten() {
                let mut named: BTreeSet<String> = ID
                    .captures_iter(&sc[2])
                    .flatten()
                    .filter(|c| &c[1] == "FR")
                    .map(|c| def_id(&c))
                    .collect();
                for range in RANGE.captures_iter(&sc[2]).flatten() {
                    let (lo, hi): (u32, u32) =
                        (range[1].parse().unwrap_or(0), range[2].parse().unwrap_or(0));
                    named.extend(
                        frs.iter()
                            .filter(|fr| (lo..=hi).contains(&fr[3..6].parse().unwrap_or(0)))
                            .cloned(),
                    );
                }
                if named.is_empty() && !sc[2].contains("(spec-wide)") {
                    let n = line
                        + para[..sc.get(0).map_or(0, |g| g.start())]
                            .matches('\n')
                            .count();
                    bad.push(format!(
                        "{}:{n}: {} names no FR and is not marked `(spec-wide)`",
                        spec.display(),
                        &sc[1]
                    ));
                }
                covered.extend(named);
            }
            line += para.matches('\n').count() + 2;
        }
    }
    let defs: BTreeMap<String, usize> = DEF.captures_iter(&text).flatten().rev_first();
    for fr in frs.difference(&covered) {
        bad.push(format!(
            "{}:{}: {fr} is named by no success criterion",
            spec.display(),
            line_at(&text, defs[fr])
        ));
    }
    bad
}

/// The first offset of each id a spec declares.
trait RevFirst {
    fn rev_first(self) -> BTreeMap<String, usize>;
}

impl<'t, I: Iterator<Item = Captures<'t>>> RevFirst for I {
    fn rev_first(self) -> BTreeMap<String, usize> {
        let mut out = BTreeMap::new();
        for c in self {
            out.entry(def_id(&c))
                .or_insert(c.get(0).map_or(0, |g| g.start()));
        }
        out
    }
}

/// The sixteen characters before `at`.
fn before(body: &str, at: usize) -> &str {
    let from = body[..at]
        .char_indices()
        .rev()
        .nth(15)
        .map_or(0, |(i, _)| i);
    &body[from..at]
}

/// Check 4: a task list citing an id the spec does not have; another feature's requirement, named by its feature, is not this spec's.
fn check_stale_tasks(spec: &Path, tasks: &Path) -> Vec<String> {
    let spec_text = read(spec);
    let have: BTreeSet<String> = DEF
        .captures_iter(&spec_text)
        .flatten()
        .map(|c| def_id(&c))
        .collect();
    let body = read(tasks);
    let mut bad = Vec::new();
    for m in ID.find_iter(&body).flatten() {
        if !NAMED_ELSEWHERE
            .is_match(before(&body, m.start()))
            .unwrap_or(false)
            && !have.contains(m.as_str())
        {
            let spec_name = spec.file_name().unwrap_or_default().to_string_lossy();
            bad.push(format!(
                "{}:{}: cites {}, which {spec_name} does not define",
                tasks.display(),
                line_at(&body, m.start()),
                m.as_str()
            ));
        }
    }
    bad
}

/// Check 7: a task id on two task lines of one `tasks.md`.
fn check_duplicate_tasks(tasks: &Path) -> Vec<String> {
    let text = read(tasks);
    let mut seen: BTreeMap<String, usize> = BTreeMap::new();
    let mut bad = Vec::new();
    for (n, line) in py_lines(&text).enumerate() {
        let Ok(Some(m)) = TASK_LINE.captures(line) else {
            continue;
        };
        if let Some(first) = seen.get(&m[1]) {
            bad.push(format!("{}:{}: task id {} is taken (line {first}) - file a task with `make task-add F=<n> TITLE=...`, which takes the next free id", tasks.display(), n + 1, &m[1]));
        } else {
            seen.insert(m[1].to_owned(), n + 1);
        }
    }
    bad
}

/// Check 6: a feature numbered 377 or above carries a well-formed approval line.
fn check_approval(spec_dir: &Path) -> Vec<String> {
    let spec = spec_dir.join("spec.md");
    let name = spec_dir.file_name().unwrap_or_default().to_string_lossy();
    let digits: String = name.chars().take_while(char::is_ascii_digit).collect();
    let number = if digits.len() >= 3 && name[digits.len()..].starts_with('-') {
        digits.parse().unwrap_or(0)
    } else {
        0
    };
    if number < APPROVAL_FIRST || !spec.is_file() {
        return Vec::new();
    }
    let data = std::fs::read(&spec).unwrap_or_default();
    let bad = form_problem(&String::from_utf8_lossy(&data));
    if bad.is_empty() {
        return Vec::new();
    }
    let why = if bad == "no-line" {
        "has none"
    } else {
        "quotes fewer than three words"
    };
    vec![format!("{}:1: {CHECK6_MARK} {why} - a feature is filed only with the GM's approval; ask the GM, then add, verbatim: {APPROVAL_FORM}", spec.display())]
}

/// Every complaint about one `specs/NNN-*/` directory; `tree_root` is what check 2 scans.
fn lint(spec_dir: &Path, tree_root: &Path) -> Vec<String> {
    let spec = spec_dir.join("spec.md");
    if !spec.is_file() {
        return Vec::new();
    }
    let tasks = spec_dir.join("tasks.md");
    let mut bad = check_withdrawn(spec_dir, tree_root);
    if tasks.is_file() {
        bad.extend(check_figures(&spec));
        bad.extend(check_orphans(&spec));
        bad.extend(check_stale_tasks(&spec, &tasks));
        bad.extend(check_duplicate_tasks(&tasks));
    }
    bad.extend(check_measured_figures(spec_dir));
    bad.extend(check_approval(spec_dir));
    bad
}

/// A finding without its locations, so a line that only moved is not a new finding.
fn bare(finding: &str) -> String {
    LOCATION.replace_all(finding, "").trim().to_owned()
}

/// The findings in `now` that `before` does not account for, as a multiset.
fn introduced(now: Vec<String>, before: &[String]) -> Vec<String> {
    let mut left: BTreeMap<String, usize> = BTreeMap::new();
    for finding in before {
        *left.entry(bare(finding)).or_default() += 1;
    }
    now.into_iter()
        .filter(|finding| {
            let count = left.entry(bare(finding)).or_default();
            let added = *count == 0;
            *count = count.saturating_sub(1);
            added
        })
        .collect()
}

/// The findings on a spec directory as it stood at `base`, or None when it did not exist there (feature 301 FR-027: a push that only
/// changes a landed spec is judged on what it introduces, not on rules added after that spec landed).
fn at_base(root: &Path, base: &str, spec_dir: &Path) -> Option<Vec<String>> {
    let top = std::fs::canonicalize(root).unwrap_or_default();
    let full = std::fs::canonicalize(spec_dir).unwrap_or_else(|_| spec_dir.to_owned());
    let rel = full
        .strip_prefix(&top)
        .unwrap_or(&full)
        .to_string_lossy()
        .into_owned();
    let listing = git_text(root, &["ls-tree", "-r", "--name-only", base, "--", &rel]);
    if listing.trim().is_empty() {
        return None;
    }
    let dir = scratch("spec-lint-base");
    for name in listing.split_whitespace() {
        let shown = Command::new("git")
            .arg("-C")
            .arg(root)
            .args(["show", &format!("{base}:{name}")])
            .output();
        let dest = dir.join(name);
        let _ = std::fs::create_dir_all(dest.parent().unwrap_or(&dir));
        let _ = std::fs::write(dest, shown.map(|o| o.stdout).unwrap_or_default());
    }
    let found = lint(&dir.join(&rel), root);
    let _ = std::fs::remove_dir_all(&dir);
    Some(found)
}

/// Every `specs/NNN-*/` the delta against the merge base touches, untracked ones too.
fn touched_spec_dirs(root: &Path) -> Vec<PathBuf> {
    let top = std::fs::canonicalize(root).unwrap_or_default();
    let base = git_text(&top, &["merge-base", "HEAD", "origin/main"]);
    let base = if base.trim().is_empty() {
        "HEAD"
    } else {
        base.trim()
    };
    let mut names = git_text(&top, &["diff", "--name-only", base]);
    names += &git_text(&top, &["ls-files", "--others", "--exclude-standard"]);
    let mut out: Vec<PathBuf> = Vec::new();
    for name in names.split_whitespace() {
        let mut parts = name.split('/');
        if parts.next() == Some("specs") {
            let dir = parts
                .next()
                .map_or_else(PathBuf::new, |p| top.join("specs").join(p));
            if dir.is_dir() && !out.contains(&dir) {
                out.push(dir);
            }
        }
    }
    out
}

const GOOD: &str = "# x\n\n## Summary\n\nIt took 91 min, measured in `research.md` R1.\n\n## Functional requirements\n\n**FR-001** A thing.\n\n**FR-001a** Another.\n\n## Success criteria\n\n**SC-001** (FR-001, FR-001a) Both hold.\n**SC-002** (spec-wide) The gate is green.\n\n## Decisions recorded\n\n**D1** We kept the 22 ft figure out of the rule (`research.md` R2).\n\n## Review history\n\nRound 1 said 6.7 m and we withdrew it.\n";
const FIGURE_LINE: &str = "It took 91 min, measured in `research.md` R1.";
const SC1: &str = "**SC-001** (FR-001, FR-001a) Both hold.";
const SC2: &str = "**SC-002** (spec-wide) The gate is green.";
const TITLED: &str = "**FR-001 A thing.** With a title in the bold span.";
const FR1: &str = "**FR-001** A thing.";
const TASK: &str = "- [ ] T01 do the thing (FR-001)\n";

/// (the text replaced in GOOD, what replaces it, research.md's text, tasks.md's text, what the first finding must hold, or "" for none).
type Row = (
    &'static str,
    &'static str,
    &'static str,
    &'static str,
    &'static str,
);
const SELFTEST: [Row; 13] = [
    ("", "", "", TASK, ""),
    (FR1, TITLED, "", TASK, ""),
    (
        SC1,
        "- **SC-001 Both hold.** (FR-001, FR-001a)",
        "",
        TASK,
        "",
    ),
    (
        "**FR-001a** Another.",
        "**FR-001a A title that\nwraps a line.** Another.",
        "",
        TASK,
        "",
    ),
    (FIGURE_LINE, "It took 91 min.", "", TASK, "no pointer"),
    (FIGURE_LINE, "It took 20 rounds.", "", TASK, ""),
    (
        SC1,
        "**SC-001** (FR-001) One holds.",
        "",
        TASK,
        "FR-001a is named by no success criterion",
    ),
    (
        SC2,
        "**SC-002** The gate is green.",
        "",
        TASK,
        "names no FR",
    ),
    ("", "", "", "- [ ] T01 do the thing (FR-404)\n", "FR-404"),
    ("", "", "WITHDRAWN: the 22 ft figure\n", TASK, ""),
    (
        FR1,
        "**FR-001** Keep the 22 ft figure.",
        "WITHDRAWN: the 22 ft figure\n",
        TASK,
        "withdrawn text still standing",
    ),
    ("", "", "WITHDRAWN: 22 ft\n", TASK, "twelve characters"),
    (FIGURE_LINE, "It took 91 min.", "", "", ""),
];

fn checks_one_to_four(dir: &Path) -> Vec<String> {
    let tree = dir.parent().and_then(Path::parent).unwrap_or(dir);
    lint(dir, tree)
        .into_iter()
        .filter(|x| !is_check5(x) && !x.contains(CHECK6_MARK))
        .collect()
}

/// The rows whose verdict is not what they say.
fn wrong_rows(rows: &[Row]) -> Vec<usize> {
    let root = scratch("spec-lint");
    let dir = root.join("specs/999-a-feature");
    let _ = std::fs::create_dir_all(&dir);
    let wrong = rows
        .iter()
        .enumerate()
        .filter(|(_, (from, to, research, tasks, want))| {
            let spec = if from.is_empty() {
                GOOD.to_owned()
            } else {
                GOOD.replace(from, to)
            };
            let _ = std::fs::write(dir.join("spec.md"), spec);
            let _ = std::fs::remove_file(dir.join("research.md"));
            let _ = std::fs::remove_file(dir.join("tasks.md"));
            if !research.is_empty() {
                let _ = std::fs::write(dir.join("research.md"), research);
            }
            if !tasks.is_empty() {
                let _ = std::fs::write(dir.join("tasks.md"), tasks);
            }
            let found = checks_one_to_four(&dir);
            if want.is_empty() {
                !found.is_empty()
            } else {
                !found.iter().any(|f| f.contains(want))
            }
        })
        .map(|(i, _)| i)
        .collect();
    let _ = std::fs::remove_dir_all(&root);
    wrong
}

fn selftest() -> Outcome {
    let wrong = wrong_rows(&SELFTEST);
    let moved = introduced(
        vec!["a.md:3: same".to_owned(), "a.md:4: same".to_owned()],
        &["a.md:1: same".to_owned()],
    );
    Outcome::selftest(
        wrong.is_empty() && moved == ["a.md:4: same"],
        "spec-lint selftest ok\n",
        format!("spec-lint SELFTEST FAILED: rows {wrong:?}, the multiset {moved:?}\n"),
    )
}

/// `l7r-gate check spec-lint --delta ROOT | DIR... | --selftest | --figure-pattern`.
pub(super) fn cli(args: &[String]) -> Outcome {
    let has = |flag: &str| args.iter().any(|a| a == flag);
    if has("--selftest") {
        return selftest();
    }
    if has("--figure-pattern") {
        return Outcome::out(figure_source() + "\n");
    }
    let named: Vec<&String> = args.iter().filter(|a| !a.starts_with("--")).collect();
    let root = Path::new(named.first().map_or(".", |a| a.as_str()));
    let delta = has("--delta");
    let dirs = if delta {
        touched_spec_dirs(root)
    } else {
        named.iter().map(PathBuf::from).collect()
    };
    let Some(first) = dirs.first() else {
        return Outcome::out(String::new());
    };
    let tree = std::fs::canonicalize(first)
        .ok()
        .and_then(|p| p.parent()?.parent().map(Path::to_owned))
        .unwrap_or_default();
    let merged = if delta {
        git_text(root, &["merge-base", "HEAD", "origin/main"])
    } else {
        String::new()
    };
    let mut bad = Vec::new();
    for dir in &dirs {
        let found = lint(dir, &tree);
        let earlier = if merged.trim().is_empty() || found.is_empty() {
            None
        } else {
            at_base(root, merged.trim(), dir)
        };
        bad.extend(match earlier {
            Some(old) => introduced(found, &old),
            None => found,
        });
    }
    if bad.is_empty() {
        return Outcome::out(String::new());
    }
    Outcome {
        stdout: format!("{}\n\nspec-lint: {} finding(s). Each is a thing a review round would otherwise spend itself on (feature 236, the GM: mistakes caught early and cheaply).\n", bad.join("\n"), bad.len()),
        stderr: String::new(),
        code: 1,
    }
}

#[cfg(test)]
mod tests;
