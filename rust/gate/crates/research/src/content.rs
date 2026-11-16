//! The page's CONTENT in `l7r/diagram/interactive/assets/*.json` (`interactive/content.py`, feature 207; ported by feature 449 T144): prose
//! a reader sees lives in assets, outside the engine's key, so a wording edit is not an engine change. The loader is deliberately dumb: no
//! schema, a malformed file refused loudly.

use std::path::Path;

use serde_json::Value;

use crate::{Error, Result};

/// Where the assets are, from the tree's root.
pub const ASSETS: &str = "l7r/diagram/interactive/assets";

/// The parsed JSON of `<tree>/<ASSETS>/<name>`.
///
/// # Errors
/// A file that cannot be read (`OSError`) or is not JSON (`JSONDecodeError`), each in the library's words.
pub fn content(tree: &Path, name: &str) -> Result<Value> {
    let path = tree.join(ASSETS).join(name);
    let text = l7r_gate_core::record::read_text(&path)
        .map_err(|e| Error::new("OSError", format!("{e}: '{}'", path.display())))?;
    crate::json(&text).map_err(|e| Error::new("JSONDecodeError", e))
}

#[cfg(test)]
mod tests;
