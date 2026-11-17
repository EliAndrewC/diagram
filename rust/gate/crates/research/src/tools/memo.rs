//! `l7r-gate record check record|glossary` and `l7r-gate record check <name> --inputs <tree> ... [--code <file> ...] [--facts
//! <module>:<attr>] -- <command ...>` (`scripts/gates/memo_check.py`, feature 383 plan D2; ported by feature 449 T148, phase 4's S5): run a
//! check, or replay its last PASS while nothing it reads has changed. The GM, 2026-10-12: *"if we made use of a caching layer, then I feel
//! like it would not take nearly five seconds"*. A pass is kept by the content of every file under the input trees (tracked by the
//! index's blob id, changed or untracked by its bytes, the ignored left out), the code that checks, and the command; a FAILING run is
//! never kept. Each run is one usage-log row, `memo_check`'s name, `passed` or `refused` - none for a run that raised, as the Python's
//! `memo_check.py` wrote none then. `L7R_CACHE_OFF` set to anything but `0` runs the check and keeps nothing.
//!
//! The two presets are the Makefile's `CHECK=1` and the push's rows; each runs its check in this process (the record's build, the
//! glossary's check) where the Python ran its module in its own. The general form runs its command: a `python3 -m <module>` command as
//! the Python ran it in process (its output read as text as written, an uncaught exception ending the check with nothing on stdout and no
//! row), any other as a child process (its output read as text with universal newlines, as `subprocess.run(text=True)` reads it). The
//! Python's `--facts <module>:<attr>` imported the module before a `-m` run and handed it a per-file memo, which changed only its speed:
//! the module is imported here too (one that does not import ends the check as it raised there; what its import prints is shown before
//! the run's output and never kept), and nothing is installed.
//!
//! The kept file is the Python's, `<git common dir>/l7r-cache/memo-<name>.json`, `{"key": ..., "out": ..., "err": ...}` written as
//! `json.dump` writes it. Its key cannot be the Python's - that hashed the interpreter's version and the Python modules' semantic ids -
//! so it is this program's (path, inode, size, time) and the `--code` files' bytes with the project modules they import, and a pass the
//! Python kept is a miss here once. The record's check keys today's UTC date too (feature 449 T163, constitution XIV): its refusals read
//! the date - a row's upload is pending for seven days - so a pass kept on one day would be replayed past a row's window, letting
//! through a record the check now refuses; the Python's key held no date, and T148's port matched it before this fix.

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Value};

use super::{said, Run};
use crate::{re, Error};

/// The usage log's name for every run, `memo_check.py`'s, which `scripts/tool-registry.json` lists: the row its `l7r-gate log usage`
/// wrote, written in process now (`check tool-signals` reads the name here).
pub const USAGE_LOG_TOOL: &str = "memo_check";
/// The Python's usage line, its program named as the port (`ask:449-T135-generator`: a message naming the generator the cut deletes names
/// the port).
pub const USAGE: &str = "usage: l7r-gate record check record|glossary, or <name> --inputs <tree> ... [--code <file> ...] [--facts <module>:<attr>] -- <command ...>\n";
/// The kind of an error that ends a check as the Python's uncaught exception did: its words are the child's stderr, printed as they are.
pub const RAISED: &str = "raised";
/// The input trees both presets read (`PRESETS`, measured in specs/383 research R1).
const PRESET_INPUTS: [&str; 2] = ["research", "l7r/diagram/interactive/assets"];

/// What a call asks: a preset by its name, or the general form.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Call {
    Preset(String),
    General {
        name: String,
        inputs: Vec<String>,
        code: Vec<String>,
        facts: Option<String>,
        command: Vec<String>,
    },
}

