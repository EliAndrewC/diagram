//! The reviewer's snapshot: a changed map's files from the clone and from main, copied where the gate's cache never evicts them, and
//! each owed unit's dispatch prompt - `l7r-gate reviews snapshot`, ported from `scripts/reviews/review_snapshot.py` by feature 449 T132
//! (`ask:449-phase3-remainder` Q2 task B): whole, no door, `scripts/checks_door.py` deleted with it, its last caller. The owed units are
//! [`super::owed::owed`]'s, in process, where the Python asked the checks door's `review_owed`.
//!
//! WHY THIS EXISTS (feature 231, GM 2026-09-12: *"if we are supposed to snapshot the pool before I make verify, then it should not be on
//! you to remember to do that. That should just happen automatically"*). The gate's roll cache evicts a pool map's standing `.png` and
//! `.html` when it regenerates the map, so a settlement-review dispatched beside a gate loses its artifacts mid-review - on feature 228
//! the reviewer spent minutes waiting for renders that never came back. Taken wherever a review is found owed at gate time: by
//! `make verify`.
//!
//! AND WRITES THE DISPATCH PROMPT, ONE PER UNIT (feature 248, GM 2026-09-14; per unit since feature 294). Feature 247's review was one
//! agent handed four maps, serialized - 11 of the feature's 36 minutes. So each unit's snapshot carries `dispatch.md`, the whole prompt
//! for THAT unit's agent, and the pair guard refuses a dispatch naming more than one.
//!
//! ```text
//! reviews snapshot --root CLONE [--mirror MAIN] [--key ENGINE_KEY] UNIT...
//!   copies each owed unit's map or sheet (.json .svg .png .html .notes.md) from the clone's pool into
//!   <CLONE>/.git/review-snapshot/UNIT/clone/ and main's from the mirror into .../UNIT/main/, clearing the unit's previous snapshot
//!   first; writes .../UNIT/dispatch.md; prints one line per unit naming both directories, every file the clone did not have, and the
//!   prompt file
//! reviews snapshot --root CLONE --stale-renders UNIT...
//!   the generator of each unit's map whose render is missing or older than its map (385 T26), one a line, and stops
//! ```

use std::path::{Path, PathBuf};
use std::time::UNIX_EPOCH;

use l7r_guard::shared::py_text::repr;

use super::owed::{owed, Unit};
use super::reply;
use crate::Reply;

const TREES: [&str; 2] = ["pool", "legacy-hand-authored-pool"];
/// What a reviewer reads of a map or sheet, in the order it is listed.
const SUFFIXES: [&str; 5] = [".json", ".svg", ".png", ".html", ".notes.md"];
const NO_CLONE: &str = "not in the clone's pool";
const NO_MAIN: &str = "unavailable (no mirror, or main has no such map)";

/// The folder of map or sheet `name` under either pool tree of `tree_root`: the first of `sorted(glob("*/<name>"))` that is a
/// directory (`*` matching a dot folder too, as `pathlib` does).
fn map_dir(tree_root: &Path, name: &str) -> Option<PathBuf> {
    for tree in TREES {
        let mut kinds: Vec<String> = std::fs::read_dir(tree_root.join(tree))
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.file_name().to_string_lossy().into_owned())
            .collect();
        kinds.sort();
        if let Some(d) = kinds
            .iter()
            .map(|k| tree_root.join(tree).join(k).join(name))
            .find(|d| d.is_dir())
        {
            return Some(d);
        }
    }
    None
}

