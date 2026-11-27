//! A feature's tasks, the open ones in `tasks.md` and the ticked ones archived in `tasks-done.md` (feature 449 T142).
//!
//! WHY (the GM, 2026-11-15: "please do that, because I imagine that will make our long-running featuers with tons of tasks much more
//! token efficient"). 449's tasks.md held 131 ticked tasks of 137, about 63 KB, read whole by every session and agent that opened it to
//! find the six still open. A ticked task is finished text: the tick moves its block - its `- [x] Tnn` line and the indented lines
//! under it - into `tasks-done.md`, as the tick already moves a finished plan section from plan.md to plan-done.md (feature 385 T63).
//!
//! THE ONE READER (FR-003). Every reader that needs the ticked tasks - the spec-kit state, the next free id, the closing check, the
//! tick's own "already ticked", the research boxes, the feature report, the push's plan check, the feature-approval guard - reads both
//! files through [`all_text`] (or [`joined`], where the texts come from `git show`); a reader of the open tasks alone reads tasks.md as
//! before. It lives here, in the guard, because the guard cannot build on the gate's crates and both read it.
//!
//! WHAT MOVES, AND WHAT STAYS (feature 449 T142's decisions):
//! - every ticked task with an id (`- [x] T<n>`) whose lines hold no open box: a ticked task with a box still open under it is not
//!   done (feature 330's indented rule) and still holds a landing (`holding_with` reads it in tasks.md), so it stays;
//! - NO "most recent few" are kept: nothing reads a ticked task from tasks.md - the tick prints what it moved, the land's commit names
//!   it, `git log` holds its time and the verify note travels with its block - so a kept window would be a number with no reason;
//! - the GM-review box (`- [ ] GM review (make gm-reviewed F=<n>) [lands-open]`) has no task id and never moves: `make gm-reviewed`,
//!   `ensure_box` and the state rule's "landed, the GM's box open" read it in tasks.md; nor do the phase headings, the `## Occasions`
//!   section the reviews read, or any prose;
//! - tasks-done.md holds the blocks in task order (by id), each byte for byte, under one header line; tasks.md gets ONE pointer line
//!   under its title. No marker is left where a block stood: the tick ends a task's block at the next column-0 `- [` or `## ` and keeps
//!   only box lines after its `verify:` line, so a column-0 marker below a task would be eaten by that task's next tick.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::{re, read_text};

/// The open tasks' file.
pub const OPEN: &str = "tasks.md";
/// The archived tasks' file.
pub const DONE: &str = "tasks-done.md";
/// The one line tasks.md carries once a task has moved.
pub const POINTER: &str = "Ticked tasks are archived in `tasks-done.md` (feature 449 T142): `make tick` moves each ticked task there with its lines; this file holds the open ones.";

static TICKED: LazyLock<Regex> = LazyLock::new(|| re(r"^- \[[xX]\] (T(\d+)([a-z]?))\b"));
static ANY_BOX: LazyLock<Regex> = LazyLock::new(|| re(r"^- \[[ xX]\] "));

/// The text of `path` where it is a file, else "".
fn text_if_file(path: &Path) -> Result<String, String> {
    if path.is_file() {
        read_text(path)
    } else {
        Ok(String::new())
    }
}

/// The archived tasks of feature directory `d` ("" where there are none).
///
/// # Errors
/// A tasks-done.md that cannot be read.
pub fn done_text(d: &Path) -> Result<String, String> {
    if d.join(super::archive::DIR).is_dir() {
        // split into parts (451 T537): every part, then the flat tail
        return Ok(super::archive::text(&super::archive::files(d), DONE));
    }
    text_if_file(&d.join(DONE))
}

/// The open tasks' text and the archived ones', as one text for a reader that counts or finds tasks (never for one that writes back): a
/// newline between them, so the last line of one never runs into the first of the other.
#[must_use]
pub fn joined(open: &str, done: &str) -> String {
    if done.is_empty() {
        return open.to_owned();
    }
    let gap = if open.is_empty() || open.ends_with('\n') {
        ""
    } else {
        "\n"
    };
    format!("{open}{gap}{done}")
}

/// Every task of `d`, open and archived ([`joined`]).
///
/// # Errors
/// A tasks.md or tasks-done.md that cannot be read.
pub fn all_text(d: &Path) -> Result<String, String> {
    Ok(joined(&text_if_file(&d.join(OPEN))?, &done_text(d)?))
}

/// Does the archived text hold `task` ticked?
#[must_use]
pub fn archived(done: &str, task: &str) -> bool {
    done.lines().any(|l| {
        TICKED
            .captures(l)
            .ok()
            .flatten()
            .is_some_and(|c| &c[1] == task)
    })
}

/// A task's place in task order: its number, then its letter; a block with no id after every one that has.
fn order(block: &str) -> (u128, String) {
    TICKED
        .captures(block.lines().next().unwrap_or(""))
        .ok()
        .flatten()
        .map_or((u128::MAX, String::new()), |c| {
            (c[2].parse().unwrap_or(u128::MAX), c[3].to_owned())
        })
}

fn blank(line: &str) -> bool {
    line.trim().is_empty()
}

fn indented(line: &str) -> bool {
    line.starts_with([' ', '\t']) && !blank(line)
}

