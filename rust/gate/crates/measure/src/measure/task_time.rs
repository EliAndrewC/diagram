//! `make task-time [SINCE=24h|<ISO>] [UNTIL=<ISO>] [F=<feature>]` - THE TASK TIME BREAKDOWN (feature 451 T243; the GM 2026-11-25:
//! "maybe if I just say task time breakdown then that can mean this kind of thing"): each task LANDED in the window, across features,
//! its time by category and by make target or program, each with MINUTES and BLOCKING minutes and both percentages (of the task, of
//! the window), on `make where-time`'s reader (its runs, their ends and phases, its agents and their spans).
//!
//! WHY ONE TABLE ACROSS FEATURES. A day's main session works several features, its lines filed in whichever was active; on 2026-11-25
//! the day's account was two `make where-time` reports stitched by hand, each booking the other's hours "another feature" (361 min of
//! 449's). Here every clone's every log is read once, each line tagged with its log's feature, a task keyed (feature, task).
//!
//! THE DENOMINATORS. Minutes are machine minutes - every main session's and builder's own time, every review agent's span, every Bash
//! run, every page-session phase - and overlap; a percentage of minutes is of the summed minutes. Blocking minutes are BY TASK AND
//! DEPENDENCY (the GM 2026-11-25: "a minute should count as blocking. When something else is waiting on it to be done before it can be
//! started"): each main session's clock inside the window, each second once per task it blocks, booked to the task whose next step waited on
//! it - by the `Blocks:` clue the work's dispatch, brief or command gave, else by the defaults (`book`'s doc), each task with blocking
//! work in flight its own piece - so they sum over tasks and pass the clock where tasks ran side by side, in one session or across clones; a wait on work that blocked no task is named apart, never blocking. Waiting on the GM
//! (his turn, or away) is reported with its share of the whole, and left out of every other percentage's denominator (amendment (i),
//! the GM 2026-11-25): those are of the WORKING time, the whole less the GM's, and sum to 100 over it - over its own SIDE since
//! 451 T510: the tasks' side (every cell but a batch's or a carry's, with the minutes a task waited on a landing, `cross`) and the
//! landings' side (every batch's cell and every carry's) are each their own denominator, no percentage of one of the other's total. The line "Working at once" shows
//! how many actors worked together.

use std::collections::{BTreeMap, HashMap};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_gate_core::record::args::{parse_with, Spec};
use l7r_shared::guards::event_log_hooks::common_git_dir;
use serde_json::Value;

use super::events::{fixed, get, hhmm, is, load_all, names, or_s, s, t_of, ts, Event, Raised};
use super::reply;
use super::where_time::columns::{self, spent};
use crate::Reply;

pub mod asked;
pub mod book;
pub mod cross;
pub mod held;
pub mod program;
pub mod progress;
pub mod tiers;
mod top;

use book::{is_tier, Batch, Cell, Key, Ledger, Page, CARRY};

/// Every event log of every clone (and the mirror's), each once: (feature, path), the feature its file's stem.
#[must_use]
pub fn all_logs(root: &Path, clones: &Path) -> Vec<(String, PathBuf)> {
    let mut seen: Vec<PathBuf> = Vec::new();
    let mut out = Vec::new();
    for base in bases(root, clones) {
        let dir = common_git_dir(&base).join("l7r-events");
        for n in names(&dir).into_iter().filter(|n| {
            Path::new(n)
                .extension()
                .is_some_and(|e| e.eq_ignore_ascii_case("jsonl"))
        }) {
            let p = dir.join(&n);
            let real = std::fs::canonicalize(&p).unwrap_or(p.clone());
            if !seen.contains(&real) {
                seen.push(real);
                out.push((n.trim_end_matches(".jsonl").to_owned(), p));
            }
        }
    }
    out
}

/// The trees whose logs are read: `root`, the mirror (the clones' parent, whose own log a session there writes) and every clone.
fn bases(root: &Path, clones: &Path) -> Vec<PathBuf> {
    let mut bases = vec![root.to_path_buf()];
    bases.extend(clones.parent().map(Path::to_path_buf));
    bases.extend(names(clones).into_iter().map(|n| clones.join(n)));
    bases.retain(|b| b.join(".git").exists());
    bases
}

