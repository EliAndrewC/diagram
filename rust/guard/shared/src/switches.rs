//! The research switch's one reader (feature 451 T244, the GM 2026-11-25: "I would like to essentially defer all of it until at least
//! tomorrow"): `dev/switches.json`'s `research` entry, `open` (the shipped rules: research runs when a decision needs it) or `deferred`
//! (no search pass and no page session starts unasked; a physical task's boxes may be answered `deferred: UNRESEARCHED`). The guard, the
//! tick and the switches tool (`l7r-gate switches`) all read it here, since the guard builds on no gate crate.
//!
//! A MISSING OR MALFORMED ENTRY READS `open`, with MALFORMED in its why: `open` is the state in which the research rules bind, as
//! `clean` is the claims switch's, so a broken file never silently defers research.

use std::path::Path;

use serde_json::Value;

/// The file, relative to the repository's top.
pub const FILE: &str = "dev/switches.json";
/// The research axis' states, the default first.
pub const RESEARCH_STATES: [&str; 2] = ["open", "deferred"];
/// The answer a deferred research box carries on its own line (T244).
pub const DEFERRED_ANSWER: &str = "deferred: UNRESEARCHED";

/// The research axis as read: its state and, where thrown, why, by whom and when; `why` names a malformed entry.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Research {
    pub state: String,
    pub why: String,
    pub who: String,
    pub utc: String,
}

impl Research {
    /// Is research deferred?
    #[must_use]
    pub fn deferred(&self) -> bool {
        self.state == "deferred"
    }

    fn open(why: String) -> Self {
        Self {
            state: "open".to_owned(),
            why,
            ..Self::default()
        }
    }
}

fn text(raw: &Value, key: &str) -> String {
    raw[key].as_str().unwrap_or_default().to_owned()
}

/// The research axis of `data`, the file's parsed text (`None` where it did not parse).
#[must_use]
pub fn research_of(data: Option<&Value>) -> Research {
    let Some(data) = data.filter(|d| d.is_object()) else {
        return Research::open(
            "switches.json is MALFORMED - research reads open, its rules in force".to_owned(),
        );
    };
    let Some(raw) = data.get("research") else {
        return Research::open(String::new());
    };
    let state = raw["state"].as_str().unwrap_or_default();
    if !RESEARCH_STATES.contains(&state) {
        return Research::open(format!(
            "the research entry is MALFORMED (state {}, not one of ('open', 'deferred')) - research reads open, its rules in force",
            raw["state"]
        ));
    }
    Research {
        state: state.to_owned(),
        why: text(raw, "why"),
        who: text(raw, "who"),
        utc: text(raw, "utc"),
    }
}

/// The research axis of the repository at `root`; no file is the default, `open`.
#[must_use]
pub fn research(root: &Path) -> Research {
    let Ok(body) = std::fs::read_to_string(root.join(FILE)) else {
        return Research::open(String::new());
    };
    research_of(serde_json::from_str::<Value>(&body).ok().as_ref())
}

#[cfg(test)]
mod tests;
