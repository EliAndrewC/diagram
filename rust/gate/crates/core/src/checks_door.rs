//! The modal batches `report` names, kept for the dispatch guard (feature 449 T86, from `checks_door.rs`, split out by T92). The doors' loop
//! that lived here left with its last door, `owed-door`, when feature 449 T149 ported `entry_owed.py`, the door's last Python caller.

use std::path::Path;

use l7r_shared::checks;
use l7r_shared::pyjson;
use serde_json::{json, Value};

const BATCHES: &str = "modal-batches.json";

/// `record_owed.keep_batches`: the batches `report` names, kept for the dispatch guard, by atomic rename.
///
/// # Errors
///
/// The text of the write or the rename that failed.
pub fn keep_batches(root: &Path, batches: &Value) -> Result<(), String> {
    let common = checks::common_dir(root);
    let body = pyjson::dumps(
        &json!({"utc": checks::now(), "batches": batches}),
        None,
        true,
    ) + "\n";
    let path = common.join(BATCHES);
    let tmp = path.with_extension(format!("{}.tmp", std::process::id()));
    std::fs::write(&tmp, body).map_err(|e| e.to_string())?;
    std::fs::rename(&tmp, &path).map_err(|e| e.to_string())
}

#[cfg(test)]
mod tests;
