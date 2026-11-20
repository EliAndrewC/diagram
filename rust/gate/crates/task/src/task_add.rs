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
//! THE ID is one more than the highest id of the feature's own tasks in its tasks.md, tasks-done.md (the ticked tasks `make tick`
//! archives, feature 449 T142: an id there is taken), plan.md and plan-done.md. THE BOX goes before
//! the GM-review box (as `claims-carry` places its boxes), else at the end, with its research line. THE SECTION, given, is a file whose
//! text has `{T}` for the id; it goes into plan.md before the feature's `## T<n> - the close` heading, else at the end. The title is
//! `TASK_TITLE`. NO LANDS-OPEN MARK OR LINE (feature 405 T32, D4; the GM 2026-10-20): a task nobody has started holds no landing, so a
//! task filed mid-feature needs neither.
//!
//! MAKE QUICK OVER WHAT IT WROTE (feature 451 T19, D16; FR-011): the box and section written, quick's checks run over them
//! ([`quick`]); on a red they run again with both files as they were, and where the with-line run has a failure the other lacks, the
//! files stay as they were and the filing is refused, naming those failures; a red the same without the line is reported as already
//! there and the line kept. `QUICK_OK="<reason>"` files it anyway, recorded by the tool in the guard log (`make guard-log
//! GUARD=task-add`), as `PERF_LATER_OK` is by `make task-start`.

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_plan::plan::template::{PERFORMANCE, RED_EXIT, TEMPLATE};
use l7r_guard::shared::escape::enough;
use l7r_guard::shared::log::Entry;
use l7r_guard::shared::py_text::{strip, SPACE_CLASS};
use serde_json::Value;

use crate::tick::text::re;
use crate::tick::{repo_root, spec_dir};
use crate::{raised, read_strict, reply, write_file, Reply};

const PHYSICAL: &str = "      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited\n";

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
    for name in [
        "tasks.md",
        l7r_guard::shared::speckit::tasks::DONE,
        "plan.md",
        "plan-done.md",
    ] {
        if d.join(name).is_file() {
            text += &read_strict(&d.join(name))?;
        }
    }
    let top = ID
        .captures_iter(&text)
        .map_while(Result::ok)
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

/// `l7r-gate task-add ...` from `cwd`, `title` what `TASK_TITLE` says; `QUICK_OK` from the environment.
#[must_use]
pub fn cli(words: &[String], cwd: &Path, title: &str) -> Reply {
    cli_with(words, cwd, title, &|k| std::env::var(k).ok())
}

/// One guard-log entry of quick's refusal or its escape (`make guard-log GUARD=task-add`, `make audit`); never fails.
fn record(event: &str, detail: &str, rule: &str) {
    let detail: String = detail.chars().take(400).collect();
    let _ = l7r_guard::shared::log::write(&Entry {
        guard: "task-add",
        event,
        detail: &detail,
        rule,
        context: None,
        input: &Value::Null,
        session_name: "",
    });
}

/// [`cli`] with the environment's variables read through `env` (a closure in the tests).
pub(crate) fn cli_with(words: &[String], cwd: &Path, title: &str, env: crate::tick::Env) -> Reply {
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
    let quick_ok = env("QUICK_OK")
        .map(|w| strip(&w).to_owned())
        .unwrap_or_default();
    if !quick_ok.is_empty() && !enough(&quick_ok) {
        record("blocked", &quick_ok, "QUICK_OK-no-reason");
        return reply(String::new(), "task-add: QUICK_OK needs a REASON, not just a value - two words and eight characters: why this line is filed although make quick's checks fail on it (feature 451 T19)\n".to_owned(), 2);
    }
    let lines = match quick::lines(&root) {
        Ok(lines) => lines,
        Err(why) => return reply(String::new(), format!("task-add: refused, nothing written - make quick's checks cannot be listed, so what it writes cannot be checked (feature 451 T19): {why}\nRun it from the repository, whose Makefile has `quick:`.\n"), 2),
    };
    let was = [d.join("tasks.md"), d.join("plan.md")].map(|p| std::fs::read(&p).ok());
    match file(
        &root,
        &d,
        title,
        &section,
        &section_path,
        physical,
        performance,
    ) {
        Ok((out, err, tid)) => checked(&root, &d, &lines, &was, (out, err, &tid), &quick_ok)
            .unwrap_or_else(|why| raised("task-add", String::new(), "", &why)),
        Err((err, why)) => raised("task-add", String::new(), &err, &why),
    }
}

