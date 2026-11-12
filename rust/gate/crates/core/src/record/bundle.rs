//! The check bundles (feature 449 T88, `ask:449-T88-bundles`, from `check_bundle.py`, `bundle_owed.py`, `modal_bundle.py` and `earlier_rounds.py`): the files one check agent reads, copied out of the repository with a MANIFEST naming each copy's origin (feature 250), refused for a check nothing owes (feature 311). `l7r-gate record check-bundle ...` and `record modal-bundle ...`; what they reach of Python still unported goes through one runner, `scripts/bundle_door.py` ([`door`]).

use std::fmt::Write as _;
use std::path::{Component, Path, PathBuf};

use crate::record::repo::{fail, Fail};
use crate::Reply;

pub mod door;

/// Where a bundle goes by default: no `CLAUDE.md` sits above it.
#[cfg(not(any(test, feature = "testkit")))]
const DEFAULT_ROOT: &str = "/tmp/l7r-check";

/// [`DEFAULT_ROOT`].
#[cfg(not(any(test, feature = "testkit")))]
#[must_use]
pub fn default_root() -> PathBuf {
    PathBuf::from(DEFAULT_ROOT)
}

/// The tests' default directory, so a test of a default OUT never writes a session's real bundles: the process's shared directory
/// (`beside_binary`), in the run's own temp directory, which `make rust-test` removes whole when the run ends (feature 449 T101).
#[cfg(any(test, feature = "testkit"))]
#[must_use]
pub fn default_root() -> PathBuf {
    static ROOT: std::sync::OnceLock<PathBuf> = std::sync::OnceLock::new();
    ROOT.get_or_init(|| l7r_guard::shared::tempdir::beside_binary("l7r-check-tests"))
        .clone()
}
pub const MANIFEST: &str = "MANIFEST.md";

/// What a run printed, and the runner it opened, carried to its reply.
pub struct Run {
    pub out: String,
    pub err: String,
    pub door: door::Runner,
}

impl Run {
    #[must_use]
    pub fn new(root: &Path) -> Self {
        Self {
            out: String::new(),
            err: String::new(),
            door: door::Runner::new(&crate::record::repo::tree_of(root)),
        }
    }

    /// `print(text)`.
    pub fn say(&mut self, text: &str) {
        self.out.push_str(text);
        self.out.push('\n');
    }

    /// `print(text, file=sys.stderr)`.
    pub fn warn(&mut self, text: &str) {
        self.err.push_str(text);
        self.err.push('\n');
    }

    /// The reply with exit `code`, or a failure the Python raised: what was printed, the failure after it, exit 1.
    #[must_use]
    pub fn reply(self, done: Result<i32, Fail>) -> Reply {
        match done {
            Ok(code) => Reply {
                stdout: self.out,
                stderr: self.err,
                code,
            },
            Err(why) => Reply {
                stdout: self.out,
                stderr: self.err + &why + if why.ends_with('\n') { "" } else { "\n" },
                code: 1,
            },
        }
    }
}

/// A path as `pathlib.Path` spells it: no `.` component, no doubled or trailing separator.
#[must_use]
pub fn py_path(text: &str) -> PathBuf {
    let mut out = PathBuf::new();
    for c in Path::new(text).components() {
        if c != Component::CurDir {
            out.push(c.as_os_str());
        }
    }
    if out.as_os_str().is_empty() {
        out.push(".");
    }
    out
}

/// `pathlib.Path(text).resolve()`: the real path, or the absolute one where it does not exist.
#[must_use]
pub fn resolve(text: &str) -> PathBuf {
    std::fs::canonicalize(text).unwrap_or_else(|_| {
        let p = py_path(text);
        if p.is_absolute() {
            p
        } else {
            std::env::current_dir().unwrap_or_default().join(p)
        }
    })
}

/// `f"{n:,}"`.
#[must_use]
pub fn thousands(n: usize) -> String {
    let digits = n.to_string();
    let mut out = String::new();
    for (i, c) in digits.chars().enumerate() {
        if i > 0 && (digits.len() - i) % 3 == 0 {
            out.push(',');
        }
        out.push(c);
    }
    out
}

/// `str(path)`.
#[must_use]
pub fn shown(path: &Path) -> String {
    path.to_string_lossy().into_owned()
}

/// `str(path.relative_to(root))`, or the path itself outside the root.
#[must_use]
pub fn relative(path: &Path, root: &Path) -> String {
    path.strip_prefix(root)
        .map_or_else(|_| shown(path), |p| shown(&py_path(&shown(p))))
}

/// `sorted(paths)` as Python orders `Path`s: part by part, not as strings.
pub fn sort_paths(paths: &mut [PathBuf]) {
    paths.sort_by(|a, b| a.components().cmp(b.components()));
}

/// `text.casefold()` for what the record's names hold: lowercase, and the German sharp s as `ss`.
#[must_use]
pub fn casefold(text: &str) -> String {
    text.to_lowercase().replace('\u{df}', "ss")
}

/// `re.sub(r"[^a-z0-9]+", "-", text).strip("-")`.
#[must_use]
pub fn dashed(text: &str) -> String {
    dash_runs(text, |c| c.is_ascii_lowercase() || c.is_ascii_digit())
}

/// Each run of characters `keep` refuses as one `-`, none at either end.
pub fn dash_runs(text: &str, keep: fn(&char) -> bool) -> String {
    let mut out = String::new();
    let mut gap = false;
    for c in text.chars() {
        if keep(&c) {
            if gap && !out.is_empty() {
                out.push('-');
            }
            gap = false;
            out.push(c);
        } else {
            gap = true;
        }
    }
    out
}

