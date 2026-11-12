//! FR-011: the gated route needs a named, complete spec-kit feature (from `ci/features.py`). Which open box holds a landing is the guard's
//! `shared::speckit::holding`, asked in process since feature 449 T118 (`ask:449-T83-scope`: the Rust callers of `speckit-todo.py` call
//! it in process); a spec's fidelity verdict is the arbiter's `spec_verdict`.

use std::path::Path;

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct FeatureStatus {
    pub name: Option<String>,
    pub exists: bool,
    pub faithful: bool,
    pub open_tasks: Vec<String>,
}

impl FeatureStatus {
    #[must_use]
    pub fn complete(&self) -> bool {
        self.exists && self.faithful && self.open_tasks.is_empty()
    }

    #[must_use]
    pub fn why(&self) -> String {
        let Some(name) = &self.name else {
            return "no spec-kit feature is named (export SPECIFY_FEATURE=NNN-slug, or .specify/feature.json) - diagram engine work always has one".to_owned();
        };
        if !self.exists {
            return format!("feature '{name}' has no specs/{name}/ directory with a tasks.md - if it is only filed, name the feature this work belongs to: SPECIFY_FEATURE=<NNN-slug> scripts/sync-with-main.sh done");
        }
        let mut problems = Vec::new();
        if !self.faithful {
            problems.push("spec.md carries no FAITHFUL verdict (constitution XVI)".to_owned());
        }
        if !self.open_tasks.is_empty() {
            let shown = self
                .open_tasks
                .iter()
                .take(3)
                .cloned()
                .collect::<Vec<_>>()
                .join("; ");
            let more = if self.open_tasks.len() > 3 {
                format!("; +{} more", self.open_tasks.len() - 3)
            } else {
                String::new()
            };
            problems.push(format!(
                "{} open task(s) in tasks.md: {shown}{more}",
                self.open_tasks.len()
            ));
        }
        if problems.is_empty() {
            return format!("feature {name}: no task holds this landing (an open task nobody started holds none), spec FAITHFUL");
        }
        format!("feature {name}: {}", problems.join(" | "))
    }
}

/// `SPECIFY_FEATURE`, or the last part of `.specify/feature.json`'s `feature_directory`.
pub fn active_feature(root: &Path, from_env: Option<&str>) -> Option<String> {
    let named = from_env.map(str::trim).filter(|v| !v.is_empty());
    if let Some(name) = named {
        return Some(name.to_owned());
    }
    let text = std::fs::read_to_string(root.join(".specify/feature.json")).ok()?;
    let data: serde_json::Value = serde_json::from_str(&text).ok()?;
    let dir = data["feature_directory"]
        .as_str()
        .unwrap_or_default()
        .trim_end_matches('/');
    dir.rsplit('/')
        .next()
        .filter(|n| !n.is_empty())
        .map(str::to_owned)
}

/// The named feature's directory, verdict and the open tasks that hold the landing; an unreadable `tasks.md` holds nothing, as the Python's
/// traceback printed nothing.
#[must_use]
pub fn feature_status(root: &Path, name: Option<&str>) -> FeatureStatus {
    let Some(name) = name else {
        return FeatureStatus::default();
    };
    let dir = root.join("specs").join(name);
    let owned = Some(name.to_owned());
    let Ok(tasks) = std::fs::read_to_string(dir.join("tasks.md")) else {
        return FeatureStatus {
            name: owned,
            ..FeatureStatus::default()
        };
    };
    let held = l7r_guard::shared::speckit::holding(&dir).unwrap_or_default();
    let open_tasks = tasks
        .lines()
        .filter_map(|l| {
            l.trim_start()
                .strip_prefix("- [ ] ")
                .filter(|t| t.starts_with('T') && t[1..].starts_with(|c: char| c.is_ascii_digit()))
        })
        .map(str::trim)
        .filter(|t| held.iter().any(|h| h.starts_with(t)))
        .map(|t| t.chars().take(80).collect())
        .collect();
    let faithful = !crate::arbiter::spec_verdict(&dir).is_empty();
    FeatureStatus {
        name: owned,
        exists: true,
        faithful,
        open_tasks,
    }
}

#[cfg(test)]
mod tests;
