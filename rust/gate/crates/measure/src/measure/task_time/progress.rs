//! `make task-progress` - THE TASKS IN FLIGHT (feature 451 T293; the GM 2026-11-26: "does their tooling that we have already built
//! allow you to see while a task is in progress where the time is going? ... I think that we should be able to see that kind of
//! thing"): one block per thing running NOW - each builder under its pool tree, each landing in flight, each page session - a
//! builder's with its minutes SO FAR by the task time breakdown's own categories, then a line each for the pool's free trees and
//! the tasks carried into the clone that no landing has placed.
//!
//! WHY. `make task-time` books a task's categories when it lands, and `make where-time` showed a running task's agents but not its
//! split: on 2026-11-26 T285 had 0 minutes booked at 17 minutes in and T292 14 minutes, 12 of them in one column (T293's line in
//! tasks.md). The events are logged live; nothing read them before the tick.
//!
//! IT REUSES THE BOOKING, IT DOES NOT COPY IT. A builder's minutes are [`super::book::book`]'s over a world of that builder's FAMILY
//! alone - its own lines, the agents it dispatched and theirs, their Bash runs - summed over every key, so they carry the same
//! categories and the same rules as the landed report. Two things are added, each named in the output, because the booking reads
//! closed gaps only: a call open at this moment is closed at `now` (a line of this module's making, never written), and the model
//! turn open at this moment is a row of its own.
//!
//! WHAT IS RUNNING is read from the pool's registry first (`builder-pool.json`: one block a held tree), then from the lines: an agent
//! is running when it has a start and no stop AND its session's latest `Stop` names it in flight (or it began after that `Stop`). The
//! second test is there because a start with no stop is also an agent cut off: on 2026-11-26 at 20:27Z the 451 log held three such
//! agents since 08:00Z, two running builders and a `spec-fidelity` started at 15:19Z whose last line was 15:23Z, and the session's
//! latest `Stop` named exactly the two (measured with a Python pass over the log's start, stop and `Stop` lines).
//!
//! NO PHASE IS EVER OPEN IN THE LOG: a `Phase` line is written when its step ends - the writer takes a span as
//! `<step>:<t0>:<t1>:<code>` (`event_log/phase.rs`) and has no start form. So the step a builder is in now is its open make run with
//! its last FINISHED phase, and the phase running at this moment sits in the run's own category until its line lands.
//!
//! THE KNOWN GAPS, said in the output and not hidden:
//! - A RESUMED builder is no gap since 451 T324 and T345: every start and stop of an agent is read, so it is running where a start
//!   or a call of its own follows its last stop, and stopped at its last stop otherwise; its minutes are its turns and runs in every
//!   span, the time it was stopped between them a wait and no turn. (Before, the reader kept one start and one stop an agent, and
//!   such a builder's minutes were headed "at least".)
//! - A pool tree's `Phase` lines written before 451 T332 can name another task (the writer now reads the pool's registry, `event_log_hooks/filed.rs`): each is booked here to the task the pool's log
//!   (`builder-pool.log`) says held its tree at that time ([`held::retask`], which the landed report shares since 451 T391), and a builder's family reads only its own tree's lines.
//!
//! THE READ-BACK. Lines are read from the earliest held tree's take, or [`BACK_H`] hours, whichever is earlier (`--back <N>h`
//! reads further): a task staged for a landing keeps its tree until it lands, so its carry is inside that span.

use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};

use l7r_gate_core::record::args::{parse_with, Spec};
use l7r_shared::builder_pool::{self, Tree};
use l7r_shared::context::context;
use l7r_shared::guards::event_log_hooks::common_git_dir;

use super::super::events::{is, names, or_s, t_of, ts, Event, Raised};
use super::super::reply;
use super::super::where_time::columns::{self, spent, Run, Runs, Subagents};
use super::book::{self, actor, ran, review_cat, run_cat};
use super::{all_logs, bases, held, iso_of, load, sums, tiers};
use crate::Reply;

mod render;
mod scene;

use scene::{Scene, Seen};

/// The hours read back where no held tree is older. GUESS, a knob (`--back`): unmeasured, set to hold a builder's whole run.
pub const BACK_H: f64 = 2.0;

