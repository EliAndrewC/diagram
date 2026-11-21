//! The map declaration (feature 449 T175, `pack_audit/onmap.py` whole; feature 257, spec FR-003): a sheet whose subject already stands
//! on a settlement map says so in its notes, and the map check holds the sheet to that map.
//!
//! ```text
//! **On map**: <manifest path from the skill root> - <manifest key> at (<x>, <y>) = <sheet id>
//! ```
//!
//! A sheet with no such line is on no map; one whose subject a map records opts out in so many words: `**On map**: none - <why>`.
//!
//! Research:
//!     the map declaration - NONE: a notes line read by its grammar, deciding nothing about a building

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;
use l7r_shared::py_text::repr;

use crate::py::float;

// `re.M`'s `$` is the end of any line: written out, since `pyre::py` reads `$` as the end of the text (feature 449 T175)
/// FEATURE 449 T182: the spaces about the declaration stop at its line (`[ \t]`, not `\s`) - `\s*` took the line break after it and a
/// blank line below, so a refused line was quoted with them and an empty one read the next line as its declaration.
static ON_MAP_LINE: LazyLock<Regex> =
    LazyLock::new(|| py(r"(?m)^\*\*On map\*\*:[ \t]*(?P<rest>[^\n]*?)[ \t]*(?=\n|\z)"));
static ON_MAP: LazyLock<Regex> = LazyLock::new(|| {
    py(
        r"^(?P<manifest>\S+)\s+-\s+(?P<key>[A-Za-z_][\w]*)\s+at\s+\(\s*(?P<x>-?\d+(?:\.\d+)?)\s*,\s*(?P<y>-?\d+(?:\.\d+)?)\s*\)\s*=\s*`?(?P<sheet_id>[A-Za-z_][\w-]*)`?$",
    )
});
static NONE: LazyLock<Regex> = LazyLock::new(|| py(r"^none\s+-\s+\S"));

/// The declaration's grammar, as a refusal names it.
pub const GRAMMAR: &str =
    "**On map**: <manifest path from the skill root> - <manifest key> at (<x>, <y>) = <sheet id>";
/// The explicit opt-out (feature 294 B24): a sheet whose subject a map records, drawn to stand apart from it, says why.
pub const OPT_OUT: &str = "**On map**: none - <why>";

/// A sheet's declared map: the manifest (a path from the skill root, or absolute), the list the subject is recorded in, its center in
/// the map's px, and the `id` of the sheet rect that is the subject.
#[derive(Debug, Clone, PartialEq)]
pub struct OnMap {
    pub manifest: String,
    pub key: String,
    pub x: f64,
    pub y: f64,
    pub sheet_id: String,
}

/// The declaration in a notes file's text, None when there is none (or it is the opt-out).
///
/// # Errors
/// A line that starts the declaration and does not follow the grammar, refused by name.
pub fn parse_on_map(notes: &str) -> Result<Option<OnMap>, Error> {
    let Some(m) = ON_MAP_LINE.captures(notes).ok().flatten() else {
        return Ok(None);
    };
    let rest = &m["rest"];
    if NONE.is_match(rest).unwrap_or(false) {
        return Ok(None);
    }
    let bare = rest.replace('`', "");
    let Some(g) = ON_MAP.captures(&bare).ok().flatten() else {
        return Err(Error::new(
            "ValueError",
            format!(
                "the notes' `**On map**:` line does not follow the grammar `{GRAMMAR}`: {}",
                repr(&m[0])
            ),
        ));
    };
    Ok(Some(OnMap {
        manifest: g["manifest"].to_owned(),
        key: g["key"].to_owned(),
        x: float(&g["x"])?,
        y: float(&g["y"])?,
        sheet_id: g["sheet_id"].to_owned(),
    }))
}

/// Whether the notes carry an `**On map**:` line at all - a declaration, or the explicit opt-out.
#[must_use]
pub fn declares(notes: &str) -> bool {
    ON_MAP_LINE.is_match(notes).unwrap_or(false)
}

/// The notes file beside a sheet (`<stem>.notes.md`), or nothing for a path that is no `.svg`.
#[must_use]
pub fn notes_path(svg_path: &str) -> Option<String> {
    svg_path
        .strip_suffix(".svg")
        .map(|stem| format!("{stem}.notes.md"))
}

/// The text of the sheet's notes file, None where there is none (`os.path.isfile`).
///
/// # Errors
/// The file cannot be read: Python's `OSError` or `UnicodeDecodeError`.
pub fn read_notes(svg_path: &str) -> Result<Option<String>, Error> {
    let Some(notes) = notes_path(svg_path) else {
        return Ok(None);
    };
    if !Path::new(&notes).is_file() {
        return Ok(None);
    }
    l7r_gate_core::record::read_text(Path::new(&notes))
        .map(Some)
        .map_err(|e| crate::py::os_error(&e, &notes))
}

/// The declaration of the sheet's notes file, or None.
///
/// # Errors
/// The notes cannot be read, or their line breaks the grammar.
pub fn read_on_map(svg_path: &str) -> Result<Option<OnMap>, Error> {
    match read_notes(svg_path)? {
        Some(text) => parse_on_map(&text),
        None => Ok(None),
    }
}

#[cfg(test)]
mod tests {
    use super::{declares, notes_path, parse_on_map, read_on_map, OnMap};

    #[test]
    fn a_declaration_is_read_by_its_grammar() {
        let line = "x\n**On map**: pool/a/b.json - religious at (12.5, -3) = `shrine` \nmore";
        assert_eq!(
            parse_on_map(line).unwrap(),
            Some(OnMap {
                manifest: "pool/a/b.json".into(),
                key: "religious".into(),
                x: 12.5,
                y: -3.0,
                sheet_id: "shrine".into()
            })
        );
        assert_eq!(parse_on_map("**On map**: none - apart").unwrap(), None);
        assert_eq!(parse_on_map("no line").unwrap(), None);
        // T182: the refused line is quoted without the line break after it (it was quoted with it), and an empty declaration is
        // refused as itself, never read from the line below
        let e = parse_on_map("**On map**: somewhere\n\n").unwrap_err();
        assert!(
            e.message.ends_with(": '**On map**: somewhere'"),
            "{}",
            e.message
        );
        let e = parse_on_map("**On map**:\nm.json - houses at (1, 2) = s").unwrap_err();
        assert!(e.message.ends_with(": '**On map**:'"), "{}", e.message);
        assert!(declares("**On map**: none - x") && !declares("On map"));
        assert_eq!(notes_path("a.png"), None);
    }

    #[test]
    fn a_sheet_s_notes_are_read_beside_it() {
        let dir = l7r_shared::tempdir::TempDir::new("mode-a-onmap");
        let svg = dir.path().join("s.svg").to_string_lossy().into_owned();
        assert_eq!(read_on_map(&svg).unwrap(), None);
        std::fs::write(
            dir.path().join("s.notes.md"),
            "**On map**: m.json - houses at (1, 2) = s",
        )
        .unwrap();
        assert_eq!(read_on_map(&svg).unwrap().unwrap().key, "houses");
        std::fs::write(dir.path().join("t.notes.md"), [0xff_u8]).unwrap();
        let t = dir.path().join("t.svg").to_string_lossy().into_owned();
        assert_eq!(read_on_map(&t).unwrap_err().kind, "UnicodeDecodeError");
        assert_eq!(read_on_map("x.txt").unwrap(), None);
    }
}
