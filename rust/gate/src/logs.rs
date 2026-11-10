//! The small records the gate's shell writes (feature 449 T069, from the inline Python of the Makefile's `LOGRUN` and `LOGBYPASS`, the three push
//! gates' bypass heredocs and `land-tooling.sh`): a run, a bypass, a landing's line, and the two reads the shell's branches take.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{SystemTime, UNIX_EPOCH};

use l7r_guard::shared::log::civil;
use l7r_guard::shared::sha256;
use serde_json::{json, Map, Value};

use crate::cohort::git;
use crate::Reply;

/// Two records written by one process in one second never share a name.
static SERIAL: AtomicU64 = AtomicU64::new(0);

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// The moment a record is stamped with.
struct Now {
    secs: u64,
    micros: u32,
}

impl Now {
    fn read() -> Self {
        let since = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default();
        Self {
            secs: since.as_secs(),
            micros: since.subsec_micros(),
        }
    }

    fn utc(&self) -> String {
        let (y, mo, d, h, mi, s) = civil(self.secs);
        format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
    }

    fn month(&self) -> String {
        let (y, mo, ..) = civil(self.secs);
        format!("{y:04}-{mo:02}")
    }

    /// `YYYYMMDDTHHMMSS`, what a record's file name opens with.
    fn compact(&self) -> String {
        let (y, mo, d, h, mi, s) = civil(self.secs);
        format!("{y:04}{mo:02}{d:02}T{h:02}{mi:02}{s:02}")
    }
}

/// A string as Python's `json.dumps` writes it: every non-ASCII character escaped.
fn ascii_string(text: &str, ascii: bool) -> String {
    let mut out = String::with_capacity(text.len() + 2);
    for c in Value::String(text.to_owned()).to_string().chars() {
        if c.is_ascii() || !ascii {
            out.push(c);
        } else {
            let mut units = [0u16; 2];
            for unit in c.encode_utf16(&mut units) {
                let _ = write!(out, "\\u{unit:04x}");
            }
        }
    }
    out
}

/// A float as Python's `repr` writes it: shortest digits, positional from 1e-4 up to 1e16, and a signed two-digit exponent outside that.
fn py_float(f: f64) -> String {
    let scientific = format!("{f:e}");
    let (mantissa, exponent) = scientific.split_once('e').unwrap_or((&scientific, "0"));
    let exponent: i32 = exponent.parse().unwrap_or(0);
    if (-4..16).contains(&exponent) {
        let plain = format!("{f}");
        return if plain.contains('.') {
            plain
        } else {
            plain + ".0"
        };
    }
    format!(
        "{mantissa}e{}{:02}",
        if exponent < 0 { '-' } else { '+' },
        exponent.abs()
    )
}

/// `value` as Python's `json.dumps(value, indent=indent)` writes it, byte for byte.
fn dumps(value: &Value, indent: Option<usize>, level: usize, out: &mut String, ascii: bool) {
    let line =
        |depth: usize| indent.map_or_else(String::new, |n| format!("\n{}", " ".repeat(n * depth)));
    let comma = if indent.is_some() { "," } else { ", " };
    match value {
        Value::Number(n) if n.is_f64() => *out += &py_float(n.as_f64().unwrap_or(0.0)),
        Value::String(s) => *out += &ascii_string(s, ascii),
        Value::Array(items) if !items.is_empty() => {
            out.push('[');
            for (i, item) in items.iter().enumerate() {
                *out += if i == 0 { "" } else { comma };
                *out += &line(level + 1);
                dumps(item, indent, level + 1, out, ascii);
            }
            *out += &line(level);
            out.push(']');
        }
        Value::Object(map) if !map.is_empty() => {
            out.push('{');
            for (i, (key, item)) in map.iter().enumerate() {
                *out += if i == 0 { "" } else { comma };
                *out += &line(level + 1);
                *out += &ascii_string(key, ascii);
                *out += ": ";
                dumps(item, indent, level + 1, out, ascii);
            }
            *out += &line(level);
            out.push('}');
        }
        other => *out += &other.to_string(),
    }
}

fn indented(value: &Value) -> String {
    let mut out = String::new();
    dumps(value, Some(2), 0, &mut out, true);
    out + "\n"
}

fn one_line(value: &Value) -> String {
    let mut out = String::new();
    dumps(value, None, 0, &mut out, true);
    out
}