/// The row a running builder's open model turn is listed under: its tool is not known until the turn ends.
pub const OPEN_TURN: &str = "builders: the turn open now (its tool not yet known)";

/// One agent of a block, as it stands now.
#[derive(Debug, Clone, PartialEq)]
pub struct AgentNow {
    /// Its id.
    pub aid: String,
    /// Its kind.
    pub kind: String,
    /// Its dispatch: its first start in the lines read.
    pub t0: f64,
    /// Its last stop, where no line of its follows it.
    pub stop: Option<f64>,
    /// Its last own line.
    pub last: f64,
    /// It stopped and ran on: a start or a call of its own after a stop.
    pub resumed: bool,
    /// Whether it is running now (the module's doc).
    pub running: bool,
    /// Its context in tokens, and where the figure is from.
    pub ctx: Option<(u64, &'static str)>,
}

/// One thing in flight under a task: a pool tree's holder and its builders, or a builder no tree is held for.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct Block {
    /// Who holds it, as a reader names it (`451 T293`).
    pub holder: String,
    /// Its pool tree's directory name and when it was placed.
    pub tree: Option<(String, f64)>,
    /// Its builders, in dispatch order.
    pub agents: Vec<AgentNow>,
    /// What each is doing at this moment, one line each.
    pub steps: Vec<String>,
    /// Its minutes so far: (category, seconds), the largest first.
    pub rows: Vec<(String, f64)>,
    /// When its task was carried into the clone, where it was.
    pub carried: Option<f64>,
}

/// One landing in flight.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct Landing {
    /// Its feature and tasks.
    pub name: String,
    /// When its run began.
    pub t0: f64,
    /// Its last finished phase and when that ended.
    pub phase: Option<(String, f64)>,
    /// Its minutes so far by category.
    pub rows: Vec<(String, f64)>,
}

/// What the report shows.
#[derive(Debug, Default)]
pub struct View {
    /// The moment it describes, and where the lines were read from.
    pub span: (f64, f64),
    /// The builders' blocks.
    pub blocks: Vec<Block>,
    /// The landings in flight.
    pub landings: Vec<Landing>,
    /// One line a page session running, and one a review agent the session itself dispatched.
    pub others: Vec<String>,
    /// The pool's free trees: (directory name, free since).
    pub free: Vec<(String, String)>,
    /// One line a task carried into the clone that no landing has placed or landed.
    pub staged: Vec<String>,
}

/// The lines read, the transcripts' ends and commands, and the moment.
struct Read<'a> {
    stream: &'a [Event],
    aside: &'a [Event],
    subs: &'a Subagents,
    queued: &'a HashMap<String, f64>,
    goal: &'a str,
    span: (f64, f64),
}

impl Read<'_> {
    /// The Bash runs of `lines` (each call open now closed at the moment), and their minutes by category as the breakdown books them.
    fn booked(
        &self,
        lines: &[Event],
        phases: &[Event],
    ) -> Result<(Runs, Vec<(String, f64)>), Raised> {
        let w = columns::Window {
            end: self.span.1,
            enqueued: self.queued,
            stopped: &self.subs.stopped,
            queued: &self.subs.queued,
            goal: self.goal,
        };
        let runs = columns::runs(lines, phases, &[], &w)?;
        let starts: Vec<Event> = lines
            .iter()
            .filter(|e| is(e, "ev", "SubagentStart") || is(e, "ev", "SubagentStop"))
            .cloned()
            .collect();
        let mut agents = columns::flight(&runs, &starts, lines, self.span.1)?.agents;
        spent::clip(&mut agents, self.span);
        let ledger = book::book(&book::World {
            stream: lines,
            runs: &runs,
            commands: &self.subs.commands,
            agents: &agents,
            pages: &[],
            window: self.span,
            batches: &[],
            carried: &HashMap::new(),
        })?;
        let mut rows: Vec<(String, f64)> = sums(&ledger, &|_| true)
            .0
            .into_iter()
            .map(|(cat, c)| (cat, c.min))
            .filter(|(_, s)| *s > 0.0)
            .collect();
        rows.sort_by(|a, b| b.1.total_cmp(&a.1).then(a.0.cmp(&b.0)));
        Ok((runs, rows))
    }

    /// The `Phase` and `BgEnd` lines a block's runs are tied to: a pool tree's own phases, else (no tree) the phases no pool tree
    /// wrote that name `task`.
    fn phases(&self, tree: Option<&str>, task: &str, pool: &[String]) -> Vec<Event> {
        self.aside
            .iter()
            .filter(|e| {
                let from = tiers::dir_name(&or_s(e, "clone"));
                !is(e, "ev", "Phase")
                    || tree.map_or_else(
                        || !pool.contains(&from) && or_s(e, "task") == task,
                        |t| from == t,
                    )
            })
            .cloned()
            .collect()
    }

    /// A run as a reader meets it now: its make target or program, how long it has run, and its last finished phase.
    fn run_now(&self, r: &Run, phases: &[Event]) -> String {
        let last = phases
            .iter()
            .filter(|p| is(p, "ev", "Phase") && ts(&or_s(p, "t0")).is_ok_and(|a| a >= r.t0))
            .filter_map(|p| Some((ts(&or_s(p, "t1")).ok()?, p)))
            .max_by(|a, b| a.0.total_cmp(&b.0));
        format!(
            "{}{}, {} min in; {}",
            run_cat(r, &self.subs.commands).1,
            if r.bg { " in the background" } else { "" },
            render::m(self.span.1 - r.t0),
            last.map_or_else(
                || "no phase of it has finished".to_owned(),
                |(t1, p)| format!(
                    "its last finished phase: {} {}, ended {}",
                    or_s(p, "src"),
                    or_s(p, "step"),
                    render::hms(t1)
                )
            )
        )
    }
}

