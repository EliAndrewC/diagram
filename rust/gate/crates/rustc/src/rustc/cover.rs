//! The coverage run (feature 444 T17; feature 449 T92, T100, T105, T108): 100% of a crate's lines by its own tests, `cargo llvm-cov`.
//! The owed crates' test binaries are built in one cargo call a family, and every crate's tests and report then run side by side,
//! each in a report directory of its own.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::time::Instant;

use super::{crates, family, lcov_missed, leak_checked, own, re, run_in, tail, Ran, World};

/// The flags `show-env` adds to RUSTFLAGS for coverage, every crate built with them. Only the last run's profiles are cleared and only
/// the tests' binary is built: `llvm-cov clean` rebuilt the crate from scratch on every run (the GM 2026-11-07: "Are we recompiling
/// EVERYTHING every time?").
const COVERAGE_FLAGS: [&str; 3] = [
    "-C instrument-coverage",
    "--cfg=coverage",
    "--cfg=trybuild_no_target",
];

/// COVERAGE INSTRUMENTS THE WORKSPACE'S OWN CRATES ONLY (feature 449 T100): `show-env`'s RUSTFLAGS instrumented every crate the build
/// compiles, `fancy-regex` and `serde` too, though the report counts only the workspace's lines - and the checks crate's tests, which
/// scan the tree with regexes, took 23 s under coverage against 0.6 s plain (2026-11-11). The coverage flags move out of RUSTFLAGS
/// into a `RUSTC_WORKSPACE_WRAPPER` that adds them, which cargo calls for the workspace's crates alone, the rest of RUSTFLAGS (rust-lld,
/// T96) left to every crate. `script` is written each run with the same text, so its path and content never move a build's key.
pub(super) fn workspace_only(env: &mut BTreeMap<String, String>, script: &Path) {
    let Some(flags) = env.get("RUSTFLAGS").cloned() else {
        return;
    };
    let added: Vec<&str> = COVERAGE_FLAGS
        .iter()
        .copied()
        .filter(|f| flags.contains(f))
        .collect();
    let rest = COVERAGE_FLAGS.iter().fold(flags, |f, c| f.replace(c, ""));
    let rest: Vec<&str> = rest.split_whitespace().collect();
    let text = format!("#!/bin/sh\nexec \"$@\" {}\n", added.join(" "));
    if std::fs::read_to_string(script).ok().as_deref() != Some(text.as_str()) {
        let _ = std::fs::write(script, &text);
        let _ =
            std::fs::set_permissions(script, std::os::unix::fs::PermissionsExt::from_mode(0o755));
    }
    env.insert("RUSTFLAGS".to_owned(), rest.join(" "));
    env.insert(
        "RUSTC_WORKSPACE_WRAPPER".to_owned(),
        script.display().to_string(),
    );
}

