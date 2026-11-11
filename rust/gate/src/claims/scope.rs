//! Every unit in scope at a tree (`tools/claims.all_units`, feature 449 T82): the hamlet scope's `.py` units, every Rust phase's, the
//! `.py` units claimed outside the scope, then the procedure sections - in the Python's order, which the form problems print in.
//!
//! THE `.py` HALF STAYS PYTHON (`ask:449-T82-claims`): a `.py` unit's core is CPython's `ast.dump`, so `tools/claims.py_units` is asked
//! through `scripts/bundle_door.py`, and only when a file it reads changed: its answer is kept under the clone's common git directory,
//! keyed by the reader's code and every `.py` file under `l7r/diagram/` (its read set, measured in T82's plan), so a run with no `.py`
//! change starts no Python. A tree with no `.py` file there asks nothing: the reader's answer is empty.

use std::path::{Path, PathBuf};

use l7r_guard::shared::sha256;
use serde_json::{json, Map, Value};

use super::units::{all_rust_units, doc_units, from_json, rel, rglob, Pair, PROCEDURES};
use crate::record::bundle::door::Runner;
use crate::record::repo::{read_text, Fail};

/// The kept answers' file under the common git directory's `l7r-cache/`.
const KEPT: &str = "claims-py-units.json";
/// How many answers the file keeps: a gate reads the head and the merge base, a session a head that moves.
const KEEP: usize = 4;

/// What reaches the Python half: the runner, started on the first miss, and the kept answers.
pub(crate) struct Reader {
    tree: PathBuf,
    door: Option<Runner>,
    kept: Map<String, Value>,
    path: Option<PathBuf>,
    fresh: Vec<String>,
    added: bool,
}

/// `L7R_CACHE_OFF` set to anything but empty or `0`.
pub(crate) fn cache_off() -> bool {
    std::env::var("L7R_CACHE_OFF").is_ok_and(|v| !v.is_empty() && v != "0")
}

impl Reader {
    /// The reader of the scripts under `tree`, its answers kept in `keep`'s common git directory (none outside a repository, or with the cache off).
    pub(crate) fn new(tree: &Path, keep: &Path) -> Self {
        let path = (!cache_off())
            .then(|| crate::codeid::common_git_dir(keep))
            .flatten()
            .map(|d| d.join("l7r-cache").join(KEPT));
        let kept = path
            .as_deref()
            .and_then(|p| std::fs::read_to_string(p).ok())
            .and_then(|t| serde_json::from_str::<Value>(&t).ok())
            .and_then(|v| v.as_object().cloned())
            .unwrap_or_default();
        Self {
            tree: tree.to_path_buf(),
            door: None,
            kept,
            path,
            fresh: Vec::new(),
            added: false,
        }
    }

    /// The runner, started on its first verb.
    pub(crate) fn door(&mut self) -> &mut Runner {
        let tree = self.tree.clone();
        self.door.get_or_insert_with(|| Runner::new(&tree))
    }

    /// A verb of the runner.
    pub(crate) fn ask(&mut self, verb: &str, args: &Value) -> Result<Value, Fail> {
        self.door().ask(verb, args)
    }

    fn key(
        &self,
        skill: &Path,
        every: bool,
        stars: bool,
        files: &[PathBuf],
    ) -> Result<String, Fail> {
        let mut h: Vec<u8> = Vec::new();
        for code in ["l7r/diagram/tools/claims.py", "scripts/bundle_door.py"] {
            h.extend(std::fs::read(self.tree.join(code)).unwrap_or_default());
            h.push(0);
        }
        h.extend(format!("{every}\0{stars}\0").as_bytes());
        for p in files {
            h.extend(rel(p, skill).as_bytes());
            h.push(0);
            h.extend(std::fs::read(p).map_err(|e| format!("{}: {e}", p.display()))?);
            h.push(0);
        }
        Ok(sha256::hex(&h))
    }

    /// (the hamlet scope's `.py` units, those claimed outside it) at `skill`, from the kept answer or the runner.
    pub(crate) fn py_units(
        &mut self,
        skill: &Path,
        every: bool,
        stars: bool,
    ) -> Result<(Vec<Pair>, Vec<Pair>), Fail> {
        let files: Vec<PathBuf> = rglob(&skill.join("l7r").join("diagram"), ".py")
            .into_iter()
            .filter(|p| !p.components().any(|c| c.as_os_str() == "__pycache__"))
            .collect();
        if files.is_empty() {
            return Ok((Vec::new(), Vec::new()));
        }
        let key = self.key(skill, every, stars, &files)?;
        let answer = if let Some(v) = self.kept.get(&key) {
            v.clone()
        } else {
            let v = self.ask(
                "claims_py_units",
                &json!([skill.to_string_lossy(), every, stars]),
            )?;
            self.kept.insert(key.clone(), v.clone());
            self.added = true;
            v
        };
        self.fresh.retain(|k| *k != key);
        self.fresh.push(key);
        let half = |i: usize| -> Vec<Pair> {
            answer
                .get(i)
                .and_then(Value::as_array)
                .map(|a| a.iter().map(from_json).collect())
                .unwrap_or_default()
        };
        Ok((half(0), half(1)))
    }

    /// The kept answers written back: this run's, then those kept before, at most [`KEEP`], by atomic rename.
    pub(crate) fn save(&mut self) {
        let Some(path) = self.path.clone() else {
            return;
        };
        let mut order: Vec<String> = self.fresh.iter().rev().cloned().collect();
        order.extend(
            self.kept
                .keys()
                .filter(|k| !self.fresh.contains(k))
                .cloned(),
        );
        order.truncate(KEEP);
        let out: Map<String, Value> = order
            .iter()
            .filter_map(|k| Some((k.clone(), self.kept.get(k)?.clone())))
            .collect();
        if !self.added {
            return;
        }
        self.added = false;
        let _ = std::fs::create_dir_all(path.parent().unwrap_or(Path::new(".")));
        let tmp = path.with_extension(format!("{}.tmp", std::process::id()));
        if std::fs::write(&tmp, Value::Object(out.clone()).to_string()).is_ok() {
            let _ = std::fs::rename(&tmp, &path);
        }
        self.kept = out;
    }
}

impl Drop for Reader {
    fn drop(&mut self) {
        self.save();
    }
}

/// Every unit in scope at `skill` with its module's errors (`all_units`); paths repository-relative under `repo_prefix`.
pub(crate) fn all_units(
    reader: &mut Reader,
    skill: &Path,
    every: bool,
    stars: bool,
) -> Result<Vec<Pair>, Fail> {
    let (inside, outside) = reader.py_units(skill, every, stars)?;
    let mut out = inside;
    out.extend(all_rust_units(skill, "")?);
    out.extend(outside);
    for (doc, tops) in PROCEDURES {
        let p = skill.join(doc);
        if !p.is_file() {
            continue;
        }
        let text = read_text(&p)?;
        out.extend(
            doc_units(&text, doc, tops)
                .into_iter()
                .map(|u| (u, Vec::new())),
        );
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