/// What each check is asked, per its contract (`.claude/agents/<check>.md`); `None` for a check with no prompt, where the Python's
/// `ASK[check]` raised `KeyError`.
fn ask_of(unit: &Unit) -> Option<String> {
    let on = if unit.on.is_empty() {
        "no map draws it"
    } else {
        &unit.on
    };
    let (occasion, subject) = (&unit.occasion, repr(&unit.subject));
    Some(match unit.check.as_str() {
        "settlement-review" => format!("the WHOLE-MAP review of {on}: {occasion}. Run your contract's whole-map sweeps on it."),
        "building-review" => format!(
            "the review of the sheet {on}: {occasion}. Run the sections of your contract this occasion owes. A finding on a part of the \
             sheet this occasion did not change is a row to file, not this unit's verdict: give it severity `outside` and judge the verdict \
             on the change alone." // GUARD_EDIT_OK: feature 374 batch 6 - the round arbiter's tooling fix (ask:b6-ochiba-r3)
        ),
        "glyph-check" => format!("the glyph check of the element {subject}, on {on}: {occasion}. Judge that element where it stands on this map - nothing else on the map is under review."),
        "size-audit" => format!("the size audit of {subject} on {on}: {occasion}. Anchor that kind's size; nothing else is under review."),
        "fix-check" => format!("the fix check on {on}: {occasion}. Answer the GM's complaint at fit zoom first, then whether the fix fired and whether its record can bear it."),
        _ => return None,
    })
}

/// One unit's snapshot: the two sides' directories (`None` with no mirror, or no such map), the suffixes each lacked, the prompt file.
struct Rec {
    slug: String,
    on: String,
    clone: Option<PathBuf>,
    main: Option<PathBuf>,
    missing: Vec<&'static str>,
    main_missing: Vec<&'static str>,
    dispatch: Option<PathBuf>,
}

fn missing_note(rec: &Rec) -> String {
    if rec.missing.is_empty() || rec.clone.is_none() {
        String::new()
    } else {
        format!(
            "(missing in the clone: {} - regenerate it with make map)",
            rec.missing.join(" ")
        )
    }
}

fn shown(p: Option<&PathBuf>, none: &str) -> String {
    p.map_or_else(|| none.to_owned(), |d| d.display().to_string())
}

/// The one-unit prompt a session hands the Agent tool (feature 248 FR-002, per unit since feature 294).
fn dispatch_text(rec: &Rec, ask: &str, check: &str, root: &Path, key: &str) -> String {
    let note = missing_note(rec);
    let missing = if note.is_empty() {
        note
    } else {
        format!("  {note}")
    };
    format!(
        "UNIT: {slug}\n{check} - {ask}\n\nThis prompt was written by the tooling (feature 294): one agent per owed unit, and the pair guard refuses a dispatch that\n\
         names more than one. Do not review anything else - its own agent has it - and wait for nothing but your own work.\n\n\
         Clone: {clone} (the directory holding `.git/review-snapshot/`; run the `make` targets from its\n\
         root). Engine key: {key}. The gate went green on this content before this dispatch.\n\n\
         Snapshot - read THESE:\n  after (the clone): {after}{missing}\n  before (main):     {before}\n\n\
         Follow your contract end to end, then `make review-verdict UNIT={slug} VERDICT=<PASS|NEEDS-WORK|NOT-REVIEWABLE> [FINDINGS=<json file>]`\n\
         as your last act, and quote the line it prints.\n",
        slug = rec.slug,
        clone = root.display(),
        key = if key.is_empty() { "not computed" } else { key },
        after = shown(rec.clone.as_ref(), NO_CLONE),
        before = shown(rec.main.as_ref(), NO_MAIN),
    )
}

/// One line per unit: where each side is, what the clone did not have, and the prompt file.
fn describe(rec: &Rec) -> String {
    let note = missing_note(rec);
    let missing = if note.is_empty() {
        note
    } else {
        format!(" {note}")
    };
    let prompt = rec
        .dispatch
        .as_ref()
        .map_or_else(String::new, |p| format!(" | prompt {}", p.display()));
    format!(
        "snapshot {} (on {}): clone {}{missing} | main {}{prompt}",
        rec.slug,
        if rec.on.is_empty() { "?" } else { &rec.on },
        shown(rec.clone.as_ref(), NO_CLONE),
        shown(rec.main.as_ref(), NO_MAIN),
    )
}

