//! The session's facts, each read once a process and handed to every guard (plan D6): the mirror (`derive_main`), and the session's
//! clone (`clone-sync-hooks.sh resolve`: the claim map, else the transcript's last `/rename`, else the sessions json). Each read is
//! counted, so a test pins it to once.
//!
//! THE ONE RESOLVER (feature 449 T143, `ask:449-phase4-slices` Q12): `scripts/hooks/lib/clone-resolve.sh` and its inline Python are deleted, and
//! the shell's guard log names its session through this module (`l7r-gate log guard`); each step reads its sources as the Python read
//! them - `str.isspace` for the kebab case, `str()` of a name that is not a string, a dot file not globbed, and a record that is no dict
//! ending the lookup with no name, as the Python's `AttributeError` did.

use std::cell::{Cell, OnceCell};
use std::io::BufRead as _;
use std::path::{Path, PathBuf};

use serde_json::Value;

use crate::shared::py_text;
use crate::shared::pyjson::{py_str, truthy};

/// One event's session facts, read lazily and once.
pub struct Session {
    pub id: String,
    pub cwd: String,
    pub transcript: String,
    /// The `CLONE_MAIN` and `CLONE_SESSIONS_DIR` test seams, read from the environment by `from_input`.
    pub main_seam: Option<String>,
    pub sessions_dir: PathBuf,
    main: OnceCell<PathBuf>,
    map: OnceCell<MapEntry>,
    clone: OnceCell<Option<PathBuf>>,
    named: OnceCell<String>,
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
        // `${CLONE_SESSIONS_DIR:-${HOME:-/home/agent}/.claude/sessions}`: an empty seam is no seam (feature 449 T143)
        let home = home_or_default(env("HOME"));
        let sessions_dir = match env("CLONE_SESSIONS_DIR").and_then(non_empty) {
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
            map: OnceCell::new(),
            clone: OnceCell::new(),
            named: OnceCell::new(),
            text: OnceCell::new(),
            messages: OnceCell::new(),
            reads: Cell::new(0),
        }
    }

    /// The mirror: `CLONE_MAIN`, else the top of the work tree `cwd` stands in, cut at `/.clones/` (`derive_main`) - found by
    /// walking up for `.git`, the answer `git rev-parse --show-toplevel` gives, with no process started. The walk starts from the
    /// directory's real path, as git's answer is one, and a `cwd` that is no directory has no top, as `git -C` fails on it (feature 449
    /// T143: an empty `cwd` walked up from the process's own directory).
    pub fn main(&self) -> &Path {
        self.main.get_or_init(|| {
            if let Some(m) = &self.main_seam {
                return PathBuf::from(m);
            }
            let real = std::fs::canonicalize(&self.cwd).ok().filter(|p| p.is_dir());
            let top = real.as_deref().and_then(|r| {
                r.ancestors()
                    .find(|d| d.join(".git").exists())
                    .map(Path::to_path_buf)
            });
            match top {
                Some(t) => t
                    .to_string_lossy()
                    .split("/.clones/")
                    .next()
                    .map_or(t.clone(), PathBuf::from),
                // no work tree: the tree the guard runs from, as `derive_main` fell back to the script's own (`shared::env`: a test
                // reads its own environment, never a session's exported tree, feature 451 T32)
                None => crate::shared::env::opt("L7R_GUARD_TREE")
                    .map_or_else(|| PathBuf::from("/diagram"), PathBuf::from),
            }
        })
    }

    /// The session's clone, or None where it does not resolve (`resolve`).
    pub fn clone_dir(&self) -> Option<&Path> {
        self.clone.get_or_init(|| self.resolve()).as_deref()
    }

    /// The clone's directory name, the guard log's `session_name` - or "" where it does not resolve. Named as `guard_log` named it from
    /// the text `clone-resolve.sh resolve` printed (feature 449 T143): the claim map's text as it stands, its last line and that line's
    /// part after its last `/` (`tail -1`, `${name##*/}`), a byte that is not UTF-8 one character as Python's `surrogateescape` read it,
    /// and nothing for a map that cannot be read (the script's `cat` failing under `set -e`); else the clone the name gives.
    pub fn name(&self) -> String {
        self.named
            .get_or_init(|| match self.map_entry() {
                MapEntry::Text(raw) => {
                    let mut text: &[u8] = raw;
                    text = text.strip_suffix(b"\n").unwrap_or(text);
                    let line = text.rsplit(|b| *b == b'\n').next().unwrap_or_default();
                    let base = line.rsplit(|b| *b == b'/').next().unwrap_or_default();
                    let kept: Vec<u8> = base.iter().copied().filter(|b| *b != 0).collect();
                    crate::shared::log::surrogate_escaped(&kept)
                }
                MapEntry::Unreadable => String::new(),
                MapEntry::Absent => self
                    .canonical()
                    .and_then(|c| c.file_name().map(|n| n.to_string_lossy().into_owned()))
                    .unwrap_or_default(),
            })
            .clone()
    }

    /// The claim map's entry for this session, read once.
    fn map_entry(&self) -> &MapEntry {
        self.map.get_or_init(|| {
            if self.id.is_empty() {
                return MapEntry::Absent;
            }
            let map = self.main().join(".clones/.session-clones").join(&self.id);
            if !map.is_file() {
                return MapEntry::Absent;
            }
            self.reads.set(self.reads.get() + 1);
            std::fs::read(&map).map_or(MapEntry::Unreadable, MapEntry::Text)
        })
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
        if let MapEntry::Text(raw) = self.map_entry() {
            if let Ok(c) = std::str::from_utf8(raw) {
                return Some(PathBuf::from(c.trim()));
            }
        }
        self.canonical()
    }

    /// The clone the session's NAME gives (`canonical_clone`): the transcript's last `/rename`, else the sessions json - the claim
    /// map left out, as the pretool guard compares the two (T013).
    pub fn canonical(&self) -> Option<PathBuf> {
        if self.id.is_empty() {
            return None;
        }
        let (name, source) = match self.titled() {
            Found::Name(n) => n,
            Found::Ended => return None,
            Found::Nothing => match self.listed() {
                Found::Name(n) => n,
                Found::Ended | Found::Nothing => return None,
            },
        };
        let name = if source == "derived" || py_text::strip(&name).is_empty() {
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
                c.is_ascii_lowercase() || c.is_ascii_digit() || py_text::is_space(*c) || *c == '-'
            })
            .collect();
        let kebab = py_text::split(&kept).join("-");
        (!kebab.is_empty()).then(|| self.main().join(".clones").join(kebab))
    }

    /// The transcript's last `custom-title` record (the session's `/rename`).
    /// A line at a time and only the matching lines parsed: a session's transcript reached 658 MB on 2026-11-08, and this was read at every turn's end.
    /// Its lines split as Python's text mode splits them (`\r` too), and a title that is not a string named by its `str()`.
    fn titled(&self) -> Found {
        self.reads.set(self.reads.get() + 1);
        let path = Path::new(&self.transcript);
        if self.transcript.is_empty() || !path.is_file() {
            return Found::Nothing;
        }
        // a file that stands and cannot be opened raised in the Python, which printed nothing
        let Ok(file) = std::fs::File::open(path) else {
            return Found::Ended;
        };
        let mut last = None;
        for raw in std::io::BufReader::new(file)
            .split(b'\n')
            .map_while(Result::ok)
        {
            for part in raw.split(|b| *b == b'\r') {
                let line = String::from_utf8_lossy(part);
                if !line.contains("custom-title") {
                    continue;
                }
                let Ok(r) = serde_json::from_str::<Value>(&line) else {
                    continue;
                };
                if !r.is_object() {
                    return Found::Ended;
                }
                let title = r.get("customTitle").map(named).unwrap_or_default();
                if r.get("type").and_then(Value::as_str) == Some("custom-title")
                    && !py_text::strip(&title).is_empty()
                {
                    last = Some(title);
                }
            }
        }
        last.map_or(Found::Nothing, |t| {
            Found::Name((t, "transcript".to_owned()))
        })
    }

    /// The sessions json naming this session: `glob("*.json")`'s files in the directory's order, a dot file not among them.
    fn listed(&self) -> Found {
        let Ok(entries) = std::fs::read_dir(&self.sessions_dir) else {
            return Found::Nothing;
        };
        for p in entries.filter_map(Result::ok).map(|e| e.path()) {
            let file = p
                .file_name()
                .map(|n| n.to_string_lossy().into_owned())
                .unwrap_or_default();
            if file.starts_with('.') || p.extension().is_none_or(|x| x != "json") {
                continue;
            }
            let Some(d) = self
                .read(&p)
                .and_then(|t| serde_json::from_str::<Value>(&t).ok())
            else {
                continue;
            };
            if !d.is_object() {
                return Found::Ended;
            }
            let ids = ["id", "sessionId", "session_id"]
                .map(|k| d.get(k).and_then(Value::as_str).unwrap_or(""));
            if ids.contains(&self.id.as_str()) {
                let source = d.get("nameSource").and_then(Value::as_str).unwrap_or("");
                return Found::Name((
                    d.get("name").map(named).unwrap_or_default(),
                    source.to_owned(),
                ));
            }
        }
        Found::Nothing
    }
}

/// The claim map's entry for a session: no file there, a file that cannot be read, or its bytes.
enum MapEntry {
    Absent,
    Unreadable,
    Text(Vec<u8>),
}

/// What a lookup of the session's name found: a name and its source, nothing (the next source is asked), or a record that is no dict,
/// which ended the Python's lookup with no name at all.
enum Found {
    Name((String, String)),
    Nothing,
    Ended,
}

/// A name as the Python's `str(name or "")` wrote it: "" for a false value, a string as it is, `str()` of anything else.
fn named(v: &Value) -> String {
    if truthy(v) {
        py_str(v)
    } else {
        String::new()
    }
}

/// `HOME`, else `/home/agent`, as the shell's `${HOME:-/home/agent}` - outside the generic `with_env`, so its one fallback is one line
/// to cover, not one an instantiation never reaches.
fn home_or_default(home: Option<String>) -> String {
    home.and_then(non_empty)
        .unwrap_or_else(|| "/home/agent".to_owned())
}

/// `s`, unless it is empty (an exported but empty seam is no seam).
fn non_empty(s: String) -> Option<String> {
    (!s.is_empty()).then_some(s)
}

#[cfg(test)]
mod tests;
