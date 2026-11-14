//! `l7r-gate tick <feature> <task> <note> [--boxes] [--note-from-env] [--landing]` - `make tick`: ONE task ticked in a spec-kit feature's
//! tasks.md, with its verify note. Ported from `scripts/tick-task.py` by feature 449 T131 (`ask:449-phase3-remainder` Q2 task A), every
//! refusal and line as the Python had them, the usage text naming `tick-task.py` byte for byte (`ask:449-usage-text`).
//!
//! WHY (feature 188, GM 2026-09-05: *"The idea of a make tick helper. does indeed seem good. So we should go ahead and do that."*). The
//! session that measured the cost of a one-line CSS change found about a third of its model turns were bookkeeping: hand-rolled regex
//! scripts to tick a task, two of which matched nothing and wrote nothing, and one heredoc that truncated a task file before reading it.
//! A single-purpose tool that REFUSES rather than guesses removes the class.
//!
//! `note` becomes `verify: DONE. <note>`; `--boxes` ticks a physical task's research boxes; `--note-from-env` takes the note from
//! `$TICK_NOTE`, because a note quoting code in backticks must never pass through a shell that would run it; `--landing` is `make land`'s
//! tick, written before the push that carries it, for a task named in `L7R_LAND_TICKS`. Refusals exit 2 and write nothing. The last tick
//! closes the feature only past the closing check (feature 375 FR-009/FR-014), and a tick archives the plan's finished sections (feature
//! 385 T63). `--land-check <feature> <note> <task>... [--boxes]` prints, as JSON, what `make land`'s first pass asks of each task, which
//! the land asks in process ([`land_check`]); `--resolve <feature>` prints the repository root and the feature's directory as JSON, no run
//! recorded - its caller `scripts/task-add.py` ported in T135 and asks [`repo_root`] and [`spec_dir`] in process, and the form is kept
//! (T119's rule that no command form vanishes unannounced).

pub mod refusal;
pub mod text;

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;

use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::pyjson::dumps;
use l7r_guard::shared::speckit::py_path;
use serde_json::{json, Value};

use crate::{raised, read_strict, reply, Reply};
pub use refusal::{Ask, Env};
use text::Refused;

/// What raised, as its message: the Python's uncaught exception.
pub type Raise<T> = Result<T, String>;

/// The name the tick's automatic archive step is recorded under in the usage log (`usage_log` by the tool's one writer, feature 406
/// T03, D162), which `scripts/tool-registry.json` registers; the tick itself records no run, as `tick-task.py` recorded none.
const USAGE_LOG_TOOL: &str = "tick-archive";
const USAGE: &str =
    "usage: tick-task.py <feature> <task> <note> [--boxes]   (make tick F=188 T=T03 NOTE=...)";
const LAND_USAGE: &str = "usage: tick-task.py --land-check <feature> <note> <task>... [--boxes]";

/// The repository root: git's answer, or the nearest ancestor holding `specs/` (`tick-task.repo_root`; the land's copy since T121, one
/// copy again here).
#[must_use]
pub fn repo_root(start: &Path) -> PathBuf {
    let out = Command::new("git")
        .args(["rev-parse", "--show-toplevel"])
        .current_dir(start)
        .output();
    match out {
        Ok(o) if o.status.success() => PathBuf::from(strip(&String::from_utf8_lossy(&o.stdout))),
        _ => {
            let here = start.canonicalize().unwrap_or(start.to_path_buf());
            here.ancestors()
                .find(|c| c.join("specs").is_dir())
                .map_or(here.clone(), Path::to_path_buf)
        }
    }
}

/// `specs/<feature>` when that exists, else the ONE `specs/<feature>-*` - None when neither, or several (`tick-task.spec_dir`).
#[must_use]
pub fn spec_dir(root: &Path, feature: &str) -> Option<PathBuf> {
    let specs = root.join("specs");
    // `Path`'s own normal form, as the Python's `root / "specs" / feature` printed it
    let exact = py_path(&specs.join(feature).to_string_lossy());
    if exact.is_dir() {
        return Some(exact);
    }
    let prefix = format!("{feature}-");
    let mut hits: Vec<PathBuf> = std::fs::read_dir(&specs)
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| {
            let n = e.file_name().to_string_lossy().into_owned();
            n.starts_with(&prefix) && e.path().is_dir()
        })
        .map(|e| e.path())
        .collect();
    hits.sort();
    (hits.len() == 1).then(|| hits.remove(0))
}

/// What `make land`'s first pass asks of one task: the refusal [`text::tick`] raises ("" when it would tick), what [`refusal::refusal`]
/// says with the landed check left out ("" when none; not asked where the tick refused), and whether [`text::boxes_refusal`] finds a
/// research box open, which the land reads to choose `--boxes` for the task's tick under `BOXES=1` (feature 449 T121's choice, kept).
#[derive(Debug, PartialEq, Eq)]
pub struct Checked {
    pub task: String,
    pub tick: String,
    pub refusal: String,
    pub box_open: bool,
}

