//! The engines a live map is drawn by, and each one's identity (feature 449 T221, from `specs/449-rust-codebase/derivations/T219-pipeline.md`,
//! Keep 4: the engine's identity is its binary, taken once a run, never its sources per map).
//!
//! Two engines: the hamlet driver (`rust/phases`' `hamlet`, which reads its spec and nothing else) and the Mode A engine (`l7r-mode-a`,
//! whose `hand-sheet` and `compound` draw the sheets and report every file they read). Each is identified by its binary's GNU build id, a
//! hash the linker takes over the linked output, so any change to the engine or to what is compiled into it (the hamlet's knobs and tables)
//! moves it; a binary with no such note is hashed whole (the derivation's assumption 4).
//!
//! A STALE BINARY IS NO ENGINE: an id read from a binary older than its sources would answer CACHED after an engine edit. The binary is asked
//! of `scripts/gates/l7r-gate.sh <engine>` with `L7R_GATE_PRINT_FRESH=1`, which builds it where it is stale and prints its path; a check
//! that must not build (the review gate's in-process question, [`super::is_current`]) asks with `L7R_GATE_STALE_OK=1` too, which builds
//! none and prints nothing for a stale binary - and a map whose engine cannot be named fresh is not current.
//!
//! Research: plumbing - NONE: names and identifies the engine binaries, deciding nothing about a map

use std::fmt::Write as _;
use std::io::{Read as _, Seek as _, SeekFrom};
use std::path::{Path, PathBuf};
use std::process::Command;

use crate::walk::Kind;

/// An engine that draws live maps.
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum Engine {
    Hamlet,
    ModeA,
}

impl Engine {
    /// The engine a map of `kind` is drawn by, or None (a frozen exhibit, an unclassified folder).
    #[must_use]
    pub fn of(kind: Kind) -> Option<Self> {
        match kind {
            Kind::Hamlet => Some(Self::Hamlet),
            Kind::Compound | Kind::HandSheet => Some(Self::ModeA),
            Kind::Frozen | Kind::Report => None,
        }
    }

    /// The engine's word to `l7r-gate.sh`, and its name in an entry's meta.
    #[must_use]
    pub fn word(self) -> &'static str {
        match self {
            Self::Hamlet => "hamlet",
            Self::ModeA => "mode-a",
        }
    }
}

/// Where an engine's binary is: the launcher's fresh build in a run, a stand-in in a test.
pub trait Binaries {
    /// The engine's binary, fresh.
    ///
    /// # Errors
    /// No fresh binary can be named: its build failed, or (a check that builds none) it is stale.
    fn binary(&mut self, engine: Engine) -> Result<PathBuf, String>;
}

/// The launcher, `scripts/gates/l7r-gate.sh <engine>`, asked for each engine's fresh binary; `build` false builds none.
pub struct Launcher {
    pub root: PathBuf,
    pub build: bool,
}

impl Binaries for Launcher {
    fn binary(&mut self, engine: Engine) -> Result<PathBuf, String> {
        let mut cmd = Command::new(self.root.join("scripts/gates/l7r-gate.sh"));
        cmd.arg(engine.word())
            .env("L7R_GATE_PRINT_FRESH", "1")
            .current_dir(&self.root);
        if self.build {
            cmd.env_remove("L7R_GATE_STALE_OK")
                .env_remove("L7R_GATE_NO_BUILD");
        } else {
            // neither a stale binary built nor a missing one: the launcher builds where there is none unless told not to
            cmd.env("L7R_GATE_STALE_OK", "1")
                .env("L7R_GATE_NO_BUILD", "1");
        }
        let done = cmd
            .output()
            .map_err(|e| format!("the {} engine's launcher did not start: {e}", engine.word()))?;
        let path = String::from_utf8_lossy(&done.stdout).trim().to_owned();
        if done.status.success() && !path.is_empty() {
            return Ok(PathBuf::from(path));
        }
        Err(if self.build {
            format!(
                "the {} engine could not be built - fix what the build names: {}",
                engine.word(),
                String::from_utf8_lossy(&done.stderr).trim()
            )
        } else {
            format!(
                "the {} engine's binary is older than its sources (built by the next make map)",
                engine.word()
            )
        })
    }
}

