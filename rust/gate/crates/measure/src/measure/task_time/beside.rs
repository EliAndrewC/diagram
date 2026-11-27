//! What the report prints BESIDE a landed task's minutes (feature 451 T512): its size, its counts, its turns and its tokens
//! ([`super::sized`], [`super::turns`]), and a table of each task's minutes in seven groups of the report's own categories, each
//! its % of the task, the window's tasks' side in a last row. A share is printed only of TIME and of TOKENS - a task's tokens by
//! kind and by actor (the GM 2026-11-27: "Can you also make it so that the report that we generate includes percentages as
//! well?"); a COUNT and a line class carry none, and test runs and compiles carry the minutes per run of their own category
//! instead (451 T521, the GM the same day: "I don't know that it's useful to see percentages for counts the way that it is to see
//! percentages for time", and of the line classes: "I think I only really care about that for time and tokens"). Raw figures
//! only - no ratio of lines to minutes, no ranking (the GM's Goodhart caution).

use std::collections::HashMap;
use std::fmt::Write as _;

use super::super::where_time::columns::ran::{self, Counts};
use super::super::where_time::columns::spent::Tok;
use super::super::where_time::columns::SLOT_WAIT;
use super::book::{Cell, Key, Ledger};
use super::sized::{Lines, Size};
use super::turns::Turns;
use super::{is_gm, m, pct, CARRY};

/// What the report prints beside the minutes.
#[derive(Debug, Default)]
pub struct Extra {
    /// Each landed task's size.
    pub sizes: HashMap<Key, Size>,
    /// Each task's turns and tokens.
    pub turns: HashMap<Key, Turns>,
    /// The main session's model calls booked to no task, and their tokens.
    pub unbooked: (usize, Tok),
}

/// The minutes per run of `n` runs that held `secs` seconds, `-` for no run (451 T521).
#[must_use]
pub fn per_run(n: usize, secs: f64) -> String {
    if n == 0 {
        return "-".to_owned();
    }
    #[expect(clippy::cast_precision_loss, reason = "a run count")]
    let per = secs / n as f64;
    m(per)
}

/// What a count of runs prints after it: the minutes per run of `secs`, its category's seconds, nothing for no run (451 T521).
fn each(n: usize, secs: f64) -> String {
    let per = per_run(n, secs);
    if n == 0 {
        String::new()
    } else {
        format!(", {per} min each")
    }
}

/// The seconds of category `cat` in category rows, none where it is absent.
fn secs(cats: &[(String, Cell)], cat: &str) -> f64 {
    cats.iter()
        .find(|(n, _)| n == cat)
        .map_or(0.0, |(_, v)| v.min)
}

/// Lines added and deleted, no share (451 T521).
fn lines(l: Lines) -> String {
    format!("+{} -{}", l.add, l.del)
}

/// Tokens in thousands with their share of `of`.
fn tokens(x: f64, of: f64) -> String {
    format!(
        "{}k ({})",
        super::super::events::fixed(x / 1000.0, 1),
        pct(x, of)
    )
}

/// Tokens in thousands.
fn kilo(x: f64) -> String {
    format!("{}k", super::super::events::fixed(x / 1000.0, 1))
}

/// Every token a call's usage names.
fn all(t: &Tok) -> f64 {
    t.out + t.fresh + t.cached + t.created
}

/// The ledger's counts for `key` (its counted lines, 451 T522, [`counts`]) and its make runs.
#[must_use]
pub fn counts(l: &Ledger, key: &Key) -> (Counts, usize) {
    let makes = l
        .runs
        .iter()
        .filter(|((k, t), _)| k == key && t.starts_with("make "))
        .map(|(_, n)| n)
        .sum();
    (ran::counts(l.ran.get(key).into_iter().flatten()), makes)
}

/// A count of lines and the minutes each of their own spans held on average, `-` minutes for none (451 T521, T522).
fn runs_each((n, secs): (usize, f64)) -> String {
    format!("{n}{}", each(n, secs))
}

/// A task's compiles: how many, how many did work, the minutes each (451 T522).
fn compiles(c: &Counts) -> String {
    format!(
        "{} ({} of {} s or more){}",
        c.compile.0,
        c.worked,
        super::super::events::fixed(ran::NOOP_BELOW_S, 1),
        each(c.compile.0, c.compile.1)
    )
}

