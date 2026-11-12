//! `make work-budget-bundle MODE=budget|audit PHASE=<stage> [DERIVATION=<file>]` - the `work-budget` agent's bundle (feature 443
//! T05, plan D10; FR-008), ported whole from `scripts/reviews/work_budget_bundle.py` by feature 449 T134 (the round arbiter's
//! `ask:449-phase3-remainder`), its refusals, its words and its files unchanged.
//!
//! MODE BUDGET judges a stage's derivation BEFORE its rebuild, blind to today's code and counts so today's waste cannot anchor the
//! target (the design the GM approved, 2026-10-28, section 4). The bundle holds the derivation, the stage's contract (its
//! `## Contract` section: the manifest keys it reads and writes) and the rubric, and REFUSES a derivation holding a fenced block of
//! Python, a path under `l7r/` or a figure tagged as a current count (`calls` or `ops` beside a number) - each would put today's
//! code or its numbers in front of the judge.
//!
//! MODE AUDIT judges the landed code against its counters: the stage's modules (the file defining `stage_<name>`, and the files under
//! the stage's own package), the newest `make work-budget` run's counts for the stage at each size by kind and by function, its
//! call chains (the stage's section of the newest kept `make perf-fanout` report, `dev/perf-log/*-fanout-*.txt`) and its budget
//! (`dev/work-budget.json`, or `BUDGET=<file>` - the funnel fixture's, FR-009).
//!
//! Written to `/tmp/l7r-check/work-budget-<mode>-<stage>/`, a `MANIFEST.md` naming each file. The agent's first line is its verdict;
//! save it as `verdict.txt` beside the derivation, and write its ledger row (`make ledger-owed`).
//!
//! Where it lives (feature 449 T134): beside `measure work-budget` in the `trials` crate, the work budget's Rust; `budget_change`
//! reads `sizes` from here in process, where the Python imported it. `--sources PHASE` prints, as JSON, the stage's old modules
//! `scripts/gates/phase_sources.py` imported `stage_files` and `counted_files` for (phase 3's Python, run by command, FR-003).

use std::path::{Path, PathBuf};

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use l7r_gate_core::record::args::{parse_with, Spec};
use l7r_guard::shared::py_text::{is_space, SPACE_CLASS};
use l7r_guard::shared::pyjson::dumps;

mod code;
mod derivation;
pub mod pyast;

pub use code::{counted_files, stage_files};
pub use derivation::sizes;

pub(crate) type R<T> = Result<T, String>;

const OUT: &str = "/tmp/l7r-check";
const RUBRIC: &str = "docs/work-budget-rubric.md";
const TABLE: &str = "dev/work-budget.json";
pub(crate) const RUNS: &str = "dev/work-budget";

/// A pattern written for Python's `re`, compiled so it matches as there: `\s` is Python's whitespace (`str.isspace`, the
/// separators `\x1c`-`\x1f` among them, which the regex crate's `\s` leaves out), and `\Z` the end of the text.
pub(crate) fn py_re(pattern: &str) -> Regex {
    let (mut out, mut class, mut chars) = (String::new(), false, pattern.chars().peekable());
    while let Some(c) = chars.next() {
        match (c, chars.peek().copied()) {
            ('\\', Some(n)) => {
                chars.next();
                match n {
                    's' if class => out.push_str(SPACE_CLASS),
                    's' => out.extend(["[", SPACE_CLASS, "]"]),
                    'S' => out.extend(["[^", SPACE_CLASS, "]"]),
                    'Z' => out.push_str("\\z"),
                    _ => {
                        out.push('\\');
                        out.push(n);
                    }
                }
            }
            ('[', _) if !class => {
                class = true;
                out.push(c);
                if chars.peek() == Some(&'^') {
                    out.push('^');
                    chars.next();
                }
                if chars.peek() == Some(&']') {
                    out.push_str("\\]");
                    chars.next();
                }
            }
            (']', _) if class => {
                class = false;
                out.push(c);
            }
            _ => out.push(c),
        }
    }
    Regex::new(&out).unwrap_or_else(|e| unreachable!("{pattern}: {e}"))
}

/// Whether `c` is whitespace to Python.
fn is_py_space(c: char) -> bool {
    is_space(c)
}

/// Whether `lit` is a number Python's tokenizer reads.
fn pyast_number(lit: &str) -> bool {
    pyast::is_number(lit)
}

/// `path.read_text(encoding="utf-8")`: the failure Python raised for a file that does not read.
pub(crate) fn read(path: &Path) -> R<String> {
    l7r_gate_core::record::repo::read_text(path)
}

