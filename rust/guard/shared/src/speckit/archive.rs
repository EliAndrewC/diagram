//! A feature's finished records cut into parts (451 T537): `plan-done.md` and `tasks-done.md` moved, whole task by whole task, into
//! parts of at most [`BOUND`] bytes under `archive/`, with a machine index (`archive/index.json`: each part, and each task's parts) and a
//! note for a reader (`archive/INDEX.md`, "Load this file when:").
//!
//! WHY (the GM 2026-11-27, 462's request.md: future sessions "naively just opening these very large files and then blowing through
//! their own context windows"): 451's plan-done.md stood at 3.6 MB and tasks-done.md at 0.6 MB; a Read, a grep or a tool reading one
//! task's section read the whole file (`make plan-delta` plan-done.md eleven times a call, `make decide` and `make task-add`
//! tasks-done.md five times; T536's record, `dev/measurements/2026-11-27/t536-record-readers/results.md`).
//!
//! THE CUT (decided here, 451 T537): runs of whole tasks in the record's own order ([`cut`] says why not the ids'), packed under a
//! byte bound. A byte bound,
//! not a fixed id range: ten-id ranges of 451's plan-done.md ran 152 KB at the largest against a 60 KB median, so a range part could
//! still overrun a reader; the largest single task is 33 KB, so every task fits a part. Each part is named for its sequence and its
//! lowest and highest id for a reader's eye; a tool finds a task's parts by the index alone, never by the name (the ranges overlap).
//!
//! THE LAYOUT IS EITHER: a feature with no `archive/` reads its flat files as before; one with it reads every part in order and then the
//! flat file, which is the tail a tick wrote since the last fold. [`fold`] moves a flat file into new parts: where `archive/` stands (the
//! tick runs it after its archive step), or forced by `make archive-split`, the one way a feature is first split. No size starts a
//! split by itself: FR-004 names 451's records alone, and a split landing in the same push as these readers would meet the mirror's
//! older guard binary, which reads the flat files (the advisor's ruling on the build half, 2026-11-27; 462 T546 prices a size trigger).

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Value};

use crate::plan_text::leading_tasks;

/// The parts' directory, in the feature directory.
pub const DIR: &str = "archive";
/// The machine index, feature-relative.
pub const INDEX: &str = "archive/index.json";
/// The reader's note, feature-relative.
pub const NOTE: &str = "archive/INDEX.md";
/// The archived plan sections.
pub const PLAN_DONE: &str = "plan-done.md";
/// The archived (ticked) tasks.
pub const TASKS_DONE: &str = "tasks-done.md";
/// The records cut into parts.
pub const RECORDS: [&str; 2] = [PLAN_DONE, TASKS_DONE];
/// A part's most bytes, but a single task larger than it, which stands in a part alone. 64 KiB (a GUESS knob, 451 T537): about 16,000
/// tokens at 4 bytes a token, under the Read tool's cap for one call, and about 390 lines of 451's plan-done.md, under its 2,000-line
/// default.
pub const BOUND: usize = 65_536;

/// A heading a plan part may be cut at: a task's section opens at a level-2 or level-3 heading.
static CUT: LazyLock<Regex> = LazyLock::new(|| build(r"^#{2,3} (.*)"));
/// A task's block in tasks-done.md opens at a column-0 box.
static BOX: LazyLock<Regex> = LazyLock::new(|| build(r"^- \[[ xX]\] (T\d+[a-z]?)?"));

fn build(pattern: &str) -> Regex {
    crate::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// A reader of a feature directory's file by its feature-relative path: the working tree's ([`files`]), or a revision's (`git show`).
pub type Read<'a> = &'a dyn Fn(&str) -> Option<String>;

/// The working tree's reader of feature directory `d`.
pub fn files(d: &Path) -> impl Fn(&str) -> Option<String> + '_ {
    move |rel| std::fs::read_to_string(d.join(rel)).ok()
}

/// The index (an empty object where none stands or it does not parse).
fn index(read: Read) -> Value {
    read(INDEX)
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or_else(|| json!({}))
}

fn strings(v: &Value) -> Vec<String> {
    v.as_array()
        .map(|a| {
            a.iter()
                .filter_map(Value::as_str)
                .map(str::to_owned)
                .collect()
        })
        .unwrap_or_default()
}

/// `record`'s `parts`, in order, then its flat file, each text ending in a line break.
fn joined(read: Read, parts: &[String], record: &str) -> String {
    let mut out = String::new();
    // a part's own header line is no record text: left in, it would join the section before it (the last of the part before)
    let body = |t: String| match t.split_once("\n\n") {
        Some((head, rest)) if head.starts_with("# ") && !head.contains('\n') => rest.to_owned(),
        _ => t,
    };
    for text in parts
        .iter()
        .filter_map(|p| read(&format!("{DIR}/{p}")).map(body))
        .chain(read(record))
    {
        out += &text;
        if !out.is_empty() && !out.ends_with('\n') {
            out.push('\n');
        }
    }
    out
}

