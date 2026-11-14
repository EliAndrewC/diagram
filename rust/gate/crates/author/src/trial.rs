//! A trial's two tools (ported whole from `scripts/trial-start.py` and `trial-review.py` by feature 449 T135, `ask:449-phase3-remainder`).
//!
//! `l7r-gate trial-start <slug>` - `make trial SLUG=<slug>` (feature 438): a feature number claimed (in process, [`crate::claim`], the
//! same lock and numbering as `make claim`, where the Python ran `claim-feature.py`) and its trial brief written. A trial is a question a
//! measurement answers, asked before any decision to build (docs/spec-kit-and-reviews.md, "The trial form"): its `spec.md` is the brief
//! `.specify/templates/trial-template.md` gives (`**Form**: trial`), measured first, reviewed once when the evidence is fixed and the
//! status turns Done. WHY (feature 437): the array geometry trial's spec took three review rounds and a round-arbiter ruling - about 12
//! minutes of reviewer time - because it was reviewed while its evidence changed beside it.
//!
//! `l7r-gate trial-review <n>` - `make trial-review F=<n>` (feature 442): the bundle and the dispatch of a trial's ONE review. Its
//! research files record each measurement's output beside its figure, so the review CHECKS each figure against the output recorded
//! beside it and re-runs a command only where an output is missing or disagrees - trial 441's review re-ran every profile to re-derive
//! figures its research already held (about 3 of its 5.6 minutes). The bundle (`/tmp/l7r-check/trial-review-<NNN>/`) holds the brief,
//! `request.md`, every `research/*.md` and `*.json` and a `MANIFEST.md`; the dispatch is printed for spec-fidelity, MODE 2.
//!
//! Both read the tree the wrapper names (`L7R_GATE_TREE`), where the Python read its own file's tree.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_gate_core::Reply;
use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::speckit::splitlines;

use crate::{raised, read_strict, reply};

const REQUEST: &str =
    "# Feature {n} - the GM's request, verbatim\n\n> [the GM's words, verbatim]\n";

/// The trial brief and the request stub written into a claimed feature `directory`, its approval line carrying `approved` (the GM's
/// words, verbatim) when given, so the approval guard passes the brief's first commit (feature 440 T05).
fn brief(directory: &Path, today: &str, template: &Path, approved: &str) -> Result<(), String> {
    let name = directory
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let head = name.split('-').next().unwrap_or("");
    let n: i128 = head
        .parse()
        .map_err(|_| format!("ValueError: invalid literal for int() with base 10: '{head}'"))?;
    let mut text = read_strict(template)?
        .replace("[DATE]", today)
        .replace("[N]", &n.to_string());
    if !strip(approved).is_empty() {
        let words = strip(approved).replace('"', "'");
        text = text.replace("\"[his words, verbatim]\"", &format!("\"{words}\""));
    }
    let write =
        |p: PathBuf, t: &str| std::fs::write(&p, t).map_err(|e| format!("{}: {e}", p.display()));
    write(directory.join("spec.md"), &text)?;
    if !directory.join("request.md").exists() {
        write(
            directory.join("request.md"),
            &REQUEST.replace("{n}", &n.to_string()),
        )?;
    }
    Ok(())
}

/// `l7r-gate trial-start <slug>` over `tree`, `approved` the GM's words (`TRIAL_APPROVED`).
#[must_use]
pub fn start_cli(args: &[String], tree: &Path, approved: &str) -> Reply {
    if args.len() != 1 || strip(&args[0]).is_empty() {
        return reply(
            String::new(),
            "make trial: SLUG=<kebab-slug> is required - e.g. make trial SLUG=fewer-seat-candidates\n".to_owned(),
            2,
        );
    }
    let claimed = crate::claim::cli(&["--".to_owned(), args[0].clone()], tree);
    if claimed.code != 0 {
        return reply(String::new(), claimed.stderr, claimed.code);
    }
    let name = claimed
        .stdout
        .lines()
        .last()
        .map(str::to_owned)
        .unwrap_or_default();
    let template = tree.join(".specify/templates/trial-template.md");
    if let Err(why) = brief(
        &tree.join("specs").join(&name),
        &l7r_gate_core::record::bundle::today(),
        &template,
        approved,
    ) {
        return raised("trial-start", String::new(), &claimed.stderr, &why);
    }
    reply(
        format!("{name}\n"),
        format!("{}trial: specs/{name}/spec.md is the brief (**Form**: trial) - fill its question, rule and request.md; measure first; one review when Done\n", claimed.stderr),
        0,
    )
}

const INSTRUCTION: &str = "Each figure in the brief and its research is recorded with the command that measured it and its output (a fenced block beside it): CHECK each figure against the output recorded beside it, and re-run a command only where no output is recorded for it or the output disagrees with its figure.";

/// A TRIAL THAT LANDED NO ENGINE CODE says so on its Status line (439, 441): only its review is told to check rather than re-run - a
/// trial whose spike lands takes the ordinary full review (feature 442, the spec review's round 1).
const STOPPED: [&str; 2] = ["set down", "stopped at the measurement"];

/// Does the brief's Status open Done and say the trial was set down or stopped at the measurement?
fn measurement_only(spec_text: &str) -> bool {
    splitlines(spec_text)
        .into_iter()
        .find(|line| line.starts_with("**Status**:"))
        .is_some_and(|line| {
            let low = line.to_lowercase();
            strip(low.strip_prefix("**status**:").unwrap_or(&low)).starts_with("done")
                && STOPPED.iter().any(|s| low.contains(s))
        })
}

/// The entries of `dir` that `Path.glob("*")` yields (hidden ones among them, as `pathlib`'s glob takes them), in path order.
fn listed(dir: &Path) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .collect();
    out.sort();
    out
}