/// The context of agent `aid` of session `sid`: its transcript's last call where a transcript is found, else its stop's.
fn context_of(projects: &Path, sid: &str, aid: &str, seen: &Seen) -> Option<(u64, &'static str)> {
    let live = names(projects).into_iter().find_map(|p| {
        let path: PathBuf = projects
            .join(p)
            .join(sid)
            .join("subagents")
            .join(format!("agent-{aid}.jsonl"));
        context(&path)
    });
    live.map(|n| (n, "its transcript's last call"))
        .or(seen.ctx.map(|n| (n, "at its stop")))
}

/// One block: the builders `mine`, their family's minutes and what each is doing now.
fn block(
    read: &Read,
    scene: &Scene,
    mine: &[String],
    (tree, pool): (Option<&Tree>, &[String]),
    projects: &Path,
) -> Result<Block, Raised> {
    let now = read.span.1;
    let family = scene.family(mine);
    let mut lines: Vec<Event> = read
        .stream
        .iter()
        .filter(|e| family.contains(&scene::who(e)))
        .cloned()
        .collect();
    lines.extend(
        scene
            .open
            .iter()
            .filter(|e| family.contains(&actor(e)))
            .map(|e| scene::closed(e, now)),
    );
    let first = &scene.seen[&mine[0]];
    let name = tree.map(|t| tiers::dir_name(&t.tree.to_string_lossy()));
    let phases = read.phases(name.as_deref(), &first.task, pool);
    let (runs, mut rows) = read.booked(&lines, &phases)?;
    let mut out = Block {
        holder: tree.map_or_else(|| first.name(), Tree::holder),
        tree: name.zip(tree.map(|t| ts(&t.since).unwrap_or(read.span.0))),
        ..Block::default()
    };
    let mut turn = 0.0;
    for aid in mine {
        let s = &scene.seen[aid];
        let running = scene.running(aid);
        let opens: Vec<&Event> = scene.open.iter().filter(|e| actor(e) == *aid).collect();
        let mut doing: Vec<String> = Vec::new();
        for o in &opens {
            doing.push(match runs.runs.iter().find(|r| r.id == or_s(o, "id")) {
                Some(r) => read.run_now(r, &phases),
                None => format!(
                    "a {} call, {} min in",
                    or_s(o, "tool"),
                    render::m(now - t_of(o)?)
                ),
            });
        }
        if running && opens.is_empty() {
            turn += now - s.last;
            doing.push(format!(
                "a model turn, {} min since its last call ended",
                render::m(now - s.last)
            ));
        }
        for r in runs.runs.iter().filter(|r| r.bg && r.open && r.by == *aid) {
            doing.push(read.run_now(r, &phases));
        }
        for (kid, k) in scene
            .seen
            .iter()
            .filter(|(kid, k)| k.parent == *aid && scene.running(kid))
        {
            doing.push(format!(
                "waiting on its {} agent {} ({}), {} min in",
                k.kind,
                render::short(kid),
                review_cat(&k.kind).unwrap_or("a builder of its own"),
                render::m(now - k.t0)
            ));
        }
        doing.sort();
        if doing.is_empty() {
            doing.push("nothing of its is in flight: it waits on the session (a carry, a landing, or its closing builder)".to_owned());
        }
        out.steps.push(format!(
            "{} now: {}",
            render::short(aid),
            doing.join("; and ")
        ));
        out.agents.push(AgentNow {
            aid: aid.clone(),
            kind: s.kind.clone(),
            t0: s.t0,
            stop: s.stop,
            last: s.last,
            resumed: s.resumed,
            running,
            ctx: context_of(projects, &s.sid, aid, s),
        });
    }
    if turn > 0.0 {
        rows.push((OPEN_TURN.to_owned(), turn));
        rows.sort_by(|a, b| b.1.total_cmp(&a.1).then(a.0.cmp(&b.0)));
    }
    out.rows = rows;
    Ok(out)
}

