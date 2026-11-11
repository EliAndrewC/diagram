//! Pointers to the research resolve, and none is of a retired form (features 301, 303; feature 449 T065, from `check-research-pointers.py`). A pointer names a question's file or a section of `research/contents.json`, never a built
//! page. Only a line that can hold a pointer is asked. A run is recorded by `usage_log` under `USAGE_LOG_TOOL`.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::Path;

use fancy_regex::{Captures, Regex};
use serde_json::Value;

use super::{git_text, py_lines, Outcome};

pub(super) const USAGE_LOG_TOOL: &str = "check-research-pointers";
const RECORD: &str = "research";
const MAPPING: &str = "moved-303.json";
const CURRENT_DIRS: [&str; 5] = ["questions", "sources", "assets", "site", "archive"];
const VERBATIM: [&str; 2] = ["tests/hooks/fixtures/", "research/source-attempts.jsonl"];
const REFUSAL_DATA: [&str; 8] = [
    "tests/tooling/test_attempts.py",
    "rust/gate/src/record/leaves/tests.rs",
    "tests/hooks/test-record-edit-hooks.sh",
    "tests/hooks/test-check-bundle-hooks.sh",
    "rust/guard/src/guards/check_bundle_hooks/tests.rs",
    "tests/interactive/test_record.py",
    "rust/gate/src/checks/research_pointers/tests.rs",
    "rust/gate/src/checks/research_pointers.rs",
];
const FIXTURES: [&str; 11] = [
    "rust/gate/src/plan/",
    "tests/",
    "rust/gate/src/record/", // the record tools' tests and fragment-move's self-test name records of a scratch repository
    "scripts/gates/check-entry-headings.py",
    "rust/gate/src/checks/", // the checks' own tests and self-tests name fixture records
    "rust/gate/src/checks_door/", // the door's tests name fixture records (feature 449 T86)
    "rust/gate/src/arbiter/bundle/", // the arbiter bundle's tests name records of a scratch repository (feature 449 T88)
    "rust/gate/src/measure/depiction_replay/", // the replay's tests name records of a scratch repository (feature 449 T88)
    "rust/guard/src/guards/check_bundle_hooks/", // a dispatch's fixture prompts name records of a scratch repository
    "rust/guard/src/guards/record_edit_hooks/",
    "rust/guard/src/shared/checks/", // the check state's tests name fixture records
];
const EXEMPT_EXT: [&str; 5] = [".png", ".webp", ".jpg", ".pdf", ".gz"];

fn pattern(text: &str) -> Regex {
    Regex::new(text).unwrap()
}

/// The forms every line is asked about.
struct Forms {
    question: Regex,
    section: Regex,
    glued: Regex,
    old_fragment: Regex,
    old_directory: Regex,
    old_page: Regex,
    source_block: Regex,
    quoted: Regex,
}

impl Forms {
    fn new() -> Self {
        Self {
            question: pattern(
                r#"^research/questions/(\d{4}-[^\s"'`)\]<>,;|#*]+?\.html)(?![\w.-])"#,
            ),
            section: pattern(r"^research/contents\.json#([a-z0-9-]+)"),
            glued: pattern(
                r"^research/contents\.json#[a-z0-9-]+(?:[A-Z0-9_*{]|<(?!/)|/[^\s)`]|\.md\b|\.html\b)",
            ),
            old_fragment: pattern(
                r#"^research/((?:[a-z][a-z-]*/)+)(\d{3}-[^\s"'`)\]<>,;|#*]+?\.html)(?![\w.-])"#,
            ),
            old_directory: pattern(r"^research/((?:[a-z][a-z-]*/)*[a-z][a-z-]*)/(?![\w.-])"),
            old_page: pattern(
                r#"^research/(citations/)?((?:[a-z][a-z-]*/)*[A-Za-z][A-Za-z-]*)\.html(?:#[^\s"'`)\]<>,;|]+)?(?![\w/-])"#,
            ),
            source_block: pattern(r"(?s)<!-- SOURCE: GM NOTES.*?<!-- END SOURCE -->"),
            quoted: pattern(r#"(?s)\*"[^"]*?"\*"#),
        }
    }
}

/// `[\w.-]`, the character none of the pointer forms may follow.
fn wordish(c: char) -> bool {
    c.is_alphanumeric() || c == '_' || c == '.' || c == '-'
}

/// `finditer` for a form anchored at `research/`: each occurrence not glued to what precedes it, tried once, so that a long line costs its occurrences rather than a scan per character (the look-behind, by hand).
fn at_research<'t>(re: &Regex, line: &'t str) -> Vec<Captures<'t>> {
    let (mut out, mut from) = (Vec::new(), 0);
    while let Some(found) = line[from..].find("research/") {
        let at = from + found;
        from = at + "research/".len();
        if line[..at].chars().next_back().is_some_and(wordish) {
            continue;
        }
        if let Ok(Some(c)) = re.captures(&line[at..]) {
            from = at + c.get(0).map_or(1, |m| m.end().max(1));
            out.push(c);
        }
    }
    out
}