/// `json.dumps(value, indent=indent, ensure_ascii=ascii)`, byte for byte.
pub(crate) fn py_dumps(value: &Value, indent: usize, ascii: bool) -> String {
    let mut out = String::new();
    dumps(value, Some(indent), 0, &mut out, ascii);
    out
}

/// One line as `json.dumps(value, ensure_ascii=False)` writes it.
pub(crate) fn one_line_utf8(value: &Value) -> String {
    let mut out = String::new();
    dumps(value, None, 0, &mut out, false);
    out
}

fn head(root: &Path) -> String {
    git(root, &["rev-parse", "--short", "HEAD"])
        .1
        .trim()
        .to_owned()
}

/// A record under `dev/<log>/<month>/`, named by its time and this process; its path.
fn write_dated(root: &Path, log: &str, now: &Now, record: &Value) -> Result<PathBuf, String> {
    let dir = root.join("dev").join(log).join(now.month());
    std::fs::create_dir_all(&dir).map_err(crate::measure::text_err)?;
    let file = dir.join(format!(
        "{}{:06}-{}.json",
        now.compact(),
        now.micros,
        std::process::id()
    ));
    std::fs::write(&file, indented(record)).map_err(crate::measure::text_err)?;
    Ok(file)
}

/// What a `make` gate run adds to its record from its environment.
pub(crate) struct RunEnv {
    pub mode: Option<String>,
    pub selected: String,
    pub stats: String,
}

impl RunEnv {
    fn read() -> Self {
        let var = |k: &str| std::env::var(k).unwrap_or_default();
        Self {
            mode: Some(var("RUN_MODE")).filter(|m| !m.is_empty()),
            selected: var("RUN_SELECTED"),
            stats: var("RUN_STATS"),
        }
    }
}

/// `log run <target> <scope> <seconds> <result> [cache]`: the record of a gate run, and the git directory's pointer to it.
fn run_record(args: &[String], env: &RunEnv, root: &Path) -> Result<(), String> {
    let [target, scope, seconds, result, rest @ ..] = args else {
        return Err(
            "usage: l7r-gate log run <target> <scope> <seconds> <result> [cache]".to_owned(),
        );
    };
    let seconds: i64 = seconds
        .parse()
        .map_err(|_| format!("log run: seconds is not a number: {seconds}"))?;
    let now = Now::read();
    let mut record = Map::new();
    let mut put = |k: &str, v: Value| {
        record.insert(k.to_owned(), v);
    };
    put("utc", json!(now.utc()));
    put("target", json!(target));
    put("scope", json!(scope));
    put("seconds", json!(seconds));
    put("result", json!(result));
    put("commit", json!(head(root)));
    if let Some(cache) = rest
        .first()
        .filter(|c| matches!(c.as_str(), "warm" | "cold"))
    {
        put("cache", json!(cache));
    }
    if let Some(mode) = &env.mode {
        put("mode", json!(mode));
        put("selected", json!(env.selected));
    }
    if let Ok(Value::Object(stats)) = serde_json::from_str(&env.stats) {
        for (k, v) in stats {
            put(&k, v);
        }
    }
    let file = write_dated(root, "run-log", &now, &Value::Object(record))?;
    let git_dir = git(root, &["rev-parse", "--absolute-git-dir"]).1;
    let whole = std::fs::canonicalize(&file).map_err(crate::measure::text_err)?;
    std::fs::write(
        Path::new(git_dir.trim()).join("last-run-record"),
        whole.display().to_string(),
    )
    .map_err(crate::measure::text_err)
}

/// `log bypass <target> <outcome> <why>`: a bypass a `make` recipe permitted, refused or saw cancelled.
fn bypass(args: &[String], root: &Path) -> Result<(), String> {
    let [target, outcome, why] = args else {
        return Err("usage: l7r-gate log bypass <target> <outcome> <why>".to_owned());
    };
    let now = Now::read();
    let record = json!({"utc": now.utc(), "target": target, "commit": head(root), "outcome": outcome, "why": why});
    write_dated(root, "bypass-log", &now, &record).map(|_| ())
}

/// `log gate-bypass <gate> <dir> <why>`: a push gate's escape, which ships with the push and which `make audit` lists.
fn gate_bypass(args: &[String], root: &Path) -> Result<(), String> {
    let [gate, dir, why] = args else {
        return Err("usage: l7r-gate log gate-bypass <gate> <dir> <why>".to_owned());
    };
    let now = Now::read();
    let seed = format!(
        "{}{}{}",
        std::process::id(),
        now.micros,
        SERIAL.fetch_add(1, Ordering::Relaxed)
    );
    let file = Path::new(dir).join(format!(
        "{}Z-{}.json",
        now.compact(),
        &sha256::hex(seed.as_bytes())[..6]
    ));
    let record = json!({"utc": now.utc(), "target": gate, "commit": head(root), "why": why});
    std::fs::write(file, indented(&record)).map_err(crate::measure::text_err)
}

