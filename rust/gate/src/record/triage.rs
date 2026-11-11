//! The pop-up triage (from `modal_triage.py`, feature 449 T87): a drawing or question page's edit owes a pop-up's checks only where it bears on that pop-up. `make modal-triage` writes one bundle of each moved page's changed blocks and the pop-ups naming it; `make modal-triaged` applies a triage reply, answering what the reply leaves alone and marking what it names.

use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::checks::pages::read_page;
use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::pyjson;
use serde_json::{json, Map, Value};

use super::args::{parse, Parsed, Spec};
use super::modals::{self, Modal, DEPICTION_CHECK, RESEARCH_AGENT, RESEARCH_CHECKS};
use super::owed::{self, answered as is_answered, merge_base, read_answer, write_answer};
use super::repo::{fail, git, read_text, read_universal, Fail};
use super::units::re;
use crate::Reply;

const DEFAULT_OUT: &str = "/tmp/l7r-check";
const TOUCHED: &str = "modal-triage-touched.json";

static TOUCHES: LazyLock<Regex> =
    LazyLock::new(|| re(r"^TOUCHES\s+`?(\S+?)`?(?:\s+@\s+`?(\S+?)`?)?\s+-\s+(.*)$"));

/// One clone's bundle directory.
fn default_out(root: &Path) -> PathBuf {
    let name = root
        .file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
    Path::new(DEFAULT_OUT).join(format!("modal-triage-{name}"))
}

/// Whether the unit is owed only because a page it names moved.
pub(crate) fn triage_only(why: &str) -> bool {
    why.starts_with("a page its ")
}

/// {slug: fingerprint} of the units a triage named.
pub(crate) fn touched(store: &Path) -> Result<std::collections::HashMap<String, String>, Fail> {
    let Some(text) = read_universal(&store.join(TOUCHED))? else {
        return Ok(std::collections::HashMap::new());
    };
    let value: Map<String, Value> = serde_json::from_str(&text).map_err(fail)?;
    Ok(value
        .into_iter()
        .map(|(k, v)| (k, v.as_str().unwrap_or("").to_owned()))
        .collect())
}

/// (slug, why, fingerprint) of every unit owed only a triage: unanswered at its fingerprint and not named by a triage.
pub(crate) fn pending(
    root: &Path,
    base: &str,
    store: &Path,
    owed: Option<&[(String, String, String)]>,
) -> Result<Vec<(String, String, String)>, Fail> {
    let named = touched(store)?;
    let rows = match owed {
        Some(r) => r.to_vec(),
        None => modals::owed(root, base, "")?,
    };
    Ok(rows
        .into_iter()
        .filter(|(slug, why, fp)| {
            triage_only(why) && !is_answered(store, slug, fp, "") && named.get(slug) != Some(fp)
        })
        .collect())
}

/// The page at `path` written into the clone's object store as it stands; its blob id, or "".
pub(crate) fn keep(root: &Path, path: &str) -> String {
    if !root.join(path).is_file() {
        return String::new();
    }
    git(root, &["hash-object", "-w", "--", path])
        .trim()
        .to_owned()
}

fn blob_text(root: &Path, blob: &str) -> String {
    git(root, &["cat-file", "-p", blob])
}

fn kept_pages(store: &Path, slug: &str) -> Map<String, Value> {
    read_answer(store, slug)
        .get("pages")
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default()
}

fn page_before(
    root: &Path,
    store: &Path,
    slug: &str,
    path: &str,
    base: &str,
    read: &mut modals::RevReader,
) -> String {
    let blob = kept_pages(store, slug)
        .get(path)
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_owned();
    let kept = Some(blob)
        .filter(|b| !b.is_empty())
        .map(|b| blob_text(root, &b))
        .unwrap_or_default();
    let fall_back = kept.is_empty() && !base.is_empty();
    if fall_back {
        read.read(path).unwrap_or_default()
    } else {
        kept
    }
}