/// Each task's FIRST start in any tree's `task-starts.jsonl` (`make task-start`'s record), by (feature, task).
#[must_use]
pub fn starts(root: &Path, clones: &Path) -> BTreeMap<Key, f64> {
    let mut out: BTreeMap<Key, f64> = BTreeMap::new();
    // a record read twice (a tree that is another's) changes no first start
    for base in bases(root, clones) {
        let p = common_git_dir(&base).join("task-starts.jsonl");
        // a start and its `make task-unstart` read as no start (451 T359)
        let text = l7r_shared::speckit::marks::live_starts(
            &std::fs::read_to_string(&p).unwrap_or_default(),
        );
        for v in text
            .lines()
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        {
            let (Some(f), Some(t), Some(at)) = (
                v.get("feature").and_then(Value::as_str),
                v.get("task").and_then(Value::as_str),
                v.get("utc")
                    .and_then(Value::as_str)
                    .and_then(|u| ts(u).ok()),
            ) else {
                continue;
            };
            let e = out.entry((f.to_owned(), t.to_owned())).or_insert(at);
            *e = e.min(at);
        }
    }
    out
}

/// `SINCE=`: `<N>h` hours before `now`, else an ISO time as given.
///
/// # Errors
///
/// An hour count that is no number.
pub fn since_of(text: &str, now: f64) -> Result<String, Raised> {
    match text.strip_suffix('h') {
        Some(n) => {
            let h: f64 = n
                .parse()
                .map_err(|_| format!("task-time: SINCE={text}: <N>h or an ISO time"))?;
            Ok(iso_of(now - h * 3600.0))
        }
        None => Ok(text.to_owned()),
    }
}

fn iso_of(t: f64) -> String {
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "seconds since the epoch, after it"
    )]
    let (y, mo, d, h, mi, sec) = l7r_shared::log::civil(t.max(0.0) as u64);
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{sec:02}Z")
}

/// What the report reads, loaded.
pub struct Loaded {
    /// Every log's window lines, tagged `feature`, in time order.
    pub stream: Vec<Event>,
    /// The set-aside lines (`Phase`, `BgEnd`), tagged.
    pub aside: Vec<Event>,
    /// The window in UTC seconds.
    pub window: (f64, f64),
}

/// Every log's lines from `since` (its text, as `load_all` cuts) to `until`, each tagged with its feature.
///
/// # Errors
///
/// A log or line the reader cannot read.
pub fn load(logs: &[(String, PathBuf)], since: &str, until: &str) -> Result<Loaded, Raised> {
    let (mut stream, mut aside) = (Vec::new(), Vec::new());
    for (feature, p) in logs {
        let got = load_all(std::slice::from_ref(p), &[], since, "")?;
        let tag = |mut e: Event| {
            e.insert("feature".to_owned(), Value::String(feature.clone()));
            e
        };
        stream.extend(
            got.stream
                .into_iter()
                .filter(|e| until.is_empty() || s(e, "t").as_str() <= until)
                .map(tag),
        );
        aside.extend(got.aside.into_iter().map(tag));
    }
    let mut keyed = Vec::with_capacity(stream.len());
    for e in stream {
        keyed.push((t_of(&e)?, e));
    }
    keyed.sort_by(|a, b| a.0.total_cmp(&b.0));
    let stream: Vec<Event> = keyed.into_iter().map(|(_, e)| e).collect();
    // `since` is never empty: the command line defaults it to 24h
    let lo = ts(since)?;
    let hi = if until.is_empty() {
        let mut last = lo;
        for e in stream.iter().chain(&aside) {
            last = last.max(t_of(e)?);
        }
        last
    } else {
        ts(until)?
    };
    Ok(Loaded {
        stream,
        aside,
        window: (lo, hi),
    })
}