/// A directory's entries, in the order the system lists them (`os.scandir`'s, which `glob` keeps before any sort).
fn listing(dir: &Path) -> Vec<PathBuf> {
    std::fs::read_dir(dir)
        .map(|rd| rd.filter_map(Result::ok).map(|e| e.path()).collect())
        .unwrap_or_default()
}

/// `sorted(dir.glob(f"{prefix}*{suffix}"))`: the entries whose names open with `prefix` and end with `suffix`, files and
/// directories alike, as `pathlib` sorts them.
pub(crate) fn glob(dir: &Path, prefix: &str, suffix: &str) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = listing(dir)
        .into_iter()
        .filter(|p| {
            let n = p.file_name().unwrap_or_default().to_string_lossy();
            n.len() >= prefix.len() + suffix.len() && n.starts_with(prefix) && n.ends_with(suffix)
        })
        .collect();
    out.sort();
    out
}

/// `sorted(dir.rglob(f"*{suffix}"))`: every entry below `dir` whose name ends with `suffix`, a linked directory not followed.
pub(crate) fn rglob(dir: &Path, suffix: &str) -> Vec<PathBuf> {
    let mut out = Vec::new();
    let mut todo = vec![dir.to_owned()];
    while let Some(d) = todo.pop() {
        for p in listing(&d) {
            if p.file_name()
                .unwrap_or_default()
                .to_string_lossy()
                .ends_with(suffix)
            {
                out.push(p.clone());
            }
            if p.symlink_metadata().is_ok_and(|m| m.is_dir()) {
                todo.push(p);
            }
        }
    }
    out.sort();
    out
}

/// A write's failure at `path` as the error Python raised there.
pub(crate) fn io(path: &Path, done: std::io::Result<()>) -> R<()> {
    done.map_err(|e| format!("{}: {e}", path.display()))
}

fn write(path: &Path, text: &str) -> R<()> {
    io(path, std::fs::write(path, text))
}

fn copy(from: &Path, to: &Path) -> R<()> {
    std::fs::copy(from, to)
        .map(drop)
        .map_err(|e| format!("{}: {e}", from.display()))
}

fn mkdir(path: &Path) -> R<()> {
    io(path, std::fs::create_dir_all(path))
}

fn load(path: &Path) -> R<Value> {
    loads(&read(path)?).map_err(|e| format!("{}: {e}", path.display()))
}

/// The marker a non-finite float travels under inside a `serde_json` value, which holds none: Python's `json` reads and writes
/// `Infinity`, `-Infinity` and `NaN`, so a table `float()` wrote one into reads back, and writes again, as it did (feature 449
/// T134, the coordinator's ruling: the port matches the Python on non-finite figures).
const NONFINITE: &str = "\u{1}pyfloat:";

/// `json.loads(text)`: JSON, and Python's three non-finite numbers where a value stands.
///
/// # Errors
///
/// The text is no JSON Python reads: why.
pub(crate) fn loads(text: &str) -> Result<Value, String> {
    if !text.contains("NaN") && !text.contains("Infinity") {
        return serde_json::from_str(text).map_err(|e| e.to_string());
    }
    let (mut out, mut rest, mut in_string, mut escaped) =
        (String::with_capacity(text.len()), text, false, false);
    while let Some(c) = rest.chars().next() {
        if !in_string {
            if let Some(word) = ["-Infinity", "Infinity", "NaN"]
                .into_iter()
                .find(|w| rest.starts_with(w))
            {
                out.extend(["\"\\u0001pyfloat:", word, "\""]);
                rest = &rest[word.len()..];
                continue;
            }
        }
        if in_string {
            if escaped {
                escaped = false;
            } else if c == '\\' {
                escaped = true;
            } else if c == '"' {
                in_string = false;
            }
        } else if c == '"' {
            in_string = true;
        }
        out.push(c);
        rest = &rest[c.len_utf8()..];
    }
    serde_json::from_str(&out).map_err(|e| e.to_string())
}

/// `json.dumps(value, indent=indent)`, a non-finite figure written as Python writes it.
#[must_use]
pub(crate) fn dumps_py(value: &Value, indent: Option<usize>) -> String {
    let text = dumps(value, indent, true);
    if !text.contains("\\u0001pyfloat:") {
        return text;
    }
    ["-Infinity", "Infinity", "NaN"].iter().fold(text, |t, w| {
        t.replace(&format!("\"\\u0001pyfloat:{w}\""), w)
    })
}