/// A crate's package name, from its manifest.
fn package_name(manifest: &Path) -> Option<String> {
    let text = std::fs::read_to_string(manifest).unwrap_or_default();
    re(r#"(?m)^name\s*=\s*"([^"]+)""#)
        .captures(&text)
        .ok()
        .flatten()
        .map(|c| c[1].to_owned())
}

/// The environment of a family's coverage build: its build directory, `show-env`'s coverage settings, and the coverage flags moved to
/// the workspace's own crates (`workspace_only`). Asked once a family: each crate's run adds its own.
fn cover_env(world: &World, manifest: &Path, work: &Path) -> BTreeMap<String, String> {
    let manifest_arg = manifest.display().to_string();
    let target = work.join("target");
    let mut env = BTreeMap::from([
        (
            "PATH".to_owned(),
            format!(
                "{}:{}",
                world.path_dir.display(),
                std::env::var("PATH").unwrap_or_default()
            ),
        ),
        ("CARGO_TARGET_DIR".to_owned(), target.display().to_string()),
    ]);
    // from the tree's root, as every cargo call: show-env folds `.cargo/config.toml`'s rustflags (rust-lld, T96) into the RUSTFLAGS it
    // prints, which replace the config's for the build below
    let shown = run_in(
        Some(&world.root),
        &world.cargo,
        &[
            own(&["llvm-cov", "show-env", "--manifest-path"]),
            vec![manifest_arg],
        ]
        .concat(),
        &env,
    );
    for line in shown.stdout.lines() {
        if let Some((k, v)) = line.split_once('=') {
            env.insert(
                k.trim_start_matches("export ").to_owned(),
                v.trim().trim_matches(['\'', '"']).to_owned(),
            );
        }
    }
    workspace_only(&mut env, &work.join("instrument.sh"));
    env
}

/// The directory a crate's coverage build is kept in (a test shares one over its copies of a fixture): one a family of crates
/// (`family`), so the gate's crates build their shared dependencies once.
pub(super) fn cover_dir(world: &World, manifest: &Path) -> PathBuf {
    let family = family(manifest);
    let name = family.file_name().unwrap_or_default().to_string_lossy();
    world
        .cover_work
        .clone()
        .unwrap_or_else(|| world.target.join(format!("cover-{name}")))
}

/// A step's time, on the line the logs read.
fn took(step: &str, began: Instant) -> String {
    format!(
        "rust-checks: cover {step} {:.1} s\n",
        began.elapsed().as_secs_f64()
    )
}

fn remove(path: &Path) {
    let _ = std::fs::remove_dir_all(path);
}

/// The test binary a cargo build's JSON messages name for each package, by its manifest.
fn test_binaries(stdout: &str) -> BTreeMap<PathBuf, PathBuf> {
    stdout
        .lines()
        .filter_map(|l| serde_json::from_str::<serde_json::Value>(l).ok())
        .filter_map(|v| {
            let exe = v.get("executable")?.as_str()?;
            let manifest = v.get("manifest_path")?.as_str()?;
            Some((canon(Path::new(manifest)), PathBuf::from(exe)))
        })
        .collect()
}

fn canon(path: &Path) -> PathBuf {
    std::fs::canonicalize(path).unwrap_or_default()
}

/// A built crate's test binary, or why there is none.
type Built = Result<PathBuf, Ran>;

/// THE COVERAGE BUILDS TOGETHER (feature 449 T105; the GM 2026-11-11): each crate's coverage run built its instrumented test binary
/// alone, one crate after another in the family's one build directory, which cargo locks - after a core edit 17 builds and 14.6 s of
/// `make static`'s 54.0 s (2026-11-11), on a machine of 22 cores. The family's owed crates are built in one cargo call, which compiles
/// them side by side, and its JSON names each crate's test binary, so no crate's run builds again (T108: those builds were 6.0 s of a
/// core edit's run after T105). A failed build of several is asked again a crate at a time, so the failure is the crate's that has it.
fn build(
    world: &World,
    env: &BTreeMap<String, String>,
    group: &[&PathBuf],
    said: &mut String,
) -> Vec<(PathBuf, Built)> {
    let began = Instant::now();
    let mut args = own(&[
        "test",
        "--no-run",
        "--lib",
        "--quiet",
        "--message-format=json-render-diagnostics",
        "--manifest-path",
    ]);
    args.push(group[0].display().to_string());
    for name in group.iter().filter_map(|m| package_name(m)) {
        args.extend(["-p".to_owned(), name]);
    }
    let built = run_in(Some(&world.root), &world.cargo, &args, env);
    said.push_str(&took(&format!("build of {} crate(s)", group.len()), began));
    if built.code != 0 && group.len() > 1 {
        return group
            .iter()
            .flat_map(|m| build(world, env, &[m], said))
            .collect();
    }
    let binaries = test_binaries(&built.stdout);
    group
        .iter()
        .map(|m| {
            let found = binaries.get(&canon(m)).filter(|_| built.code == 0);
            let why = Ran {
                code: 1,
                stdout: String::new(),
                stderr: format!(
                    "{}rust-checks: the coverage build named no test binary for {}\n",
                    built.stderr,
                    m.display()
                ),
            };
            ((*m).clone(), found.cloned().ok_or(why))
        })
        .collect()
}

/// THE CRATES' TESTS AND REPORTS SIDE BY SIDE (feature 449 T108; the GM 2026-11-11): one crate's tests and report, in a report
/// directory of its own (`view`), which holds its test binary alone, linked in, and the profiles its tests write. The report reads
/// every binary and every profile in its build directory, so in the family's one directory a crate's run moved every other crate's
/// binary aside and cleared the last run's profiles (T92, T105), and the crates ran one after another - 17.2 s of a core edit's
/// `make static`, one crate 8.9 s of it (2026-11-11). Each in its own, the runs share nothing. The tests run as `cargo test` runs them,
/// from the crate's directory with cargo's variables, but directly: `cargo test` holds the build directory's lock while they run.
fn run_one(world: &World, job: &Job, lcov: &Path, tmp: &Path, said: &mut String) -> Ran {
    let dir = job.manifest.parent().unwrap_or(Path::new("."));
    let tag = dir.file_name().unwrap_or_default().to_string_lossy();
    let view = job.work.join("view").join(&*tag);
    remove(&view);
    let deps = view.join("debug/deps");
    let _ = std::fs::create_dir_all(&deps);
    let linked = deps.join(job.exe.file_name().unwrap_or_default());
    let _ =
        std::fs::hard_link(&job.exe, &linked).is_ok() || std::fs::copy(&job.exe, &linked).is_ok();
    let mut env = job.env.clone();
    for (k, v) in [
        ("TMPDIR", tmp.display().to_string()),
        (
            "LLVM_PROFILE_FILE",
            view.join("rust-%p-%22m.profraw").display().to_string(),
        ),
        ("CARGO", world.cargo.clone()),
        ("CARGO_MANIFEST_DIR", dir.display().to_string()),
        (
            "CARGO_PKG_NAME",
            package_name(&job.manifest).unwrap_or_default(),
        ),
    ] {
        env.insert(k.to_owned(), v);
    }
    let began = Instant::now();
    let tests = run_in(
        Some(dir),
        &job.exe.display().to_string(),
        &own(&["-q"]),
        &env,
    );
    said.push_str(&took(&format!("tests {tag}"), began));
    if tests.code != 0 {
        remove(&view);
        return tests;
    }
    for k in ["CARGO_TARGET_DIR", "CARGO_LLVM_COV_TARGET_DIR"] {
        env.insert(k.to_owned(), view.display().to_string());
    }
    let began = Instant::now();
    let report = [
        own(&["llvm-cov", "report", "--lcov", "--output-path"]),
        vec![lcov.display().to_string()],
        vec![
            "--manifest-path".to_owned(),
            job.manifest.display().to_string(),
        ],
    ]
    .concat();
    let done = run_in(Some(&world.root), &world.cargo, &report, &env);
    said.push_str(&took(&format!("report {tag}"), began));
    remove(&view);
    done
}

/// A crate whose test binary is built: where, its family's directory and environment.
struct Job {
    manifest: PathBuf,
    exe: PathBuf,
    work: PathBuf,
    env: BTreeMap<String, String>,
}

/// Each owed crate's lines no test reaches, by manifest, and the timing lines to print: the binaries built together a family, then
/// every crate's tests and report side by side (`run_one`). A crate whose run failed answers its directory and line 0.
pub(super) fn uncovered_each(
    world: &World,
    owed: &[&PathBuf],
) -> (BTreeMap<PathBuf, BTreeMap<String, Vec<u32>>>, String) {
    let mut families: BTreeMap<PathBuf, Vec<&PathBuf>> = BTreeMap::new();
    for manifest in owed {
        families
            .entry(cover_dir(world, manifest))
            .or_default()
            .push(manifest);
    }
    let mut said = String::new();
    let mut jobs: Vec<Result<Job, (PathBuf, Ran)>> = Vec::new();
    for (work, group) in families {
        let _ = std::fs::create_dir_all(&work);
        let env = cover_env(world, group[0], &work);
        for (manifest, built) in build(world, &env, &group, &mut said) {
            jobs.push(match built {
                Ok(exe) => Ok(Job {
                    manifest,
                    exe,
                    work: work.clone(),
                    env: env.clone(),
                }),
                Err(why) => Err((manifest, why)),
            });
        }
    }
    let began = Instant::now();
    let count = jobs.len();
    let width = side_by_side(count);
    let queue = std::sync::Mutex::new(jobs.into_iter());
    let done = std::sync::Mutex::new(Vec::new());
    std::thread::scope(|s| {
        for _ in 0..width {
            s.spawn(|| {
                while let Some(job) = next(&queue) {
                    let one = run_job(world, job);
                    done.lock()
                        .unwrap_or_else(std::sync::PoisonError::into_inner)
                        .push(one);
                }
            });
        }
    });
    let ran = done
        .into_inner()
        .unwrap_or_else(std::sync::PoisonError::into_inner);
    said.push_str(&took(
        &format!("tests and reports of {count} crate(s), {width} at a time"),
        began,
    ));
    let mut got = BTreeMap::new();
    for (manifest, lcov, done, own_said) in ran {
        said.push_str(&own_said);
        let missed = missed(world, &manifest, &lcov, &done);
        got.insert(manifest, missed);
    }
    (got, said)
}

/// HOW MANY AT ONCE (T108): a quarter of the cores, at least one. Every owed crate at once (17 after a core edit) took the load of 22
/// cores to 31 and failed two crates' timing tests, a crop's 300 ms and a lock's 50 ms (2026-11-11); each crate's tests run on
/// threads of their own already.
fn side_by_side(count: usize) -> usize {
    let cores = std::thread::available_parallelism().map_or(1, std::num::NonZero::get);
    (cores / 4).clamp(1, count.max(1))
}

/// The next job of a shared queue.
fn next<T>(queue: &std::sync::Mutex<impl Iterator<Item = T>>) -> Option<T> {
    queue
        .lock()
        .unwrap_or_else(std::sync::PoisonError::into_inner)
        .next()
}

/// A crate's directory name, what its report and its time are kept under.
fn tag(manifest: &Path) -> String {
    let dir = manifest
        .parent()
        .and_then(Path::file_name)
        .unwrap_or_default();
    dir.to_string_lossy().into_owned()
}

/// What one crate's run gave: the manifest, its report, how the run went and its timing lines.
type Done = (PathBuf, PathBuf, Ran, String);

/// One crate's run, or its failed build.
fn run_job(world: &World, job: Result<Job, (PathBuf, Ran)>) -> Done {
    match job {
        Ok(job) => {
            let lcov = job.work.join(format!("lcov-{}.info", tag(&job.manifest)));
            let mut said = String::new();
            let done = leak_checked(&job.manifest, |tmp| {
                run_one(world, &job, &lcov, tmp, &mut said)
            });
            (job.manifest, lcov, done, said)
        }
        Err((manifest, why)) => (manifest, PathBuf::new(), why, String::new()),
    }
}

/// One crate's lines no test reaches, from its report; a failed run names the crate, not a line.
fn missed(world: &World, manifest: &Path, lcov: &Path, done: &Ran) -> BTreeMap<String, Vec<u32>> {
    let parent = manifest.parent().unwrap_or(Path::new("."));
    let text = std::fs::read_to_string(lcov);
    let (Ok(text), 0) = (text, done.code) else {
        let (out, err) = (tail(&done.stdout), tail(&done.stderr));
        eprintln!("rust-checks: the coverage run failed on {} - fix what it names (a failing test), then ask again:\n{out}{err}", parent.file_name().unwrap_or_default().to_string_lossy());
        return BTreeMap::from([(parent.display().to_string(), vec![0])]);
    };
    let canon_dir = |p: &Path| format!("{}/", canon(p).display());
    let mine = canon_dir(parent);
    // a crate nested in this one's directory (the gate's `crates/*` under the binary's) owns its own lines: 100% of a crate's lines by
    // its own tests (feature 449 T92)
    let nested: Vec<String> = crates(&world.root, &[])
        .iter()
        .filter_map(|m| m.parent())
        .map(canon_dir)
        .filter(|d| d != &mine && d.starts_with(&mine))
        .collect();
    lcov_missed(&text)
        .into_iter()
        .filter(|(p, _)| {
            let at = canon(Path::new(p)).display().to_string();
            at.starts_with(&mine) && !nested.iter().any(|n| at.starts_with(n.as_str()))
        })
        .collect()
}
