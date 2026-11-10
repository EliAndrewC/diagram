//! The canonical download list, the GM's marked copy, ingest and sync (feature 313; feature 449 T80, from `downloads.py`).
//!
//! WHY (the GM, 2026-10-02, `specs/313-download-list/request.md`): the list of sources only the GM can fetch *"deserves to be in source control somewhere"*, and the
//! GM's working file *"should be an actual copy and not the canonical source"*. Per entry, *"a space that is already set aside, where I can either check a box
//! (i.e. turning `[ ]` into `[x]`)"*; the GM marks the copy, says "ingest", and the marks are recorded here; the GM says "sync", and the copy is replaced from here.
//!
//! The canonical list is `research/to-download.md`; what was last imported, synced and ingested is `research/to-download.state.json`; the GM's copy is
//! `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`, written by `sync` alone (`download-copy-hooks` refuses a session's own write to it). Ingest ends by running the
//! still-Python `archive_ops.py inbox` by path until its task lands (`ask:449-T80-order` step 3); nothing else here runs Python.

use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::process::Command;

use fancy_regex::Regex;
use serde_json::{json, Value};

use super::reply;
use crate::measure::text_err;
use crate::Reply;

mod add;
mod check;
mod ingest;
pub(crate) mod parse;

pub(crate) const CANON: &str = "research/to-download.md";
const STATE: &str = "research/to-download.state.json";
const HIGH_RISK: &str = "specs/312-uncited-source-catalog/high-risk-sources.md";
const USAGE: &str = "usage: l7r-gate record downloads import [--gm F] [--high-risk F] | ingest [--keep IDS] [--drop IDS] [--mark ID=STATE ...] | sync | add <draft.md> | check [--base REF] | selftest | tag\n";