/// The first pass's question of every task in `dir`, its tasks.md read once (`land_check` in the Python, one process for every task as
/// `land.py`'s import asked them in one; in the land's own process since feature 449 T131).
///
/// # Errors
/// What the Python raised: tasks.md missing or unreadable, a refusal that could not be asked.
pub fn checks(
    root: &Path,
    dir: &Path,
    note: &str,
    tasks: &[String],
    boxes: bool,
    env: Env,
) -> Raise<Vec<Checked>> {
    let text = read_strict(&dir.join("tasks.md"))?;
    let mut out = Vec::new();
    for task in tasks {
        let box_open = !text::boxes_refusal(&text, task, false).is_empty();
        let row = match text::tick(&text, task, note, false) {
            Err(Refused::Value(why) | Refused::Exit(why)) => Checked {
                task: task.clone(),
                tick: why,
                refusal: String::new(),
                box_open,
            },
            Ok(_) => {
                let ask = Ask::with_env(root, dir, task, note, env);
                Checked {
                    task: task.clone(),
                    tick: String::new(),
                    refusal: refusal::refusal(&ask, false, boxes)?.0,
                    box_open,
                }
            }
        };
        out.push(row);
    }
    Ok(out)
}

/// `--land-check <feature> <note> <task>... [--boxes]`: [`checks`] as JSON, `[{"task", "tick", "refusal", "box_open"}, ...]`.
fn land_check_cli(words: &[String], cwd: &Path, env: Env) -> Reply {
    let boxes = words.iter().any(|a| a == "--boxes");
    let args: Vec<&String> = words.iter().filter(|a| *a != "--boxes").collect();
    if args.len() < 3 {
        return reply(String::new(), format!("{LAND_USAGE}\n"), 2);
    }
    let root = repo_root(cwd);
    let Some(dir) = spec_dir(&root, args[0]) else {
        return no_dir(args[0], &root);
    };
    let tasks: Vec<String> = args[2..].iter().map(|t| (*t).clone()).collect();
    match checks(&root, &dir, args[1], &tasks, boxes, env) {
        Ok(rows) => {
            let list: Vec<Value> = rows
                .into_iter()
                .map(|r| json!({"task": r.task, "tick": r.tick, "refusal": r.refusal, "box_open": r.box_open}))
                .collect();
            reply(
                format!("{}\n", dumps(&Value::Array(list), None, true)),
                String::new(),
                0,
            )
        }
        Err(why) => raised("tick", String::new(), "", &why),
    }
}

fn no_dir(feature: &str, root: &Path) -> Reply {
    reply(
        String::new(),
        format!(
            "tick: no single specs/{feature}* directory under {}\n",
            root.display()
        ),
        2,
    )
}

/// The closing check at the tick that would close the feature, in process (`reviews::closing`, where the Python ran `close-check
/// --reasons-json`), its implementation check `claims::impl_check` in process too (feature 449 T132): may it close? The refusal goes
/// to `err`.
fn closing(ask: &Ask, err: &mut String) -> Raise<bool> {
    let tools = l7r_gate_reviews::reviews::closing::Tools {
        tree: &ask.tree,
        impl_check: l7r_gate_claims::claims::impl_check::missing_each,
    };
    let mut found = l7r_gate_reviews::reviews::closing::reasons(
        &tools,
        &ask.root.join("specs"),
        &[ask.dir.to_path_buf()],
    )?;
    let reasons = found.each.pop().unwrap_or_default();
    if reasons.is_empty() {
        return Ok(true);
    }
    let _ = writeln!(
        err,
        "tick: refused - this tick would close the feature, and:\n  {}",
        reasons.join("\n  ")
    );
    Ok(false)
}

