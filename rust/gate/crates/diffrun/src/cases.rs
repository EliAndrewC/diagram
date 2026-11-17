//! The cases file (feature 449 T161): the two sides, the world, the normalizations and the cases, read from JSON and checked whole before
//! anything runs - a refusal names the field, so a harness is fixed before an hour of running, not after.
//!
//! The format is `docs/diff-run.md`'s; every path is read relative to `root` (the cases file's directory unless given) after `{NAME}`
//! templates are filled from `vars`.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use fancy_regex::Regex;
use serde_json::{Map, Value};

/// Where a normalization applies: a step's output, a file's content, a file's name.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Target {
    Stdout,
    Stderr,
    Files,
    Names,
}

/// What a normalization does: a regex and its replacement, or the text split at a separator and its pieces sorted (a server's log, a
/// set of commits written by concurrent lanes: run-to-run order the harnesses of T146 sorted by hand).
pub enum Kind {
    Replace(Regex, String),
    Sort(Regex),
}

/// One named normalization.
pub struct Norm {
    pub name: String,
    pub kind: Kind,
    pub on: Vec<Target>,
    /// Only files whose (raw, world-relative) name matches; `None` every file.
    pub only_files: Option<Regex>,
    /// Applied only to the cases that name it in their `norms` (T146's `sort_stdout`).
    pub opt_in: bool,
    /// Its definition as written, for the keys.
    pub raw: Value,
}

/// A fingerprint entry: a path's content, or a git revision's tree (the old side's Python at its revision, read without a checkout).
pub enum Print {
    Path(String),
    Git { repo: String, rev: String },
}

/// One side: its command template (`{CMD}` in a step), its environment and variables, the commands that make its binaries current
/// before anything runs, and the files it runs from.
pub struct Side {
    pub label: String,
    pub cmd: Vec<String>,
    pub env: Map<String, Value>,
    pub vars: BTreeMap<String, String>,
    pub build: Vec<Vec<String>>,
    pub fingerprint: Vec<Print>,
    /// The definition without its fingerprint list, for the keys: a case that declares its sources is keyed on those, so a change to
    /// the side's fingerprint list must not move it.
    pub raw: Value,
}

/// One step: its argv, and whether its output is compared (a `between` step of T146's sets the world up mid-case and is not).
pub struct Step {
    pub argv: Vec<String>,
    pub compare: bool,
}

/// One case.
pub struct Case {
    pub name: String,
    pub steps: Vec<Step>,
    pub env: Map<String, Value>,
    pub inputs: Vec<String>,
    /// The new side's declared sources; `None` keys the new side on its whole fingerprint.
    pub sources: Option<Vec<String>>,
    pub files: Option<Vec<String>>,
    pub norms: Vec<String>,
    /// The definition without `sources`, for the old side's key: tightening a declaration never reruns an old side.
    pub raw: Value,
}

/// A named extra output beside the world's files: a file anywhere, or a command's stdout (a git log, a status).
pub struct Extra {
    pub name: String,
    pub from: From,
}

/// Where an extra is read from.
pub enum From {
    Path(String),
    Cmd(Vec<String>),
}

/// The world's checkout (feature 449 T169), made by the runner before `world.setup`: a clone of `repo` at `rev` into `{WORLD}/<into>`,
/// limited to the `sparse` paths where any are named. `rev` `WORKTREE` is the repository's `HEAD` with its uncommitted changes and
/// untracked files laid over it - the new side of a port whose work is not yet committed.
pub struct Checkout {
    pub repo: String,
    pub rev: String,
    pub into: String,
    pub sparse: Vec<String>,
}

/// The worlds a run builds (feature 449 T169, the plan review's ruling): `Sparse` - `world.checkout.sparse` honored - for iterating
/// (an incremental, `--only` or `--twice` run); `Whole` for a `--verify` or `--all` run, whose report is the record a plan cites. WHY: a
/// path list too narrow fails both sides alike, which the comparison reads as agreement - a false pass in the comparison FR-002 rests on -
/// so the record is never built on a sparse world.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Worlds {
    Whole,
    Sparse,
}

/// The whole cases file.
pub struct Cases {
    pub file: PathBuf,
    pub root: PathBuf,
    pub state: PathBuf,
    pub vars: BTreeMap<String, String>,
    pub setup: Vec<Vec<String>>,
    pub checkout: Option<Checkout>,
    pub cwd: String,
    pub wrap: Vec<String>,
    pub files: Vec<String>,
    pub ignore: Vec<String>,
    pub extras: Vec<Extra>,
    pub env: Map<String, Value>,
    pub env_drop: Vec<String>,
    pub timeout_s: u64,
    pub max_text: usize,
    pub inputs: Vec<String>,
    pub norms: Vec<Norm>,
    pub old: Side,
    pub new: Side,
    pub cases: Vec<Case>,
    /// The world's definition as written, for both keys.
    pub world_raw: Value,
}

