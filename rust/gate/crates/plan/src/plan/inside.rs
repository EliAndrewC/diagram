//! A TASK BUILT INSIDE ANOTHER TASK'S SECTION (feature 451 T307 part 2). A filed task whose work a builder did inside another task's
//! reviewed section - T393 in T391, T398 in T394, T366 in T359, T395 and half of T297 in T313, T410 in T308 (2026-11-26/27) - had no
//! way out: its plan stub stood unfilled, so its tick was refused (no review, no Approach block), and `make task-withdraw` refused it
//! for its carried code. Its way out: the host's section says so in a line of its own, `Built here: T<n> - <what>`, which `make decide`
//! holds to an open box with an unfilled stub ([`lint`](super::lint)'s `BuiltHere`) and the host's plan review therefore reads and
//! rules on; and a landing of both (or of the task alone, its host already ticked) ticks it with ` built inside T<host>` appended to its
//! box, its stub removed - the tick's own work, `l7r_gate_task::tick`, which asks [`built_inside`] here.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::history::History;
use super::sections::{re, task_sections};
use super::status::{section_clear, section_current, RECORD};
use super::template::without_stub;

/// The line, at a line's start or as a list item: `Built here: T<n> - <what>`, `<what>` not empty.
static LINE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^(?:- )?Built here: (T[0-9]+[a-z]?) - (\S[^\n]*)$"));

/// Each `Built here:` line of `section`: (its offset, the task it names, what was built).
pub(super) fn named(section: &str) -> Vec<(usize, String, String)> {
    LINE.captures_iter(section)
        .map_while(Result::ok)
        .filter_map(|c| {
            Some((
                c.get(0)?.start(),
                c[1].to_owned(),
                c[2].trim_end().to_owned(),
            ))
        })
        .collect()
}

/// The words the tick appends to a task's box built inside `host`: its line then ends ` built inside T<host>`.
#[must_use]
pub fn box_suffix(host: &str) -> String {
    format!(" built inside {host}")
}

/// The task a box was BUILT INSIDE, or None: ticked, its line ending [`box_suffix`] - THE ONE RULE OF THE FORM, which the tick writes
/// and the plan gate's scope reads as it reads a withdrawal (`shared::speckit::withdrawn_box`): nothing was decided in the task's own
/// section. Anchored at the line's end, so a title that only says the words (`a task built inside T391 ...`) is none.
#[must_use]
pub fn built_inside_box(line: &str) -> Option<&str> {
    static END: LazyLock<Regex> =
        LazyLock::new(|| re(r"^[ \t]*- \[[xX]\] .* built inside (T[0-9]+[a-z]?)[ \t\r\n]*$"));
    let found = END.captures(line).ok().flatten()?;
    found.get(1).map(|m| m.as_str())
}

/// The task whose section names a task built inside it, and what its review says.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Host {
    /// The host task's id.
    pub task: String,
    /// What the `Built here:` line says was built.
    pub what: String,
    /// Its section carries a current CLEAR verdict, read as the archive reads one ([`task_current`] or [`section_clear`]).
    pub clear: bool,
    /// Its section stands in plan-done.md (archived at its tick), not plan.md.
    pub archived: bool,
}

/// The task whose section in `dir`'s plan.md - or plan-done.md, where its tick archived it before this task's - names `task` in a
/// `Built here:` line; None where no section does. A task's own section naming itself is no host. The first found: plan.md's
/// sections in id order, then plan-done.md's.
#[must_use]
pub fn built_inside(dir: &Path, task: &str) -> Option<Host> {
    let read = |name: &str| std::fs::read_to_string(dir.join(name)).unwrap_or_default();
    let plan_path = dir.join("plan.md");
    let review: serde_json::Value =
        serde_json::from_str(&read(RECORD)).unwrap_or(serde_json::Value::Null);
    let history = History::new(&plan_path, "HEAD");
    // an archived section is read without history: its text moved byte for byte, so its recorded digest still holds
    for (text, history, archived) in [
        (read("plan.md"), Some(&history), false),
        (read("plan-done.md"), None, true),
    ] {
        for (host, section) in task_sections(&text) {
            let Some((_, _, what)) = named(&section).into_iter().find(|(_, t, _)| t == task) else {
                continue;
            };
            if host == task {
                continue;
            }
            let clear = section_current(&review, &text, &host, &section, history)
                || section_clear(&review, &section, history);
            return Some(Host {
                task: host,
                what,
                clear,
                archived,
            });
        }
    }
    None
}

/// What `make decide` says of each `Built here:` line of `section`, the plan of `members`: (its span, why it does not stand). A line
/// stands where it names an OPEN box of tasks.md whose plan section is its unfilled stub or none ([`without_stub`]) - or, the section
/// decided again later, a box already ticked built inside one of `members` ([`built_inside_box`]). WHY judged here: the host's review
/// is the only one the absorbed task's work gets, so the line must name a task whose landing would remove nothing anybody decided.
pub(super) fn decide_findings(
    spec_dir: &Path,
    section: &str,
    members: &[String],
) -> Vec<((usize, usize), String)> {
    let read = |name: &str| std::fs::read_to_string(spec_dir.join(name)).unwrap_or_default();
    let (plan, tasks) = (read("plan.md"), read("tasks.md") + &read("tasks-done.md"));
    let mut out = Vec::new();
    for (at, task, what) in named(section) {
        let shown = format!("Built here: {task} - {what}");
        let span = (at, at + shown.len());
        let boxed = tasks.lines().find(|l| {
            l.starts_with("- [")
                && l.get(6..)
                    .is_some_and(|r| r.split_whitespace().next() == Some(&task))
        });
        let why = match boxed {
            _ if members.contains(&task) => format!("{task} is a task this section itself decides"),
            None => format!("{task} is no filed task of tasks.md or tasks-done.md"),
            Some(line) if line.starts_with("- [ ] ") => {
                if without_stub(&plan, &task).is_ok() {
                    continue;
                }
                format!("{task}'s plan section has been filled in: a task built here keeps only its unfilled stub, which its landing removes - empty it back to its template, or decide it on its own and drop this line")
            }
            Some(line) => {
                if built_inside_box(line).is_some_and(|h| members.iter().any(|m| m == h)) {
                    continue;
                }
                format!("{task} is ticked, and not built inside this section's task - it decides nothing here")
            }
        };
        out.push((span, format!("{why}: '{shown}'")));
    }
    out
}

#[cfg(test)]
mod tests;
