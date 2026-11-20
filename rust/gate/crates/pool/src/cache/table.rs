//! THE READ TABLE (feature 449 T221, from `specs/449-rust-codebase/derivations/T219-pipeline.md`, "Contract" and Keep 3): one file a
//! clone, one row a distinct path any published map's engine reported reading (a miss among them) and one a font directory or file the
//! Mode A raster loads, each row its path, stat, the filesystem's time it was hashed at, its digest (none for a font row) and the maps that
//! read it. A path shared by several sheets is held once a run, not once a map (the `work-budget` agent's first verdict on the derivation).
//!
//! The file is text, one row a line, tab-separated: `<kind> <path> <size> <mtime> <ctime> <inode> <hashed> <digest> <maps>`, the kind `r`
//! (a read), `d` (a font directory) or `f` (a font file), the maps space-separated `<tier>/<name>`. A row's map list is kept as its text
//! and split only when the row moved or a run asks which maps it names (the derivation's `list_read`). It is written whole, to a temporary
//! file renamed over it, and only in a run where a row changed.
//!
//! Research: plumbing - NONE: the cache's bookkeeping, deciding nothing about a map

use std::collections::BTreeMap;
use std::path::Path;

use super::stat::Stat;

/// The table's first line: a table with any other is read as none (its entries thrown away, never trusted).
pub const HEADER: &str = "# l7r pool read table 1";

/// What a row holds.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RowKind {
    /// A file an engine reported reading, or looking for and not finding.
    Read,
    /// A font directory the Mode A raster scans: held by its stat alone.
    FontDir,
    /// A font file the Mode A raster loads: held by its stat alone.
    FontFile,
}

impl RowKind {
    fn tag(self) -> &'static str {
        match self {
            Self::Read => "r",
            Self::FontDir => "d",
            Self::FontFile => "f",
        }
    }

    fn of(tag: &str) -> Option<Self> {
        match tag {
            "r" => Some(Self::Read),
            "d" => Some(Self::FontDir),
            "f" => Some(Self::FontFile),
            _ => None,
        }
    }

    /// A font row: a directory or a file of the font set.
    #[must_use]
    pub fn is_font(self) -> bool {
        self != Self::Read
    }
}

/// One row.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Row {
    pub kind: RowKind,
    pub stat: Stat,
    /// The filesystem's time at or before the digest was taken: the stat stands for the digest only while the file settled before it.
    pub hashed: i128,
    /// The content's digest (`-` for an absent file, empty for a font row).
    pub digest: String,
    maps: String,
}

impl Row {
    /// A row with no map yet.
    #[must_use]
    pub fn new(kind: RowKind, stat: Stat, hashed: i128, digest: String) -> Self {
        Self {
            kind,
            stat,
            hashed,
            digest,
            maps: String::new(),
        }
    }

    /// The maps the row names (the derivation's `list_read`: split from its text only when asked).
    #[must_use]
    pub fn maps(&self) -> Vec<&str> {
        self.maps.split(' ').filter(|m| !m.is_empty()).collect()
    }

    /// Whether the row names `map`.
    #[must_use]
    pub fn names(&self, map: &str) -> bool {
        self.maps().contains(&map)
    }

    /// `map` added to the row's list; whether it was not there.
    pub fn add(&mut self, map: &str) -> bool {
        if self.names(map) {
            return false;
        }
        if !self.maps.is_empty() {
            self.maps.push(' ');
        }
        self.maps.push_str(map);
        true
    }

    /// The row's list emptied: its maps' entries removed.
    pub fn clear(&mut self) {
        self.maps.clear();
    }
}

/// The table: its rows by path, and whether a row changed this run (it is written only then).
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Table {
    pub rows: BTreeMap<String, Row>,
    pub changed: bool,
}

/// A path the table can hold: one with no tab or line end, which its lines could not keep.
#[must_use]
pub fn holdable(path: &str) -> bool {
    !path.contains(['\t', '\n', '\r'])
}

