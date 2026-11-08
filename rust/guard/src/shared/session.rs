//! The session's facts, each read once a process and handed to every guard (plan D6): the mirror (`derive_main`), and the session's
//! clone (`clone-sync-hooks.sh resolve`: the claim map, else the transcript's last `/rename`, else the sessions json). Each read is
//! counted, so a test pins it to once.

use std::cell::{Cell, OnceCell};
use std::path::{Path, PathBuf};

use serde_json::Value;

/// One event's session facts, read lazily and once.
pub struct Session {
    pub id: String,
    pub cwd: String,
    pub transcript: String,
    /// The `CLONE_MAIN` and `CLONE_SESSIONS_DIR` test seams, read from the environment by `from_input`.
    pub main_seam: Option<String>,
    pub sessions_dir: PathBuf,
    main: OnceCell<PathBuf>,
    clone: OnceCell<Option<PathBuf>>,
    text: OnceCell<Option<String>>,
    messages: OnceCell<Vec<String>>,
    /// The file reads made, for the tests that pin them.
    pub reads: Cell<u32>,
}

impl Session {
    /// The facts of the hook `input`, with the test seams and `HOME` taken from the environment.
    #[must_use]
    pub fn from_input(input: &Value) -> Self {
        Self::with_env(input, |k| std::env::var(k).ok())
    }

    /// The facts of `input` with the environment read through `env`.
    pub fn with_env(input: &Value, env: impl Fn(&str) -> Option<String>) -> Self {
        let field = |k: &str| {
            input
                .get(k)
                .and_then(Value::as_str)
                .unwrap_or("")
                .to_owned()
        };
        let home = env("HOME").unwrap_or_default();
        let sessions_dir = match env("CLONE_SESSIONS_DIR") {
            Some(d) => PathBuf::from(d),
            None => Path::new(&home).join(".claude/sessions"),
        };
        Self {
            id: field("session_id"),
            cwd: field("cwd"),
            transcript: field("transcript_path"),
            main_seam: env("CLONE_MAIN").and_then(non_empty),
            sessions_dir,
            main: OnceCell::new(),
            clone: OnceCell::new(),
            text: OnceCell::new(),
            messages: OnceCell::new(),
            reads: Cell::new(0),
        }
    }

    /// The mirror: `CLONE_MAIN`, else the top of the work tree `cwd` stands in, cut at `/.clones/` (`derive_main`) - found by
    /// walking up for `.git`, the answer `git rev-parse --show-toplevel` gives, with no process started.
    pub fn main(&self) -> &Path {
        self.main.get_or_init(|| {
            if let Some(m) = &self.main_seam {
                return PathBuf::from(m);
            }
            let top = Path::new(&self.cwd)
                .ancestors()
                .find(|d| d.join(".git").exists())
                .map(Path::to_path_buf);
            match top {
                Some(t) => t
                    .to_string_lossy()
                    .split("/.clones/")
                    .next()
                    .map_or(t.clone(), PathBuf::from),
                // no work tree: the tree the guard runs from, as `derive_main` fell back to the script's own
                None => std::env::var("L7R_GUARD_TREE")
                    .map_or_else(|_| PathBuf::from("/diagram"), PathBuf::from),
            }
        })
    }

    /// The session's clone, or None where it does not resolve (`resolve`).
    pub fn clone_dir(&self) -> Option<&Path> {
        self.clone.get_or_init(|| self.resolve()).as_deref()
    }

    /// The clone's directory name, the guard log's `session_name` - or "" where it does not resolve.
    pub fn name(&self) -> String {
        self.clone_dir()
            .and_then(Path::file_name)
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default()
    }

    /// The transcript's text, read once; None where it cannot be read.
    pub fn transcript_text(&self) -> Option<&str> {
        self.text
            .get_or_init(|| self.read(Path::new(&self.transcript)))
            .as_deref()
    }

    /// Every message the GM wrote in this session (`transcript::gm_messages`), read once.
    pub fn gm_messages(&self) -> &[String] {
        self.messages.get_or_init(|| {
            self.transcript_text()
                .map(super::transcript::gm_messages)
                .unwrap_or_default()
        })
    }

    fn read(&self, p: &Path) -> Option<String> {
        self.reads.set(self.reads.get() + 1);
        std::fs::read_to_string(p).ok()
    }

    fn resolve(&self) -> Option<PathBuf> {
        if self.id.is_empty() {
            return None;
        }
        let map = self.main().join(".clones/.session-clones").join(&self.id);
        if let Some(c) = self.read(&map) {
            return Some(PathBuf::from(c.trim()));
        }
        self.canonical()
    }

    /// The clone the session's NAME gives (`canonical_clone`): the transcript's last `/rename`, else the sessions json - the claim
    /// map left out, as the pretool guard compares the two (T013).
    pub fn canonical(&self) -> Option<PathBuf> {
        if self.id.is_empty() {
            return None;
        }
        let (name, source) = self.titled().or_else(|| self.listed())?;
        let name = if source == "derived" || name.trim().is_empty() {
            self.main()
                .file_name()
                .map(|n| n.to_string_lossy().into_owned())
                .unwrap_or_default()
        } else {
            name
        };
        let kept: String = name
            .to_lowercase()
            .chars()
            .filter(|c| {
                c.is_ascii_lowercase() || c.is_ascii_digit() || c.is_whitespace() || *c == '-'
            })
            .collect();
        let kebab = kept.split_whitespace().collect::<Vec<_>>().join("-");
        (!kebab.is_empty()).then(|| self.main().join(".clones").join(kebab))
    }

    /// The transcript's last `custom-title` record (the session's `/rename`).
    fn titled(&self) -> Option<(String, String)> {
        self.transcript_text()?
            .lines()
            .rev()
            .filter(|l| l.contains("custom-title"))
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
            .filter(|r| r.get("type").and_then(Value::as_str) == Some("custom-title"))
            .filter_map(|r| {
                r.get("customTitle")
                    .and_then(Value::as_str)
                    .map(str::to_owned)
            })
            .find(|t| !t.trim().is_empty())
            .map(|t| (t, "transcript".to_owned()))
    }

    /// The sessions json naming this session.
    fn listed(&self) -> Option<(String, String)> {
        let entries = std::fs::read_dir(&self.sessions_dir).ok()?;
        entries
            .filter_map(Result::ok)
            .map(|e| e.path())
            .filter(|p| p.extension().is_some_and(|x| x == "json"))
            .find_map(|p| {
                let d: Value = serde_json::from_str(&self.read(&p)?).ok()?;
                let ids = ["id", "sessionId", "session_id"]
                    .map(|k| d.get(k).and_then(Value::as_str).unwrap_or(""));
                ids.contains(&self.id.as_str()).then(|| {
                    let s = |k: &str| d.get(k).and_then(Value::as_str).unwrap_or("").to_owned();
                    (s("name"), s("nameSource"))
                })
            })
    }
}

/// `s`, unless it is empty (an exported but empty seam is no seam).
fn non_empty(s: String) -> Option<String> {
    (!s.is_empty()).then_some(s)
}

#[cfg(test)]
mod tests;