/// (when, key) of each task a landing landed inside the window: a landing's `end` phase with `landed`, its `tasks` under its feature.
///
/// # Errors
///
/// A line's time the reader cannot read.
pub fn landed(
    aside: &[Event],
    (lo, hi): (f64, f64),
    only: &str,
) -> Result<Vec<(f64, Key)>, Raised> {
    let mut out: Vec<(f64, Key)> = Vec::new();
    for e in aside
        .iter()
        .filter(|e| is(e, "ev", "Phase") && is(e, "src", "land") && is(e, "step", "end"))
    {
        let t = t_of(e)?;
        if get(e, "landed").as_bool() != Some(true) || t < lo || t > hi {
            continue;
        }
        let feature = or_s(e, "feature");
        if !only.is_empty() && !feature.starts_with(&format!("{only}-")) {
            continue;
        }
        for task in get(e, "tasks")
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(Value::as_str)
        {
            let k = (feature.clone(), task.to_owned());
            if !out.iter().any(|(_, x)| *x == k) {
                out.push((t, k));
            }
        }
    }
    Ok(out)
}

/// The page sessions' phases (a detached runner's), each under its log's feature and its task.
///
/// # Errors
///
/// A phase's span the reader cannot read.
pub fn pages(aside: &[Event]) -> Result<Vec<Page>, Raised> {
    let mut out = Vec::new();
    for e in aside
        .iter()
        .filter(|e| is(e, "ev", "Phase") && is(e, "src", "page-session"))
    {
        let span = |k: &str| {
            get(e, k)
                .as_str()
                .map_or(Err(format!("TypeError: a Phase line's {k} is no text")), ts)
        };
        let task = or_s(e, "task");
        out.push(Page {
            t0: span("t0")?,
            t1: span("t1")?,
            key: (
                or_s(e, "feature"),
                if task.is_empty() {
                    "-".to_owned()
                } else {
                    task
                },
            ),
            sid: or_s(e, "name"),
            blocks: or_s(e, "blocks"),
        });
    }
    Ok(out)
}

fn pct(x: f64, of: f64) -> String {
    if of > 0.0 {
        format!("{}%", fixed(100.0 * x / of, 1))
    } else {
        "-".to_owned()
    }
}

fn m(x: f64) -> String {
    fixed(x / 60.0, 1)
}

/// The category table's rows: a category and its cell.
type CatRows = Vec<(String, Cell)>;
/// The target table's rows: a target, the category it books to, its runs and its cell.
type TargetRows = Vec<(String, String, usize, Cell)>;

/// The sums the report reads: by category and by target, over the keys `pick` takes.
fn sums(l: &Ledger, pick: &dyn Fn(&Key) -> bool) -> (CatRows, TargetRows) {
    let mut cats: HashMap<&str, Cell> = HashMap::new();
    let mut targets: HashMap<&str, (String, usize, Cell)> = HashMap::new();
    for ((_, cat, target), c) in l.cells.iter().filter(|((k, _, _), _)| pick(k)) {
        let e = cats.entry(cat).or_default();
        e.min += c.min;
        e.block += c.block;
        e.fg += c.fg;
        if !target.is_empty() {
            // a target books its run's remainder to its category, its phases' named in the category table
            let to = l.books_to.get(target).unwrap_or(cat);
            let t = targets
                .entry(target)
                .or_insert_with(|| (to.clone(), 0, Cell::default()));
            t.2.min += c.min;
            t.2.block += c.block;
        }
    }
    for ((_, target), n) in l.runs.iter().filter(|((k, _), _)| pick(k)) {
        if let Some(t) = targets.get_mut(target.as_str()) {
            t.1 += n;
        }
    }
    let mut c: Vec<(String, Cell)> = cats
        .into_iter()
        .map(|(k, v)| (k.to_owned(), v))
        .filter(|(_, v)| v.min + v.block > 0.0)
        .collect();
    c.sort_by(|a, b| {
        (b.1.block + b.1.min)
            .total_cmp(&(a.1.block + a.1.min))
            .then(a.0.cmp(&b.0))
    });
    let mut t: Vec<(String, String, usize, Cell)> = targets
        .into_iter()
        .map(|(k, (cat, n, v))| (k.to_owned(), cat, n, v))
        .filter(|x| x.3.min + x.3.block > 0.0)
        .collect();
    t.sort_by(|a, b| {
        (b.3.block + b.3.min)
            .total_cmp(&(a.3.block + a.3.min))
            .then(a.0.cmp(&b.0))
    });
    (c, t)
}

