//! One side of one case run (feature 449 T161): a fresh world built by the setup commands, the steps run in it, and what changed in it.
//!
//! WHY A FRESH WORLD A CASE AND SIDE: a kept result is reused on a later day against the other side's fresh run, so each case must start
//! from the same world whichever cases ran before it - T146's harness reset one world between cases by hand; here the setup builds it
//! anew into an empty directory, and the directory is removed after the side's outputs are read.

use std::collections::BTreeMap;
use std::io::Read;
use std::os::unix::process::CommandExt as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::{Duration, Instant};

use serde_json::{Map, Value};

use crate::cases::{fill, Case, Cases, From, Side};

/// One step's raw outputs.
pub struct StepOut {
    pub exit: i32,
    pub stdout: String,
    pub stderr: String,
}

/// One side's raw run: the compared steps, what changed under the world (a deleted file `None`), the named extras among them, the time
/// the steps took.
pub struct Raw {
    pub steps: Vec<StepOut>,
    pub delta: BTreeMap<String, Option<Vec<u8>>>,
    pub took_s: f64,
    pub world: PathBuf,
}

/// Everything a side's commands are filled from: the file's `vars`, the side's, `{WORLD}`, `{SIDE}` and `{ROOT}`.
#[must_use]
pub fn vars(cases: &Cases, side: &Side, which: &str, world: &Path) -> BTreeMap<String, String> {
    let mut v = cases.vars.clone();
    v.extend(side.vars.clone());
    v.insert("WORLD".to_owned(), world.display().to_string());
    v.insert("SIDE".to_owned(), which.to_owned());
    v.insert("ROOT".to_owned(), cases.root.display().to_string());
    v
}

const MAKE_VARS: [&str; 4] = ["MAKEFLAGS", "MAKELEVEL", "MFLAGS", "MAKEOVERRIDES"];

/// The environment: the runner's own, less make's variables and the dropped prefixes, then the world's, the side's and the case's (null unsets).
fn env(
    cases: &Cases,
    side: &Side,
    case: Option<&Case>,
    vars: &BTreeMap<String, String>,
) -> Vec<(String, String)> {
    // make's own variables never reach a side: run through `make diff-run`, a step's `make` saw itself a sub-make (`make[1]: ***` in
    // its stderr, the jobserver's descriptors in MAKEFLAGS), where the same run straight from the shell did not (feature 449 T161's
    // worked example, observed 2026-11-16)
    let mut out: BTreeMap<String, String> = std::env::vars()
        .filter(|(k, _)| {
            !MAKE_VARS.contains(&k.as_str())
                && !cases.env_drop.iter().any(|p| k.starts_with(p.as_str()))
        })
        .collect();
    let none = Map::new();
    for layer in [&cases.env, &side.env, case.map_or(&none, |c| &c.env)] {
        for (k, v) in layer {
            match v {
                Value::String(s) => {
                    out.insert(k.clone(), fill(s, vars));
                }
                _ => {
                    out.remove(k);
                }
            }
        }
    }
    for k in ["WORLD", "SIDE"] {
        out.insert(
            format!("DIFF_RUN_{k}"),
            vars.get(k).cloned().unwrap_or_default(),
        );
    }
    out.into_iter().collect()
}

fn kill_group(pid: u32) {
    // the whole process group: a step's own children (a loopback server, a browser) die with it, so none outlives its world
    let _ = Command::new("kill")
        .args(["-KILL", "--", &format!("-{pid}")])
        .stderr(Stdio::null())
        .status();
}

fn reader(pipe: Option<impl Read + Send + 'static>) -> std::thread::JoinHandle<Vec<u8>> {
    std::thread::spawn(move || {
        let mut buf = Vec::new();
        if let Some(mut p) = pipe {
            let _ = p.read_to_end(&mut buf);
        }
        buf
    })
}

/// One command run to its end or its timeout.
///
/// # Errors
///
/// A command that cannot start, or one that outran `timeout`.
pub fn command(
    argv: &[String],
    cwd: &Path,
    env: &[(String, String)],
    timeout: Duration,
) -> Result<StepOut, String> {
    let mut child = Command::new(&argv[0])
        .args(&argv[1..])
        .current_dir(cwd)
        .env_clear()
        .envs(env.iter().map(|(k, v)| (k, v)))
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .process_group(0)
        .spawn()
        .map_err(|e| format!("{}: cannot start: {e}", argv.join(" ")))?;
    let (out, err) = (reader(child.stdout.take()), reader(child.stderr.take()));
    let start = Instant::now();
    let status = loop {
        if let Ok(Some(status)) = child.try_wait() {
            break status;
        }
        if start.elapsed() > timeout {
            kill_group(child.id());
            let _ = child.wait();
            return Err(format!(
                "{}: timed out after {} s",
                argv.join(" "),
                timeout.as_secs()
            ));
        }
        std::thread::sleep(Duration::from_millis(5));
    };
    kill_group(child.id());
    let text = |h: std::thread::JoinHandle<Vec<u8>>| {
        String::from_utf8_lossy(&h.join().unwrap_or_default()).into_owned()
    };
    // a signal's death reads as the shell reads it, 128 + the signal
    let exit = status.code().unwrap_or_else(|| {
        128 + std::os::unix::process::ExitStatusExt::signal(&status).unwrap_or(0)
    });
    Ok(StepOut {
        exit,
        stdout: text(out),
        stderr: text(err),
    })
}

