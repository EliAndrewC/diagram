//! A STOP BLOCK SAID ONCE (feature 451 T171; the GM 2026-11-23, on hook output length: "That amount of output consumes tokens, so
//! could we accomplish the same thing with no loss of fidelity and fewer tokens?"). A Stop guard's refusal is said in full the first
//! time, its fix command and escape with it; while its text is unchanged, a repeat is one line, `still: <its first 8 words> - unchanged
//! since HH:MM` (UTC, the time it was said in full), and it is still a refusal. A changed text is said in full again, and so is a block
//! that returns after a Stop that passed without it: a block back hours later, past a compaction, must carry its command again.
//!
//! Each guard's last full block is kept by the SHA-256 of its text in one file a session, `<git dir>/l7r-said/<session id>.json`, so
//! a fixture clone holds its own and sessions sharing a clone never read each other's. A payload with no session id keeps nothing and
//! says every block in full. A file that cannot be read or written says the block in full: the summary saves words, never a refusal.
//!
//! Measured 2026-11-23 on a replay of the coordinator's Stops since 2026-11-22 00:00 UTC (its transcript's `stop_hook_summary`
//! records against the event log's 422 Stop lines): 28 of set-down's 69 blocks repeated the block said before them, unchanged.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

/// How many of a block's words its one-line summary repeats (the GM's form, through the coordinator's brief of 2026-11-23).
const WORDS: usize = 8;

/// The session's file, `<git dir>/l7r-said/<session id>.json`, its directory made; None for a payload with no session id.
#[must_use]
pub fn file(git_dir: &Path, input: &Value) -> Option<PathBuf> {
    if crate::state::field(input, "session_id").is_empty() {
        return None;
    }
    let dir = git_dir.join("l7r-said").to_string_lossy().into_owned();
    Some(crate::state::session_file(input, Some(dir), "", "json"))
}

fn record(file: &Path) -> serde_json::Map<String, Value> {
    std::fs::read_to_string(file)
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .and_then(|v| v.as_object().cloned())
        .unwrap_or_default()
}

/// The words to say for `guard`'s block `text` at `now` (seconds past the epoch): `text` itself, recorded, unless the block recorded
/// for `guard` is this one, when its one-line summary.
#[must_use]
pub fn say(file: Option<&Path>, guard: &str, text: &str, now: i64) -> String {
    let Some(file) = file else {
        return text.to_owned();
    };
    let hash = crate::sha256::hex(text.as_bytes());
    let mut kept = record(file);
    if let Some(since) = kept
        .get(guard)
        .filter(|k| k.get("hash").and_then(Value::as_str) == Some(hash.as_str()))
        .and_then(|k| k.get("since").and_then(Value::as_i64))
    {
        let head: Vec<&str> = text.split_whitespace().take(WORDS).collect();
        let day = since.rem_euclid(86_400);
        return format!(
            "still: {} - unchanged since {:02}:{:02}",
            head.join(" "),
            day / 3600,
            day % 3600 / 60
        );
    }
    kept.insert(guard.to_owned(), json!({"hash": hash, "since": now}));
    let _ = std::fs::write(file, Value::Object(kept).to_string());
    text.to_owned()
}

/// The `SessionStart` sources after which the context may no longer hold a block said in full (Claude Code's `source`: `compact` after
/// a compaction, `clear` after `/clear`, `resume` on a resumed session); `startup` is a new session id, whose record is empty already.
const FORGETS: [&str; 3] = ["compact", "clear", "resume"];

/// A COMPACTION FORGETS WHAT WAS SAID (451 T171): a `SessionStart` of `source` in [`FORGETS`] removes the session's record, so the next
/// Stop says each block in full, its fix command with it. WHY: a repeat shown only as its `still:` line after a compaction had lost
/// the command the full block carried (the GM 2026-11-23, 451's request.md: "no loss of fidelity").
pub fn forget(file: Option<&Path>, source: &str) {
    if let Some(file) = file.filter(|_| FORGETS.contains(&source)) {
        let _ = std::fs::remove_file(file);
    }
}

