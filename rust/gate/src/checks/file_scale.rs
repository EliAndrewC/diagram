//! No source file past the ~1,000-line bar, and no directory past 5,000 files (constitution Principle X clause 13; feature 449 T065, from `check-file-scale.py`). A run is recorded by `usage_log` under `USAGE_LOG_TOOL`.

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use super::{git_z, Outcome};

pub(super) const USAGE_LOG_TOOL: &str = "check-file-scale";
const MAX_LINES: usize = 1000;
const MARKER: &str = "FILE_SIZE_OK:";
const MIN_REASON: usize = 40;
const HEADER_LINES: usize = 40;
const SKIP_PARTS: [&str; 6] = [
    "legacy-hand-authored-pool",
    ".clones",
    "specs",
    ".git",
    "__pycache__",
    "node_modules",
];
const MAX_DIR_FILES: usize = 5000;
const DIR_SKIP_PARTS: [&str; 3] = [".clones", ".git", "node_modules"];
const GUIDANCE: &str = "\n  Each file above is past the ~1,000-line bar of constitution Principle X clause 13. The clone\n  doing this work splits it before the work can merge - that is the rule the GM gated on\n  2026-08-31, and it is not deferrable to a later pass.\n\n  SPLIT IT - NEVER TRIM IT TO JUST UNDER THE BAR (the GM, 2026-10-21, feature 405 T53): folding or\n  cutting lines to land at 1,000 leaves the file at the bar, and the next edit pays again.\n\n  THE PRESCRIBED SHAPE: the file becomes a DIRECTORY-MODULE - `hamletgen/ways.py` becomes\n  `hamletgen/ways/` with sub-modules of about 666 lines each (2/3 of the bar, a guideline,\n  not a check), its `__init__.py` re-exporting every name importers used, so no importer changes -\n  carrying a CLAUDE.md that indexes them with a \"look here when\" line each, so a future session\n  loads only the part it needs. A `.rs` file splits the same way: `ways.rs` becomes `ways/` with a `mod.rs`\n  (or `ways.rs` beside the folder) declaring its sub-modules and `pub use`-ing what callers named.\n\n  Read, in this order:\n    - .specify/memory/constitution.md, Principle X clause 13 (the rule and both carve-outs)\n    - CLAUDE.md, \"Verification and iteration\" (the operational mirror)\n    - the deleted engine's structures/ package - a worked exemplar (git history): its\n      __init__.py composes the sub-mixins back into the one class its caller imports, and its\n      CLAUDE.md is the index format. Seventeen more packages in this tree follow it.\n\n  TWO CARVE-OUTS, before you split:\n    - ORDERED DATA (clause 13): one cohesive ordered dataset whose row order IS the execution\n      contract may stay large - say so in the first 40 lines with `FILE_SIZE_OK: <reason>`,\n      at least 40 characters. `make audit` lists every file that takes this.\n    - A DERIVED ROSTER (clause 14): if the bulk restates what code elsewhere already declares,\n      splitting is the WRONG fix - duplicated information does not shrink by being divided.\n      Derive the surface instead (feature 027 took 3,148 lines to 63 that way).\n";
const DIR_GUIDANCE: &str = "\n  Each directory above holds more than 5,000 files of its own. Split it into subdirectories by a\n  key the files already carry - a month for a log (`dev/run-log/<YYYY-MM>/`, the worked example), a leading\n  number range or a kind for content - and make every reader search recursively, so nothing written in the old\n  layout is lost. A shell glob over one flat folder fails outright near 25,000 files (\"Argument list too long\").\n";

/// Raw lines, as `wc -l` and `nl -b a` count them, which is what clause 13 means: a last line with no newline counts.
fn raw_lines(data: &[u8]) -> usize {
    data.split(|b| *b == b'\n').count() - 1 + usize::from(data.last().is_some_and(|b| *b != b'\n'))
}

/// The stated reason from a marker in the file's first lines.
fn justification(data: &[u8]) -> Option<String> {
    let text = String::from_utf8_lossy(data);
    text.lines()
        .take(HEADER_LINES)
        .find_map(|l| l.split_once(MARKER).map(|(_, r)| r.trim().to_owned()))
}

fn walk(dir: &Path, into: &mut Vec<PathBuf>) {
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let path = entry.path();
        if entry.file_type().is_ok_and(|t| t.is_dir()) {
            walk(&path, into);
        } else {
            into.push(path);
        }
    }
}

