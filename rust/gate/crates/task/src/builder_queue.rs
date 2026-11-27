//! `l7r-gate queue`, `queue-add` and `builder-next` (feature 451 T313, with T395 and the first half of T297; the GM, 2026-11-26:
//! "what you are doing sounds like something that we want our tooling to actually enforce. Because otherwise you just have to
//! remember to keep our tasks in flight"): THE BUILDERS' QUEUE LISTED, WRITTEN AND ASKED FOR ITS NEXT TASK. The format, each
//! state, the overlap rule and the next entry are `l7r_shared::builder_queue`'s, which the Stop guard reads too
//! (`rust/guard/src/guards/pool_idle_hooks.rs`); this module is the three commands over it and `make builder-done`'s first line.
//!
//! - `make queue [F=<feature>]` lists `specs/<feature>/queue.txt` (every queue of the clone where no feature is named), each
//!   entry with its state computed: landed, built, in flight, waiting on what, READY. A malformed line is an error naming the
//!   line, and nothing is listed.
//! - `make queue-add T= KIND= [JOBS= MEASURES= LOAD=1 CRATE= FILES= WAITS= NOTE=]` appends one entry, read back through the one
//!   parser before it is written, refused for a task with no box in the feature's `tasks.md` and outside the clone (the queue
//!   every command reads is the clone's file, whatever tree asks). A plain edit of the file does as well.
//! - `make builder-next [F=<feature>]` prints the next READY entry (performance work first, FR-013) that overlaps no task holding a tree, with its exact
//!   `make builder-brief` command, each READY entry it passed over with the in-flight task it overlaps, each held tree whose task
//!   the queue does not list, and the pool's count against `L7R_BUILDERS`; with no entry to hand out, why.
//! - [`dispatch`] is that entry as `make builder-done`'s step 1, where a placeholder stood while the queue was prose (451 T394).
//! - A fix entry `make builder-brief` would refuse - one of its tasks' lines names a new mechanism by the brief's own test,
//!   `l7r_shared::builder_brief::mechanism` - is FLAGGED by each of the four (`l7r_shared::builder_queue::flag`, 451 T412, which the
//!   pool-idle Stop block says too, 451 T481), never skipped: see there.
//! - With no feature named, a `queue.txt` that does not parse is PASSED OVER, a line on stderr each (451 T418): another feature may
//!   hold a file of that name in another form (the page sessions' queues of features 269 and 280), as the Stop guard's walk passes it.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_gate_core::Reply;
use l7r_shared::builder_brief::targets;
use l7r_shared::builder_pool;
use l7r_shared::builder_queue::{self as queue, flag, flagged, Board, State};

use crate::builder_brief::feature_dir;
use crate::builder_tree::{self, feature_key, refused, Pool};
use crate::reply;

const ADD_USAGE: &str = "usage: make queue-add T=<task(s)> KIND=fix|measurement|build-half|closing-half [F=<feature>] [JOBS=<1-3>] [MEASURES=<things measured>] [LOAD=1] [CRATE=\"<crate dirs>\"] [FILES=\"<paths or prefixes>\"] [WAITS=\"<T<n> GM alone>\"] [NOTE=\"<a note>\"]\n";
const HEADER: &str = "# The builders' queue of this feature: one entry a line, in the order to hand out. make queue lists it with each entry's state\n# computed (landed, built, in flight, waiting, READY); make builder-next names the next; make queue-add appends, and a plain edit\n# does as well. A line STAYS until its task is landed; a task that needs another builder gets another line. The format and the\n# rules: rust/guard/shared/src/builder_queue.rs.\n# <task[,task]> <kind> [jobs=<1-3>] [measures=<n>] [load=1] crates=<dir,dir|-> files=<path,prefix|-> [waits=<T<n>,GM,alone>] [note=<the rest of the line>]\n";
const RULE: &str = "  (two entries overlap where a crate or path of one is the other's, or lies under it by whole path components)\n";

