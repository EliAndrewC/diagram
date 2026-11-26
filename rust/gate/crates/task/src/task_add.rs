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
//! ([`quick`]); on a red they run again with the box and section taken out, and where the with-line run has a failure the other lacks,
//! they stay out and the filing is refused, naming those failures; a red the same without the line is reported as already there and
//! the line kept (put in again). `QUICK_OK="<reason>"` files it anyway, recorded by the tool in the guard log (`make guard-log
//! GUARD=task-add`), as `PERF_LATER_OK` is by `make task-start`.
//!
//! ONE FILING AT A TIME, AND ONLY ITS OWN TEXT TAKEN OUT (feature 451 T84, measured 2026-11-21). The run snapshotted tasks.md and
//! plan.md before it wrote, ran quick, and on a red wrote the whole-file snapshots back - its `was`, then its `now` - so any
//! other edit of the two files made while quick ran went with them. Measured in a scratch tree, a stand-in quick sleeping 1 s and red
//! with a finding outside specs/: two `task-add` 0.3 s apart lost BOTH boxes and both sections in 6 of 6 rounds, each run printing
//! "filed ... already red ... so it is kept"; another writer's line appended during the run without the line was lost in 3 of 3 rounds,
//! during the run with it in 0 of 3 (it was in `now`), and on a refusal in 3 of 3. With a green quick and no stagger 0 of 6 were lost,
//! but the id's read then the write is an unlocked read-modify-write. So the run holds the feature's filing lock ([`lock`], an `flock`
//! under the git common directory) from the id's read to quick's last run, and a withdrawal takes out of the CURRENT text the exact box
//! and section this run put in ([`Insert::withdrawn`]), never a copy written back; a red already there runs quick without the line by
//! withdrawing it and putting it in again by the same rules ([`Filing::put_in`]) - not on a copy of the tree, as quick's lines run in the
//! root itself and read what they like of it.

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_core::codeid::common_git_dir;
use l7r_gate_plan::plan::template::{PERFORMANCE, RED_EXIT, TEMPLATE};
use l7r_shared::escape::enough;
use l7r_shared::log::Entry;
use l7r_shared::py_text::{strip, SPACE_CLASS};
use serde_json::Value;

use crate::tick::text::re;
use crate::tick::{repo_root, spec_dir, Env};
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
///
/// ONE WRITER ACROSS TREES (feature 451 T255; the parallel trials of 2026-11-25: builders in two worktrees each filed T247, then
/// T248, renumbered by hand): the id is also past every id of the same four files on `main` and `origin/main` as last fetched
/// (`git show <ref>:./<file>`, no fetch under the lock), and past every id [`RESERVED`] records for the feature - the file every
/// worktree of the clone shares, written under the filing lock ([`lock`], already in the git common directory) before the box goes
/// in ([`reserve`]). A filing withdrawn gives its id back ([`release`]), so the next filing takes it, as before.
fn next_id(d: &Path) -> Result<String, String> {
    let mut text = String::new();
    for name in FILES {
        if d.join(name).is_file() {
            text += &read_strict(&d.join(name))?;
        }
        for r in ["main", "origin/main"] {
            let (code, out) = crate::git(d, &["show", &format!("{r}:./{name}")]);
            if code == Some(0) {
                text += &String::from_utf8_lossy(&out);
            }
        }
    }
    let top = ID
        .captures_iter(&text)
        .map_while(Result::ok)
        .filter_map(|c| c[1].parse::<u128>().ok())
        .chain(reserved(d).into_iter().map(|(n, _)| n))
        .max()
        .unwrap_or(0);
    Ok(format!("T{:02}", top + 1))
}

/// The files whose ids are taken: the feature's tasks, its ticked ones (feature 449 T142) and its plan's sections.
const FILES: [&str; 4] = [
    "tasks.md",
    l7r_shared::speckit::tasks::DONE,
    "plan.md",
    "plan-done.md",
];

/// The reservation file in the git common directory: one line an id handed out, `<feature> T<n>`, never rewritten but by
/// [`release`] under the lock. A tree git does not know has no other worktree to clash with, and keeps none.
const RESERVED: &str = "task-ids.txt";