/// The landings in flight and the staged tasks, from the main sessions' own lines.
#[expect(
    clippy::too_many_lines,
    reason = "one pass over the lines read, top to bottom: split, each half would take the other's state"
)]
fn landings(
    read: &Read,
    scene: &Scene,
    takes: &[tiers::Take],
    view: &mut View,
) -> Result<(), Raised> {
    let now = read.span.1;
    let mut lines: Vec<Event> = read
        .stream
        .iter()
        .filter(|e| scene::who(e).starts_with("s:"))
        .cloned()
        .collect();
    let synth: HashSet<String> = scene
        .open
        .iter()
        .filter(|e| actor(e).starts_with("s:"))
        .map(|e| {
            lines.push(scene::closed(e, now));
            or_s(e, "id")
        })
        .collect();
    let (runs, _) = read.booked(&lines, read.aside)?;
    let carried = tiers::carries(&runs, &read.subs.commands, takes);
    let batches = tiers::batches((&lines, read.aside), &runs, &read.subs.commands, &carried)?;
    let mut flying: Vec<String> = Vec::new();
    for r in runs.runs.iter().filter(|r| {
        r.by.is_empty()
            && ran(r, &read.subs.commands).iter().any(|m| m == "land")
            && (synth.contains(&r.id)
                || (r.bg && (r.open || r.t1 >= now) && scene.in_flight(&r.sid, &r.bg_id, r.t0)))
    }) {
        let batch = batches.iter().find(|b| {
            b.attempts
                .iter()
                .any(|a| a.open && (a.t0 - r.t0).abs() < 0.5)
        });
        let (feature, tasks) = batch.map_or_else(
            || (String::new(), vec![r.task.clone()]),
            |b| (b.feature.clone(), b.tasks.clone()),
        );
        let phase = read
            .aside
            .iter()
            .filter(|p| is(p, "ev", "Phase") && is(p, "make", "land") && or_s(p, "sid") == r.sid)
            .filter_map(|p| Some((ts(&or_s(p, "t0")).ok()?, ts(&or_s(p, "t1")).ok()?, p)))
            .filter(|(a, _, _)| *a >= r.t0)
            .max_by(|a, b| a.1.total_cmp(&b.1))
            .map(|(_, t1, p)| (format!("{} {}", or_s(p, "src"), or_s(p, "step")), t1));
        let own: Vec<Event> = lines
            .iter()
            .filter(|e| or_s(e, "id") == r.id)
            .cloned()
            .collect();
        flying.extend(tasks.iter().map(|t| format!("{feature} {t}")));
        view.landings.push(Landing {
            name: format!("{} {}", scene::number(&feature), tasks.join(" "))
                .trim()
                .to_owned(),
            t0: r.t0,
            phase,
            rows: read.booked(&own, read.aside)?.1,
        });
    }
    let mut told: HashSet<String> = HashSet::new();
    // a task's LATEST carry is the one a landing waits on
    for (_, at, detail) in carried.iter().rev() {
        let (number, tasks) = held::holder(detail);
        let number = number.as_str();
        for task in &tasks {
            let mine = |b: &&book::Batch| {
                scene::number(&b.feature) == number && b.tasks.iter().any(|t| t == task)
            };
            let landed = batches
                .iter()
                .filter(mine)
                .any(|b| b.landed().is_some_and(|t| t >= *at));
            let key = format!("{number} {task}");
            for b in view.blocks.iter_mut().filter(|b| b.holder == key) {
                // latest first: an earlier carry never replaces the one already written
                b.carried = b.carried.or(Some(*at));
            }
            if landed
                || flying.iter().any(|f| {
                    scene::number(f.split(' ').next().unwrap_or("")) == number
                        && f.ends_with(&format!(" {task}"))
                })
                || !told.insert(key.clone())
            {
                continue;
            }
            let failed = batches
                .iter()
                .filter(mine)
                .flat_map(|b| &b.attempts)
                .filter(|a| !a.landed && !a.open && a.t0 >= *at)
                .map(|a| a.t1)
                .reduce(f64::max);
            view.staged.push(format!(
                "{key}: carried {}, {} min ago; {}",
                render::hms(*at),
                render::m(now - at),
                failed.map_or_else(
                    || "no `make land` has named it".to_owned(),
                    |t| format!(
                        "a landing naming it went red at {} and none has run since",
                        render::hms(t)
                    )
                )
            ));
        }
    }
    Ok(())
}