fn total(c: &[(String, Cell)]) -> Cell {
    c.iter().fold(Cell::default(), |a, (_, x)| Cell {
        min: a.min + x.min,
        block: a.block + x.block,
        fg: a.fg + x.fg,
    })
}

/// Waiting on the GM (his turn, or away): reported, but out of every other percentage's denominator (the GM 2026-11-25: "time spent
/// waiting for me should probably not be counted in those percentages, even if it is recorded").
fn is_gm(cat: &str) -> bool {
    cat.starts_with("the GM")
}

/// The working time of `cats`: their total less the GM's.
fn working(cats: &[(String, Cell)]) -> Cell {
    let gm = total(
        &cats
            .iter()
            .filter(|(c, _)| is_gm(c))
            .cloned()
            .collect::<Vec<_>>(),
    );
    let all = total(cats);
    Cell {
        min: all.min - gm.min,
        block: all.block - gm.block,
        fg: all.fg - gm.fg,
    }
}

/// The window's three wholes (451 T510): the whole, the GM's rows' denominator as before; the tasks' side's working time, the
/// minutes a task waited on a landing in its blocking; the landings' side's working time.
#[derive(Debug, Clone, Copy, PartialEq, Default)]
pub struct Sides {
    /// Everything booked, the GM's wait in it.
    pub whole: Cell,
    /// The tasks' side, less the GM's wait, with the cross-blocking in its blocking.
    pub tasks: Cell,
    /// The landings' side: every batch's time and every carry.
    pub landings: Cell,
}

/// Whether a cell is the landings' side's (451 T510): a batch's, or a carry into the clone; never the GM's wait.
fn landing_side(key: &Key, cat: &str) -> bool {
    !is_gm(cat) && (is_tier(key) || cat == CARRY)
}

/// The window's three wholes from its ledger and the cross-blocking seconds.
fn sides(l: &Ledger, cross: f64) -> Sides {
    let mut d = Sides::default();
    for ((key, cat, _), c) in &l.cells {
        d.whole.min += c.min;
        d.whole.block += c.block;
        let side = if landing_side(key, cat) {
            &mut d.landings
        } else if is_gm(cat) {
            continue;
        } else {
            &mut d.tasks
        };
        side.min += c.min;
        side.block += c.block;
    }
    d.tasks.block += cross;
    d
}

/// One task's (or a group's) two tables: the GM's rows as percentages of the whole (itself, the window's `d.whole`), every other row
/// of the working time (itself, and its side of the window, 451 T510: the landings' for a carry's row or a `tier` table, else the
/// tasks').
fn tables(
    out: &mut String,
    cats: &[(String, Cell)],
    targets: &[(String, String, usize, Cell)],
    d: &Sides,
    tier: bool,
) {
    let side = |cat: &str| {
        if tier || cat == CARRY {
            d.landings
        } else {
            d.tasks
        }
    };
    let (me, me_w) = (total(cats), working(cats));
    let mine: Cell = cats
        .iter()
        .filter(|(c, _)| !is_gm(c) && (tier || c != CARRY))
        .fold(Cell::default(), |a, (_, x)| Cell {
            min: a.min + x.min,
            block: a.block + x.block,
            fg: 0.0,
        });
    let (all, work) = (d.whole, side(""));
    out.push_str("| category | minutes | % of task | % of window | blocking | % of task | % of window |\n|---|---|---|---|---|---|---|\n");
    for (cat, c) in cats {
        let (t, w) = if is_gm(cat) {
            (me, all)
        } else {
            (me_w, side(cat))
        };
        let _ = writeln!(
            out,
            "| {cat} | {} | {} | {} | {} | {} | {} |",
            m(c.min),
            pct(c.min, t.min),
            pct(c.min, w.min),
            m(c.block),
            pct(c.block, t.block),
            pct(c.block, w.block)
        );
    }
    let _ = writeln!(
        out,
        "| all | {} | | {} | {} | | {} |",
        m(me.min),
        pct(me.min, all.min),
        m(me.block),
        pct(me.block, all.block)
    );
    let _ = writeln!(
        out,
        "| working (all but waiting on the GM) | {} | | {} | {} | | {} |\n",
        m(me_w.min),
        pct(mine.min, work.min),
        m(me_w.block),
        pct(mine.block, work.block)
    );
    out.push_str("| make target or program | books to | runs | minutes | % of task | % of window | blocking | % of task | % of window |\n|---|---|---|---|---|---|---|---|---|\n");
    for (t, cat, n, c) in targets {
        let _ = writeln!(
            out,
            "| {t} | {cat} | {n} | {} | {} | {} | {} | {} | {} |",
            m(c.min),
            pct(c.min, me_w.min),
            pct(c.min, side(cat).min),
            m(c.block),
            pct(c.block, me_w.block),
            pct(c.block, side(cat).block)
        );
    }
    out.push('\n');
}

