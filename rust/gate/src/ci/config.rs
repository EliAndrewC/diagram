//! The constants and the secrets: the only module that knows the AWS account's names (from `ci/config.py`). `RATE_PER_MIN` is mirrored in exactly one other place, the `gm-assistant-ci-monthly-alert` Lambda's environment
//! variable; change both together. The history of each figure is in the git history of `config.py` and in `dev/ci.md`.

use std::collections::HashMap;
use std::path::{Path, PathBuf};

pub(crate) const RATE_PER_MIN: f64 = 0.02;
pub(crate) const COMPUTE_TYPE: &str = "BUILD_GENERAL1_LARGE";
pub(crate) const PROJECT_MERGE: &str = "gm-assistant-merge";
pub(crate) const PROJECT_CHECK: &str = "gm-assistant-check";
pub(crate) const GITHUB_REPO: &str = "EliAndrewC/diagram";
pub(crate) const MAILBOX_PREFIX: &str = "session/";
/// A parked build aborts itself after this long with no go signal: the most a dead dispatcher can cost (FR-036).
pub(crate) const PARK_TIMEOUT_S: u32 = 120;
/// The log is streamed by polling inside one process the session backgrounded (R5).
pub(crate) const STREAM_POLL_S: u64 = 10;

/// Per-minute rates by compute type (us-east-1 Linux on-demand, 2026-08), for `make ci-check COMPUTE=`.
pub(crate) const RATES: [(&str, f64); 4] = [
    ("BUILD_GENERAL1_XLARGE", 0.08),
    ("BUILD_GENERAL1_2XLARGE", 0.20),
    ("BUILD_GENERAL1_LARGE", 0.02),
    ("BUILD_GENERAL1_MEDIUM", 0.01),
];

pub(crate) fn rate_of(compute: &str) -> f64 {
    RATES
        .iter()
        .find(|(name, _)| *name == compute)
        .map_or(RATE_PER_MIN, |(_, r)| *r)
}

/// Estimates printed before a dispatch (FR-014). `reference` is measured; `full` and `operation` are placeholders never calibrated (`dev/run-log/20260904T001453005229-3306563.json`).
pub(crate) fn estimate_minutes(kind: &str) -> f64 {
    match kind {
        "full" => 8.0,
        _ => 10.0,
    }
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub(crate) struct Secrets {
    pub region: String,
    pub access_key_id: String,
    pub secret_access_key: String,
    pub ci_bucket: String,
    pub ecr_image: String,
    pub log_group: String,
    pub github_pat: String,
}

fn candidates(root: &Path) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = std::env::var_os("DIAGRAM_SECRETS")
        .filter(|e| !e.is_empty())
        .map(PathBuf::from)
        .into_iter()
        .collect();
    out.push(root.join("development-secrets.ini"));
    if root
        .parent()
        .and_then(Path::file_name)
        .is_some_and(|n| n == ".clones")
    {
        out.extend(
            root.parent()
                .and_then(Path::parent)
                .map(|main| main.join("development-secrets.ini")),
        );
    }
    out.push(PathBuf::from(
        "/host-l7r-repo/gm-assistant/webapp/development-secrets.ini",
    ));
    out
}

/// `section -> key -> value`, as `configparser` reads this file: `key = value` or `key: value`, a `#` or `;` line a comment.
fn ini(text: &str) -> HashMap<String, HashMap<String, String>> {
    let mut sections: HashMap<String, HashMap<String, String>> = HashMap::new();
    let mut current = String::new();
    for raw in text.lines() {
        let line = raw.trim();
        if line.is_empty() || line.starts_with('#') || line.starts_with(';') {
            continue;
        }
        if let Some(name) = line.strip_prefix('[').and_then(|l| l.strip_suffix(']')) {
            name.clone_into(&mut current);
        } else if let Some((key, value)) = line.split_once(['=', ':']) {
            sections
                .entry(current.clone())
                .or_default()
                .insert(key.trim().to_lowercase(), value.trim().to_owned());
        }
    }
    sections
}

/// The first readable candidate wins; a missing file is an error naming every place looked.
pub(crate) fn load_secrets(root: &Path) -> Result<Secrets, String> {
    let places = candidates(root);
    let Some(text) = places.iter().find_map(|p| std::fs::read_to_string(p).ok()) else {
        let looked: Vec<String> = places.iter().map(|p| p.display().to_string()).collect();
        return Err(format!("no development-secrets.ini found; looked in:\n  {}\n(copy development-secrets.ini.example at the repository root and fill the [aws] and [github] keys)", looked.join("\n  ")));
    };
    let parsed = ini(&text);
    let of = |section: &str, key: &str, default: &str| {
        parsed
            .get(section)
            .and_then(|s| s.get(key))
            .map_or(default, String::as_str)
            .to_owned()
    };
    Ok(Secrets {
        region: of("aws", "region", "us-east-1"),
        access_key_id: of("aws", "access_key_id", ""),
        secret_access_key: of("aws", "secret_access_key", ""),
        ci_bucket: of("aws", "ci_bucket", ""),
        ecr_image: of("aws", "ecr_image", ""),
        log_group: of("aws", "log_group", "/aws/codebuild/gm-assistant"),
        github_pat: of("github", "codebuild_pat", ""),
    })
}

/// `l7r-gate github-token`: the push's credential, from the same file; a tree with no secrets answers nothing, and the push then reports its own failure.
pub(crate) fn github_token(root: &Path) -> crate::Reply {
    match load_secrets(root) {
        Ok(s) => crate::Reply {
            stdout: format!("{}\n", s.github_pat),
            stderr: String::new(),
            code: 0,
        },
        Err(why) => crate::Reply {
            stdout: String::new(),
            stderr: format!("{why}\n"),
            code: 1,
        },
    }
}

#[cfg(test)]
mod tests;
