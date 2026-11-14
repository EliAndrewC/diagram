//! `l7r-gate task-add <feature> [--section FILE] [--physical] [--performance]` - `make task-add`: a task box, and its plan section,
//! filed with the next free id (feature 385 T64, plan D83). Ported whole from `scripts/task-add.py` by feature 449 T135
//! (`ask:449-phase3-remainder`): the root and the feature's directory are the tick's own ([`crate::tick::repo_root`],
//! [`crate::tick::spec_dir`]), asked in process where the Python ran `l7r-gate tick --resolve`; the section's template is the plan
//! gate's ([`l7r_gate_plan::plan::template`]), which the approach gate reads too.
//!
//! WHY. The GM, 2026-10-18: inserting a task "somewhere in the middle of the task list ... sounds like something that could potentially
//! eat up a lot of tokens if we are doing it by hand. And hence why it should get tooling." Tasks T41-T64 were each added by a
//! hand-written insertion script of 1-2k tokens, and two hand-picked ids (T47, T48) collided with an umbrella heading.
//!
//! THE ID is one more than the highest id of the feature's own tasks in its tasks.md, plan.md and plan-done.md. THE BOX goes before
//! the GM-review box (as `claims-carry` places its boxes), else at the end, with its research line. THE SECTION, given, is a file whose
//! text has `{T}` for the id; it goes into plan.md before the feature's `## T<n> - the close` heading, else at the end. The title is
//! `TASK_TITLE`. NO LANDS-OPEN MARK OR LINE (feature 405 T32, D4; the GM 2026-10-20): a task nobody has started holds no landing, so a
//! task filed mid-feature needs neither.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_plan::plan::template::{PERFORMANCE, RED_EXIT, TEMPLATE};
use l7r_guard::shared::py_text::{strip, SPACE_CLASS};

use crate::tick::{repo_root, spec_dir};
use crate::{raised, read_strict, reply, write_file, Reply};

const PHYSICAL: &str = "      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited\n";

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

// Python's `\s` (its whitespace) and `\d` read as ASCII digits, which every task id is
static ID: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"(?m)^(?:[{SPACE_CLASS}]*- \[[ xX]\]|##) T([0-9]+)[a-z]?\b"
    ))
});
static GM_BOX: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \[[ x]\] GM review\b"));
static CLOSE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^## T[0-9]+ - the close\b"));

/// One more than the highest id of the feature's own tasks - its boxes and its plan's `## T<n>` sections - zero-padded as its ids are.
/// Never an id a title or a section merely QUOTES (feature 405 T31, D3): 405's moved titles name "(385 T147)", and reading every
/// `T<n>` gave its new tasks T148 on.
fn next_id(d: &Path) -> Result<String, String> {
    let mut text = String::new();
    for name in ["tasks.md", "plan.md", "plan-done.md"] {
        if d.join(name).is_file() {
            text += &read_strict(&d.join(name))?;
        }
    }
    let top = ID
        .captures_iter(&text)
        .flatten()
        .filter_map(|c| c[1].parse::<u128>().ok())
        .max()
        .unwrap_or(0);
    Ok(format!("T{:02}", top + 1))
}

fn add_box(tasks: &str, tid: &str, title: &str, physical: bool) -> String {
    let research = if physical { "physical" } else { "rendering" };
    let boxed = format!(
        "- [ ] {tid} {title}\n      research: {research}\n{}",
        if physical { PHYSICAL } else { "" }
    );
    match GM_BOX.find(tasks).ok().flatten() {
        Some(gm) => format!("{}{boxed}{}", &tasks[..gm.start()], &tasks[gm.start()..]),
        None => format!(
            "{tasks}{}{boxed}",
            if tasks.ends_with('\n') { "" } else { "\n" }
        ),
    }
}

fn add_section(plan: &str, tid: &str, section: &str) -> String {
    let body = format!("{}\n\n", section.replace("{T}", tid).trim_end_matches('\n'));
    match CLOSE.find(plan).ok().flatten() {
        Some(close) => format!("{}{body}{}", &plan[..close.start()], &plan[close.start()..]),
        None => format!(
            "{plan}{}\n{body}",
            if plan.ends_with('\n') { "" } else { "\n" }
        ),
    }
}

