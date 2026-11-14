//! The authoring tools (feature 449 T135, `ask:449-phase3-remainder`, ported whole with no door, FR-003): `l7r-gate claim` (`make claim`
//! and spec-kit's `create-new-feature.sh`, [`claim`]), `l7r-gate trial-start` and `trial-review` (`make trial`, `make trial-review`,
//! [`trial`]) and `l7r-gate patch` (the anchored-edit sweep, [`patch`]), from `scripts/claim-feature.py`, `trial-start.py`,
//! `trial-review.py` and `patch.py`. `make trial` claims its number in process, where `trial-start.py` ran `claim-feature.py`.

pub mod claim;
pub mod patch;
pub mod trial;

use l7r_gate_core::Reply;

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// A raise: what was printed before it, then its message after a `Traceback` line, exit 1, as the Python's uncaught exception ended (the
/// form the other ports answer one in, `ask:449-usage-text`).
fn raised(tool: &str, stdout: String, stderr: &str, why: &str) -> Reply {
    reply(
        stdout,
        format!("{stderr}Traceback (most recent call last):\n  l7r-gate {tool}\n{why}\n"),
        1,
    )
}

/// A file as `read_text(encoding="utf-8")` reads it: strictly UTF-8, its newlines universal; the error what the Python raised.
fn read_strict(path: &std::path::Path) -> Result<String, String> {
    let bytes = std::fs::read(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let text = String::from_utf8(bytes)
        .map_err(|e| format!("UnicodeDecodeError: {}: {e}", path.display()))?;
    Ok(l7r_gate_core::record::repo::universal(&text))
}

#[cfg(test)]
mod tests;
