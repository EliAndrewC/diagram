//! `l7r-gate plan section <feature> <task[,task]> [--cited]` (451 T501, `make plan-section`): exactly a task's plan sections - every
//! heading of its own, a bundle heading naming it included - from plan.md, or from plan-done.md for an archived task, and with `--cited`
//! the sections those name by task id, one level. WHY: builders read their sections by grep and sed over the whole plan, 3.68 MB of plan
//! text in their tool results over 2026-11-26/27, 14.7% of them (451 T499, `dev/measurements/2026-11-27/plan-reads/results.md`), and
//! each result is paid again as cached input every later turn (the GM 2026-11-27: token cost is as important as task throughput).

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::Path;

use super::sections::{blocks, leading_tasks, strip_archive, task_sections, TASK_ID};

/// The files a task's sections are looked for in, in order: the live plan, then its archive.
const FILES: [&str; 2] = ["plan.md", "plan-done.md"];

/// Each file's sections, parsed on first need: plan-done.md (3.1 MB for 451) only for a task plan.md has no section of.
struct Plans<'a> {
    dir: &'a Path,
    parsed: [Option<BTreeMap<String, String>>; 2],
}

impl Plans<'_> {
    /// (the file, the task's own section), or None where neither file holds a heading of the task's own. `task_sections` gives a task
    /// with no heading of its own the first heading that mentions it, which is another task's section, so that is no section here.
    fn find(&mut self, task: &str) -> Option<(&'static str, String)> {
        for (name, slot) in FILES.iter().zip(self.parsed.iter_mut()) {
            let sections = slot.get_or_insert_with(|| {
                task_sections(&std::fs::read_to_string(self.dir.join(name)).unwrap_or_default())
            });
            let text = sections.get(task).map_or("", String::as_str);
            let title = text
                .lines()
                .next()
                .unwrap_or("")
                .trim_start_matches('#')
                .trim();
            if leading_tasks(title).contains(&task) {
                return Some((name, text.to_owned()));
            }
        }
        None
    }
}

/// The task ids `text` names, in order, once each, but `skip` and an id another feature's number qualifies (`449 T92` in 451's plan is
/// 449's task, not 451's T92), across a line break too, and across a list of its ids ("449 T92, T93 and T94": all three 449's; the
/// plan review's round 1 on T501) - a list's ids parted only by commas, dashes, spaces, line breaks, "and" or "or".
pub(super) fn cited(text: &str, feature: &str, skip: &[String]) -> Vec<String> {
    let mut named: Vec<String> = Vec::new();
    let (mut end, mut number) = (None, "");
    for m in TASK_ID.find_iter(text).map_while(Result::ok) {
        let listed = end.is_some_and(|e| {
            text[e..m.start()]
                .split([' ', '\n', ',', '-'])
                .all(|w| matches!(w, "" | "and" | "or"))
        });
        if !listed {
            // a hard-wrapped plan puts "449" at a line's end and "T92" on the next, after its indent
            let before = text[..m.start()].trim_end_matches([' ', '\n']);
            number = &before[before.trim_end_matches(|c: char| c.is_ascii_digit()).len()..];
        }
        end = Some(m.end());
        let id = m.as_str().to_owned();
        if (number.is_empty() || number == feature) && !skip.contains(&id) && !named.contains(&id) {
            named.push(id);
        }
    }
    named
}

/// `section <feature> <task[,task]> [--cited]`: the feature's plan must exist; any fourth word but `--cited` is refused with the usage.
pub(super) fn cli(words: &[String], root: &Path) -> crate::Reply {
    let Some(dir) = super::resolve(&words[1], root).filter(|d| d.join("plan.md").is_file()) else {
        return super::fail(
            format!(
                "section: no single specs/{}* directory with a plan.md\n",
                words[1]
            ),
            2,
        );
    };
    match words.get(3).map(String::as_str) {
        None => super::said(show(&dir, &words[2], false)),
        Some("--cited") => super::said(show(&dir, &words[2], true)),
        Some(_) => super::fail(super::USAGE, 2),
    }
}

/// The output for `words` (`<task[,task]>`, a bare number read as its id) of the feature at `dir`.
pub(super) fn show(dir: &Path, words: &str, cite: bool) -> String {
    let feature = dir.file_name().unwrap_or_default().to_string_lossy();
    let feature = feature.split('-').next().unwrap_or("");
    let tasks: Vec<String> = words
        .split([',', ' '])
        .filter(|w| !w.is_empty())
        .map(|w| {
            if w.starts_with('T') {
                w.to_owned()
            } else {
                format!("T{w}")
            }
        })
        .collect();
    let mut plans = Plans {
        dir,
        parsed: [None, None],
    };
    let mut printed: Vec<String> = Vec::new();
    let mut out = String::new();
    let mut found: Vec<(&str, Vec<String>)> = Vec::new();
    for task in &tasks {
        match plans.find(task) {
            Some((file, text)) => {
                out += &section(&format!("{task} ({file})"), &text, &mut printed);
                found.push((task, cited(&text, feature, &tasks)));
            }
            None => {
                _ = writeln!(
                    out,
                    "{task}: no section of its own in plan.md or plan-done.md"
                );
            }
        }
    }
    if cite {
        let mut missing: Vec<String> = Vec::new();
        let mut ids: Vec<(&str, &String)> = Vec::new();
        for (task, named) in &found {
            ids.extend(
                named
                    .iter()
                    .filter(|id| !ids.iter().any(|(_, seen)| seen == id))
                    .map(|id| (*task, id))
                    .collect::<Vec<_>>(),
            );
        }
        for (by, id) in ids {
            match plans.find(id) {
                Some((file, text)) => {
                    out += &section(
                        &format!("{id} ({file}, cited by {by})"),
                        &text,
                        &mut printed,
                    );
                }
                None => missing.push(id.clone()),
            }
        }
        if !missing.is_empty() {
            _ = writeln!(
                out,
                "cited with no section of its own: {}",
                missing.join(", ")
            );
        }
    }
    out
}

/// `text`'s blocks under the line `==> <label>`, but a block already printed for another task (a bundle's shared heading), the archive's
/// marker lines dropped; a section all of whose blocks are printed is said so in its label's line.
fn section(label: &str, text: &str, printed: &mut Vec<String>) -> String {
    let mut body = String::new();
    for (_, block, _) in blocks(text) {
        if !block.is_empty() && !printed.contains(&block) {
            body += &strip_archive(&block);
            printed.push(block);
        }
    }
    if body.is_empty() {
        format!("==> {label}: its sections are printed above\n")
    } else {
        format!("==> {label}\n{body}")
    }
}
