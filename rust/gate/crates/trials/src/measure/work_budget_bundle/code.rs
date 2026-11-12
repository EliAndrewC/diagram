//! What the bundles read of today's code (feature 443 T05; feature 444 T15-T19, T26, T40, FR-015; ported by feature 449 T134 from
//! `work_budget_bundle.py`): a stage's modules and every module its counters name or its code calls, for MODE AUDIT; and today's
//! names, which a MODE BUDGET derivation may not use. Python's `ast` reads became `pyast` (see its header for why a parser).

use std::collections::{BTreeSet, HashMap, HashSet};
use std::path::{Component, Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::pyast::{self, Callee, Module, What};
use super::{glob, py_re, read, rglob, R};

pub(super) const HAMLET: &str = "l7r/diagram/hamletgen";
/// The rebuilt phases' crates (feature 444 FR-010).
pub(super) const RUST: &str = "rust";
const FANOUT: &str = "dev/perf-log";

static KNOB: LazyLock<Regex> =
    LazyLock::new(|| py_re(r#"Knob\(\s*"([a-z0-9_]+)"\s*,\s*\[([^\]]*)\]"#));
static QUOTED: LazyLock<Regex> = LazyLock::new(|| py_re(r#""([a-z0-9_]+)""#));
// a backticked dotted name or path splits
static IDENT: LazyLock<Regex> =
    LazyLock::new(|| py_re(r"`([A-Za-z_][\w./]*)`|\b([A-Za-z]\w*_\w*|[A-Z][a-z0-9]+[A-Z]\w*)\b"));
static DOCUMENT: LazyLock<Regex> = LazyLock::new(|| py_re(r"\.(txt|md|json|html)$"));
static CRATE_PATH: LazyLock<Regex> = LazyLock::new(|| py_re(r"\bcrate::([a-z_][a-z0-9_]*)::"));

fn matches(re: &Regex, text: &str) -> bool {
    re.is_match(text).unwrap_or(false)
}

/// Whether a path has a component named `target` (a build tree), as `"target" in p.parts` asks of the whole path.
fn in_build_tree(p: &Path) -> bool {
    p.components()
        .any(|c| c == Component::Normal("target".as_ref()))
}

/// The file defining `stage_<phase>` under the hamlet package, and, when that file is in a subpackage, its siblings; and a
/// Rust phase's source beside it (feature 444 T17, `dev/rust-tooling.md` "the work-budget audit bundle"): the `.rs` file under
/// `rust/` defining `fn stage_<phase>`, with its siblings when it sits in a module directory of its own.
///
/// # Errors
///
/// A source that does not read.
pub fn stage_files(root: &Path, phase: &str) -> R<Vec<PathBuf>> {
    let escaped = fancy_regex::escape(phase);
    let pat = py_re(&format!(r"(?m)^def stage_{escaped}\("));
    let hamlet = root.join(HAMLET);
    let mut found = Vec::new();
    if hamlet.is_dir() {
        for p in rglob(&hamlet, ".py") {
            if matches(&pat, &read(&p)?) {
                found.push(p);
            }
        }
    }
    // A RUST STAGE WITH NO PYTHON BESIDE IT (feature 444 T40): the Python hamlet engine is deleted, and a lookup that returned
    // nothing without its Python function found no stage at all - every audit bundle refused
    let mut files = match found.first() {
        Some(first) if first.parent() != Some(hamlet.as_path()) => {
            glob(first.parent().unwrap_or(root), "", ".py")
        }
        Some(_) => found,
        None => vec![],
    };
    let rs = py_re(&format!(
        r"(?m)^\s*(?:pub(?:\(crate\))?\s+)?fn\s+stage_{escaped}\b"
    ));
    let mut rust = Vec::new();
    if root.join(RUST).is_dir() {
        // every file is read, as the Python read it (one that does not read still fails the run), and the pattern asked only of
        // those holding its name: the same answer, where the pattern over all 682 sources cost 0.24 s (feature 449 T134, measured)
        let literal = format!("stage_{phase}");
        for p in rglob(&root.join(RUST), ".rs") {
            let text = read(&p)?;
            if text.contains(&literal) && matches(&rs, &text) {
                rust.push(p);
            }
        }
    }
    if let Some(first) = rust.first() {
        let home = first.parent().unwrap_or(root);
        if home.file_name().is_some_and(|n| n != "src") {
            // the module's own file above its directory (`src/sink.rs` for `src/sink/`), where it is not a `mod.rs` inside it
            let own = home.parent().unwrap_or(root).join(format!(
                "{}.rs",
                home.file_name().unwrap_or_default().to_string_lossy()
            ));
            if own.is_file() {
                files.push(own);
            }
            files.extend(glob(home, "", ".rs"));
        } else {
            files.push(first.clone());
        }
        let rs_files: Vec<PathBuf> = files
            .iter()
            .filter(|f| f.extension().is_some_and(|e| e == "rs"))
            .cloned()
            .collect();
        for q in crate_modules(root, &rs_files)? {
            if !files.contains(&q) {
                files.push(q);
            }
        }
    }
    Ok(files)
}

/// The crate's modules the stage's Rust reaches by path (`crate::course::drawn` brings `src/course.rs`) - THE AUDIT READS EVERY
/// LOOP THE STAGE RUNS (feature 444 T26's MODE AUDITs: the field's bundle lacked `course.rs`, whose loops its new counter names).
fn crate_modules(root: &Path, rs: &[PathBuf]) -> R<Vec<PathBuf>> {
    let src = root.join(RUST).join("phases").join("src");
    let mut out = Vec::new();
    for p in rs {
        let text = read(p)?;
        let names: BTreeSet<String> = CRATE_PATH
            .captures_iter(&text)
            .filter_map(Result::ok)
            .filter_map(|c| c.get(1).map(|m| m.as_str().to_owned()))
            .collect();
        for name in names {
            for q in [
                src.join(format!("{name}.rs")),
                src.join(&name).join("mod.rs"),
            ] {
                if q.is_file() && !out.contains(&q) && !rs.contains(&q) {
                    out.push(q);
                }
            }
        }
    }
    Ok(out)
}

/// A file's name in the bundle's `code/`: its path from the repository root, `/` as `__`, so two modules of one name (the field's
/// and the sink's `brook.rs`, feature 444 T26) never overwrite each other.
pub(super) fn bundled_name(root: &Path, p: &Path) -> String {
    p.strip_prefix(root).map_or_else(
        |_| {
            p.file_name()
                .unwrap_or_default()
                .to_string_lossy()
                .into_owned()
        },
        |rel| rel.to_string_lossy().replace('/', "__"),
    )
}

/// The counters' keys a stage's rows name (`<kind>@<function>`), each row's `ops` read as Python iterates it.
///
/// # Errors
///
/// An `ops` that is no mapping or list of names: where Python's iteration raised.
pub fn counter_keys(counts: &[Value]) -> R<Vec<String>> {
    let mut out = Vec::new();
    for r in counts {
        match r.get("ops") {
            None | Some(Value::Null | Value::Bool(false)) => {}
            Some(Value::String(s)) if s.is_empty() => {}
            Some(Value::Number(n)) if n.as_f64() == Some(0.0) => {}
            Some(Value::Object(m)) => out.extend(m.keys().filter(|k| k.contains('@')).cloned()),
            Some(Value::Array(items)) => {
                for k in items {
                    let k = k
                        .as_str()
                        .ok_or("TypeError: argument of type is not iterable")?;
                    if k.contains('@') {
                        out.push(k.to_owned());
                    }
                }
            }
            Some(_) => return Err("TypeError: a stage's ops is not iterable".to_owned()),
        }
    }
    Ok(out)
}

/// The modules under `l7r/` defining each function the stage's counters name (`<kind>@<function>`, a method's class dropped)
/// - THE WORK IS AUDITED WHERE IT IS COUNTED (feature 444 T15's MODE AUDIT: the water frame's whole count sat in `plan.py`'s
///   `_roll`, outside the stage's own module, so the audit could not see whether `plan_site` left a loop uncounted).
///
/// # Errors
///
/// A source that does not read, or a counters' row Python could not iterate.
pub fn counted_files(root: &Path, counts: &[Value]) -> R<Vec<PathBuf>> {
    let names: BTreeSet<String> = counter_keys(counts)?
        .iter()
        .map(|k| {
            let function = k.split_once('@').map_or("", |(_, f)| f);
            function.rsplit('.').next().unwrap_or(function).to_owned()
        })
        .collect();
    // one alternation a language, where the Python searched once a name: the same answer, any name defined, at one pass a file
    let alternation = names
        .iter()
        .map(|n| fancy_regex::escape(n).into_owned())
        .collect::<Vec<_>>()
        .join("|");
    let python = py_re(&format!(r"(?m)^\s*def (?:{alternation})\("));
    let rust = py_re(&format!(
        r"(?m)^\s*(?:pub(?:\(crate\))?\s+)?fn (?:{alternation})\b"
    ));
    let defines = |text: &str, rust_file: bool| {
        !names.is_empty() && matches(if rust_file { &rust } else { &python }, text)
    };
    let mut found = Vec::new();
    for p in rglob(&root.join("l7r"), ".py") {
        if defines(&read(&p)?, false) {
            found.push(p);
        }
    }
    // ...AND IN THE RUST PHASES (feature 444 T19): a counter a Rust function keeps names it as a Python one does, and its `.rs`
    // file rides in the bundle beside the Python
    for p in rglob(&root.join(RUST), ".rs") {
        if !in_build_tree(&p) && defines(&read(&p)?, true) {
            found.push(p);
        }
    }
    // ...AND WHEREVER A KEY IS COUNTED BY ITS OWN NAME (the round arbiter's tooling fix on ask:444-T16-field-audit-5): a key that
    // names no function - `write@field_ink`, counted in the ink's `draw` - brought no module, and the audit could not see its loops
    for p in keyed_files(root, counts)? {
        if !found.contains(&p) {
            found.push(p);
        }
    }
    Ok(found)
}

/// The modules under `l7r/` that count one of the stage's keys by its own name (`"write@field_ink"` in the source).
///
/// # Errors
///
/// A source that does not read, or a counters' row Python could not iterate.
pub(super) fn keyed_files(root: &Path, counts: &[Value]) -> R<Vec<PathBuf>> {
    let keys: Vec<String> = counter_keys(counts)?
        .iter()
        .map(|k| format!("\"{k}\""))
        .collect();
    let mut out = Vec::new();
    for p in rglob(&root.join("l7r"), ".py") {
        let text = read(&p)?;
        if keys.iter().any(|k| text.contains(k.as_str())) {
            out.push(p);
        }
    }
    Ok(out)
}

/// A path's modification time as Python's `st_mtime` (seconds, the nanoseconds a float fraction).
fn mtime(p: &Path) -> f64 {
    use std::os::unix::fs::MetadataExt;
    // every source was read before its time is asked (the counted and keyed modules, the stage's), so none fails here
    #[expect(
        clippy::cast_precision_loss,
        reason = "a file time in seconds and nanoseconds, as CPython's st_mtime computes it"
    )]
    std::fs::metadata(p).map_or(0.0, |m| m.mtime() as f64 + m.mtime_nsec() as f64 * 1e-9)
}

/// The newest modification time of the engine's sources - its Python and its Rust phases (their build trees left out).
fn newest_source(root: &Path) -> f64 {
    let mut sources = rglob(&root.join("l7r"), ".py");
    sources.extend(
        rglob(&root.join(RUST), ".rs")
            .into_iter()
            .filter(|q| !in_build_tree(q)),
    );
    sources
        .iter()
        .fold(0.0_f64, |newest, q| newest.max(mtime(q)))
}

/// The stage's section of the newest kept `make perf-fanout` report, or why there is none (`STALE: ` opening a refusal).
///
/// # Errors
///
/// A report or a source that does not read.
pub(super) fn fanout_section(root: &Path, phase: &str) -> R<String> {
    let Some(newest) = glob(&root.join(FANOUT), "", ".txt")
        .into_iter()
        .filter(|p| is_fanout(p))
        .next_back()
    else {
        return Ok(format!(
            "no `make perf-fanout` report is kept: run `make perf-fanout STAGES={phase}`\n"
        ));
    };
    let rel = newest
        .strip_prefix(root)
        .unwrap_or(&newest)
        .to_string_lossy()
        .into_owned();
    // ...NEVER A STALE ONE (the round arbiter's tooling fix on ask:444-T16-field-audit-5: an audit got T12's report of a deleted
    // engine and rebuilt the chains by hand): a report older than the newest engine source is refused, with the command
    if mtime(&newest) < newest_source(root) {
        return Ok(format!("STALE: {rel} is older than the engine it would describe - run `make perf-fanout STAGES={phase}` first\n"));
    }
    let text = read(&newest)?;
    // a stage's section opens `<stage>: ` at column 0
    let section = py_re(&format!(
        r"(?ms)^{}: .*?(?=^[a-z_]+: |\Z)",
        fancy_regex::escape(phase)
    ));
    let found = section
        .find(&text)
        .ok()
        .flatten()
        .map(|m| m.as_str().to_owned());
    Ok(format!(
        "from {rel}\n\n{}",
        found.unwrap_or_else(|| format!("(the report has no section for {phase})\n"))
    ))
}

/// `*-fanout-*.txt`.
fn is_fanout(p: &Path) -> bool {
    let name = p.file_name().unwrap_or_default().to_string_lossy();
    name.strip_suffix(".txt")
        .is_some_and(|stem| stem.contains("-fanout-"))
}

/// A module's tree and what it defines, read once a run.
struct Parsed {
    tree: Module,
    defined: HashSet<String>,
}

/// Every function and class a module defines, at its top level or as a method.
fn defined(tree: &Module) -> HashSet<String> {
    pyast::walk(tree)
        .into_iter()
        .filter_map(|n| match &n.what {
            What::Def(name) | What::Class(name, _) => Some(name.clone()),
            _ => None,
        })
        .collect()
}

/// A module's imports from `l7r`: each name brought in by `from M import n as b` (b -> (M, n)), each `import M as m` (m -> M).
type Imports = (HashMap<String, (String, String)>, HashMap<String, String>);

/// The parsed modules of one run, each read once (the GM 2026-11-07: "the literal most important thing here is making things
/// FAST": an audit parsed and walked the same modules some 1,200 times, 18 s).
pub(super) struct Code<'a> {
    root: &'a Path,
    parsed: HashMap<PathBuf, std::rc::Rc<Parsed>>,
}

impl<'a> Code<'a> {
    pub(super) fn new(root: &'a Path) -> Self {
        Code {
            root,
            parsed: HashMap::new(),
        }
    }

    fn parse(&mut self, path: &Path) -> R<std::rc::Rc<Parsed>> {
        if let Some(p) = self.parsed.get(path) {
            return Ok(p.clone());
        }
        let tree = pyast::parse(&read(path)?).map_err(|e| format!("{}: {e}", path.display()))?;
        let p = std::rc::Rc::new(Parsed {
            defined: defined(&tree),
            tree,
        });
        self.parsed.insert(path.to_owned(), p.clone());
        Ok(p)
    }

    fn module_file(&self, dotted: &str) -> Option<PathBuf> {
        let p = dotted
            .split('.')
            .filter(|s| !s.is_empty())
            .fold(self.root.to_owned(), |p, part| p.join(part));
        let py = p.with_extension("py");
        if py.is_file() {
            return Some(py);
        }
        let init = p.join("__init__.py");
        init.is_file().then_some(init)
    }

    /// A module's imports from `l7r`, as `_imports_of` reads them in `ast.walk`'s order (a later binding of a name wins).
    fn imports(&self, path: &Path, tree: &Module) -> Imports {
        let rel = path.strip_prefix(self.root).unwrap_or(path);
        let pkg: Vec<String> = rel
            .parent()
            .map(|d| d.iter().map(|c| c.to_string_lossy().into_owned()).collect())
            .unwrap_or_default();
        let (mut names, mut mods) = (HashMap::new(), HashMap::new());
        for n in pyast::walk(tree) {
            match &n.what {
                What::From(module, level, aliases) => {
                    let base = if *level == 0 {
                        String::new()
                    } else {
                        let len = isize::try_from(pkg.len()).unwrap_or(0);
                        let end = len - isize::try_from(*level).unwrap_or(0) + 1;
                        let end = usize::try_from(if end < 0 {
                            (len + end).max(0)
                        } else {
                            end.min(len)
                        })
                        .unwrap_or(0);
                        pkg[..end].join(".")
                    };
                    let module = [base.as_str(), module.as_str()]
                        .iter()
                        .filter(|x| !x.is_empty())
                        .copied()
                        .collect::<Vec<_>>()
                        .join(".");
                    for (name, asname) in aliases {
                        let bound = asname.clone().unwrap_or_else(|| name.clone());
                        let whole = format!("{module}.{name}");
                        if whole.starts_with("l7r.") && self.module_file(&whole).is_some() {
                            mods.insert(bound, whole); // a module imported by name (`from . import water`)
                        } else if module.starts_with("l7r.") {
                            names.insert(bound, (module.clone(), name.clone()));
                        }
                    }
                }
                What::Import(aliases) => {
                    for (name, asname) in
                        aliases.iter().filter(|(name, _)| name.starts_with("l7r."))
                    {
                        mods.insert(asname.clone().unwrap_or_else(|| name.clone()), name.clone());
                    }
                }
                _ => {}
            }
        }
        (names, mods)
    }

    /// The file defining `name` imported from `module`: the module itself, the module it re-exports the name from (followed),
    /// or, for a package, the submodule that defines it.
    fn definer(&mut self, module: &str, name: &str, seen: &BTreeSet<String>) -> R<Option<PathBuf>> {
        let Some(f) = self.module_file(module) else {
            return Ok(None);
        };
        if seen.contains(module) {
            return Ok(None);
        }
        let parsed = self.parse(&f)?;
        if parsed.defined.contains(name) {
            return Ok(Some(f));
        }
        let mut deeper = seen.clone();
        deeper.insert(module.to_owned());
        let (names, _) = self.imports(&f, &parsed.tree);
        if let Some((m, n)) = names.get(name) {
            // `from .law_water import crossing_points`
            if let Some(q) = self.definer(m, n, &deeper)? {
                return Ok(Some(q));
            }
        }
        if f.file_name().is_some_and(|n| n == "__init__.py") {
            for q in rglob(f.parent().unwrap_or(self.root), ".py")
                .into_iter()
                .filter(|q| *q != f)
            {
                let rel = q.strip_prefix(self.root).unwrap_or(&q).with_extension("");
                let sub = rel
                    .iter()
                    .map(|c| c.to_string_lossy().into_owned())
                    .collect::<Vec<_>>()
                    .join(".");
                let sub = sub.strip_suffix(".__init__").unwrap_or(&sub).to_owned();
                // a submodule's own, or its re-export
                if let Some(found) = self.definer(&sub, name, &deeper)? {
                    return Ok(Some(found));
                }
            }
        }
        Ok(None)
    }

    /// The modules defining what the stage's own code CALLS - a function imported from `l7r`, a module's function called through
    /// it, a Settlement method called on `self` or `s` that the calling file does not define - and each called name whose definition
    /// cannot be found (the round arbiter's tooling fix on ask:444-T16-field-audit-6: audits 4 and 5 both found called code missing
    /// from their bundles - `field_channel`, `rest_basin` - and the gap cost a superseded GM question).
    pub(super) fn called_files(&mut self, seeds: &[PathBuf]) -> R<(Vec<PathBuf>, Vec<String>)> {
        let settlement = self.root.join("l7r").join("diagram").join("settlement");
        let mut mixins: Vec<(PathBuf, std::rc::Rc<Parsed>)> = Vec::new();
        if settlement.is_dir() {
            for q in rglob(&settlement, ".py") {
                let parsed = self.parse(&q)?;
                mixins.push((q, parsed));
            }
        }
        let (mut found, mut missing): (Vec<PathBuf>, BTreeSet<String>) =
            (Vec::new(), BTreeSet::new());
        for p in seeds {
            let parsed = self.parse(p)?;
            let (names, mods) = self.imports(p, &parsed.tree);
            let rel = p
                .strip_prefix(self.root)
                .unwrap_or(p)
                .to_string_lossy()
                .into_owned();
            for n in pyast::walk(&parsed.tree) {
                let What::Call(callee) = &n.what else {
                    continue;
                };
                let (hit, what) = match callee {
                    Callee::Name(id) if names.contains_key(id) => {
                        let (m, name) = &names[id];
                        (
                            vec![self.definer(m, name, &BTreeSet::new())?],
                            format!("{name} (from {m}, called in {rel})"),
                        )
                    }
                    Callee::Attr(base, attr) if mods.contains_key(base) => {
                        let m = &mods[base];
                        (
                            vec![self.definer(m, attr, &BTreeSet::new())?],
                            format!("{m}.{attr} (called in {rel})"),
                        )
                    }
                    // none is no refusal: a dict's or a list's own method
                    Callee::Attr(base, attr)
                        if (base == "self" || base == "s") && !parsed.defined.contains(attr) =>
                    {
                        (
                            mixins
                                .iter()
                                .filter(|(_, d)| d.defined.contains(attr))
                                .map(|(q, _)| Some(q.clone()))
                                .collect(),
                            String::new(),
                        )
                    }
                    _ => continue,
                };
                for q in hit {
                    match q {
                        None => {
                            missing.insert(what.clone());
                        }
                        Some(q) if !found.contains(&q) && !seeds.contains(&q) => found.push(q),
                        Some(_) => {}
                    }
                }
            }
        }
        Ok((found, missing.into_iter().collect()))
    }

    /// Today's names - every module and package, function, method, class, and module- or class-level name defined under `l7r/`
    /// (a local variable is not one) - and the names a derivation may still use: each knob's name and forms, each stage's name,
    /// and each key of the pool's hamlet manifests (their nested records' keys too).
    fn code_names(&mut self) -> R<(HashSet<String>, HashSet<String>)> {
        let (mut defined_names, mut allowed) = (HashSet::new(), HashSet::new());
        for f in rglob(&self.root.join("l7r"), ".py") {
            let src = read(&f)?;
            let stem = f
                .file_stem()
                .unwrap_or_default()
                .to_string_lossy()
                .into_owned();
            let parent = f
                .parent()
                .and_then(Path::file_name)
                .unwrap_or_default()
                .to_string_lossy()
                .into_owned();
            defined_names.extend([stem, parent].into_iter().filter(|n| n != "__init__"));
            for c in KNOB.captures_iter(&src).filter_map(Result::ok) {
                allowed.insert(c.get(1).map_or("", |m| m.as_str()).to_owned());
                let forms = c.get(2).map_or("", |m| m.as_str());
                allowed.extend(
                    QUOTED
                        .captures_iter(forms)
                        .filter_map(Result::ok)
                        .filter_map(|q| q.get(1).map(|m| m.as_str().to_owned())),
                );
            }
            let Ok(tree) = pyast::parse(&src) else {
                continue;
            };
            defined_names.extend(defined(&tree));
            defined_names.extend(
                pyast::scope_names(&tree)
                    .into_iter()
                    .filter(|n| n.chars().count() > 2),
            );
        }
        // the budget units' names, the stages, stay a derivation's to use
        let budgets = self.root.join("dev").join("work-budget.json");
        if budgets.is_file() {
            let table: Value = super::loads(&read(&budgets)?)
                .map_err(|e| format!("{}: {e}", budgets.display()))?;
            let Value::Object(top) = table else {
                return Err("AttributeError: the budget table has no .get".to_owned());
            };
            match top.get("stages") {
                None => {}
                Some(Value::Object(stages)) => allowed.extend(stages.keys().cloned()),
                Some(Value::Array(items)) if items.iter().all(Value::is_string) => {
                    allowed.extend(items.iter().filter_map(|v| v.as_str().map(str::to_owned)));
                }
                Some(Value::String(s)) => allowed.extend(s.chars().map(String::from)),
                Some(_) => {
                    return Err("TypeError: the budget table's stages are no names".to_owned())
                }
            }
        }
        for dir in glob(&self.root.join("pool").join("hamlets"), "", "") {
            for f in glob(&dir, "", ".json") {
                // a manifest that does not read is Python's OSError, raised; one that is no UTF-8 or no JSON its ValueError, skipped
                let bytes = std::fs::read(&f).map_err(|e| format!("{}: {e}", f.display()))?;
                if let Some(v) = String::from_utf8(bytes)
                    .ok()
                    .and_then(|t| super::loads(&t).ok())
                {
                    keys(&v, &mut allowed);
                }
            }
        }
        Ok((defined_names, allowed))
    }

    /// GREENFIELD (feature 444 FR-015; the GM 2026-10-29: "the ENTIRE point of what we're doing is to do a greenfield implementation
    /// unencumbered by the bad implementation chopices of our previous implementation"): a derivation names no module, function,
    /// method, class or module- or class-level name of today's code - 110 of them had carried today's design into 20 of the 23
    /// derivations - other than a knob's name or form and a manifest key. A figure only today's code holds is a knob the derivation
    /// names as one, in its own words.
    pub(super) fn code_name_problems(&mut self, text: &str) -> R<Vec<String>> {
        let (defined_names, allowed) = self.code_names()?;
        let mut names = BTreeSet::new();
        for c in IDENT.captures_iter(text).filter_map(Result::ok) {
            let r = c.get(1).or_else(|| c.get(2)).map_or("", |m| m.as_str());
            // a document beside the derivation (`placer.py.txt`) is not a name of the code
            if matches(&DOCUMENT, r) {
                continue;
            }
            names.extend(
                r.split(['.', '/'])
                    .filter(|w| !w.is_empty())
                    .map(str::to_owned),
            );
        }
        let found: Vec<&String> = names
            .iter()
            .filter(|n| defined_names.contains(*n) && !allowed.contains(*n))
            .collect();
        if found.is_empty() {
            return Ok(vec![]);
        }
        let shown: Vec<&str> = found.iter().take(12).map(|s| s.as_str()).collect();
        Ok(vec![format!(
            "today's code's names ({}): {}{} - write the contract from the research and the reference manifests in your own words, a figure only the code holds as a knob you name (FR-015)",
            found.len(),
            shown.join(", "),
            if found.len() > 12 { " ..." } else { "" }
        )])
    }
}

/// Every key of a manifest's mappings, nested ones too, a list's first fifty items read.
fn keys(v: &Value, into: &mut HashSet<String>) {
    match v {
        Value::Object(m) => {
            into.extend(m.keys().cloned());
            for w in m.values() {
                keys(w, into);
            }
        }
        Value::Array(items) => {
            for w in items.iter().take(50) {
                keys(w, into);
            }
        }
        _ => {}
    }
}

#[cfg(test)]
mod tests;
