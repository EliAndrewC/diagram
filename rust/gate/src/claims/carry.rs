//! A finding a page edit surfaced on code left unchanged is CARRIED, not refused, and the push's claims gate (`scripts/record/
//! claims_carry.py`, ported by feature 449 T82; feature 385 amendment 3, FR-013, plan D26-D29, and feature 445's switch): the record
//! `specs/<feature>/claims-carried.jsonl`, the known drifts, and what the gate refuses and warns.

#![expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "Python's `str.endswith`, which this port keeps, is case-sensitive"
)]

use std::collections::{BTreeSet, HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use super::index::{
    field, is, live_rows, load_map, owed, relabel_answered, Cur, Index, INDEX, STORE,
};
use super::report::{base_cores, base_tree, classify, load_deferred, open_findings, Base};
use super::scope::Reader;
use crate::record::repo::{fail, git, read_text, Fail};
use crate::record::units::re;

pub(crate) const RECORD: &str = "claims-carried.jsonl";
/// The standing feature that fixes claims findings (the GM, 2026-10-26): a landing with no engine code files its carries here.
pub(crate) const CLAIMS_FEATURE: &str = "405";
const LANDS_OPEN: &str = " [lands-open]";
/// The kind of a gm-review.jsonl row that records an admitted known drift (feature 430 D6).
pub(crate) const KNOWN_KIND: &str = "known-drift";
/// The words an accept records when the round arbiter accepts a known drift.
pub(crate) const ACCEPTED: &str = "a known drift accepted by the round arbiter";
const BY_ARBITER: &str = "accepted by the round arbiter";

static BOX: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \[( |x)\] (T\d+)\b(.*)$"));
static GM_BOX: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \[[ x]\] GM review\b"));
static TASK_NAMED: LazyLock<Regex> = LazyLock::new(|| re(r"feature (\d{3}) (T\d+)"));
static KNOWN_LINE: LazyLock<Regex> =
    LazyLock::new(|| re(r"\Aknown: (.*) - a known drift \((\d{3}) (T\d+[a-z]?)\) to record"));

fn canon(p: &Path) -> PathBuf {
    let real = std::fs::canonicalize(p);
    real.unwrap_or_default()
}

fn git_lines(root: &Path, args: &[&str]) -> Vec<String> {
    git(root, args)
        .lines()
        .map(|l| l7r_guard::shared::py_text::strip(l).to_owned())
        .filter(|l| !l.is_empty())
        .collect()
}

/// Does this tree's delta change engine code, as the gate's one list and the content id decide it?
pub(crate) fn touches_engine(root: &Path) -> Result<bool, Fail> {
    let base = git_lines(root, &["merge-base", "origin/main", "HEAD"])
        .into_iter()
        .next()
        .unwrap_or_else(|| "HEAD".to_owned());
    let mut paths = git_lines(root, &["diff", "--name-only", &base]);
    paths.extend(git_lines(
        root,
        &["ls-files", "--others", "--exclude-standard"],
    ));
    let scratch = super::temp_dir("ids");
    let mut pairs: Vec<(PathBuf, Vec<u8>)> = Vec::new();
    for f in paths.iter().filter(|p| crate::delta::is_engine(p)) {
        if !f.ends_with(".py") {
            return Ok(true);
        }
        let before = std::process::Command::new("git")
            .arg("-C")
            .arg(root)
            .args(["show", &format!("{base}:{f}")])
            .output()
            .map_err(fail)?;
        let now = root.join(f);
        if !before.status.success() || !now.is_file() {
            return Ok(true);
        }
        pairs.push((PathBuf::from(f), before.stdout));
        pairs.push((PathBuf::from(f), std::fs::read(&now).map_err(fail)?));
    }
    if pairs.is_empty() {
        return Ok(false);
    }
    let _ = std::fs::create_dir_all(&scratch);
    let files: Vec<(PathBuf, Vec<u8>)> = pairs
        .into_iter()
        .enumerate()
        .map(|(i, (_, data))| {
            let p = scratch.join(format!("{i}.py"));
            let _ = std::fs::write(&p, &data);
            (p, data)
        })
        .collect();
    let script = crate::codeid::script(root);
    let ids = crate::codeid::content_ids(
        &files,
        &mut crate::codeid::Cache::at(root),
        "python3",
        &script,
    );
    let _ = std::fs::remove_dir_all(&scratch);
    let ids = ids?;
    Ok(ids.chunks(2).any(|p| p[0] != p[1]))
}

fn read_or_empty(path: &Path) -> Result<String, Fail> {
    if path.is_file() {
        read_text(path)
    } else {
        Ok(String::new())
    }
}

/// The open task ids of a feature's tasks.md.
pub(crate) fn open_ids(d: &Path) -> Result<HashSet<String>, Fail> {
    let text = read_or_empty(&d.join("tasks.md"))?;
    Ok(BOX
        .captures_iter(&text)
        .flatten()
        .filter(|c| &c[1] == " ")
        .map(|c| c[2].to_owned())
        .collect())
}

/// The rows of a feature's carry record.
pub(crate) fn rows(d: &Path) -> Result<Vec<Value>, Fail> {
    read_or_empty(&d.join(RECORD))?
        .lines()
        .filter(|l| !l7r_guard::shared::py_text::strip(l).is_empty())
        .map(|l| serde_json::from_str(l).map_err(|e| format!("json.decoder.JSONDecodeError: {e}")))
        .collect()
}

/// The feature carried findings are filed into: the claims feature for a delta with no engine code, while it has an open task; the active one otherwise.
pub(crate) fn target(root: &Path) -> Result<Option<PathBuf>, Fail> {
    if !touches_engine(root)? {
        if let Some(claims) = crate::plan::resolve_feature(CLAIMS_FEATURE, root) {
            if !open_ids(&claims)?.is_empty() {
                return Ok(Some(claims));
            }
        }
    }
    Ok(crate::plan::active_feature(root))
}

/// key -> its open task, for every key the record of the feature carries file into files.
pub(crate) fn filed(target: Option<&Path>) -> Result<HashMap<String, String>, Fail> {
    let Some(d) = target else {
        return Ok(HashMap::new());
    };
    let live = open_ids(d)?;
    let mut out = HashMap::new();
    for r in rows(d)? {
        let task = r.get("task").and_then(Value::as_str).unwrap_or_default();
        if !live.contains(task) {
            continue;
        }
        for k in r
            .get("keys")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
        {
            out.insert(k.as_str().unwrap_or_default().to_owned(), task.to_owned());
        }
    }
    Ok(out)
}

fn ruled(d: &Path, ruling: &str) -> Result<bool, Fail> {
    Ok(read_or_empty(&d.join("arbiter.jsonl"))?
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .any(|r| is(&r, "trigger", ruling)))
}

fn file_into(text: &str, task: &str, keys: &[String], by: &str) -> Result<String, String> {
    for c in BOX.captures_iter(text).flatten() {
        if &c[2] != task {
            continue;
        }
        if &c[1] != " " {
            return Err(format!(
                "{task} is ticked; file into an open task, or leave T= off for a new one"
            ));
        }
        let whole = c.get(0).unwrap_or_else(|| unreachable!());
        let line = whole.as_str();
        let (body, tail) = line
            .strip_suffix(LANDS_OPEN)
            .map_or((line, ""), |b| (b, LANDS_OPEN));
        return Ok(format!(
            "{}{body}; carried by {by}: {}{tail}{}",
            &text[..whole.start()],
            keys.join(", "),
            &text[whole.end()..]
        ));
    }
    Err(format!("no task {task} in tasks.md"))
}

fn new_box(text: &str, keys: &[String], ruling: &str) -> (String, String) {
    let top = BOX
        .captures_iter(text)
        .flatten()
        .filter_map(|c| c[2][1..].parse::<u64>().ok())
        .max()
        .unwrap_or(0);
    let task = format!("T{:02}", top + 1);
    let by = if ruling.is_empty() {
        "the claims gate (385 FR-013): findings on code the change left unchanged".to_owned()
    } else {
        format!("the round arbiter's ruling {ruling}: findings it carried")
    };
    let line = format!("- [ ] {task} Carried by {by} - fix the code or the claim and re-check each: {}{LANDS_OPEN}\n      research: rendering\n", keys.join(", "));
    match GM_BOX.find(text).ok().flatten() {
        Some(m) => (
            format!("{}{line}{}", &text[..m.start()], &text[m.start()..]),
            task,
        ),
        None => (format!("{}\n{line}", text.trim_end_matches('\n')), task),
    }
}

/// The claims switch: `report` (absent, or no `claims` entry) or `clean`; a malformed file or entry closes to `clean`.
pub(crate) fn claims_mode(root: &Path) -> String {
    let path = root.join("dev").join("switches.json");
    if !path.is_file() {
        return "report".to_owned();
    }
    let Ok(Ok(data)) = read_text(&path).map(|t| serde_json::from_str::<Value>(&t)) else {
        return "clean".to_owned();
    };
    let state = match &data {
        Value::Object(m) => match m.get("claims") {
            None => Some(json!("report")),
            Some(c) if !super::index::truthy(Some(c)) => Some(json!("report")),
            Some(Value::Object(c)) => c.get("state").cloned(),
            Some(_) => return "clean".to_owned(),
        },
        _ => None,
    };
    match state.as_ref().and_then(Value::as_str) {
        Some(s @ ("report" | "clean")) => s.to_owned(),
        _ => "clean".to_owned(),
    }
}

/// Files `keys` into the feature being landed; what was done, or the error naming what to do instead.
pub(crate) fn carry(
    root: &Path,
    feature: &str,
    task: &str,
    keys: &[String],
    ruling: &str,
) -> Result<String, String> {
    if claims_mode(root) == "report" {
        return Err("the claims switch is at report: a carried finding is a row of `make claims-report`, filed nowhere (feature 445); `make claims-clean REASON=` when the claims are closed out".to_owned());
    }
    let mut d = crate::plan::resolve_feature(feature, root);
    let (here, active) = (target(root)?, crate::plan::active_feature(root));
    if let (Some(dd), Some(h), Some(a)) = (&d, &here, &active) {
        if canon(dd) == canon(a) {
            d = Some(h.clone());
        }
    }
    let wrong = match (&d, &here) {
        (Some(dd), Some(h)) => canon(dd) != canon(h),
        _ => true,
    };
    if wrong {
        let moved = matches!((&here, &active), (Some(h), Some(a)) if canon(h) != canon(a));
        let place = if moved {
            "the claims feature's - this delta holds no engine code"
        } else {
            "the active task's"
        };
        let name = here.as_ref().map_or_else(
            || "none: `make task-start F=<n> T=<Txx>` first".to_owned(),
            |h| {
                h.file_name()
                    .unwrap_or_default()
                    .to_string_lossy()
                    .into_owned()
            },
        );
        return Err(format!(
            "a carried finding is filed only into {place} ({name}), not {feature}"
        ));
    }
    let d = d.unwrap_or_default();
    if !ruling.is_empty() && !ruled(&d, ruling)? {
        let name = d.file_name().unwrap_or_default().to_string_lossy();
        return Err(format!("RULING={ruling} is no trigger in {name}/arbiter.jsonl - name the round arbiter's recorded ruling that carried these findings"));
    }
    if keys.is_empty() {
        return Ok("claims-carry: no carried finding is unfiled".to_owned());
    }
    let tasks = d.join("tasks.md");
    let text = read_text(&tasks)?;
    let by = if ruling.is_empty() {
        "the claims gate (385 FR-013)".to_owned()
    } else {
        format!("the round arbiter's ruling {ruling}")
    };
    let (text, task) = if task.is_empty() {
        new_box(&text, keys, ruling)
    } else {
        (file_into(&text, task, keys, &by)?, task.to_owned())
    };
    std::fs::write(&tasks, text).map_err(fail)?;
    let mut row = Map::new();
    row.insert("task".into(), json!(task));
    row.insert("keys".into(), json!(keys));
    row.insert("utc".into(), json!(crate::record::repo::utc_now()));
    if !ruling.is_empty() {
        row.insert("ruling".into(), json!(ruling));
    }
    let line = crate::logs::one_line(&Value::Object(row)) + "\n";
    let mut f = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(d.join(RECORD))
        .map_err(fail)?;
    std::io::Write::write_all(&mut f, line.as_bytes()).map_err(fail)?;
    let name = d.file_name().unwrap_or_default().to_string_lossy();
    Ok(format!("claims-carry: {} finding(s) filed into {name} {task}; commit tasks.md and {RECORD} with the landing", keys.len()))
}

/// The claim key a classified line (`f"{verdict:<14} {key} - {note}"`) names.
pub(crate) fn key_of(line: &str) -> String {
    let rest: String = line.chars().skip(14).collect();
    l7r_guard::shared::py_text::strip(rest.split(" - ").next().unwrap_or_default()).to_owned()
}

/// key -> `<feature> <task>` for every DRIFTED claim whose text names an open task row naming its unit, and every DRIFTED claim the arbiter accepted.
pub(crate) fn known_drifts(
    cur: &Cur,
    index: &Index,
    root: &Path,
) -> Result<HashMap<String, String>, Fail> {
    let mut cand: Vec<(String, (String, String))> = Vec::new();
    for (key, v) in index {
        let found: Vec<(String, String)> = match cur.get(key) {
            Some(row) if is(v, "verdict", "DRIFTED") => TASK_NAMED
                .captures_iter(&row.claim.account)
                .flatten()
                .map(|c| (c[1].to_owned(), c[2].to_owned()))
                .collect(),
            _ => Vec::new(),
        };
        if let Some(last) = found.last() {
            cand.push((key.clone(), last.clone()));
        }
    }
    let named: HashSet<&String> = cand.iter().map(|(k, _)| k).collect();
    let mut out: HashMap<String, String> = index
        .iter()
        .filter(|(k, v)| {
            !named.contains(k)
                && cur.contains(k)
                && is(v, "verdict", "DRIFTED")
                && field(v, "note").contains(ACCEPTED)
        })
        .map(|(k, _)| (k.clone(), BY_ARBITER.to_owned()))
        .collect();
    let mut boxes: HashMap<(String, String), String> = HashMap::new();
    for (key, (feat, task)) in cand {
        if let std::collections::hash_map::Entry::Vacant(slot) =
            boxes.entry((feat.clone(), task.clone()))
        {
            let specs = spec_glob(root, &feat, Some("tasks.md"));
            let found = match specs.first() {
                Some(p) => {
                    let text = read_text(p)?;
                    re(&format!(r"(?m)^- \[ \] {task} .*$"))
                        .find(&text)
                        .ok()
                        .flatten()
                        .map(|m| m.as_str().to_owned())
                }
                None => None,
            };
            slot.insert(found.unwrap_or_default());
        }
        let uid = key.rsplit_once('#').map_or(key.as_str(), |p| p.0);
        let tail = uid.split_once("::").map_or(uid, |p| p.1);
        let name = tail.rsplit_once('.').map_or(tail, |p| p.1);
        let row = &boxes[&(feat.clone(), task.clone())];
        let pat = re(&format!(r"(?<![\w.]){}(?!\w)", fancy_regex::escape(name)));
        if !row.is_empty() && pat.is_match(row).unwrap_or(false) {
            out.insert(key, format!("{feat} {task}"));
        } else if field(&index[&key], "note").contains(ACCEPTED) {
            out.insert(key, BY_ARBITER.to_owned());
        }
    }
    Ok(out)
}

/// `sorted((root / "specs").glob(f"{feat}-*[/leaf]"))`.
pub(crate) fn spec_glob(root: &Path, feat: &str, leaf: Option<&str>) -> Vec<PathBuf> {
    let prefix = format!("{feat}-");
    let mut out: Vec<PathBuf> = std::fs::read_dir(root.join("specs"))
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| e.file_name().to_string_lossy().starts_with(&prefix))
        .map(|e| leaf.map_or_else(|| e.path(), |l| e.path().join(l)))
        .filter(|p| leaf.is_none() || p.exists())
        .collect();
    out.sort();
    out
}