/// The arguments as `memo_check.parse` reads them: a preset's name alone, or a name, `--inputs` (one or more), `--code`, at most one
/// `--facts`, `--` and a command; none for anything else.
#[must_use]
pub fn parse(args: &[String]) -> Option<Call> {
    if let [name] = args {
        if name == "record" || name == "glossary" {
            return Some(Call::Preset(name.clone()));
        }
    }
    let cut = args.iter().position(|a| a == "--")?;
    if args[0].starts_with("--") {
        return None;
    }
    let (mut inputs, mut code, mut facts) = (Vec::new(), Vec::new(), Vec::new());
    let mut current: Option<&str> = None;
    for a in &args[1..cut] {
        match a.as_str() {
            flag @ ("--inputs" | "--code" | "--facts") => current = Some(flag),
            _ => match current? {
                "--inputs" => inputs.push(a.clone()),
                "--code" => code.push(a.clone()),
                _ => facts.push(a.clone()),
            },
        }
    }
    let command = args[cut + 1..].to_vec();
    (!inputs.is_empty() && !command.is_empty() && facts.len() <= 1).then(|| Call::General {
        name: args[0].clone(),
        inputs,
        code,
        facts: facts.pop(),
        command,
    })
}

fn git_z(root: &Path, args: &[String]) -> Vec<String> {
    let out = Command::new("git").arg("-C").arg(root).args(args).output();
    out.ok()
        .filter(|o| o.status.success())
        .map(|o| {
            String::from_utf8_lossy(&o.stdout)
                .split('\0')
                .filter(|s| !s.is_empty())
                .map(str::to_owned)
                .collect()
        })
        .unwrap_or_default()
}

fn hash_file(path: &Path) -> String {
    std::fs::read(path).map_or_else(
        |_| "gone".to_owned(),
        |d| l7r_gate_core::codeid::git_blob_id(&d),
    )
}

/// `record_cache.content_ids(root, prefixes, untracked=True)`: every tracked file under the prefixes by its index blob id, a file the
/// work tree changed and one git neither tracks nor ignores by its bytes' blob id ("gone" where it cannot be read).
#[must_use]
pub fn content_ids(root: &Path, prefixes: &[String]) -> BTreeMap<String, String> {
    let with = |head: &[&'static str]| -> Vec<String> {
        head.iter()
            .map(|h| (*h).to_owned())
            .chain(std::iter::once("--".to_owned()))
            .chain(prefixes.iter().cloned())
            .collect()
    };
    let mut ids = BTreeMap::new();
    for rec in git_z(root, &with(&["ls-files", "-s", "-z"])) {
        let (meta, path) = rec.split_once('\t').unwrap_or((rec.as_str(), ""));
        let parts: Vec<&str> = meta.split_whitespace().collect();
        if parts.len() == 3 && !path.is_empty() {
            ids.insert(path.to_owned(), parts[1].to_owned());
        }
    }
    for args in [
        &["diff", "--name-only", "-z"][..],
        &["ls-files", "--others", "--exclude-standard", "-z"][..],
    ] {
        for path in git_z(root, &with(args)) {
            let id = hash_file(&root.join(&path));
            ids.insert(path, id);
        }
    }
    ids
}

static IMPORT: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^[ \t]*import[ \t]+([^#\n]+)"));
static FROM: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?m)^[ \t]*from[ \t]+([A-Za-z_][\w.]*)[ \t]+import[ \t]+(\([^)]*\)|[^#\n]+)")
});

/// The names a module imports, as `ast.walk` finds them: each `import a.b`, and each `from m import x` as `m` and `m.x` (a relative import
/// left out). Read from the text, line by line, so an import a docstring quotes is counted too - a key that misses less, never more.
fn import_names(text: &str) -> Vec<String> {
    let text = text.replace("\\\n", " ");
    let alias = |a: &str| a.split_whitespace().next().unwrap_or("").to_owned();
    let mut out = Vec::new();
    for c in IMPORT.captures_iter(&text).flatten() {
        out.extend(c[1].split(',').map(alias).filter(|a| !a.is_empty()));
    }
    for c in FROM.captures_iter(&text).flatten() {
        let module = c[1].to_owned();
        let names: Vec<String> = c[2]
            .trim_matches(['(', ')'])
            .split(',')
            .map(alias)
            .filter(|a| !a.is_empty())
            .collect();
        out.push(module.clone());
        out.extend(names.iter().map(|n| format!("{module}.{n}")));
    }
    out
}

