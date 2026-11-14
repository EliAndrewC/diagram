//! `l7r-gate set-down <feature>` - `make set-down F=<feature> WHY="<reason>"`: the feature's work is set down (feature 385 T70, plan
//! D89). Ported whole from `scripts/set-down.py` by feature 449 T135 (`ask:449-phase3-remainder`), beside `task-start`, whose
//! `task-starts.jsonl` it reads.
//!
//! Writes one row to `<git common dir>/set-downs.jsonl`, which the guard's `set_down_hooks` reads: a turn may then end with the
//! feature's tasks open, until the next `make task-start`. The reason (`SET_DOWN_WHY`) is two words or more, as every escape's is.
//!
//! WORK THAT RESISTED IS SET DOWN ON THE ARBITER'S RULING (feature 405, the GM 2026-10-21). While an open task of the feature owes a
//! part B (`approach-owed.json`) and the round arbiter has ruled on nothing since, the set-down is refused and names `make
//! arbiter-ask`: a process stop goes to the arbiter, whose rules ask first whether more room, within the research, settles it. T26
//! was set down "for the GM to see T107 first" when the arbiter would have ruled the farms wider apart. The escape is
//! `SET_DOWN_OK="<reason>"` (the usage cap's wind-down, say), logged by the make target.
//!
//! A GOAL IS WORKED TO THE USAGE CAP (the GM 2026-10-23: *"I thought we had tooling to make it so that we didn't stop partway through
//! a feature being done when I asked for it to be worked to completion"*). The run of 2026-10-23 set 405 down at 69% of an armed 80%
//! cap and ended its turn on a question at 1:53am with the GM asleep. While the 7-day figure is under the cap - the weekly soft cap, or
//! a goal's cap where one is still armed (`~/.claude/hooks/usage_cap.py`; the GM retired goal caps 2026-10-24) - the set-down is
//! refused unless the round arbiter has ruled on a set-down ask since the feature's last task-start.

use std::path::{Path, PathBuf};

use l7r_guard::shared::py_text::{fmt_g, split, strip};
use l7r_guard::shared::pyjson::{dumps, py_str};
use l7r_guard::shared::speckit::splitlines;
use serde_json::{json, Map, Value};

use crate::phase_sources::glob::glob;
use crate::{common_text, git, now_secs, raised, read_strict, reply, utc_text, Reply};

/// What the environment says: `SET_DOWN_WHY`, `SET_DOWN_OK`, the session, the cap's directory and the home.
pub type Env<'a> = &'a dyn Fn(&str) -> Option<String>;

/// A `%Y-%m-%dT%H:%M:%SZ` stamp's sortable form (`str(text or "")[:19]`).
fn utc_key(v: Option<&Value>) -> String {
    let text = v.map_or_else(|| "None".to_owned(), py_str);
    text.chars().take(19).collect()
}

/// The git directory as `rev-parse --absolute-git-dir` names it, else `<root>/.git`.
fn git_dir(root: &Path) -> PathBuf {
    let (_, out) = git(root, &["rev-parse", "--absolute-git-dir"]);
    let text = strip(&String::from_utf8_lossy(&out)).to_owned();
    Some(text)
        .filter(|t| !t.is_empty())
        .map_or(root.join(".git"), PathBuf::from)
}

/// A file's lines, "" where it is not a file.
fn lines_of(path: &Path) -> Result<Vec<String>, String> {
    if !path.is_file() {
        return Ok(Vec::new());
    }
    Ok(splitlines(&read_strict(path)?)
        .into_iter()
        .map(str::to_owned)
        .collect())
}

/// One line as `json.loads(raw)` and a `.get` on it read it: none for a line that is not JSON (`ValueError`, skipped), a raise for a
/// row that is no object (`AttributeError`, which nothing caught).
fn row_of(raw: &str) -> Result<Option<Map<String, Value>>, String> {
    match serde_json::from_str::<Value>(raw) {
        Ok(Value::Object(m)) => Ok(Some(m)),
        Ok(other) => Err(format!(
            "AttributeError: '{}' object has no attribute 'get'",
            kind(&other)
        )),
        Err(_) => Ok(None),
    }
}

