//! Hashing a set of the repository's files by what runs (feature 449 T72): the walk both `state::tooling_hash` and `config_hash` make, and what decides how the gate's tests run. A `.py` file's semantic bytes are
//! Python's own `ast.dump`, kept by blob under the git directory and asked of `codeid.py` once a run only for those it lacks (`ask:449-T062-py-id`, FR-006); the hashes equal the ones `state.py` and `gate_config.py` wrote, so a recorded tooling hash still reads.

use std::path::{Path, PathBuf};
use std::process::Command;

use fancy_regex::Regex;
use l7r_guard::shared::sha256;

use crate::codeid::{self, stated};

/// The machinery of the gate itself; a change here plans a full run (feature 415 plan D3).
const MACHINERY: [&str; 5] = [
    "l7r/diagram/ci",
    "l7r/diagram/pipeline",
    "l7r/diagram/_invocation.py",
    "tests/conftest.py",
    "tests/_scope.py",
];
/// The pinned lockfiles; their `.in` sources are not.
const LOCKFILES: [&str; 2] = ["requirements.txt", "requirements-dev.txt"];
/// The Makefile targets whose recipes run the gate's test phase.
const TEST_TARGETS: [&str; 2] = ["test", "test-full"];

fn walk(dir: &Path, into: &mut Vec<PathBuf>) {
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let path = entry.path();
        // a link to a directory is an entry, not a directory to descend (`rglob`'s rule)
        let descend = entry.file_type().is_ok_and(|t| t.is_dir());
        into.push(path.clone());
        if descend {
            walk(&path, into);
        }
    }
}

/// Each of `rels`: a directory's whole tree sorted as paths, or the path itself, in the order given.
pub(crate) fn under_each(root: &Path, rels: &[&str]) -> Vec<PathBuf> {
    let mut files = Vec::new();
    for rel in rels {
        let path = root.join(rel);
        if path.is_dir() {
            let mut found = Vec::new();
            walk(&path, &mut found);
            found.sort();
            files.extend(found);
        } else {
            files.push(path);
        }
    }
    files
}

fn is_python(path: &Path) -> bool {
    path.extension().is_some_and(|e| e == "py")
}

fn counted(path: &Path) -> bool {
    path.is_file() && !path.components().any(|c| c.as_os_str() == "__pycache__")
}

/// A kept semantic form goes after a week unused, so that a tree's edits do not pile up under the git directory.
const KEPT_FOR: std::time::Duration = std::time::Duration::from_secs(7 * 24 * 60 * 60);

/// Where each semantic form is kept, by raw blob id, one directory for each docstring rule; None outside a repository, where nothing is kept.
fn kept_dir(root: &Path, keep: bool) -> Option<PathBuf> {
    codeid::common_git_dir(root).map(|d| {
        d.join("semantic-dumps")
            .join(if keep { "keep" } else { "strip" })
    })
}

/// Forms no file of this run named and not touched for `KEPT_FOR`.
fn prune(dir: &Path, used: &std::collections::BTreeSet<String>) {
    let now = std::time::SystemTime::now();
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let name = entry.file_name().to_string_lossy().into_owned();
        let age = entry
            .metadata()
            .and_then(|m| m.modified())
            .map(|at| now.duration_since(at).unwrap_or_default());
        if !used.contains(&name) && age.is_ok_and(|a| a > KEPT_FOR) {
            let _ = std::fs::remove_file(entry.path());
        }
    }
}