/// `record_cache.imported_files`: `path` and every project file it imports, transitively - a name beside it, in a directory the scripts
/// put on `sys.path`, or under the repository by its dotted name; the standard library and installed packages resolve to nothing.
pub fn imported_files(path: &Path, repo: &Path, seen: &mut BTreeSet<PathBuf>) {
    let path = crate::resolve(path);
    if seen.contains(&path) || !path.is_file() {
        return;
    }
    seen.insert(path.clone());
    let parent = path.parent().unwrap_or(Path::new("/")).to_path_buf();
    let dirs: Vec<PathBuf> = std::iter::once(parent.clone())
        .chain(
            [
                "../hooks/lib",
                "../reviews",
                "../record",
                "../measure",
                "../gates",
            ]
            .iter()
            .map(|d| parent.join(d)),
        )
        .collect();
    let repo_real = crate::resolve(repo);
    for name in import_names(&crate::read(&path).unwrap_or_default()) {
        let parts: Vec<&str> = name.split('.').collect();
        let mut candidates: Vec<PathBuf> = if parts.len() == 1 {
            dirs.iter().map(|d| d.join(format!("{name}.py"))).collect()
        } else {
            Vec::new()
        };
        let nested: PathBuf = parts.iter().collect();
        candidates.push(repo.join(&nested).with_extension("py"));
        candidates.push(repo.join(&nested).join("__init__.py"));
        if let Some(c) = candidates
            .into_iter()
            .find(|c| c.is_file() && crate::resolve(c).starts_with(&repo_real))
        {
            imported_files(&c, repo, seen);
        }
    }
}

/// The checking code's key: the program, and each `--code` file with the project modules it imports, by their bytes.
#[must_use]
pub fn code_key(repo: &Path, program: &str, code: &[PathBuf]) -> String {
    let mut files = BTreeSet::new();
    for c in code {
        imported_files(c, repo, &mut files);
    }
    let mut text = program.to_owned();
    for f in files {
        text.push('\x1f');
        text.push_str(&l7r_guard::shared::sha256::hex(
            &std::fs::read(&f).unwrap_or_default(),
        ));
    }
    text
}

/// `record_cache.off()`: `L7R_CACHE_OFF` set to anything but empty or `0`.
#[must_use]
pub fn off() -> bool {
    off_of(std::env::var("L7R_CACHE_OFF").ok().as_deref())
}

/// [`off`] of the variable's value, none where it is unset.
#[must_use]
pub fn off_of(value: Option<&str>) -> bool {
    !matches!(value, None | Some("" | "0"))
}

/// One check's kept pass (`record_cache.ResultMemo`): where it lives, none with the cache off or outside a repository, and its key.
pub struct Memo {
    path: Option<PathBuf>,
    key: String,
}

impl Memo {
    /// The memo of the check `name` over `inputs`, its key also over `code` (the checking code's key) and `argv`.
    #[must_use]
    pub fn new(
        root: &Path,
        name: &str,
        inputs: &[String],
        code: &str,
        argv: &[String],
        off: bool,
    ) -> Self {
        let ids = content_ids(root, inputs);
        let mut parts: Vec<String> = vec![name.to_owned()];
        parts.extend(argv.iter().cloned());
        parts.push(code.to_owned());
        parts.extend(ids.iter().map(|(p, i)| format!("{p}\x1e{i}")));
        let path = if off {
            None
        } else {
            l7r_guard::shared::usage::common(root)
                .map(|d| d.join("l7r-cache").join(format!("memo-{name}.json")))
        };
        Self {
            path,
            key: l7r_guard::shared::sha256::hex(parts.join("\x1f").as_bytes()),
        }
    }

