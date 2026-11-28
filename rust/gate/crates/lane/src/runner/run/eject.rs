//! A batch's EJECTIONS (feature 461 T15, T18, T19, T24; split out of `run.rs` at the 1,000-line bar): a red's changes filed as
//! repair entries before their `eject` lines (`file_groups`, which the halving's `red` and `inferred` ejections call too), the
//! tripwire's hold ([`trip`]), a green set whose push failed twice ([`integrate`]), and a change whose carry stopped in conflict
//! ([`conflicted`], 461 T25).

use std::path::Path;

use serde_json::json;

use super::{all_hand_ins, in_tree, short, spec_of, stopped, HandIn, Lane, Redden, ATTEMPTS};
use crate::log;
use crate::repairs;
use crate::tripwire::{self, Trip};

/// A GREEN SET WHOSE PUSH FAILED TWICE (461 T19, D7's table): every change of `todo` filed as ONE repair entry of kind `integrate`,
/// `why` `push` - `tasks` every change's, `units` the landing's push line, `attempt` the second attempt's file, the push's output -
/// before its `eject` lines (`repairs`' doc); the batch's one `owed` line, returned for the `landed` line to be followed by. Never
/// `stopped`: the fresh builder's hand-in supersedes the set (D7), and the lane goes on with the next batch.
pub(super) fn integrate(
    l: &Lane,
    id: &str,
    todo: &[&HandIn],
    push: &str,
    attempt: &str,
    spec: &str,
) -> Result<String, String> {
    let tasks: Vec<String> = todo.iter().flat_map(|h| h.tasks.clone()).collect();
    let entry = repairs::Entry {
        feature: spec.to_owned(),
        tasks: tasks.clone(),
        kind: "integrate".to_owned(),
        ejected: todo.iter().map(|h| h.commit.clone()).collect(),
        batch: id.to_owned(),
        why: "push".to_owned(),
        units: vec![push.to_owned()],
        attempt: attempt.to_owned(),
    };
    let r = repairs::file(l.common, &l7r_gate_core::record::repo::utc_now(), &entry)?;
    for h in todo {
        l.append(
            "eject",
            &json!({"batch": id, "change": h.commit, "repair": r, "why": "push"}),
        )?;
    }
    let feature = todo.first().map_or("", |h| h.feature.as_str());
    Ok(format!(
        "lane: batch {id} green but its push failed twice - {feature} {} filed as repair {r} (integrate, push: {push}) - make builder-next hands it to a fresh builder: {attempt}",
        tasks.join(" ")
    ))
}

/// A PLACED RED'S EJECTION (D6 step 2, D7): the `attribute` line, then each placed change as a repair entry of its own (`why` `red`,
/// its units) - each entry filed before its `eject` lines (`repairs`' doc), then one `owed` line an entry, naming it and the attempt
/// file. The ejected commits, returned. A group a task of which this ejection pins a SECOND time (461 T18, `crate::tripwire`) files no
/// repair: once every other group is filed, [`trip`] holds it for the round arbiter and stops the runner. A red the record cannot
/// place is halved, never ejected here (461 T24).
pub(super) fn eject(
    l: &Lane,
    id: &str,
    tree: &Path,
    todo: &[&HandIn],
    red: &Redden,
    placed: &[(usize, Vec<String>)],
) -> Result<Vec<String>, String> {
    let groups: Vec<Group> = placed
        .iter()
        .map(|(i, units)| (vec![todo[*i]], units.clone(), "red"))
        .collect();
    let candidates: Vec<&str> = groups
        .iter()
        .flat_map(|(hs, _, _)| hs.iter().map(|h| h.commit.as_str()))
        .collect();
    l.append(
        "attribute",
        &json!({"batch": id, "candidates": candidates, "how": "record"}),
    )?;
    file_groups(l, id, tree, red, &groups)
}