/// A section whose checklist item 6 does not route a red result through `make arbiter-ask`.
fn lacks_red_exit(section: &str) -> bool {
    let item6 = l7r_guard::shared::speckit::splitlines(section)
        .into_iter()
        .find(|ln| {
            ln.trim_start_matches(l7r_guard::shared::py_text::is_space)
                .starts_with("6.")
        })
        .unwrap_or("");
    !item6.contains("make arbiter-ask")
}

/// `l7r-gate task-add ...` from `cwd`, `title` what `TASK_TITLE` says.
#[must_use]
pub fn cli(words: &[String], cwd: &Path, title: &str) -> Reply {
    let physical = words.iter().any(|a| a == "--physical");
    let performance = words.iter().any(|a| a == "--performance");
    let mut args: Vec<String> = words
        .iter()
        .filter(|a| *a != "--physical" && *a != "--performance")
        .cloned()
        .collect();
    let mut section = String::new();
    if let Some(i) = args.iter().position(|a| a == "--section") {
        section = args.get(i + 1).cloned().unwrap_or_default();
        args.drain(i..(i + 2).min(args.len()));
    }
    let title = strip(title);
    if args.len() != 1 || title.is_empty() {
        return reply(
            String::new(),
            "usage: make task-add F=<feature> TITLE=\"<what the task does>\" [SECTION=<file with {T}>] [RESEARCH=physical] [PERF=1]\n"
                .to_owned(),
            2,
        );
    }
    let root = repo_root(cwd);
    let Some(d) = spec_dir(&root, &args[0]).filter(|d| d.join("tasks.md").is_file()) else {
        return reply(
            String::new(),
            format!(
                "task-add: no single specs/{}* directory with a tasks.md under {}\n",
                args[0],
                root.display()
            ),
            2,
        );
    };
    let section_path = cwd.join(&section);
    if !section.is_empty() && !section_path.is_file() {
        return reply(
            String::new(),
            format!("task-add: SECTION={section} is not a file\n"),
            2,
        );
    }
    match file(
        &root,
        &d,
        title,
        &section,
        &section_path,
        physical,
        performance,
    ) {
        Ok((out, err)) => reply(out, err, 0),
        Err((err, why)) => raised("task-add", String::new(), &err, &why),
    }
}

/// The box and the section written: what was printed, or what raised after what was printed.
fn file(
    root: &Path,
    d: &Path,
    title: &str,
    section: &str,
    section_path: &Path,
    physical: bool,
    performance: bool,
) -> Result<(String, String), (String, String)> {
    let mut err = String::new();
    let base = if section.is_empty() {
        TEMPLATE.to_owned()
    } else {
        read_strict(section_path).map_err(|why| (String::new(), why))?
    };
    let text = format!("{base}{}", if performance { PERFORMANCE } else { "" });
    if !section.is_empty() && lacks_red_exit(&text) {
        err = format!("task-add: SECTION={section}'s checklist item 6 has no red exit through `make arbiter-ask` - the plan review will ask for: {RED_EXIT}\n");
    }
    let fail = |why: String| (err.clone(), why);
    let tid = next_id(d).map_err(fail)?;
    let tasks = read_strict(&d.join("tasks.md")).map_err(fail)?;
    write_file(
        &d.join("tasks.md"),
        add_box(&tasks, &tid, title, physical).as_bytes(),
    )
    .map_err(fail)?;
    let plan = if d.join("plan.md").is_file() {
        read_strict(&d.join("plan.md")).map_err(fail)?
    } else {
        String::new()
    };
    write_file(
        &d.join("plan.md"),
        add_section(&plan, &tid, &text).as_bytes(),
    )
    .map_err(fail)?;
    let rel = d.strip_prefix(root).map_err(|_| {
        fail(format!(
            "ValueError: {:?} is not in the subpath of {:?}",
            d.join("tasks.md").display().to_string(),
            root.display().to_string()
        ))
    })?;
    let out = format!(
        "task-add: {tid} filed in {}, its section in {}{}\n",
        rel.join("tasks.md").display(),
        rel.join("plan.md").display(),
        if section.is_empty() {
            " (the template: fill each <...>)"
        } else {
            ""
        }
    );
    Ok((out, err))
}

#[cfg(test)]
mod tests;
