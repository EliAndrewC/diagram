//! The two keys of a case (feature 449 T161's plan, "Each side of a case is kept on its own key"): a fix to the port reruns what it
//! could change and nothing else.
//!
//! - THE OLD SIDE'S KEY: the world's definition, the old side's definition, the case's (its `sources` left out), the normalizations that
//!   apply to it, the content of the inputs it declares, and the old side's fingerprint. A fix to the port moves none of these, so the
//!   old side's recorded result stands across every rerun of a task.
//! - THE NEW SIDE'S KEY: the same with the new side's definition, and in place of the whole new fingerprint the content of the source
//!   paths the case declares it exercises; a case that declares none is keyed on the whole new fingerprint, as a rebuild then reruns it.
//!
//! A declared path that does not exist is refused, not hashed as absent: an absent path's hash never moves, so a misspelled
//! declaration would keep a stale result for good.

use std::collections::{BTreeMap, HashMap};
use std::path::{Path, PathBuf};

use l7r_shared::sha256::hex;
use serde_json::{json, Value};

use crate::cases::{fill, Case, Cases, Print, Side, Worlds};

/// The content hashes of one run, each path hashed once however many cases name it.
#[derive(Default)]
pub struct Hasher {
    cache: HashMap<PathBuf, String>,
}

fn walk(dir: &Path, rel: &str, out: &mut Vec<String>) -> std::io::Result<()> {
    let mut entries: Vec<_> = std::fs::read_dir(dir)?.collect::<Result<_, _>>()?;
    entries.sort_by_key(std::fs::DirEntry::file_name);
    for e in entries {
        let name = e.file_name().to_string_lossy().into_owned();
        // git's own store is not a source: the tree a revision names is hashed through `Print::Git` instead
        if name == ".git" {
            continue;
        }
        let path = e.path();
        let here = format!("{rel}{name}");
        let kind = e.file_type()?;
        if kind.is_symlink() {
            out.push(format!("L {here} {}", std::fs::read_link(&path)?.display()));
        } else if kind.is_dir() {
            walk(&path, &format!("{here}/"), out)?;
        } else {
            out.push(format!("F {here} {}", hex(&std::fs::read(&path)?)));
        }
    }
    Ok(())
}

impl Hasher {
    /// The content hash of a file or a directory (every file under it, by name and content, `.git` left out).
    ///
    /// # Errors
    ///
    /// A path that does not exist or cannot be read.
    pub fn path(&mut self, path: &Path) -> Result<String, String> {
        if let Some(h) = self.cache.get(path) {
            return Ok(h.clone());
        }
        let meta = std::fs::metadata(path).map_err(|e| {
            format!(
                "{}: {e} - a declared path must exist, or its key would never move",
                path.display()
            )
        })?;
        let h = if meta.is_dir() {
            let mut lines = Vec::new();
            walk(path, "", &mut lines).map_err(|e| format!("{}: {e}", path.display()))?;
            hex(lines.join("\n").as_bytes())
        } else {
            hex(&std::fs::read(path).map_err(|e| format!("{}: {e}", path.display()))?)
        };
        self.cache.insert(path.to_path_buf(), h.clone());
        Ok(h)
    }

    /// The tree `rev` names in `repo` (`git rev-parse <rev>^{tree}`): the content of a whole revision, read without a checkout.
    ///
    /// # Errors
    ///
    /// A revision git cannot name.
    pub fn git(&mut self, repo: &Path, rev: &str) -> Result<String, String> {
        let key = repo.join(format!("@{rev}"));
        if let Some(h) = self.cache.get(&key) {
            return Ok(h.clone());
        }
        let tree = std::process::Command::new("git")
            .arg("-C")
            .arg(repo)
            .args([
                "rev-parse",
                "--verify",
                "--quiet",
                &format!("{rev}^{{tree}}"),
            ])
            .output()
            .ok()
            .filter(|o| o.status.success())
            .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
            .filter(|t| !t.is_empty())
            .ok_or_else(|| format!("fingerprint: {rev} names no revision in {}", repo.display()))?;
        self.cache.insert(key, tree.clone());
        Ok(tree)
    }
}