/// A float as a JSON value: a number, or the marker of a non-finite one.
#[must_use]
pub(crate) fn num(f: f64) -> Value {
    if f.is_finite() {
        json!(f)
    } else {
        let word = if f.is_nan() {
            "NaN"
        } else if f > 0.0 {
            "Infinity"
        } else {
            "-Infinity"
        };
        Value::String(format!("{NONFINITE}{word}"))
    }
}

/// The non-finite figure a marker stands for.
#[must_use]
pub(crate) fn nonfinite(text: &str) -> Option<f64> {
    text.strip_prefix(NONFINITE).map(|w| match w {
        "NaN" => f64::NAN,
        "Infinity" => f64::INFINITY,
        _ => f64::NEG_INFINITY,
    })
}

/// The MODE BUDGET bundle: its exit status and its line.
fn budget_bundle(root: &Path, phase: &str, derivation: &str, out: &Path) -> R<(i32, String)> {
    let src = root.join(derivation);
    if !src.is_file() {
        return Ok((
            2,
            format!("work-budget-bundle: no derivation at {derivation}"),
        ));
    }
    let text = read(&src)?;
    let mut bad = derivation::refusals(&text);
    bad.extend(code::Code::new(root).code_name_problems(&text)?);
    if !bad.is_empty() {
        return Ok((1, format!("work-budget-bundle: REFUSED - a MODE BUDGET bundle holds no code and no counts of today's code:\n{}", indented(&bad))));
    }
    let Some(contract) = derivation::CONTRACT
        .find(&text)
        .ok()
        .flatten()
        .map(|m| m.as_str().to_owned())
    else {
        return Ok((1, "work-budget-bundle: REFUSED - the derivation has no `## Contract` section (what the stage reads and writes)".to_owned()));
    };
    let mut short = derivation::form_problems(&text)?;
    short.extend(derivation::answer_problems(&src, &text)?);
    if !short.is_empty() {
        return Ok((1, format!("work-budget-bundle: REFUSED - the derivation is short of the template's fields ({}):\n{}", derivation::TEMPLATE, indented(&short))));
    }
    mkdir(out)?;
    write(&out.join("derivation.md"), &text)?;
    write(&out.join("contract.md"), &contract)?;
    // the earlier verdicts, for the judge to confirm each closed
    let name = src.file_name().unwrap_or_default().to_string_lossy();
    let stage = name.strip_suffix(".derivation.md").unwrap_or(&name);
    let mut verdicts = derivation::verdict_files(src.parent().unwrap_or(root), stage);
    verdicts.sort();
    for v in verdicts {
        copy(&v, &out.join(v.file_name().unwrap_or_default()))?;
    }
    copy(&root.join(RUBRIC), &out.join("rubric.md"))?;
    write(
        &out.join("MANIFEST.md"),
        &format!(
            "# work-budget MODE BUDGET - {phase}\n\nMODE BUDGET: judge the derivation before the rebuild. Read, beside this file:\n\n\
             - `rubric.md` - the standards S1-S11 and the worked homestead reference;\n\
             - `contract.md` - what the stage reads and writes;\n\
             - `derivation.md` - the pseudocode and the operation count, factor by factor;\n\
             - any `<stage>.verdict-<N>.txt` - the earlier verdicts; the derivation's `## Earlier findings` answers each - confirm each closed.\n\n\
             The first line of your reply is the verdict: SOUND, LOOSE or UNDERIVED.\n"
        ),
    )?;
    Ok((0, out.join("MANIFEST.md").to_string_lossy().into_owned()))
}

fn indented(lines: &[String]) -> String {
    lines
        .iter()
        .map(|b| format!("  {b}"))
        .collect::<Vec<_>>()
        .join("\n")
}

/// The newest `make work-budget` run's rows for `phase`: each roll's seed, households and the stage's counts.
fn stage_rows(run: &Value, phase: &str) -> R<Vec<Value>> {
    let rows: Vec<&Value> = match &run["rows"] {
        Value::Array(rows) => rows.iter().collect(),
        Value::Object(m) if m.is_empty() => vec![],
        _ => return Err("KeyError or TypeError: the run's rows".to_owned()),
    };
    let mut out = Vec::new();
    for r in rows {
        let stage = match r.get("stages") {
            Some(Value::Object(stages)) => stages.get(phase),
            _ => return Err("KeyError or TypeError: a row's stages".to_owned()),
        };
        let Some(stage) = stage else { continue };
        let (Some(seed), Some(households), Value::Object(fields)) =
            (r.get("seed"), r.get("households"), stage)
        else {
            return Err("KeyError or TypeError: a row's seed, households or stage".to_owned());
        };
        let mut row = Map::new();
        row.insert("seed".to_owned(), seed.clone());
        row.insert("households".to_owned(), households.clone());
        for (k, v) in fields {
            row.insert(k.clone(), v.clone());
        }
        out.push(Value::Object(row));
    }
    Ok(out)
}

