//! The guard log (`scripts/hooks/lib/guardlog.sh`'s `guard_log`): one JSON file a firing, `<UTC to the microsecond>-<pid>.json` in
//! `GUARD_LOG_DIR` (else `~/.claude/guard-log`), written to a temporary beside it and renamed into place, its fields those
//! `make audit` and `make guard-log` read. A write that fails is silent: an entry must never cost the guard its answer.

use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use serde_json::{json, Value};

/// One firing: the guard, its event (`blocked`, `escaped`, `rewrote`, ...), the detail (cut at 200 characters), the rule (the event
/// where none is given), the guard's own decision inputs, the hook input and the session's name and id.
pub struct Entry<'a> {
    pub guard: &'a str,
    pub event: &'a str,
    pub detail: &'a str,
    pub rule: &'a str,
    pub context: Option<Value>,
    pub input: &'a Value,
    pub session_name: &'a str,
}

/// The log's directory: `GUARD_LOG_DIR`, else `~/.claude/guard-log`.
#[must_use]
pub fn dir() -> PathBuf {
    dir_from(
        std::env::var("GUARD_LOG_DIR").ok(),
        &std::env::var("HOME").unwrap_or_default(),
    )
}

/// The log's directory given the environment's `GUARD_LOG_DIR` and `HOME`.
fn dir_from(seam: Option<String>, home: &str) -> PathBuf {
    match seam {
        Some(d) => PathBuf::from(d),
        None => Path::new(home).join(".claude/guard-log"),
    }
}

/// The civil date and time of `secs` past the epoch, UTC: (year, month, day, hour, minute, second).
pub(crate) fn civil(secs: u64) -> (i64, u32, u32, u64, u64, u64) {
    let days = i64::try_from(secs / 86_400).unwrap_or(0);
    let rem = secs % 86_400;
    // days to a civil date (Howard Hinnant's algorithm)
    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let day_of_era = z.rem_euclid(146_097);
    let year_of_era =
        (day_of_era - day_of_era / 1460 + day_of_era / 36_524 - day_of_era / 146_096) / 365;
    let day_of_year = day_of_era - (365 * year_of_era + year_of_era / 4 - year_of_era / 100);
    let mp = (5 * day_of_year + 2) / 153;
    let d = u32::try_from(day_of_year - (153 * mp + 2) / 5 + 1).unwrap_or(1);
    let m = u32::try_from(if mp < 10 { mp + 3 } else { mp - 9 }).unwrap_or(1);
    let y = year_of_era + era * 400 + i64::from(m <= 2);
    (y, m, d, rem / 3600, rem % 3600 / 60, rem % 60)
}

/// Write `e` into `dir` at `now`; the path written, or None where the write failed.
#[must_use]
pub fn write_at(dir: &Path, e: &Entry, now: SystemTime) -> Option<PathBuf> {
    let since = now.duration_since(UNIX_EPOCH).ok()?;
    let (year, month, day, hour, min, sec) = civil(since.as_secs());
    let path = dir.join(format!(
        "{year:04}{month:02}{day:02}T{hour:02}{min:02}{sec:02}{:06}-{}.json",
        since.subsec_micros(),
        std::process::id()
    ));
    let field = |k: &str| {
        e.input
            .get(k)
            .and_then(Value::as_str)
            .unwrap_or("")
            .to_owned()
    };
    let ti = e.input.get("tool_input").cloned().unwrap_or(Value::Null);
    let command = ["command", "file_path"]
        .iter()
        .find_map(|k| ti.get(*k).and_then(Value::as_str).filter(|s| !s.is_empty()))
        .unwrap_or("");
    let session = Some(field("session_id"))
        .filter(|s| !s.is_empty())
        .unwrap_or_else(|| "unknown".to_owned());
    let name = if e.session_name.is_empty() {
        session.clone()
    } else {
        e.session_name.to_owned()
    };
    let entry = json!({
        "utc": format!("{year:04}-{month:02}-{day:02}T{hour:02}:{min:02}:{sec:02}Z"), "guard": e.guard, "event": e.event,
        "rule": if e.rule.is_empty() { e.event } else { e.rule }, "session": session, "session_name": name, "cwd": field("cwd"),
        "tool": field("tool_name"), "transcript": field("transcript_path"), "detail": e.detail.chars().take(200).collect::<String>(),
        "command": command, "context": e.context.clone().unwrap_or(Value::Null),
    });
    std::fs::create_dir_all(dir).ok()?;
    let tmp = path.with_extension("json.tmp");
    std::fs::write(&tmp, serde_json::to_string_pretty(&entry).ok()?).ok()?;
    std::fs::rename(&tmp, &path).ok()?;
    Some(path)
}

/// Write `e` into the log now (`guard_log`).
#[must_use]
pub fn write(e: &Entry) -> Option<PathBuf> {
    write_at(&dir(), e, SystemTime::now())
}

#[cfg(test)]
mod tests {
    use std::time::{Duration, UNIX_EPOCH};

    use serde_json::{json, Value};

    use super::{civil, dir_from, write, write_at, Entry};

    #[test]
    fn a_firing_is_one_file_with_todays_fields() {
        let d = std::env::temp_dir().join(format!("l7r-guard-log-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        let input = json!({"session_id": "sid", "cwd": "/c", "tool_name": "Bash", "transcript_path": "/t", "tool_input": {"command": "ls"}});
        let e = Entry {
            guard: "make-only",
            event: "blocked",
            detail: &"x".repeat(250),
            rule: "",
            context: Some(json!({"why": 1})),
            input: &input,
            session_name: "",
        };
        let at = UNIX_EPOCH + Duration::from_micros(1_794_112_496_123_456);
        let p = write_at(&d, &e, at).unwrap();
        assert!(p
            .file_name()
            .unwrap()
            .to_string_lossy()
            .starts_with("20261108T043456123456-"));
        let v: Value = serde_json::from_str(&std::fs::read_to_string(&p).unwrap()).unwrap();
        assert_eq!(v["utc"], "2026-11-08T04:34:56Z");
        assert_eq!(
            (
                v["rule"].as_str(),
                v["session_name"].as_str(),
                v["command"].as_str()
            ),
            (Some("blocked"), Some("sid"), Some("ls"))
        );
        assert_eq!(v["detail"].as_str().unwrap().len(), 200);
        let bare = json!({});
        let e2 = Entry {
            guard: "g",
            event: "escaped",
            detail: "",
            rule: "r",
            context: None,
            input: &bare,
            session_name: "named",
        };
        let v2: Value =
            serde_json::from_str(&std::fs::read_to_string(write_at(&d, &e2, at).unwrap()).unwrap())
                .unwrap();
        assert_eq!(
            (
                v2["session"].as_str(),
                v2["session_name"].as_str(),
                v2["context"].clone()
            ),
            (Some("unknown"), Some("named"), Value::Null)
        );
        std::fs::write(d.join("a-file"), "").unwrap();
        assert!(write_at(&d.join("a-file"), &e2, at).is_none());
        std::env::set_var("GUARD_LOG_DIR", &d);
        assert!(write(&e2).is_some());
        assert_eq!(civil(951_782_400), (2000, 2, 29, 0, 0, 0), "a leap day");
        assert_eq!(civil(0), (1970, 1, 1, 0, 0, 0));
        assert_eq!(
            dir_from(None, "/h"),
            std::path::Path::new("/h/.claude/guard-log")
        );
    }
}