/// The page sessions running: each run log of the clone (`<git dir>/page-sessions/run-*.log`) written since the read-back that has
/// not said `ALL DONE`, with the brief it is in. A log untouched since the read-back is taken as a dead runner's: a runner killed
/// leaves its log without the line for good (73 of the directory's 299 entries held it on 2026-11-26, `grep -l`).
fn pages(common: &Path, (lo, now): (f64, f64), view: &mut View) {
    let dir = common.join("page-sessions");
    for n in names(&dir).into_iter().filter(|n| {
        n.starts_with("run-")
            && std::path::Path::new(n)
                .extension()
                .is_some_and(|e| e == "log")
    }) {
        let path = dir.join(&n);
        let written = std::fs::metadata(&path)
            .and_then(|m| m.modified())
            .ok()
            .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
            .map_or(0.0, |d| d.as_secs_f64());
        let text = std::fs::read_to_string(&path).unwrap_or_default();
        if written < lo || text.lines().any(|l| l == "ALL DONE") {
            continue;
        }
        let ended = text.lines().filter(|l| l.starts_with("ended ")).count();
        let brief = text
            .lines()
            .rfind(|l| l.starts_with("started "))
            .and_then(|l| l.split(' ').nth(2))
            .unwrap_or("no brief started");
        view.others.push(format!(
            "page session {}: in {brief}, {} min since its log's last line ({}); {ended} of its briefs ended",
            n.trim_end_matches(".log"),
            render::m(now - written),
            render::hms(written)
        ));
    }
}

