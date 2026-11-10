//! The work-budget check's round cap (from `hm_budget_rounds.py`; the round arbiter's tooling fix on ask:444-T02-field-round-15): a stage's rounds are its recorded `MODE BUDGET` verdicts.

use std::path::Path;
use std::sync::LazyLock;
use std::time::UNIX_EPOCH;

use fancy_regex::Regex;
use serde_json::{Map, Value};

use super::arbiter::epoch_iso;
use super::{name_of, text};

const ROUND_CAP: usize = 2;

static STAGE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"/work-budget-budget-([a-z_]+)/MANIFEST\.md")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "the `<stage>.verdict-<N>.txt` the tool writes"
)]
fn verdicts(dir: &Path, stage: &str) -> Vec<std::path::PathBuf> {
    let prefix = format!("{stage}.verdict-");
    let mut out: Vec<std::path::PathBuf> = std::fs::read_dir(dir.join("phases"))
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| {
            let n = e.file_name().to_string_lossy().into_owned();
            n.starts_with(&prefix) && n.ends_with(".txt")
        })
        .map(|e| e.path())
        .collect();
    out.sort();
    out
}

fn mtime(path: &Path) -> f64 {
    std::fs::metadata(path)
        .and_then(|m| m.modified())
        .ok()
        .and_then(|t| t.duration_since(UNIX_EPOCH).ok())
        .map_or(0.0, |d| d.as_secs_f64())
}

/// "" when a `work-budget` dispatch may go, else why not.
#[must_use]
pub fn refusal(feature_dir: Option<&Path>, rulings: &Map<String, Value>, prompt: &str) -> String {
    let Ok(Some(caps)) = STAGE.captures(prompt) else {
        return String::new();
    };
    let Some(dir) = feature_dir else {
        return String::new();
    };
    let stage = caps[1].to_owned();
    let found = verdicts(dir, &stage);
    let last = found.iter().map(|p| mtime(p)).fold(0.0_f64, f64::max);
    let named = Regex::new(&format!(
        r"(?<![a-z_]){}(?![a-z_])",
        fancy_regex::escape(&stage)
    ))
    .unwrap_or_else(|e| unreachable!("{e}"));
    let mut about: Vec<(f64, &String, &Value)> = rulings
        .iter()
        .filter(|(t, _)| named.is_match(t).unwrap_or(false))
        .map(|(t, r)| (epoch_iso(text(r, "utc")), t, r))
        .collect();
    about.sort_by(|a, b| a.0.total_cmp(&b.0));
    let since: Vec<&(f64, &String, &Value)> = about.iter().filter(|x| x.0 > last).collect();
    if let Some(latest) = since.last().filter(|x| text(x.2, "ruling") == "accept") {
        return format!(
            "the round arbiter accepted {stage}'s derivation ({}) after its last verdict - no further work-budget round runs on it; an edit to a Total or a Bounds figure re-owes a ruling: make arbiter-ask SUBJECT=<id> WHY=\"<what changed>\"",
            latest.1
        );
    }
    if found.len() >= ROUND_CAP && !since.iter().any(|x| text(x.2, "ruling") == "continue") {
        let n = found.len() + 1;
        return format!(
            "round {n} of work-budget on {stage} passes its cap of {ROUND_CAP} with no arbiter continue since {} - bring it to the round arbiter first: make arbiter-ask SUBJECT=<feature>-{stage}-round-{n} WHY=\"<the verdicts and what changed>\" FILES=\"<the verdict files>\"",
            name_of(&found[found.len() - 1])
        );
    }
    String::new()
}

#[cfg(test)]
mod tests;