/// `shutil.copy`: the bytes and the mode.
fn copy(from: &Path, to: &Path) -> Result<(), String> {
    std::fs::copy(from, to)
        .map(|_| ())
        .map_err(|e| format!("{}: {e}", from.display()))
}

/// The trial's brief, request and research copied into `out` and its MANIFEST written; the MANIFEST's path.
fn bundle(feature: &Path, out: &Path, stopped: bool) -> Result<PathBuf, String> {
    let fail = |e: std::io::Error| format!("{}: {e}", out.display());
    if out.exists() || out.is_symlink() {
        if out.is_dir() && !out.is_symlink() {
            std::fs::remove_dir_all(out).map_err(fail)?;
        } else {
            return Err(format!("NotADirectoryError: {}", out.display()));
        }
    }
    std::fs::create_dir_all(out.join("research")).map_err(fail)?;
    let names = ["spec.md", "request.md"];
    for name in names {
        if feature.join(name).is_file() {
            copy(&feature.join(name), &out.join(name))?;
        }
    }
    // A RECORDED OUTPUT RIDES WITH ITS NOTES: trial 447's tables came from JSON its scripts wrote beside them, and a bundle of the
    // Markdown alone left its reviewer re-running an hour's measurement to check them
    let research: Vec<PathBuf> = if feature.join("research").is_dir() {
        listed(&feature.join("research"))
            .into_iter()
            .filter(|f| f.extension().is_some_and(|x| x == "md" || x == "json"))
            .collect()
    } else {
        Vec::new()
    };
    let mut files: Vec<String> = names
        .iter()
        .filter(|n| out.join(n).is_file())
        .map(|n| (*n).to_owned())
        .collect();
    for f in &research {
        let name = f
            .file_name()
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default();
        copy(f, &out.join("research").join(&name))?;
        files.push(format!("research/{name}"));
    }
    let feature_name = feature
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let manifest = format!(
        "# The one review of trial {feature_name}\n\nThe brief (`spec.md`, **Form**: trial) with its evidence fixed, and the GM's words (`request.md`).\n\n{}\n\nJudge whether the brief and its verdict do what the GM asked, and whether the verdict is the branch of the brief's own rule its measurement took.\n\n## Files\n\n{}",
        if stopped { INSTRUCTION } else { "Its spike lands engine code: review it in full, re-running what you need." },
        files.iter().fold(String::new(), |mut all, n| {
            let _ = writeln!(all, "- `{n}`");
            all
        })
    );
    std::fs::write(out.join("MANIFEST.md"), manifest).map_err(fail)?;
    Ok(out.join("MANIFEST.md"))
}

/// `l7r-gate trial-review <n>` over `tree`, its bundle under `check_dir` (`/tmp/l7r-check`, the Python's `CHECK_DIR`).
#[must_use]
pub fn review_cli(args: &[String], tree: &Path, check_dir: &Path) -> Reply {
    let refuse = |why: String| reply(String::new(), why, 2);
    // `str.isdigit` with a digit outside ASCII (a superscript `²`): Python's test passed it and `int()` then raised, exit 1. Read as ASCII
    // digits otherwise; other scripts' decimal digits, which `int()` would read, no feature number has
    if let Some(odd) = args
        .first()
        .map(|a| strip(a))
        .filter(|a| args.len() == 1 && a.chars().all(char::is_numeric) && !a.is_ascii())
    {
        return raised(
            "trial-review",
            String::new(),
            "",
            &format!(
                "ValueError: invalid literal for int() with base 10: {}",
                l7r_guard::shared::py_text::repr(odd)
            ),
        );
    }
    let number = args
        .first()
        .map(|a| strip(a))
        .filter(|a| args.len() == 1 && !a.is_empty() && a.bytes().all(|b| b.is_ascii_digit()));
    let Some(number) = number else {
        return refuse(
            "make trial-review: F=<feature number> is required - e.g. make trial-review F=441\n"
                .to_owned(),
        );
    };
    // `f"{int(n):03d}"`: the digits with their leading zeros dropped, padded to three
    let n = format!("{:0>3}", number.trim_start_matches('0'));
    let mut found: Vec<PathBuf> = listed(&tree.join("specs"))
        .into_iter()
        .filter(|p| {
            p.file_name()
                .is_some_and(|f| f.to_string_lossy().starts_with(&format!("{n}-")))
        })
        .collect();
    found.truncate(1);
    let spec = found.first().map(|d| d.join("spec.md"));
    let text = match spec.as_deref().filter(|s| s.is_file()).map(read_strict) {
        Some(Ok(t)) => Some(t),
        Some(Err(why)) => return raised("trial-review", String::new(), "", &why),
        None => None,
    };
    let (Some(feature), Some(text)) = (
        found.first(),
        text.filter(|t| t.contains("**Form**: trial")),
    ) else {
        return refuse(format!("make trial-review: specs/{n}-* is no trial brief (**Form**: trial) - an ordinary spec takes its review from spec-fidelity's MODE 2 as before\n"));
    };
    let stopped = measurement_only(&text);
    let manifest = match bundle(
        feature,
        &check_dir.join(format!("trial-review-{n}")),
        stopped,
    ) {
        Ok(m) => m,
        Err(why) => return raised("trial-review", String::new(), "", &why),
    };
    let name = feature
        .file_name()
        .map(|f| f.to_string_lossy().into_owned())
        .unwrap_or_default();
    let tail = if stopped {
        format!(" {INSTRUCTION}")
    } else {
        " Its spike lands engine code: review it in full.".to_owned()
    };
    reply(
        format!("MODE 2: SPECIFICATION REVIEW of trial {name} - its one review: read {} and the files beside it.{tail}\n", manifest.display()),
        String::new(),
        0,
    )
}

#[cfg(test)]
mod tests;
