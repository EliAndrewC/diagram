//! A LINK ON A MIXED INCREMENTAL SESSION, healed once (feature 451 T336). A rustc killed past its front end - a build cut short by
//! the first pre-warm (`prewarm.rs`), a command's timeout, an interrupt - can leave the crate's last FINISHED incremental session
//! written into, and every later build of that crate then fails its link - `rust-lld: error: undefined hidden symbol: ...
//! .llvm.<n>`, referenced from `<crate>-<hash>.<unit>.rcgu.o` - until the crate's incremental directories are removed: a builder
//! met it as a test build red twice on code that was right, and found a directory by hand (2026-11-26). Measured the same day in
//! a pool tree on `rust/guard`: 29 of 54 tries with a build cut failed so (by SIGTERM, SIGINT and SIGKILL), 0 of 20 left to finish,
//! and each of the 29 built once the crate's incremental directories were gone (`dev/measurements/2026-11-26/prewarm-link/`). Shown:
//! a cut build changes files of the finished session in place (same inode). INFERRED, not read in rustc: that the working
//! session's files are hard links of the finished one's, written in place under the dev profile's `opt-level = 2`.
//!
//! So the test build that fails this way (`built`, asked by `stepped`) drops EVERY incremental directory of each crate the linker
//! names (`<profile>/incremental/<crate>-*`: what healed 29 of 29; the one directory holding the named unit healed once on the
//! day and was not measured, so the narrower drop is not taken) and each named build's fingerprint (so an rlib built from the mix
//! is rebuilt too, as the launcher's retry does), under cargo's own lock of the build directory, and asks the build ONCE more,
//! never again: the crate compiles from nothing (`rust/guard` 22 to 44 s against an 11 s incremental build). It writes a `Phase`
//! line, step `link-heal` (`phase.rs`), spanning the drop and the second build, inside the `build` line's span. The launcher
//! does the same for the tools' own build (`scripts/gates/l7r-gate.sh`, feature 451 T142); the guard's launcher (451 T146) and
//! the coverage build (451 T206) do not yet.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::time::SystemTime;

use super::{cargo, phase, Ran, World};

/// The linker's words for it.
const SIGN: &str = "undefined hidden symbol";
/// The `Phase` step of a heal: the drop and the one build after it.
pub(super) const STEP: &str = "link-heal";
/// The seconds it waits for cargo's lock of a build directory (GUESS, a knob): past the longest single crate's build measured,
/// 82.7 s (451 T316), which a pre-warm finishing its crate in the tree can hold it for.
pub(super) const LOCK_S: f64 = 120.0;

/// What the linker's words name, under this tree's target directory.
#[derive(Default)]
struct Named {
    /// The build directories (`<target>/<profile>`), whose `.cargo-lock` is held for the drop.
    profiles: BTreeSet<PathBuf>,
    /// Every incremental directory of each named crate.
    sessions: BTreeSet<PathBuf>,
    /// Each named build's fingerprint.
    prints: BTreeSet<PathBuf>,
}

/// A unit is `<crate>-<hash>.<unit>.rcgu.o`, met as a path under `<profile>/deps/` or as a member of an rlib whose path came just
/// before it.
fn named(world: &World, stderr: &str) -> Named {
    let target = world
        .target_override
        .as_ref()
        .map_or_else(|| world.target.clone(), PathBuf::from);
    let mut found = Named::default();
    let mut profile: Option<PathBuf> = None;
    for word in stderr.split(|c: char| c.is_whitespace() || matches!(c, ':' | '(' | ')' | '"')) {
        let path = Path::new(word);
        let deps = path.parent().filter(|d| d.ends_with("deps"));
        if let Some(dir) = deps.and_then(Path::parent) {
            profile = dir.starts_with(&target).then(|| dir.to_path_buf());
        }
        let build = path
            .file_name()
            .and_then(|n| n.to_str())
            .and_then(|n| n.strip_suffix(".rcgu.o"))
            .and_then(|n| n.rsplit_once('.'))
            .and_then(|(build, _unit)| build.rsplit_once('-'));
        let (Some(dir), Some((krate, hash))) = (&profile, build) else {
            continue;
        };
        found.profiles.insert(dir.clone());
        found.sessions.extend(
            entries(&dir.join("incremental"))
                .into_iter()
                .filter(|d| name(d).starts_with(&format!("{krate}-"))),
        );
        found.prints.extend(
            entries(&dir.join(".fingerprint"))
                .into_iter()
                .filter(|d| name(d).ends_with(&format!("-{hash}"))),
        );
    }
    found
}