/// `st_mtime` as Python's float reads it (`sec + nsec * 1e-9`), so two times compare as the Python compared them.
fn mtime(p: &Path) -> Result<f64, String> {
    let t = std::fs::metadata(p)
        .and_then(|m| m.modified())
        .map_err(|e| format!("FileNotFoundError: {e}: {}", p.display()))?;
    #[expect(clippy::cast_precision_loss, reason = "Python's own float")]
    let at = match t.duration_since(UNIX_EPOCH) {
        Ok(d) => d.as_secs() as f64 + f64::from(d.subsec_nanos()) * 1e-9,
        Err(e) => -(e.duration().as_secs() as f64 + f64::from(e.duration().subsec_nanos()) * 1e-9),
    };
    Ok(at)
}

fn rel(p: &Path, root: &Path) -> String {
    p.strip_prefix(root)
        .unwrap_or(p)
        .to_string_lossy()
        .into_owned()
}

/// The generator (`pool/.../<map>.gen.py`, relative to `root`) of each owed unit's map whose `.png` or `.html` is missing or older than
/// its `.gen.py` or `.json` - rendered by `make verify` before the snapshot (feature 385 T26, plan D48; the round arbiter's fix on
/// hour:385-approach-checklist@12). An entry with no generator whose `.png` is missing is listed as `sheet:<its .svg>`, which `make verify`
/// refuses, naming `make sheet-render` (spec-fidelity, T26 round 1: "every unit").
fn stale_renders(root: &Path, units: &[&Unit]) -> Result<Vec<String>, String> {
    let mut out: Vec<String> = Vec::new();
    for unit in units {
        let Some(src) = (!unit.on.is_empty())
            .then(|| map_dir(root, &unit.on))
            .flatten()
        else {
            continue;
        };
        let file = |suffix: &str| src.join(format!("{}{suffix}", unit.on));
        let gen = file(".gen.py");
        if !gen.is_file() {
            let svg = file(".svg");
            if svg.is_file() && !file(".png").is_file() {
                out.push(format!("sheet:{}", rel(&svg, root)));
            }
            continue;
        }
        let mut made = mtime(&gen)?;
        if file(".json").is_file() {
            made = made.max(mtime(&file(".json"))?);
        }
        let mut stale = false;
        for r in [file(".png"), file(".html")] {
            if !r.is_file() || mtime(&r)? < made {
                stale = true;
                break;
            }
        }
        let name = rel(&gen, root);
        if stale && !out.contains(&name) {
            out.push(name);
        }
    }
    Ok(out)
}

/// `shutil.copy2`: the bytes, the mode, and the access and modification times.
fn copy2(from: &Path, to: &Path) -> Result<(), String> {
    let oops = |e: std::io::Error| format!("OSError: {e}: {}", from.display());
    std::fs::copy(from, to).map_err(oops)?;
    let meta = std::fs::metadata(from).map_err(oops)?;
    let times = std::fs::FileTimes::new()
        .set_accessed(meta.accessed().map_err(oops)?)
        .set_modified(meta.modified().map_err(oops)?);
    std::fs::File::open(to)
        .and_then(|f| f.set_times(times))
        .map_err(oops)
}

/// An I/O error as Python's `OSError` names it, with its path.
fn os_error(p: &Path) -> impl Fn(std::io::Error) -> String + '_ {
    move |e| format!("OSError: {e}: {}", p.display())
}

