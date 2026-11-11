//! A claims check IN FLIGHT, seen rather than inferred (`scripts/record/claims_flight.py`, ported by feature 449 T82; feature 426 D1):
//! `make claims-bundle` and `make claims-triage` mark their bundle, `make claims-checked` and `make claims-triaged` clear it, and
//! `make land` waits for a claims round only while a live mark stands.

use std::path::{Component, Path, PathBuf};

use l7r_guard::shared::pyjson::py_float;
use l7r_guard::shared::sha256;
use serde_json::Value;

use crate::record::repo::{fail, Fail};

/// A mark older than this is stale: the landing's own claims wait, past which it would have stopped waiting anyway.
pub const MAX_AGE_S: f64 = 1200.0;

/// `Path(p).resolve()`: absolute, every symlink of the part that exists resolved, the rest appended.
pub fn resolved(p: &Path) -> PathBuf {
    let mut clean = PathBuf::new();
    for c in std::path::absolute(p).unwrap_or_default().components() {
        if c == Component::ParentDir {
            clean.pop();
        } else {
            clean.push(c);
        }
    }
    let found = clean.ancestors().find_map(|anc| {
        let real = std::fs::canonicalize(anc).ok()?;
        let rest = clean.strip_prefix(anc).unwrap_or(anc);
        Some(if rest.as_os_str().is_empty() {
            real
        } else {
            real.join(rest)
        })
    });
    found.unwrap_or(clean)
}

fn dir(root: &Path) -> PathBuf {
    let out = std::process::Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["rev-parse", "--git-common-dir"])
        .output();
    let common = out
        .ok()
        .filter(|o| o.status.success())
        .map(|o| l7r_guard::shared::py_text::strip(&String::from_utf8_lossy(&o.stdout)).to_owned())
        .filter(|s| !s.is_empty())
        .map_or_else(|| root.join(".git"), PathBuf::from);
    let common = if common.is_absolute() {
        common
    } else {
        root.join(common)
    };
    common.join("claims-in-flight")
}

fn name(bundle: &Path) -> String {
    format!(
        "{}.json",
        &sha256::hex(resolved(bundle).to_string_lossy().as_bytes())[..16]
    )
}

/// The time now, as `time.time()`.
pub fn now() -> f64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0.0, |d| d.as_secs_f64())
}

/// `bundle` is in flight: built, its check about to be dispatched.
pub fn mark(root: &Path, bundle: &Path) -> Result<(), Fail> {
    let d = dir(root);
    std::fs::create_dir_all(&d).map_err(fail)?;
    let text = format!(
        "{{\"bundle\": {}, \"at\": {}}}",
        l7r_guard::shared::pyjson::ascii_string(&resolved(bundle).to_string_lossy(), true),
        py_float(now())
    );
    std::fs::write(d.join(name(bundle)), text).map_err(fail)
}

/// `bundle`'s reply is recorded: no longer in flight.
pub fn clear(root: &Path, bundle: &Path) {
    let _ = std::fs::remove_file(dir(root).join(name(bundle)));
}

/// `float(v)` of a JSON value, 0 where it is absent: the failure Python's `float` raises on what it cannot read.
fn float(v: Option<&Value>) -> Result<f64, Fail> {
    match v {
        None => Ok(0.0),
        Some(Value::Number(n)) => Ok(n.as_f64().unwrap_or(0.0)),
        Some(Value::Bool(b)) => Ok(f64::from(u8::from(*b))),
        Some(Value::String(s)) => l7r_guard::shared::py_text::strip(s)
            .parse()
            .map_err(|_| format!("ValueError: could not convert string to float: {s:?}")),
        Some(other) => Err(format!(
            "TypeError: float() argument must be a string or a real number, not {other}"
        )),
    }
}

/// The bundles in flight at `now`: marked within [`MAX_AGE_S`] and not cleared.
pub fn live(root: &Path, now: f64) -> Result<Vec<String>, Fail> {
    let d = dir(root);
    let mut files: Vec<PathBuf> = std::fs::read_dir(&d)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| p.extension().is_some_and(|e| e == "json"))
        .collect();
    files.sort();
    let mut out = Vec::new();
    for f in files {
        let Ok(rec) = std::fs::read_to_string(&f).map(|t| serde_json::from_str::<Value>(&t)) else {
            continue;
        };
        let Ok(rec) = rec else { continue };
        let at = float(rec.as_object().ok_or("AttributeError: 'get'")?.get("at"))?;
        if now - at <= MAX_AGE_S {
            let fallback = f
                .file_name()
                .unwrap_or_default()
                .to_string_lossy()
                .into_owned();
            out.push(
                rec.get("bundle")
                    .map_or(fallback, crate::record::bundle::py_str),
            );
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
