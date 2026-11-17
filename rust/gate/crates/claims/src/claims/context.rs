//! What a Rust unit's code turns on, carried into its claims bundle as context: `scripts/record/claims_context.py`'s rules (feature 385
//! T25, plan D47) on a Rust item (feature 449 T165). Before T165 a `.rs` unit's bundle carried only the constants of its own file it
//! named (feature 444 T16), where a `.py` unit's carries the functions of its module it calls, the constants it reads wherever they are
//! defined, what a distance claim turns on two calls down, and what a CANNOT-TELL's note names - so a Rust unit judged CANNOT-TELL for
//! want of a callee had no bundle that would show it.
//!
//! THE RULES, the Python's: a FIRST bundle (`callees`) carries the unit's own file's functions it calls, at most [`CALLEES_MAX`], then
//! every constant it reads; a claim whose label names a distance (`direct`) carries every function it calls and theirs, two calls down,
//! with every constant any of them reads, uncapped; a re-bundle of a CANNOT-TELL (`chase`) carries each name its note puts in
//! backticks and, breadth first, what each calls or reads, within [`CHASE_CHARS`].
//!
//! THE NAMES, read from the item's tokens: a call by a bare name (`drawn(`), by a path (`crate::course::drawn(`, `Brook::new(`,
//! `Self::lay(`), and a constant read (an all-capitals name). A name resolves in the unit's own file first; else a path, or a bare name a
//! `use` of the file brings in (a glob `use super::*;` too), resolves to the one item of its crate (`rust/<crate>/`, test files left
//! out) that defines it - the path's or the `use`'s module choosing among several, a type naming its method (`Brook.new`). A bare
//! name the file neither defines nor imports (a closure's, a local's), a name no item of the crate defines (the standard library's,
//! another crate's) and a method called on a value (`x.lay(`, whose type the tokens cannot tell) are not followed: the Python's
//! bare-name rule leaves `obj.f()` out too.

use std::collections::{HashMap, HashSet};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::units::{items, rel, rglob, walked, Unit};
use crate::record::units::re;

/// The most of a unit's own file's functions a first bundle carries (`claims.CALLEES_MAX`).
pub const CALLEES_MAX: usize = 6;
/// The most characters a CANNOT-TELL's chase adds to a bundle (`claims_context.CHASE_CHARS`, D47b).
pub const CHASE_CHARS: usize = 30_000;
/// The calls a distance claim's context follows down (`claims_context.direct`'s `depth`).
const DEPTH: usize = 2;

/// One file of a crate: its path, the bodies of its `use` statements, and its items' (qualname, kind, source).
struct File {
    path: String,
    uses: Vec<String>,
    items: Vec<(String, String, String)>,
}

/// One crate's files, in walk order.
type Table = Vec<File>;

/// The items of each crate a bundle has read, built once a bundle.
#[derive(Default)]
pub struct Tables(HashMap<String, Table>);

/// What a bundle's units carry as context so far, and the crates' items it has read.
pub struct Gather {
    pub refs: Vec<String>,
    pub tables: Tables,
}

static USE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^\s*(?:pub(?:\([^)]*\))?\s+)?use\s+([^;]*);"));

/// `rust/<crate>` of a repository path under `rust/`.
fn crate_of(path: &str) -> String {
    path.split('/').take(2).collect::<Vec<_>>().join("/")
}

/// Python's `str.isupper()`: a cased character, and every cased one upper case.
fn caps(name: &str) -> bool {
    name.chars().any(char::is_uppercase) && !name.chars().any(char::is_lowercase)
}

fn ident(tok: &str) -> bool {
    tok.starts_with(|c: char| c.is_alphabetic() || c == '_')
}

/// A test file (`tests.rs`, or under `tests/`): what its items define is no engine code's context.
fn test_file(path: &str) -> bool {
    path.ends_with("/tests.rs") || path.contains("/tests/")
}

/// The module a `use` of `file` names `name` from - by name, or by a glob (`use super::*;`) - empty where it names none; None where no
/// `use` names it.
fn imported(file: &File, name: &str) -> Option<String> {
    let word = re(&format!(r"\b{name}\b"));
    file.uses.iter().find_map(|u| {
        if !(u.trim_end().ends_with('*') || word.is_match(u).unwrap_or(false)) {
            return None;
        }
        // the segment before the `::` that leads to the name (or to the glob): `crate::course::drawn` -> `course`
        let before = u.split(name).next().unwrap_or(u);
        Some(
            before
                .rsplit_once("::")
                .map_or_else(String::new, |(left, _)| {
                    let last = left.rsplit("::").next().unwrap_or(left);
                    last.trim_matches(|c: char| !c.is_alphanumeric() && c != '_')
                        .to_owned()
                }),
        )
    })
}