/// Copy each unit's map or sheet from `root` (the clone) and `mirror` (main) into the clone's `.git/review-snapshot/<slug>/{clone,main}/`
/// and write its `dispatch.md`; one line a unit, as [`describe`] writes it. A unit whose check has no prompt raises after its copies, as
/// the Python's `KeyError` did.
fn snapshot(
    root: &Path,
    mirror: Option<&Path>,
    units: &[&Unit],
    key: &str,
) -> Result<Vec<String>, String> {
    let mut out = Vec::new();
    for unit in units {
        let slug = unit.slug();
        let dest = root.join(".git").join("review-snapshot").join(&slug);
        if dest.exists() {
            std::fs::remove_dir_all(&dest).map_err(os_error(&dest))?;
        }
        let mut rec = Rec {
            slug,
            on: unit.on.clone(),
            clone: None,
            main: None,
            missing: Vec::new(),
            main_missing: Vec::new(),
            dispatch: None,
        };
        for (side, tree) in [("clone", Some(root)), ("main", mirror)] {
            let src = tree
                .filter(|_| !unit.on.is_empty())
                .and_then(|t| map_dir(t, &unit.on));
            let mut lack: Vec<&'static str> = Vec::new();
            let target = dest.join(side);
            if let Some(src) = &src {
                std::fs::create_dir_all(&target).map_err(os_error(&target))?;
                let sheet = src.join(format!("{}.svg", unit.on)).is_file();
                for suffix in SUFFIXES {
                    let f = src.join(format!("{}{suffix}", unit.on));
                    if f.is_file() {
                        copy2(&f, &target.join(format!("{}{suffix}", unit.on)))?;
                    } else if !(suffix == ".json" && sheet) {
                        // a Mode A sheet has no manifest; a map always has one
                        lack.push(suffix);
                    }
                }
            } else {
                lack = SUFFIXES.to_vec();
            }
            let found = src.map(|_| target);
            if side == "clone" {
                (rec.clone, rec.missing) = (found, lack);
            } else {
                (rec.main, rec.main_missing) = (found, lack);
            }
        }
        std::fs::create_dir_all(&dest).map_err(os_error(&dest))?;
        let Some(ask) = ask_of(unit) else {
            return Err(format!("KeyError: {}", repr(&unit.check)));
        };
        let prompt = dest.join("dispatch.md");
        std::fs::write(&prompt, dispatch_text(&rec, &ask, &unit.check, root, key))
            .map_err(os_error(&prompt))?;
        rec.dispatch = Some(prompt);
        out.push(describe(&rec));
    }
    Ok(out)
}

/// What the command line asked (`argparse` over `--root`, `--mirror`, `--key`, `--stale-renders` and the units).
#[derive(Default)]
struct Asked {
    root: Option<String>,
    mirror: Option<String>,
    key: String,
    stale: bool,
    units: Vec<String>,
}

const OPTIONS: [&str; 5] = ["--root", "--mirror", "--key", "--stale-renders", "--help"];

/// `argparse`'s negative number (`^-\d+$|^-\d*\.\d+$`), its dash dropped, which it reads as a value, never a flag, when no option looks like one.
fn negative_number(body: &str) -> bool {
    let digits = |t: &str| t.chars().all(|c| c.is_ascii_digit());
    match body.split_once('.') {
        None => !body.is_empty() && digits(body),
        Some((whole, frac)) => digits(whole) && !frac.is_empty() && digits(frac),
    }
}

/// A word `argparse` reads as an option: a dash and more, no negative number, and no space unless it names an option.
fn flag_like(word: &str) -> bool {
    word.len() > 1
        && word.starts_with('-')
        && !negative_number(&word[1..])
        && (!word.contains(' ') || !matching(word).is_empty())
}

/// The options a word names: its whole name, or (a `--` word) a prefix of it, the part before an `=` read as the name.
fn matching(word: &str) -> Vec<&'static str> {
    let name = word.split_once('=').map_or(word, |(n, _)| n);
    OPTIONS
        .into_iter()
        .filter(|o| *o == name || (name.starts_with("--") && name.len() > 2 && o.starts_with(name)))
        .collect()
}