/// Every text of `record` (its parts, then its flat file): for a reader that must see all of it. A by-task reader takes [`task_text`].
#[must_use]
pub fn text(read: Read, record: &str) -> String {
    joined(read, &strings(&index(read)["parts"][record]), record)
}

/// Every archived plan section of feature directory `d` ([`text`] of the working tree's plan-done.md).
#[must_use]
pub fn plan_done(d: &Path) -> String {
    text(&files(d), PLAN_DONE)
}

/// The text of the parts holding `task`'s own headings or block, then the flat file: what a reader of one task opens.
#[must_use]
pub fn task_text(read: Read, record: &str, task: &str) -> String {
    joined(read, &strings(&index(read)["tasks"][record][task]), record)
}

/// The task ids the parts of `record` hold, per the index (the flat file's are the caller's to read).
#[must_use]
pub fn ids(read: Read, record: &str) -> Vec<String> {
    index(read)["tasks"][record]
        .as_object()
        .map(|m| m.keys().cloned().collect())
        .unwrap_or_default()
}

/// Every file of the archive, feature-relative: the index, the note and each part (for a step that cleans or names them); none where
/// no index stands.
#[must_use]
pub fn paths(read: Read) -> Vec<String> {
    let index = index(read);
    if index.as_object().is_none_or(serde_json::Map::is_empty) {
        return Vec::new();
    }
    let mut out = vec![INDEX.to_owned(), NOTE.to_owned()];
    for record in RECORDS {
        out.extend(
            strings(&index["parts"][record])
                .into_iter()
                .map(|p| format!("{DIR}/{p}")),
        );
    }
    out
}

/// A task's sort key: its number, then its letter.
fn order(id: &str) -> (u128, String) {
    let digits: String = id
        .chars()
        .skip(1)
        .take_while(char::is_ascii_digit)
        .collect();
    (
        digits.parse().unwrap_or(u128::MAX),
        id[1 + digits.len()..].to_owned(),
    )
}

/// The ids a line opens a piece for: a plan heading's own tasks, a box's task; None for any other line (and for a heading or box that
/// owns none, which stays inside the piece before it).
fn owned(record: &str, line: &str) -> Option<Vec<String>> {
    let re = if record == PLAN_DONE { &CUT } else { &BOX };
    let c = re.captures(line).ok().flatten()?;
    let words = c.get(1).map_or("", |m| m.as_str().trim_end());
    let ids: Vec<String> = if record == PLAN_DONE {
        leading_tasks(words)
            .into_iter()
            .map(str::to_owned)
            .collect()
    } else {
        vec![words.to_owned()]
    };
    (!ids.is_empty() && !ids[0].is_empty()).then_some(ids)
}

/// What stands before the first piece (the header's title and blank lines dropped: an archive marker, say), and (the leading task,
/// the ids the piece owns, its text) for each piece of a flat record, in the file's order.
fn pieces(record: &str, text: &str) -> (String, Vec<(String, Vec<String>, String)>) {
    let mut out: Vec<(String, Vec<String>, String)> = Vec::new();
    let mut head = String::new();
    for line in text.split_inclusive('\n') {
        match (owned(record, line), out.last_mut()) {
            (Some(ids), _) => out.push((ids[0].clone(), ids, line.to_owned())),
            (None, Some(last)) => last.2.push_str(line),
            (None, None) if !(line.starts_with("# ") || line.trim().is_empty()) => {
                head.push_str(line);
            }
            (None, None) => {}
        }
    }
    (head, out)
}

/// A part: its lowest id, its highest, the ids its pieces own, its text.
type Part = (String, String, Vec<String>, String);

/// The parts `record`'s flat `text` is cut into, in the record's own order: its pieces taken in RUNS - a piece whose task the run
/// before it owns (a bundle's member's part B after the bundle, a task's Approach after its section) joins that run - and whole runs
/// packed under [`BOUND`], a run larger than it alone in its part. What stood before the first piece opens the first part, before any
/// heading, so it joins no task's section. WHY the record's order and not the ids': a task's section is its headings joined in the
/// order they stand (`plan_text::task_sections`), and a bundle's member's headings stand in its bundle's run and in its own, so a
/// sort by id moved 451 T352's bundle heading after its part B headings and `make plan-section T=T352` printed them in another order
/// (measured on a copy of 451's records, 2026-11-27). Each part is named for the lowest and the highest id it holds.
fn cut(record: &str, text: &str) -> Vec<Part> {
    let (head, pieces) = pieces(record, text);
    let mut runs: Vec<(Vec<String>, String)> = Vec::new();
    for (lead, ids, body) in pieces {
        match runs.last_mut() {
            Some(run) if run.0.contains(&lead) => {
                run.0.extend(ids);
                run.1 += &body;
            }
            _ => runs.push((ids, body)),
        }
    }
    let mut parts: Vec<Part> = Vec::new();
    for (ids, body) in runs {
        match parts.last_mut() {
            Some(p) if p.3.len() + body.len() <= BOUND => {
                p.2.extend(ids);
                p.3 += &body;
            }
            _ => parts.push((String::new(), String::new(), ids, body)),
        }
    }
    for p in &mut parts {
        let mut sorted: Vec<&String> = p.2.iter().collect();
        sorted.sort_by_key(|id| order(id));
        p.0.clone_from(sorted[0]);
        p.1.clone_from(sorted[sorted.len() - 1]);
    }
    if let Some(first) = parts.first_mut() {
        first.3.insert_str(0, &head);
    }
    parts
}