/// Every claim key a feature's `gm-review.jsonl` records as an admitted known drift.
pub(crate) fn recorded_known(root: &Path) -> Result<HashSet<String>, Fail> {
    let mut files: Vec<PathBuf> = std::fs::read_dir(root.join("specs"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path().join("gm-review.jsonl"))
        .filter(|p| p.exists())
        .collect();
    files.sort();
    let mut out = HashSet::new();
    for f in files {
        for ln in super::units::splitlines(&read_text(&f)?) {
            let Ok(r) = serde_json::from_str::<Value>(&ln) else {
                continue;
            };
            if is(&r, "kind", KNOWN_KIND) && super::index::truthy(r.get("claim")) {
                out.insert(
                    r["claim"]
                        .as_str()
                        .map_or_else(|| r["claim"].to_string(), str::to_owned),
                );
            }
        }
    }
    Ok(out)
}

/// (owed refusals, introduced, pre-existing, carried (key, line)).
pub(crate) type Classified = (Vec<String>, Vec<String>, Vec<String>, Vec<(String, String)>);

/// What the gate reads of a tree: the rows now, the index, and what is owed.
pub(crate) struct Reading {
    pub(crate) cur: Cur,
    pub(crate) index: Index,
}

/// (owed refusals, introduced, pre-existing, carried) at `root` against its merge base with origin/main.
pub(crate) fn classified(
    reader: &mut Reader,
    root: &Path,
    at: &Reading,
) -> Result<Classified, Fail> {
    let store = load_map(&root.join(STORE))?;
    let due = owed(
        &at.cur,
        &at.index,
        Some(&root.join("research").join("questions")),
        Some(&store),
    )?;
    let mut mb =
        l7r_guard::shared::py_text::strip(&git(root, &["merge-base", "HEAD", "origin/main"]))
            .to_owned();
    if mb.is_empty() {
        l7r_guard::shared::py_text::strip(&git(root, &["rev-parse", "HEAD"])).clone_into(&mut mb);
    }
    let base_index = if mb.is_empty() {
        Index::new()
    } else {
        let text = git(root, &["show", &format!("{mb}:{INDEX}")]);
        let parsed = serde_json::from_str::<Value>(if text.is_empty() { "{}" } else { &text });
        let parsed = parsed.map_err(|e| format!("json.decoder.JSONDecodeError: {e}"));
        parsed?.as_object().cloned().unwrap_or_default()
    };
    let tmp = super::temp_dir("base");
    std::fs::create_dir_all(&tmp).map_err(fail)?;
    let judged = (|| -> Result<_, Fail> {
        let cores = if mb.is_empty() {
            HashMap::new()
        } else {
            base_tree("git", root, &mb, &tmp)?;
            base_cores(reader, &tmp)?
        };
        let mut answered = HashSet::new();
        for (k, v) in &at.index {
            if let Some(row) = at.cur.get(k) {
                if relabel_answered(v, row, root)? {
                    answered.insert(k.clone());
                }
            }
        }
        let deferred = load_deferred(&root.join(super::index::DEFERRED))?;
        let qdir = tmp.join("research").join("questions");
        classify(
            &at.cur,
            &at.index,
            &Base {
                index: &base_index,
                cores: &cores,
                qdir: &qdir,
                deferred: &deferred,
                answered: &answered,
            },
        )
    })();
    let _ = std::fs::remove_dir_all(&tmp);
    let (intro, pre, carried) = judged?;
    Ok((
        due.into_iter()
            .map(|(k, why)| format!("owed ({why}): {k}"))
            .collect(),
        intro,
        pre,
        carried,
    ))
}

/// (key, refusal) for every open finding `make claims-report` lists: what the gate refuses at `clean`.
pub(crate) fn open_lines(root: &Path, at: &Reading) -> Result<Vec<(String, String)>, Fail> {
    let rows = live_rows(&at.cur, &at.index);
    Ok(open_findings(&rows, &load_deferred(&root.join(super::index::DEFERRED))?)?
        .into_iter()
        .map(|(v, k, note)| {
            let cut: String = note.chars().take(160).collect();
            let line = format!("open ({v}): {k} - {cut} - fix it or its claim here: `make claims-bundle UNITS=\"{k}\"`");
            (k, line)
        })
        .collect())
}

/// (refusals, warnings) for the push: owed units, introduced findings, carried ones not yet filed, unrecorded known drifts; at `clean` every open finding.
pub(crate) fn gate(
    reader: &mut Reader,
    root: &Path,
    at: &Reading,
) -> Result<(Vec<String>, Vec<String>), Fail> {
    let (refuse, intro, pre, carried) = classified(reader, root, at)?;
    let known = known_drifts(&at.cur, &at.index, root)?;
    let (revealed, intro): (Vec<String>, Vec<String>) = intro
        .into_iter()
        .partition(|x| known.contains_key(&key_of(x)));
    let done_known = recorded_known(root)?;
    let unrecorded: Vec<&String> = revealed
        .iter()
        .filter(|x| known[&key_of(x)] != BY_ARBITER && !done_known.contains(&key_of(x)))
        .collect();
    let mut pre = pre;
    pre.extend(
        revealed
            .iter()
            .filter(|x| !unrecorded.contains(x))
            .map(|x| format!("known drift ({}): {x}", known[&key_of(x)])),
    );
    let d = target(root)?;
    let done = filed(d.as_deref())?;
    let dname = d.as_ref().map(|p| {
        p.file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned()
    });
    let how = dname.as_ref().map_or_else(
        || "`make task-start F=<n> T=<Txx>`, then `make claims-carry F=<n>`".to_owned(),
        |n| {
            format!(
                "`make claims-carry F={}`",
                n.split('-').next().unwrap_or_default()
            )
        },
    );
    let mut flagged: Vec<String> = intro.iter().map(|x| format!("introduced: {x}")).collect();
    flagged.extend(carried.iter().filter(|(k, _)| !done.contains_key(k)).map(|(_, line)| format!("carry: {line} - a finding on code the change left unchanged: file it with {how} (make land files it itself)")));
    flagged.extend(unrecorded.iter().map(|x| format!("known: {x} - a known drift ({}) to record for the GM: `make claims-known` (make land runs it)", known[&key_of(x)])));
    let warn: Vec<String> = carried
        .iter()
        .filter(|(k, _)| done.contains_key(k))
        .map(|(k, line)| {
            format!(
                "carried ({} {}): {line}",
                dname.clone().unwrap_or_default(),
                done[k]
            )
        })
        .collect();
    let pre_lines: Vec<String> = pre.iter().map(|x| format!("pre-existing: {x}")).collect();
    if claims_mode(root) == "report" {
        let mut w = flagged;
        w.extend(pre_lines);
        w.extend(warn);
        return Ok((refuse, w));
    }
    let mut named: BTreeSet<String> = intro.iter().map(|x| key_of(x)).collect();
    named.extend(carried.iter().map(|(k, _)| k.clone()));
    named.extend(revealed.iter().map(|x| key_of(x)));
    let listed: Vec<String> = open_lines(root, at)?
        .into_iter()
        .filter(|(k, _)| !named.contains(k) || done.contains_key(k))
        .map(|(_, l)| l)
        .collect();
    let mut r = refuse;
    r.extend(flagged);
    r.extend(listed);
    let mut w = pre_lines;
    w.extend(warn);
    Ok((r, w))
}

/// `make claims-known`: each known drift the gate would refuse unrecorded, written as a row of its task's feature's `gm-review.jsonl` with the GM's box, by the Python (`gm_review.add_row`, T91's); the lines written.
pub(crate) fn record_known(
    reader: &mut Reader,
    root: &Path,
    at: &Reading,
) -> Result<Vec<String>, Fail> {
    let (refuse, _) = gate(reader, root, at)?;
    let mut written = Vec::new();
    let found = refuse
        .iter()
        .filter_map(|l| KNOWN_LINE.captures(l).ok().flatten());
    for m in found {
        let (key, feat, task) = (key_of(&m[1]), m[2].to_owned(), m[3].to_owned());
        let finding: String = l7r_guard::shared::py_text::strip(&m[1])
            .chars()
            .take(400)
            .collect();
        for spec in spec_glob(root, &feat, None).into_iter().take(1) {
            let row = json!({"kind": KNOWN_KIND, "claim": key, "task": task, "finding": finding, "utc": crate::record::repo::utc_now()});
            reader.ask("gm_review_add_row", &json!([spec.to_string_lossy(), row]))?;
            let name = spec.file_name().unwrap_or_default().to_string_lossy();
            written.push(format!("{name} {task}: {key}"));
        }
    }
    Ok(written)
}

#[cfg(test)]
mod more;
#[cfg(test)]
mod tests;