/// `log land-tooling <git-dir> <files> <outcome>`: one line for a `make land-tooling`, naming the task the session had started.
fn land_tooling(args: &[String]) -> Result<(), String> {
    let [git_dir, files, outcome] = args else {
        return Err("usage: l7r-gate log land-tooling <git-dir> <files> <outcome>".to_owned());
    };
    let dir = Path::new(git_dir);
    let starts = std::fs::read_to_string(dir.join("task-starts.jsonl")).unwrap_or_default();
    let last: Value = starts
        .lines()
        .next_back()
        .and_then(|l| serde_json::from_str(l).ok())
        .unwrap_or_else(|| json!({}));
    let names: Vec<&str> = files.split_whitespace().collect();
    let line = json!({"feature": last["feature"].as_str().unwrap_or(""), "task": last["task"].as_str().unwrap_or(""), "files": names, "outcome": outcome,
        "log": dir.join("land-tooling.log").display().to_string(), "utc": Now::read().utc()});
    let path = dir.join("land-tooling.jsonl");
    let mut text = std::fs::read_to_string(&path).unwrap_or_default();
    let _ = writeln!(text, "{}", one_line(&line));
    std::fs::write(path, text).map_err(crate::measure::text_err)
}

pub(crate) fn log_cli(args: &[String], root: &Path) -> Reply {
    let rest = args.get(1..).unwrap_or(&[]);
    let done = match args.first().map(String::as_str) {
        Some("run") => run_record(rest, &RunEnv::read(), root),
        Some("bypass") => bypass(rest, root),
        Some("gate-bypass") => gate_bypass(rest, root),
        Some("land-tooling") => land_tooling(rest),
        _ => Err("usage: l7r-gate log run | bypass | gate-bypass | land-tooling ...".to_owned()),
    };
    match done {
        Ok(()) => reply(String::new(), String::new(), 0),
        Err(why) => reply(String::new(), why + "\n", 1),
    }
}

/// `json-field <file> <key>...`: each key's text on one line, `-` for an empty or missing one, so a shell `read` splits it; nothing and exit 1 when
/// the file does not read.
pub(crate) fn json_field(args: &[String]) -> Reply {
    let [file, keys @ ..] = args else {
        return reply(
            String::new(),
            "usage: l7r-gate json-field <file> <key>...\n".to_owned(),
            2,
        );
    };
    let parsed: Option<Value> = std::fs::read_to_string(file)
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok());
    let Some(value) = parsed else {
        return reply(String::new(), String::new(), 1);
    };
    let cell = |k: &String| match &value[k.as_str()] {
        Value::String(s) if !s.is_empty() => s.clone(),
        Value::Null | Value::String(_) => "-".to_owned(),
        other => other.to_string(),
    };
    reply(
        keys.iter().map(cell).collect::<Vec<_>>().join(" ") + "\n",
        String::new(),
        0,
    )
}

/// A `pyproject.toml`'s `[tool.ruff...]` sections as a `ruff.toml`, the `tool.ruff.` prefix dropped: `--config` reads that form.
pub(crate) fn ruff_toml(pyproject: &str) -> String {
    let mut out = String::new();
    let mut keep = false;
    for line in pyproject.lines() {
        let trimmed = line.trim();
        let section = trimmed
            .starts_with('[')
            .then(|| trimmed.trim_start_matches('[').trim_end_matches(']'));
        if let Some(name) = section {
            let exact = trimmed.ends_with(']')
                && !trimmed.starts_with("[[")
                && (name == "tool.ruff" || name.starts_with("tool.ruff."));
            keep = exact;
            if exact {
                out += &name
                    .strip_prefix("tool.ruff.")
                    .map_or_else(String::new, |rest| format!("[{rest}]"));
                out.push('\n');
            }
        } else if keep {
            out += line;
            out.push('\n');
        }
    }
    out
}

/// `ruff-toml`: stdin to stdout.
pub(crate) fn ruff_cli(input: &mut dyn std::io::Read) -> Reply {
    let mut text = String::new();
    let _ = input.read_to_string(&mut text);
    reply(ruff_toml(&text), String::new(), 0)
}

#[cfg(test)]
mod tests;