impl Cases {
    /// Whether the world's checkout names a sparse path list: only then do a run's worlds differ by its kind.
    #[must_use]
    pub fn declares_sparse(&self) -> bool {
        self.checkout.as_ref().is_some_and(|c| !c.sparse.is_empty())
    }
}

/// `{NAME}` filled from `vars` until nothing more changes (a variable may name another); an unknown name stays as written.
#[must_use]
pub fn fill(text: &str, vars: &BTreeMap<String, String>) -> String {
    let mut out = text.to_owned();
    for _ in 0..8 {
        let before = out.clone();
        for (k, v) in vars {
            out = out.replace(&format!("{{{k}}}"), v);
        }
        if out == before {
            break;
        }
    }
    out
}

fn strings(v: Option<&Value>, what: &str) -> Result<Vec<String>, String> {
    match v {
        None => Ok(Vec::new()),
        Some(Value::Array(items)) => items
            .iter()
            .map(|i| {
                i.as_str()
                    .map(str::to_owned)
                    .ok_or_else(|| format!("{what}: every item is a string"))
            })
            .collect(),
        Some(_) => Err(format!("{what}: a list of strings")),
    }
}

fn argvs(v: Option<&Value>, what: &str) -> Result<Vec<Vec<String>>, String> {
    match v {
        None => Ok(Vec::new()),
        Some(Value::Array(items)) => items.iter().map(|i| strings(Some(i), what)).collect(),
        Some(_) => Err(format!("{what}: a list of argv lists")),
    }
}

fn object(v: Option<&Value>, what: &str) -> Result<Map<String, Value>, String> {
    match v {
        None => Ok(Map::new()),
        Some(Value::Object(m)) => {
            if m.values().all(|x| x.is_string() || x.is_null()) {
                Ok(m.clone())
            } else {
                Err(format!("{what}: each value a string, or null to unset"))
            }
        }
        Some(_) => Err(format!("{what}: an object")),
    }
}

fn string_map(v: Option<&Value>, what: &str) -> Result<BTreeMap<String, String>, String> {
    let m = object(v, what)?;
    Ok(m.iter()
        .map(|(k, x)| (k.clone(), x.as_str().unwrap_or_default().to_owned()))
        .collect())
}

fn regex(text: &str, what: &str) -> Result<Regex, String> {
    Regex::new(text).map_err(|e| format!("{what}: {e}"))
}

fn norm(v: &Value) -> Result<Norm, String> {
    let name = v["name"]
        .as_str()
        .ok_or("normalizations: each has a name")?
        .to_owned();
    let what = format!("normalization {name}");
    let kind = match (v["regex"].as_str(), v["sort"].as_str()) {
        (Some(r), None) => Kind::Replace(
            regex(r, &what)?,
            v["replace"]
                .as_str()
                .map_or_else(|| format!("<{name}>"), str::to_owned),
        ),
        (None, Some(s)) => Kind::Sort(regex(s, &what)?),
        _ => return Err(format!("{what}: exactly one of `regex` or `sort`")),
    };
    let on = match strings(v.get("on"), &what)? {
        on if on.is_empty() => vec![Target::Stdout, Target::Stderr, Target::Files, Target::Names],
        on => on
            .iter()
            .map(|t| match t.as_str() {
                "stdout" => Ok(Target::Stdout),
                "stderr" => Ok(Target::Stderr),
                "files" => Ok(Target::Files),
                "names" => Ok(Target::Names),
                other => Err(format!(
                    "{what}: `on` takes stdout, stderr, files, names - not {other}"
                )),
            })
            .collect::<Result<_, _>>()?,
    };
    let only_files = v["where"].as_str().map(|w| regex(w, &what)).transpose()?;
    Ok(Norm {
        name,
        kind,
        on,
        only_files,
        opt_in: v["opt_in"].as_bool().unwrap_or(false),
        raw: v.clone(),
    })
}

fn print(v: &Value) -> Result<Print, String> {
    match v {
        Value::String(p) => Ok(Print::Path(p.clone())),
        Value::Object(m) => match (
            m.get("git").and_then(Value::as_str),
            m.get("rev").and_then(Value::as_str),
        ) {
            (Some(repo), Some(rev)) => Ok(Print::Git {
                repo: repo.to_owned(),
                rev: rev.to_owned(),
            }),
            _ => Err(
                "fingerprint: an object entry is {\"git\": <repository>, \"rev\": <revision>}"
                    .to_owned(),
            ),
        },
        _ => Err("fingerprint: a path or {\"git\", \"rev\"}".to_owned()),
    }
}