/// Each of `groups` filed as a repair entry of its own before its `eject` lines, one `owed` line an entry, its red read in `red`
/// (the attempt it rests on); a group a task of which this ejection pins a SECOND time (461 T18) is held by [`trip`] once the others
/// are filed. The ejected commits, returned.
pub(super) fn file_groups(
    l: &Lane,
    id: &str,
    tree: &Path,
    red: &Redden,
    groups: &[Group],
) -> Result<Vec<String>, String> {
    let candidates: Vec<&str> = groups
        .iter()
        .flat_map(|(hs, _, _)| hs.iter().map(|h| h.commit.as_str()))
        .collect();
    // each group's trips, read before any line of this ejection is written (the pins are other batches')
    let (history, entries, hand_ins) = (
        log::read(l.common),
        repairs::read(l.common),
        all_hand_ins(l.common),
    );
    let trips: Vec<Vec<Trip>> = groups
        .iter()
        .map(|(hs, _, _)| {
            hs.iter()
                .flat_map(|h| {
                    tripwire::trips(&history, &entries, &hand_ins, &h.feature, &h.tasks, id)
                })
                .collect()
        })
        .collect();
    let mut held: Vec<(&Group, &[Trip])> = Vec::new();
    for (group, trip) in groups.iter().zip(&trips) {
        if !trip.is_empty() {
            held.push((group, trip));
            continue;
        }
        let (hs, units, why) = group;
        let tasks: Vec<String> = hs.iter().flat_map(|h| h.tasks.clone()).collect();
        let entry = repairs::Entry {
            feature: red.spec.clone(),
            tasks: tasks.clone(),
            kind: "fix".to_owned(),
            ejected: hs.iter().map(|h| h.commit.clone()).collect(),
            batch: id.to_owned(),
            why: (*why).to_owned(),
            units: units.clone(),
            attempt: red.attempt.clone(),
        };
        let r = repairs::file(l.common, &l7r_gate_core::record::repo::utc_now(), &entry)?;
        for h in hs {
            l.append(
                "eject",
                &json!({"batch": id, "change": h.commit, "repair": r, "why": why}),
            )?;
        }
        let feature = hs.first().map_or("", |h| h.feature.as_str());
        let line = format!(
            "lane: batch {id} red at attempt {} - {feature} {} ejected as repair {r} ({}) - make builder-next hands it to a fresh builder: {}",
            red.n,
            tasks.join(" "),
            said(group),
            red.attempt
        );
        l.append("owed", &json!({"batch": id, "line": line}))?;
    }
    if held.is_empty() {
        return Ok(candidates.into_iter().map(str::to_owned).collect());
    }
    trip(l, id, tree, red, &held)
}

/// An ejection's group: its changes, its units and its `why`.
pub(super) type Group<'a> = (Vec<&'a HandIn>, Vec<String>, &'static str);

/// A group's `<why>: <units>`, or that the record names none.
fn said(group: &Group) -> String {
    let (_, units, why) = group;
    let named = if units.is_empty() {
        "the record names none".to_owned()
    } else {
        units.join(", ")
    };
    format!("{why}: {named}")
}

/// A CARRY'S REPAIR (461 T25, D7's table; data-model.md, "A repair entry"): the change `h` as ONE repair entry of kind
/// `integrate` - `why` `conflict`, `units` the `conflict`ing files, or, where its carry stopped with no conflicting path but not on
/// the lane's own tree (Decision 4), `why` `carry`, `units` the carry's own stop lines - `attempt` the carry's own output kept as
/// `attempts/<batch>-carry-<sha>.log`; then its `eject` line (neither `why` pins: `tripwire::PINS`) and one `owed` line. Never
/// `stopped`: the fresh builder's hand-in supersedes the change, and the batch goes on.
pub(super) fn conflicted(
    l: &Lane,
    id: &str,
    tree: &Path,
    h: &HandIn,
    conflict: &[String],
    output: &str,
) -> Result<(), String> {
    let spec = spec_of(tree, id, &h.feature)?;
    let dir = l.common.join(log::DIR).join(ATTEMPTS);
    let kept = dir.join(format!("{id}-carry-{}.log", short(&h.commit)));
    let _ = std::fs::create_dir_all(&dir);
    let _ = std::fs::write(&kept, output);
    let attempt = kept.to_string_lossy().into_owned();
    let (why, units) = if conflict.is_empty() {
        ("carry", stop_lines(output))
    } else {
        ("conflict", conflict.to_vec())
    };
    let entry = repairs::Entry {
        feature: spec,
        tasks: h.tasks.clone(),
        kind: "integrate".to_owned(),
        ejected: vec![h.commit.clone()],
        batch: id.to_owned(),
        why: why.to_owned(),
        units: units.clone(),
        attempt: attempt.clone(),
    };
    let r = repairs::file(l.common, &l7r_gate_core::record::repo::utc_now(), &entry)?;
    l.append(
        "eject",
        &json!({"batch": id, "change": h.commit, "repair": r, "why": why}),
    )?;
    let line = format!(
        "lane: batch {id}'s carry of {} stopped{} - {} {} ejected as repair {r} (integrate, {why}: {}) - make builder-next hands it to a fresh builder; the rest of the batch goes on: {attempt}",
        short(&h.commit),
        if conflict.is_empty() { "" } else { " in conflict" },
        h.feature,
        h.tasks.join(" "),
        units.join(", ")
    );
    l.append("owed", &json!({"batch": id, "line": line}))
}