/// Which version of `path` a unit's triage diffs against: the blob its last answer kept, or "".
fn baseline(store: &Path, slug: &str, path: &str) -> String {
    kept_pages(store, slug)
        .get(path)
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_owned()
}

/// (blocks new or changed, blocks removed) between two versions of a page.
fn changed_blocks(old: &str, new: &str) -> (Vec<String>, Vec<String>) {
    let was: Vec<String> = read_page(old).blocks.into_iter().map(|b| b.words).collect();
    let now: Vec<String> = read_page(new).blocks.into_iter().map(|b| b.words).collect();
    let (old_set, new_set): (HashSet<&String>, HashSet<&String>) =
        (was.iter().collect(), now.iter().collect());
    (
        now.iter()
            .filter(|w| !old_set.contains(w))
            .cloned()
            .collect(),
        was.iter()
            .filter(|w| !new_set.contains(w))
            .cloned()
            .collect(),
    )
}

fn pages_of(m: &Modal, check: &str) -> Vec<String> {
    if check == DEPICTION_CHECK {
        m.drawing_files()
    } else {
        m.entry_files()
    }
}

fn clear_dir(dir: &Path) -> Result<(), Fail> {
    if dir.exists() {
        for entry in std::fs::read_dir(dir).map_err(fail)?.flatten() {
            std::fs::remove_file(entry.path()).map_err(fail)?;
        }
    }
    Ok(())
}

fn truncated(text: &str) -> String {
    text.chars().take(400).collect()
}

/// A page's changed blocks and the pop-ups naming it, keyed `(path, baseline)` (sorted), each pop-up's checks sorted.
type ByPage = std::collections::BTreeMap<
    (String, String),
    std::collections::BTreeMap<String, std::collections::BTreeSet<String>>,
>;