fn side(v: &Value, which: &str) -> Result<Side, String> {
    let what = format!("sides.{which}");
    if !v.is_object() {
        return Err(format!("{what}: the side is missing"));
    }
    let cmd = strings(v.get("cmd"), &format!("{what}.cmd"))?;
    let fingerprint = match v.get("fingerprint") {
        Some(Value::Array(items)) if !items.is_empty() => {
            items.iter().map(print).collect::<Result<_, _>>()?
        }
        _ => {
            return Err(format!(
                "{what}.fingerprint: the files the side runs from, at least one"
            ))
        }
    };
    let mut raw = v.clone();
    if let Some(m) = raw.as_object_mut() {
        m.remove("fingerprint");
        m.remove("label");
    }
    Ok(Side {
        label: v["label"].as_str().unwrap_or(which).to_owned(),
        cmd,
        env: object(v.get("env"), &format!("{what}.env"))?,
        vars: string_map(v.get("vars"), &format!("{what}.vars"))?,
        build: argvs(v.get("build"), &format!("{what}.build"))?,
        fingerprint,
        raw,
    })
}

/// A path inside the world or the repository, as `checkout` takes one: relative, and never climbing out with `..`.
fn inside(path: &str) -> bool {
    !path.is_empty() && !path.starts_with('/') && !path.split('/').any(|p| p == "..")
}

fn checkout(v: &Value) -> Result<Checkout, String> {
    let what = "world.checkout";
    let text = |k: &str| {
        v.get(k)
            .and_then(Value::as_str)
            .map(str::to_owned)
            .ok_or_else(|| format!("{what}.{k}: a string - the checkout is {{\"repo\", \"rev\", \"into\", \"sparse\": [paths]}}"))
    };
    if !v.is_object() {
        return Err(format!(
            "{what}: an object {{\"repo\", \"rev\", \"into\", \"sparse\": [paths]}}"
        ));
    }
    let into = text("into")?;
    if !inside(&into) {
        return Err(format!(
            "{what}.into: a directory under {{WORLD}}, relative and without `..`, not {into:?}"
        ));
    }
    let sparse = strings(v.get("sparse"), &format!("{what}.sparse"))?;
    if let Some(bad) = sparse.iter().find(|p| !inside(p)) {
        return Err(format!(
            "{what}.sparse: each path relative to the repository, without `..`, not {bad:?}"
        ));
    }
    Ok(Checkout {
        repo: text("repo")?,
        rev: text("rev")?,
        into,
        sparse: sparse
            .iter()
            .map(|p| p.trim_end_matches('/').to_owned())
            .collect(),
    })
}

fn step(v: &Value, case: &str) -> Result<Step, String> {
    let what = format!("case {case}: a step");
    let (argv, compare) = match v {
        Value::Array(_) => (strings(Some(v), &what)?, true),
        Value::Object(m) => (
            strings(m.get("argv"), &what)?,
            m.get("compare").and_then(Value::as_bool).unwrap_or(true),
        ),
        _ => {
            return Err(format!(
                "{what} is an argv list or {{\"argv\", \"compare\"}}"
            ))
        }
    };
    if argv.is_empty() {
        return Err(format!("{what} has an empty argv"));
    }
    Ok(Step { argv, compare })
}

fn case(v: &Value, norms: &[Norm]) -> Result<Case, String> {
    let name = v["name"]
        .as_str()
        .ok_or("cases: each has a name")?
        .to_owned();
    let steps: Vec<Step> = match v.get("steps") {
        Some(Value::Array(items)) if !items.is_empty() => items
            .iter()
            .map(|s| step(s, &name))
            .collect::<Result<_, _>>()?,
        _ => return Err(format!("case {name}: `steps` is a non-empty list")),
    };
    let wanted = strings(v.get("norms"), &format!("case {name}.norms"))?;
    if let Some(unknown) = wanted.iter().find(|w| !norms.iter().any(|n| &n.name == *w)) {
        return Err(format!("case {name}: no normalization named {unknown}"));
    }
    let sources = match v.get("sources") {
        None => None,
        s => Some(strings(s, &format!("case {name}.sources"))?),
    };
    let files = match v.get("files") {
        None => None,
        f => Some(strings(f, &format!("case {name}.files"))?),
    };
    let mut raw = v.clone();
    if let Some(m) = raw.as_object_mut() {
        m.remove("sources");
    }
    Ok(Case {
        steps,
        env: object(v.get("env"), &format!("case {name}.env"))?,
        inputs: strings(v.get("inputs"), &format!("case {name}.inputs"))?,
        sources,
        files,
        norms: wanted,
        raw,
        name,
    })
}