/// The header's two lines beside the totals: what was waited on that blocked no task, and how many actors worked at once.
fn beside(out: &mut String, l: &Ledger) {
    let mut free: Vec<(&String, &f64)> = l.free.iter().collect();
    free.sort_by(|a, b| b.1.total_cmp(a.1).then(a.0.cmp(b.0)));
    let _ = writeln!(
        out,
        "Waited on, blocking no task (a page session or research pass whose brief names none, work whose clue is `Blocks: none`): {} min{}.\n",
        m(l.free.values().sum()),
        free.iter().fold(String::new(), |mut o, (c, x)| {
            let _ = write!(o, " - {c} {}", m(**x));
            o
        })
    );
    let n = l.at_once;
    let _ = writeln!(
        out,
        "Working at once (main sessions in their own turns and runs, agents, page sessions), minutes of the window: none {}, one {}, two {}, three or more {}.\n",
        m(n[0]),
        m(n[1]),
        m(n[2]),
        m(n[3])
    );
}

/// The report (the module's doc): the window, its table in two sides (451 T510), a line a landed task and the second tier's section
/// (451 T298, `top`), the biggest blocking categories and whether each could run in parallel, each landed task's tables, the rest of
/// the window's, and the footnote naming what could not be booked.
#[must_use]
pub fn render(
    (l, whole): (&Ledger, &Ledger),
    (landed, batches): (&[(f64, Key)], &[Batch]),
    (window, from, starts): ((f64, f64), f64, &BTreeMap<Key, f64>),
    (runs, cross): (&columns::Runs, &cross::Cross),
) -> String {
    let all_c = sums(l, &|_| true).0;
    let (all, work) = (total(&all_c), working(&all_c));
    let d = sides(l, cross.both);
    let keys: Vec<&Key> = landed.iter().map(|(_, k)| k).collect();
    let landed_block = total(&sums(l, &|x| keys.contains(&x)).0).block;
    let mut out = format!(
        "# The task time breakdown, {} to {} UTC ({} tasks landed)\n\nminutes {} (machine, overlapping), blocking {} (by task and dependency: \
         each task's own turns and what its next step waited on, summed over tasks, so it passes the clock where tasks ran side by side, in one session or across clones; \
         the landed tasks' {})\n\n\
         Waiting on the GM: {} min blocking, {} of the window's blocking. It is left out of every other percentage: the GM's rows are \
         percentages of the whole (the task's, the window's), every other row's - minutes and blocking, of the task and of the window - \
         of its own side's working time, the GM's less (451 T510: the two sides' denominators are apart): the tasks' side {} min, {} min \
         blocking ({} of it a task waiting on a landing), the landings' side (every batch landing and every carry) {} min, {} min \
         blocking.\n\n",
        iso_of(window.0),
        iso_of(window.1),
        landed.len(),
        m(all.min),
        m(all.block),
        m(landed_block),
        m(all.block - work.block),
        pct(all.block - work.block, all.block),
        m(d.tasks.min),
        m(d.tasks.block),
        m(cross.both),
        m(d.landings.min),
        m(d.landings.block)
    );
    beside(&mut out, l);
    top::window_table(&mut out, l, &d, cross);
    top::task_lines(&mut out, whole, landed, batches);
    top::second_tier(&mut out, l, batches, window, &d);
    out.push_str(
        "## The biggest blocking on the tasks' side, and whether it could run in parallel\n\n",
    );
    let mut by_block = sums(l, &|x| !is_tier(x)).0;
    by_block.sort_by(|a, b| b.1.block.total_cmp(&a.1.block));
    for (cat, c) in by_block
        .iter()
        .filter(|(cat, c)| c.block > 0.0 && !is_gm(cat) && cat != CARRY)
        .take(5)
    {
        let how = if c.fg > 0.0 {
            format!(
                "{} of it a foreground run its actor waited on, which could run in the background beside other work; the rest already in the background and waited on",
                pct(c.fg, c.block)
            )
        } else {
            "serial in its actor (a model's turn, an agent's span or a wait): parallel only across more actors".to_owned()
        };
        let _ = writeln!(
            out,
            "- {cat}: {} min blocking ({} of the tasks' side's working blocking) - {how}",
            m(c.block),
            pct(c.block, d.tasks.block)
        );
    }
    out.push_str("\n(the parallel reading is a proxy, measured: the share of a category's blocking that was a foreground run in its actor; \
                   the landings' side is in the second tier's section)\n\n");
    for (t, k) in landed {
        let _ = writeln!(
            out,
            "## {} {} (landed {}{})\n",
            k.0,
            k.1,
            hhmm(*t),
            cut_note(starts.get(k).copied(), from)
        );
        // the task's WHOLE time, read back to `from`: the window picks which tasks, not which of their time (round 2 of its review)
        let (c, tg) = sums(whole, &|x| x == k);
        let (w, inside) = (total(&c), total(&sums(l, &|x| x == k).0));
        let _ = writeln!(
            out,
            "Its whole time, from {}: {} min, {} min blocking; inside the window {} min ({} of it), {} min blocking ({}); its % of window is its whole time against its side's totals, so it can pass 100%.\n",
            iso_of(from),
            m(w.min),
            m(w.block),
            m(inside.min),
            pct(inside.min, w.min),
            m(inside.block),
            pct(inside.block, w.block)
        );
        tables(&mut out, &c, &tg, &d, false);
    }
    out.push_str(
        "## The rest of the window: tasks not landed in it, and time under no task (`-`); the second tier's is in its own section\n\n",
    );
    let (c, tg) = sums(l, &|x| !keys.contains(&x) && !is_tier(x));
    tables(&mut out, &c, &tg, &d, false);
    out.push_str("## The whole window, the tasks' side (a carry's rows of the landings' side, its % of window of that side's)\n\n");
    let (c, tg) = sums(l, &|x| !is_tier(x));
    tables(&mut out, &c, &tg, &d, false);
    footnote(&mut out, landed, (from, starts), runs, window.0);
    out
}