fn entries(dir: &Path) -> Vec<PathBuf> {
    std::fs::read_dir(dir)
        .map(|all| all.flatten().map(|e| e.path()).collect())
        .unwrap_or_default()
}

fn name(path: &Path) -> String {
    path.file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned()
}

/// A crate's test build (`cargo test --no-run`, `args`), its link on a mixed session healed once. A heal that linked is said here,
/// on the gate's own stderr: `stepped` goes on to the run and keeps nothing a green build said.
pub(super) fn built(world: &World, args: &[&str], manifest: &Path) -> Ran {
    let first = cargo(world, args, manifest, &[]);
    let red = first.code != 0;
    let done = healed(world, manifest, first, LOCK_S, &mut || {
        cargo(world, args, manifest, &[])
    });
    if red && done.code == 0 {
        eprint!("{}", done.stderr);
    }
    done
}

/// `built`, a crate's test build: where its link failed on a mixed session, the named crates' incremental directories are dropped
/// and `again` asked, once; its answer is the build's, under a line that says what was done. Any other result comes back as it
/// is, and so does this one where no incremental directory is named (a fingerprint alone dropped would rebuild from the same
/// session) or cargo's lock is not had.
pub(super) fn healed(
    world: &World,
    manifest: &Path,
    built: Ran,
    lock_s: f64,
    again: &mut dyn FnMut() -> Ran,
) -> Ran {
    if built.code == 0 || !built.stderr.contains(SIGN) {
        return built;
    }
    let began = SystemTime::now();
    let mut note = "l7r-gate rust: the link failed on a mixed incremental session (rust-lld: undefined hidden symbol) - a build of this crate was killed while rustc compiled it (feature 451 T336)".to_owned();
    let found = named(world, &built.stderr);
    let held: Vec<_> = found
        .profiles
        .iter()
        .filter_map(|p| l7r_shared::tool::flock_within(&p.join(".cargo-lock"), lock_s).ok()?)
        .collect();
    if found.sessions.is_empty() || held.len() < found.profiles.len() {
        let _ = writeln!(note, "; nothing was dropped (the linker names no crate with an incremental directory under this tree's target directory, or another cargo held the build directory for {lock_s} s). The repair: remove the crate's directories under <target>/debug/incremental/ (<crate>-*) and run again. The link's own words:");
        return Ran {
            stderr: format!("{note}{}", built.stderr),
            ..built
        };
    }
    for path in found.sessions.iter().chain(&found.prints) {
        let _ = std::fs::remove_dir_all(path);
    }
    drop(held);
    let second = again();
    phase::wrote(world, STEP, &[manifest], began, second.code);
    let shown: Vec<String> = found
        .sessions
        .iter()
        .chain(&found.prints)
        .map(|p| {
            let last: Vec<_> = p.iter().rev().take(2).collect();
            format!("{}/{}", last[1].to_string_lossy(), name(p))
        })
        .collect();
    let _ = writeln!(
        note,
        "; dropped {} and built again: {}",
        shown.join(", "),
        if second.code == 0 {
            "linked"
        } else {
            "that build failed too, in cargo's words below"
        }
    );
    Ran {
        stderr: format!("{note}{}", second.stderr),
        ..second
    }
}
