//! The one-time import from the GM's file (feature 313 plan D3), and `add`: the draft's entries appended under the next numbers, taken under a host-wide lock that sees
//! every clone (D6). The mirror and the lock are downloads' own: `<mirror>/.specify/download-ids.lock`, an `flock` the Python took through `reserve-prefix.py`'s `Lock`.

use std::fs::{File, OpenOptions};
use std::io::Write as _;
use std::os::unix::fs::OpenOptionsExt as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;
use std::time::{Duration, Instant};

use fancy_regex::Regex;
use serde_json::json;

use super::parse::{entries, parse, render, strip, Block, Entry, Marks, HEAD};
use super::{compiled, read, Ctx, CANON};
use crate::checks::py_repr;
use crate::logs::one_line;
use crate::measure::text_err;
use crate::record::py_lines;

const LOCK: &str = "download-ids.lock";
const LEDGER: &str = "download-ids.jsonl";
const HR_BEGIN: &str =
    "<!-- high-risk: imported from specs/312-uncited-source-catalog/high-risk-sources.md -->";
const HR_END: &str = "<!-- high-risk: end -->";
const GM_BEGIN: &str =
    "<!-- imported: the GM's TO-DOWNLOAD.md from here to the end, entries given their mark lines -->";
const STATUS_DOWNLOADED: [&str; 12] = [
    "1", "2", "3", "4", "5", "6", "8", "12", "13", "14", "15", "16",
];
const STATUS_NOT_FOUND: [&str; 4] = ["7", "9", "10", "11"];
const MONEY_SUBJECTS: [&str; 2] = ["money", "comparative"];
const MONEY_SECTIONS: [&str; 2] = ["money", "comparative-money"];

const HEADER: &str = r#"
**This is the canonical list, kept in the diagram repository (feature 313).** Your file in `academic-sources/` is a copy of
it. Mark the copy as you go; nothing else in it needs editing.

**Marking an entry.** Under each heading are three lines. Turn `[ ]` into `[x]` for what happened:

- **downloaded** - you have the whole work, saved in `academic-sources/`.
- **partial** - you have only part of it, such as the abstract or an excerpt.
- **paywalled** - it needs a paid or institutional login. It can be ticked with partial, when the abstract was free.
- **not found** - you could not find it anywhere. Tick it alone.
- **Found elsewhere** - tick it with downloaded or partial when what you have came from somewhere other than the links
  given, and write where after `where:`.
- **Saved as** is optional: the file's name, if you want to save the session matching your download to its entry.

**When you are ready, say "ingest".** The session records your marks here, archives the files you saved, and tells you
about anything it could not settle. **Say "sync"** to have your copy replaced by this list, with the entries added since
your last sync. Sync refuses while your copy holds marks that have not been ingested, so nothing you mark is lost.

New entries are only ever added at the very end of the file, never in between, so once you have worked to the end of a
part, that part stays done.
"#;

static NEW_HEAD: LazyLock<Regex> = LazyLock::new(|| compiled(r"^### NEW\. (.+)$"));
static POINTER: LazyLock<Regex> = LazyLock::new(|| {
    compiled(
        r"research/(?:questions/[0-9]{4}-[a-z0-9-]+(?:\.drawing)?\.html|contents\.json#[a-z0-9-]+)",
    )
});
static PROJECT_TAG: LazyLock<Regex> = LazyLock::new(|| compiled(r"^\[(money|diagram)\] "));
static SUBJECTS: LazyLock<Regex> = LazyLock::new(|| compiled(r"<!-- tags: subject=([^;>]*)"));
static LINK_LINE: LazyLock<Regex> = LazyLock::new(|| compiled(r"(?m)^- \*\*\[[^\]]+\]\(https?://"));
static FALLBACK: LazyLock<Regex> = LazyLock::new(|| compiled(r"(?m)^- Fallback: .*\]\(https?://"));
static RESTS: LazyLock<Regex> = LazyLock::new(|| compiled(r"(?m)^- \*\*Rests on it:\*\*"));
static BLOCKED: LazyLock<Regex> = LazyLock::new(|| compiled(r"(?m)^- Blocked by: \S"));

fn split_first(text: &str) -> (&str, &str) {
    text.split_once('\n').unwrap_or((text, ""))
}

/// The canonical list from the GM's file and 312's high-risk list (plan D3); entries the GM's 2026-09-13 status table settled are ticked from it (spec FR-004).
pub(super) fn import_list(gm_text: &str, high_risk_text: &str) -> String {
    let (gm_title, gm_rest) = split_first(gm_text);
    let (hr_title, hr_rest) = split_first(high_risk_text);
    let hr_heading = format!("## {}", hr_title.strip_prefix("# ").unwrap_or(hr_title));
    let text = [
        gm_title,
        HEADER,
        "---",
        "",
        HR_BEGIN,
        &hr_heading,
        hr_rest.trim_end_matches('\n'),
        HR_END,
        "",
        "---",
        "",
        GM_BEGIN,
        gm_rest,
    ]
    .join("\n");
    let mut blocks = parse(&text);
    for block in &mut blocks {
        if let Block::Item(e) = block {
            let id = e.id.as_str();
            let (downloaded, not_found) = (
                STATUS_DOWNLOADED.contains(&id),
                STATUS_NOT_FOUND.contains(&id),
            );
            e.marks = Some(Marks {
                downloaded,
                not_found,
                ..Marks::default()
            });
            if downloaded || not_found {
                e.recorded = Some(
                    "- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)"
                        .to_owned(),
                );
            }
        }
    }
    render(&blocks)
}