    /// The kept (stdout, stderr), while the key holds.
    #[must_use]
    pub fn hit(&self) -> Option<(String, String)> {
        let kept: Value =
            serde_json::from_str(&std::fs::read_to_string(self.path.as_ref()?).ok()?).ok()?;
        let text = |k: &str| {
            kept.get(k)
                .and_then(Value::as_str)
                .unwrap_or_default()
                .to_owned()
        };
        (kept.get("key").and_then(Value::as_str) == Some(self.key.as_str()))
            .then(|| (text("out"), text("err")))
    }

    /// Keep a pass, written whole; a file that cannot be written keeps nothing, as the Python's `keep` swallowed its own failure.
    pub fn keep(&self, out: &str, err: &str) {
        let Some(path) = &self.path else { return };
        let row = l7r_guard::shared::pyjson::dumps(
            &json!({"key": self.key, "out": out, "err": err}),
            None,
            true,
        );
        let tmp = path.with_extension(format!("{}.tmp", std::process::id()));
        let _ = std::fs::create_dir_all(path.parent().unwrap_or(path))
            .and_then(|()| std::fs::write(&tmp, row))
            .and_then(|()| std::fs::rename(&tmp, path));
    }

    /// The check: the kept pass replayed, or `check` run and its pass kept.
    ///
    /// # Errors
    /// `check`'s.
    pub fn run(&self, check: impl FnOnce() -> Run) -> Run {
        if let Some((out, err)) = self.hit() {
            return Ok(said(out, err, 0));
        }
        let ran = check()?;
        if ran.code == 0 {
            self.keep(&ran.stdout, &ran.stderr);
        }
        Ok(ran)
    }
}

/// The interpreter a `-m` command names as the Python's own (`[sys.executable, "-m"]`): the first `python3` on the `PATH`.
fn python() -> String {
    std::env::var_os("PATH")
        .into_iter()
        .flat_map(|p| std::env::split_paths(&p).collect::<Vec<_>>())
        .map(|d| d.join("python3"))
        .find(|p| p.is_file())
        .map_or_else(String::new, |p| p.display().to_string())
}

/// `universal newlines`: `\r\n` and a lone `\r` read as `\n`.
fn universal(text: &str) -> String {
    text.replace("\r\n", "\n").replace('\r', "\n")
}

/// Whether `argv` is a command the Python ran in its own process (`python3 -m <module> ...`, `[sys.executable, "-m"]`).
fn in_process(argv: &[String]) -> bool {
    argv.len() > 2 && argv[1] == "-m" && (argv[0] == "python3" || argv[0] == python())
}

/// The facts module (`<module>:<attr>`) a `-m` command's run was handed, imported as the Python imported it before the run: what its
/// import printed, which the Python printed straight through and kept nothing of.
///
/// # Errors
/// A module that does not import ends the check as it raised there (`RAISED`, its traceback).
pub fn facts_import(root: &Path, facts: &str) -> crate::Result<(String, String)> {
    let module = facts.split_once(':').map_or(facts, |(m, _)| m);
    let probe = Command::new("python3")
        .args([
            "-c",
            "import importlib, sys; importlib.import_module(sys.argv[1])",
            module,
        ])
        .current_dir(root)
        .output()
        .ok();
    let text = |b: &[u8]| String::from_utf8_lossy(b).into_owned();
    match probe {
        Some(p) if p.status.success() => Ok((text(&p.stdout), text(&p.stderr))),
        other => Err(Error::new(
            RAISED,
            other.map(|p| text(&p.stderr)).unwrap_or_default(),
        )),
    }
}