/// The state directory beside a cases file: `<dir>/<stem>.diff-run/`.
#[must_use]
pub fn state_dir(file: &Path) -> PathBuf {
    let stem = file.file_stem().unwrap_or_default().to_string_lossy();
    file.with_file_name(format!("{stem}.diff-run"))
}

/// The cases file at `file`, read and checked.
///
/// # Errors
///
/// What is wrong with it, naming the field.
pub fn load(file: &Path) -> Result<Cases, String> {
    let text = std::fs::read_to_string(file).map_err(|e| format!("{}: {e}", file.display()))?;
    let v: Value = serde_json::from_str(&text).map_err(|e| format!("{}: {e}", file.display()))?;
    let base = file
        .parent()
        .filter(|p| !p.as_os_str().is_empty())
        .unwrap_or(Path::new("."))
        .to_path_buf();
    let base = std::fs::canonicalize(&base).unwrap_or(base);
    let root = v["root"]
        .as_str()
        .map_or_else(|| base.clone(), |r| base.join(r));
    let world = &v["world"];
    let setup = argvs(world.get("setup"), "world.setup")?;
    let checkout = world.get("checkout").map(checkout).transpose()?;
    if setup.is_empty() && checkout.is_none() {
        return Err("world.setup: the commands that build a world into the fresh directory {WORLD}, at least one (or a `world.checkout`)".to_owned());
    }
    let norms: Vec<Norm> = match v.get("normalizations") {
        None => Vec::new(),
        Some(Value::Array(items)) => items.iter().map(norm).collect::<Result<_, _>>()?,
        Some(_) => return Err("normalizations: a list".to_owned()),
    };
    let mut seen = std::collections::BTreeSet::new();
    if let Some(dup) = norms.iter().find(|n| !seen.insert(n.name.clone())) {
        return Err(format!("normalizations: {} is named twice", dup.name));
    }
    let extras = match world.get("extras") {
        None => Vec::new(),
        Some(Value::Array(items)) => items
            .iter()
            .map(|e| {
                let name = e["name"]
                    .as_str()
                    .ok_or("world.extras: each has a name")?
                    .to_owned();
                let from = match (e["path"].as_str(), e.get("cmd")) {
                    (Some(p), None) => From::Path(p.to_owned()),
                    (None, Some(c)) => {
                        From::Cmd(strings(Some(c), &format!("world.extras {name}.cmd"))?)
                    }
                    _ => {
                        return Err(format!(
                            "world.extras {name}: exactly one of `path` or `cmd`"
                        ))
                    }
                };
                Ok(Extra { name, from })
            })
            .collect::<Result<_, String>>()?,
        Some(_) => return Err("world.extras: a list".to_owned()),
    };
    let cases: Vec<Case> = match v.get("cases") {
        Some(Value::Array(items)) if !items.is_empty() => items
            .iter()
            .map(|c| case(c, &norms))
            .collect::<Result<_, _>>()?,
        _ => return Err("cases: a non-empty list".to_owned()),
    };
    let mut names = std::collections::BTreeSet::new();
    if let Some(dup) = cases.iter().find(|c| !names.insert(c.name.clone())) {
        return Err(format!("cases: {} is named twice", dup.name));
    }
    let files = strings(world.get("files"), "world.files")?;
    Ok(Cases {
        file: file.to_path_buf(),
        state: state_dir(&base.join(file.file_name().unwrap_or_default())),
        vars: string_map(v.get("vars"), "vars")?,
        setup,
        checkout,
        cwd: world["cwd"].as_str().unwrap_or("{WORLD}").to_owned(),
        wrap: strings(world.get("wrap"), "world.wrap")?,
        files: if files.is_empty() {
            vec![".".to_owned()]
        } else {
            files
        },
        ignore: strings(world.get("ignore"), "world.ignore")?,
        extras,
        env: object(world.get("env"), "world.env")?,
        env_drop: strings(world.get("env_drop_prefixes"), "world.env_drop_prefixes")?,
        timeout_s: world["timeout_s"].as_u64().unwrap_or(900),
        max_text: world["max_text_bytes"]
            .as_u64()
            .and_then(|n| usize::try_from(n).ok())
            .unwrap_or(5_000_000),
        inputs: strings(world.get("inputs"), "world.inputs")?,
        old: side(&v["sides"]["old"], "old")?,
        new: side(&v["sides"]["new"], "new")?,
        norms,
        cases,
        world_raw: world.clone(),
        root,
    })
}