/// Where `(?m)^(?=### NEW\. )` splits a draft: a piece before each heading line.
fn pieces(text: &str) -> Vec<&str> {
    let mut starts: Vec<usize> = Vec::new();
    if text.starts_with("### NEW. ") {
        starts.push(0);
    }
    starts.extend(
        text.match_indices('\n')
            .map(|(i, _)| i + 1)
            .filter(|i| text[*i..].starts_with("### NEW. ")),
    );
    let mut out = Vec::new();
    let mut from = 0;
    for start in starts {
        out.push(&text[from..start]);
        from = start;
    }
    out.push(&text[from..]);
    out
}

fn all_pointers(body: &str) -> Vec<String> {
    POINTER
        .find_iter(body)
        .flatten()
        .map(|m| m.as_str().to_owned())
        .collect()
}

fn has(pattern: &Regex, body: &str) -> bool {
    pattern.is_match(body).unwrap_or(false)
}

/// The draft's entries as (title, body lines), each checked for its parts (plan D6); refuses naming what is missing.
fn drafts(text: &str, record: &Path) -> Result<Vec<(String, Vec<String>)>, String> {
    let mut out = Vec::new();
    for chunk in pieces(text) {
        if strip(chunk).is_empty() {
            continue;
        }
        let lines: Vec<&str> = chunk.trim_end_matches('\n').split('\n').collect();
        let Some(title) = NEW_HEAD.captures(lines[0]).ok().flatten() else {
            return Err("a draft entry is headed `### NEW. <the work>` - the number is given when it is appended".to_owned());
        };
        let body = lines[1..].join("\n");
        let mut missing: Vec<String> = [
            ("a link line `- **[...](https://...)**`", &*LINK_LINE),
            ("`- Fallback:` with a link", &*FALLBACK),
            ("`- **Rests on it:**`", &*RESTS),
            ("`- Blocked by:`", &*BLOCKED),
        ]
        .iter()
        .filter(|(_, p)| !has(p, &body))
        .map(|(what, _)| (*what).to_owned())
        .collect();
        let pointers = all_pointers(&body);
        if pointers.is_empty() {
            missing.push("a pointer in Rests on it (`research/questions/NNNN-<id>.html` or `research/contents.json#<section>`)".to_owned());
        }
        let gone: Vec<&str> = pointers
            .iter()
            .filter_map(|p| {
                p.strip_prefix("research/")
                    .filter(|r| r.starts_with("questions/"))
                    .filter(|r| !record.join(r).is_file())
                    .map(|_| p.as_str())
            })
            .collect();
        if !gone.is_empty() {
            missing.push(format!(
                "pointers that exist ({} - none such)",
                gone.join(", ")
            ));
        }
        if !missing.is_empty() {
            return Err(format!(
                "draft entry {} lacks: {}",
                py_repr(&title[1].into()),
                missing.join("; ")
            ));
        }
        out.push((
            title[1].to_owned(),
            lines[1..].iter().map(|l| (*l).to_owned()).collect(),
        ));
    }
    if out.is_empty() {
        return Err("the draft holds no `### NEW. <the work>` entry".to_owned());
    }
    Ok(out)
}

/// `money` when any question or section the entry's body points at is a money one, else `diagram`.
fn project_of(body: &str, record: &Path) -> &'static str {
    for pointer in all_pointers(body) {
        if let Some(section) = pointer.strip_prefix("research/contents.json#") {
            if MONEY_SECTIONS.contains(&section) {
                return "money";
            }
            continue;
        }
        let file = record.join(pointer.strip_prefix("research/").unwrap_or(&pointer));
        let text = if file.is_file() {
            read(&file).unwrap_or_default()
        } else {
            String::new()
        };
        let money = SUBJECTS
            .captures(&text)
            .ok()
            .flatten()
            .is_some_and(|m| m[1].split(',').any(|s| MONEY_SUBJECTS.contains(&strip(s))));
        if money {
            return "money";
        }
    }
    "diagram"
}

/// The heading with its project tag after the number, replacing any tag it had.
pub(super) fn tagged(heading: &str, project: &str) -> String {
    let Some(end) = HEAD.find(heading).ok().flatten().map(|m| m.end()) else {
        return heading.to_owned();
    };
    let title = PROJECT_TAG.replace(&heading[end..], "");
    format!("{}[{project}] {title}", &heading[..end])
}

