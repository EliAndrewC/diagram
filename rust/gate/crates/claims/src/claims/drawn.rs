//! A procedure section's known departure, owed again when the code that draws it moves (feature 451 T220).
//!
//! A claim of `docs/buildings.md` or `docs/building-programs.md` is fingerprinted by its section's text and its pages, never by the
//! Rust that draws the section. So a claim judged DRIFTED with `fix: code` - "known (417 T33): the porch is drawn 8 by 6 ft" - stood
//! in `make claims-report` after `layout.rs` drew the porch at the page's size: nothing the index reads had moved, and the claim was
//! never judged again. Such a finding's row keeps a digest of the Mode A engine's sources (`drawn`), and is owed again when it
//! differs. What it costs: every `fix: code` finding on a section is judged once more after any change under `rust/mode_a/src`,
//! whether or not the change draws that section - two rows on 2026-11-24, six at the most the report has held.

use std::path::Path;

use l7r_shared::sha256;
use serde_json::Value;

use super::index::field;

/// Why such a finding is owed again.
pub const DRAWN: &str = "the code that draws it changed since the finding";
/// The sources that draw the procedure sections' plans.
const ENGINE: &str = "rust/mode_a/src";

fn walk(dir: &Path, out: &mut Vec<std::path::PathBuf>) {
    let mut entries: Vec<_> = std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .collect();
    entries.sort_by_key(std::fs::DirEntry::file_name);
    for e in entries {
        let p = e.path();
        if p.is_dir() {
            walk(&p, out);
        } else if p.extension().is_some_and(|x| x == "rs") {
            out.push(p);
        }
    }
}

/// The Mode A engine's sources under `root`, fingerprinted: every `.rs` file's path and bytes.
pub fn drawn_by(root: &Path) -> String {
    let mut files = Vec::new();
    walk(&root.join(ENGINE), &mut files);
    let mut all = Vec::new();
    for f in files {
        all.extend_from_slice(
            f.strip_prefix(root)
                .unwrap_or(&f)
                .to_string_lossy()
                .as_bytes(),
        );
        all.push(0);
        all.extend(std::fs::read(&f).unwrap_or_default());
        all.push(0);
    }
    sha256::hex(&all).chars().take(16).collect()
}

/// Does a finding's row keep the engine it was judged against? Only a section's DRIFTED whose note says the code is what moves.
pub fn keeps(verdict: &str, note: &str) -> bool {
    verdict == "DRIFTED" && note.contains("fix: code")
}

/// Is `was` such a finding, judged against an engine that has changed since?
pub fn moved(was: &Value, root: &Path) -> bool {
    keeps(field(was, "verdict"), field(was, "note"))
        && was
            .get("drawn")
            .and_then(Value::as_str)
            .is_some_and(|d| d != drawn_by(root))
}

#[cfg(test)]
mod tests {
    use super::{drawn_by, moved};
    use serde_json::json;

    #[test]
    fn a_section_s_code_fix_drift_is_owed_again_when_the_engine_moves() {
        let root = crate::checks::scratch("claims-drawn");
        let put = |rel: &str, text: &str| {
            let p = root.join(rel);
            std::fs::create_dir_all(p.parent().unwrap()).unwrap();
            std::fs::write(p, text).unwrap();
        };
        // 417 T33's genkan porch: the section said the porch is drawn 8 by 6 ft, the code to be fixed
        put(
            "rust/mode_a/src/compound/layout.rs",
            "const GENKAN: (f64, f64) = (8.0, 6.0);\n",
        );
        put("rust/mode_a/src/notes.md", "not code\n");
        let at = drawn_by(&root);
        let known = json!({"verdict": "DRIFTED", "note": "known (417 T33): the porch is drawn 8 by 6 ft; fix: code; effect: a short porch", "drawn": at});
        assert!(!moved(&known, &root));
        put("rust/mode_a/src/notes.md", "still not code\n");
        assert!(!moved(&known, &root));
        // the fix lands in the code: the finding is owed again, where no section or page moved
        put(
            "rust/mode_a/src/compound/layout.rs",
            "const GENKAN: (f64, f64) = (12.0, 9.0);\n",
        );
        assert!(moved(&known, &root));
        // a finding the claim is to answer, a pass, and a row judged before the digest was kept are not
        for other in [
            json!({"verdict": "DRIFTED", "note": "reads loosely; fix: claim; effect: none", "drawn": at}),
            json!({"verdict": "IN-STEP", "note": "fine", "drawn": at}),
            json!({"verdict": "DRIFTED", "note": "known (417 T33): x; fix: code; effect: y"}),
        ] {
            assert!(!moved(&other, &root), "{other}");
        }
    }
}
