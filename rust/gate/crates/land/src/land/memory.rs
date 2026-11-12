//! How many workers the landing cohort gets beside a running gate: the processors and the memory the gate leaves (405 T48, T72).

use std::path::Path;
use std::sync::LazyLock;
use std::time::SystemTime;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::{split, strip};

use super::Land;

/// What the gate holds at its peak, kept free for it when the cohort's workers are sized (3.1 GB on six workers, measured 2026-10-04,
/// rounded up), and the Makefile's own per-roll allowance for a cohort worker (`make cohort` JOBS=).
const GATE_RESERVE_MB: i64 = 3500;
const ROLL_MB: i64 = 500;
const GATE_WORKERS: i64 = 6;
/// A memory-watch notice this recent still describes the machine (the watch writes one only when the containers near their cap).
const MEMWATCH_FRESH_S: f64 = 900.0;
static SHARED: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"working set is ([\d.]+) of their shared ([\d.]+) GB")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// `os.cpu_count()`: the processors online, from the kernel's list (`0-11`, `0,2-5`), or None where it cannot be read.
pub(super) fn cpus_online(path: &Path) -> Option<i64> {
    let text = std::fs::read_to_string(path).ok()?;
    let mut n = 0;
    for part in strip(&text).split(',') {
        let (lo, hi) = part.split_once('-').unwrap_or((part, part));
        let (lo, hi): (i64, i64) = (lo.parse().ok()?, hi.parse().ok()?);
        n += hi - lo + 1;
    }
    Some(n)
}

/// Python's `int(text)`: surrounding whitespace allowed, and underscores between digits.
fn py_int(text: &str) -> Result<i64, String> {
    let t = strip(text);
    let digits = t.strip_prefix(['+', '-']).unwrap_or(t);
    let ok = !digits.is_empty()
        && !digits.starts_with('_')
        && !digits.ends_with('_')
        && !digits.contains("__")
        && digits.chars().all(|c| c.is_ascii_digit() || c == '_');
    if !ok {
        return Err(format!(
            "ValueError: invalid literal for int() with base 10: {text:?}"
        ));
    }
    t.replace('_', "")
        .parse()
        .map_err(|e| format!("ValueError: {e}"))
}

/// The second field of a line (`ln.split()[1]`), Python's `IndexError` where it has none.
fn second(line: &str) -> Result<&str, String> {
    split(line)
        .get(1)
        .copied()
        .ok_or_else(|| "IndexError: list index out of range".to_owned())
}

/// The containers' shared cap less their working set, MB, from the memory watch's newest notice when it is `MEMWATCH_FRESH_S` old or
/// less; None when there is none (no watch, no recent notice, no figure in it). On 2026-10-26 at 12:59 a landing's cohort, sized at 6
/// workers from the 6.5 GB its own container showed free, took the shared 10 GB cap to its limit, and memguard killed another session's
/// 1.4 GB process. ...THE NEWEST RECENT NOTICE THAT CARRIES THE FIGURE: a memguard kill notice carries none, and the first form read only
/// the newest notice - after the kills of 2026-10-26 13:49-13:51 it found no figure and sized the next landing's cohort at 4 workers.
pub(super) fn shared_free_mb(mw: &Path, now: f64) -> Result<Option<i64>, String> {
    // an unreadable or undecodable file is `except OSError, ValueError: return None` (a decode error is a `ValueError`); an empty one
    // is the `IndexError` the Python let through
    let Some(text) = std::fs::read(mw.join("latest"))
        .ok()
        .and_then(|b| String::from_utf8(b).ok())
    else {
        return Ok(None);
    };
    let first = split(&text)
        .first()
        .copied()
        .ok_or_else(|| "IndexError: list index out of range".to_owned())?;
    let Ok(latest) = py_int(first) else {
        return Ok(None);
    };
    let mut notices: Vec<(i64, std::path::PathBuf)> = std::fs::read_dir(mw.join("events"))
        .into_iter()
        .flatten()
        .flatten()
        .filter_map(|e| {
            let path = e.path();
            let name = e.file_name().to_string_lossy().into_owned();
            let stem = name.strip_suffix(".txt")?;
            let n = (!stem.is_empty() && stem.chars().all(|c| c.is_ascii_digit()))
                .then(|| stem.parse::<i64>().ok())
                .flatten()?;
            (n <= latest).then_some((n, path))
        })
        .collect();
    notices.sort_by(|a, b| b.cmp(a));
    for (_seq, path) in notices {
        let Ok(meta) = std::fs::metadata(&path) else {
            continue;
        };
        let mtime = meta
            .modified()
            .ok()
            .and_then(|t| t.duration_since(SystemTime::UNIX_EPOCH).ok())
            .map_or(0.0, |d| d.as_secs_f64());
        if now - mtime > MEMWATCH_FRESH_S {
            return Ok(None); // older notices are older still
        }
        let Ok(bytes) = std::fs::read(&path) else {
            continue;
        };
        let body = String::from_utf8_lossy(&bytes);
        if let Some(m) = SHARED.captures(&body).ok().flatten() {
            let float = |s: &str| {
                s.parse::<f64>()
                    .map_err(|_| format!("ValueError: could not convert string to float: '{s}'"))
            };
            let free = (float(&m[2])? - float(&m[1])?) * 1024.0;
            #[expect(
                clippy::cast_possible_truncation,
                reason = "Python's int() of a float: toward zero, a memory figure far inside i64"
            )]
            return Ok(Some(free.trunc() as i64));
        }
    }
    Ok(None)
}