fn group<'t>(c: &Captures<'t>, n: usize) -> &'t str {
    c.get(n).map_or("", |m| m.as_str())
}

/// The migration's mapping and the record as it stands.
struct Mapping {
    files: BTreeMap<String, String>,
    pages: BTreeMap<String, String>,
    numbers: BTreeMap<String, String>,
    questions: BTreeSet<String>,
    sections: BTreeSet<String>,
    heads: BTreeSet<String>,
    /// The lengths of `heads`, longest first: the longest name wins, as the alternation did.
    lengths: Vec<usize>,
    old_md: Regex,
    old_dir: Regex,
    command: Regex,
}

fn table(data: &Value, key: &str) -> BTreeMap<String, String> {
    data[key]
        .as_object()
        .into_iter()
        .flatten()
        .map(|(k, v)| (k.clone(), v.as_str().unwrap_or_default().to_owned()))
        .collect()
}

fn walk_sections(list: &Value, into: &mut BTreeSet<String>) {
    for s in list.as_array().into_iter().flatten() {
        into.insert(s["id"].as_str().unwrap_or_default().to_owned());
        walk_sections(&s["sections"], into);
    }
}

/// The alternation, longest first: a shorter name must not win over the longer one it opens.
fn alternation<'a>(names: impl Iterator<Item = &'a str>) -> String {
    let mut sorted: Vec<&str> = names.collect();
    sorted.sort_by_key(|n| std::cmp::Reverse(n.len()));
    if sorted.is_empty() {
        return "(?!)".to_owned();
    }
    sorted
        .iter()
        .map(|n| fancy_regex::escape(n).into_owned())
        .collect::<Vec<_>>()
        .join("|")
}

/// Each `<page>[ /]<NNN>` of a line: `(whole, page, number)`. Found from the digits outward, since the alternation of every old page name, tried at each character of a long line, was quadratic (77 s, feature 383).
fn old_numbers<'t>(line: &'t str, mapping: &Mapping) -> Vec<(&'t str, &'t str, &'t str)> {
    let bytes = line.as_bytes();
    let mut out = Vec::new();
    let mut last_end = 0;
    for sep in 0..bytes.len().saturating_sub(3) {
        if !matches!(bytes[sep], b' ' | b'/')
            || !bytes[sep + 1..sep + 4].iter().all(u8::is_ascii_digit)
        {
            continue;
        }
        let tail = &line[sep + 4..];
        if tail.chars().next().is_some_and(char::is_numeric)
            || tail.strip_prefix('-').is_some_and(|r| {
                r.starts_with(|c: char| c.is_ascii_lowercase() || c.is_ascii_digit())
            })
            || tail
                .strip_prefix('.')
                .is_some_and(|r| r.starts_with(|c: char| c.is_numeric()))
        {
            continue;
        }
        let name = mapping
            .lengths
            .iter()
            .filter(|n| **n <= sep && sep - **n >= last_end)
            .find_map(|n| {
                let start = sep - n;
                let head = line.get(start..sep)?;
                (mapping.heads.contains(head)
                    && !line[..start]
                        .chars()
                        .next_back()
                        .is_some_and(|c| wordish(c) || c == '/'))
                .then_some(start)
            });
        if let Some(start) = name {
            out.push((
                &line[start..sep + 4],
                &line[start..sep],
                &line[sep + 1..sep + 4],
            ));
            last_end = sep + 4;
        }
    }
    out
}