/// Write the triage bundle (`MANIFEST.md`, `triage.json`); (its MANIFEST, how many units), or None for no unit owed one.
pub(crate) fn bundle(
    root: &Path,
    out: &Path,
    base: &str,
) -> Result<Option<(PathBuf, usize)>, Fail> {
    let base = if base.is_empty() {
        merge_base(root)
    } else {
        base.to_owned()
    };
    let store = owed::store(root);
    let units = pending(root, &base, &store, None)?;
    if units.is_empty() {
        return Ok(None);
    }
    let modals_now: Vec<(String, Modal)> = modals::modals_now(root, false)?
        .into_iter()
        .map(|m| (m.uid(), m))
        .collect();
    let find = |uid: &str| modals_now.iter().find(|(u, _)| u == uid).map(|(_, m)| m);
    let mut read = modals::read_at(root, &base);
    let mut by_page: ByPage = ByPage::new();
    let mut blocks: std::collections::HashMap<(String, String), (Vec<String>, Vec<String>)> =
        std::collections::HashMap::new();
    let (mut reads, mut blobs) = (Map::new(), Map::new());
    for (slug, why, _fp) in &units {
        let (check, uid) = slug.split_once(':').unwrap_or((slug, ""));
        let named = |p: &String| why.contains(&name_of(p));
        for path in find(uid)
            .map(|m| pages_of(m, check))
            .unwrap_or_default()
            .into_iter()
            .filter(named)
        {
            let now = read_universal(&root.join(&path))?.unwrap_or_default();
            let key = (path.clone(), baseline(&store, slug, &path));
            if !blocks.contains_key(&key) {
                let before = page_before(root, &store, slug, &path, &base, &mut read);
                blocks.insert(key.clone(), changed_blocks(&before, &now));
            }
            by_page
                .entry(key)
                .or_default()
                .entry(uid.to_owned())
                .or_default()
                .insert(check.to_owned());
            reads
                .entry(slug.clone())
                .or_insert_with(|| json!([]))
                .as_array_mut()
                .map(|a| a.push(json!(path)));
            let row = blobs.entry(slug.clone()).or_insert_with(|| json!({}));
            if let Some(m) = row.as_object_mut() {
                m.insert(path.clone(), json!(keep(root, &path)));
            }
        }
    }
    clear_dir(out)?;
    std::fs::create_dir_all(out).map_err(fail)?;
    let mut parts = vec![
        "# Triage of pop-up checks (feature 375, FR-001)\n".to_owned(),
        "owed-checks: modal-triage\n".to_owned(),
        "For the `modal-triage` agent: rule on each pop-up below as your contract says, and reply in its form.\n".to_owned(),
    ];
    for (key, popups) in &by_page {
        let (path, base_blob) = key;
        let (fresh, gone) = &blocks[key];
        let against = if base_blob.is_empty() {
            "against the merge base (no check has read it yet)"
        } else {
            "against the version these pop-ups' last check read"
        };
        parts.push(format!(
            "## {path}\n\n({against})\n\nNew or changed blocks:\n"
        ));
        if fresh.is_empty() {
            parts.push("(none)\n".to_owned());
        } else {
            parts.extend(fresh.iter().map(|w| format!("> {w}\n")));
        }
        if !gone.is_empty() {
            parts.push("Removed blocks (no longer on the page):\n".to_owned());
            parts.extend(gone.iter().map(|w| format!("> {w}\n")));
        }
        parts.push("Pop-ups naming it:\n".to_owned());
        for (uid, checks) in popups {
            let m = find(uid).map_or_else(Modal::default, Clone::clone);
            let checks: Vec<&str> = checks.iter().map(String::as_str).collect();
            let depiction = m.tag("Depiction");
            let tail = if depiction.is_empty() {
                String::new()
            } else {
                format!(" | Depiction - {}", truncated(depiction))
            };
            parts.push(format!(
                "- UID `{uid}` ({}): About - {}{tail}",
                checks.join(", "),
                truncated(m.tag("About"))
            ));
        }
        parts.push(String::new());
    }
    let manifest = out.join("MANIFEST.md");
    std::fs::write(&manifest, parts.join("\n") + "\n").map_err(fail)?;
    let units_map: Map<String, Value> = units
        .iter()
        .map(|(s, _, fp)| (s.clone(), json!(fp)))
        .collect();
    let data = json!({"units": units_map, "pages": reads, "blobs": blobs});
    std::fs::write(
        out.join("triage.json"),
        pyjson::dumps(&pyjson::sorted(&data), Some(1), true) + "\n",
    )
    .map_err(fail)?;
    Ok(Some((manifest, units.len())))
}

fn name_of(p: &str) -> String {
    Path::new(p)
        .file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned())
}

/// Does a unit whose checks read `unit_pages` read the page a reply line named?
fn reads_page(page: &str, unit_pages: &[String]) -> bool {
    let name = name_of(page);
    unit_pages.iter().any(|p| {
        let n = name_of(p);
        n == name || n == format!("{name}.html")
    })
}

fn as_pages(v: Option<&Value>) -> Vec<String> {
    v.and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|s| s.as_str().map(str::to_owned))
        .collect()
}

