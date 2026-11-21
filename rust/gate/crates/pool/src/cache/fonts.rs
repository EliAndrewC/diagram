//! The font set a Mode A sheet's picture is drawn with (feature 449 T221, from `specs/449-rust-codebase/derivations/T219-pipeline.md`: the
//! Mode A raster loads the system's fonts, so their identity is part of a sheet's key - each font directory and font file a row of the read
//! table, held by its stat alone, a directory listed again only when its own stat moved).
//!
//! WHERE THE RASTER LOOKS: `resvg`'s font database scans the directories fontconfig names, and the system's `/etc/fonts/fonts.conf` names
//! `/usr/share/fonts`, `/usr/local/share/fonts`, the XDG data home's `fonts` and `~/.fonts` (read 2026-11-19); a root that is not there is
//! held as absent (a miss is a read: one created later moves the set). Inside them the database takes every subdirectory and every file
//! with a font's extension (`fontdb`'s `load_fonts_dir_impl`: `ttf`, `ttc`, `otf`, `otc`, either case), its links followed - so a
//! file of any other name moves nothing it draws, and is not held.
//!
//! Research: the font set's roots - CONVENTION: fontconfig's own directories as this system's `/etc/fonts/fonts.conf` names them, read 2026-11-19

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};

use super::table::RowKind;

/// The extensions of the files the font database loads.
const FONT_EXT: [&str; 8] = ["ttf", "ttc", "otf", "otc", "TTF", "TTC", "OTF", "OTC"];

/// The font roots for a home and an XDG data home (none: `<home>/.local/share`).
#[must_use]
pub fn roots(home: Option<&Path>, xdg_data: Option<&Path>) -> Vec<PathBuf> {
    let mut out = vec![
        PathBuf::from("/usr/share/fonts"),
        PathBuf::from("/usr/local/share/fonts"),
    ];
    if let Some(data) = xdg_data
        .map(Path::to_path_buf)
        .or_else(|| home.map(|h| h.join(".local/share")))
    {
        out.push(data.join("fonts"));
    }
    if let Some(h) = home {
        out.push(h.join(".fonts"));
    }
    out
}

/// This process's font roots: `HOME` and `XDG_DATA_HOME` as they stand.
#[must_use]
pub fn system_roots() -> Vec<PathBuf> {
    let var = |n: &str| {
        std::env::var_os(n)
            .filter(|v| !v.is_empty())
            .map(PathBuf::from)
    };
    roots(var("HOME").as_deref(), var("XDG_DATA_HOME").as_deref())
}

/// The font set under `roots`: each root (there or not) and each directory beneath it as [`RowKind::FontDir`], each font file as
/// [`RowKind::FontFile`], links followed and each directory listed once however it is reached; with the directories listed and the
/// names read, for the counts.
#[must_use]
pub fn walk(roots: &[PathBuf]) -> (Vec<(PathBuf, RowKind)>, usize, usize) {
    let mut out = Vec::new();
    let mut seen = BTreeSet::new();
    let (mut listed, mut names) = (0, 0);
    let mut todo: Vec<PathBuf> = roots.iter().rev().cloned().collect();
    while let Some(dir) = todo.pop() {
        let canonical = std::fs::canonicalize(&dir).unwrap_or_else(|_| dir.clone());
        if !seen.insert(canonical) {
            continue;
        }
        out.push((dir.clone(), RowKind::FontDir));
        let Ok(listing) = std::fs::read_dir(&dir) else {
            continue;
        };
        listed += 1;
        let mut entries: Vec<PathBuf> = listing.flatten().map(|e| e.path()).collect();
        names += entries.len();
        entries.sort();
        let mut subdirs = Vec::new();
        for p in entries {
            if p.is_dir() {
                subdirs.push(p);
            } else if p
                .extension()
                .is_some_and(|e| FONT_EXT.iter().any(|f| e == *f))
                && p.is_file()
            {
                out.push((p, RowKind::FontFile));
            }
        }
        todo.extend(subdirs.into_iter().rev());
    }
    (out, listed, names)
}

#[cfg(test)]
mod tests {
    use std::path::{Path, PathBuf};

    use super::{roots, system_roots, walk};
    use crate::cache::table::RowKind;

    /// The roots are fontconfig's four, the XDG data home where it is set; the walk holds every directory (a root not there among them),
    /// each font file by its extension, no other file, and a directory reached twice once.
    #[test]
    fn the_font_set_is_every_directory_and_font_file_under_the_roots() {
        let home = Path::new("/h");
        assert_eq!(
            roots(Some(home), None),
            [
                "/usr/share/fonts",
                "/usr/local/share/fonts",
                "/h/.local/share/fonts",
                "/h/.fonts"
            ]
            .map(PathBuf::from)
        );
        assert_eq!(
            roots(None, Some(Path::new("/x")))[2],
            PathBuf::from("/x/fonts")
        );
        assert_eq!(roots(None, None).len(), 2);
        assert!(system_roots().len() >= 2);
        let dir = l7r_shared::tempdir::TempDir::new("cache-fonts");
        let a = dir.path().join("a");
        std::fs::create_dir_all(a.join("sub")).unwrap();
        for f in ["x.ttf", "sub/y.OTC", "readme.txt"] {
            std::fs::write(a.join(f), "f").unwrap();
        }
        std::os::unix::fs::symlink(&a, dir.path().join("link")).unwrap();
        let gone = dir.path().join("gone");
        let (set, listed, names) = walk(&[a.clone(), gone.clone(), dir.path().join("link")]);
        assert_eq!(
            set,
            vec![
                (a.clone(), RowKind::FontDir),
                (a.join("x.ttf"), RowKind::FontFile),
                (a.join("sub"), RowKind::FontDir),
                (a.join("sub/y.OTC"), RowKind::FontFile),
                (gone, RowKind::FontDir),
            ]
        );
        assert_eq!((listed, names), (2, 4));
    }
}