/// The view of the clone `root` at `now` (the module's doc).
///
/// # Errors
///
/// A log, line or transcript the reader cannot read.
#[expect(
    clippy::too_many_lines,
    reason = "one pass over the lines read, top to bottom: split, each half would take the other's state"
)]
pub fn view(
    root: &Path,
    (projects, clones): (&Path, &Path),
    now: f64,
    back_h: Option<f64>,
) -> Result<View, Raised> {
    let common = common_git_dir(root);
    let trees = builder_pool::read(&common);
    let held = trees
        .iter()
        .filter(|t| !t.free())
        .filter_map(|t| ts(&t.since).ok());
    let lo = back_h.map_or_else(
        || held.fold(now - BACK_H * 3600.0, f64::min),
        |h| now - h * 3600.0,
    );
    // a log not written since the read-back holds no line of it
    let logs: Vec<(String, PathBuf)> = all_logs(root, clones)
        .into_iter()
        .filter(|(_, p)| {
            std::fs::metadata(p)
                .and_then(|m| m.modified())
                .ok()
                .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
                .is_none_or(|d| d.as_secs_f64() >= lo)
        })
        .collect();
    let mut got = load(&logs, &iso_of(lo), &iso_of(now.ceil()))?;
    let takes = tiers::takes(&bases(root, clones));
    // the set-aside lines are not cut at the window's end by the reader: a view as of a past moment reads none after it
    got.aside.retain(|e| t_of(e).is_ok_and(|t| t <= now));
    held::retask(&mut got.aside, &held::of(root, clones), "");
    let mut sids: Vec<String> = got.stream.iter().map(|e| or_s(e, "sid")).collect();
    sids.sort();
    sids.dedup();
    let span = (lo, now);
    let subs = columns::read_subagents(&sids, projects, span);
    let queued = &subs.enqueued;
    let goal =
        columns::default_goal(&std::fs::read_to_string(root.join("Makefile")).unwrap_or_default());
    let read = Read {
        stream: &got.stream,
        aside: &got.aside,
        subs: &subs,
        queued,
        goal: &goal,
        span,
    };
    let scene = Scene::of(&got.stream)?;
    let pool: Vec<String> = trees
        .iter()
        .map(|t| tiers::dir_name(&t.tree.to_string_lossy()))
        .collect();
    let mut view = View {
        span,
        ..View::default()
    };
    let mut placed: HashSet<String> = HashSet::new();
    for tree in &trees {
        if tree.free() {
            view.free.push((
                tiers::dir_name(&tree.tree.to_string_lossy()),
                tree.since.clone(),
            ));
            continue;
        }
        let since = ts(&tree.since).unwrap_or(lo);
        let mine: Vec<String> = scene
            .order
            .iter()
            .filter(|a| {
                let s = &scene.seen[*a];
                s.builder()
                    && s.t0 >= since
                    && tree.tasks.contains(&s.task)
                    && scene::number(&s.feature) == tree.feature
            })
            .cloned()
            .collect();
        if mine.is_empty() {
            view.blocks.push(Block {
                holder: tree.holder(),
                tree: Some((tiers::dir_name(&tree.tree.to_string_lossy()), since)),
                ..Block::default()
            });
            continue;
        }
        placed.extend(scene.family(&mine));
        view.blocks
            .push(block(&read, &scene, &mine, (Some(tree), &pool), projects)?);
    }
    for aid in scene.order.iter().filter(|a| scene.running(a)) {
        let s = &scene.seen[aid];
        if placed.contains(aid) {
            continue;
        }
        if s.builder() {
            placed.extend(scene.family(std::slice::from_ref(aid)));
            view.blocks.push(block(
                &read,
                &scene,
                std::slice::from_ref(aid),
                (None, &pool),
                projects,
            )?);
        } else {
            view.others.push(format!(
                "{} agent {} ({}), dispatched by the session: {} min in",
                s.kind,
                render::short(aid),
                s.name(),
                render::m(now - s.t0)
            ));
        }
    }
    landings(&read, &scene, &takes, &mut view)?;
    pages(&common, span, &mut view);
    Ok(view)
}

/// `l7r-gate measure task-progress [--root R] [--back <N>h]`, `now` the moment it describes.
#[must_use]
pub fn cli(args: &[String], projects: &Path, clones: &Path, now: f64) -> Reply {
    let specs = [
        Spec::value("--root"),
        Spec::value("--back"),
        Spec::value("--at"),
    ];
    let usage =
        "usage: l7r-gate measure task-progress [--root <tree>] [--back <N>h] [--at <ISO UTC>]\n";
    let p = match parse_with(args, &specs, 0) {
        Ok(p) => p,
        Err(why) => return reply(String::new(), format!("{usage}{why}\n"), 2),
    };
    let back = p.text("--back", "");
    let back_h = back.strip_suffix('h').and_then(|n| n.parse::<f64>().ok());
    if !back.is_empty() && back_h.is_none() {
        return reply(
            String::new(),
            format!("task-progress: BACK={back}: <N>h, e.g. BACK=6h\n{usage}"),
            2,
        );
    }
    // `--at <ISO>`: the view as of a past moment, from the lines up to it (a replay: a transcript read today can name a later end)
    let now = match p.text("--at", "") {
        "" => Ok(now),
        at => ts(at),
    };
    let seen = now.and_then(|now| {
        view(
            Path::new(p.text("--root", ".")),
            (projects, clones),
            now,
            back_h,
        )
    });
    match seen {
        Ok(v) => reply(render::render(&v), String::new(), 0),
        Err(why) => reply(String::new(), format!("{why}\n"), 1),
    }
}

#[cfg(test)]
mod tests;
