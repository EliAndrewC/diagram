//! `make map MAP=<folder|spec>` (feature 449 T221): one pool map - a hamlet, a generated compound or a hand sheet - drawn by its engine
//! through the generation cache ([`crate::cache`]), or served from it, and said: `CACHED`, `REGENERATED` (with why) or, a frozen legacy
//! exhibit, `FROZEN`. `MAP=--all` does every live map of the pool in one run (render-sync's, and the counting run's).
//!
//! THE ONE DRIVER: before T221 a map was its `.gen.py` (six of them, each calling `interactive/sheet.py`), run by `pipeline/regen.py`
//! under `gencache.py`'s key, and a hamlet was not a `make map` at all. Now the walk's kind names the engine and the spec - a hamlet's
//! `.spec.json`, a compound's `.compound.json`, a hand sheet's `.svg` - and nothing per map is code.
//!
//! The map is named by its folder (`pool/<tier>/<map>`), any file in it, or its bare name.
//!
//! Research: plumbing - NONE: finds a map and says what the cache did with it, deciding nothing about a place

use std::fmt::Write as _;
use std::path::Path;

use crate::cache::{self, engine::Binaries, Options, Outcome, Verdict};
use crate::counts::Counts;
use crate::walk::{walk, Kind, Map, Walk};

/// The map a target names: a folder or a file in one (from the root, or a path under it), or a bare name.
///
/// # Errors
/// No map folder of the walk is named.
pub fn resolve<'a>(root: &Path, w: &'a Walk, target: &str) -> Result<&'a Map, String> {
    let trimmed = target.trim_end_matches('/');
    let at = Path::new(trimmed);
    let at = at.strip_prefix(root).unwrap_or(at);
    let found = if trimmed.contains('/') {
        let full = root.join(at);
        let folder = if full.is_dir() {
            at
        } else {
            at.parent().unwrap_or(at)
        };
        w.maps.iter().find(|m| Path::new(&m.rel()) == folder)
    } else {
        w.folder(trimmed)
    };
    found.ok_or_else(|| {
        format!(
            "make map: no pool map is named {target} - name its folder (MAP=pool/<tier>/<map>), a file in it, or its name; `l7r-gate pool list` lists them"
        )
    })
}

/// An outcome's line on stdout, or (failed) on stderr.
fn said(o: &Outcome, out: &mut String, err: &mut String) {
    err.push_str(&o.said);
    let _ = match &o.verdict {
        Verdict::Cached => writeln!(out, "CACHED       {}", o.map),
        Verdict::Regenerated(why) | Verdict::Unpublished(why) => {
            writeln!(out, "REGENERATED  {} - {why}", o.map)
        }
        Verdict::Frozen => writeln!(
            out,
            "FROZEN       {} - a frozen legacy exhibit (the GM, 2026-08-16): never regenerated; its fix is conversion into the live pool",
            o.map
        ),
        Verdict::Failed(why) => writeln!(err, "make map: {}: {why}", o.map),
    };
}

/// `map <target>...` or `map --all`, with the engines' binaries from `binaries`: each map's line, exit 1 where one failed.
#[must_use]
pub fn cli(root: &Path, args: &[&str], binaries: &mut dyn Binaries, opts: Options) -> crate::Said {
    let w = walk(root);
    let (maps, every): (Vec<Map>, bool) = if args == ["--all"] {
        (
            w.in_tree(crate::LIVE)
                .filter(|m| m.kind.is_live())
                .cloned()
                .collect(),
            true,
        )
    } else if args.is_empty() || args.iter().any(|a| a.starts_with("--")) {
        return (String::new(), USAGE.to_owned(), 2);
    } else {
        let mut maps = Vec::new();
        for a in args {
            match resolve(root, &w, a) {
                Ok(m) if m.kind == Kind::Report => {
                    return (String::new(), format!("make map: {} holds no map the pool walk can classify (`l7r-gate pool index` names why)\n", m.rel()), 1);
                }
                Ok(m) => maps.push(m.clone()),
                Err(why) => return (String::new(), format!("{why}\n"), 1),
            }
        }
        (maps, false)
    };
    let mut counts = Counts::default();
    let outcomes = match cache::run(root, &maps, every, binaries, &mut counts, opts) {
        Ok(o) => o,
        Err(why) => {
            return (
                String::new(),
                format!("make map: the generation cache: {why}\n"),
                1,
            )
        }
    };
    let (mut out, mut err) = (String::new(), String::new());
    for o in &outcomes {
        said(o, &mut out, &mut err);
    }
    let failed = outcomes
        .iter()
        .any(|o| matches!(o.verdict, Verdict::Failed(_)));
    (out, err, i32::from(failed))
}

/// The command's usage.
pub const USAGE: &str =
    "usage: pool map <pool/<tier>/<map> | a file in it | its name>... | pool map --all\n";

#[cfg(test)]
mod tests;