fn walk(dir: &Path, rel: &str, ignore: &[String], out: &mut BTreeMap<String, Vec<u8>>) {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    for e in entries.flatten() {
        let name = e.file_name().to_string_lossy().into_owned();
        if ignore.contains(&name) {
            continue;
        }
        let path = e.path();
        let here = if rel.is_empty() {
            name
        } else {
            format!("{rel}/{name}")
        };
        match e.file_type() {
            Ok(t) if t.is_symlink() => {
                let to = std::fs::read_link(&path).unwrap_or_default();
                out.insert(here, format!("<link -> {}>", to.display()).into_bytes());
            }
            Ok(t) if t.is_dir() => walk(&path, &here, ignore, out),
            _ => {
                out.insert(here, std::fs::read(&path).unwrap_or_default());
            }
        }
    }
}

/// Every file under the compared paths of the world, by its world-relative name, and each named extra.
fn snapshot(
    cases: &Cases,
    files: &[String],
    world: &Path,
    vars: &BTreeMap<String, String>,
    cwd: &Path,
    env: &[(String, String)],
) -> BTreeMap<String, Vec<u8>> {
    let mut out = BTreeMap::new();
    for f in files {
        let rel = fill(f, vars);
        let rel = rel.trim_end_matches('/');
        let path = if rel == "." {
            world.to_path_buf()
        } else {
            world.join(rel)
        };
        if path.is_file() {
            out.insert(rel.to_owned(), std::fs::read(&path).unwrap_or_default());
        } else {
            walk(
                &path,
                if rel == "." { "" } else { rel },
                &cases.ignore,
                &mut out,
            );
        }
    }
    for x in &cases.extras {
        let got = match &x.from {
            From::Path(p) => std::fs::read(fill(p, vars)).ok(),
            From::Cmd(argv) => {
                let argv: Vec<String> = argv.iter().map(|a| fill(a, vars)).collect();
                command(&argv, cwd, env, Duration::from_secs(cases.timeout_s))
                    .ok()
                    .map(|o| o.stdout.into_bytes())
            }
        };
        if let Some(bytes) = got {
            out.insert(format!("<{}>", x.name), bytes);
        }
    }
    out
}

/// The side's build commands, run once a run before its first case, from the root: they make its binaries current, since the new
/// side's key reads its sources and its result comes from a binary.
///
/// # Errors
///
/// A build that fails or cannot start.
pub fn build(cases: &Cases, side: &Side, which: &str) -> Result<(), String> {
    let vars = vars(cases, side, which, &cases.root);
    let env = env(cases, side, None, &vars);
    for argv in &side.build {
        let argv: Vec<String> = argv.iter().map(|a| fill(a, &vars)).collect();
        let out = command(
            &argv,
            &cases.root,
            &env,
            Duration::from_secs(cases.timeout_s),
        )?;
        if out.exit != 0 {
            return Err(format!(
                "{which} side's build `{}` exited {}:\n{}",
                argv.join(" "),
                out.exit,
                tail(&out.stderr)
            ));
        }
    }
    Ok(())
}

fn tail(text: &str) -> String {
    let lines: Vec<&str> = text.lines().collect();
    lines[lines.len().saturating_sub(20)..].join("\n")
}

/// One side of `case`, run in a fresh `world`, which is removed after.
///
/// # Errors
///
/// A setup command that fails, a step that cannot start or outruns the timeout: no result, so nothing is kept.
pub fn side(
    cases: &Cases,
    case: &Case,
    side: &Side,
    which: &str,
    world: &Path,
) -> Result<Raw, String> {
    let _ = std::fs::remove_dir_all(world);
    let got = std::fs::create_dir_all(world)
        .map_err(|e| format!("{}: {e}", world.display()))
        .and_then(|()| in_world(cases, case, side, which, world));
    let _ = std::fs::remove_dir_all(world);
    got
}

fn in_world(
    cases: &Cases,
    case: &Case,
    side: &Side,
    which: &str,
    world: &Path,
) -> Result<Raw, String> {
    let vars = vars(cases, side, which, world);
    let env = env(cases, side, Some(case), &vars);
    let timeout = Duration::from_secs(cases.timeout_s);
    for argv in &cases.setup {
        let argv: Vec<String> = argv.iter().map(|a| fill(a, &vars)).collect();
        let out = command(&argv, &cases.root, &env, timeout)?;
        if out.exit != 0 {
            return Err(format!(
                "setup `{}` exited {}:\n{}",
                argv.join(" "),
                out.exit,
                tail(&out.stderr)
            ));
        }
    }
    let cwd = PathBuf::from(fill(&cases.cwd, &vars));
    let files = case.files.as_ref().unwrap_or(&cases.files);
    let before = snapshot(cases, files, world, &vars, &cwd, &env);
    let wrap: Vec<String> = cases.wrap.iter().map(|a| fill(a, &vars)).collect();
    let (mut steps, mut took) = (Vec::new(), 0.0);
    for step in &case.steps {
        let mut argv = wrap.clone();
        for a in &step.argv {
            if a == "{CMD}" {
                argv.extend(side.cmd.iter().map(|c| fill(c, &vars)));
            } else {
                argv.push(fill(a, &vars));
            }
        }
        let start = Instant::now();
        let out = command(&argv, &cwd, &env, timeout)?;
        took += start.elapsed().as_secs_f64();
        if step.compare {
            steps.push(out);
        }
    }
    let after = snapshot(cases, files, world, &vars, &cwd, &env);
    let mut delta: BTreeMap<String, Option<Vec<u8>>> = after
        .iter()
        .filter(|(k, v)| before.get(*k) != Some(v))
        .map(|(k, v)| (k.clone(), Some(v.clone())))
        .collect();
    delta.extend(
        before
            .keys()
            .filter(|k| !after.contains_key(*k))
            .map(|k| (k.clone(), None)),
    );
    Ok(Raw {
        steps,
        delta,
        took_s: took,
        world: world.to_path_buf(),
    })
}
