//! HOLDING THE TABLE (feature 449 T221, the derivation's `hold the table:` step): each row the run needs is held against its file - the
//! stat equal and the file settled before the row's hashing, nothing more; else the file hashed, and a digest that moved removes every
//! entry the row names, durably, before the row takes the new digest (Keep 3). A font row has no digest: any move of its stat removes the
//! sheets' entries and the font set is walked again.
//!
//! Research: plumbing - NONE: the cache's bookkeeping, deciding nothing about a map

use std::collections::BTreeSet;

use super::{abs, digest, map_id, stat, Run};
use crate::walk::Map;

impl Run<'_> {
    /// The rows `maps` need held: every row when they are every live map, else the rows naming one of them (each row's list read to ask)
    /// and the font rows where one is a sheet.
    pub(super) fn hold(&mut self, maps: &[&Map], every: bool) -> Result<(), String> {
        let ids: BTreeSet<String> = maps.iter().map(|m| map_id(m)).collect();
        let sheets = maps.iter().any(|m| m.kind.is_sheet());
        let paths: Vec<String> = self.table.rows.keys().cloned().collect();
        let mut fonts_moved = false;
        for path in paths {
            let row = &self.table.rows[&path];
            let wanted = every
                || if row.kind.is_font() {
                    sheets
                } else {
                    self.counts.add(crate::walk::LIVE, "list_read", 1);
                    row.maps().iter().any(|m| ids.contains(*m))
                };
            if !wanted {
                continue;
            }
            self.count("stat", 1);
            self.count("stat_compare", 1);
            let at = abs(&self.root, &path);
            let now = stat::stat(&at);
            let row = &self.table.rows[&path];
            if row.kind.is_font() {
                if now != row.stat {
                    fonts_moved = true;
                    self.remove_named(&path, "the font set changed")?;
                }
                continue;
            }
            if now == row.stat && now.settled_before(row.hashed) {
                self.held.insert(path);
                continue;
            }
            let was = row.digest.clone();
            let (d, blocks) = digest(&at);
            self.count("hash_block", usize::try_from(blocks).unwrap_or(usize::MAX));
            self.count("digest_compare", 1);
            if d != was {
                self.remove_named(&path, &format!("{path} changed"))?;
            }
            let clock = self.clock;
            let row = self
                .table
                .rows
                .get_mut(&path)
                .unwrap_or_else(|| unreachable!("a path of the table"));
            if d != row.digest {
                row.clear();
            }
            (row.stat, row.hashed, row.digest) = (now, clock, d);
            self.table.changed = true;
            self.held.insert(path);
        }
        if fonts_moved {
            self.table.rows.retain(|_, r| !r.kind.is_font());
            self.table.changed = true;
        }
        Ok(())
    }

    /// Every entry the row at `path` names removed (its list read), durably, with why.
    fn remove_named(&mut self, path: &str, why: &str) -> Result<(), String> {
        self.count("list_read", 1);
        let maps: Vec<String> = self.table.rows[path]
            .maps()
            .iter()
            .map(|m| (*m).to_owned())
            .collect();
        for m in maps {
            self.remove_entry(&m, why)?;
        }
        Ok(())
    }
}
