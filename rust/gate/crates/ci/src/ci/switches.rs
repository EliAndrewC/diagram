//! The iteration switches (feature 132, from `l7r/diagram/switches.py`): `dev/switches.json` holds `claims` and `port`. Absent is the defaults; malformed closes: remote off, claims `clean`, the port at the last
//! committed state. Unknown keys are ignored, on purpose (feature 185): only the named axes are read, so a leftover block from before a lock was retired is simply not looked at.

use std::fmt::Write as _;
use std::path::Path;
use std::process::Command;

use serde_json::{json, Value};

use crate::codeid::stated;

const FILE: &str = "dev/switches.json";
const CLAIMS_STATES: [&str; 2] = ["report", "clean"];
const DEFAULT_CLAIMS: &str = "report";
const PORT_STATES: [&str; 2] = ["rust-only", "integrated"];
const DEFAULT_PORT: &str = "rust-only";
/// The idle timer's entry in its command line (feature 449 T014).
const IDLE_TIMER_MARK: &str = "--idle-tests";

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Axis {
    pub state: String,
    pub why: String,
    pub who: String,
    pub utc: String,
}

impl Axis {
    fn bare(state: &str) -> Self {
        Self {
            state: state.to_owned(),
            ..Self::default()
        }
    }

    fn json(&self) -> Value {
        json!({"state": self.state, "why": self.why, "who": self.who, "utc": self.utc})
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Switches {
    /// Non-empty when the file was malformed: the axes are then closed.
    pub error: String,
    pub claims: Axis,
    pub port: Axis,
}

impl Switches {
    fn defaults() -> Self {
        Self {
            error: String::new(),
            claims: Axis::bare(DEFAULT_CLAIMS),
            port: Axis::bare(DEFAULT_PORT),
        }
    }
}

/// The state of the last committed file, the state in force when the working copy's port entry is malformed.
fn committed_port(root: &Path) -> String {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["show", &format!("HEAD:{FILE}")])
        .output();
    let text = done
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
        .unwrap_or_default();
    let data: Value = serde_json::from_str(&text).unwrap_or_default();
    let state = data["port"]["state"].as_str().unwrap_or_default();
    if PORT_STATES.contains(&state) {
        state
    } else {
        DEFAULT_PORT
    }
    .to_owned()
}

fn closed(error: &str, root: &Path) -> Switches {
    let why = format!("switches.json is MALFORMED ({error}) - failing closed");
    Switches {
        error: error.to_owned(),
        claims: Axis {
            state: "clean".to_owned(),
            why: why.clone(),
            ..Axis::default()
        },
        port: Axis {
            state: committed_port(root),
            why,
            ..Axis::default()
        },
    }
}

fn text(raw: &Value, key: &str) -> String {
    raw[key].as_str().unwrap_or_default().to_owned()
}

/// An axis, or why its entry is malformed; a missing entry is its default.
fn axis(data: &Value, name: &str, allowed: &[&str; 2], default: &str) -> Result<Axis, String> {
    let Some(raw) = data.get(name) else {
        return Ok(Axis::bare(default));
    };
    if !raw.is_object() {
        return Err(format!("'{name}' is not an object"));
    }
    let state = raw["state"].as_str().unwrap_or_default();
    if !allowed.contains(&state) {
        return Err(format!(
            "{name}.state is {}, not one of ('{}', '{}')",
            raw["state"], allowed[0], allowed[1]
        ));
    }
    Ok(Axis {
        state: state.to_owned(),
        why: text(raw, "why"),
        who: text(raw, "who"),
        utc: text(raw, "utc"),
    })
}

#[must_use]
pub fn read(root: &Path) -> Switches {
    let path = root.join(FILE);
    if !path.is_file() {
        return Switches::defaults();
    }
    let data: Value =
        match serde_json::from_str(&std::fs::read_to_string(&path).unwrap_or_default()) {
            Ok(data) => data,
            Err(why) => return closed(&why.to_string(), root),
        };
    if !data.is_object() {
        return closed("top level is not an object", root);
    }
    // a bad port entry stands at the state in force
    let claims = axis(&data, "claims", &CLAIMS_STATES, DEFAULT_CLAIMS).unwrap_or_else(|why| Axis {
        state: "clean".to_owned(),
        why: format!("the claims entry is MALFORMED ({why}) - failing closed"),
        ..Axis::default()
    });
    let port = axis(&data, "port", &PORT_STATES, DEFAULT_PORT).unwrap_or_else(|why| Axis {
        state: committed_port(root),
        why: format!("the port entry is MALFORMED ({why}) - the last committed state in force"),
        ..Axis::default()
    });
    Switches {
        error: String::new(),
        claims,
        port,
    }
}

fn who_am_i(root: &Path) -> String {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["config", "user.name"])
        .output();
    let name = done
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
        .unwrap_or_default();
    Some(name)
        .filter(|n| !n.is_empty())
        .unwrap_or("unknown".to_owned())
}