/// Fold feature directory `d`'s flat records into new parts where `force` or where `archive/` stands; the parts written, feature-relative. The parts, the index and the note are written before the flat file is removed:
/// a failure between leaves a task in both places, which a reader of the whole sees twice, never in neither.
///
/// # Errors
/// A file that cannot be written or removed.
pub fn fold(d: &Path, force: bool) -> Result<Vec<String>, String> {
    if !(force || d.join(DIR).is_dir()) {
        return Ok(Vec::new());
    }
    let mut index = index(&files(d));
    let feature = d
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    let mut written = Vec::new();
    for record in RECORDS {
        let flat = d.join(record);
        let Ok(text) = std::fs::read_to_string(&flat) else {
            continue;
        };
        let stem = record.trim_end_matches(".md");
        let dir = d.join(DIR).join(stem);
        io(&dir, std::fs::create_dir_all(&dir))?;
        let mut parts = strings(&index["parts"][record]);
        for (first, last, ids, body) in cut(record, &text) {
            let n = parts.len() + 1;
            let name = format!("{stem}/{n:03}-{first}-{last}.md");
            let path = d.join(DIR).join(&name);
            let header = format!(
                "# {feature} - {record}, part {n} ({first} to {last}), cut by `make archive-split` (451 T537); what is where: {NOTE}\n\n"
            );
            io(&path, std::fs::write(&path, header + &body))?;
            for id in ids {
                let slot = &mut index["tasks"][record][&id];
                if !strings(slot).contains(&name) {
                    let mut named = strings(slot);
                    named.push(name.clone());
                    *slot = json!(named);
                }
            }
            parts.push(name.clone());
            written.push(format!("{DIR}/{name}"));
        }
        index["parts"][record] = json!(parts);
        index["bound"] = json!(BOUND);
        let at = d.join(INDEX);
        let pretty = serde_json::to_string_pretty(&index).unwrap_or_default() + "\n";
        io(&at, std::fs::write(&at, pretty))?;
        let note = d.join(NOTE);
        io(&note, std::fs::write(&note, note_text(d, &feature, &index)))?;
        io(&flat, std::fs::remove_file(&flat))?;
    }
    Ok(written)
}

/// An I/O result with its path named in the error.
fn io<T>(p: &Path, r: std::io::Result<T>) -> Result<T, String> {
    r.map_err(|e| format!("{}: {e}", p.display()))
}

/// The reader's note: what is where, how to find one task, and what not to do.
fn note_text(d: &Path, feature: &str, index: &Value) -> String {
    let number = feature.split('-').next().unwrap_or(feature);
    let mut out = format!(
        "# {feature} - its finished records, in parts\n\n\
Load this file when: you need a finished (ticked) task of feature {number} - its archived plan section, or its task line and verify\n\
note - or you are about to open, read or grep this feature's plan-done.md or tasks-done.md, which stand here in parts.\n\n\
WHY: these records grew to megabytes (451's plan-done.md 3.6 MB, its tasks-done.md 0.6 MB); a session that read or grepped one whole\n\
spent its context on it (the GM 2026-11-27; 451 T536, T537). `make archive-split` cut them, in their own order, into parts of about\n\
{BOUND} bytes (a task larger than that alone in its part); a part's name is its sequence and its lowest and highest id, and the ranges overlap, so find a task by index.json.\n\n\
## How to find one task\n\n\
- Its plan section: `make plan-section F={number} T=T<n>` - it opens only the part that holds the task.\n\
- Its part by hand: `index.json` here maps each task to its part(s) (`tasks` -> the record -> `T<n>`); read that part alone.\n\
- A task archived since the last fold is in the flat plan-done.md or tasks-done.md beside this directory (the tail; a tick folds it\n  in).\n\n\
## Do not\n\n\
- Read every part, `cat archive/*`, or Read a part when one task's section is all you need (`make plan-section`).\n\
- Grep this directory or the feature directory broadly: a common word matches thousands of lines. Grep with `-l` or `-c` first,\n  then read the one part it names.\n\
- Read the feature's plan-review.json whole: it is not cut here (451's stood at 5.0 MB; 462 T545 splits it). `make plan-section`\n  and `make plan-delta` read it for you.\n\n\
## The parts\n\n| record | part | bytes |\n|---|---|---|\n"
    );
    for record in RECORDS {
        for part in strings(&index["parts"][record]) {
            let bytes = std::fs::metadata(d.join(DIR).join(&part)).map_or(0, |m| m.len());
            _ = writeln!(out, "| {record} | `{part}` | {bytes} |");
        }
    }
    out
}

#[cfg(test)]
mod tests;