impl Tables {
    /// The files of `path`'s crate, its test files left out (a file that does not read, empty).
    fn of(&mut self, root: &Path, path: &str) -> &Table {
        let krate = crate_of(path);
        self.0.entry(krate.clone()).or_insert_with(|| {
            let base = root.join("rust");
            rglob(&root.join(&krate), ".rs")
                .into_iter()
                .filter(|p| walked(&rel(p, &base)) && !test_file(&rel(p, root)))
                .map(|p| {
                    let text = std::fs::read_to_string(&p).unwrap_or_default();
                    File {
                        path: rel(&p, root),
                        uses: USE
                            .captures_iter(&text)
                            .flatten()
                            .map(|c| c[1].to_owned())
                            .collect(),
                        items: items(&text, 0, "", false)
                            .into_iter()
                            .map(|(q, kind, _, _, _, body)| (q, kind, body))
                            .collect(),
                    }
                })
                .collect()
        })
    }

    /// `path::qualname` of what `name` names from `path` (a function when `called`, else a constant), or None. The unit's own file
    /// first; else, for a path (`course::drawn`, `Brook::new`) or a name a `use` of the file brings in, the one item of its crate that
    /// defines it - a module (the path's, or the `use`'s) choosing among several, a type naming its method. A bare name the file
    /// neither defines nor imports - a closure's, a local's - is no item's.
    fn resolve(
        &mut self,
        root: &Path,
        path: &str,
        name: &str,
        called: bool,
        qual: Option<&str>,
    ) -> Option<String> {
        let typed = qual.filter(|q| q.starts_with(char::is_uppercase));
        let want = typed.map_or_else(|| name.to_owned(), |t| format!("{t}.{name}"));
        let fits = |(q, kind, _): &(String, String, String)| {
            *q == want
                && (if called {
                    kind != "constant" && kind != "class"
                } else {
                    kind == "constant"
                })
        };
        let table = self.of(root, path);
        let own = table.iter().find(|f| f.path == path);
        if own.is_some_and(|f| f.items.iter().any(fits)) {
            return Some(format!("{path}::{want}"));
        }
        let module = match qual {
            Some(q) => (typed.is_none()).then(|| q.to_owned()),
            None => Some(own.and_then(|f| imported(f, name))?),
        };
        let mut hits: Vec<&String> = table
            .iter()
            .filter(|f| f.items.iter().any(fits))
            .map(|f| &f.path)
            .collect();
        if let Some(module) = module
            .filter(|m| hits.len() > 1 && !["", "crate", "super", "self"].contains(&m.as_str()))
        {
            hits.retain(|p| {
                p.split('/')
                    .any(|part| part == module || part == format!("{module}.rs"))
            });
        }
        (hits.len() == 1).then(|| format!("{}::{want}", hits[0]))
    }

    /// `path::qualname` of each function or constant `source` (an item of `path`, named `own`) uses that its crate defines: its own
    /// file's first, then the rest (`claims_context._refs`).
    pub(super) fn refs(&mut self, root: &Path, path: &str, source: &str, own: &str) -> Vec<String> {
        let own_type = own.rsplit_once('.').map(|p| p.0.to_owned());
        let (mut local, mut far) = (Vec::new(), Vec::new());
        for (name, called, qual) in named(source) {
            if name == own.rsplit('.').next().unwrap_or(own) && qual.is_none() {
                continue;
            }
            let qual = if qual.as_deref() == Some("Self") {
                own_type.clone()
            } else {
                qual
            };
            if let Some(r) = self.resolve(root, path, &name, called, qual.as_deref()) {
                let list = if r.starts_with(&format!("{path}::")) {
                    &mut local
                } else {
                    &mut far
                };
                if !list.contains(&r) {
                    list.push(r);
                }
            }
        }
        local.extend(far);
        local
    }

    /// Each crate definition of `name` (a function or a constant) - every walked crate's, at most three (`claims_context.defined_in`).
    fn defined_in(&mut self, root: &Path, name: &str) -> Vec<String> {
        let crates: Vec<String> = std::fs::read_dir(root.join("rust"))
            .map(|d| {
                d.flatten()
                    .filter(|e| e.file_type().is_ok_and(|t| t.is_dir()))
                    .map(|e| e.file_name().to_string_lossy().into_owned())
                    .filter(|n| walked(n))
                    .collect()
            })
            .unwrap_or_default();
        let mut crates = crates;
        crates.sort();
        let mut out = Vec::new();
        for c in crates {
            for f in self.of(root, &format!("rust/{c}/")) {
                if f.items
                    .iter()
                    .any(|(q, kind, _)| q == name && kind != "class")
                {
                    out.push(format!("{}::{name}", f.path));
                }
            }
        }
        out.truncate(3);
        out
    }

    pub(super) fn source(&mut self, root: &Path, reference: &str) -> Option<String> {
        let (path, qual) = reference.split_once("::")?;
        self.of(root, path)
            .iter()
            .filter(|f| f.path == path)
            .flat_map(|f| &f.items)
            .find(|(q, _, _)| q == qual)
            .map(|(_, _, body)| body.clone())
    }
}