/// Bytes 64 a block: the derivation's unit of hashing.
pub const BLOCK: u64 = 64;

/// A little-endian integer of `n` bytes at `at` of `b`.
fn le(b: &[u8], at: usize, n: usize) -> Option<u64> {
    let bytes = b.get(at..at + n)?;
    Some(
        bytes
            .iter()
            .rev()
            .fold(0u64, |acc, x| (acc << 8) | u64::from(*x)),
    )
}

/// The GNU build id of the 64-bit little-endian ELF file at `path`, hex, from its program headers' notes; None where it has none.
fn gnu_build_id(path: &Path) -> Option<String> {
    let mut f = std::fs::File::open(path).ok()?;
    let mut head = [0u8; 64];
    f.read_exact(&mut head).ok()?;
    if head[..4] != *b"\x7fELF" || head[4] != 2 || head[5] != 1 {
        return None;
    }
    let (phoff, phentsize, phnum) = (
        le(&head, 0x20, 8)?,
        le(&head, 0x36, 2)?,
        le(&head, 0x38, 2)?,
    );
    let mut table = vec![0u8; usize::try_from(phentsize * phnum).ok()?];
    f.seek(SeekFrom::Start(phoff)).ok()?;
    f.read_exact(&mut table).ok()?;
    for ph in table.chunks(usize::try_from(phentsize).ok()?) {
        // PT_NOTE
        if le(ph, 0, 4)? != 4 {
            continue;
        }
        let (offset, size) = (le(ph, 0x08, 8)?, le(ph, 0x20, 8)?);
        let mut notes = vec![0u8; usize::try_from(size).ok()?];
        f.seek(SeekFrom::Start(offset)).ok()?;
        f.read_exact(&mut notes).ok()?;
        let mut at = 0usize;
        while at + 12 <= notes.len() {
            let namesz = usize::try_from(le(&notes, at, 4)?).ok()?;
            let descsz = usize::try_from(le(&notes, at + 4, 4)?).ok()?;
            let kind = le(&notes, at + 8, 4)?;
            let name_at = at + 12;
            let desc_at = name_at + namesz.next_multiple_of(4);
            let next = desc_at + descsz.next_multiple_of(4);
            // NT_GNU_BUILD_ID, its owner "GNU\0"
            if kind == 3 && notes.get(name_at..name_at + namesz) == Some(b"GNU\0") {
                let desc = notes.get(desc_at..desc_at + descsz)?;
                return Some(desc.iter().fold(String::new(), |mut s, b| {
                    let _ = write!(s, "{b:02x}");
                    s
                }));
            }
            at = next;
        }
    }
    None
}

/// The engine binary's identity: `gnu:<its build id>`, or `sha256:<the whole file's>` for a binary without the note, with the bytes it
/// hashed for that (0 for a build id).
///
/// # Errors
/// The binary cannot be read.
pub fn identity(path: &Path) -> Result<(String, u64), String> {
    if let Some(id) = gnu_build_id(path) {
        return Ok((format!("gnu:{id}"), 0));
    }
    let bytes = std::fs::read(path).map_err(|e| format!("{}: {e}", path.display()))?;
    Ok((
        format!("sha256:{}", l7r_shared::sha256::hex(&bytes)),
        bytes.len() as u64,
    ))
}

/// What an engine's run said.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Ran {
    pub code: i32,
    pub stdout: String,
    pub stderr: String,
}

/// `binary args...` run from the tree's root with the tree named to it (`L7R_GATE_TREE`, the launcher's), its output kept.
///
/// # Errors
/// The binary did not start.
pub fn run(root: &Path, binary: &Path, args: &[String]) -> Result<Ran, String> {
    let done = Command::new(binary)
        .args(args)
        .env("L7R_GATE_TREE", root)
        .current_dir(root)
        .output()
        .map_err(|e| format!("{} did not start: {e}", binary.display()))?;
    Ok(Ran {
        code: done.status.code().unwrap_or(-1),
        stdout: String::from_utf8_lossy(&done.stdout).into_owned(),
        stderr: String::from_utf8_lossy(&done.stderr).into_owned(),
    })
}

#[cfg(test)]
mod tests;