impl Mapping {
    fn new(record: &Path) -> Self {
        let data: Value = serde_json::from_str(
            &std::fs::read_to_string(record.join(MAPPING)).unwrap_or_default(),
        )
        .unwrap_or_default();
        let (files, pages, numbers) = (
            table(&data, "files"),
            table(&data, "pages"),
            table(&data, "numbers"),
        );
        let questions = std::fs::read_dir(record.join("questions"))
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.file_name().to_string_lossy().into_owned())
            .filter(|n| super::has_ext(n, "html"))
            .collect();
        let contents: Value = serde_json::from_str(
            &std::fs::read_to_string(record.join("contents.json")).unwrap_or_default(),
        )
        .unwrap_or_default();
        let mut sections = BTreeSet::new();
        walk_sections(&contents["sections"], &mut sections);
        let heads: BTreeSet<String> = numbers
            .keys()
            .map(|k| k.split(' ').next().unwrap_or_default().to_owned())
            .collect();
        let dirs = alternation(pages.keys().map(String::as_str));
        Self {
            lengths: heads
                .iter()
                .map(String::len)
                .collect::<BTreeSet<_>>()
                .into_iter()
                .rev()
                .collect(),
            heads,
            old_md: pattern(&format!(r"^research/({dirs})\.md\b")),
            old_dir: pattern(&format!(r#"^research/({dirs})(?=["'`)\s,;:]|\.(?!\w)|$)"#)),
            command: pattern(&format!(
                r"PAGE=({dirs})\b(?!/)(?:(?:\s+|,\s*)SECTION=(\d{{3}})\b)?"
            )),
            files,
            pages,
            numbers,
            questions,
            sections,
        }
    }

    fn section_of(&self, page: &str) -> String {
        let bare = page.strip_prefix("rendering/").unwrap_or(page);
        self.pages
            .get(bare)
            .or_else(|| self.pages.get(page))
            .map_or_else(
                || "a section of research/contents.json".to_owned(),
                |s| format!("research/contents.json#{s}"),
            )
    }

    fn number_of(&self, key: &str) -> Option<&String> {
        self.numbers
            .get(key)
            .or_else(|| self.numbers.get(&format!("rendering/{key}")))
    }
}

/// The question files and sections one line names; whether each exists is asked of the record as it stands.
fn refs(forms: &Forms, text: &str) -> (Vec<String>, Vec<String>) {
    let of = |re: &Regex| {
        at_research(re, text)
            .iter()
            .map(|c| group(c, 1).to_owned())
            .collect()
    };
    (of(&forms.question), of(&forms.section))
}

fn resolved(
    questions: &[String],
    sections: &[String],
    mapping: &Mapping,
    fixture: bool,
) -> Vec<String> {
    if fixture {
        return Vec::new();
    }
    let q = questions
        .iter()
        .filter(|q| !mapping.questions.contains(*q))
        .map(|q| format!("`research/questions/{q}` - no such question file"));
    let s = sections
        .iter()
        .filter(|s| !mapping.sections.contains(*s))
        .map(|s| format!("`research/contents.json#{s}` - no such section"));
    q.chain(s).collect()
}

fn retired_commands(text: &str, mapping: &Mapping, landed_spec: bool, out: &mut Vec<String>) {
    for c in mapping.command.captures_iter(text).flatten() {
        let whole = group(&c, 0);
        let (page, number) = (group(&c, 1), c.get(2));
        let Some(number) = number else {
            out.push(format!(
                "`{whole}` - a retired page argument; name `IN={}` (or `Q=<NNNN>`)",
                mapping
                    .pages
                    .get(page)
                    .map_or("<section or tag>", String::as_str)
            ));
            continue;
        };
        if let Some(new) = mapping.number_of(&format!("{page} {}", number.as_str())) {
            out.push(format!(
                "`{whole}` - a retired page argument; name `Q={new}`"
            ));
        } else if !landed_spec {
            out.push(format!("`{whole}` - a retired page argument; name `Q=<NNNN>` (its number names no question: in a landed spec only, as history, it may stand)"));
        }
    }
    for (whole, page, number) in old_numbers(text, mapping) {
        if let Some(new) = mapping.number_of(&format!("{page} {number}")) {
            out.push(format!(
                "`{whole}` - a question's old page and number; it is now {new}"
            ));
        }
    }
}

fn head(path: &str) -> &str {
    path.split('/').next().unwrap_or_default()
}

/// The retired forms in one line, read from the migration's mapping alone.
fn retired(
    forms: &Forms,
    text: &str,
    mapping: &Mapping,
    refusal_data: bool,
    landed_spec: bool,
) -> Vec<String> {
    let mut out = Vec::new();
    if refusal_data {
        return out;
    }
    for c in at_research(&forms.glued, text) {
        out.push(format!("`{}` - path text glued after a section id; name the section alone or the question's file", group(&c, 0)));
    }
    for c in at_research(&mapping.old_md, text) {
        out.push(format!(
            "`{}` - a retired page (feature 303); name {}",
            group(&c, 0),
            mapping.section_of(group(&c, 1))
        ));
    }
    for c in at_research(&mapping.old_dir, text) {
        out.push(format!(
            "`{}` - the page directories are retired (feature 303); name {}",
            group(&c, 0),
            mapping.section_of(group(&c, 1))
        ));
    }
    for c in at_research(&forms.old_fragment, text)
        .into_iter()
        .filter(|c| !CURRENT_DIRS.contains(&head(group(c, 1))))
    {
        let old = format!("{}{}", group(&c, 1), group(&c, 2));
        let tail = mapping.files.get(&old).map_or_else(
            || "name its question, `research/questions/NNNN-<slug>.html`".to_owned(),
            |new| format!("it is now `research/{new}`"),
        );
        out.push(format!(
            "`research/{old}` - the page directories are retired (feature 303); {tail}"
        ));
    }
    for c in at_research(&forms.old_directory, text)
        .into_iter()
        .filter(|c| !CURRENT_DIRS.contains(&head(group(c, 1))) && group(c, 1) != "contents.json")
    {
        out.push(format!(
            "`research/{}/` - the page directories are retired (feature 303); name {}",
            group(&c, 1),
            mapping.section_of(group(&c, 1))
        ));
    }
    for c in at_research(&forms.old_page, text)
        .into_iter()
        .filter(|c| !CURRENT_DIRS.contains(&head(group(c, 2))))
    {
        let page = group(&c, 2);
        let place = if page == "SOURCES" {
            "the registry's fragments, `research/sources/`".to_owned()
        } else {
            mapping.section_of(page)
        };
        out.push(format!("`{}` - a built page; name {place}", group(&c, 0)));
    }
    retired_commands(text, mapping, landed_spec, &mut out);
    out
}

fn exempt(path: &str) -> bool {
    let name = path.rsplit('/').next().unwrap_or(path);
    VERBATIM.iter().any(|v| path.starts_with(v))
        || path.ends_with("/plan-review.json")
        || path == "research/moved-303.json"
        || path == "specs/303-research-organization/migration.md"
        || name == "request.md"
        || name == "README.md"
        || EXEMPT_EXT.iter().any(|e| path.ends_with(e))
}

/// A span of text replaced by as many newlines as it held, so that line numbers stand.
fn blanked(re: &Regex, text: &str) -> String {
    re.replace_all(text, |c: &Captures<'_>| {
        "\n".repeat(group(c, 0).matches('\n').count())
    })
    .into_owned()
}