/// The size, count, turn and token cells of one task, in the summary table's order.
fn cells(whole: &Ledger, k: &Key, x: &Extra) -> Vec<String> {
    let s = x.sizes.get(k).cloned().unwrap_or_default();
    let t = x.turns.get(k).copied().unwrap_or_default();
    let (counted, makes) = counts(whole, k);
    let tok = t.tok();
    let every = all(&tok);
    let shared = if s.shared.is_empty() {
        String::new()
    } else {
        format!(" (shared with {})", s.shared.join(" "))
    };
    vec![
        format!("{}{shared}", s.commits),
        lines(s.test),
        lines(s.code),
        lines(s.prose),
        runs_each(counted.unit),
        runs_each(counted.cover),
        compiles(&counted),
        makes.to_string(),
        t.builders.to_string(),
        t.agents.to_string(),
        t.session.to_string(),
        tokens(tok.out, every),
        tokens(tok.fresh, every),
        tokens(tok.cached, every),
        tokens(tok.created, every),
        format!(
            "{} / {} / {}",
            pct(all(&t.builders_tok), every),
            pct(all(&t.agents_tok), every),
            pct(all(&t.session_tok), every)
        ),
    ]
}

/// The summary table: one row a landed task, then the one line naming each figure's source and what it cannot see.
pub fn table(out: &mut String, whole: &Ledger, landed: &[(f64, Key)], x: &Extra) {
    out.push_str(
        "## The landed tasks' size, counts, turns and tokens (451 T512: raw figures, a share only of tokens, for \
         the process review to read beside the minutes, never a target)\n\n\
         | task | commits | test lines | non-test lines | prose lines | unit-test runs | coverage runs | compiles | make runs | \
         builder turns | review-agent turns | session turns | output | fresh input | cache read | cache write | tokens: builders / \
         review agents / session |\n\
         |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n",
    );
    for (_, k) in landed {
        let _ = writeln!(
            out,
            "| {} {} | {} |",
            k.0,
            k.1,
            cells(whole, k, x).join(" | ")
        );
    }
    let _ = writeln!(
        out,
        "\n(a share only of time and of tokens: each token kind's % is of the task's tokens, and the last column each actor's share \
         of them; a count and a line class carry none (451 T521): unit-test runs, coverage runs and compiles carry the minutes \
         each of their own lines' spans held (451 T522), a make target's runs its own row's minutes per run in the task's target table, lines and \
         turns are counts alone) {SOURCES} The main session's calls booked to no task: {}, their tokens {} (output {}, cache read {}).\n",
        x.unbooked.0,
        kilo(all(&x.unbooked.1)),
        kilo(x.unbooked.1.out),
        kilo(x.unbooked.1.cached)
    );
}

/// What each figure is read from and what it cannot see, the one line the summary prints.
pub const SOURCES: &str = "Sources: LINES from git, each commit whose subject names the task (`451 T510:`, a bundle's `451 T470 \
     T363:` whole under each task it names, marked shared, never split; a coverage repair `451: T490's coverage repair`), a landing's \
     tick commit left out; test = `tests/`, `tests.rs`, `*_tests.rs`, prose = `specs/` and `.md`, an inline `#[cfg(test)]` block \
     counted non-test (its files counted in the task's section); a commit whose subject names no task is in no row. UNIT-TEST RUNS, COVERAGE RUNS \
     and COMPILES are the `Phase` lines its runs held, tied as its minutes are, and its pool tree's pre-warm builds by their own task \
     (451 T522, each listed under the task's tables): a unit-test run a `test` line, a coverage run a `cover-run` line, a compile \
     every compiler invocation - a `build` or `cover-build` line (written only where the binary's key moved, so a kept result is \
     none), each `lint` pass and each `prewarm` - and one that ran 1.0 s or more counted as having done work, a shorter one likely \
     cargo finding every crate fresh (a GUESS from its span: the line does not say); a `make quick` or preflight line, which holds \
     its own cargo calls' lines, is counted in none. A pool tree's line goes only to a run of its holder's tasks. MAKE RUNS are its `make` targets' runs. TURNS \
     are model calls, each message id once: a builder's and a review agent's from its transcript over the read-back (the agent under \
     the task its lines name), the main session's from its transcript, each call booked to the task its next own event-log line \
     names, a line carrying only the session's `make task-start` mark booked to none, a call after the task's carry the second \
     tier's. TOKENS are those calls' usage, the advisor's own calls not in them.";

/// The seven groups of the per-task minutes table, in its order.
pub const GROUPS: [&str; 7] = [
    "builder thinking",
    "code read/write",
    "tests",
    "compile",
    "review",
    "session",
    "other",
];

/// The group a category's minutes go to, none for the GM's rows (out of the working time) and a carry's (the landings' side).
#[must_use]
pub fn group(cat: &str) -> Option<&'static str> {
    const REVIEW: [&str; 7] = [
        "plan review",
        "claims round",
        "record and pop-up checks",
        "the GM's filter",
        "other review agents",
        "map and building reviews",
        "arbiter",
    ];
    if is_gm(cat) || cat == CARRY {
        return None;
    }
    Some(
        if cat.ends_with("reading code")
            || cat.ends_with("writing code")
            || cat == "shell reads and file edits"
        {
            "code read/write"
        } else if cat == "tests" || cat == "hook suites" {
            "tests"
        } else if cat == "compile" || cat == SLOT_WAIT {
            "compile"
        } else if REVIEW.iter().any(|r| cat.starts_with(r)) {
            "review"
        } else if cat.starts_with("builders: ") {
            "builder thinking"
        } else if cat.starts_with("main session: ") {
            "session"
        } else {
            "other"
        },
    )
}

