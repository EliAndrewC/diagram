//! The host's one working copy of the archive repository (`archive.py`'s `Archive`; ported by feature 449 T146), written and pushed under
//! the host-wide lock. ONE WORKING COPY on the host (the GM: *"you can just push directly to it without each of our diagram .clones/
//! having its own copy"*): `<mirror>/.specify/source-archive/`, written under `<mirror>/.specify/source-archive.lock`, pushed straight to
//! GitHub. The PAT reaches git as `GIT_CONFIG_*` environment entries, never on a command line, in a file or in a log (FR-011).
//!
//! This is the working copy's one writer (FR-003): Python's `archive.Archive` keeps only the lock, `git` and the reads until S4, and
//! its one write left, the push, forwards here (`l7r-gate record archive push`; T147 retired `ensure` and `place-gm` with S3b).

use std::path::{Path, PathBuf};
use std::process::{Command, Output};

use crate::{Error, Result};

pub const WORKDIR: &str = "source-archive";
pub const LOCK: &str = "source-archive.lock";
pub const UNPUSHED: &str = "source-archive.unpushed";

/// The environment that authenticates git to GitHub with the PAT as an extra header (FR-011): the process's own, every `GIT_CONFIG_*`
/// replaced.
#[must_use]
pub fn git_env(token: &str) -> Vec<(String, String)> {
    let basic = b64(format!("x-access-token:{token}").as_bytes());
    vec![
        ("GIT_CONFIG_COUNT".into(), "1".into()),
        (
            "GIT_CONFIG_KEY_0".into(),
            "http.https://github.com/.extraheader".into(),
        ),
        (
            "GIT_CONFIG_VALUE_0".into(),
            format!("AUTHORIZATION: basic {basic}"),
        ),
        ("GIT_TERMINAL_PROMPT".into(), "0".into()),
    ]
}

/// The push's credential: the gate's `github-token`, run where the Python ran it (in the mirror), its stdout stripped; empty where the
/// tree has none (the push then reports its own failure).
#[cfg(not(test))]
#[must_use]
pub fn token(root: &Path) -> String {
    token_from(
        &l7r_gate_core::record::repo::tree_of(root).join("scripts/gates/l7r-gate.sh"),
        &l7r_gate_core::record::repo::mirror_of(root),
    )
}

/// [`token`] from the launcher `gate`, run in `mirror`.
#[must_use]
pub fn token_from(gate: &Path, mirror: &Path) -> String {
    Command::new(gate)
        .arg("github-token")
        .current_dir(mirror)
        .output()
        .map_or_else(
            |_| String::new(),
            |o| l7r_guard::shared::py_text::strip(&String::from_utf8_lossy(&o.stdout)).to_owned(),
        )
}

/// The working copy and how git reaches its remote.
#[derive(Debug, Clone)]
pub struct Archive {
    pub home: PathBuf,
    pub dir: PathBuf,
    pub remote: String,
    /// `None`: the process's own environment, as the Python's `env=None`; otherwise the PAT's entries over it.
    pub env: Option<Vec<(String, String)>>,
    /// The GM's downloads, where [`crate::manifest::place_gm`] copies from (`L7R_GM_SOURCES`, read once here).
    pub gm: PathBuf,
    /// The git run (`git`; a test names one that fails as git can).
    pub git_program: String,
}

/// The repository's remote (`rec.REPO + ".git"`).
#[must_use]
pub fn remote() -> String {
    format!("{}.git", l7r_gate_research::record::archive::REPO)
}

fn os_error(e: &std::io::Error, what: &Path) -> Error {
    Error::new("OSError", format!("{e}: '{}'", what.display()))
}

impl Archive {
    #[must_use]
    pub fn new(home: &Path, env: Option<Vec<(String, String)>>) -> Self {
        Self {
            home: home.to_path_buf(),
            dir: home.join(WORKDIR),
            remote: remote(),
            env,
            gm: crate::manifest::gm_dir(),
            git_program: "git".to_owned(),
        }
    }

    /// The lock, held while the returned file is open (`flock`, polled every 20 ms): a `TimeoutError` past `timeout` seconds.
    ///
    /// # Errors
    /// The lock file cannot be made, or the lock is not had in time.
    pub fn locked(&self, timeout: f64) -> Result<std::fs::File> {
        let at = self.home.join(LOCK);
        match l7r_guard::shared::tool::flock_within(&at, timeout) {
            Ok(Some(f)) => Ok(f),
            Ok(None) => Err(Error::new(
                "TimeoutError",
                format!("could not take {} within {}s", at.display(), py_g(timeout)),
            )),
            Err(e) => Err(os_error(&e, &at)),
        }
    }