/// The command run from `root`, as `memo_check.run` ran it.
///
/// # Errors
/// A command that cannot start, output that is not UTF-8 (the Python's `UnicodeDecodeError`), or a `-m` module that raised (`RAISED`).
pub fn command(root: &Path, argv: &[String]) -> Run {
    let in_process = in_process(argv);
    let done = Command::new(&argv[0])
        .args(&argv[1..])
        .current_dir(root)
        .output()
        .map_err(|e| Error::new("FileNotFoundError", format!("{e}: '{}'", argv[0])))?;
    let text = |b: Vec<u8>| {
        String::from_utf8(b).map_err(|e| Error::new("UnicodeDecodeError", e.to_string()))
    };
    let (out, err) = (text(done.stdout)?, text(done.stderr)?);
    let code = done.status.code().unwrap_or_else(|| {
        -std::os::unix::process::ExitStatusExt::signal(&done.status).unwrap_or(1)
    });
    if in_process {
        // `runpy` in the Python's own process: an exception it let through ended the check, its captured stdout lost
        if code == 1 && err.contains("Traceback (most recent call last):") {
            return Err(Error::new(RAISED, err));
        }
        return Ok(said(out, err, code));
    }
    Ok(said(universal(&out), universal(&err), code))
}

/// A preset's check, its pass kept by its inputs, this program and (the record's) today's date.
///
/// # Errors
/// The check's, which the Python let through.
pub fn preset(name: &str, root: &Path, program: &str, today: &str) -> Run {
    let inputs: Vec<String> = PRESET_INPUTS.iter().map(|s| (*s).to_owned()).collect();
    let (module, check): (&str, fn(&Path) -> Run) = if name == "record" {
        ("record_asset", super::site::check)
    } else {
        ("glossary_asset", super::glossary::check)
    };
    let argv: Vec<String> = [
        "python3",
        "-m",
        &format!("l7r.diagram.tools.{module}"),
        "--check",
    ]
    .iter()
    .map(|s| (*s).to_owned())
    .collect();
    let code = if name == "record" {
        format!("{program}\x1f{today}")
    } else {
        program.to_owned()
    };
    Memo::new(root, name, &inputs, &code, &argv, off()).run(|| check(root))
}

/// The general form's run: the kept pass replayed, or the facts module imported (a `-m` command's) and the command run, its pass kept -
/// what the import printed shown before the run's output and never kept, as the Python printed it straight through.
///
/// # Errors
/// [`facts_import`]'s and [`command`]'s.
pub fn general(root: &Path, memo: &Memo, words: &[String], facts: Option<&str>) -> Run {
    if let Some((out, err)) = memo.hit() {
        return Ok(said(out, err, 0));
    }
    let (pre_out, pre_err) = match facts.filter(|_| in_process(words)) {
        Some(f) => facts_import(root, f)?,
        None => (String::new(), String::new()),
    };
    let ran = command(root, words)?;
    if ran.code == 0 {
        memo.keep(&ran.stdout, &ran.stderr);
    }
    Ok(said(pre_out + &ran.stdout, pre_err + &ran.stderr, ran.code))
}

/// `record check ...` over the repository `root`, `program` this program's id, `today` the UTC date: the call run and its run recorded
/// in the usage log as `memo_check.py` recorded it.
///
/// # Errors
/// What the check let through; a run that raised records nothing.
pub fn cli(args: &[String], root: &Path, program: &str, today: &str) -> Run {
    let ran = match parse(args) {
        None => Ok(said("", USAGE, 2)),
        Some(Call::Preset(name)) => preset(&name, root, program, today),
        Some(Call::General {
            name,
            inputs,
            code,
            facts,
            command: words,
        }) => {
            let files: Vec<PathBuf> = code.iter().map(|c| root.join(c)).collect();
            let memo = Memo::new(
                root,
                &name,
                &inputs,
                &code_key(root, program, &files),
                &words,
                off(),
            );
            general(root, &memo, &words, facts.as_deref())
        }
    };
    if let Ok(r) = &ran {
        l7r_guard::shared::usage::record(
            root,
            USAGE_LOG_TOOL,
            "check",
            l7r_guard::shared::usage::exited(r.code),
        );
    }
    ran
}

#[cfg(test)]
mod tests;