/// (name, called, its path's last qualifier) for each call and each all-capitals name read in `source`, in order of first use.
fn named(source: &str) -> Vec<(String, bool, Option<String>)> {
    let raw = crate::codeid::rust_tokens(source.as_bytes());
    let t: Vec<&str> = std::str::from_utf8(&raw)
        .unwrap_or_default()
        .split('\0')
        .collect();
    let at = |k: usize| t.get(k).copied().unwrap_or_default();
    let mut seen = HashSet::new();
    let mut out = Vec::new();
    for (i, tok) in t.iter().enumerate() {
        let before = i.checked_sub(1).map_or("", at);
        // a `.` before a name is a field or a method, but `..` is a range or a struct's rest: `0..BINS` reads `BINS`
        let field = before == "." && (i < 2 || at(i - 2) != ".");
        if !ident(tok) || before == "fn" || field {
            continue;
        }
        let called = at(i + 1) == "(";
        if !called && (!caps(tok) || at(i + 1) == "!") {
            continue;
        }
        let qual = (i >= 3 && before == ":" && at(i - 2) == ":" && ident(at(i - 3)))
            .then(|| at(i - 3).to_owned());
        if seen.insert(((*tok).to_owned(), called, qual.clone())) {
            out.push(((*tok).to_owned(), called, qual));
        }
    }
    out
}

/// The context a Rust unit's bundle carries (`bundle.py_context`'s rules): the first bundle's; when a claim's label names a distance,
/// what it turns on two calls down; and what the CANNOT-TELL notes `asked` for.
pub fn rust_context(
    tables: &mut Tables,
    root: &Path,
    unit: &Unit,
    src: &str,
    distance: bool,
    asked: &[String],
) -> Vec<String> {
    let refs = tables.refs(root, &unit.path, src, &unit.qualname);
    let own_file = format!("{}::", unit.path);
    let mut out: Vec<String> = refs
        .iter()
        .filter(|r| r.starts_with(&own_file) && !constant(r))
        .take(CALLEES_MAX)
        .cloned()
        .collect();
    out.extend(refs.iter().filter(|r| constant(r)).cloned());
    if distance {
        out.extend(direct(tables, root, unit, src));
    }
    out.extend(chase(tables, root, unit, asked));
    let mut seen = HashSet::new();
    out.retain(|r| seen.insert(r.clone()));
    out
}

/// Whether `path::qualname` names a constant (its last name all capitals).
pub(super) fn constant(reference: &str) -> bool {
    let qual = reference.rsplit("::").next().unwrap_or_default();
    caps(qual.rsplit('.').next().unwrap_or(qual))
}

/// Every function the unit calls and theirs, [`DEPTH`] calls down, with every constant any of them reads - uncapped (D47a).
fn direct(tables: &mut Tables, root: &Path, unit: &Unit, src: &str) -> Vec<String> {
    let own = unit
        .qualname
        .rsplit('.')
        .next()
        .unwrap_or(&unit.qualname)
        .to_owned();
    let mut out: Vec<String> = Vec::new();
    let mut level = vec![(unit.path.clone(), unit.qualname.clone(), src.to_owned())];
    for _ in 0..DEPTH {
        let mut next = Vec::new();
        for (path, name, source) in &level {
            for r in tables.refs(root, path, source, name) {
                if out.contains(&r) || r.ends_with(&format!("::{own}")) {
                    continue;
                }
                out.push(r.clone());
                if !constant(&r) {
                    // every reference resolved from a crate's items has its source there
                    let s = tables.source(root, &r).unwrap_or_default();
                    let (p, q) = r.split_once("::").unwrap_or_default();
                    next.push((p.to_owned(), q.to_owned(), s));
                }
            }
        }
        level = next;
    }
    for (path, name, source) in &level {
        for r in tables.refs(root, path, source, name) {
            if constant(&r) && !out.contains(&r) {
                out.push(r);
            }
        }
    }
    out
}

/// Each name a CANNOT-TELL asked for that the unit's file or crate defines (else every walked crate's definition of it, at most
/// three) and, breadth first, what each calls or reads, within [`CHASE_CHARS`] (D47b).
fn chase(tables: &mut Tables, root: &Path, unit: &Unit, names: &[String]) -> Vec<String> {
    let mut queue: Vec<String> = Vec::new();
    for name in names {
        let called = !caps(name);
        match tables.resolve(root, &unit.path, name, called, None) {
            Some(r) => queue.push(r),
            None => queue.extend(tables.defined_in(root, name)),
        }
    }
    let (mut out, mut used) = (Vec::new(), 0);
    while !queue.is_empty() {
        let r = queue.remove(0);
        if out.contains(&r) {
            continue;
        }
        let src = tables.source(root, &r).unwrap_or_default();
        if used + src.chars().count() > CHASE_CHARS {
            break;
        }
        used += src.chars().count();
        out.push(r.clone());
        let (p, q) = r.split_once("::").unwrap_or_default();
        if !constant(&r) {
            queue.extend(
                tables
                    .refs(root, p, &src, q)
                    .into_iter()
                    .filter(|x| !out.contains(x)),
            );
        }
    }
    out
}

#[cfg(test)]
mod tests;