/// Apply a triage reply; the messages `make modal-triaged` prints.
pub(crate) fn record(
    store: &Path,
    units: &Map<String, Value>,
    reply: &str,
    pages: Option<&Value>,
    blobs: Option<&Value>,
) -> Result<Vec<String>, Fail> {
    let mut named: Vec<(String, Vec<(String, String)>)> = Vec::new();
    for raw in reply.split('\n') {
        if let Ok(Some(c)) = TOUCHES.captures(strip(raw).trim_matches('`')) {
            let uid = c[1].trim_matches('`').to_owned();
            let row = (
                c.get(2).map_or_else(String::new, |g| g.as_str().to_owned()),
                c[3].to_owned(),
            );
            match named.iter_mut().find(|(u, _)| *u == uid) {
                Some((_, rows)) => rows.push(row),
                None => named.push((uid, vec![row])),
            }
        }
    }
    let mut slugs: Vec<&String> = units.keys().collect();
    slugs.sort();
    let uids: HashSet<&str> = slugs
        .iter()
        .map(|s| s.split_once(':').map_or("", |p| p.1))
        .collect();
    let mut refused: Vec<&str> = named
        .iter()
        .map(|(u, _)| u.as_str())
        .filter(|u| !uids.contains(u))
        .collect();
    refused.sort_unstable();
    let mut msgs: Vec<String> = refused
        .iter()
        .map(|u| format!("refused: `{u}` is not a pop-up of this triage"))
        .collect();
    let mut mark = touched(store)?;
    let known: Vec<String> = pages
        .and_then(Value::as_object)
        .into_iter()
        .flatten()
        .flat_map(|(_, v)| as_pages(Some(v)))
        .collect();
    for slug in slugs {
        let fp = units[slug].as_str().unwrap_or("");
        let uid = slug.split_once(':').map_or("", |p| p.1);
        let lines = named
            .iter()
            .find(|(u, _)| u == uid)
            .map_or(&[][..], |(_, v)| v.as_slice());
        let unit_pages = pages.and_then(|p| p.get(slug));
        let hit: Vec<&str> = lines
            .iter()
            .filter(|(page, _)| {
                page.is_empty()
                    || pages.is_none()
                    || unit_pages.is_none()
                    || !reads_page(page, &known)
                    || reads_page(page, &as_pages(unit_pages))
            })
            .map(|(_, why)| why.as_str())
            .collect();
        if let Some(first) = hit.first() {
            mark.insert(slug.clone(), fp.to_owned());
            msgs.push(format!("touched: {slug} - {first}"));
        } else {
            let mut kept = read_answer(store, slug)
                .get("pages")
                .and_then(Value::as_object)
                .cloned()
                .unwrap_or_default();
            for (k, v) in blobs
                .and_then(|b| b.get(slug))
                .and_then(Value::as_object)
                .into_iter()
                .flatten()
            {
                kept.insert(k.clone(), v.clone());
            }
            let pages_value = Value::Object(kept);
            write_answer(store, slug, fp, "triage: untouched", Some(&pages_value))?;
        }
    }
    std::fs::create_dir_all(store).map_err(fail)?;
    let body = Value::Object(mark.into_iter().map(|(k, v)| (k, json!(v))).collect());
    std::fs::write(
        store.join(TOUCHED),
        pyjson::dumps(&pyjson::sorted(&body), Some(1), true) + "\n",
    )
    .map_err(fail)?;
    Ok(msgs)
}

/// Why `make modal-bundle` may not bundle `check` on `m` yet: a unit of it owed only a triage that has not named it.
pub(crate) fn refusal(
    root: &Path,
    m: &Modal,
    check: &str,
    owed: Option<&[(String, String, String)]>,
) -> Result<String, Fail> {
    let base = merge_base(root);
    let store = owed::store(root);
    let slugs: HashSet<String> = if check == RESEARCH_AGENT {
        RESEARCH_CHECKS
            .iter()
            .map(|c| format!("{c}:{}", m.uid()))
            .collect()
    } else {
        HashSet::from([format!("{check}:{}", m.uid())])
    };
    let mut waiting: Vec<String> = pending(root, &base, &store, owed)?
        .into_iter()
        .map(|p| p.0)
        .filter(|s| slugs.contains(s))
        .collect();
    if waiting.is_empty() {
        return Ok(String::new());
    }
    waiting.sort();
    Ok(format!("{} owe(s) only a TRIAGE (a page it names moved, its own words did not) - `make modal-triage` first; it sends on only the pop-ups a change bears on", waiting.join(", ")))
}

fn usage(line: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("{line}\n"),
        code: 2,
    }
}