/// The reservation file of the repository holding `d`, none outside git.
fn reserved_path(d: &Path) -> Option<std::path::PathBuf> {
    common_git_dir(d).map(|c| c.join(RESERVED))
}

/// The ids [`RESERVED`] holds for `d`'s feature, as numbers with their lines; none where it cannot be read.
fn reserved(d: &Path) -> Vec<(u128, String)> {
    let name = d.file_name().unwrap_or_default().to_string_lossy();
    reserved_path(d)
        .and_then(|p| std::fs::read_to_string(p).ok())
        .unwrap_or_default()
        .lines()
        .filter_map(|l| {
            let (f, t) = l.split_once(' ')?;
            let n = t.strip_prefix('T')?.parse().ok()?;
            (f == name).then(|| (n, l.to_owned()))
        })
        .collect()
}

/// `tid` recorded as handed out for `d`'s feature, under the filing lock.
fn reserve(d: &Path, tid: &str) -> Result<(), String> {
    use std::io::Write as _;
    let Some(path) = reserved_path(d) else {
        return Ok(());
    };
    let name = d.file_name().unwrap_or_default().to_string_lossy();
    std::fs::OpenOptions::new()
        .append(true)
        .create(true)
        .open(&path)
        .and_then(|mut f| writeln!(f, "{name} {tid}"))
        .map_err(|e| format!("{}: {e}", path.display()))
}

/// `tid` given back: a withdrawn filing's id is the next filing's again. A file that cannot be rewritten leaves a gap, never a clash.
fn release(d: &Path, tid: &str) {
    let Some(path) = reserved_path(d) else {
        return;
    };
    let name = d.file_name().unwrap_or_default().to_string_lossy();
    let line = format!("{name} {tid}");
    let text = std::fs::read_to_string(&path).unwrap_or_default();
    let kept: String = text
        .lines()
        .filter(|l| *l != line)
        .flat_map(|l| [l, "\n"])
        .collect();
    let _ = std::fs::write(&path, kept);
}

/// What one filing puts into one file: `text` at byte `at` of the text it read.
#[derive(Debug, Clone, PartialEq, Eq)]
struct Insert {
    at: usize,
    text: String,
}

impl Insert {
    /// `to` with the text put in.
    fn applied(&self, to: &str) -> String {
        format!("{}{}{}", &to[..self.at], self.text, &to[self.at..])
    }

    /// `now` with the text taken out - the copy nearest `at`, so the one put there when another writer's edit above it moved it - or
    /// `None` when no copy is left.
    fn withdrawn(&self, now: &str) -> Option<String> {
        let at = now
            .match_indices(self.text.as_str())
            .map(|(i, _)| i)
            .min_by_key(|i| i.abs_diff(self.at))?;
        Some(format!("{}{}", &now[..at], &now[at + self.text.len()..]))
    }
}

fn add_box(tasks: &str, tid: &str, title: &str, physical: bool) -> Insert {
    let research = if physical { "physical" } else { "rendering" };
    let boxed = format!(
        "- [ ] {tid} {title}\n      research: {research}\n{}",
        if physical { PHYSICAL } else { "" }
    );
    match GM_BOX.find(tasks).ok().flatten() {
        Some(gm) => Insert {
            at: gm.start(),
            text: boxed,
        },
        None => Insert {
            at: tasks.len(),
            text: format!("{}{boxed}", if tasks.ends_with('\n') { "" } else { "\n" }),
        },
    }
}

fn add_section(plan: &str, tid: &str, section: &str) -> Insert {
    let body = format!("{}\n\n", section.replace("{T}", tid).trim_end_matches('\n'));
    match CLOSE.find(plan).ok().flatten() {
        Some(close) => Insert {
            at: close.start(),
            text: body,
        },
        None => Insert {
            at: plan.len(),
            text: format!("{}\n{body}", if plan.ends_with('\n') { "" } else { "\n" }),
        },
    }
}