/// Every row of a JSON-lines file, each read by [`row_of`] before any is used, as the Python built its list first.
fn rows(path: &Path) -> Result<Vec<Map<String, Value>>, String> {
    let mut out = Vec::new();
    for raw in lines_of(path)? {
        out.extend(row_of(&raw)?);
    }
    Ok(out)
}

fn kind(v: &Value) -> &'static str {
    match v {
        Value::Null => "NoneType",
        Value::Bool(_) => "bool",
        Value::Number(n) if n.is_f64() => "float",
        Value::Number(_) => "int",
        Value::String(_) => "str",
        Value::Array(_) => "list",
        Value::Object(_) => "dict",
    }
}

/// Python's truth of a JSON value.
fn truthy(v: &Value) -> bool {
    match v {
        Value::Null => false,
        Value::Bool(b) => *b,
        Value::Number(n) => n.as_f64().is_some_and(|f| f != 0.0),
        Value::String(s) => !s.is_empty(),
        Value::Array(a) => !a.is_empty(),
        Value::Object(m) => !m.is_empty(),
    }
}

/// Why the feature may not be set down yet - an open task owes a part B the round arbiter has not ruled on since - or none.
fn unruled(root: &Path, feature: &str) -> Result<Option<String>, String> {
    let gd = git_dir(root);
    // `except (OSError, ValueError)`: unreadable, not UTF-8 or not JSON reads as nothing owed
    let owed = std::fs::read(gd.join("approach-owed.json"))
        .ok()
        .and_then(|b| String::from_utf8(b).ok())
        .and_then(|t| serde_json::from_str::<Value>(&t).ok());
    let Some(owed) = owed else {
        return Ok(None);
    };
    let items: Vec<Value> = match owed {
        Value::Array(a) => a,
        // a dict iterates its keys and a string its characters, none of them a row
        Value::Object(_) | Value::String(_) => Vec::new(),
        other => {
            return Err(format!(
                "TypeError: '{}' object is not iterable",
                kind(&other)
            ))
        }
    };
    let d = root.join("specs").join(feature);
    let tasks = if d.join("tasks.md").is_file() {
        read_strict(&d.join("tasks.md"))?
    } else {
        String::new()
    };
    let open: Vec<&Map<String, Value>> = items
        .iter()
        .filter_map(Value::as_object)
        .filter(|r| r.get("feature").is_some_and(|f| f == feature))
        .filter(|r| {
            r.get("part")
                .filter(|p| truthy(p))
                .map_or_else(|| "B".to_owned(), py_str)
                == "B"
        })
        .filter(|r| {
            tasks.contains(&format!(
                "- [ ] {} ",
                r.get("task").map_or_else(|| "None".to_owned(), py_str)
            ))
        })
        .collect();
    // `max` keeps the first of equal keys
    let Some(last) = open.iter().copied().reduce(|best, r| {
        if utc_key(r.get("utc")) > utc_key(best.get("utc")) {
            r
        } else {
            best
        }
    }) else {
        return Ok(None);
    };
    let since = utc_key(last.get("utc"));
    for row in rows(&d.join("arbiter.jsonl"))? {
        if utc_key(row.get("utc")) >= since {
            return Ok(None);
        }
    }
    let said = |k: &str| last.get(k).map_or_else(|| "None".to_owned(), py_str);
    Ok(Some(format!(
        "set-down: refused - {} at {} owes {} a part B, and the round arbiter has ruled on nothing since. Work that resisted is set down on its ruling, which asks first whether more room within the research settles it: make arbiter-ask SUBJECT=set-down-{} WHY=\"<what resisted, the routes measured, the room knob and its ceiling>\" FILES=\"<the cohort record>\", then make set-down again (escape: SET_DOWN_OK=\"<reason>\", e.g. the usage cap's wind-down)",
        said("trigger"),
        said("utc"),
        said("task"),
        said("task")
    )))
}