/// `dir` as a reader names it: its path under the clone.
fn under(p: &Pool, dir: &Path) -> String {
    let file = dir.join(queue::FILE);
    file.strip_prefix(&p.clone)
        .unwrap_or(&file)
        .display()
        .to_string()
}

/// The feature directories a command reads: the one `feature` names, else every one of the clone that holds a queue.
fn dirs(p: &Pool, feature: &str) -> Result<Vec<PathBuf>, String> {
    let key = feature_key(feature);
    let start = "make queue-add T=<task(s)> KIND=<kind> F=<feature> starts one";
    if key.is_empty() {
        let all = queue::queues(&p.clone);
        if all.is_empty() {
            return Err(format!(
                "no specs/*/queue.txt in {} - {start}",
                p.clone.display()
            ));
        }
        return Ok(all);
    }
    let dir = feature_dir(&p.clone, &key);
    dir.map(|d| vec![d])
        .ok_or_else(|| format!("no specs/{key}-* directory in {}", p.clone.display()))
}

/// The boards of the queues `feature` names, each with its file's path under the clone, and a line for each file passed over. A
/// queue named by `feature` that cannot be read or parsed is the error; with no feature named, such a file is passed over (451
/// T418: features 269 and 280 hold a page session's `queue.txt`), and only where none parses is the first one's error the answer.
fn boards(p: &Pool, feature: &str) -> Result<(Vec<(Board, String)>, String), String> {
    let trees = builder_pool::read(&p.common);
    let (mut out, mut passed, mut first) = (Vec::new(), String::new(), None);
    let named = !feature_key(feature).is_empty();
    for dir in dirs(p, feature)? {
        match queue::board(&p.clone, &p.common, &dir, &trees) {
            Ok(b) => out.push((b, under(p, &dir))),
            Err(why) if named => return Err(why),
            Err(why) => {
                let _ = writeln!(passed, "passed over {}: it does not parse as a builders' queue ({} line(s) refused; make queue F={} names each)", under(p, &dir), why.lines().count(), feature_key(&dir.file_name().unwrap_or_default().to_string_lossy()));
                first.get_or_insert(why);
            }
        }
    }
    match first.filter(|_| out.is_empty()) {
        Some(why) => Err(why),
        None => Ok((out, passed)),
    }
}

/// The make targets of the clone's Makefile, which the mechanism test reads a `make <target>` against.
fn known(p: &Pool) -> BTreeSet<String> {
    targets(&std::fs::read_to_string(p.clone.join("Makefile")).unwrap_or_default())
}

fn word(s: &State) -> String {
    match s {
        State::Landed => "landed".to_owned(),
        State::Built(owed) => format!("built ({owed})"),
        State::InFlight(tree) => format!("in flight ({})", tree.display()),
        State::Waiting(on) => format!("waiting on {on}"),
        State::Ready => "READY".to_owned(),
    }
}

fn listing(b: &Board, at: &str, known: &BTreeSet<String>) -> String {
    let words: Vec<String> = b.states.iter().map(word).collect();
    let count = |opens: &str| words.iter().filter(|w| w.starts_with(opens)).count();
    let mut out = format!(
        "queue: {at} - {} entries: {} landed, {} built, {} in flight, {} waiting, {} READY\n",
        words.len(),
        count("landed"),
        count("built"),
        count("in flight"),
        count("waiting"),
        count("READY")
    );
    for (i, (e, w)) in b.entries.iter().zip(&words).enumerate() {
        let _ = writeln!(
            out,
            "  line {:>3}  {:<14} {:<13} {w}",
            e.line,
            e.name(),
            e.kind
        );
        out += &flagged(b, i, known, "              ");
    }
    out
}

/// What was passed over and what was not checked, a line each, `pad` before each.
fn asides(b: &Board, pad: &str) -> String {
    let mut out = String::new();
    for (i, why) in &b.next.skipped {
        let e = &b.entries[*i];
        let _ = writeln!(
            out,
            "{pad}passed over: {} (line {}) - {why}",
            e.name(),
            e.line
        );
    }
    if !b.next.skipped.is_empty() {
        let _ = write!(out, "{pad}{}", RULE.trim_start());
    }
    for holder in &b.next.unchecked {
        let _ = writeln!(out, "{pad}not checked: {holder} holds a tree and the queue lists no entry in flight for it - its files are unknown");
    }
    out
}