/// Set one axis, keeping the others; a malformed file is replaced here, the throw being the repair and a diff someone reads.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn write(
    root: &Path,
    name: &str,
    state: &str,
    why: &str,
    utc: &str,
) -> Result<Switches, String> {
    if why.trim().is_empty() {
        return Err("a reason is required (REASON=...) - a reason someone will READ is a decision you have to defend".to_owned());
    }
    let allowed = match name {
        "claims" => CLAIMS_STATES,
        "port" => PORT_STATES,
        _ => ["", ""],
    };
    if state.is_empty() || !allowed.contains(&state) {
        return Err(format!("unknown switch {name}={state}"));
    }
    let current = read(root);
    let mut out = if current.error.is_empty() {
        current
    } else {
        Switches::defaults()
    };
    let new = Axis {
        state: state.to_owned(),
        why: why.trim().to_owned(),
        who: who_am_i(root),
        utc: utc.to_owned(),
    };
    match name {
        "claims" => out.claims = new,
        _ => out.port = new,
    }
    let path = root.join(FILE);
    stated(std::fs::create_dir_all(root.join("dev")), FILE)?;
    let body = stated(
        serde_json::to_string_pretty(
            &json!({"claims": out.claims.json(), "port": out.port.json()}),
        )
        .map_err(std::io::Error::other),
        FILE,
    )?;
    stated(std::fs::write(path, format!("{body}\n")), FILE)?;
    Ok(out)
}

fn described(name: &str, a: &Axis, default: &str) -> String {
    if a.state == default && a.why.is_empty() {
        format!("  {name:<7} {:<10} (default)", a.state)
    } else {
        let who = if a.who.is_empty() { "?" } else { &a.who };
        format!(
            "  {name:<7} {:<10} since {} by {who}: {}",
            a.state, a.utc, a.why
        )
    }
}

#[must_use]
pub fn describe(sw: &Switches) -> String {
    let mut head = "switches (dev/switches.json):".to_owned();
    if !sw.error.is_empty() {
        let _ = write!(
            head,
            "\n  MALFORMED - {} - claims closed until a `make claims-*` or `make port-*` rewrites it",
            sw.error
        );
    }
    [
        head,
        described("claims", &sw.claims, DEFAULT_CLAIMS),
        described("port", &sw.port, DEFAULT_PORT),
    ]
    .join("\n")
}

/// The process table this needs, injected so that which exit of the walk a test reaches is not decided by the machine (feature 174).
pub trait Table {
    fn parent(&self, pid: u32) -> Option<u32>;
    fn cmdline(&self, pid: u32) -> String;
}

pub struct LiveTable;

impl Table for LiveTable {
    fn parent(&self, pid: u32) -> Option<u32> {
        let status = std::fs::read_to_string(format!("/proc/{pid}/status")).ok()?;
        status
            .lines()
            .find_map(|l| l.strip_prefix("PPid:"))
            .and_then(|v| v.trim().parse().ok())
    }

    fn cmdline(&self, pid: u32) -> String {
        let raw = std::fs::read(format!("/proc/{pid}/cmdline")).unwrap_or_default();
        String::from_utf8_lossy(&raw).replace('\0', " ")
    }
}

fn ancestors(pid: u32, table: &dyn Table) -> Vec<u32> {
    let (mut out, mut at) = (Vec::new(), pid);
    while at > 1 && out.len() < 64 {
        match table.parent(at) {
            Some(parent) if parent > 0 => {
                out.push(parent);
                at = parent;
            }
            _ => break,
        }
    }
    out
}

/// Does this process descend from the idle timer that wrote `.git/idle-tests.running`? The Makefile's `DONE_NAME` picks `idle-done` from it, the mechanism by which an unattended gate neither grants nor revokes a push.
pub fn idle_context(top: &Path, pid: u32, table: &dyn Table) -> bool {
    let Some(timer) = std::fs::read_to_string(top.join(".git/idle-tests.running"))
        .ok()
        .and_then(|t| t.trim().parse::<u32>().ok())
    else {
        return false;
    };
    let line = table.cmdline(timer);
    ancestors(pid, table).contains(&timer)
        && line.contains(IDLE_TIMER_MARK)
        && line.contains(" timer ")
}

/// `l7r-gate switches show | state AXIS | idle | set AXIS STATE --why W`.
pub fn cli(args: &[String], root: &Path, utc: &str) -> crate::Reply {
    let say = |stdout: String, stderr: String, code: i32| crate::Reply {
        stdout,
        stderr,
        code,
    };
    let words: Vec<&str> = args.iter().map(String::as_str).collect();
    match words.as_slice() {
        ["show"] => say(format!("{}\n", describe(&read(root))), String::new(), 0),
        ["state", "claims"] => say(format!("{}\n", read(root).claims.state), String::new(), 0),
        ["state", "port"] => say(format!("{}\n", read(root).port.state), String::new(), 0),
        ["idle"] => say(
            format!(
                "{}\n",
                u8::from(idle_context(root, std::process::id(), &LiveTable))
            ),
            String::new(),
            0,
        ),
        ["set", name, state, "--why", why] => match write(root, name, state, why, utc) {
            Ok(sw) => say(format!("{}\n", describe(&sw)), String::new(), 0),
            Err(why) => say(String::new(), format!("switches: REFUSED - {why}\n"), 1),
        },
        _ => say(
            String::new(),
            "usage: l7r-gate switches show | state AXIS | idle | set AXIS STATE --why W\n"
                .to_owned(),
            2,
        ),
    }
}

fn utc_of(secs: u64) -> String {
    let (y, mo, d, h, mi, s) = l7r_guard::shared::log::civil(secs);
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
}

/// `l7r-gate switches ...`, refused outside this project's make.
pub fn guarded(args: &[String], root: &Path, procs: &dyn super::via_make::Procs) -> crate::Reply {
    let tree = crate::codeid::script(root);
    if let Some(text) = super::via_make::refusal(
        procs,
        tree.ancestors().nth(3).unwrap_or(root),
        "l7r.diagram.switches",
        "switches",
    ) {
        return crate::Reply {
            stdout: String::new(),
            stderr: text,
            code: 2,
        };
    }
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    cli(args, root, &utc_of(secs))
}

#[cfg(test)]
mod tests;