/// The feature's last task-start stamp in this clone, "" where none.
fn since_start(root: &Path, feature: &str) -> Result<String, String> {
    let gd = git_dir(root);
    let mut last = String::new();
    for raw in lines_of(&gd.join("task-starts.jsonl"))? {
        let Some(row) = row_of(&raw)? else {
            continue;
        };
        if row.get("feature").is_some_and(|f| f == feature) {
            last = last.max(utc_key(row.get("utc")));
        }
    }
    Ok(last)
}

/// A JSON number (a bool among them, as `isinstance(x, (int, float))` takes one) as a float.
fn number(v: Option<&Value>) -> Option<f64> {
    match v? {
        Value::Bool(b) => Some(f64::from(u8::from(*b))),
        Value::Number(n) => n.as_f64(),
        _ => None,
    }
}

/// The JSON object a file holds, `{}` where it cannot be read, is not JSON or is no object (the Python's `load`).
fn load(path: &Path) -> Map<String, Value> {
    match std::fs::read(path)
        .ok()
        .and_then(|b| String::from_utf8(b).ok())
        .and_then(|t| serde_json::from_str(&t).ok())
    {
        Some(Value::Object(m)) => m,
        _ => Map::new(),
    }
}

/// `x.get(key)` of a value the Python called `.get` on: an object's field, none for `{}`'s stand-in (a falsy value), a raise otherwise.
fn get<'v>(v: Option<&'v Value>, key: &str) -> Result<Option<&'v Value>, String> {
    match v {
        Some(Value::Object(m)) => Ok(m.get(key)),
        Some(other) if truthy(other) => Err(format!(
            "AttributeError: '{}' object has no attribute 'get'",
            kind(other)
        )),
        _ => Ok(None),
    }
}

/// Why the feature may not be set down while the 7-day figure is under the cap - a goal's armed cap where one is armed, else the
/// account's weekly soft cap (`usage_cap.py cap`, 90% by default) - or none. BOTH ARE READ FRESH AT EACH CALL (the GM 2026-10-24: "the
/// cap suddenly changes while you're in the middle of working"): the cap from `caps.json` as it stands now, and the reading only while
/// its week lasts - past `seven_day_resets_at` it is last week's figure and decides nothing, as `usage_cap._live_pct` reads it.
fn under_cap(root: &Path, feature: &str, env: Env) -> Result<Option<String>, String> {
    let sid = env("CLAUDE_CODE_SESSION_ID").unwrap_or_default();
    let cap_dir = env("USAGE_CAP_DIR").filter(|d| !d.is_empty()).map_or_else(
        || PathBuf::from(env("HOME").unwrap_or_default()).join(".claude/usage-cap"),
        PathBuf::from,
    );
    let safe: String = sid
        .chars()
        .map(|c| {
            if c.is_alphanumeric() || c == '_' || c == '-' {
                c
            } else {
                '_'
            }
        })
        .collect();
    let latest = if sid.is_empty() {
        Map::new()
    } else {
        load(&cap_dir.join(format!("latest-{safe}.json")))
    };
    let Some(pct) = number(latest.get("seven_day")) else {
        return Ok(None);
    };
    #[expect(
        clippy::cast_precision_loss,
        reason = "the clock as Python's time.time() float"
    )]
    let now = now_secs() as f64;
    if number(latest.get("seven_day_resets_at")).is_some_and(|r| now > r) {
        return Ok(None);
    }
    // a reading came from a session's own file, so there is a session here (the Python's `if sid` always held by now)
    let budget = load(&cap_dir.join(format!("budget-{safe}.json")));
    let uuid = get(latest.get("account"), "uuid")?
        .filter(|u| truthy(u))
        .map_or_else(String::new, py_str);
    let caps = load(&cap_dir.join("caps.json"));
    let soft = number(get(caps.get(&uuid), "cap")?);
    let cap = number(budget.get("cap")).or(soft).unwrap_or(90.0);
    if pct >= cap {
        return Ok(None);
    }
    let since = since_start(root, feature)?;
    // read line by line, as the Python's loop returned at the first ruling before it reached a row that would raise
    for raw in lines_of(&root.join("specs").join(feature).join("arbiter.jsonl"))? {
        let Some(row) = row_of(&raw)? else {
            continue;
        };
        let trigger = row.get("trigger").map_or_else(String::new, py_str);
        if trigger.starts_with("ask:set-down") && utc_key(row.get("utc")) >= since {
            return Ok(None);
        }
    }
    Ok(Some(format!(
        "set-down: refused - the weekly cap is {}% and the 7-day figure is {}%: a goal is worked to the cap, and the GM may be asleep. Take the next open task; a stop for any other reason goes to the round arbiter: make arbiter-ask SUBJECT=set-down-{} WHY=\"<what blocks every open task, the routes measured>\", then make set-down again (escape: SET_DOWN_OK=\"<reason>\")",
        fmt_g(cap),
        fmt_g(pct),
        feature.split('-').next().unwrap_or("")
    )))
}