fn next_said(b: &Board, at: &str, known: &BTreeSet<String>) -> String {
    let head = match b.next.pick {
        Some(i) => format!(
            "builder-next: {} {} (line {} of {at}), the next READY entry that overlaps no task in flight, performance work first (FR-013):\n  {}\n{}",
            b.key,
            b.entries[i].name(),
            b.entries[i].line,
            b.entries[i].command(&b.key),
            flagged(b, i, known, "  ")
        ),
        None => format!("builder-next: no entry of {at} to hand out - {}\n", b.next.none),
    };
    head + &asides(b, "  ")
}

/// THE OPEN PERFORMANCE TASKS NO QUEUE LINE NAMES (451 T313's round-3 ruling; T421), a line each with the command that writes its
/// line, `pad` before each, under one heading; nothing where there is none. Named FIRST by `make queue`, `make builder-next` and `make
/// builder-done`'s step 1, as by the Stop block.
fn unlisted_said(p: &Pool, prefer: &str, pad: &str) -> String {
    let all = queue::unlisted(&p.clone, &p.common, prefer);
    if all.is_empty() {
        return String::new();
    }
    let mut out = "FIRST, open performance work (FR-013) no queue line names - write each one's line (CRATE= and FILES= as its task line names them, WAITS= where it waits, which quiets it):\n".to_owned();
    for u in &all {
        let _ = writeln!(
            out,
            "{pad}{}   ({}, KIND by make builder-brief's mechanism test)",
            u.command, u.tasks
        );
    }
    out
}

/// THE NEXT DISPATCH, as `make builder-done` prints it after `  1. `: the open performance tasks no queue line names first, then the
/// entry [`queue::offer`] picks over EVERY queue of the clone - a READY performance entry of any active feature's queue before the
/// done task's own feature's first pick (FR-013 "in any active feature", 451 T313's round-3 ruling) - with what it passed over; or
/// why there is none: no entry to hand out, or the feature's queue missing or malformed (never a refusal: the tree is committed).
pub(crate) fn dispatch(p: &Pool, feature: &str) -> String {
    let key = feature_key(feature);
    let trees = builder_pool::read(&p.common);
    // every readable queue: another feature's file of that name in another form (a page session's) is passed, as `idle` passes it
    let (mut all, mut paths) = (Vec::new(), Vec::new());
    for dir in queue::queues(&p.clone) {
        if let Ok(b) = queue::board(&p.clone, &p.common, &dir, &trees) {
            all.push(b);
            paths.push(under(p, &dir));
        }
    }
    let mut out = unlisted_said(p, &key, "     ");
    let own = all.iter().find(|b| b.key == key);
    // every line after the first under step 1's `  1. `, as `asides` pads its own
    let lead = |out: &str| -> &'static str {
        if out.is_empty() {
            ""
        } else {
            "     "
        }
    };
    if own.is_none() {
        let why = boards(p, feature).err().unwrap_or_default();
        let pad = lead(&out);
        let _ = writeln!(
            out,
            "{}no next dispatch named: {} - make queue-add T=<task(s)> KIND=<kind> F={feature} starts the queue",
            pad,
            why.lines().next().unwrap_or_default()
        );
    }
    match queue::offer(&all, &key) {
        Some((b, i)) => {
            let at = all
                .iter()
                .position(|o| std::ptr::eq(o, b))
                .map_or("", |k| paths[k].as_str());
            let e = &b.entries[i];
            let pad = lead(&out);
            let _ = writeln!(
                out,
                "{}{}   ({} {}, line {} of {at}: the next READY entry that overlaps no task in flight, performance work of any queue first)",
                pad,
                e.command(&b.key),
                b.key,
                e.name(),
                e.line
            );
            out + &flagged(b, i, &known(p), "     ") + &asides(b, "     ")
        }
        None => match own {
            Some(b) => format!(
                "{out}{}no next dispatch: {} (make queue F={})\n",
                lead(&out),
                b.next.none,
                b.key
            ),
            None => out,
        },
    }
}