/// The variables a declared path is filled from: the file's own `vars` and `{ROOT}`.
fn path_vars(cases: &Cases) -> BTreeMap<String, String> {
    let mut vars = cases.vars.clone();
    vars.insert("ROOT".to_owned(), cases.root.display().to_string());
    vars
}

/// A declared path as the runner reads it: its templates filled, relative to `root`.
#[must_use]
pub fn resolve(cases: &Cases, path: &str) -> PathBuf {
    cases.root.join(fill(path, &path_vars(cases)))
}

fn hashed(cases: &Cases, paths: &[String], h: &mut Hasher) -> Result<Value, String> {
    paths
        .iter()
        .map(|p| Ok(json!([p, h.path(&resolve(cases, p))?])))
        .collect::<Result<Vec<_>, String>>()
        .map(Value::Array)
}

fn fingerprint(cases: &Cases, side: &Side, h: &mut Hasher) -> Result<Value, String> {
    side.fingerprint
        .iter()
        .map(|p| match p {
            Print::Path(p) => Ok(json!([p, h.path(&resolve(cases, p))?])),
            Print::Git { repo, rev } => {
                Ok(json!({"git": repo, "rev": rev, "tree": h.git(&resolve(cases, repo), rev)?}))
            }
        })
        .collect::<Result<Vec<_>, String>>()
        .map(Value::Array)
}

/// The normalizations that apply to `case`: every one not opt-in, and the opt-in ones it names.
#[must_use]
pub fn applying<'c>(cases: &'c Cases, case: &Case) -> Vec<&'c crate::cases::Norm> {
    cases
        .norms
        .iter()
        .filter(|n| !n.opt_in || case.norms.contains(&n.name))
        .collect()
}

/// The world's definition as a key reads it: where a sparse path list is declared, the worlds the run builds with it (feature 449
/// T169), so no side kept from a sparse world stands in a run on whole ones, nor the reverse - and a whole world's key leaves the list
/// out, since it builds no differently for it. A file with no sparse list keys as before.
fn world_key(cases: &Cases, worlds: Worlds) -> Value {
    if !cases.declares_sparse() {
        return cases.world_raw.clone();
    }
    let mut world = cases.world_raw.clone();
    if worlds == Worlds::Whole {
        if let Some(co) = world.get_mut("checkout").and_then(Value::as_object_mut) {
            co.remove("sparse");
        }
    }
    json!({"definition": world, "worlds": if worlds == Worlds::Whole { "whole" } else { "sparse" }})
}

/// The case's (old key, new key), for a run that builds `worlds`.
///
/// # Errors
///
/// A declared path that does not exist, a revision git cannot name.
pub fn keys(
    cases: &Cases,
    case: &Case,
    h: &mut Hasher,
    worlds: Worlds,
) -> Result<(String, String), String> {
    let norms: Vec<&Value> = applying(cases, case).iter().map(|n| &n.raw).collect();
    let mut inputs = hashed(cases, &cases.inputs, h)?;
    if let (Value::Array(all), Value::Array(more)) = (&mut inputs, hashed(cases, &case.inputs, h)?)
    {
        all.extend(more);
    }
    // `v`: the runner's own result format; a change to the runner that changes what a side's kept result holds raises it, so every
    // kept result is run again rather than compared against one the old runner wrote
    let common = json!({"v": 1, "world": world_key(cases, worlds), "vars": cases.vars, "case": case.raw, "norms": norms, "inputs": inputs});
    let old = json!({"common": common, "side": cases.old.raw, "fingerprint": fingerprint(cases, &cases.old, h)?});
    let runs_from = match &case.sources {
        Some(sources) => json!({"sources": hashed(cases, sources, h)?}),
        None => json!({"fingerprint": fingerprint(cases, &cases.new, h)?}),
    };
    let new = json!({"common": common, "side": cases.new.raw, "runs_from": runs_from});
    Ok((
        hex(old.to_string().as_bytes()),
        hex(new.to_string().as_bytes()),
    ))
}