/// `l7r-gate set-down <feature>` from `cwd`, the process's environment read.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    cli_with(args, cwd, &|k| std::env::var(k).ok())
}

/// `l7r-gate set-down <feature>` from `cwd`, `env` what the environment says.
fn cli_with(args: &[String], cwd: &Path, env: Env) -> Reply {
    let why = env("SET_DOWN_WHY").unwrap_or_default();
    let why = strip(&why);
    if args.len() != 1 || split(why).len() < 2 {
        return reply(
            String::new(),
            "usage: make set-down F=<feature> WHY=\"<why it stops here, two words or more>\"\n"
                .to_owned(),
            2,
        );
    }
    let (code, out) = git(cwd, &["rev-parse", "--show-toplevel"]);
    if code != Some(0) {
        return raised(
            "set-down",
            String::new(),
            "",
            "subprocess.CalledProcessError: git rev-parse --show-toplevel failed",
        );
    }
    let root = PathBuf::from(strip(&String::from_utf8_lossy(&out)));
    let feature = &args[0];
    let found = match glob(&root.join("specs"), &format!("{feature}*")) {
        Ok(f) => f,
        Err(why) => return raised("set-down", String::new(), "", &why),
    };
    let mut hits: Vec<String> = found
        .iter()
        .filter(|d| d.is_dir())
        .filter_map(|d| d.file_name().map(|n| n.to_string_lossy().into_owned()))
        .filter(|n| n == feature || n.starts_with(&format!("{feature}-")))
        .collect();
    hits.sort();
    if hits.len() != 1 {
        return reply(
            String::new(),
            format!("set-down: no single specs/{feature}* directory\n"),
            2,
        );
    }
    let hit = &hits[0];
    if strip(&env("SET_DOWN_OK").unwrap_or_default()).is_empty() {
        let why_not = match unruled(&root, hit) {
            Ok(None) => under_cap(&root, hit, env),
            other => other,
        };
        match why_not {
            Ok(Some(refusal)) => return reply(String::new(), format!("{refusal}\n"), 2),
            Ok(None) => {}
            Err(why) => return raised("set-down", String::new(), "", &why),
        }
    }
    let common = Some(common_text(cwd))
        .filter(|c| !c.is_empty())
        .ok_or(std::io::Error::other(
            "subprocess.CalledProcessError: git rev-parse --git-common-dir failed",
        ));
    let row = json!({"feature": hit, "why": why, "utc": utc_text(now_secs())});
    let written = common
        .and_then(|c| {
            std::fs::OpenOptions::new()
                .create(true)
                .append(true)
                .open(Path::new(&c).join("set-downs.jsonl"))
        })
        .and_then(|mut f| {
            std::io::Write::write_all(&mut f, format!("{}\n", dumps(&row, None, true)).as_bytes())
        });
    if let Err(e) = written {
        return raised("set-down", String::new(), "", &e.to_string());
    }
    reply(format!("set-down: {hit} set down ({why}); a turn may end with its tasks open until the next make task-start\n"), String::new(), 0)
}

#[cfg(test)]
mod tests;