/// The command line as `argparse` reads it: options by their whole name or a unique prefix, `=` or the next word for a value, the
/// units one run of positional words; a usage error is one line naming the complaint (`ask:449-usage-text`).
fn parse(args: &[String]) -> Result<Asked, String> {
    let mut a = Asked::default();
    let (mut i, mut ended, mut run) = (0, false, 0u8); // run: 0 none yet, 1 in the units, 2 past them
    while i < args.len() {
        let w = &args[i];
        i += 1;
        if !ended && w == "--" {
            ended = true;
            continue;
        }
        if ended || !flag_like(w) {
            match run {
                0 | 1 => {
                    run = 1;
                    a.units.push(w.clone());
                }
                _ => return Err(format!("unrecognized arguments: {w}")),
            }
            continue;
        }
        if run == 1 {
            run = 2;
        }
        let inline = w.split_once('=').map(|(_, v)| v);
        let hits = matching(w);
        let opt = match hits.as_slice() {
            _ if w == "-h" => "--help",
            // no two options share a prefix, so a word names one option or none
            [one] => *one,
            _ => return Err(format!("unrecognized arguments: {w}")),
        };
        if matches!(opt, "--stale-renders" | "--help") {
            if inline.is_some() {
                return Err(format!("argument {opt}: ignored explicit argument"));
            }
            if opt == "--help" {
                return Err("--help".to_owned());
            }
            a.stale = true;
            continue;
        }
        let value = if let Some(v) = inline {
            v.to_owned()
        } else {
            match args.get(i) {
                Some(v) if !flag_like(v) && v != "--" => {
                    i += 1;
                    v.clone()
                }
                _ => return Err(format!("argument {opt}: expected one argument")),
            }
        };
        match opt {
            "--root" => a.root = Some(value),
            "--mirror" => a.mirror = Some(value),
            _ => a.key = value,
        }
    }
    if a.root.is_none() || a.units.is_empty() {
        let mut lacking = Vec::new();
        if a.root.is_none() {
            lacking.push("--root");
        }
        if a.units.is_empty() {
            lacking.push("units");
        }
        return Err(format!(
            "the following arguments are required: {}",
            lacking.join(", ")
        ));
    }
    Ok(a)
}

/// The usage `--help` prints (the Python printed argparse's help; `--help` is not a malformed invocation, and no caller reads it).
const HELP: &str = "usage: l7r-gate reviews snapshot --root CLONE [--mirror MAIN] [--key ENGINE_KEY] [--stale-renders] UNIT...\n";

/// `l7r-gate reviews snapshot ...`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let a = match parse(args) {
        Ok(a) => a,
        Err(why) if why == "--help" => return reply(HELP.to_owned(), String::new(), 0),
        Err(why) => {
            return reply(
                String::new(),
                format!("l7r-gate reviews snapshot: {why}\n"),
                2,
            )
        }
    };
    let root = crate::record::bundle::resolve(a.root.as_deref().unwrap_or_default());
    // main's tree: the parent of the clone's `.clones/`, when it has one and none was named
    let mirror = match a.mirror.as_deref() {
        Some(m) if !m.is_empty() => Some(PathBuf::from(m)),
        _ => {
            let parts: Vec<_> = root.components().collect();
            parts
                .iter()
                .position(|c| c.as_os_str() == ".clones")
                .map(|at| parts[..at].iter().collect::<PathBuf>())
        }
    };
    // every owed unit: the caller named the due ones (375 amendment 9)
    let (_, units, _) = owed(&root, true);
    let unknown: Vec<&str> = a
        .units
        .iter()
        .filter(|s| !units.iter().any(|u| u.slug() == **s))
        .map(String::as_str)
        .collect();
    if !unknown.is_empty() {
        return reply(
            String::new(),
            format!(
                "_review_snapshot: not owed by this delta: {}\n",
                unknown.join(" ")
            ),
            2,
        );
    }
    // `{u.slug: u for u in units}`: of two units with one slug, the later
    let asked: Vec<&Unit> = a
        .units
        .iter()
        .filter_map(|s| units.iter().rev().find(|u| u.slug() == *s))
        .collect();
    let said = if a.stale {
        stale_renders(&root, &asked).map(|names| names.join("\n") + "\n")
    } else {
        snapshot(&root, mirror.as_deref(), &asked, &a.key)
            .map(|lines| lines.iter().flat_map(|l| [l.as_str(), "\n"]).collect())
    };
    match said {
        Ok(out) => reply(out, String::new(), 0),
        Err(why) => reply(
            String::new(),
            format!("Traceback (most recent call last):\n  l7r-gate reviews snapshot\n{why}\n"),
            1,
        ),
    }
}

#[cfg(test)]
mod tests;
