//! THE LOCKSTEP'S PYTHON HALF KEPT (feature 449 T178, the GM 2026-11-18, request.md: the efficiency fixes): the parse lockstep's one
//! end-to-end test (`lockstep.rs`) started the Python and ran its readings of every pool sheet and fixture on every run, 7.9 s, so an edit
//! cycle of `make rust-test CRATE=rust/mode_a` took 13-16 s in T175 at a load of 4-6. The Python's output is now kept under the clone's
//! git directory, beside the gate's own kept results (`.git/rust-checks/`, `rust/gate/crates/rustc/src/rustc/kept.rs`) in a directory of
//! its own, with a key over everything it reads, and the Python runs only when that key moves - the comparison, its assertions and its
//! fixtures unchanged.
//! Measured (2026-11-18, `make rust-test CRATE=rust/mode_a` after a Rust-only edit - a probe test added - best of three, scratchpad
//! `t178/phases.log`): 9.19 s before, the test binary 5.50 s, at a load of 0.8-1.3; 6.91 s after, the binary 2.57 s, at 4.2-4.4 - the
//! port's half now the longest; after a Python edit, which reruns it, 8.0 s.
//!
//! WHAT THE KEY READS, MEASURED (2026-11-18, method: an audit hook logging every `open` and `os.listdir` of the test's Python, scratchpad
//! `t178/opens.log`): the `.py` files under `l7r/`, and also `l7r/diagram/buildings/types.json`, the `interactive/assets/` JSON and 556
//! opens of its `modals/` Markdown - so the whole `l7r/` tree, every file but the bytecode caches; every sheet, notes file and manifest
//! handed or found under `pool/`, `tests/fixtures/` and `legacy-hand-authored-pool/`, whose directories `mapmatch.maps_recording` LISTS and
//! tests with `isfile`, so every name there is keyed too; the test's own directory (the fixtures it writes, their notes and manifests,
//! `given.json`); each path handed, read from the test's working directory (`no-such-sheet.svg`, whose absence is the reading); the
//! script's whole text; and `shapely`, whose package it lists and loads, which the interpreter's version string alone would not move - so
//! every installed distribution's name and version beside it. A render (`.png`, `.html`) is keyed by its bytes like any file: one run's
//! log showed none read, but other inputs could make the Python read one, and hashing the pool's renders costs about 0.13 s (feature
//! 449 T178's plan review; observed 2026-11-18, method: `sha256sum` over the 19 renders, 55 MB). Only the bytecode caches are left out,
//! being built wholly from the `.py` sources the key reads.
//!
//! THE TEST'S DIRECTORY IS IN THE OUTPUT: each sheet's reading is keyed by its path, and a refusal names it, so a kept output holds
//! [`MARK`] where the directory stood and the current one is put back on reading; the key reads the directory's files with the same mark,
//! so a run in a new directory with the same fixtures has the same key.
//!
//! Research:
//!     the lockstep's kept half - NONE: where the Python's output comes from, deciding nothing about a building

use std::fmt::Write as _;
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};

use l7r_guard::shared::sha256;

/// The trees of the repository the Python half reads or lists, each keyed whole (every name, and every file's bytes).
const TREES: [&str; 4] = ["l7r", "pool", "tests/fixtures", "legacy-hand-authored-pool"];

/// The bytecode caches: what Python writes from the sources the key already reads.
const CACHE: &str = "__pycache__";

/// What stands for the test's directory in a kept output and in the key's text: a NUL, which no JSON text holds unescaped, so no part
/// of an output is mistaken for it.
const MARK: &str = "\0";

/// The installed interpreter: its version and every distribution it can import, in one start (65 ms, measured 2026-11-18).
pub(super) const IDENTITY: &str = "import sys, importlib.metadata as m\nprint(sys.executable, sys.version)\n\
                                   print(sorted(f\"{d.metadata.get('Name')}=={d.version}\" for d in m.distributions()))";