/// What one tracked file says wrongly.
fn file_problems(root: &Path, path: &str, forms: &Forms, mapping: &Mapping) -> Vec<String> {
    let text = std::fs::read_to_string(root.join(path)).unwrap_or_default();
    // the two blanking patterns only where they can match: most files hold neither
    let text = if text.contains("*\"") || text.contains("<!-- SOURCE") {
        blanked(&forms.quoted, &blanked(&forms.source_block, &text))
    } else {
        text
    };
    let (fixture, refusal_data, landed_spec) = (
        FIXTURES.iter().any(|f| path.starts_with(f)),
        REFUSAL_DATA.contains(&path),
        path.starts_with("specs/"),
    );
    let mut bad = Vec::new();
    for (at, line) in py_lines(&text).enumerate() {
        if line.contains("research/")
            || line.contains("PAGE=")
            || !old_numbers(line, mapping).is_empty()
        {
            let found = line_problems(forms, line, mapping, fixture, refusal_data, landed_spec);
            bad.extend(found.into_iter().map(|p| format!("{path}:{}: {p}", at + 1)));
        }
    }
    bad
}

/// Every wrong pointer, in the order `git ls-files` names the files. On several threads: this reads every tracked file on
/// every push and preflight, and the Python it replaced did so in 0.41 s on its content cache (`m:t065-pointers-warm`).
fn check(root: &Path) -> Vec<String> {
    let record = root.join(RECORD);
    if !record.is_dir() {
        return Vec::new();
    }
    let (forms, mapping) = (Forms::new(), Mapping::new(&record));
    let listed = git_text(root, &["ls-files"]);
    let paths: Vec<&str> = listed
        .lines()
        .filter(|p| !exempt(p) && !p.contains("/research/site/"))
        .collect();
    let threads = std::thread::available_parallelism().map_or(1, std::num::NonZero::get);
    let scan = |part: &[&str]| -> Vec<String> {
        part.iter()
            .flat_map(|p| file_problems(root, p, &forms, &mapping))
            .collect()
    };
    std::thread::scope(|s| {
        let scan = &scan;
        let running: Vec<_> = paths
            .chunks(paths.len().div_ceil(threads).max(1))
            .map(|part| s.spawn(move || scan(part)))
            .collect();
        running
            .into_iter()
            .flat_map(|t| t.join().unwrap_or_default())
            .collect()
    })
}