/// The grouping said in one line.
pub const GROUPING: &str = "Grouped from the report's own categories: builder thinking = every `builders:` row but its reading and \
     writing code; code read/write = `reading code` and `writing code` (builders' and the session's) and `shell reads and file \
     edits`; tests = `tests` and `hook suites`; compile = `compile` and `waiting on a build slot`; review = the review agents' and \
     their commands' rows (plan review, claims round, record and pop-up checks, the GM's filter, other review agents, map and \
     building reviews, arbiter); session = every other `main session:` row; other = the rest (git, wait loops, programs, research \
     and page sessions, docs, waits). The GM's rows and a carry are left out: each % is of the task's working minutes.";

/// A row of the grouped table from category rows: each group's minutes with its % of their total, and the total.
fn grouped(cats: &[(String, Cell)]) -> String {
    let mut by: HashMap<&str, f64> = HashMap::new();
    for (cat, c) in cats {
        if let Some(g) = group(cat) {
            *by.entry(g).or_default() += c.min;
        }
    }
    // a fold from 0.0, not `sum`, whose empty sum is -0.0 and printed so
    let whole = by.values().fold(0.0, |a, b| a + b);
    let mut out = format!("{} |", m(whole));
    for g in GROUPS {
        let x = by.get(g).copied().unwrap_or(0.0);
        let _ = write!(out, " {} ({}) |", m(x), pct(x, whole));
    }
    out
}

/// The OWN-PATH seconds of the keys `pick` takes, by category, as category rows (the seconds in `min`), largest first.
#[must_use]
pub fn own_cats(l: &Ledger, pick: &dyn Fn(&Key) -> bool) -> Vec<(String, Cell)> {
    cats_of(&l.own, pick)
}

/// The builders' stopped stretches beside the own path, as [`own_cats`] reads the path.
pub fn stopped_cats(l: &Ledger, pick: &dyn Fn(&Key) -> bool) -> Vec<(String, Cell)> {
    cats_of(&l.stopped, pick)
}

/// One of the own-path maps' category rows over the keys `pick` takes, the largest first.
fn cats_of(
    map: &HashMap<(Key, String, String), f64>,
    pick: &dyn Fn(&Key) -> bool,
) -> Vec<(String, Cell)> {
    let mut by: HashMap<&str, f64> = HashMap::new();
    for ((_, cat, _), s) in map.iter().filter(|((k, _, _), _)| pick(k)) {
        *by.entry(cat).or_default() += s;
    }
    let mut rows: Vec<(String, Cell)> = by
        .into_iter()
        .filter(|(_, s)| *s > 0.0)
        .map(|(c, s)| {
            let cell = Cell {
                min: s,
                ..Cell::default()
            };
            (c.to_owned(), cell)
        })
        .collect();
    rows.sort_by(|a, b| b.1.min.total_cmp(&a.1.min).then(a.0.cmp(&b.0)));
    rows
}

/// A reader of category rows from a ledger, over the keys a pick takes.
type Rows = dyn Fn(&Ledger, &dyn Fn(&Key) -> bool) -> Vec<(String, Cell)>;

/// One grouped table: one row a landed task (its whole time, `whole`), the window's tasks' side (`l`) last, of `rows`' figure.
fn grouped_table(
    out: &mut String,
    (whole, l): (&Ledger, &Ledger),
    landed: &[(f64, Key)],
    (what, rows): (&str, &Rows),
) {
    let _ = write!(out, "| task | {what} |");
    for g in GROUPS {
        let _ = write!(out, " {g} |");
    }
    out.push_str("\n|---|---|---|---|---|---|---|---|---|\n");
    for (_, k) in landed {
        let _ = writeln!(
            out,
            "| {} {} | {}",
            k.0,
            k.1,
            grouped(&rows(whole, &|x| x == k))
        );
    }
    let side = rows(l, &|x| !super::is_tier(x));
    let _ = writeln!(out, "| the window, the tasks' side | {}\n", grouped(&side));
}

