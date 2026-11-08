//! Keep a clone's untracked `.claude/settings.local.json` excluding the MIRROR's root CLAUDE.md (feature 250; ported from `clone_local_settings.py`, feature 449 T051). Every clone lives
//! inside the mirror, so a session working in one loads the root CLAUDE.md twice. Measured on a probe, 2026-09-26: excluding the mirror's copy took a session's first turn from
//! 28,590 tokens to 21,267, and every turn carries it. Only in a clone; other keys are kept; a file that is not JSON is left alone and reported, never overwritten.

use std::path::{Path, PathBuf};

use serde_json::{Map, Value};

const KEY: &str = "claudeMdExcludes";

fn mirror_claude_md(clone: &Path) -> Option<String> {
    let real = clone.canonicalize().unwrap_or_else(|_| clone.to_path_buf());
    let parts: Vec<_> = real.components().collect();
    let at = parts.iter().position(|c| c.as_os_str() == ".clones")?;
    let mirror: PathBuf = parts[..at].iter().collect();
    Some(mirror.join("CLAUDE.md").to_string_lossy().into_owned())
}

/// What was done, as one line - empty when nothing needed doing.
pub(crate) fn ensure(clone: &Path) -> String {
    let Some(target) = mirror_claude_md(clone) else {
        return String::new();
    };
    let path = clone.join(".claude/settings.local.json");
    let mut data = Map::new();
    if path.is_file() {
        let text = std::fs::read_to_string(&path).unwrap_or_default();
        let parsed =
            serde_json::from_str::<Map<String, Value>>(if text.is_empty() { "{}" } else { &text });
        let Ok(read) = parsed else {
            return format!("clone-settings: {} is not JSON - left alone; add \"{KEY}\": [\"{target}\"] by hand", path.display());
        };
        data = read;
    }
    let mut excludes = data
        .get(KEY)
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_default();
    if excludes.iter().any(|v| v == target.as_str()) {
        return String::new();
    }
    excludes.push(Value::from(target.clone()));
    data.insert(KEY.to_owned(), Value::Array(excludes));
    let _ = path.parent().map(std::fs::create_dir_all);
    let text = serde_json::to_string_pretty(&data).unwrap_or_default();
    let _ = std::fs::write(&path, format!("{text}\n"));
    format!("clone-settings: {} now excludes the mirror's {target}, which every session in this clone loaded beside the clone's own copy (about 7,000 tokens a turn) - it takes effect at the next session start", path.display())
}

#[cfg(test)]
mod tests;