/// What the Python half is handed and reads.
pub(super) struct Inputs<'a> {
    /// The repository the Python reads (`sys.argv[1]`).
    pub tree: &'a Path,
    /// The test's own directory, the fixtures written there.
    pub dir: &'a Path,
    /// The directory the Python starts in, which a relative path is read from.
    pub cwd: &'a Path,
    /// The script, its stdin and its `given.json`, as handed, and the interpreter's identity ([`IDENTITY`]'s output).
    pub texts: &'a [&'a str],
    /// Every path it is handed, each read where it stands.
    pub paths: &'a [String],
}

/// `bytes` with every `dir` in it replaced by [`MARK`].
fn marked(bytes: &[u8], dir: &str) -> Vec<u8> {
    String::from_utf8_lossy(bytes)
        .replace(dir, MARK)
        .into_bytes()
}

/// A file's digest, marked with `dir` where one is given, or `absent`.
fn digest(at: &Path, dir: Option<&str>) -> String {
    match (std::fs::read(at), dir) {
        (Err(_), _) => "absent".to_owned(),
        (Ok(b), None) => sha256::hex(&b),
        (Ok(b), Some(d)) => sha256::hex(&marked(&b, d)),
    }
}

/// One line for each name under `path` (shown as `shown`), sorted, with its bytes' digest - marked with `dir` where one is given; a
/// cache left out.
fn walk(path: &Path, shown: &str, dir: Option<&str>, out: &mut String) {
    let mut names: Vec<String> = std::fs::read_dir(path)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| n != CACHE)
        .collect();
    names.sort();
    for name in names {
        let (at, rel) = (path.join(&name), format!("{shown}/{name}"));
        if at.is_dir() {
            let _ = writeln!(out, "d {rel}");
            walk(&at, &rel, dir, out);
        } else {
            let _ = writeln!(out, "f {rel} {}", digest(&at, dir));
        }
    }
}

/// The key of the Python half's output: a digest over everything it reads.
pub(super) fn key(i: &Inputs) -> String {
    let d = i.dir.to_string_lossy();
    let mut text = format!("{}\n{}\n", i.tree.display(), i.cwd.display());
    for part in i.texts {
        let _ = writeln!(text, "t {}", sha256::hex(&marked(part.as_bytes(), &d)));
    }
    for tree in TREES {
        walk(&i.tree.join(tree), tree, None, &mut text);
    }
    walk(i.dir, MARK, Some(&d), &mut text);
    for p in i.paths {
        let shown = String::from_utf8_lossy(&marked(p.as_bytes(), &d)).into_owned();
        let _ = writeln!(text, "p {shown} {}", digest(&i.cwd.join(p), Some(&d)));
    }
    sha256::hex(text.as_bytes())
}

/// The interpreter's identity, [`IDENTITY`]'s output: none where it cannot start or fails, so nothing is kept (a key that lost the
/// distributions would hold over an upgrade of one).
pub(super) fn identity(python: &str) -> Option<String> {
    Command::new(python)
        .args(["-I", "-c", IDENTITY])
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
}

/// Where the kept output lives: under the clone's git directory, as the gate's kept results do; none outside a repository.
pub(super) fn place(tree: &Path) -> Option<PathBuf> {
    let out = Command::new("git")
        .arg("-C")
        .arg(tree)
        .args(["rev-parse", "--absolute-git-dir"])
        .output()
        .ok()?;
    let dir = String::from_utf8_lossy(&out.stdout).trim().to_owned();
    (out.status.success() && !dir.is_empty())
        .then(|| Path::new(&dir).join("rust-tests/mode_a-lockstep"))
}

/// The text `dir` is inside a JSON string.
fn in_json(dir: &Path) -> String {
    let quoted = serde_json::Value::from(dir.to_string_lossy()).to_string();
    // one quote off each end, not `trim_matches`, which took an escaped quote's too
    quoted[1..quoted.len() - 1].to_owned()
}