/// The report's last lines: the landed tasks cut at the read-back `from`, and what could not be booked, named.
fn footnote(
    out: &mut String,
    landed: &[(f64, Key)],
    (from, starts): (f64, &BTreeMap<Key, f64>),
    runs: &columns::Runs,
    since: f64,
) {
    // round 3 of its review: the read-back stops at `from`, so a landed task started before it, or with no start recorded, is named
    let cut: Vec<String> = landed
        .iter()
        .filter(|(_, k)| starts.get(k).is_none_or(|s| *s < from))
        .map(|(_, k)| format!("{} {}", k.0, k.1))
        .collect();
    let _ = writeln!(
        out,
        "Cut at the read-back ({}, `BACK=` reads further): {} - a landed task started before it, or with no start in `task-starts.jsonl`, \
         carries only its time from there.\n",
        iso_of(from),
        if cut.is_empty() { "none".to_owned() } else { cut.join(", ") }
    );
    let _ = writeln!(
        out,
        "Unbooked, named: {} Bash calls refused before running (no run); {} phases tied to no run ({} min, not in the minutes); a wait with \
         nothing in flight is `{} - <class>`, its class what came just before and after it, one not yet classed `unexplained` with the \
         line that followed it; with only a monitor and no page session `{}`; a builder's time inside its span no line of its accounts for \
         `{}`; a command no transcript holds `{}`. Wait loops do no work: their minutes are the time they were held open, and their blocking \
         is booked to what they waited on{}. (feature 451 T243, the task time breakdown)",
        runs.refused,
        runs.loose.0,
        m(runs.loose.1),
        book::NOTHING,
        book::MONITOR,
        book::UNLINED,
        book::UNREAD,
        columns::scratch_note(&runs.scratch, since)
    );
}