/// The carry's own stop lines in its `output` (its `carry:` and `land:` lines; none where it said none).
fn stop_lines(output: &str) -> Vec<String> {
    output
        .lines()
        .map(str::trim)
        .filter(|x| x.starts_with("carry:") || x.starts_with("land:"))
        .map(str::to_owned)
        .collect()
}

/// A command's exit, stdout and stderr; one that could not start is exit -1, its error the stderr.
pub(super) fn outcome(o: std::io::Result<std::process::Output>) -> (i32, String, String) {
    match o {
        Ok(o) => (
            o.status.code().unwrap_or(-1),
            String::from_utf8_lossy(&o.stdout).into_owned(),
            String::from_utf8_lossy(&o.stderr).into_owned(),
        ),
        Err(e) => (-1, String::new(), e.to_string()),
    }
}

/// THE TRIPWIRE FIRED (461 T18, D6 step 4; `crate::tripwire`'s doc): each held change's `eject` line with no repair and the trigger
/// it waits on, `make arbiter-ask` in the lane's tree with the two attempt files (its output beside the attempt's, `.arbiter.log`),
/// the batch's `stop` line, and the runner stopped through [`stopped`] - its one `owed` line.
fn trip(
    l: &Lane,
    id: &str,
    tree: &Path,
    red: &Redden,
    held: &[(&Group, &[Trip])],
) -> Result<Vec<String>, String> {
    let trips: Vec<Trip> = held.iter().flat_map(|(_, t)| t.iter().cloned()).collect();
    let subject = tripwire::subject(&trips);
    let trigger = format!("ask:{subject}");
    let changes: Vec<&HandIn> = held.iter().flat_map(|(g, _)| g.0.iter().copied()).collect();
    for ((hs, _, why), _) in held {
        for h in hs {
            l.append(
                "eject",
                &json!({"batch": id, "change": h.commit, "repair": null, "why": why, "arbiter": trigger, "attempt": red.attempt}),
            )?;
        }
    }
    let files = tripwire::files(&trips, &red.attempt).join(" ");
    let tasks: Vec<String> = changes.iter().flat_map(|h| h.tasks.clone()).collect();
    let feature = changes.first().map_or("", |h| h.feature.as_str());
    let reds: Vec<String> = held.iter().map(|(g, _)| said(g)).collect();
    let mut before: Vec<&str> = trips.iter().map(|t| t.before.batch.as_str()).collect();
    before.dedup();
    let pin = trips.iter().map(|t| t.n).max().unwrap_or(2);
    let why = format!(
        "{feature} {} was ejected red by the landing lane again (pin {pin}): batch {}, then batch {id} at attempt {} ({}). The lane filed no second repair. Rule: continue (the work its repair then does), accept, or a process fault.",
        tasks.join(" "),
        before.join(", "),
        red.n,
        reds.join("; ")
    );
    let spec_dir = format!("specs/{}", red.spec);
    let env = [
        ("SPECIFY_FEATURE", red.spec.as_str()),
        ("SPECIFY_FEATURE_DIRECTORY", spec_dir.as_str()),
    ];
    let words = [
        "--no-print-directory".to_owned(),
        "arbiter-ask".to_owned(),
        format!("SUBJECT={subject}"),
        format!("WHY={why}"),
        format!("FILES={files}"),
    ];
    let words: Vec<&str> = words.iter().map(String::as_str).collect();
    let (code, out, err) = outcome(in_tree(tree, &words, &env).output());
    let kept = format!("{}.arbiter.log", red.attempt);
    let _ = std::fs::write(&kept, format!("{out}{err}"));
    let shas: Vec<&str> = changes.iter().map(|h| h.commit.as_str()).collect();
    l.append(
        "stop",
        &json!({"batch": id, "why": "arbiter", "trigger": trigger, "spec": red.spec, "tasks": tasks, "held": shas, "attempts": files}),
    )?;
    let asked = match (code, tripwire::manifest(&out)) {
        (0, Some(m)) => format!("dispatch round-arbiter on {m}"),
        (0, None) => format!("dispatch round-arbiter on the bundle its output names ({kept})"),
        _ => format!(
            "make arbiter-ask SUBJECT={subject} FILES=\"{files}\" failed (exit {code}: {}), its output {kept}: ask it by hand, then dispatch round-arbiter on its bundle",
            err.lines().next().unwrap_or_default().trim()
        ),
    };
    stopped(
        l,
        id,
        format!(
            "lane: batch {id} stopped at attempt {} - {feature} {} red again ({}; pinned before in batch {}), no repair filed: the round arbiter is owed {trigger} - {asked}; once make arbiter-ruled records its ruling, make lane-start files its repair (why arbiter)",
            red.n,
            tasks.join(" "),
            reds.join("; "),
            before.join(", ")
        ),
    )
}
