//! ONE MAP KEYED, AND DRAWN ON A MISS (feature 449 T221, the derivation's `key:` and `miss:` steps).
//!
//! The key: the entry's meta read, its engine id and picture switch compared with the run's, its spec held by its record (stat, or digest
//! on a moved stat), each artifact in the map's folder held by its record and linked back from the entry where it is not there - a HIT when
//! all held, the reads having been held by the table. A miss: the old entry removed, the spec hashed, the filesystem's clock taken, the
//! engine run into a staging folder, its reported reads held by the racy-file rule against that start, hashed, the key folded, each
//! artifact renamed into the entry and linked into the map's folder, the map added to its reads' rows, its meta written under a temporary
//! name the run renames after the table.
//!
//! Research: plumbing - NONE: the cache's bookkeeping, deciding nothing about a map

use std::path::{Path, PathBuf};

use serde_json::Value;

use super::engine::{self, Engine};
use super::entry::{self, Meta, Record};
use super::stat::{self, Stat};
use super::{at, digest, map_id, rel, spec_of, Outcome, Run, Verdict, STAGING};
use crate::walk::{Kind, Map, LIVE};

/// The marker whose mtime is the engine's start, in the staging folder.
const START: &str = ".engine-start";

/// The artifacts a kind owes: each a file name's ending, the picture's only where it is drawn.
fn owed(m: &Map, skip_render: bool) -> Vec<String> {
    let n = &m.name;
    let mut out = match m.kind {
        Kind::Hamlet => vec![".driver.svg".to_owned(), ".driver.json".to_owned()],
        Kind::Compound => vec![format!("{n}.svg"), format!("{n}.html")],
        _ => vec![format!("{n}.html")],
    };
    if m.kind.is_sheet() && !skip_render {
        out.push(format!("{n}.png"));
    }
    out
}

/// The nearest directory above `path` that stands, and whether it settled before `t0`: a file gone or never there was looked for in a
/// directory that did not change while the engine ran.
fn absence_settled(path: &Path, t0: i128) -> bool {
    path.ancestors()
        .skip(1)
        .map(stat::stat)
        .find(|s| *s != Stat::Absent)
        .is_none_or(|s| s.settled_before(t0))
}

/// The files the engine wrote in the staging folder: every one but the start marker and the hamlet's copy of its spec, by name.
fn staged(staging: &Path, staged_spec: &Path) -> std::io::Result<Vec<String>> {
    let mut out: Vec<String> = std::fs::read_dir(staging)?
        .flatten()
        .filter(|f| f.path() != staged_spec && f.file_name() != START)
        .map(|f| f.file_name().to_string_lossy().into_owned())
        .collect();
    out.sort();
    Ok(out)
}