fn line_problems(
    forms: &Forms,
    line: &str,
    mapping: &Mapping,
    fixture: bool,
    refusal_data: bool,
    landed_spec: bool,
) -> Vec<String> {
    let (questions, sections) = refs(forms, line);
    resolved(&questions, &sections, mapping, fixture)
        .into_iter()
        .chain(retired(forms, line, mapping, refusal_data, landed_spec))
        .collect()
}

/// A self-test row: (the line, fixture, refusal data, landed spec, what the first finding must contain, or "" for none).
type Row = (&'static str, bool, bool, bool, &'static str);

const SELFTEST: [Row; 27] = [
    ("see research/questions/0412-reservoir-ponds-tameike.html, research/contents.json#water and research/sources/ and research/site/q/x.html", false, false, false, ""),
    ("research/questions/0499-gone.html", false, false, false, "no such question file"),
    ("research/contents.json#nowhere", false, false, false, "no such section"),
    ("research/water/120-reservoir-ponds-tameike.html", false, false, false, "it is now `research/questions/0412-reservoir-ponds-tameike.html`"),
    ("research/towns/030-gone.html", false, false, false, "name its question"),
    ("research/water/ and", false, false, false, "name research/contents.json#water"),
    ("research/rendering/water/", false, false, false, "name research/contents.json#water"),
    ("research/water.html#x", false, false, false, "a built page; name research/contents.json#water"),
    ("research/SOURCES.html", false, false, false, "research/sources/"),
    ("water 120 and water/120", false, false, false, "it is now 0412"),
    ("water 015", false, false, false, "now 0413"),
    ("water 121, water 120-130, 120 water", false, false, false, ""),
    ("water 120.5 monme", false, false, false, ""),
    ("make check-bundle PAGE=water SECTION=120", false, false, false, "name `Q=0412`"),
    ("make record-prepass PAGE=water", false, false, false, "name `IN=water`"),
    ("PAGE=water SECTION=121", false, false, true, ""),
    ("PAGE=water SECTION=121", false, false, false, "name `Q=<NNNN>`"),
    (concat!("see research/water", ".md for it"), false, false, false, "name research/contents.json#water"),
    ("research/contents.json#water*.html", false, false, false, "glued after a section id"),
    ("<code>research/contents.json#water</code>", false, false, false, ""),
    ("research/contents.json#water<NNN>-<id>.html", false, false, false, "glued after a section id"),
    ("research/contents.json#water.", false, false, false, ""),
    ("glob(REPO / \"research/water\")", false, false, false, "name research/contents.json#water"),
    ("research/questions/0499-made-up.html", true, false, false, ""),
    ("research/water/120-reservoir-ponds-tameike.html", true, false, false, "it is now"),
    ("research/water/120-reservoir-ponds-tameike.html", false, true, false, ""),
    ("specs/229-rule-files-into-research/audit/x.md", false, false, false, ""),
];