impl Table {
    /// The table read from its text, or None where the text is not a table (no header, or a row that does not read).
    #[must_use]
    pub fn parse(text: &str) -> Option<Self> {
        let mut lines = text.lines();
        if lines.next() != Some(HEADER) {
            return None;
        }
        let mut rows = BTreeMap::new();
        for line in lines {
            let cells: Vec<&str> = line.split('\t').collect();
            let [kind, path, size, mtime, ctime, ino, hashed, digest, maps] = cells[..] else {
                return None;
            };
            let row = Row {
                kind: RowKind::of(kind)?,
                stat: Stat::from_cells(&[size, mtime, ctime, ino])?,
                hashed: hashed.parse().ok()?,
                digest: digest.to_owned(),
                maps: maps.to_owned(),
            };
            rows.insert(path.to_owned(), row);
        }
        Some(Self {
            rows,
            changed: false,
        })
    }

    /// The table as its file holds it.
    #[must_use]
    pub fn text(&self) -> String {
        let mut out = format!("{HEADER}\n");
        for (path, r) in &self.rows {
            let [size, mtime, ctime, ino] = r.stat.cells();
            out.push_str(
                &[
                    r.kind.tag(),
                    path,
                    &size,
                    &mtime,
                    &ctime,
                    &ino,
                    &r.hashed.to_string(),
                    &r.digest,
                    &r.maps,
                ]
                .join("\t"),
            );
            out.push('\n');
        }
        out
    }

    /// The table written at `path`: a temporary file beside it, synced, renamed over it, and the directory synced.
    ///
    /// # Errors
    /// The file or its directory cannot be written.
    pub fn write(&self, path: &Path) -> std::io::Result<()> {
        super::entry::replace(path, self.text().as_bytes())
    }
}

#[cfg(test)]
mod tests {
    use super::{holdable, Row, RowKind, Table, HEADER};
    use crate::cache::stat::Stat;

    /// A table reads back as it was written; its map lists add each map once and empty; anything not a table is none.
    #[test]
    fn a_table_round_trips_and_its_lists_add_once() {
        let mut t = Table::default();
        let mut r = Row::new(RowKind::Read, Stat::Absent, 7, "-".into());
        assert!(r.maps().is_empty());
        assert!(r.add("hamlets/a") && r.add("magistracies/b") && !r.add("hamlets/a"));
        assert_eq!(r.maps(), ["hamlets/a", "magistracies/b"]);
        t.rows.insert("l7r/x.md".into(), r.clone());
        let stat = Stat::Present {
            size: 1,
            mtime: 2,
            ctime: 3,
            ino: 4,
        };
        t.rows.insert(
            "/f".into(),
            Row::new(RowKind::FontFile, stat, 9, String::new()),
        );
        t.rows.insert(
            "/d".into(),
            Row::new(RowKind::FontDir, stat, 9, String::new()),
        );
        let back = Table::parse(&t.text()).unwrap();
        assert_eq!(back, t);
        assert!(back.rows["/f"].kind.is_font() && !back.rows["l7r/x.md"].kind.is_font());
        r.clear();
        assert!(r.maps().is_empty() && !r.names("hamlets/a"));
        for bad in [
            String::new(),
            "# another header\n".to_owned(),
            format!("{HEADER}\nr\tp\n"),
            format!("{HEADER}\nx\tp\t-\t-\t-\t-\t0\t-\t\n"),
            format!("{HEADER}\nr\tp\t-\t-\t-\t1\t0\t-\t\n"),
            format!("{HEADER}\nr\tp\t-\t-\t-\t-\tz\t-\t\n"),
        ] {
            assert_eq!(Table::parse(&bad), None, "{bad:?}");
        }
        assert!(holdable("a/b.md") && !holdable("a\tb") && !holdable("a\nb"));
    }
}