    fn command(&self, args: &[&str]) -> Command {
        let mut cmd = Command::new(&self.git_program);
        cmd.args(args);
        if let Some(env) = &self.env {
            for (k, _) in std::env::vars().filter(|(k, _)| k.starts_with("GIT_CONFIG_")) {
                cmd.env_remove(k);
            }
            cmd.envs(env.iter().map(|(k, v)| (k, v)));
        }
        cmd
    }

    /// `git -C <dir> <args>`, its output; with `check`, a failure is `CalledProcessError`.
    ///
    /// # Errors
    /// git cannot start, or (with `check`) exits non-zero.
    pub fn git(&self, args: &[&str], check: bool) -> Result<Output> {
        let dir = self.dir.to_string_lossy().into_owned();
        let mut all = vec!["-C", dir.as_str()];
        all.extend_from_slice(args);
        let out = self
            .command(&all)
            .output()
            .map_err(|e| os_error(&e, Path::new("git")))?;
        if check && !out.status.success() {
            return Err(Error::new(
                "CalledProcessError",
                format!(
                    "Command '{}' returned non-zero exit status {}.",
                    py_list(
                        &["git"]
                            .into_iter()
                            .chain(all.iter().copied())
                            .collect::<Vec<_>>()
                    ),
                    out.status.code().unwrap_or(-1)
                ),
            ));
        }
        Ok(out)
    }

    /// Clone the repository once; an empty one is initialized on `main` with its remote.
    ///
    /// # Errors
    /// The clone fails (`RuntimeError`), or a git step after it.
    pub fn ensure(&self) -> Result<()> {
        if self.dir.join(".git").is_dir() {
            return Ok(());
        }
        let up = self.dir.parent().unwrap_or(&self.dir);
        std::fs::create_dir_all(up).map_err(|e| os_error(&e, up))?;
        let dir = self.dir.to_string_lossy().into_owned();
        let done = self
            .command(&["clone", "-q", &self.remote, &dir])
            .output()
            .map_err(|e| os_error(&e, Path::new("git")))?;
        if !done.status.success() {
            let said = String::from_utf8_lossy(&done.stderr);
            return Err(Error::new(
                "RuntimeError",
                format!(
                    "could not clone the archive: {}",
                    first_chars(l7r_guard::shared::py_text::strip(&said), 300)
                ),
            ));
        }
        if !self
            .git(&["rev-parse", "--verify", "-q", "HEAD"], false)?
            .status
            .success()
        {
            self.git(&["checkout", "-q", "-b", "main"], true)?;
        }
        self.git(&["config", "user.name", "diagram source archive"], true)?;
        self.git(&["config", "user.email", "noreply@anthropic.com"], true)?;
        Ok(())
    }

    /// The bytes committed and not yet pushed, as the counter file says (0 where it is missing or not a number).
    #[must_use]
    pub fn unpushed(&self) -> u64 {
        std::fs::read_to_string(self.home.join(UNPUSHED))
            .ok()
            .and_then(|t| l7r_guard::shared::py_text::strip(&t).parse().ok())
            .unwrap_or(0)
    }

    fn count(&self, n: u64) -> Result<()> {
        let at = self.home.join(UNPUSHED);
        std::fs::write(&at, n.to_string()).map_err(|e| os_error(&e, &at))
    }

    /// Write `files` under `rel` and commit them (call under the lock); returns the directory used - `rel`, or `rel-2`, `rel-3` ...
    /// where a capture in the same second already holds it (FR-009: never over an earlier one).
    ///
    /// # Errors
    /// A write or a git step.
    pub fn put(&self, rel: &str, files: &[(String, Vec<u8>)], message: &str) -> Result<String> {
        let mut used = rel.to_owned();
        let mut n = 1;
        while self.dir.join(&used).exists() {
            n += 1;
            used = format!("{rel}-{n}");
        }
        let d = self.dir.join(&used);
        std::fs::create_dir_all(&d).map_err(|e| os_error(&e, &d))?;
        for (name, body) in files {
            std::fs::write(d.join(name), body).map_err(|e| os_error(&e, &d.join(name)))?;
        }
        self.git(&["add", "--", &used], true)?;
        self.git(&["commit", "-q", "-m", message], true)?;
        let total: usize = files.iter().map(|(_, b)| b.len()).sum();
        self.count(self.unpushed() + u64::try_from(total).unwrap_or(u64::MAX))?;
        Ok(used)
    }