/// `re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")`.
#[must_use]
pub fn slug(text: &str) -> String {
    dashed(&casefold(text))
}

/// Python's `\s`: Unicode whitespace and the four separators `\x1c`-`\x1f` the `regex` crate's `\s` leaves out.
const PY_SPACE: &str =
    r"\t-\r\x1c-\x1f \x85\xa0\x{1680}\x{2000}-\x{200a}\x{2028}\x{2029}\x{202f}\x{205f}\x{3000}";

/// A pattern as Python's `re` reads it: `\s` and `\S` its whitespace, `\Z` the end of the text.
#[must_use]
pub fn pyre(pattern: &str) -> fancy_regex::Regex {
    let mut out = String::with_capacity(pattern.len() + 32);
    let (mut chars, mut class) = (pattern.chars().peekable(), false);
    while let Some(c) = chars.next() {
        match (c, class) {
            ('\\', _) => match chars.next().unwrap_or('\\') {
                's' if class => out.push_str(PY_SPACE),
                's' => {
                    let _ = write!(out, "[{PY_SPACE}]");
                }
                'S' if !class => {
                    let _ = write!(out, "[^{PY_SPACE}]");
                }
                'Z' => out.push_str(r"\z"),
                n => {
                    out.push('\\');
                    out.push(n);
                }
            },
            ('[', false) => {
                class = true;
                out.push('[');
                if chars.peek() == Some(&'^') {
                    out.push('^');
                    chars.next();
                }
                if chars.peek() == Some(&']') {
                    out.push_str("\\]");
                    chars.next();
                }
            }
            (']', true) => {
                class = false;
                out.push(']');
            }
            (c, _) => out.push(c),
        }
    }
    crate::record::units::re(&out)
}

/// Every non-overlapping match of `pattern`'s group `g` (0: the whole match), as `re.findall` gives them.
#[must_use]
pub fn findall(pattern: &fancy_regex::Regex, text: &str, g: usize) -> Vec<String> {
    pattern
        .captures_iter(text)
        .flatten()
        .map(|c| c.get(g).map_or_else(String::new, |m| m.as_str().to_owned()))
        .collect()
}

/// `re.split(pattern, text)` of a pattern with no group.
#[must_use]
pub fn split_on<'a>(pattern: &fancy_regex::Regex, text: &'a str) -> Vec<&'a str> {
    let (mut out, mut at) = (Vec::new(), 0);
    for m in pattern.find_iter(text).flatten() {
        out.push(&text[at..m.start()]);
        at = m.end();
    }
    out.push(&text[at..]);
    out
}

/// Whether `pattern` matches somewhere in `text`.
#[must_use]
pub fn hit(pattern: &fancy_regex::Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

/// `datetime.date.today().isoformat()`: the local date, as `date(1)` reads the zone.
#[must_use]
pub fn today() -> String {
    let done = std::process::Command::new("date").arg("+%F").output();
    done.map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
        .unwrap_or_default()
}

/// `text.rstrip()`: Python's whitespace off the end.
pub fn rstrip(text: &str) -> &str {
    text.trim_end_matches(l7r_guard::shared::py_text::is_space)
}

/// The first `n` characters of `text` (`text[:n]`).
#[must_use]
pub fn head(text: &str, n: usize) -> &str {
    text.char_indices().nth(n).map_or(text, |(i, _)| &text[..i])
}

/// A JSON value as Python's `str()` and `repr()` print what `json.loads` made of it: the guard's `pyjson` since feature 449 T119, where the
/// event-log reader the guard and the gate share names an edit's path by it (`ask:449-T83-scope`, one implementation).
pub use l7r_guard::shared::pyjson::py_str;

/// A string as Python's `repr` prints it: the guard's `py_text::repr` since feature 449 T83, where the review ledger's lint names a
/// cell by its repr and the guard crate cannot reach the gate's (`ask:449-T83-scope`, one implementation).
pub use l7r_guard::shared::py_text::repr as py_repr;

/// `dest.parent.mkdir(parents=True, exist_ok=True); dest.write_text(text)`.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn write(dest: &Path, text: &str) -> Result<(), Fail> {
    if let Some(parent) = dest.parent() {
        std::fs::create_dir_all(parent).map_err(fail)?;
    }
    std::fs::write(dest, text).map_err(|e| format!("{}: {e}", dest.display()))
}

/// `shutil.copyfile(src, out / name)` after making its directory; the copy's name under `out`.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn copy(src: &Path, out: &Path, name: Option<&str>) -> Result<String, Fail> {
    let name = name.map_or_else(
        || {
            src.file_name()
                .map_or_else(String::new, |n| n.to_string_lossy().into_owned())
        },
        str::to_owned,
    );
    let dest = out.join(&name);
    if let Some(parent) = dest.parent() {
        std::fs::create_dir_all(parent).map_err(fail)?;
    }
    std::fs::copy(src, &dest).map_err(|e| format!("{}: {e}", src.display()))?;
    Ok(relative(&dest, out))
}

/// `shutil.rmtree(path)`.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn remove_tree(path: &Path) -> Result<(), Fail> {
    std::fs::remove_dir_all(path).map_err(|e| format!("{}: {e}", path.display()))
}

/// The usage refusal argparse gives: exit 2, nothing on stdout (its own words are not bound, `ask:449-usage-text`).
#[must_use]
pub fn usage(verb: &str, complaint: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("usage: l7r-gate record {verb}: {complaint}\n"),
        code: 2,
    }
}

#[cfg(any(test, feature = "testkit"))]
pub mod tests;