/// The kept output at `at` where it was kept under `key`, the test's directory `dir` put back in it: none where there is no keep, it
/// cannot be read, or its key is another's.
fn read(at: &Path, key: &str, dir: &Path) -> Option<Vec<u8>> {
    let text = std::fs::read_to_string(at).ok()?;
    let (kept, out) = text.split_once('\n')?;
    (kept == key).then(|| out.replace(MARK, &in_json(dir)).into_bytes())
}

/// Keep `out` at `at` under `key`, the test's directory `dir` marked - written beside and renamed, so a run reading it at the same time
/// (a test run beside a coverage run) reads the old keep or the new, never half of one. An output that does not name `dir` is not
/// kept: a reading that lost its paths is not one to trust. A keep that cannot be written is left: the next run asks the Python again.
fn write(at: &Path, key: &str, out: &[u8], dir: &Path) {
    let (text, d) = (String::from_utf8_lossy(out), in_json(dir));
    let beside = at.with_extension(format!("p{}", std::process::id()));
    let wrote = text.contains(&d)
        && at
            .parent()
            .is_some_and(|p| std::fs::create_dir_all(p).is_ok())
        && std::fs::write(&beside, format!("{key}\n{}", text.replace(&d, MARK))).is_ok()
        && std::fs::rename(&beside, at).is_ok();
    if !wrote {
        let _ = std::fs::remove_file(&beside);
    }
}

/// The Python half begun: its output kept, or its run started.
pub(super) enum Half {
    Kept(Vec<u8>),
    Running(Child),
}

/// The run the Python half is: a program, its arguments and its stdin.
pub(super) struct Run<'a> {
    pub program: &'a str,
    pub args: &'a [&'a std::ffi::OsStr],
    pub stdin: &'a [u8],
}

/// `run` started, its stdin written and closed, its outputs piped.
fn start(run: &Run) -> Child {
    let mut child = Command::new(run.program)
        .args(run.args)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    // A CHILD THAT EXITS WITHOUT READING ITS STDIN closes the pipe first, and the write then fails with EPIPE - the keep's own test
    // (`sh -c "exit 3"`) failed so under load (feature 449 T150, observed 2026-11-18 in `make static`'s cover run); the child's exit
    // and stderr say what happened, so a refused write is no failure of its own
    let _ = child.stdin.take().unwrap().write_all(run.stdin);
    child
}

/// The Python half's output: the kept one where its key holds, else `run` started now, so the port's half runs beside it.
pub(super) fn begin(at: Option<&Path>, key: &str, dir: &Path, run: &Run) -> Half {
    at.and_then(|a| read(a, key, dir))
        .map_or_else(|| Half::Running(start(run)), Half::Kept)
}

/// The Python half ended, as the test reads it.
pub(super) struct Ended {
    pub ok: bool,
    pub stderr: String,
    pub stdout: Vec<u8>,
    /// Whether the Python ran, or its output was kept.
    pub ran: bool,
}