fn compiled(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// Where this run works: the clone, the GM's copy, the interpreter `ingest`'s archive step runs under and how long `add` waits for the lock.
pub(super) struct Ctx {
    pub(super) root: PathBuf,
    pub(super) copy: PathBuf,
    pub(super) python: String,
    pub(super) timeout: f64,
}

fn read(path: &Path) -> Result<String, String> {
    super::read_text(path).map_err(|e| format!("{}: {e}", path.display()))
}

fn sha(text: &str) -> String {
    l7r_guard::shared::sha256::hex(text.as_bytes())
}

/// `datetime.date.today()`: the local date, as `date(1)` reads the same zone.
fn today() -> String {
    let done = Command::new("date").arg("+%F").output();
    done.map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
        .unwrap_or_default()
}

fn load_state(root: &Path) -> Result<Value, String> {
    let path = root.join(STATE);
    if !path.is_file() {
        return Ok(json!({}));
    }
    serde_json::from_str(&read(&path)?).map_err(text_err)
}

/// Every object's keys in sorted order, as `json.dumps(sort_keys=True)`.
fn sorted(value: &Value) -> Value {
    let Value::Object(map) = value else {
        return value.clone();
    };
    let mut keys: Vec<&String> = map.keys().collect();
    keys.sort();
    Value::Object(
        keys.into_iter()
            .map(|k| (k.clone(), sorted(&map[k])))
            .collect(),
    )
}

fn save_state(root: &Path, state: &Value) -> Result<(), String> {
    let text = crate::logs::py_dumps(&sorted(state), 1, true) + "\n";
    std::fs::write(root.join(STATE), text).map_err(text_err)
}

type Options = (Vec<(String, String)>, Vec<String>);

/// A value from `--name value` or `--name=value`, and the words that were neither; None where a flag is not one of `names` or lacks its value.
fn options(args: &[String], names: &[&str]) -> Option<Options> {
    let (mut found, mut plain) = (Vec::new(), Vec::new());
    let mut rest = args.iter();
    while let Some(word) = rest.next() {
        let Some(flag) = word.strip_prefix("--") else {
            plain.push(word.clone());
            continue;
        };
        let (name, value) = match flag.split_once('=') {
            Some((name, value)) => (name, value.to_owned()),
            None => (flag, rest.next()?.clone()),
        };
        if !names.contains(&name) {
            return None;
        }
        found.push((name.to_owned(), value));
    }
    Some((found, plain))
}

fn option(found: &[(String, String)], name: &str, or: &str) -> String {
    found
        .iter()
        .rev()
        .find(|(n, _)| n == name)
        .map_or_else(|| or.to_owned(), |(_, v)| v.clone())
}

fn usage() -> Reply {
    reply(String::new(), USAGE.to_owned(), 2)
}

fn out(text: String) -> Reply {
    reply(text, String::new(), 0)
}

fn run_tag(ctx: &Ctx) -> Result<Reply, String> {
    let path = ctx.root.join(CANON);
    let tagged = add::tag_all(&read(&path)?, &ctx.root.join("research"));
    std::fs::write(&path, &tagged).map_err(text_err)?;
    let blocks = parse::parse(&tagged);
    let heads: Vec<&str> = parse::entries(&blocks)
        .map(|e| e.heading.as_str())
        .collect();
    let money = heads
        .iter()
        .filter(|h| h.contains("] ") && h.contains("[money]"))
        .count();
    let diagram = heads.iter().filter(|h| h.contains("[diagram]")).count();
    Ok(out(format!(
        "downloads: tagged {} entries - {money} money, {diagram} diagram\n",
        heads.len()
    )))
}

fn run_import(ctx: &Ctx, gm: &Path, high_risk: &str) -> Result<Reply, String> {
    let gm_text = read(gm)?;
    let canon = ctx.root.join(CANON);
    if canon.exists() {
        return Err(format!("{CANON} exists - the import runs once"));
    }
    let imported = add::import_list(&gm_text, &read(&ctx.root.join(high_risk))?);
    std::fs::write(&canon, &imported).map_err(text_err)?;
    save_state(
        &ctx.root,
        &json!({"imported": {"sha256": sha(&gm_text), "date": today()}}),
    )?;
    let count = parse::entries(&parse::parse(&imported)).count();
    Ok(out(format!(
        "downloads: imported {count} entries into {CANON}\n"
    )))
}

fn run_add(ctx: &Ctx, named: &str) -> Result<Reply, String> {
    let mut draft = PathBuf::from(named);
    if !draft.is_absolute() && !draft.exists() {
        draft = ctx.root.join(named);
    }
    let ids = add::add(ctx, &read(&draft)?)?;
    Ok(out(format!(
        "downloads: appended {} to {CANON} - commit it; the GM sees it at the next sync\n",
        ids.join(", ")
    )))
}

fn run_check(ctx: &Ctx, base: &str) -> Reply {
    let found = check::check(&ctx.root, base);
    let lines: Vec<String> = found.iter().map(|p| format!("downloads: {p}\n")).collect();
    let stderr = lines.concat();
    reply(String::new(), stderr, i32::from(!found.is_empty()))
}

fn id_set(text: &str) -> HashSet<String> {
    parse::words(text).into_iter().map(str::to_owned).collect()
}

fn run_ingest(ctx: &Ctx, found: &[(String, String)]) -> Result<Reply, String> {
    let marks = option(found, "mark", "");
    let resolve = parse::words(&marks)
        .into_iter()
        .filter_map(|m| m.split_once('='))
        .map(|(k, v)| (k.to_owned(), v.to_owned()))
        .collect();
    let done = ingest::ingest(
        ctx,
        &id_set(&option(found, "keep", "")),
        &id_set(&option(found, "drop", "")),
        &resolve,
        &today(),
    )?;
    let (mut stdout, code) = ingest::report(&done, &ctx.root)?;
    let inbox = ctx.copy.parent().unwrap_or(Path::new("."));
    let matches = ingest::inbox_matches(&done.saved, inbox);
    let child = Command::new(&ctx.python)
        .arg(ctx.root.join("scripts/record/archive_ops.py"))
        .arg("inbox")
        .args(
            matches
                .iter()
                .map(|(eid, name)| format!("--match={name}={eid}")),
        )
        .current_dir(&ctx.root)
        .output()
        .map_err(text_err)?;
    stdout += &String::from_utf8_lossy(&child.stdout);
    let stderr = String::from_utf8_lossy(&child.stderr).into_owned();
    let last = child.status.code().unwrap_or(1);
    Ok(reply(stdout, stderr, if code != 0 { code } else { last }))
}

fn run(args: &[String], ctx: &Ctx) -> Result<Reply, String> {
    let rest = args.get(1..).unwrap_or(&[]);
    let verb = args.first().map_or("", String::as_str);
    let names: &[&str] = match verb {
        "import" => &["gm", "high-risk"],
        "ingest" => &["keep", "drop", "mark"],
        "check" => &["base"],
        "sync" | "add" | "selftest" | "tag" => &[],
        _ => return Ok(usage()),
    };
    let Some((found, plain)) = options(rest, names) else {
        return Ok(usage());
    };
    match (verb, plain.as_slice()) {
        ("selftest", []) => Ok(check::selftest(&check::selftest_failures())),
        ("tag", []) => run_tag(ctx),
        ("import", []) => {
            let gm = option(&found, "gm", &ctx.copy.display().to_string());
            run_import(ctx, Path::new(&gm), &option(&found, "high-risk", HIGH_RISK))
        }
        ("sync", []) => {
            let commit = ingest::sync(ctx, &today())?;
            Ok(out(format!(
                "downloads: the GM's copy replaced from {CANON} at {}; commit {STATE}\n",
                &commit[..12.min(commit.len())]
            )))
        }
        ("add", [draft]) => run_add(ctx, draft),
        ("check", []) => Ok(run_check(ctx, &option(&found, "base", "origin/main"))),
        ("ingest", []) => run_ingest(ctx, &found),
        _ => Ok(usage()),
    }
}

fn cli_at(args: &[String], ctx: &Ctx) -> Reply {
    run(args, ctx)
        .unwrap_or_else(|why| reply(String::new(), format!("downloads: REFUSED - {why}\n"), 1))
}

/// `l7r-gate record downloads ...`.
pub(crate) fn cli(args: &[String], root: &Path) -> Reply {
    let inbox = std::env::var("L7R_GM_SOURCES")
        .unwrap_or_else(|_| "/host-l7r-repo/academic-sources".to_owned());
    cli_at(
        args,
        &Ctx {
            root: root.to_owned(),
            copy: Path::new(&inbox).join("TO-DOWNLOAD.md"),
            python: "python3".to_owned(),
            timeout: 30.0,
        },
    )
}

#[cfg(test)]
mod tests;