/// A Stop that passed without `guard`'s block: its record dropped, so the block's return is said in full.
pub fn clear(file: Option<&Path>, guard: &str) {
    let Some(file) = file else {
        return;
    };
    let mut kept = record(file);
    if kept.remove(guard).is_some() {
        let _ = std::fs::write(file, Value::Object(kept).to_string());
    }
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::{clear, file, forget, say};

    const BLOCK: &str = "BLOCKED: a builder slot is free - 2 of 3 builders running (449 T341) - start the next: make task-start F=451 T=T90";

    #[test]
    fn a_block_is_said_once_then_summarized_until_it_changes_or_a_stop_passes_without_it() {
        let d = crate::tempdir::TempDir::new("guard-once");
        let f = file(&d, &json!({"session_id": "s/1"})).unwrap();
        assert_eq!(f, d.join("l7r-said/s_1.json"));
        // 05:45 UTC on 2026-11-23
        let at = 1_795_412_700;
        assert_eq!(say(Some(&f), "set-down", BLOCK, at), BLOCK);
        let again = say(Some(&f), "set-down", BLOCK, at + 600);
        assert_eq!(
            again,
            "still: BLOCKED: a builder slot is free - 2 - unchanged since 05:45"
        );
        // another guard's block is its own
        assert_eq!(say(Some(&f), "finished-run", "A RUN", at), "A RUN");
        assert!(say(Some(&f), "finished-run", "A RUN", at).starts_with("still: A RUN - "));
        // a changed block is said in full, and is the one kept
        let changed = BLOCK.replace("2 of 3", "1 of 3");
        assert_eq!(say(Some(&f), "set-down", &changed, at + 900), changed);
        assert!(say(Some(&f), "set-down", &changed, at + 960).ends_with("since 06:00"));
        // a Stop without the block: its return is said in full; clearing what is not kept keeps the rest
        clear(Some(&f), "set-down");
        clear(Some(&f), "set-down");
        assert_eq!(say(Some(&f), "set-down", &changed, at), changed);
        assert!(say(Some(&f), "finished-run", "A RUN", at).starts_with("still: "));
    }

    #[test]
    fn a_compaction_clear_or_resume_forgets_the_record_and_a_startup_keeps_it() {
        let d = crate::tempdir::TempDir::new("guard-once-forget");
        let f = file(&d, &json!({"session_id": "s1"})).unwrap();
        for source in ["compact", "clear", "resume"] {
            assert_eq!(say(Some(&f), "set-down", BLOCK, 0), BLOCK);
            forget(Some(&f), "startup");
            forget(Some(&f), "");
            assert!(say(Some(&f), "set-down", BLOCK, 0).starts_with("still: "));
            forget(Some(&f), source);
            assert!(!f.exists(), "{source}");
        }
        // nothing kept, or no session: nothing to forget
        forget(Some(&f), "compact");
        forget(None, "compact");
        assert_eq!(say(Some(&f), "set-down", BLOCK, 0), BLOCK);
    }

    #[test]
    fn no_session_or_an_unreadable_record_says_the_block_in_full() {
        let d = crate::tempdir::TempDir::new("guard-once-none");
        assert_eq!(file(&d, &json!({})), None);
        assert_eq!(say(None, "set-down", BLOCK, 0), BLOCK);
        assert_eq!(say(None, "set-down", BLOCK, 0), BLOCK);
        clear(None, "set-down");
        // a record that is not an object, or a directory where the file would be, keeps nothing
        let f = d.join("said.json");
        std::fs::write(&f, "[1]").unwrap();
        assert_eq!(say(Some(&f), "set-down", BLOCK, 0), BLOCK);
        let dir = d.join("a-directory");
        std::fs::create_dir_all(&dir).unwrap();
        assert_eq!(say(Some(&dir), "set-down", BLOCK, 0), BLOCK);
        assert_eq!(say(Some(&dir), "set-down", BLOCK, 0), BLOCK);
    }
}