impl Run<'_> {
    /// One map: frozen, failed, cached, or drawn.
    pub(super) fn map(&mut self, m: &Map) -> Result<Outcome, String> {
        let outcome = |verdict, said: String| Outcome {
            map: m.rel(),
            verdict,
            said,
        };
        // the legacy tree is frozen whatever its folders hold (Keep 6): an svg there in a declared tier is an exhibit, never drawn
        let e = Engine::of(m.kind).filter(|_| m.tree == LIVE);
        let Some(e) = e else {
            return Ok(outcome(
                if m.kind == Kind::Frozen || m.tree != LIVE {
                    Verdict::Frozen
                } else {
                    Verdict::Failed("its folder holds no map the pool walk can classify".to_owned())
                },
                String::new(),
            ));
        };
        let id = match self.id(e) {
            Ok(id) => id,
            Err(why) => return Ok(outcome(Verdict::Failed(why), String::new())),
        };
        match self.check(m, &id)? {
            None => Ok(outcome(Verdict::Cached, String::new())),
            Some(why) => {
                let (verdict, said) = self.draw(m, e, &id, why)?;
                Ok(outcome(verdict, said))
            }
        }
    }

    /// Why the map's entry cannot serve it, or None: a HIT.
    fn check(&mut self, m: &Map, id: &str) -> Result<Option<String>, String> {
        let key = map_id(m);
        if let Some(why) = self.removed.get(&key) {
            return Ok(Some(why.clone()));
        }
        let dir = self.entry_dir(&key);
        self.count("meta_read", 1);
        let Some(mut meta) = entry::read(&dir) else {
            return Ok(Some("no cache entry".to_owned()));
        };
        self.count("id_compare", 1);
        if meta.engine_id != id {
            return Ok(Some(format!("its engine ({}) changed", meta.engine)));
        }
        if meta.skip_render != self.opts.skip_render {
            return Ok(Some(
                "the picture switch (DIAGRAM_SKIP_RENDER) changed".to_owned(),
            ));
        }
        let spec = spec_of(m).unwrap_or_default();
        self.count("record", 1);
        self.count("stat", 1);
        self.count("stat_compare", 1);
        let now = stat::stat(&spec);
        if now != meta.spec.stat || !now.settled_before(meta.spec.hashed) {
            let (d, blocks) = digest(&spec);
            self.count("hash_block", usize::try_from(blocks).unwrap_or(usize::MAX));
            self.count("digest_compare", 1);
            if d != meta.spec.digest {
                return Ok(Some("its spec changed".to_owned()));
            }
            (meta.spec.stat, meta.spec.hashed) = (now, self.clock);
            self.count("rename", 1);
            entry::replace(&dir.join(entry::META), meta.json().as_bytes()).map_err(at(&dir))?;
        }
        for a in &meta.artifacts {
            self.count("record", 1);
            self.count("stat", 1);
            self.count("stat_compare", 1);
            let there = m.dir.join(&a.name);
            if a.is(&stat::stat(&there)) {
                continue;
            }
            let kept = dir.join(&a.name);
            self.count("stat", 1);
            self.count("stat_compare", 1);
            if !a.is(&stat::stat(&kept)) {
                return Ok(Some(format!(
                    "its entry's {} is not the one published",
                    a.name
                )));
            }
            self.count("link", 1);
            entry::link(&kept, &there).map_err(at(&there))?;
        }
        Ok(None)
    }

    /// The map drawn into a staging folder and, where nothing it read moved while it ran, published: its verdict and its engine's words.
    fn draw(
        &mut self,
        m: &Map,
        e: Engine,
        id: &str,
        why: String,
    ) -> Result<(Verdict, String), String> {
        let key = map_id(m);
        let dir = self.entry_dir(&key);
        self.remove_entry(&key, &why)?;
        let staging =
            self.dir
                .join(STAGING)
                .join(format!("{}--{}.{}", m.tier, m.name, std::process::id()));
        let io = at(&staging);
        if staging.exists() {
            std::fs::remove_dir_all(&staging).map_err(&io)?;
        }
        std::fs::create_dir_all(&staging).map_err(&io)?;
        let drawn = self.drawn(m, e, id, why, &staging, &dir);
        let _ = std::fs::remove_dir_all(&staging);
        drawn
    }

    /// [`Run::draw`]'s work, its staging folder made.
    fn drawn(
        &mut self,
        m: &Map,
        e: Engine,
        id: &str,
        why: String,
        staging: &Path,
        dir: &Path,
    ) -> Result<(Verdict, String), String> {
        let spec = spec_of(m).unwrap_or_default();
        let before = stat::stat(&spec);
        let Ok(bytes) = std::fs::read(&spec) else {
            return Ok((
                Verdict::Failed(format!("{} cannot be read", spec.display())),
                String::new(),
            ));
        };
        self.count(
            "hash_block",
            usize::try_from((bytes.len() as u64).div_ceil(engine::BLOCK)).unwrap_or(0),
        );
        let spec_digest = l7r_shared::sha256::hex(&bytes);
        let io = at(staging);
        let staged_spec = staging.join(spec.file_name().unwrap_or_default());
        let args = match m.kind {
            // the hamlet driver writes beside its spec: a copy of the bytes just hashed, drawn in the staging folder
            Kind::Hamlet => {
                std::fs::write(&staged_spec, &bytes).map_err(&io)?;
                vec![staged_spec.to_string_lossy().into_owned()]
            }
            kind => vec![
                if kind == Kind::Compound {
                    "compound"
                } else {
                    "hand-sheet"
                }
                .to_owned(),
                spec.to_string_lossy().into_owned(),
                "--out".to_owned(),
                staging.to_string_lossy().into_owned(),
            ],
        };
        let t0 = stat::fs_clock(&staging.join(START)).map_err(&io)?;
        let binary = self.paths.get(&e).cloned().unwrap_or_default();
        self.count("engine_run", 1);
        let ran = engine::run(&self.root, &binary, &args)?;
        let said = ran.stderr.clone();
        let reply: Value = serde_json::from_str(&ran.stdout).unwrap_or(Value::Null);
        let refused = match e {
            Engine::ModeA => reply.is_null() || reply.get("error").is_some(),
            Engine::Hamlet => ran.code != 0,
        };
        if refused {
            return Ok((
                Verdict::Failed(format!("its engine refused it (exit {})", ran.code)),
                said,
            ));
        }
        let artifacts = staged(staging, &staged_spec).map_err(&io)?;
        if ran.code != 0 {
            // a census that failed: the page shows what the census named, so it is linked into the folder, and nothing is published
            for name in &artifacts {
                entry::link(&staging.join(name), &m.dir.join(name)).map_err(&io)?;
            }
            return Ok((
                Verdict::Failed(format!("its census failed (exit {})", ran.code)),
                said,
            ));
        }
        if let Some(gone) = owed(m, self.opts.skip_render)
            .iter()
            .find(|end| !artifacts.iter().any(|a| a.ends_with(end.as_str())))
        {
            return Ok((Verdict::Failed(format!("its engine wrote no {gone}")), said));
        }
        let (reads, mut unsettled) = self.reported(&reply, &spec, t0);
        let now_spec = stat::stat(&spec);
        if now_spec != before || !now_spec.settled_before(t0) {
            unsettled = Some(rel(&self.root, &spec));
        }
        // linked into the folder whether published or not: the map as drawn is what its folder shows
        let names: Vec<(String, PathBuf)> = artifacts
            .iter()
            .map(|a| (a.clone(), staging.join(a)))
            .collect();
        if let Some(path) = unsettled {
            for (name, from) in &names {
                entry::link(from, &m.dir.join(name)).map_err(&io)?;
            }
            return Ok((
                Verdict::Unpublished(format!(
                    "{path} changed while its engine ran, so the entry is not cached - the next make map draws it again"
                )),
                said,
            ));
        }
        self.publish(m, e, id, (spec_digest, before, t0), &reads, &names, dir)?;
        Ok((Verdict::Regenerated(why), said))
    }

    /// The reads the engine reported (the spec apart), each stat-ed and its digest taken - a held row's where its stat stands, else the
    /// file's - and the first that may have changed while the engine ran (the racy-file rule against `t0`, the engine's start), or one the
    /// table cannot hold.
    fn reported(
        &mut self,
        reply: &Value,
        spec: &Path,
        t0: i128,
    ) -> (Vec<(String, Stat, String)>, Option<String>) {
        let mut reads: Vec<(String, Stat, String)> = Vec::new();
        let mut unsettled = None;
        for p in reply["reads"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(Value::as_str)
        {
            let path = PathBuf::from(p);
            let name = rel(&self.root, &path);
            if path == spec || reads.iter().any(|(n, _, _)| *n == name) {
                continue;
            }
            if !super::table::holdable(&name) {
                unsettled.get_or_insert(name.clone());
                continue;
            }
            self.count("stat", 1);
            let now = stat::stat(&path);
            let settled = match now {
                Stat::Absent => absence_settled(&path, t0),
                Stat::Present { .. } => now.settled_before(t0),
            };
            if !settled {
                unsettled.get_or_insert(name.clone());
            }
            let kept = self
                .table
                .rows
                .get(&name)
                .filter(|r| self.held.contains(&name) && r.stat == now);
            let d = if let Some(row) = kept {
                row.digest.clone()
            } else {
                let (d, blocks) = digest(&path);
                self.count("hash_block", usize::try_from(blocks).unwrap_or(usize::MAX));
                d
            };
            reads.push((name, now, d));
        }
        (reads, unsettled)
    }

    /// The drawn map published: its key folded, each artifact renamed into the entry and linked into the map's folder, its reads' rows
    /// keeping it, its meta written under a temporary name the run renames after the table.
    #[expect(
        clippy::too_many_arguments,
        reason = "the draw's pieces, each named where it was made"
    )]
    fn publish(
        &mut self,
        m: &Map,
        e: Engine,
        id: &str,
        (spec_digest, spec_stat, t0): (String, Stat, i128),
        reads: &[(String, Stat, String)],
        artifacts: &[(String, PathBuf)],
        dir: &Path,
    ) -> Result<(), String> {
        let key_text = {
            let mut parts = vec![
                id.to_owned(),
                self.opts.skip_render.to_string(),
                spec_digest.clone(),
            ];
            if m.kind.is_sheet() {
                parts.push(self.font_set_id());
            }
            let mut sorted: Vec<String> =
                reads.iter().map(|(p, _, d)| format!("{p}\t{d}")).collect();
            sorted.sort();
            self.count("key_fold", parts.len() + sorted.len());
            parts.extend(sorted);
            parts.join("\n")
        };
        let io = at(dir);
        std::fs::create_dir_all(dir).map_err(&io)?;
        let mut records = Vec::new();
        for (name, from) in artifacts {
            let to = dir.join(name);
            self.count("rename", 1);
            std::fs::rename(from, &to).map_err(&io)?;
            self.count("link", 1);
            entry::link(&to, &m.dir.join(name)).map_err(&io)?;
            records.push(entry::artifact(name, &to).map_err(&io)?);
        }
        let key = map_id(m);
        self.keep_rows(&key, reads, t0, m.kind.is_sheet())?;
        let meta = Meta {
            engine: e.word().to_owned(),
            engine_id: id.to_owned(),
            skip_render: self.opts.skip_render,
            spec: Record {
                path: rel(&self.root, &spec_of(m).unwrap_or_default()),
                stat: spec_stat,
                hashed: t0,
                digest: spec_digest,
            },
            artifacts: records,
            key: l7r_shared::sha256::hex(key_text.as_bytes()),
            reads: reads.len(),
        };
        self.count("record", 2 + artifacts.len());
        let at = dir.join(entry::META);
        let tmp = entry::temp_beside(&at);
        std::fs::write(&tmp, meta.json()).map_err(&io)?;
        std::fs::File::open(&tmp)
            .and_then(|f| f.sync_all())
            .map_err(&io)?;
        self.pending.push((tmp, at));
        Ok(())
    }
}