/// The MODE AUDIT bundle: its exit status and its line.
fn audit_bundle(root: &Path, phase: &str, out: &Path, budget: &str) -> R<(i32, String)> {
    let mut files = stage_files(root, phase)?;
    if files.is_empty() {
        return Ok((
            2,
            format!(
                "work-budget-bundle: no `stage_{phase}` under {} or {}",
                code::RUST,
                code::HAMLET
            ),
        ));
    }
    let Some(newest) = glob(&root.join(RUNS), "", ".json").pop() else {
        return Ok((
            2,
            "work-budget-bundle: no `make work-budget` run is recorded - run it first".to_owned(),
        ));
    };
    let run = load(&newest)?;
    let counts = stage_rows(&run, phase)?;
    let table = load(&root.join(TABLE))?;
    let mut seeds: Vec<PathBuf> = files
        .iter()
        .filter(|p| p.extension().is_some_and(|e| e == "py"))
        .cloned()
        .collect();
    for p in code::keyed_files(root, &counts)? {
        if !files.contains(&p) {
            seeds.push(p);
        }
    }
    for p in counted_files(root, &counts)? {
        if !files.contains(&p) {
            files.push(p);
        }
    }
    let (called, missing) = code::Code::new(root).called_files(&seeds)?;
    if !missing.is_empty() {
        return Ok((2, format!("work-budget-bundle: the stage's code calls what no module under l7r/ defines - the audit could not read it:\n  {}", missing.join("\n  "))));
    }
    for p in called {
        if !files.contains(&p) {
            files.push(p);
        }
    }
    let chains = code::fanout_section(root, phase)?;
    if let Some(stale) = chains.strip_prefix("STALE: ") {
        return Ok((
            2,
            format!(
                "work-budget-bundle: {}",
                l7r_guard::shared::py_text::strip(stale)
            ),
        ));
    }
    mkdir(out)?;
    mkdir(&out.join("code"))?;
    for p in &files {
        copy(p, &out.join("code").join(code::bundled_name(root, p)))?;
    }
    let summary = match &run["summary"]["stages"] {
        Value::Object(stages) => stages.get(phase).cloned().unwrap_or(Value::Null),
        _ => return Err("KeyError or AttributeError: the run's summary stages".to_owned()),
    };
    let name = newest
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    write(
        &out.join("counts.json"),
        &dumps_py(
            &json!({"run": name, "summary": summary, "rolls": counts}),
            Some(1),
        ),
    )?;
    write(&out.join("chains.txt"), &chains)?;
    let pinned = if budget.is_empty() {
        match &table["stages"] {
            Value::Object(stages) => stages.get(phase).cloned().unwrap_or(Value::Null),
            _ => return Err("KeyError or AttributeError: the budget table's stages".to_owned()),
        }
    } else {
        load(&root.join(budget))?
    };
    write(&out.join("budget.json"), &dumps_py(&pinned, Some(1)))?;
    copy(&root.join(RUBRIC), &out.join("rubric.md"))?;
    let listed: Vec<String> = files.iter().map(|p| code::bundled_name(root, p)).collect();
    write(&out.join("MANIFEST.md"), &audit_manifest(phase, &listed))?;
    Ok((0, out.join("MANIFEST.md").to_string_lossy().into_owned()))
}

/// The MODE AUDIT bundle's `MANIFEST.md`, naming each file of its `code/`.
fn audit_manifest(phase: &str, listed: &[String]) -> String {
    format!(
        "# work-budget MODE AUDIT - {phase}\n\nMODE AUDIT: judge the landed code against its counters. Read, beside this file:\n\n\
         - `rubric.md` - the standards S1-S11;\n\
         - `code/` - the stage's modules and every module defining a function its counters name, each named by its path (`/` as `__`): {};\n\
         - `counts.json` - the newest run's counted operations for the stage at each size, by kind and by function;\n\
         - `chains.txt` - the callers above each counted function;\n\
         - `budget.json` - the stage's pinned budget.\n\n\
         The first line of your reply is the verdict: WITHIN, LEEWAY (over the budget and at most twice it, the excess named and \
         reasonable: rubric S10, feature 444 FR-022), OVER or UNCOUNTED.\n",
        listed.join(", ")
    )
}