impl Land {
    /// The memory free to this container, MB: the host's `MemAvailable`, and - where the container has a cgroup v2 limit - no more than
    /// that limit less what the cgroup holds, its reclaimable file cache given back (405 T72: sized from the host's 9.5 GB alone, the
    /// batch-3 landing's 12 workers took the containers' shared 10 GB cap to 9.0 GB); and no more than the containers' SHARED cap
    /// leaves, when the watch has just said so.
    pub(super) fn memory_free_mb(&self) -> Result<i64, String> {
        // `except OSError, StopIteration, ValueError`: no file, no line, no number (or bytes that are no text) is the fallback; a line
        // with no second field is the `IndexError` the Python let through
        let fallback = GATE_RESERVE_MB + 4 * ROLL_MB;
        let text = std::fs::read(&self.meminfo)
            .ok()
            .and_then(|b| String::from_utf8(b).ok());
        let mut avail = match text
            .as_deref()
            .and_then(|t| t.lines().find(|l| l.starts_with("MemAvailable:")))
        {
            Some(line) => py_int(second(line)?).map_or(fallback, |kb| kb.div_euclid(1024)),
            None => fallback,
        };
        if let Some(cap) = self.cgroup_free()? {
            avail = avail.min(cap);
        }
        let now = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .map_or(0.0, |d| d.as_secs_f64());
        Ok(match shared_free_mb(&self.memwatch, now)? {
            Some(shared) => avail.min(shared),
            None => avail,
        })
    }

    /// The cgroup's limit less what it holds, its inactive file cache given back, MB; None with no limit or one that cannot be read.
    fn cgroup_free(&self) -> Result<Option<i64>, String> {
        // `except OSError, ValueError: pass`: an unreadable file, undecodable bytes or no number leave the figure as it was
        let read = |name: &str| {
            std::fs::read(self.cgroup.join(name))
                .ok()
                .and_then(|b| String::from_utf8(b).ok())
        };
        let Some(cap) = read("memory.max") else {
            return Ok(None);
        };
        let cap = strip(&cap);
        if cap == "max" {
            return Ok(None);
        }
        let Some(current) = read("memory.current") else {
            return Ok(None);
        };
        let Ok(held) = py_int(&current) else {
            return Ok(None);
        };
        let Some(stat) = read("memory.stat") else {
            return Ok(None);
        };
        let cache = match stat.lines().find(|l| l.starts_with("inactive_file ")) {
            Some(line) => match py_int(second(line)?) {
                Ok(n) => n,
                Err(_) => return Ok(None),
            },
            None => 0,
        };
        let Ok(cap) = py_int(cap) else {
            return Ok(None);
        };
        Ok(Some((cap - held + cache).div_euclid(1024 * 1024)))
    }

    /// The cohort's workers beside a running gate - the processors the gate leaves and the memory it leaves, at least 2 - and the memory
    /// (MB) they were sized from.
    pub(super) fn cohort_jobs(&self) -> Result<(i64, i64), String> {
        let avail = self.memory_free_mb()?;
        let cpus = self.cpus.unwrap_or(4) - 2 - GATE_WORKERS;
        let by_memory = (avail - GATE_RESERVE_MB).div_euclid(ROLL_MB);
        Ok((cpus.min(by_memory).max(2), avail))
    }
}

#[cfg(test)]
mod tests;