/// One task ticked in `dir` of `root` - every refusal asked first (the landed check left out when `landing`), the closing check at the
/// last tick, the plan's finished sections archived after; the reply `make tick` prints. `make land` ticks its tasks through this in
/// process, its `L7R_LAND_TICKS` its own list.
#[must_use]
pub fn tick(ask: &Ask, boxes: bool, landing: bool) -> Reply {
    let Ask {
        root,
        dir,
        task,
        note,
        ..
    } = *ask;
    let (mut out, mut err) = (String::new(), String::new());
    let path = dir.join("tasks.md");
    let (why, message) = match refusal::refusal(ask, !landing, boxes) {
        Ok(found) => found,
        Err(why) => return raised("tick", out, &err, &why),
    };
    if !message.is_empty() {
        let _ = writeln!(out, "{message}");
    }
    if !why.is_empty() {
        return reply(out, format!("{why}\n"), 2);
    }
    let text = match read_strict(&path) {
        Ok(t) => t,
        Err(why) => return raised("tick", out, &err, &why),
    };
    let (new, line) = match text::tick(&text, task, note, boxes) {
        Ok(done) => done,
        Err(Refused::Value(why)) => {
            return reply(
                out,
                format!("tick: refused - {why} ({})\n", path.display()),
                2,
            )
        }
        Err(Refused::Exit(why)) => return reply(out, format!("{why}\n"), 1),
    };
    let remaining = l7r_guard::shared::speckit::splitlines(&new)
        .iter()
        .filter(|l| l.starts_with("- [ ] "))
        .count();
    if remaining == 0 {
        // feature 375 FR-009/FR-014: the last tick closes the feature - its report and carried keys first; what the implementation check
        // printed passes through, as `close-check --reasons-json` let it (feature 449 T127)
        match closing(ask, &mut err) {
            Ok(true) => {}
            Ok(false) => return reply(out, err, 2),
            Err(why) => return raised("tick", out, &err, &why),
        }
    }
    if let Err(why) = crate::write_file(&path, new.as_bytes()) {
        return raised("tick", out, &err, &why);
    }
    let Ok(rel) = path.strip_prefix(root) else {
        return raised(
            "tick",
            out,
            &err,
            &format!(
                "ValueError: {} is not in the subpath of {}",
                path.display(),
                root.display()
            ),
        );
    };
    let shown: String = line.chars().take(90).collect();
    let _ = writeln!(
        out,
        "ticked {shown}\n{remaining} task(s) still open in {}",
        rel.display()
    );
    // THE PLAN ARCHIVED AT THE TICK (feature 385 T63, the GM 2026-10-18: "perhaps that should be something that is run automatically
    // when certain actions are taken"): 385's plan.md reached 168 KB with 54 finished sections, every review reading them, because
    // `make plan-archive` was a step to remember. Recorded by the one usage-log writer as an automatic step (feature 406 T03, D162).
    if dir.join("plan.md").is_file() {
        let moved = l7r_gate_plan::plan::archive_finished(dir);
        let outcome = if moved.is_empty() {
            "unchanged"
        } else {
            "changed"
        };
        l7r_guard::shared::usage::record(root, USAGE_LOG_TOOL, "step", outcome);
        if !moved.is_empty() {
            let _ = writeln!(
                out,
                "tick: archived the plan sections of {} to plan-done.md",
                moved.join(", ")
            );
        }
    }
    reply(out, err, 0)
}

/// `--resolve <feature>`: `[root, dir or null]`, the root and the feature's directory as the tick finds them.
fn resolve_cli(args: &[String], cwd: &Path) -> Reply {
    if args.len() != 1 {
        return reply(
            String::new(),
            "usage: l7r-gate tick --resolve <feature>\n".to_owned(),
            2,
        );
    }
    let root = repo_root(cwd);
    let dir = spec_dir(&root, &args[0]).map(|d| d.display().to_string());
    let said = json!([root.display().to_string(), dir]);
    reply(format!("{}\n", dumps(&said, None, true)), String::new(), 0)
}

/// `l7r-gate tick ...` from `cwd`, the process's environment read.
#[must_use]
pub fn cli(words: &[String], cwd: &Path) -> Reply {
    cli_with(words, cwd, &|k| std::env::var(k).ok())
}

/// `l7r-gate tick ...` from `cwd`, `env` what the environment says.
fn cli_with(words: &[String], cwd: &Path, env: Env) -> Reply {
    match words.first().map(String::as_str) {
        Some("--land-check") => return land_check_cli(&words[1..], cwd, env),
        Some("--resolve") => return resolve_cli(&words[1..], cwd),
        _ => {}
    }
    let flag = |f: &str| words.iter().any(|a| a == f);
    let (boxes, from_env, landing) = (flag("--boxes"), flag("--note-from-env"), flag("--landing"));
    let mut args: Vec<String> = words
        .iter()
        .filter(|a| !matches!(a.as_str(), "--boxes" | "--note-from-env" | "--landing"))
        .cloned()
        .collect();
    if from_env && args.len() == 2 {
        args.push(env("TICK_NOTE").unwrap_or_default());
    }
    if args.len() != 3 {
        return reply(String::new(), format!("{USAGE}\n"), 2);
    }
    let (feature, task, note) = (&args[0], &args[1], &args[2]);
    let root = repo_root(cwd);
    let Some(dir) = spec_dir(&root, feature) else {
        return no_dir(feature, &root);
    };
    let path = dir.join("tasks.md");
    if !path.is_file() {
        return reply(
            String::new(),
            format!("tick: {} does not exist\n", path.display()),
            2,
        );
    }
    let ticks = env("L7R_LAND_TICKS").unwrap_or_default();
    // the plan review of 405 D24: `--landing` is `make land`'s alone
    if landing && !l7r_guard::shared::py_text::split(&ticks).contains(&task.as_str()) {
        return reply(String::new(), format!("tick: refused - --landing is `make land`'s, for a task it names in L7R_LAND_TICKS; {task} is not one - make land F={feature} T={task}\n"), 2);
    }
    tick(&Ask::with_env(&root, &dir, task, note, env), boxes, landing)
}

#[cfg(test)]
mod tests;
