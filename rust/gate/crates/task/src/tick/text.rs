//! A task ticked in the text of its `tasks.md`, and its research boxes read (`tick-task.py`'s `tick`, `_is_boxes_line` and
//! `boxes_refusal`, feature 449 T131), each as the Python read the text: its lines by `str.splitlines`, its whitespace by `str.isspace`.

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::{is_space, repr, strip, SPACE_CLASS};
use l7r_guard::shared::speckit::splitlines;

/// Why a tick cannot be made: a refusal (`ValueError`, exit 2 where `make tick` reports it), or `--boxes` with no box to tick
/// (`SystemExit` with its message, exit 1).
#[derive(Debug, PartialEq, Eq)]
pub enum Refused {
    Value(String),
    Exit(String),
}

pub(crate) fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static PHYSICAL: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"^[{SPACE_CLASS}]+research:[{SPACE_CLASS}]*physical\b"
    ))
});

/// `str.splitlines(keepends=True)`: each line with its own boundary, `\r\n` one boundary.
pub(crate) fn lines_kept(text: &str) -> Vec<&str> {
    let mut out = Vec::new();
    let mut rest = text;
    while let Some(at) = rest.find(|c: char| {
        matches!(
            c,
            '\n' | '\r' | '\x0b' | '\x0c' | '\x1c'..='\x1e' | '\u{85}' | '\u{2028}' | '\u{2029}'
        )
    }) {
        let skip = if rest[at..].starts_with("\r\n") {
            2
        } else {
            rest[at..].chars().next().map_or(1, char::len_utf8)
        };
        out.push(&rest[..at + skip]);
        rest = &rest[at + skip..];
    }
    if !rest.is_empty() {
        out.push(rest);
    }
    out
}

/// `str.lstrip()`.
pub(crate) fn lstrip(text: &str) -> &str {
    text.trim_start_matches(is_space)
}

/// A RESEARCH-BOX LINE IS MATCHED BY SHAPE, NEVER BY ITS TEXT (feature 229: the literal three-box line matched nothing once the roster
/// grew to five, and `BOXES=1` reported a tick that ticked no box), AND ONE BOX A LINE, AS A TASK MAY BE WRITTEN (feature 291): an
/// indented line that is a checkbox. A task line itself starts at the margin.
pub(crate) fn is_boxes_line(line: &str) -> bool {
    line.chars().next().is_some_and(is_space) && lstrip(line).starts_with("- [")
}

fn tick_boxes(line: &str) -> String {
    if is_boxes_line(line) {
        line.replace("- [ ]", "- [x]")
    } else {
        line.to_owned()
    }
}

/// The task's line as `^- \[<mark>\] <task>\b` matches it, `marks` the characters the box may hold.
fn task_line(marks: &str, task: &str) -> Regex {
    re(&format!(r"^- \[{marks}\] {}\b", fancy_regex::escape(task)))
}

fn matches(pattern: &Regex, line: &str) -> bool {
    pattern.is_match(line).unwrap_or(false)
}

/// `tick(text, task, note, boxes)`: the new file text and the ticked task line, or why not. The note replaces the task's `verify:` text
/// whole, but not the research boxes below it, which are the task's own lines (feature 315: a tick cut T24's and T30's five boxes).
///
/// # Errors
/// The refusal, as [`Refused`].
pub fn tick(text: &str, task: &str, note: &str, boxes: bool) -> Result<(String, String), Refused> {
    let note = strip(note);
    if note.is_empty() {
        return Err(Refused::Value(
            "the verify note is empty - say what was verified (NOTE=...)".to_owned(),
        ));
    }
    let lines = lines_kept(text);
    let (open, done) = (task_line(" ", task), task_line("x", task));
    let Some(start) = lines.iter().position(|l| matches(&open, l)) else {
        if lines.iter().any(|l| matches(&done, l)) {
            return Err(Refused::Value(format!("{task} is already ticked")));
        }
        return Err(Refused::Value(format!("no open task {task} in tasks.md")));
    };
    let end = (start + 1..lines.len())
        .find(|&i| lines[i].starts_with("- [") || lines[i].starts_with("## "))
        .unwrap_or(lines.len());
    let mut block: Vec<String> = lines[start..end].iter().map(|l| (*l).to_owned()).collect();
    block[0] = format!("- [x]{}", &block[0]["- [ ]".len()..]);
    // the blank lines that separate this task from a section heading are not part of it
    let mut trail: Vec<String> = Vec::new();
    while block.len() > 1 && strip(&block[block.len() - 1]).is_empty() {
        trail.insert(0, block.pop().unwrap_or_default());
    }
    match block.iter().position(|l| lstrip(l).starts_with("verify:")) {
        None => {
            // a task written without a verify line gets one, after its last line
            let last = block.len() - 1;
            if !block[last].ends_with('\n') {
                block[last].push('\n');
            }
            block.push(format!("      verify: DONE. {note}\n"));
        }
        Some(at) => {
            let line = &block[at];
            let indent = line[..line.len() - lstrip(line).len()].to_owned();
            let kept: Vec<String> = block[at + 1..]
                .iter()
                .filter(|l| is_boxes_line(l))
                .cloned()
                .collect();
            block.truncate(at + 1);
            block.extend(kept);
            block[at] = format!("{indent}verify: DONE. {note}\n");
        }
    }
    block.extend(trail);
    if boxes {
        let ticked: Vec<String> = block.iter().map(|l| tick_boxes(l)).collect();
        // AND IT SAYS SO WHEN IT DOES NOTHING: asked to tick the boxes, the script once found no line to tick and still reported the task
        // ticked
        if ticked == block {
            return Err(Refused::Exit(format!(
                "--boxes: no research-box line found in {} - is this a `research: physical` task?",
                repr(strip(&block[0]))
            )));
        }
        block = ticked;
    }
    let first = block[0].trim_end_matches('\n').to_owned();
    let new = [
        lines[..start].concat(),
        block.concat(),
        lines[end..].concat(),
    ]
    .concat();
    Ok((new, first))
}

/// Why `task` may not be ticked: a `research: physical` task with a research box unticked, unless this tick ticks them (`--boxes`).
/// 408 T01/T02 were ticked so and only the gate's research-box test saw it - after the push, on the next session's landing.
#[must_use]
pub fn boxes_refusal(text: &str, task: &str, boxes: bool) -> String {
    let lines = splitlines(text);
    let any = task_line("[ xX]", task);
    let Some(at) = lines.iter().position(|l| matches(&any, l)) else {
        return String::new();
    };
    if boxes {
        return String::new();
    }
    let rest = &lines[at + 1..];
    let k = rest
        .iter()
        .position(|l| l.starts_with("- [") || l.starts_with('#'))
        .unwrap_or(lines.len());
    let block: Vec<&str> = std::iter::once(lines[at])
        .chain(rest.iter().take(k).copied())
        .collect();
    let physical = block.iter().any(|l| matches(&PHYSICAL, l));
    if physical
        && block[1..]
            .iter()
            .any(|l| is_boxes_line(l) && l.contains("- [ ]"))
    {
        return format!("{task} is a `research: physical` task with a research box unticked - verify each, then tick with BOXES=1 (make tick F=<n> T={task} BOXES=1 NOTE=..., or make land ... BOXES=1)");
    }
    String::new()
}

#[cfg(test)]
mod tests;