/// Files of the tree as repository-relative text: tracked and not ignored in a git tree, else a walk.
fn listed(root: &Path, pathspec: &[&str]) -> Vec<String> {
    let mut args = vec![
        "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard",
    ];
    args.extend(pathspec);
    git_z(root, &args).unwrap_or_else(|| {
        let mut found = Vec::new();
        walk(root, &mut found);
        found
            .iter()
            .filter_map(|p| p.strip_prefix(root).ok())
            .map(|p| p.to_string_lossy().into_owned())
            .collect()
    })
}

fn wanted(rel: &str) -> bool {
    super::has_ext(rel, "rs") && !rel.split('/').any(|p| SKIP_PARTS.contains(&p))
}

#[derive(Debug, Default, PartialEq, Eq)]
struct Scan {
    over: Vec<(String, usize)>,
    justified: Vec<(String, usize, String)>,
    scanned: usize,
}

fn run(root: &Path) -> Scan {
    let mut rels: Vec<String> = listed(root, &["*.rs"])
        .into_iter()
        .filter(|r| wanted(r) && root.join(r).is_file())
        .collect();
    rels.sort();
    rels.dedup();
    let mut scan = Scan {
        scanned: rels.len(),
        ..Scan::default()
    };
    for rel in rels {
        let data = std::fs::read(root.join(&rel)).unwrap_or_default();
        let lines = raw_lines(&data);
        if lines <= MAX_LINES {
            continue;
        }
        match justification(&data).filter(|r| r.chars().count() >= MIN_REASON) {
            Some(reason) => scan.justified.push((rel, lines, reason)),
            None => scan.over.push((rel, lines)),
        }
    }
    scan
}

/// Files directly in each directory.
fn dir_counts(root: &Path) -> BTreeMap<String, usize> {
    let mut counts = BTreeMap::new();
    let mut rels = listed(root, &[]);
    rels.sort();
    rels.dedup();
    for rel in rels {
        let parent = rel.rsplit_once('/').map_or(".", |(p, _)| p);
        if !parent.split('/').any(|p| DIR_SKIP_PARTS.contains(&p)) {
            *counts.entry(parent.to_owned()).or_insert(0) += 1;
        }
    }
    counts
}

/// Largest first, a tie by name.
fn crowded(root: &Path, limit: usize) -> Vec<(String, usize)> {
    let mut found: Vec<(String, usize)> = dir_counts(root)
        .into_iter()
        .filter(|(_, n)| *n > limit)
        .collect();
    found.sort_by_key(|(_, n)| std::cmp::Reverse(*n));
    found
}

fn thousands(n: usize) -> String {
    let digits = n.to_string();
    let mut out = String::new();
    for (at, c) in digits.chars().enumerate() {
        if at > 0 && (digits.len() - at) % 3 == 0 {
            out.push(',');
        }
        out.push(c);
    }
    out
}

fn listing(root: &Path, label: &str, shown: &dyn Fn(&str) -> String) -> Outcome {
    let scan = run(root);
    let mut out = String::new();
    let mut over = scan.over.clone();
    over.sort_by_key(|(_, n)| std::cmp::Reverse(*n));
    for (p, n) in &over {
        let _ = writeln!(out, "  {n:5}  {}", shown(p));
    }
    let mut justified = scan.justified.clone();
    justified.sort_by_key(|(_, n, _)| std::cmp::Reverse(*n));
    for (p, n, why) in &justified {
        let _ = writeln!(out, "  {n:5}  {}   JUSTIFIED: {why}", shown(p));
    }
    if over.is_empty() && justified.is_empty() {
        let _ = writeln!(
            out,
            "  every one of {} Python files is at or under {} lines",
            scan.scanned,
            thousands(MAX_LINES)
        );
    }
    let mut dirs: Vec<(String, usize)> = dir_counts(root).into_iter().collect();
    dirs.sort_by_key(|(_, n)| std::cmp::Reverse(*n));
    for (d, n) in dirs.iter().take(5) {
        let _ = writeln!(
            out,
            "  {n:5} files  {d}/   (ceiling {})",
            thousands(MAX_DIR_FILES)
        );
    }
    let _ = label;
    Outcome::out(out)
}

fn signed(n: usize, limit: usize) -> String {
    format!(
        "{:+}",
        i64::try_from(n).unwrap_or(0) - i64::try_from(limit).unwrap_or(0)
    )
}

