//! `make format FILE=<path>` (feature 451 T34): rustfmt over the files named and nothing else. `make format` formats every crate, so a
//! builder beside another's in-progress files formatted with a bare `rustfmt` outside make instead (four builders, 2026-11-20).
//!
//! The file goes to rustfmt on its standard input: given a path, rustfmt formats every `mod` child the file declares as well (measured
//! 2026-11-20, a scratch crate whose `main.rs` declared `mod k;`: `rustfmt main.rs` rewrote `k.rs`, the same file on standard input left
//! it). rustfmt runs from the file's directory, where it finds a `rustfmt.toml` as `cargo fmt` would, with the edition of the crate
//! that owns the file, which `cargo fmt` passes too; the file is written only where rustfmt passed and changed it, so a formatted
//! file's time stays and no kept result moves. It writes no build, so it takes no run lock (`locked_dispatch`): a one-file format
//! never waits on another run's tests.

use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::{phase, re, World};
use crate::Reply;

static EDITION: LazyLock<Regex> = LazyLock::new(|| re(r#"(?m)^\s*edition\s*=\s*"([0-9]+)""#));

const FORM: &str = "make format FILE=<path> (one file, or several: FILE=\"a.rs b.rs\") | make format CRATE=<dir> (one crate)";

fn usage(why: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("l7r-gate rust format --file: {why}\nusage: {FORM}\n"),
        code: 2,
    }
}

/// The words of a run naming `--file`: the files and `--check`, or the usage where they are not a format's alone.
fn parse(args: &[String]) -> Result<(Vec<String>, bool), Reply> {
    if args.first().map(String::as_str) != Some("format") {
        return Err(usage(
            "--file names a file to format; no other check takes it",
        ));
    }
    let (mut files, mut check, mut rest) = (Vec::new(), false, args[1..].iter());
    while let Some(word) = rest.next() {
        match word.as_str() {
            "--check" => check = true,
            "--file" => files.push(
                rest.next()
                    .ok_or_else(|| usage("--file wants a path"))?
                    .clone(),
            ),
            "--crate" => return Err(usage("FILE= and CRATE= together - name one")),
            other => return Err(usage(&format!("{other} is not a word of it"))),
        }
    }
    Ok((files, check))
}

/// The toolchain's rustfmt, as `cargo_exe` finds cargo: the installed one, else the one on the path.
pub(super) fn rustfmt_exe(toolchain: &Path) -> String {
    let installed = toolchain.join("rustfmt");
    if installed.is_file() {
        installed.display().to_string()
    } else {
        "rustfmt".to_owned()
    }
}

/// The crate that owns `file` under the tree's root: the nearest `Cargo.toml` above it that holds a package, and that package's edition
/// (2015, rustfmt's and cargo's default, where it names none).
fn owner(root: &Path, file: &Path) -> Result<(PathBuf, String), String> {
    let manifest = file
        .ancestors()
        .skip(1)
        .take_while(|d| d.starts_with(root))
        .map(|d| d.join("Cargo.toml"))
        .find(|m| std::fs::read_to_string(m).is_ok_and(|t| t.contains("[package]")))
        .ok_or("no crate under the tree owns it")?;
    let text = std::fs::read_to_string(&manifest).unwrap_or_default();
    match EDITION
        .captures(&text)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
    {
        Some(e) => Ok((manifest, e.as_str().to_owned())),
        None if !text.contains("edition") => Ok((manifest, "2015".to_owned())),
        None => Err(format!(
            "its edition is not a literal in {} - name it there as edition = \"2021\"",
            manifest.display()
        )),
    }
}

/// rustfmt over `text` on its standard input, from `dir`: its output, or its words where it failed.
fn rustfmt(world: &World, dir: &Path, edition: &str, text: &str) -> Result<String, String> {
    let spawned = Command::new(rustfmt_exe(&world.path_dir))
        .args(["--edition", edition])
        .current_dir(dir)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn();
    let mut child = match spawned {
        Ok(child) => child,
        Err(e) => return Err(format!("cannot start rustfmt: {e}\n")),
    };
    // rustfmt reads the whole input before it writes, so the input is written whole before the output is read
    if let Some(mut stdin) = child.stdin.take() {
        let _ = stdin.write_all(text.as_bytes());
    }
    // a wait that fails is a failed run with no words of its own
    let out = child.wait_with_output().ok();
    let passed = out.as_ref().is_some_and(|o| o.status.success());
    let (stdout, stderr) = out.map(|o| (o.stdout, o.stderr)).unwrap_or_default();
    if passed {
        Ok(String::from_utf8_lossy(&stdout).into_owned())
    } else {
        Err(String::from_utf8_lossy(&stderr).into_owned())
    }
}

/// One file formatted, or checked: its line for the reply, and whether it failed.
fn one(world: &World, named: &str, check: bool) -> Result<(String, bool), String> {
    let file = world.root.join(named);
    let shown = file
        .strip_prefix(&world.root)
        .unwrap_or(&file)
        .display()
        .to_string();
    if !file.is_file() {
        return Err(format!("{named}: no such file"));
    }
    if file.extension().and_then(|e| e.to_str()) != Some("rs") {
        return Err(format!("{named}: not a Rust file"));
    }
    let (manifest, edition) = owner(&world.root, &file).map_err(|why| format!("{named}: {why}"))?;
    let text = std::fs::read_to_string(&file).map_err(|e| format!("{named}: {e}"))?;
    let began = std::time::SystemTime::now();
    let dir = file.parent().unwrap_or(&world.root);
    let got = rustfmt(world, dir, &edition, &text);
    let changes = got.as_ref().is_ok_and(|g| *g != text);
    let failed = got.is_err() || (check && changes);
    phase::wrote(world, "format", &[&manifest], began, i32::from(failed));
    Ok(match got {
        Err(words) => (format!("rust-checks: format FAILED on {shown}\n{words}"), true),
        Ok(_) if !changes => (format!("rust-checks: format on {shown}: already formatted\n"), false),
        Ok(_) if check => (
            format!("rust-checks: format FAILED on {shown}: rustfmt would change it - run `make format FILE={shown}`\n"),
            true,
        ),
        Ok(formatted) => match std::fs::write(&file, formatted) {
            Ok(()) => (format!("rust-checks: format on {shown}: formatted\n"), false),
            Err(e) => (format!("rust-checks: format FAILED on {shown}: {e}\n"), true),
        },
    })
}

/// `l7r-gate rust format --file PATH... [--check]`: each file named, alone.
pub(super) fn format_files(world: &World, args: &[String]) -> Reply {
    let (files, check) = match parse(args) {
        Ok(parsed) => parsed,
        Err(reply) => return reply,
    };
    let (mut stdout, mut stderr, mut bad) = (String::new(), String::new(), 0);
    for named in &files {
        match one(world, named, check) {
            Err(why) => return usage(&why),
            Ok((line, false)) => stdout.push_str(&line),
            Ok((line, true)) => {
                bad += 1;
                stderr.push_str(&line);
            }
        }
    }
    Reply {
        stdout,
        stderr,
        code: i32::from(bad > 0),
    }
}
