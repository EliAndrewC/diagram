//! The feature's hourly checkpoint: the step-back and every owed review, together (feature 383, plan D10-D13; ported from
//! `scripts/reviews/checkpoint.py`, feature 449 T89). An hour of the feature's time after its start or its last checkpoint, a
//! step-back review of the hour (the round arbiter on an `hour:<feature>@<n>` trigger) and every review unit then owed come due at
//! once, and `make tick` is held until they are answered; `dev/step-back.json` set `off` suspends it (feature 405 T43). The clock is
//! the glyph clock's file, under the feature: `checkpoint_at`, `checkpoints`, `checkpoint_open_at`, `checkpoint_trigger`,
//! `checkpoint_units`, `units_since`.
//!
//! `l7r-gate reviews checkpoint open|hold|status|due|switch [on|off] [--why W] [--root DIR] [--tool T] [--agent A]`.

use std::path::{Path, PathBuf};

use serde_json::{json, Map, Value};

use super::glyph::{active_feature, entry, feature_start, CLOCK, GLYPH_HOUR_S, PAIRING};
use super::owed::all_owed;
use super::{
    as_float, git, gitdir, int_of, iso_seconds, local_time, now, py_path, read_object, reply,
    write_json,
};
use crate::record::args::{parse_with, Spec};
use crate::record::bundle::py_repr;
use crate::Reply;

/// The switch: absent, or any state but "off", means the step-back runs.
const SWITCH: &str = "dev/step-back.json";
/// A gap in the feature's own event log longer than this, with no Stop before it, is time the feature was not worked.
const IDLE_S: f64 = 20.0 * 60.0;
/// Dispatches this close after an admitted one are the same assistant message.
const SAME_MESSAGE_S: f64 = 5.0;
const ADMITTED: &str = "checkpoint-admitted";

fn clock(root: &Path) -> (Option<PathBuf>, Map<String, Value>) {
    let path = gitdir(root).map(|g| g.join(CLOCK));
    let clock = path
        .as_deref()
        .map(|p| read_object(Some(p)))
        .unwrap_or_default();
    (path, clock)
}

fn save(path: Option<&Path>, clock: Map<String, Value>) {
    if let Some(p) = path {
        let _ = write_json(p, &Value::Object(clock));
    }
}

/// The switch's record while the step-back is suspended (`{state, why, who, utc}`), or an empty one.
#[must_use]
pub fn suspended(root: &Path) -> Map<String, Value> {
    let sw = read_object(Some(&root.join(SWITCH)));
    if sw.get("state") == Some(&json!("off")) {
        sw
    } else {
        Map::new()
    }
}