/// A landed task's heading note where its whole time is cut at the read-back `from`: started before it, or no start recorded.
fn cut_note(start: Option<f64>, from: f64) -> String {
    match start {
        Some(s) if s >= from => String::new(),
        Some(s) => format!(
            "; started {}, before the read-back: its time before {} is not in its tables",
            iso_of(s),
            iso_of(from)
        ),
        None => format!(
            "; no start recorded: its time before {} may be missing",
            iso_of(from)
        ),
    }
}

/// The report over the clones' logs, with the transcripts under `projects`, and the end of the window it used.
///
/// # Errors
///
/// A log, line or transcript the reader cannot read.
pub fn run(
    root: &Path,
    (since, until, back_h): (&str, &str, f64),
    only: &str,
    (projects, clones): (&Path, &Path),
) -> Result<(String, f64), Raised> {
    let logs = all_logs(root, clones);
    // read `back_h` hours before the window, so a landed task's tables carry its time before it (a knob: `BACK=`)
    let lo = ts(since)?;
    let mut got = load(&logs, &iso_of(lo - back_h * 3600.0), until)?;
    // a pool tree's phases by the task that held the tree, before the runs are tied to them (451 T391)
    held::retask(&mut got.aside, &held::of(root, clones), "");
    let window = (lo, got.window.1);
    let mut sids: Vec<String> = got.stream.iter().map(|e| s(e, "sid")).collect();
    sids.sort();
    sids.dedup();
    let makefile = std::fs::read_to_string(root.join("Makefile")).unwrap_or_default();
    let goal = columns::default_goal(&makefile);
    let queued = columns::enqueued(&sids, projects);
    let subs = columns::read_subagents(&sids, projects, got.window);
    let w = columns::Window {
        end: got.window.1,
        enqueued: &queued,
        stopped: &subs.stopped,
        queued: &subs.queued,
        goal: &goal,
    };
    let runs = columns::runs(&got.stream, &got.aside, &[], &w)?;
    let agent_lines: Vec<Event> = got
        .stream
        .iter()
        .filter(|e| is(e, "ev", "SubagentStart") || is(e, "ev", "SubagentStop"))
        .cloned()
        .collect();
    let mut flight = columns::flight(&runs, &agent_lines, &got.stream, got.window.1)?;
    let mut inside = flight.agents.clone();
    spent::clip(&mut flight.agents, got.window);
    spent::clip(&mut inside, window);
    let pages = pages(&got.aside)?;
    let takes = tiers::takes(&bases(root, clones));
    let carried = tiers::carries(&runs, &subs.commands, &takes);
    let batches = tiers::batches((&got.stream, &got.aside), &runs, &subs.commands, &carried)?;
    let carry_of: HashMap<String, String> = carried
        .iter()
        .map(|(id, _, detail)| (id.clone(), detail.clone()))
        .collect();
    let world = |agents, window| book::World {
        stream: &got.stream,
        runs: &runs,
        commands: &subs.commands,
        agents,
        pages: &pages,
        window,
        batches: &batches,
        carried: &carry_of,
    };
    let whole = book::book(&world(&flight.agents, got.window))?;
    let l = book::book(&world(&inside, window))?;
    // a task's wait on a landing, from the pool's log and the event log (451 T510, `cross`)
    let dones = cross::dones(&bases(root, clones));
    let records = cross::Records {
        runs: &runs,
        stream: &got.stream,
        commands: &subs.commands,
        dones: &dones,
        takes: &takes,
        carried: &carried,
    };
    let refused = cross::refusals(&records, window.1);
    let cap = cross::cap_of(std::env::var("L7R_BUILDERS").ok().as_deref());
    let waited = cross::measure(&held::of(root, clones), &batches, &refused, window, cap);
    let text = render(
        (&l, &whole),
        (&landed(&got.aside, window, only)?, &batches),
        (window, got.window.0, &starts(root, clones)),
        (&runs, &waited),
    );
    Ok((text, window.1))
}