fn run_bundle(root: &Path, parsed: &Parsed) -> Result<Reply, Fail> {
    let out_arg = parsed.text("--out", "");
    let out = if out_arg.is_empty() {
        default_out(root)
    } else {
        PathBuf::from(out_arg)
    };
    Ok(Reply {
        stdout: match bundle(root, &out, "")? {
            None => "modal-triage: no pop-up is owed a triage\n".to_owned(),
            Some((manifest, n)) => format!(
                "{}\nmodal-triage: {n} unit(s); dispatch the `modal-triage` agent on the MANIFEST (a session started before 2026-10-17's amendment 6 landed: restart to load it), save its reply, then `make modal-triaged BUNDLE=<dir> REPLY=<file>`\n",
                manifest.display()
            ),
        },
        stderr: String::new(),
        code: 0,
    })
}

fn run_record(root: &Path, parsed: &Parsed) -> Result<Reply, Fail> {
    let (dir, reply_file) = (parsed.text("--bundle", ""), parsed.text("--reply", ""));
    let text = read_text(&Path::new(dir).join("triage.json"))?;
    let data: Value = serde_json::from_str(&text).map_err(fail)?;
    let units = data
        .get("units")
        .and_then(Value::as_object)
        .cloned()
        .ok_or_else(|| "triage.json: no units".to_owned())?;
    let reply = owed_reply(root, reply_file)?;
    let msgs = record(
        &owed::store(root),
        &units,
        &reply,
        data.get("pages"),
        data.get("blobs"),
    )?;
    let mut out = String::new();
    for msg in &msgs {
        out.push_str(&format!("modal-triaged: {msg}\n"));
    }
    let n = msgs.iter().filter(|m| m.starts_with("touched")).count();
    out.push_str(&format!("modal-triaged: {n} of {} unit(s) sent on to their checks; the rest answered `triage: untouched`\n", units.len()));
    Ok(Reply {
        stdout: out,
        stderr: String::new(),
        code: 0,
    })
}

fn owed_reply(root: &Path, path: &str) -> Result<String, Fail> {
    super::owed::reply_of(root, path)
}

/// `record modal-triage [--root DIR] bundle [--out DIR] | record --bundle DIR --reply F`.
pub(crate) fn cli(args: &[String]) -> Reply {
    let main = [Spec::value("--root")];
    let mut i = 0;
    while i < args.len() && args[i].starts_with('-') {
        i += if args[i].contains('=') { 1 } else { 2 };
    }
    let split_at = i.min(args.len());
    let parsed_main = match parse(&args[..split_at], &main) {
        Ok(p) => p,
        Err(complaint) => {
            return usage(&format!("usage: l7r-gate record modal-triage: {complaint}"))
        }
    };
    let root = std::fs::canonicalize(parsed_main.text("--root", "."))
        .unwrap_or_else(|_| parsed_main.text("--root", ".").into());
    let (verb, rest) = (
        args.get(split_at).map_or("", String::as_str),
        args.get(split_at + 1..).unwrap_or(&[]),
    );
    let (specs, runner): (&[Spec], fn(&Path, &Parsed) -> Result<Reply, Fail>) = match verb {
        "bundle" => (&[Spec::value("--out")], run_bundle),
        "record" => (
            &[Spec::value("--bundle"), Spec::value("--reply")],
            run_record,
        ),
        _ => return usage("usage: l7r-gate record modal-triage bundle | record"),
    };
    let parsed = match parse(rest, specs) {
        Ok(p) if verb != "record" || (!p.text("--bundle", "").is_empty() && !p.text("--reply", "").is_empty()) => p,
        Ok(_) => return usage("usage: l7r-gate record modal-triage record: the arguments --bundle and --reply are required"),
        Err(complaint) => return usage(&format!("usage: l7r-gate record modal-triage {verb}: {complaint}")),
    };
    runner(&root, &parsed).unwrap_or_else(|why| Reply {
        stdout: String::new(),
        stderr: why + "\n",
        code: 1,
    })
}

#[cfg(test)]
mod tests;