/// The per-task grouped tables: machine minutes, then OWN-PATH minutes (451 T512, the GM 2026-11-27: a bottleneck that runs in
/// parallel rarely blocks), each group its % of the task's own total.
pub fn groups(out: &mut String, ledgers: (&Ledger, &Ledger), landed: &[(f64, Key)]) {
    let _ = write!(
        out,
        "## Each landed task's minutes by group, each its % of the task (451 T512)\n\n{GROUPING}\n\nMachine minutes (overlapping):\n\n"
    );
    let machine = |l: &Ledger, pick: &dyn Fn(&Key) -> bool| super::sums(l, pick).0;
    grouped_table(out, ledgers, landed, ("working minutes", &machine));
    out.push_str(OWN_PATH);
    grouped_table(out, ledgers, landed, ("own-path minutes", &own_cats));
    out.push_str(STOPPED_BESIDE);
    grouped_table(out, ledgers, landed, ("stopped minutes", &stopped_cats));
}

/// What the stopped figure is, said once above its table and on each task's own-path line.
pub const STOPPED_BESIDE: &str = "Beside its own path, never in it: each builder's STOPPED stretches (its turn ended, outside its \
     spans), each second booked by the same descent to what was in flight - its own background test, compile or review, a shell \
     read - or to waiting to be resumed with nothing in flight. By the GM's blocking (request.md, 2026-11-25 (l)) a builder stopped \
     on its own review is waiting on it; the report cannot tell whether its next step needed that work (451 T512's plan review).\n\n";

/// What the own-path figure is, said once above its table.
pub const OWN_PATH: &str = "On its own path: each builder's own clock, each second booked once to what its next step waited on - its \
     own turn, a foreground test or compile, a slot wait, a wait loop, a review agent it waited on - by the descent the main \
     session's blocking takes; a run beside its turn (backgrounded, or a check a monitor watches while it reads or edits) counts \
     in machine minutes only; a stretch its builder was stopped (its own work in flight, or waiting to be resumed) is in the stopped \
     table below, not here: the path is the builder's spans, each second its own task's, summing to its builder minutes. The main session's own clock is its \
     blocking, not in these rows (451 T512, the GM 2026-11-27).\n\n";

/// A landed task's own-path table: each category's own-path minutes and its % of the task's own path.
pub fn own_table(out: &mut String, whole: &Ledger, key: &Key) {
    let rows = own_cats(whole, &|x| x == key);
    let all = rows.iter().fold(0.0, |a, (_, c)| a + c.min);
    let _ = write!(
        out,
        "Its own path (451 T512): {} min.\n\n| category | own-path minutes | % of its own path |\n|---|---|---|\n",
        m(all)
    );
    for (cat, c) in &rows {
        let _ = writeln!(out, "| {cat} | {} | {} |", m(c.min), pct(c.min, all));
    }
    let stopped = stopped_cats(whole, &|x| x == key);
    let each: Vec<String> = stopped
        .iter()
        .map(|(c, v)| format!("{c} {}", m(v.min)))
        .collect();
    let _ = writeln!(
        out,
        "\nBeside its path, its builders stopped (451 T512): {} min - {}.",
        m(stopped.iter().fold(0.0, |a, (_, c)| a + c.min)),
        each.join(" - ")
    );
    out.push('\n');
}

/// The task's line beside its tables: its `tests` and `compile` minutes, its counted lines (451 T522, each listed under its tables)
/// with the minutes each, its size, its turns and its tokens, a share only of its tokens (451 T521).
#[must_use]
pub fn line(whole: &Ledger, key: &Key, cats: &[(String, Cell)], x: &Extra) -> String {
    let (n, _) = counts(whole, key);
    let rans = whole.ran.get(key).map_or(&[][..], Vec::as_slice);
    let step = |s: &str| rans.iter().filter(|r| r.step == s).count();
    let c = cells(whole, key, x);
    let inline = x.sizes.get(key).map_or(0, |s| s.inline);
    format!(
        "Beside its minutes (451 T512): `tests` {} min, `compile` {} min; its counted lines (451 T522, listed under its tables): {} \
         unit-test runs{}, {} coverage runs{}, {} compiles ({} of {} s or more){} - {} builds, {} coverage builds, {} lint passes, {} pre-warm builds; {} make \
         runs (each target's in the runs column below, with its minutes per run); {} commits: test {}, non-test {}, prose {}, \
         {inline} of its non-test `.rs` files holding an inline test block; turns: builders {}, review agents {}, session {}; tokens: \
         output {}, fresh input {}, cache read {}, cache write {}; by actor (builders / review agents / session) {}.\n",
        m(secs(cats, "tests")),
        m(secs(cats, "compile")),
        n.unit.0,
        each(n.unit.0, n.unit.1),
        n.cover.0,
        each(n.cover.0, n.cover.1),
        n.compile.0,
        n.worked,
        super::super::events::fixed(ran::NOOP_BELOW_S, 1),
        each(n.compile.0, n.compile.1),
        step("build"),
        step("cover-build"),
        step("lint"),
        step(ran::PREWARM),
        c[7],
        c[0],
        c[1],
        c[2],
        c[3],
        c[8],
        c[9],
        c[10],
        c[11],
        c[12],
        c[13],
        c[14],
        c[15]
    )
}