/// A section whose checklist item 6 does not route a red result through `make arbiter-ask`.
fn lacks_red_exit(section: &str) -> bool {
    let item6 = l7r_shared::speckit::splitlines(section)
        .into_iter()
        .find(|ln| {
            ln.trim_start_matches(l7r_shared::py_text::is_space)
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
    let _ = l7r_shared::log::write(&Entry {
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
pub(crate) fn cli_with(words: &[String], cwd: &Path, title: &str, env: Env) -> Reply {
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
    let _held = match lock(&root, &d, env) {
        Ok(held) => held,
        Err(refused) => return refused,
    };
    match file(
        &root,
        &d,
        title,
        &section,
        &section_path,
        physical,
        performance,
    ) {
        Ok((out, err, filing, placed)) => {
            checked(&root, &filing, &placed, &lines, (out, err), &quick_ok)
                .unwrap_or_else(|why| raised("task-add", String::new(), "", &why))
        }
        Err((err, why)) => raised("task-add", String::new(), &err, &why),
    }
}

/// How long a filing waits for another's lock, in seconds (GUESS, a knob: `L7R_TASK_ADD_LOCK_WAIT`, unmeasured): a filing holds it for
/// two runs of quick's checks - T19 measured its seven lines side by side at 0.12 s - so this outlasts a slow pair many times over and
/// still refuses a holder that hangs.
const LOCK_WAIT_S: f64 = 120.0;

/// The feature's filing lock (feature 451 T84), held from the id's read to quick's last run: an `flock` on
/// `task-add-<feature>.lock` in the git common directory (`<root>/.git` where git names none), waited for up to [`LOCK_WAIT_S`];
/// refused past it with nothing written, naming the lock file.
pub(crate) fn lock(root: &Path, d: &Path, env: Env) -> Result<std::fs::File, Reply> {
    let name = d.file_name().unwrap_or_default().to_string_lossy();
    let path = common_git_dir(root)
        .unwrap_or(root.join(".git"))
        .join(format!("task-add-{name}.lock"));
    let wait = env("L7R_TASK_ADD_LOCK_WAIT")
        .and_then(|w| strip(&w).parse::<f64>().ok())
        .unwrap_or(LOCK_WAIT_S);
    match l7r_shared::tool::flock_within(&path, wait) {
        Ok(Some(held)) => Ok(held),
        Ok(None) => Err(reply(String::new(), format!("task-add: refused, nothing written - another make task-add of {name} still holds {} after {wait} s: two filings at once threw both away (feature 451 T84). Wait for it to end and file again; its process: fuser -v {}; the wait is L7R_TASK_ADD_LOCK_WAIT seconds.\n", path.display(), path.display()), 2)),
        Err(e) => Err(raised("task-add", String::new(), "", &format!("{}: {e}", path.display()))),
    }
}

/// One filing's own text: its id, its box's title and research line, and its section (`{T}` for the id), put into the CURRENT
/// tasks.md and plan.md by [`Filing::put_in`] and taken out of them again by [`Filing::take_out`].
struct Filing<'a> {
    d: &'a Path,
    tid: String,
    title: &'a str,
    physical: bool,
    section: String,
}

/// Where a filing's text went: each file's [`Insert`], and whether the filing made plan.md.
struct Placed {
    tasks: Insert,
    plan: Insert,
    plan_made: bool,
}

/// A file's bytes as text, as they are now: no line ending rewritten, for only the filing's own text is taken out of them.
fn current(path: &Path) -> Result<String, String> {
    let bytes = std::fs::read(path).map_err(|e| format!("{}: {e}", path.display()))?;
    String::from_utf8(bytes).map_err(|e| format!("UnicodeDecodeError: {}: {e}", path.display()))
}

impl Filing<'_> {
    /// The box into tasks.md, before the GM's, and the section into plan.md, before the close, by the rules of [`add_box`] and
    /// [`add_section`] over the files as they are now.
    fn put_in(&self) -> Result<Placed, String> {
        let (tasks_path, plan_path) = (self.d.join("tasks.md"), self.d.join("plan.md"));
        let tasks = read_strict(&tasks_path)?;
        let boxed = add_box(&tasks, &self.tid, self.title, self.physical);
        write_file(&tasks_path, boxed.applied(&tasks).as_bytes())?;
        let plan_made = !plan_path.is_file();
        let plan = if plan_made {
            String::new()
        } else {
            read_strict(&plan_path)?
        };
        let section = add_section(&plan, &self.tid, &self.section);
        write_file(&plan_path, section.applied(&plan).as_bytes())?;
        Ok(Placed {
            tasks: boxed,
            plan: section,
            plan_made,
        })
    }

    /// The box and the section taken out of the files as they are now, whatever else was written meanwhile, and a plan.md the filing
    /// made removed when nothing else is in it; each file tried, then an error naming each that could not be.
    fn take_out(&self, placed: &Placed) -> Result<(), String> {
        let failed: Vec<String> = [
            ("tasks.md", &placed.tasks, "box"),
            ("plan.md", &placed.plan, "section"),
        ]
        .into_iter()
        .filter_map(|(name, put, what)| self.take_one(name, put, what, placed.plan_made).err())
        .collect();
        if failed.is_empty() {
            Ok(())
        } else {
            Err(failed.join("\n"))
        }
    }

    /// One file's text taken out, as [`Filing::take_out`] says.
    fn take_one(
        &self,
        name: &str,
        put: &Insert,
        what: &str,
        plan_made: bool,
    ) -> Result<(), String> {
        let path = self.d.join(name);
        let Some(left) = put.withdrawn(&current(&path)?) else {
            return Err(format!("task-add: {}'s {what} is no longer in {} as it was written, so it cannot be taken out: something else edited it while make quick's checks ran; take it out by hand", self.tid, path.display()));
        };
        if name == "plan.md" && plan_made && left.is_empty() {
            std::fs::remove_file(&path).map_err(|e| format!("{}: {e}", path.display()))
        } else {
            write_file(&path, left.as_bytes())
        }
    }
}

/// Quick's checks over what [`file`] wrote (D16): kept when green or red as before the line; else withdrawn - its own box and section
/// taken out ([`Filing::take_out`]) - and refused, unless `QUICK_OK` gives a reason. On a red it is taken out for the run without it
/// and, kept, put in again.
fn checked(
    root: &Path,
    filing: &Filing<'_>,
    placed: &Placed,
    lines: &[String],
    (mut out, mut err): (String, String),
    quick_ok: &str,
) -> Result<Reply, String> {
    let tid = &filing.tid;
    let with = quick::run(root, lines);
    if with.is_empty() {
        let _ = writeln!(
            out,
            "task-add: make quick's checks over it: clean ({} run)",
            lines.len()
        );
        return Ok(reply(out, err, 0));
    }
    filing.take_out(placed)?;
    let without = quick::run(root, lines);
    let added = quick::introduced(&with, &without);
    let name = filing.d.file_name().unwrap_or_default().to_string_lossy();
    let listed: String = added.iter().map(quick::Failure::shown).collect();
    if added.is_empty() || !quick_ok.is_empty() {
        filing.put_in()?;
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
    release(filing.d, tid);
    let number = name.split('-').next().unwrap_or_default();
    Ok(reply(String::new(), format!("{err}task-add: refused - {tid} withdrawn, its box and section taken out of tasks.md and plan.md: make quick's checks fail on what it wrote and not without it (feature 451 FR-011):\n{listed}Fix the title or the section and file it again: make task-add F={number} TITLE=\"...\" - or file it anyway: make task-add F={number} TITLE=\"...\" QUICK_OK=\"<reason>\" (recorded)\n"), 2))
}

/// The box and the section written: what was printed, the filing and where its text went, or what raised after what was printed.
fn file<'a>(
    root: &Path,
    d: &'a Path,
    title: &'a str,
    section: &str,
    section_path: &Path,
    physical: bool,
    performance: bool,
) -> Result<(String, String, Filing<'a>, Placed), (String, String)> {
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
    let filing = Filing {
        d,
        tid: next_id(d).map_err(fail)?,
        title,
        physical,
        section: text,
    };
    reserve(d, &filing.tid).map_err(fail)?;
    let placed = filing.put_in().map_err(fail)?;
    let rel = d.strip_prefix(root).map_err(|_| {
        fail(format!(
            "ValueError: {:?} is not in the subpath of {:?}",
            d.join("tasks.md").display().to_string(),
            root.display().to_string()
        ))
    })?;
    let out = format!(
        "task-add: {} filed in {}, its section in {}{}\n",
        filing.tid,
        rel.join("tasks.md").display(),
        rel.join("plan.md").display(),
        if section.is_empty() {
            " (the template: fill each <...>)"
        } else {
            ""
        }
    );
    Ok((out, err, filing, placed))
}

mod quick;

#[cfg(test)]
mod tests;