fn own_record() -> (Forms, Mapping) {
    let record = super::scratch("research-pointers");
    let _ = std::fs::create_dir_all(record.join("questions"));
    let _ = std::fs::write(
        record.join("questions/0412-reservoir-ponds-tameike.html"),
        "x",
    );
    let _ = std::fs::write(
        record.join("contents.json"),
        r#"{"sections": [{"id": "countryside", "sections": [{"id": "water"}]}]}"#,
    );
    let _ = std::fs::write(
        record.join(MAPPING),
        r#"{"files": {"water/120-reservoir-ponds-tameike.html": "questions/0412-reservoir-ponds-tameike.html"}, "pages": {"water": "water"}, "numbers": {"water 120": "0412", "rendering/water 015": "0413"}}"#,
    );
    let built = (Forms::new(), Mapping::new(&record));
    let _ = std::fs::remove_dir_all(&record);
    built
}

/// The rows whose verdict is not what they say.
fn wrong_rows<'a>(rows: &'a [Row], forms: &Forms, mapping: &Mapping) -> Vec<&'a str> {
    rows.iter()
        .filter(|(line, fixture, data, landed, want)| {
            let found = line_problems(forms, line, mapping, *fixture, *data, *landed);
            if want.is_empty() {
                !found.is_empty()
            } else {
                !found.first().is_some_and(|f| f.contains(want))
            }
        })
        .map(|(line, ..)| *line)
        .collect()
}

/// Prove the check still bites, over a record of its own.
fn selftest() -> Outcome {
    let (forms, mapping) = own_record();
    let wrong = wrong_rows(&SELFTEST, &forms, &mapping);
    let exempt_right = exempt("specs/180-x/request.md")
        && exempt("research/moved-303.json")
        && !exempt("CLAUDE.md")
        && !exempt("research/CLAUDE.md")
        && exempt("tests/hooks/fixtures/x.json")
        && !exempt("tests/x.py")
        && !exempt("scripts/x.py");
    Outcome::selftest(
        wrong.is_empty() && exempt_right,
        "check-research-pointers selftest ok\n",
        format!("check-research-pointers SELFTEST FAILED: {wrong:?}\n"),
    )
}

/// `l7r-gate check research-pointers [ROOT]`.
pub(super) fn cli(args: &[String]) -> Outcome {
    if args.first().is_some_and(|a| a == "--selftest") {
        return selftest();
    }
    let root = std::fs::canonicalize(args.first().map_or(".", String::as_str)).unwrap_or_default();
    let bad = check(&root);
    if bad.is_empty() {
        return Outcome::out(String::new());
    }
    let mut err = "pointers to the research that do not resolve, or are of a retired form (features 301, 303):\n".to_owned();
    err.extend(bad.iter().take(60).map(|l| format!("  {l}\n")));
    if bad.len() > 60 {
        let _ = writeln!(err, "  ... and {} more", bad.len() - 60);
    }
    Outcome::refuse(err)
}

#[cfg(test)]
mod tests;