fn check(root: &Path, label: &str, shown: &dyn Fn(&str) -> String) -> Outcome {
    let scan = run(root);
    if scan.scanned == 0 {
        return Outcome::refuse(format!(
            "check-file-scale: scanned ZERO files under '{label}' - wrong root? failing loudly\n"
        ));
    }
    let mut err = String::new();
    let mut over = scan.over;
    if !over.is_empty() {
        over.sort_by_key(|(_, n)| std::cmp::Reverse(*n));
        let _ = writeln!(
            err,
            "\ncheck-file-scale: {} file(s) past the {}-line bar\n",
            over.len(),
            thousands(MAX_LINES)
        );
        for (p, n) in &over {
            let _ = writeln!(
                err,
                "  {n:5} lines ({})  {}",
                signed(*n, MAX_LINES),
                shown(p)
            );
        }
        err += GUIDANCE;
        err.push('\n');
    }
    let dirs = crowded(root, MAX_DIR_FILES);
    if !dirs.is_empty() {
        let _ = writeln!(
            err,
            "\ncheck-file-scale: {} director(ies) past the {}-file ceiling\n",
            dirs.len(),
            thousands(MAX_DIR_FILES)
        );
        for (d, n) in &dirs {
            let _ = writeln!(err, "  {n:6} files ({})  {d}/", signed(*n, MAX_DIR_FILES));
        }
        err += DIR_GUIDANCE;
        err.push('\n');
    }
    Outcome {
        stdout: String::new(),
        stderr: err,
        code: i32::from(!over.is_empty() || !dirs.is_empty()),
    }
}

/// Prove the checker bites: oversize fires, justified passes, a bare marker fires, a late marker fires, and a crowded directory fires.
fn selftest() -> Outcome {
    let base = super::scratch("file-scale");
    let body = "x = 1\n".repeat(MAX_LINES + 1);
    let put = |name: &str, text: String| {
        let _ = std::fs::write(base.join(name), text);
    };
    put("big.rs", body.clone());
    put("edge.rs", "x = 1\n".repeat(MAX_LINES));
    put(
        "ok.rs",
        format!("# {MARKER} an ordered registry whose row order is the execution contract\n{body}"),
    );
    put("thin.rs", format!("# {MARKER} ordered\n{body}"));
    put(
        "late.rs",
        format!(
            "{}# {MARKER} an ordered registry whose rows are the contract\n{}",
            "x = 1\n".repeat(HEADER_LINES + 1),
            "x = 1\n".repeat(MAX_LINES)
        ),
    );
    let scan = run(&base);
    let names: Vec<&str> = scan.over.iter().map(|(p, _)| p.as_str()).collect();
    let files_right =
        names == ["big.rs", "late.rs", "thin.rs"] && scan.justified.len() == 1 && scan.scanned == 5;
    let dirs = super::scratch("file-scale-dirs");
    for (name, n) in [("full", 3), ("over", 4)] {
        let _ = std::fs::create_dir_all(dirs.join(name));
        for i in 0..n {
            let _ = std::fs::write(dirs.join(name).join(format!("{i}.json")), "{}");
        }
    }
    let dirs_right = crowded(&dirs, 3) == [("over".to_owned(), 4)];
    let _ = std::fs::remove_dir_all(&base);
    let _ = std::fs::remove_dir_all(&dirs);
    Outcome::selftest(
        files_right && dirs_right,
        "check-file-scale: selftest ok (oversize fires, a justified file passes, a bare marker fires, a crowded directory fires)\n",
        "check-file-scale SELFTEST FAILED\n".to_owned(),
    )
}

/// A path as the caller's own root names it.
fn shown_path(label: &str, rel: &str) -> String {
    if label == "." {
        rel.to_owned()
    } else {
        Path::new(label).join(rel).display().to_string()
    }
}

/// `l7r-gate check file-scale [ROOT] | --list [ROOT] | --selftest`.
pub(super) fn cli(args: &[String]) -> Outcome {
    let words: Vec<&str> = args.iter().map(String::as_str).collect();
    let (list, rest): (bool, &[&str]) = if words.first() == Some(&"--list") {
        (true, &words[1..])
    } else {
        (false, &words[..])
    };
    if words.first() == Some(&"--selftest") {
        return selftest();
    }
    let label = rest.first().copied().unwrap_or(".");
    let root = Path::new(label);
    let shown = |rel: &str| shown_path(label, rel);
    if list {
        listing(root, label, &shown)
    } else {
        check(root, label, &shown)
    }
}

#[cfg(test)]
mod tests;
