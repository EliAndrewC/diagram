//! A file's stat as the read table holds it, and the filesystem's own clock (feature 449 T221, from
//! `specs/449-rust-codebase/derivations/T219-pipeline.md`, Keep 2: a stored digest is reused only while the file's size, mtime (ns), ctime
//! and inode all match its row AND its mtime is older than the row's own hashing - the racy-file rule).
//!
//! THE CLOCK IS THE FILESYSTEM'S: a file's timestamps come from the kernel's coarse clock, which can stand up to a tick behind the precise
//! one `SystemTime::now` reads, so a file written just after a precise "now" could carry an earlier time than it. Every reference time the
//! cache compares a file's times with is therefore itself a file's time - [`fs_clock`] writes a byte and reads its mtime back - as git
//! compares a racily clean entry with its index file's mtime.
//!
//! Research: plumbing - NONE: reads a file's metadata, deciding nothing about a map

use std::os::unix::fs::MetadataExt as _;
use std::path::Path;

/// What the table holds of a path: absent (a miss is a read, T221), or present with its size, mtime and ctime (ns) and inode.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stat {
    Absent,
    Present {
        size: u64,
        mtime: i128,
        ctime: i128,
        ino: u64,
    },
}

/// `seconds` and `nanos` as nanoseconds.
fn ns(seconds: i64, nanos: i64) -> i128 {
    i128::from(seconds) * 1_000_000_000 + i128::from(nanos)
}

/// The stat of `path`, its symlinks followed (a font directory's links are what the raster loads through); anything unreadable is absent.
#[must_use]
pub fn stat(path: &Path) -> Stat {
    std::fs::metadata(path).map_or(Stat::Absent, |m| Stat::Present {
        size: m.size(),
        mtime: ns(m.mtime(), m.mtime_nsec()),
        ctime: ns(m.ctime(), m.ctime_nsec()),
        ino: m.ino(),
    })
}

impl Stat {
    /// The later of its mtime and ctime: what the racy-file rule holds against a reference time. None for an absent file.
    #[must_use]
    pub fn newest(&self) -> Option<i128> {
        match self {
            Self::Absent => None,
            Self::Present { mtime, ctime, .. } => Some(*mtime.max(ctime)),
        }
    }

    /// Whether the stat may stand for content hashed at `hashed` (the filesystem's clock then): an absent file always may; a present one
    /// only where neither of its times reaches `hashed`, so no write after the hashing can carry the same times.
    #[must_use]
    pub fn settled_before(&self, hashed: i128) -> bool {
        self.newest().is_none_or(|t| t < hashed)
    }

    /// The four cells the table writes: size, mtime, ctime, inode, each `-` for an absent file.
    #[must_use]
    pub fn cells(&self) -> [String; 4] {
        match self {
            Self::Absent => ["-", "-", "-", "-"].map(str::to_owned),
            Self::Present {
                size,
                mtime,
                ctime,
                ino,
            } => [
                size.to_string(),
                mtime.to_string(),
                ctime.to_string(),
                ino.to_string(),
            ],
        }
    }

    /// The stat the four cells [`Stat::cells`] wrote, or None where they are not such cells.
    #[must_use]
    pub fn from_cells(cells: &[&str]) -> Option<Self> {
        match cells {
            ["-", "-", "-", "-"] => Some(Self::Absent),
            [size, mtime, ctime, ino] => Some(Self::Present {
                size: size.parse().ok()?,
                mtime: mtime.parse().ok()?,
                ctime: ctime.parse().ok()?,
                ino: ino.parse().ok()?,
            }),
            _ => None,
        }
    }
}

/// The filesystem's clock now: the file at `file` written (its content this process's id) and its mtime read back.
///
/// # Errors
/// The file cannot be written, or then read.
pub fn fs_clock(file: &Path) -> std::io::Result<i128> {
    std::fs::write(file, std::process::id().to_string())?;
    let m = std::fs::metadata(file)?;
    Ok(ns(m.mtime(), m.mtime_nsec()))
}

#[cfg(test)]
mod tests {
    use super::{fs_clock, stat, Stat};

    /// A present file's four cells read back as its stat, an absent one's as absent; anything else is no stat. The racy-file rule: a file
    /// settles only before the time it is held against.
    #[test]
    fn a_stat_round_trips_its_cells_and_settles_only_before_its_hashing() {
        let dir = l7r_shared::tempdir::TempDir::new("cache-stat");
        let f = dir.path().join("f");
        std::fs::write(&f, "abc").unwrap();
        let s = stat(&f);
        let cells = s.cells();
        let back: Vec<&str> = cells.iter().map(String::as_str).collect();
        assert_eq!(Stat::from_cells(&back), Some(s));
        assert!(matches!(s, Stat::Present { size: 3, .. }));
        let gone = stat(&dir.path().join("gone"));
        assert_eq!(gone, Stat::Absent);
        assert_eq!(Stat::from_cells(&["-", "-", "-", "-"]), Some(Stat::Absent));
        assert_eq!(Stat::from_cells(&["1", "x", "2", "3"]), None);
        assert_eq!(Stat::from_cells(&["1"]), None);
        let now = fs_clock(&dir.path().join("clock")).unwrap();
        let t = s.newest().unwrap();
        assert!(t <= now);
        assert!(s.settled_before(t + 1) && !s.settled_before(t));
        assert!(gone.settled_before(0) && gone.newest().is_none());
        assert!(fs_clock(&dir.path().join("no/such/clock")).is_err());
    }
}