/// THE OVERLAP AT A HANDOUT (451 T408, the first half of T297's line: "at dispatch, name the overlap"): a tree handed to `tasks` of
/// `feature` - by `make builder-tree`, or `make builder-brief T=<a task picked by hand>` through it - says on stderr each task in
/// flight, in any queue of the clone, whose entry the task's own open entry overlaps ([`queue::overlap`], the one rule `make
/// builder-next` passes an entry over by). A notice, never a refusal: the second of the two to land meets the first's edits at its
/// carry. Nothing where the feature has no readable queue, the task no open entry, or the entry overlaps none.
pub(crate) fn overlapping(p: &Pool, tasks: &[String], feature: &str) -> String {
    let trees = builder_pool::read(&p.common);
    let all: Vec<(Board, String)> = queue::queues(&p.clone)
        .iter()
        .filter_map(|dir| {
            let b = queue::board(&p.clone, &p.common, dir, &trees).ok()?;
            Some((b, under(p, dir)))
        })
        .collect();
    let mine = |e: &queue::Entry| e.tasks.iter().any(|t| tasks.contains(t));
    let Some((own, at)) = all.iter().find(|(b, _)| b.key == feature) else {
        return String::new();
    };
    let open =
        |(e, s): &(&queue::Entry, &State)| mine(e) && !matches!(s, State::Landed | State::Built(_));
    let Some((e, _)) = own.entries.iter().zip(&own.states).find(open) else {
        return String::new();
    };
    let mut out = String::new();
    for (b, _) in &all {
        for (o, s) in b.entries.iter().zip(&b.states) {
            let State::InFlight(tree) = s else { continue };
            let Some(path) = queue::overlap(e, o).filter(|_| b.key != feature || !mine(o)) else {
                continue;
            };
            let _ = writeln!(out, "builder-tree: NOTICE - {feature} {}'s queue entry (line {} of {at}) overlaps {} {} in flight at {path} ({}): the second of the two to land meets the first's edits; make builder-next names an entry that overlaps nothing in flight", e.name(), e.line, b.key, o.name(), tree.display());
        }
    }
    out
}