/// `l7r-gate measure task-time [--since S] [--until U] [--feature F] [--root R]`, `now` the time `--since <N>h` counts back from.
/// `--since last` (451 T298, [`asked`]) runs from the end of the last report it made and moves the marker to this one's end.
#[must_use]
pub fn cli(args: &[String], projects: &Path, clones: &Path, now: f64) -> Reply {
    let specs = [
        Spec::value("--since"),
        Spec::value("--until"),
        Spec::value("--feature"),
        Spec::value("--root"),
        Spec::value("--back"),
    ];
    let p = match parse_with(args, &specs, 0) {
        Ok(p) => p,
        Err(why) => return reply(String::new(), format!("usage: l7r-gate measure task-time [--since 24h|last|ISO] [--until ISO] [--feature F] [--back 48h]\n{why}\n"), 2),
    };
    // GUESS, a knob: two days back covers most tasks' start; each hour read costs about 1.3 s (`make task-time` took 55 s for
    // SINCE=24h and 238 s for SINCE=168h, measured 2026-11-25)
    let back = p.text("--back", "48h");
    let back_h = back.strip_suffix('h').and_then(|n| n.parse::<f64>().ok());
    let Some(back_h) = back_h else {
        return reply(String::new(), format!("task-time: BACK={back}: <N>h\n"), 1);
    };
    let root = Path::new(p.text("--root", "."));
    let marker = asked::marker(root);
    let asked_last = p.text("--since", "24h") == "last";
    let (since, from) = match (asked_last, asked::last(&marker)) {
        (false, _) => (p.text("--since", "24h").to_owned(), String::new()),
        (true, Some(at)) => (at.clone(), format!("from the end of the last report, {at}")),
        (true, None) => (
            "24h".to_owned(),
            "no earlier report is recorded, so the last 24 hours".to_owned(),
        ),
    };
    let done = since_of(&since, now).and_then(|since| {
        run(
            root,
            (&since, p.text("--until", ""), back_h),
            p.text("--feature", ""),
            (projects, clones),
        )
    });
    match done {
        Ok((text, _)) if !asked_last => reply(text, String::new(), 0),
        // the marker moves only once its report is made, and only for `SINCE=last`
        Ok((text, end)) => {
            let until = iso_of(end);
            let said = format!(
                "SINCE=last: {from}, to {until}; the next `make task-time SINCE=last` starts there (the marker: {}).\n\n",
                marker.display()
            );
            match asked::mark(&marker, &until, &iso_of(now)) {
                Ok(()) => reply(format!("{said}{text}"), String::new(), 0),
                Err(why) => reply(
                    text,
                    format!(
                        "task-time: the marker {} was not written ({why}), so the next SINCE=last starts where this one did - make its \
                         directory writable, or ask again with SINCE={until}\n",
                        marker.display()
                    ),
                    1,
                ),
            }
        }
        Err(why) => reply(String::new(), format!("{why}\n"), 1),
    }
}

#[cfg(test)]
mod cross_tests;
#[cfg(test)]
mod pool_tests;
#[cfg(test)]
mod tests;
#[cfg(test)]
mod tier_tests;