    /// Copy the GM's file or folder to `rel` once (call under the lock); false where it is already there.
    ///
    /// # Errors
    /// A copy or a git step.
    pub fn copy_in(&self, rel: &str, source: &Path) -> Result<bool> {
        let dest = self.dir.join(rel);
        if dest.exists() {
            return Ok(false);
        }
        let up = dest.parent().unwrap_or(&dest);
        std::fs::create_dir_all(up).map_err(|e| os_error(&e, up))?;
        let bytes = copy_tree(source, &dest)?;
        self.git(&["add", "--", rel], true)?;
        self.git(
            &[
                "commit",
                "-q",
                "-m",
                &format!("the GM's downloaded copy: {rel}"),
            ],
            true,
        )?;
        self.count(self.unpushed() + bytes)?;
        Ok(true)
    }

    /// Write and commit one file at `rel` (call under the lock), where nothing is yet.
    ///
    /// # Errors
    /// A write or a git step.
    pub fn put_file(&self, rel: &str, body: &[u8], message: &str) -> Result<()> {
        let at = self.dir.join(rel);
        if at.exists() {
            return Ok(());
        }
        let up = at.parent().unwrap_or(&at);
        std::fs::create_dir_all(up).map_err(|e| os_error(&e, up))?;
        std::fs::write(&at, body).map_err(|e| os_error(&e, &at))?;
        self.git(&["add", "--", rel], true)?;
        self.git(&["commit", "-q", "-m", message], true)?;
        self.count(self.unpushed() + u64::try_from(body.len()).unwrap_or(u64::MAX))
    }

    /// Push `main` (call under the lock); empty on success or with nothing committed yet, else git's complaint.
    ///
    /// # Errors
    /// git cannot start, or the counter cannot be written.
    pub fn push(&self) -> Result<String> {
        if !self
            .git(&["rev-parse", "--verify", "-q", "HEAD"], false)?
            .status
            .success()
        {
            return Ok(String::new());
        }
        let done = self.git(&["push", "-q", "origin", "HEAD:main"], false)?;
        if !done.status.success() {
            let said = String::from_utf8_lossy(&done.stderr);
            let said = first_chars(l7r_guard::shared::py_text::strip(&said), 300);
            return Ok(if said.is_empty() {
                format!("git push exited {}", done.status.code().unwrap_or(-1))
            } else {
                said
            });
        }
        self.count(0)?;
        Ok(String::new())
    }
}

/// `shutil.copytree` or `shutil.copy2` of `source` to `dest`: the bytes of every file copied.
fn copy_tree(source: &Path, dest: &Path) -> Result<u64> {
    if source.is_dir() {
        std::fs::create_dir_all(dest).map_err(|e| os_error(&e, dest))?;
        let mut total = 0;
        let mut entries: Vec<PathBuf> = std::fs::read_dir(source)
            .map_err(|e| os_error(&e, source))?
            .flatten()
            .map(|e| e.path())
            .collect();
        entries.sort();
        for p in entries {
            let name = p.file_name().map(PathBuf::from).unwrap_or_default();
            total += copy_tree(&p, &dest.join(name))?;
        }
        return Ok(total);
    }
    // `shutil.copy2` kept the file's times too; git keeps none, so nothing the archive holds depends on them
    std::fs::copy(source, dest).map_err(|e| os_error(&e, source))
}

/// `base64.b64encode`.
#[must_use]
pub fn b64(data: &[u8]) -> String {
    const ALPHABET: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let mut out = String::with_capacity(data.len().div_ceil(3) * 4);
    for chunk in data.chunks(3) {
        let b = [
            chunk[0],
            *chunk.get(1).unwrap_or(&0),
            *chunk.get(2).unwrap_or(&0),
        ];
        let n = (u32::from(b[0]) << 16) | (u32::from(b[1]) << 8) | u32::from(b[2]);
        for i in 0..4 {
            if i <= chunk.len() {
                out.push(char::from(ALPHABET[((n >> (18 - 6 * i)) & 63) as usize]));
            } else {
                out.push('=');
            }
        }
    }
    out
}

/// The first `n` characters (Python's `[:n]`).
#[must_use]
pub fn first_chars(text: &str, n: usize) -> String {
    text.chars().take(n).collect()
}

/// `f"{x:g}"` for a timeout.
fn py_g(x: f64) -> String {
    l7r_guard::shared::pyjson::py_float(x)
        .trim_end_matches(".0")
        .to_owned()
}

/// A list of strings as Python's `repr` writes it.
fn py_list(items: &[&str]) -> String {
    let inner: Vec<String> = items
        .iter()
        .map(|s| l7r_guard::shared::pyjson::value_repr(&serde_json::json!(s)))
        .collect();
    format!("[{}]", inner.join(", "))
}

#[cfg(test)]
mod tests;