/// Python's answer for `files`, framed `<length>\n<bytes>`, in one process.
fn asked(
    root: &Path,
    files: &[&PathBuf],
    keep: bool,
    python: &str,
) -> Result<Vec<Vec<u8>>, String> {
    if files.is_empty() {
        return Ok(Vec::new());
    }
    let script = codeid::script(root);
    let done = stated(
        Command::new(python)
            .arg(&script)
            .arg("--semantic")
            .arg(if keep { "keep" } else { "strip" })
            .args(files)
            .output(),
        python,
    )?;
    if !done.status.success() {
        return Err(format!(
            "{} could not read the .py files: {}",
            script.display(),
            String::from_utf8_lossy(&done.stderr).trim()
        ));
    }
    let mut out = Vec::with_capacity(files.len());
    let mut rest = done.stdout.as_slice();
    while !rest.is_empty() {
        let line = rest
            .iter()
            .position(|b| *b == b'\n')
            .ok_or("codeid.py framed a file badly")?;
        let size: usize = String::from_utf8_lossy(&rest[..line])
            .parse()
            .map_err(|_| "codeid.py framed a file badly")?;
        let body = rest
            .get(line + 1..line + 1 + size)
            .ok_or("codeid.py cut a file short")?;
        out.push(body.to_vec());
        rest = &rest[line + 1 + size..];
    }
    if out.len() == files.len() {
        Ok(out)
    } else {
        Err("codeid.py answered short".to_owned())
    }
}

/// The semantic bytes of each `.py` file named: the kept form of its blob, Python asked once for those it lacks (FR-006), so an unchanged tree starts no Python. A form is written whole and renamed into place, since a
/// reader must never hash a torn one.
fn semantic_bytes(
    root: &Path,
    files: &[&PathBuf],
    keep: bool,
    python: &str,
) -> Result<Vec<Vec<u8>>, String> {
    let dir = kept_dir(root, keep);
    let mut ids = Vec::with_capacity(files.len());
    let mut forms: Vec<Option<Vec<u8>>> = Vec::with_capacity(files.len());
    for path in files {
        let id = codeid::git_blob_id(&stated(std::fs::read(path), &path.to_string_lossy())?);
        forms.push(dir.as_ref().and_then(|d| std::fs::read(d.join(&id)).ok()));
        ids.push(id);
    }
    let lacking: Vec<usize> = (0..files.len()).filter(|&i| forms[i].is_none()).collect();
    let misses: Vec<&PathBuf> = lacking.iter().map(|&i| files[i]).collect();
    let answers = asked(root, &misses, keep, python)?;
    if let Some(d) = dir.as_ref() {
        let _ = std::fs::create_dir_all(d);
        for (&at, form) in lacking.iter().zip(&answers) {
            let tmp = d.join(format!("{}.{}.tmp", ids[at], std::process::id()));
            if std::fs::write(&tmp, form).is_ok() {
                let _ = std::fs::rename(&tmp, d.join(&ids[at]));
            }
        }
        prune(d, &ids.iter().cloned().collect());
    }
    for (at, form) in lacking.into_iter().zip(answers) {
        forms[at] = Some(form);
    }
    Ok(forms.into_iter().flatten().collect())
}

/// Every counted file's repository-relative path and its content, joined with no separator, as the Python's `h.update` calls made them.
pub(crate) fn content_hash(
    root: &Path,
    files: &[PathBuf],
    keep: bool,
    python: &str,
) -> Result<Vec<u8>, String> {
    let counted_files: Vec<&PathBuf> = files.iter().filter(|p| counted(p)).collect();
    let py: Vec<&PathBuf> = counted_files
        .iter()
        .copied()
        .filter(|p| is_python(p))
        .collect();
    let mut dumps = semantic_bytes(root, &py, keep, python)?.into_iter();
    let mut data = Vec::new();
    for path in counted_files {
        data.extend_from_slice(
            path.strip_prefix(root)
                .unwrap_or(path)
                .to_string_lossy()
                .as_bytes(),
        );
        if is_python(path) {
            data.extend(dumps.next().ok_or("codeid.py answered short")?);
        } else {
            data.extend(stated(std::fs::read(path), &path.to_string_lossy())?);
        }
    }
    Ok(data)
}

fn help_stripped(line: &str) -> &str {
    line.split_once("##")
        .map_or(line, |(head, _)| head.trim_end())
}