/// Every entry's heading tagged by `project_of` its body - the one pass over the list, and idempotent.
pub(super) fn tag_all(text: &str, record: &Path) -> String {
    let mut blocks = parse(text);
    for block in &mut blocks {
        if let Block::Item(e) = block {
            e.heading = tagged(&e.heading, project_of(&e.body_text(), record));
        }
    }
    render(&blocks)
}

fn numbers_in(text: &str) -> Vec<u64> {
    let blocks = parse(text);
    entries(&blocks)
        .filter(|e| !e.id.starts_with('H'))
        .map(|e| e.id.parse().unwrap_or(0))
        .collect()
}

/// The list with `new` appended at its end - the one place a new entry goes (spec FR-008).
fn append(canon_text: &str, new: &[Entry]) -> String {
    let added: Vec<String> = new.iter().map(|e| e.lines().join("\n")).collect();
    format!(
        "{}\n\n{}\n",
        canon_text.trim_end_matches('\n'),
        added.join("\n\n")
    )
}

/// The mirror: a clone's grandparent when its parent is `.clones`, else the root itself.
fn mirror_of(root: &Path) -> PathBuf {
    if root
        .parent()
        .and_then(Path::file_name)
        .is_some_and(|n| n == ".clones")
    {
        root.parent()
            .and_then(Path::parent)
            .unwrap_or(root)
            .to_owned()
    } else {
        root.to_owned()
    }
}

/// `flock` on the lock file, polled so a hung holder is a refusal rather than a hang; the lock lasts as long as the open file.
fn lock(path: &Path, timeout: f64) -> Result<File, String> {
    let dir = path.parent().unwrap_or(Path::new("."));
    std::fs::create_dir_all(dir).map_err(text_err)?;
    let file = OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .mode(0o644)
        .open(path)
        .map_err(text_err)?;
    let deadline = Instant::now() + Duration::from_secs_f64(timeout);
    while !l7r_guard::shared::tool::flock(&file, "-n") {
        if Instant::now() >= deadline {
            let shown = path.display();
            return Err(format!(
                "could not take the prefix lock within {timeout}s: {shown} is held (fuser {shown})"
            ));
        }
        std::thread::sleep(Duration::from_millis(20));
    }
    Ok(file)
}

/// `datetime.datetime.now(datetime.UTC).isoformat()`.
fn iso_utc() -> String {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default();
    let (y, mo, d, h, mi, s) = l7r_guard::shared::log::civil(now.as_secs());
    format!(
        "{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}.{:06}+00:00",
        now.subsec_micros()
    )
}

fn highest_held(root: &Path, mirror: &Path, ledger: &Path) -> Result<u64, String> {
    let clones = mirror.join(".clones");
    let mut paths = vec![mirror.join(CANON), root.join(CANON)];
    paths.extend(
        std::fs::read_dir(&clones)
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.path().join(CANON)),
    );
    let mut held: Vec<u64> = Vec::new();
    for path in paths.iter().filter(|p| p.is_file()) {
        held.extend(numbers_in(&read(path)?));
    }
    if ledger.is_file() {
        let text = read(ledger)?;
        for line in py_lines(&text).into_iter().filter(|l| !strip(l).is_empty()) {
            let row: serde_json::Value = serde_json::from_str(line).map_err(text_err)?;
            held.push(row["n"].as_u64().unwrap_or(0));
        }
    }
    Ok(held.into_iter().max().unwrap_or(0))
}

/// Append the draft's entries under the next numbers, taken under the host-wide lock (plan D6); returns the ids.
pub(super) fn add(ctx: &Ctx, draft: &str) -> Result<Vec<String>, String> {
    let record = ctx.root.join("research");
    let items = drafts(draft, &record)?;
    let resolved = std::fs::canonicalize(&ctx.root).map_err(text_err)?;
    let mirror = mirror_of(&resolved);
    let ledger_path = mirror.join(".specify").join(LEDGER);
    let _held = lock(&mirror.join(".specify").join(LOCK), ctx.timeout)?;
    let mut n = highest_held(&ctx.root, &mirror, &ledger_path)?;
    let mut new = Vec::new();
    let mut rows = String::new();
    for (title, body) in items {
        n += 1;
        new.push(Entry {
            id: n.to_string(),
            heading: tagged(
                &format!("### {n}. {title}"),
                project_of(&body.join("\n"), &record),
            ),
            marks: Some(Marks::default()),
            recorded: None,
            body,
        });
        rows +=
            &one_line(&json!({"n": n, "clone": ctx.root.display().to_string(), "utc": iso_utc()}));
        rows.push('\n');
    }
    let mut ledger = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&ledger_path)
        .map_err(text_err)?;
    ledger.write_all(rows.as_bytes()).map_err(text_err)?;
    let path = ctx.root.join(CANON);
    std::fs::write(&path, append(&read(&path)?, &new)).map_err(text_err)?;
    Ok(new.into_iter().map(|e| e.id).collect())
}