/// Set the switch: `off` suspends the step-back, `on` resumes it; a reason of two words or more, who and when kept.
fn throw(root: &Path, state: &str, why: &str, at: f64) -> Result<Map<String, Value>, String> {
    if !matches!(state, "on" | "off") || why.split_whitespace().count() < 2 {
        return Err(
            "make step-back-off|step-back-on REASON=\"<why, two words or more>\"".to_owned(),
        );
    }
    let named = git(root, &["config", "user.name"]).filter(|w| !w.is_empty());
    let person = named.as_deref().unwrap_or("unknown");
    let secs = int_of(at.floor());
    #[expect(clippy::cast_sign_loss, reason = "the clock is past the epoch")]
    let (y, mo, d, h, mi, s) = l7r_guard::shared::log::civil(secs as u64);
    let mut sw = Map::new();
    sw.insert("state".to_owned(), json!(state));
    sw.insert("why".to_owned(), json!(why.trim()));
    sw.insert("who".to_owned(), json!(person));
    sw.insert(
        "utc".to_owned(),
        json!(format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")),
    );
    let _ = std::fs::create_dir_all(root.join("dev"));
    let _ = write_json(&root.join(SWITCH), &Value::Object(sw.clone()));
    Ok(sw)
}

/// The feature's event log, each event with its time; an unreadable line skipped.
fn events(root: &Path, feature: &str) -> Vec<(f64, Value)> {
    let Some(path) = gitdir(root).map(|g| g.join("l7r-events").join(format!("{feature}.jsonl")))
    else {
        return Vec::new();
    };
    let text = std::fs::read_to_string(path).unwrap_or_default();
    crate::record::repo::universal(&text)
        .lines()
        .filter_map(|raw| {
            let e: Value = serde_json::from_str(raw).ok()?;
            let t = iso_seconds(e.get("t"))?;
            Some((t, e))
        })
        .collect()
}

fn ev(e: &Value) -> &str {
    e.get("ev").and_then(Value::as_str).unwrap_or("")
}

/// Seconds between `since` and `now` the session spent waiting on the GM: each gap from a Stop to the GM's next prompt, clipped.
fn gm_waits(root: &Path, feature: &str, since: f64, at: f64) -> f64 {
    let (mut waited, mut stop): (f64, Option<f64>) = (0.0, None);
    for (t, e) in events(root, feature) {
        match ev(&e) {
            "Stop" => stop = Some(stop.unwrap_or(t)),
            "UserPromptSubmit" if stop.is_some() => {
                if e.get("gm") == Some(&json!(true)) {
                    waited += (t.min(at) - stop.unwrap_or(t).max(since)).max(0.0);
                }
                stop = None;
            }
            "PreToolUse" => stop = None,
            _ => {}
        }
    }
    waited
}

/// Seconds between `since` and `now` the feature was not worked on: each gap longer than `IDLE_S`, less `IDLE_S`, unless it opens with a Stop.
fn idle(root: &Path, feature: &str, since: f64, at: f64) -> f64 {
    let (mut gone, mut last, mut stopped): (f64, Option<f64>, bool) = (0.0, None, false);
    for (t, e) in events(root, feature) {
        if let Some(l) = last {
            if !stopped {
                let (lo, hi) = (l.max(since), t.min(at));
                if hi - lo > IDLE_S {
                    gone += (hi - lo - IDLE_S).max(0.0);
                }
            }
        }
        let kind = ev(&e);
        stopped = kind == "Stop" || (stopped && !matches!(kind, "UserPromptSubmit" | "PreToolUse"));
        last = Some(t);
    }
    gone
}

/// `{feature, suspended, due, since, hour, open, units, units_since}`; `{feature, due: false}` with no feature or no event log.
pub fn state(root: &Path, at: Option<f64>) -> Map<String, Value> {
    let at = at.unwrap_or_else(now);
    let feature = active_feature(root);
    let start = if feature.is_empty() {
        None
    } else {
        feature_start(root, &feature)
    };
    let mut out = Map::new();
    out.insert("feature".to_owned(), json!(feature));
    let Some(start) = start else {
        out.insert("due".to_owned(), json!(false));
        return out;
    };
    let mine = match clock(root).1.get(&feature) {
        Some(Value::Object(m)) => m.clone(),
        _ => Map::new(),
    };
    let since = start.max(as_float(mine.get("checkpoint_at")));
    let off = !suspended(root).is_empty();
    let due = !off
        && at - since - gm_waits(root, &feature, since, at) - idle(root, &feature, since, at)
            >= GLYPH_HOUR_S;
    let hour = mine
        .get("checkpoints")
        .map_or(0, |v| int_of(as_float(Some(v))))
        + 1;
    let open = if off {
        String::new()
    } else {
        mine.get("checkpoint_trigger")
            .filter(|v| crate::cohort::truthy(v))
            .map(crate::record::bundle::py_str)
            .unwrap_or_default()
    };
    out.insert("suspended".to_owned(), json!(off));
    out.insert("due".to_owned(), json!(due));
    out.insert("since".to_owned(), json!(since));
    out.insert("hour".to_owned(), json!(hour));
    out.insert("open".to_owned(), json!(open));
    out.insert(
        "units".to_owned(),
        mine.get("checkpoint_units")
            .filter(|v| crate::cohort::truthy(v))
            .cloned()
            .unwrap_or_else(|| json!([])),
    );
    out.insert(
        "units_since".to_owned(),
        json!(as_float(mine.get("units_since"))),
    );
    out
}

/// Why the hour cannot be opened: the session exported one feature and `.specify/feature.json` names another; "" when they agree.
fn misaligned(root: &Path, exported: &str) -> String {
    let named = exported.trim().trim_matches('/');
    let Some(pointer) = std::fs::read_to_string(root.join(".specify/feature.json"))
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
    else {
        return String::new();
    };
    let fd = pointer
        .get("feature_directory")
        .map(crate::record::bundle::py_str)
        .unwrap_or_default();
    let held = py_path(&fd)
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    if !named.is_empty()
        && root.join("specs").join(named).is_dir()
        && !held.is_empty()
        && held != named
    {
        let number = named.split('-').next().unwrap_or(named);
        return format!(".specify/feature.json names {held} but this session works {named}: run `make use-feature F={number}` first");
    }
    String::new()
}

fn text(m: &Map<String, Value>, k: &str) -> String {
    m.get(k).and_then(Value::as_str).unwrap_or("").to_owned()
}

/// `make step-back`: the hour's trigger, opened once - its time and the units owed then kept with it; refused before the hour is up.
fn open_checkpoint(root: &Path, at: f64, exported: &str) -> Result<String, String> {
    let why = misaligned(root, exported);
    if !why.is_empty() {
        return Err(why);
    }
    let st = state(root, Some(at));
    let open = text(&st, "open");
    if !open.is_empty() {
        return Ok(open);
    }
    let due = st.get("due") == Some(&json!(true));
    if st.get("suspended") == Some(&json!(true)) && !due {
        let sw = suspended(root);
        let say = |k: &str| {
            sw.get(k)
                .map_or_else(|| "None".to_owned(), crate::record::bundle::py_str)
        };
        return Err(format!(
            "the hourly step-back is suspended ({}, {}: {}) - make step-back-on REASON=\"<why>\" resumes it (feature 405 T43)",
            say("who"),
            say("utc"),
            say("why")
        ));
    }
    if !due {
        let when = st.get("since").and_then(Value::as_f64).map_or_else(
            || "never (no feature or event log)".to_owned(),
            |since| {
                format!(
                    "{}, in {} s",
                    local_time(since + GLYPH_HOUR_S, "%H:%M:%S"),
                    int_of(since + GLYPH_HOUR_S - at)
                )
            },
        );
        return Err(format!(
            "the checkpoint is not due - the feature's next hour is up at {when}"
        ));
    }
    let feature = text(&st, "feature");
    let hour = st.get("hour").and_then(Value::as_i64).unwrap_or(1);
    let trigger = format!("hour:{feature}@{hour}");
    let (path, mut clock) = clock(root);
    let units: Vec<String> = all_owed(root)
        .1
        .iter()
        .map(super::owed::Unit::slug)
        .collect();
    let mine = entry(&mut clock, &feature);
    let stamp = int_of(at);
    mine.insert("checkpoint_open_at".to_owned(), json!(stamp));
    mine.insert("checkpoint_trigger".to_owned(), json!(trigger));
    mine.insert("checkpoint_units".to_owned(), json!(units));
    mine.insert("units_since".to_owned(), json!(stamp));
    save(path.as_deref(), clock);
    l7r_guard::shared::checks::arbiter::try_trip(
        root,
        &trigger,
        "hour",
        "",
        &format!("the feature's hourly step-back, hour {hour}"),
        &json!(at),
        "",
    )?;
    Ok(trigger)
}

/// The hour's ruling is recorded (`l7r-gate arbiter ruled`): the clock restarts from when the checkpoint opened.
pub fn close_checkpoint(root: &Path, trigger: &str) {
    let (path, mut clock) = clock(root);
    for mine in clock.values_mut().filter_map(Value::as_object_mut) {
        if mine.get("checkpoint_trigger") != Some(&json!(trigger)) {
            continue;
        }
        let opened = mine
            .shift_remove("checkpoint_open_at")
            .unwrap_or_else(|| json!(int_of(now())));
        mine.insert("checkpoint_at".to_owned(), opened);
        let n = mine
            .get("checkpoints")
            .map_or(0, |v| int_of(as_float(Some(v))));
        mine.insert("checkpoints".to_owned(), json!(n + 1));
        mine.shift_remove("checkpoint_trigger");
    }
    save(path.as_deref(), clock);
}

/// The engine key of the clone's working tree (`make -s engine-key REF=worktree`), "" where it cannot be had.
fn current_key(root: &Path) -> String {
    std::process::Command::new("make")
        .args(["-s", "engine-key", "REF=worktree"])
        .current_dir(root)
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
        .unwrap_or_default()
}

fn nowhere(root: &Path) -> PathBuf {
    gitdir(root).unwrap_or(PathBuf::from("/nonexistent"))
}

/// Does the unit's verdict record answer it at `key` - PASS or NEEDS-WORK at the engine key the tree has now?
fn answered(root: &Path, slug: &str, key: &str) -> bool {
    let rec = read_object(Some(
        &nowhere(root)
            .join("review-verdicts")
            .join(format!("{slug}.json")),
    ));
    let verdict = rec.get("verdict").and_then(Value::as_str).unwrap_or("");
    let at = rec
        .get("engine_key")
        .filter(|v| crate::cohort::truthy(v))
        .map(crate::record::bundle::py_str)
        .unwrap_or_default();
    !key.is_empty() && matches!(verdict, "PASS" | "NEEDS-WORK") && at == key
}

/// The checkpoint's units still owed, not dispatched since it opened and not answered at the tree's engine key.
fn undispatched(root: &Path, units: &[String], since: f64) -> Vec<String> {
    if units.is_empty() {
        return Vec::new();
    }
    let owed_now: Vec<String> = all_owed(root)
        .1
        .iter()
        .map(super::owed::Unit::slug)
        .collect();
    let pairing = read_object(Some(&nowhere(root).join(PAIRING)));
    let disp = pairing.get("dispatched").cloned().unwrap_or(Value::Null);
    let at = |s: &str| as_float(disp.get(s).and_then(|d| d.get("at")));
    let left: Vec<String> = units
        .iter()
        .filter(|s| owed_now.contains(s) && at(s) < since)
        .cloned()
        .collect();
    if left.is_empty() {
        return Vec::new();
    }
    let key = current_key(root);
    left.into_iter()
        .filter(|s| !answered(root, s, &key))
        .collect()
}

/// The refusal `make tick` prints while the checkpoint holds it, or "".
pub fn hold(root: &Path, at: Option<f64>) -> String {
    let st = state(root, at);
    if text(&st, "feature").is_empty()
        || !st.contains_key("since")
        || st.get("suspended") == Some(&json!(true))
    {
        return String::new();
    }
    let open = text(&st, "open");
    if !open.is_empty() {
        let bundle = open
            .split_once(':')
            .map_or("", |(_, b)| b)
            .replace('@', "-");
        return format!(
            "the feature's hourly checkpoint is open ({open}) and owes the round arbiter's ruling: dispatch `round-arbiter` on the bundle \
             `make step-back` built (/tmp/l7r-check/step-back-{bundle}/MANIFEST.md); it records the ruling with make arbiter-ruled (feature 383)"
        );
    }
    if st.get("due") == Some(&json!(true)) {
        return "the feature has run an hour since its last checkpoint: run `make step-back` (the round arbiter steps back over the hour) \
                and dispatch the review checks owed now (`make verify` writes one prompt per unit) - feature 383"
            .to_owned();
    }
    let units: Vec<String> = st
        .get("units")
        .and_then(Value::as_array)
        .map(|u| u.iter().map(crate::record::bundle::py_str).collect())
        .unwrap_or_default();
    let left = undispatched(root, &units, as_float(st.get("units_since")));
    if left.is_empty() {
        return String::new();
    }
    format!(
        "the last checkpoint owed {} review unit(s) not yet dispatched: {} - `make verify` writes one prompt per unit; dispatch each on a \
         green gate (feature 383)",
        left.len(),
        left.join(", ")
    )
}

/// The refusal a `make done` or an agent dispatch gets when the feature's hour is up and its step-back is not yet open, or "".
fn due(root: &Path, tool: &str, atype: &str, at: f64) -> String {
    if tool == "Agent" && atype == "round-arbiter" {
        return String::new();
    }
    let mark = gitdir(root).map(|g| g.join(ADMITTED));
    let st = state(root, Some(at));
    if st.get("due") != Some(&json!(true)) || !text(&st, "open").is_empty() {
        if let Some(m) = mark.as_deref().filter(|_| tool == "Agent") {
            let _ = std::fs::write(m, format!("{}\n", l7r_guard::shared::pyjson::py_float(at)));
        }
        return String::new();
    }
    let last: f64 = mark
        .as_deref()
        .filter(|m| m.is_file())
        .and_then(|m| std::fs::read_to_string(m).ok())
        .and_then(|t| t.trim().parse().ok())
        .unwrap_or(0.0);
    if tool == "Agent" && (0.0..=SAME_MESSAGE_S).contains(&(at - last)) {
        return String::new();
    }
    "the feature's hour is up and its step-back is not open: run `make step-back` and dispatch `round-arbiter` on the bundle it builds, \
     then carry on (feature 383; the round arbiter's tooling fix on hour:374@2)"
        .to_owned()
}

fn usage(why: &str) -> Reply {
    reply(
        String::new(),
        format!("l7r-gate reviews checkpoint: {why}\n"),
        2,
    )
}

/// `checkpoint.py`'s command line.
pub fn cli(args: &[String]) -> Reply {
    let specs = [
        Spec::value("--why"),
        Spec::value("--root"),
        Spec::value("--tool"),
        Spec::value("--agent"),
    ];
    let p = match parse_with(args, &specs, 2) {
        Ok(p) => p,
        Err(why) => return usage(&why),
    };
    let Some(verb) = p.positional.first().map(String::as_str) else {
        return usage("the following arguments are required: verb");
    };
    if !matches!(verb, "open" | "hold" | "status" | "due" | "switch") {
        return usage(&format!("argument verb: invalid choice: {}", py_repr(verb)));
    }
    let state_word = p.positional.get(1).map_or("", String::as_str);
    if !state_word.is_empty() && !matches!(state_word, "on" | "off") {
        return usage(&format!(
            "argument state: invalid choice: {}",
            py_repr(state_word)
        ));
    }
    let asked = p.text("--root", ".");
    let root = git(&py_path(asked), &["rev-parse", "--show-toplevel"])
        .filter(|t| !t.is_empty())
        .map_or_else(|| py_path(asked), PathBuf::from);
    let lines = |s: String, code: i32| {
        if s.is_empty() {
            reply(String::new(), String::new(), 0)
        } else {
            reply(s + "\n", String::new(), code)
        }
    };
    match verb {
        "switch" => match throw(&root, state_word, p.text("--why", ""), now()) {
            Ok(sw) => {
                let did = if sw.get("state") == Some(&json!("off")) {
                    "suspended"
                } else {
                    "resumed"
                };
                reply(
                    format!("step-back: {did} - {}\n", text(&sw, "why")),
                    String::new(),
                    0,
                )
            }
            Err(e) => reply(String::new(), format!("step-back: {e}\n"), 2),
        },
        "open" => match open_checkpoint(
            &root,
            now(),
            &std::env::var("SPECIFY_FEATURE").unwrap_or_default(),
        ) {
            Ok(t) => reply(t + "\n", String::new(), 0),
            Err(e) => reply(String::new(), format!("step-back: {e}\n"), 1),
        },
        "due" => lines(
            due(&root, p.text("--tool", ""), p.text("--agent", ""), now()),
            1,
        ),
        "hold" => lines(hold(&root, None), 1),
        _ => reply(
            l7r_guard::shared::pyjson::dumps(&Value::Object(state(&root, None)), Some(1), true)
                + "\n",
            String::new(),
            0,
        ),
    }
}

#[cfg(test)]
mod tests;