/// The Makefile's test configuration: each line of the test targets' recipes, then every definition of every variable they reference, closed over the variables those reference, in file order.
fn makefile_test_config(text: &str) -> String {
    let var_def = Regex::new(
        r"^(?:[\w.-]+:\s*)?(?:export\s+|override\s+)?([A-Z_][A-Z0-9_]*)\s*(?::=|\?=|\+=|=)",
    )
    .unwrap();
    let reference = Regex::new(r"\$[({]([A-Z_][A-Z0-9_]*)[)}]").unwrap();
    let target = Regex::new(r"^([\w.-]+)\s*:(?!=)").unwrap();
    let group = |re: &Regex, line: &str| {
        re.captures(line)
            .ok()
            .flatten()
            .and_then(|c| c.get(1))
            .map(|m| m.as_str().to_owned())
    };
    let refs = |line: &str| {
        reference
            .captures_iter(line)
            .flatten()
            .filter_map(|c| c.get(1).map(|m| m.as_str().to_owned()))
            .collect::<Vec<_>>()
    };
    let lines: Vec<&str> = text.lines().collect();
    let mut kept: Vec<&str> = Vec::new();
    let mut at = 0;
    while at < lines.len() {
        let line = lines[at];
        at += 1;
        if group(&target, line).is_some_and(|t| TEST_TARGETS.contains(&t.as_str()))
            && group(&var_def, line).is_none()
        {
            kept.push(help_stripped(line));
            while at < lines.len() && (lines[at].starts_with('\t') || lines[at].starts_with("##")) {
                if lines[at].starts_with('\t') {
                    kept.push(lines[at]);
                }
                at += 1;
            }
        }
    }
    let mut todo: Vec<String> = kept.iter().flat_map(|l| refs(l)).collect();
    let mut seen = std::collections::BTreeSet::new();
    while let Some(name) = todo.pop() {
        if seen.insert(name.clone()) {
            for line in lines
                .iter()
                .filter(|l| group(&var_def, l).as_ref() == Some(&name))
            {
                todo.extend(refs(help_stripped(line)));
            }
        }
    }
    kept.extend(
        lines
            .iter()
            .filter(|l| {
                group(&var_def, l).is_some_and(|n| seen.contains(&n))
                    && !help_stripped(l).is_empty()
            })
            .copied(),
    );
    kept.join("\n")
}

/// `pyproject.toml`'s `[tool.pytest...]` and `[tool.coverage...]` tables, each with its lines.
fn pyproject_test_config(text: &str) -> String {
    let head = Regex::new(r"^\s*\[+\s*([^\]]+?)\s*\]+").unwrap();
    let mut keep = false;
    let mut out = Vec::new();
    for line in text.lines() {
        if let Some(name) = head.captures(line).ok().flatten().and_then(|c| c.get(1)) {
            keep = name.as_str().starts_with("tool.pytest")
                || name.as_str().starts_with("tool.coverage");
        }
        if keep {
            out.push(line);
        }
    }
    out.join("\n")
}

type Extract = fn(&str) -> String;

/// What decides how the gate's tests run (feature 415): the machinery by what runs, the lockfiles by bytes, and the two configurations; a missing file counts as empty.
fn config_hash(root: &Path, python: &str) -> Result<String, String> {
    let rels: Vec<&str> = MACHINERY.iter().chain(LOCKFILES.iter()).copied().collect();
    let mut data = content_hash(root, &under_each(root, &rels), false, python)?;
    let extracts: [(&str, Extract); 2] = [
        ("Makefile", makefile_test_config),
        ("pyproject.toml", pyproject_test_config),
    ];
    for (name, extract) in extracts {
        data.extend_from_slice(name.as_bytes());
        data.extend_from_slice(
            extract(&std::fs::read_to_string(root.join(name)).unwrap_or_default()).as_bytes(),
        );
    }
    Ok(sha256::hex(&data))
}

/// `l7r-gate config-hash`.
pub(crate) fn cli(args: &[String], root: &Path, python: &str) -> crate::Reply {
    if !args.is_empty() {
        return crate::Reply {
            stdout: String::new(),
            stderr: "usage: l7r-gate config-hash\n".to_owned(),
            code: 2,
        };
    }
    match config_hash(root, python) {
        Ok(hash) => crate::Reply {
            stdout: format!("{hash}\n"),
            stderr: String::new(),
            code: 0,
        },
        Err(why) => crate::Reply {
            stdout: String::new(),
            stderr: format!("l7r-gate config-hash: {why}\n"),
            code: 1,
        },
    }
}

#[cfg(test)]
mod tests;