/// `--sources PHASE`: the stage's old modules, relative to the root - the Python defining `stage_<phase>` and every module
/// defining a function its counters name in the newest run - as `phase_sources.sources` read them before its extra globs, a
/// JSON list (feature 449 T134: `phase_sources.py` imported `stage_files` and `counted_files`; it runs this, one process a call).
fn sources(root: &Path, phase: &str) -> R<String> {
    // THE OLD CODE IS THE PYTHON: `stage_files` also names a Rust phase's `.rs` source (the audit bundle reads it), which is the
    // very code the task writes and must stay readable
    let mut files: Vec<PathBuf> = stage_files(root, phase)?
        .into_iter()
        .filter(|p| p.extension().is_some_and(|e| e == "py"))
        .collect();
    if let Some(newest) = glob(&root.join(RUNS), "", ".json").pop() {
        let run = load(&newest)?;
        let Value::Array(rows) = &run["rows"] else {
            return Err("KeyError or TypeError: the run's rows".to_owned());
        };
        let mut counts = Vec::new();
        for r in rows {
            let Some(Value::Object(stages)) = r.get("stages") else {
                return Err("KeyError or TypeError: a row's stages".to_owned());
            };
            counts.extend(stages.get(phase).cloned());
        }
        for p in counted_files(root, &counts)? {
            if !files.contains(&p) {
                files.push(p);
            }
        }
    }
    let rel: Vec<Value> = files
        .iter()
        .map(|p| {
            Value::String(
                p.strip_prefix(root)
                    .unwrap_or(p)
                    .to_string_lossy()
                    .into_owned(),
            )
        })
        .collect();
    Ok(dumps(&Value::Array(rel), None, true) + "\n")
}

fn reply(stdout: String, stderr: String, code: i32) -> crate::Reply {
    crate::Reply {
        stdout,
        stderr,
        code,
    }
}

/// `l7r-gate work-budget-bundle budget|audit PHASE [--derivation F] [--root R] [--out O] [--budget B]`, and `--sources PHASE`.
#[must_use]
pub fn cli(args: &[String], root: &Path) -> crate::Reply {
    let usage = |why: &str| {
        reply(String::new(), format!("usage: work_budget_bundle.py budget|audit PHASE [--derivation F] [--out O] [--budget B]: {why}\n"), 2)
    };
    let specs = [
        Spec::value("--derivation"),
        Spec::value("--root"),
        Spec::value("--out"),
        Spec::value("--budget"),
        // named so no prefix argparse took for the Python's own flags (`--o` for `--out`) turns ambiguous
        Spec::value("--sources"),
    ];
    let a = match parse_with(args, &specs, 2) {
        Ok(a) => a,
        Err(why) => return usage(&why),
    };
    let root = PathBuf::from(a.text("--root", &root.to_string_lossy()));
    if a.has("--sources") {
        return match sources(&root, a.text("--sources", "")) {
            Ok(out) => reply(out, String::new(), 0),
            Err(why) => reply(String::new(), format!("work-budget-bundle: {why}\n"), 1),
        };
    }
    let [mode, phase] = a.positional.as_slice() else {
        return usage("the following arguments are required: mode, phase");
    };
    if !matches!(mode.as_str(), "budget" | "audit") {
        return usage(&format!(
            "argument mode: invalid choice: '{mode}' (choose from budget, audit)"
        ));
    }
    if phase.is_empty() {
        return reply(
            String::new(),
            "work-budget-bundle: PHASE= is required\n".to_owned(),
            2,
        );
    }
    let out = PathBuf::from(a.text("--out", ""));
    let out = if out.as_os_str().is_empty() {
        Path::new(OUT).join(format!("work-budget-{mode}-{phase}"))
    } else {
        out
    };
    let run = || -> R<(i32, String)> {
        if out.exists() {
            if out.symlink_metadata().is_ok_and(|m| m.is_symlink()) || !out.is_dir() {
                return Err(format!(
                    "OSError: cannot remove {} as a tree",
                    out.display()
                ));
            }
            io(&out, std::fs::remove_dir_all(&out))?;
        }
        if mode == "budget" {
            let derivation = a.text("--derivation", "");
            if derivation.is_empty() {
                return Ok((
                    2,
                    "work-budget-bundle: MODE=budget needs DERIVATION=<file>".to_owned(),
                ));
            }
            return budget_bundle(&root, phase, derivation, &out);
        }
        audit_bundle(&root, phase, &out, a.text("--budget", ""))
    };
    match run() {
        Ok((0, msg)) => reply(msg + "\n", String::new(), 0),
        Ok((code, msg)) => reply(String::new(), msg + "\n", code),
        Err(why) => reply(String::new(), format!("work-budget-bundle: {why}\n"), 1),
    }
}

#[cfg(test)]
mod tests;