/// Where the block starting at line `at` ends: its indented lines, and a blank run only where an indented line follows it (old features
/// wrote a task's notes in paragraphs); the blank lines after it are not its own.
fn block_end(lines: &[&str], at: usize) -> usize {
    let mut end = at + 1;
    let mut i = at + 1;
    while i < lines.len() {
        if indented(lines[i]) {
            i += 1;
            end = i;
        } else if blank(lines[i]) {
            i += 1;
        } else {
            break;
        }
    }
    end
}

/// The ticked blocks of `open` that may move, as (first line, end) line ranges.
fn movable(lines: &[&str]) -> Vec<(usize, usize)> {
    let mut out = Vec::new();
    let mut i = 0;
    while i < lines.len() {
        if TICKED.is_match(lines[i]).unwrap_or(false) {
            let end = block_end(lines, i);
            if !lines[i + 1..end].iter().any(|l| l.contains("- [ ]")) {
                out.push((i, end));
            }
            i = end;
        } else {
            i += 1;
        }
    }
    out
}

/// The blocks of an archive: from each column-0 box to the next, their trailing blank lines dropped; and the header above the first.
fn split_done(done: &str) -> (String, Vec<String>) {
    let mut head = String::new();
    let mut blocks: Vec<String> = Vec::new();
    for line in done.split_inclusive('\n') {
        if ANY_BOX.is_match(line).unwrap_or(false) {
            blocks.push(String::new());
        }
        match blocks.last_mut() {
            Some(b) => b.push_str(line),
            None => head.push_str(line),
        }
    }
    for b in &mut blocks {
        let kept = b.trim_end().len();
        b.truncate(kept);
        b.push('\n');
    }
    (head, blocks)
}

/// tasks.md with the pointer line under its title (or at its top), once.
fn with_pointer(text: &str) -> String {
    if text.lines().any(|l| l == POINTER) {
        return text.to_owned();
    }
    let mut lines: Vec<&str> = text.split_inclusive('\n').collect();
    let at = match lines.iter().position(|l| l.starts_with("# ")) {
        Some(h) if lines.get(h + 1).is_some_and(|l| blank(l)) => h + 2,
        Some(h) => {
            lines.insert(h + 1, "\n");
            h + 2
        }
        None => 0,
    };
    let line = format!("{POINTER}\n");
    lines.insert(at, "\n");
    lines.insert(at, &line);
    lines.concat()
}

/// What moves: (tasks.md's new text, tasks-done.md's new text, the ids moved in task order), or None when no ticked task may move.
/// `name` is the feature directory's name, for a new archive's header.
#[must_use]
pub fn archive_text(open: &str, done: &str, name: &str) -> Option<(String, String, Vec<String>)> {
    let lines: Vec<&str> = open.split_inclusive('\n').collect();
    let moving = movable(&lines);
    if moving.is_empty() {
        return None;
    }
    let mut kept = String::new();
    let mut moved: Vec<String> = Vec::new();
    let mut next = 0;
    for &(start, end) in &moving {
        kept.extend(lines[next..start].iter().copied());
        let mut block = lines[start..end].concat();
        if !block.ends_with('\n') {
            block.push('\n');
        }
        moved.push(block);
        next = end;
        // the blank line that separated the block from what came before goes with it where a blank line follows too
        if kept.ends_with("\n\n") || kept.is_empty() {
            while lines.get(next).is_some_and(|l| blank(l)) {
                next += 1;
            }
        }
    }
    kept.extend(lines[next..].iter().copied());
    let (mut head, mut blocks) = split_done(done);
    if head.trim().is_empty() {
        head = format!("# {name} - the ticked tasks, archived by `make tick` (feature 449 T142; the open ones are in tasks.md)\n\n");
    }
    let mut ids: Vec<&String> = moved.iter().collect();
    ids.sort_by_key(|b| order(b));
    let ids: Vec<String> = ids
        .into_iter()
        .filter_map(|b| TICKED.captures(b).ok().flatten().map(|c| c[1].to_owned()))
        .collect();
    blocks.extend(moved);
    // a stable sort: an id archived twice keeps both blocks, in the order they came, for the spec lint's check 7 to name
    blocks.sort_by_key(|b| order(b));
    Some((
        with_pointer(&kept),
        format!("{head}{}", blocks.concat()),
        ids,
    ))
}

/// Move every ticked task of `d` that may move from tasks.md to tasks-done.md ([`archive_text`]); the ids moved, none when tasks.md is
/// absent or nothing may move. The archive is written first: a failure between the two writes leaves a task in both files, which the
/// spec lint's duplicate check names, never in neither.
///
/// # Errors
/// A file that cannot be read or written.
pub fn archive(d: &Path) -> Result<Vec<String>, String> {
    let path = d.join(OPEN);
    if !path.is_file() {
        return Ok(Vec::new());
    }
    let name = super::py_name(d);
    // the flat tail alone: a split feature's parts are folded, never rewritten (451 T537)
    let Some((open, done, ids)) =
        archive_text(&read_text(&path)?, &text_if_file(&d.join(DONE))?, &name)
    else {
        return Ok(Vec::new());
    };
    let write =
        |p: &Path, t: &str| std::fs::write(p, t).map_err(|e| format!("{}: {e}", p.display()));
    write(&d.join(DONE), &done)?;
    write(&path, &open)?;
    Ok(ids)
}

#[cfg(test)]
mod tests;