/// `path` as `bytes` say, or gone when they are `None`.
fn put_back(path: &Path, bytes: Option<&Vec<u8>>) -> Result<(), String> {
    match bytes {
        Some(b) => write_file(path, b),
        None => std::fs::remove_file(path).map_err(|e| format!("{}: {e}", path.display())),
    }
}

/// Quick's checks over what [`file`] wrote (D16): kept when green or red as before the line; else withdrawn - `was`, the two files'
/// bytes before it - and refused, unless `QUICK_OK` gives a reason.
fn checked(
    root: &Path,
    d: &Path,
    lines: &[String],
    was: &[Option<Vec<u8>>; 2],
    (mut out, mut err, tid): (String, String, &str),
    quick_ok: &str,
) -> Result<Reply, String> {
    let with = quick::run(root, lines);
    if with.is_empty() {
        let _ = writeln!(
            out,
            "task-add: make quick's checks over it: clean ({} run)",
            lines.len()
        );
        return Ok(reply(out, err, 0));
    }
    let paths = [d.join("tasks.md"), d.join("plan.md")];
    let now = [std::fs::read(&paths[0]).ok(), std::fs::read(&paths[1]).ok()];
    for (p, b) in paths.iter().zip(was) {
        put_back(p, b.as_ref())?;
    }
    let without = quick::run(root, lines);
    let added = quick::introduced(&with, &without);
    let name = d.file_name().unwrap_or_default().to_string_lossy();
    let listed: String = added.iter().map(quick::Failure::shown).collect();
    if added.is_empty() || !quick_ok.is_empty() {
        for (p, b) in paths.iter().zip(&now) {
            put_back(p, b.as_ref())?;
        }
    }
    if added.is_empty() {
        let already: String = with.iter().map(quick::Failure::shown).collect();
        let _ = write!(err, "task-add: make quick is already red, and not by {tid} - the same failures without it, so it is kept:\n{already}");
        return Ok(reply(out, err, 0));
    }
    if !quick_ok.is_empty() {
        record("escaped", &format!("{name} {tid}: {quick_ok}"), "quick-ok");
        let _ = write!(err, "task-add: QUICK_OK taken (recorded) - {tid} kept although make quick's checks fail on it:\n{listed}");
        return Ok(reply(out, err, 0));
    }
    record(
        "blocked",
        &format!("{name} {tid}: {}", listed.trim()),
        "quick-red",
    );
    let number = name.split('-').next().unwrap_or_default();
    Ok(reply(String::new(), format!("{err}task-add: refused - {tid} withdrawn, tasks.md and plan.md as they were: make quick's checks fail on what it wrote and not without it (feature 451 FR-011):\n{listed}Fix the title or the section and file it again: make task-add F={number} TITLE=\"...\" - or file it anyway: make task-add F={number} TITLE=\"...\" QUICK_OK=\"<reason>\" (recorded)\n"), 2))
}

/// The box and the section written: what was printed and the id, or what raised after what was printed.
fn file(
    root: &Path,
    d: &Path,
    title: &str,
    section: &str,
    section_path: &Path,
    physical: bool,
    performance: bool,
) -> Result<(String, String, String), (String, String)> {
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
    Ok((out, err, tid))
}

mod quick;

#[cfg(test)]
mod tests;