/// `make queue-add`: one entry appended to the feature's queue.
fn add(p: &Pool, args: &[String], note: &str) -> Reply {
    let arg = |i: usize| args.get(i).map_or("", String::as_str);
    let items =
        |i: usize| -> Vec<&str> { arg(i).split([' ', ',']).filter(|w| !w.is_empty()).collect() };
    let no = |why: String| refused(format!("queue-add: refused - {why}\n{ADD_USAGE}"));
    let key = feature_key(arg(1));
    if key.is_empty() {
        return no(
            "F=<feature> (or SPECIFY_FEATURE) names the feature whose queue it is".to_owned(),
        );
    }
    let Some(dir) = feature_dir(&p.clone, &key) else {
        return no(format!(
            "no specs/{key}-* directory in {}",
            p.clone.display()
        ));
    };
    let mut line = format!("{} {}", items(0).join(","), arg(2));
    for (name, i) in [("jobs", 3), ("measures", 4), ("load", 8)] {
        if !arg(i).is_empty() {
            let _ = write!(line, " {name}={}", arg(i));
        }
    }
    let or_none = |i: usize| {
        Some(items(i).join(","))
            .filter(|l| !l.is_empty())
            .unwrap_or("-".to_owned())
    };
    let _ = write!(line, " crates={} files={}", or_none(5), or_none(6));
    if !items(7).is_empty() {
        let _ = write!(line, " waits={}", items(7).join(","));
    }
    let note: Vec<&str> = note.split_whitespace().collect();
    if !note.is_empty() {
        let _ = write!(line, " note={}", note.join(" "));
    }
    let entry = match queue::parse(&line).map(|all| all.into_iter().next()) {
        Err(why) => return no(why),
        Ok(None) => return no("T=<task(s)> and KIND=<kind> name the entry".to_owned()),
        Ok(Some(e)) => e,
    };
    let at = under(p, &dir);
    let tasks = std::fs::read_to_string(dir.join("tasks.md")).unwrap_or_default();
    let boxed = |t: &String| {
        let named = format!("] {t} ");
        tasks
            .lines()
            .any(|l| l.trim_start().starts_with("- [") && format!("{l} ").contains(&named))
    };
    if let Some(t) = entry.tasks.iter().find(|t| !boxed(t)) {
        return no(format!(
            "{t} has no box in {}: file it first (make task-add)",
            at.replace(queue::FILE, "tasks.md")
        ));
    }
    let path = dir.join(queue::FILE);
    let mut text = std::fs::read_to_string(&path).unwrap_or_else(|_| HEADER.to_owned());
    if !text.ends_with('\n') {
        text.push('\n');
    }
    let _ = writeln!(text, "{}", entry.text());
    let mut entry = entry;
    entry.line = text.lines().count();
    entry.ordinal = queue::parse(&text).map_or(1, |all| {
        all.iter()
            .filter(|o| o.tasks.contains(&entry.tasks[0]))
            .count()
    });
    let line_of = |t: &String| {
        let named = format!("- [ ] {t} ");
        tasks
            .lines()
            .find(|l| format!("{} ", l.trim_start()).starts_with(&named))
            .map(str::to_owned)
    };
    let flag = flag(&entry, &key, &line_of, &known(p), "  ");
    match std::fs::write(&path, &text) {
        Ok(()) => reply(
            format!(
                "queue-add: {at} line {}: {}\n{flag}",
                entry.line,
                entry.text()
            ),
            String::new(),
            0,
        ),
        Err(e) => reply(String::new(), format!("queue-add: {at}: {e}\n"), 1),
    }
}

/// `l7r-gate queue|queue-add|builder-next <args>` from `cwd`, the entry's note read from `NOTE`.
#[must_use]
pub fn cli(verb: &str, args: &[String], cwd: &Path) -> Reply {
    let note = std::env::var("NOTE").unwrap_or_default();
    run(verb, args, cwd, &note, queue::builders())
}

pub(crate) fn run(verb: &str, args: &[String], cwd: &Path, note: &str, builders: usize) -> Reply {
    let Some(p) = builder_tree::pool(cwd) else {
        return refused(format!("{verb}: not in a git repository\n"));
    };
    if verb == "queue-add" {
        // the queue is the clone's: every reader reads it there, and a pool tree's builder writes only its own tree
        if crate::toplevel_or_dot(cwd) != p.clone {
            return refused(format!("queue-add: refused - run it in the clone, {}: the queue every command reads is the clone's, and this tree is not it\n", p.clone.display()));
        }
        return add(&p, args, note);
    }
    let (all, passed) = match boards(&p, args.first().map_or("", String::as_str)) {
        Ok(all) => all,
        Err(why) => return refused(format!("{verb}: {why}\n")),
    };
    let known = known(&p);
    let mut out = if verb == "builder-next" {
        unlisted_said(
            &p,
            &feature_key(args.first().map_or("", String::as_str)),
            "  ",
        )
    } else {
        String::new()
    };
    for (b, at) in &all {
        out += &if verb == "queue" {
            listing(b, at, &known)
        } else {
            next_said(b, at, &known)
        };
    }
    if verb == "queue" {
        out += &unlisted_said(
            &p,
            &feature_key(args.first().map_or("", String::as_str)),
            "  ",
        );
    }
    if verb == "builder-next" {
        let trees = builder_pool::read(&p.common);
        let free = trees.iter().filter(|t| t.free()).count();
        let _ = writeln!(out, "builder-next: {} of {builders} builders in flight (L7R_BUILDERS), {free} pool tree(s) free", trees.len() - free);
    }
    reply(
        out,
        passed.replace("passed over ", &format!("{verb}: passed over ")),
        0,
    )
}

#[cfg(test)]
mod tests;