/// The Python half ended: a kept one succeeded with nothing on stderr, as it was kept only so; a run's output kept where it did.
pub(super) fn end(half: Half, at: Option<&Path>, key: &str, dir: &Path) -> Ended {
    match half {
        Half::Kept(stdout) => Ended {
            ok: true,
            stderr: String::new(),
            stdout,
            ran: false,
        },
        Half::Running(child) => {
            let out = child.wait_with_output().unwrap();
            let stderr = String::from_utf8_lossy(&out.stderr).into_owned();
            let ok = out.status.success();
            if let (Some(a), true, true) = (at, ok, stderr.is_empty()) {
                write(a, key, &out.stdout, dir);
            }
            Ended {
                ok,
                stderr,
                stdout: out.stdout,
                ran: true,
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use std::ffi::OsStr;
    use std::path::Path;

    use super::{begin, end, identity, key, place, read, write, Inputs, Run};
    use l7r_guard::shared::tempdir::TempDir;

    fn put(at: &Path, text: &str) {
        std::fs::create_dir_all(at.parent().unwrap()).unwrap();
        std::fs::write(at, text).unwrap();
    }

    /// A scratch tree with one file of each kind the key reads, and some it does not; the test's directory, its `given.json` naming it.
    fn scratch(root: &Path, dir: &Path) {
        for (rel, text) in [
            ("l7r/diagram/tools/pack_audit/parse.py", "x = 1\n"),
            ("l7r/diagram/buildings/types.json", "{}"),
            (
                "l7r/diagram/interactive/assets/modals/hamlet/byre.md",
                "a byre",
            ),
            ("l7r/diagram/__pycache__/parse.cpython-314.pyc", "bytecode"),
            ("pool/magistracies/s/s.svg", "<svg/>"),
            ("pool/magistracies/s/s.notes.md", "notes"),
            ("pool/magistracies/s/s.png", "render"),
            ("tests/fixtures/s-red.svg", "<svg/>"),
            ("legacy-hand-authored-pool/towns/u/u.json", "{}"),
            ("docs/other.md", "unread"),
            ("rust/mode_a/src/lib.rs", "unread"),
        ] {
            put(&root.join(rel), text);
        }
        put(&dir.join("fixture-0.svg"), "<svg/>");
        put(
            &dir.join("given.json"),
            &format!("[\"{}/fixture-0.svg\"]", dir.display()),
        );
    }

    fn key_of(root: &Path, dir: &Path, texts: &[&str]) -> String {
        let paths = vec![
            format!("{}/fixture-0.svg", dir.display()),
            "no-such-sheet.svg".to_owned(),
        ];
        key(&Inputs {
            tree: root,
            dir,
            cwd: &root.join("rust/mode_a"),
            texts,
            paths: &paths,
        })
    }

    #[test]
    fn the_key_moves_with_each_input_and_no_other() {
        let tmp = TempDir::new("mode-a-keep-key");
        let (root, dir) = (tmp.path().join("t"), tmp.path().join("d1"));
        scratch(&root, &dir);
        let texts = ["script", "python 3.14.4 shapely==2.1"];
        let first = key_of(&root, &dir, &texts);
        // each input moved, the key with it, and back
        for rel in [
            "t/l7r/diagram/tools/pack_audit/parse.py",
            "t/l7r/diagram/buildings/types.json",
            "t/l7r/diagram/interactive/assets/modals/hamlet/byre.md",
            "t/pool/magistracies/s/s.svg",
            "t/pool/magistracies/s/s.notes.md",
            "t/pool/magistracies/s/s.png",
            "t/tests/fixtures/s-red.svg",
            "t/legacy-hand-authored-pool/towns/u/u.json",
            "d1/fixture-0.svg",
            "t/rust/mode_a/no-such-sheet.svg",
            "t/pool/magistracies/n/n.json",
        ] {
            let at = tmp.path().join(rel);
            let was = std::fs::read(&at).ok();
            put(&at, "moved");
            assert_ne!(key_of(&root, &dir, &texts), first, "{rel}");
            if let Some(b) = was {
                std::fs::write(&at, b).unwrap();
            } else {
                std::fs::remove_file(&at).unwrap();
                let _ = std::fs::remove_dir(at.parent().unwrap());
            }
            assert_eq!(key_of(&root, &dir, &texts), first, "{rel}");
        }
        for (i, moved) in ["script2", "python 3.14.5", "stdin"].iter().enumerate() {
            let mut t: Vec<&str> = texts.to_vec();
            t.push("");
            t[i] = moved;
            assert_ne!(
                key_of(&root, &dir, &t),
                key_of(&root, &dir, &[texts[0], texts[1], ""])
            );
        }
        // a file it does not read moved: a cache, a file outside its trees
        for rel in [
            "l7r/diagram/__pycache__/parse.cpython-314.pyc",
            "docs/other.md",
            "rust/mode_a/src/lib.rs",
        ] {
            put(&root.join(rel), "moved");
            assert_eq!(key_of(&root, &dir, &texts), first, "{rel}");
        }
        // the same fixtures in another directory, their `given.json` naming it: the same key
        let other = tmp.path().join("d2-longer");
        scratch(&root, &other);
        assert_eq!(key_of(&root, &other, &texts), first);
    }

    #[test]
    fn a_keep_is_read_only_under_its_own_key() {
        let tmp = TempDir::new("mode-a-keep-read");
        let at = tmp.path().join("git/rust-tests/mode_a-lockstep");
        let (one, two) = (Path::new("/tmp/a-1"), Path::new("/tmp/b \"2\""));
        write(&at, "k1", br#"{"/tmp/a-1/s.svg": "at /tmp/a-1"}"#, one);
        let beside: Vec<_> = std::fs::read_dir(at.parent().unwrap()).unwrap().collect();
        assert_eq!(beside.len(), 1);
        assert_eq!(
            read(&at, "k1", two).unwrap(),
            br#"{"/tmp/b \"2\"/s.svg": "at /tmp/b \"2\""}"#
        );
        // a stale key, no keep, a keep that cannot be read
        assert_eq!(read(&at, "k2", one), None);
        assert_eq!(read(&tmp.path().join("none"), "k1", one), None);
        std::fs::write(&at, "no line").unwrap();
        assert_eq!(read(&at, "no line", one), None);
        std::fs::write(&at, b"k1\n\xff").unwrap();
        assert_eq!(read(&at, "k1", one), None);
        // an output that does not name its directory is not kept, nor one with nowhere to go
        std::fs::remove_file(&at).unwrap();
        write(&at, "k3", b"{}", one);
        assert!(!at.exists());
        let blocked = tmp.path().join("file");
        std::fs::write(&blocked, "").unwrap();
        write(&blocked.join("keep"), "k1", b"/tmp/a-1", one);
        assert!(blocked.is_file());
    }

    #[test]
    fn a_run_is_kept_and_then_read_and_a_failed_one_is_not() {
        let tmp = TempDir::new("mode-a-keep-run");
        let at = tmp.path().join("keep");
        let dir = tmp.path().join("d");
        let printed = format!("[\"{}\"]", dir.display());
        let sh = |script: &'static str| [OsStr::new("-c"), OsStr::new(script)];
        let (cat, warns, fails) = (sh("cat"), sh("cat; echo no >&2"), sh("exit 3"));
        let side = |args| Run {
            program: "sh",
            args,
            stdin: printed.as_bytes(),
        };
        // the run's stdin is what it prints: kept, then read back with no run
        let ran = end(
            begin(Some(&at), "k", &dir, &side(&cat)),
            Some(&at),
            "k",
            &dir,
        );
        assert_eq!(
            (ran.ok, ran.stderr.as_str(), ran.stdout.as_slice(), ran.ran),
            (true, "", printed.as_bytes(), true)
        );
        let kept = end(
            begin(Some(&at), "k", &dir, &side(&fails)),
            Some(&at),
            "k",
            &dir,
        );
        assert_eq!((kept.ok, kept.stdout, kept.ran), (true, ran.stdout, false));
        // a run that writes to stderr is not kept, nor one with no git directory
        let warned = end(
            begin(Some(&at), "k2", &dir, &side(&warns)),
            Some(&at),
            "k2",
            &dir,
        );
        assert_eq!((warned.ok, warned.stderr.as_str()), (true, "no\n"));
        assert_eq!(read(&at, "k2", &dir), None);
        let bare = end(begin(None, "k", &dir, &side(&fails)), None, "k", &dir);
        assert_eq!((bare.ok, bare.ran), (false, true));
    }

    #[test]
    fn the_keep_lives_in_the_git_directory_and_the_interpreter_is_named() {
        let tmp = TempDir::new("mode-a-keep-place");
        assert_eq!(place(tmp.path()), None);
        let real = Path::new(env!("CARGO_MANIFEST_DIR"));
        assert!(place(real).unwrap().ends_with("rust-tests/mode_a-lockstep"));
        assert_eq!(identity("true").as_deref(), Some(""));
        assert_eq!(identity("false"), None);
        assert_eq!(identity("/no/such/python3-t178"), None);
    }
}
