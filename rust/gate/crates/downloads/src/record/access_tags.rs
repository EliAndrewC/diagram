//! The access tag: what can be got of each source, and when that was last known (feature 313, spec FR-011; feature 449 T80, from `access_tags.py`).
//!
//! WHY (the GM, 2026-10-02, `specs/312-uncited-source-catalog/request.md`): *"it is useful for us to record what things in the past you were able to get versus things
//! that timed out versus things that I was able to get ... versus things that I was able to get only a like partial summary of ... versus things that I found require a
//! paid login"*.
//!
//! The states are declared once, in order from the most open, in `research/source-access.json`. DERIVED, NOT STORED (spec Decisions): a stored copy would go stale at the
//! next archive capture and conflict across clones, so the tag is computed each time from what the repository records (plan D9):
//!   1. a GM mark on a download-list entry naming the key: downloaded -> gm-full whatever else is ticked; partial -> gm-partial; paywalled alone -> paywalled; not found
//!      alone gives no state. Several entries: the newest mark that gives a state, on the same date the most open; a not-found only adds to the basis;
//!   2. else the most open of the key's archive manifest rows (feature 309), dated by its capture - a row whose page would not render whole but whose served text is kept
//!      counts as open, since we read it;
//!   3. else, no row: open with a READ comment, dated by the latest READ; never-read without one;
//!   4. a state recorded by hand in `source-access.json` wins over 2-3 on the same date or later, never over a GM mark that gives a state.
//!
//! A download-list entry with no registry key is `download:<id>`: rule 1, then a state recorded by hand, else never-read.

use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use super::downloads::parse::{entries, parse, strip, words, Entry, Marks, RECORDED};
use super::downloads::CANON;
use super::{read_text, reply};
use crate::checks::py_repr;
use crate::logs::{one_line_utf8, py_dumps};
use crate::measure::text_err;
use crate::Reply;

const ACCESS: &str = "research/source-access.json";
const REGISTRY: &str = "research/sources/010-works-cited";
const MANIFEST: &str = "research/archive";
const USAGE: &str = "usage: l7r-gate record access-tags report [--key K] [--json] | set <key|download:ID> <state> <date> <reason> | entry-keys <id>\n";

fn compiled(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static KEY_HEAD: LazyLock<Regex> = LazyLock::new(|| compiled(r#"<h3 id="([^"]+)""#));
static READ: LazyLock<Regex> = LazyLock::new(|| compiled(r"READ (\d{4}-\d{2}-\d{2})"));
static TICKED_KEY: LazyLock<Regex> = LazyLock::new(|| compiled(r"`([a-z0-9][a-z0-9-]*)`"));
static KEY_LINE: LazyLock<Regex> = LazyLock::new(|| compiled(r"(?m)^- Key: (.+)$"));
static LINK: LazyLock<Regex> = LazyLock::new(|| compiled(r"\]\((https?://[^)\s\x1c-\x1f]+)\)"));
static HTTP: LazyLock<Regex> = LazyLock::new(|| compiled(r"HTTP (\d{3})"));
static DOWN: LazyLock<Regex> =
    LazyLock::new(|| compiled(r"(?i)Timeout|network|aborted|ECONN|ENOTFOUND|socket"));
static DATE: LazyLock<Regex> = LazyLock::new(|| compiled(r"^\d{4}-\d{2}-\d{2}$"));

fn found_groups(pattern: &Regex, text: &str) -> Vec<String> {
    pattern
        .captures_iter(text)
        .flatten()
        .map(|c| c[1].to_owned())
        .collect()
}

/// One source's tag.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Tag {
    pub state: String,
    date: Option<String>,
    basis: String,
}

impl Tag {
    fn new(state: &str, date: Option<String>, basis: String) -> Self {
        Self {
            state: state.to_owned(),
            date,
            basis,
        }
    }

    /// `<state> (<date>) - <basis>`, the line the report and ingest print.
    #[must_use]
    pub fn line(&self) -> String {
        format!(
            "{} ({}) - {}",
            self.state,
            self.date.as_deref().unwrap_or("no date"),
            self.basis
        )
    }

    fn as_json(&self) -> Value {
        json!({"state": self.state, "date": self.date, "basis": self.basis})
    }
}

/// What the repository records, read once.
pub struct World {
    order: Vec<String>,
    recorded: Map<String, Value>,
    keys: BTreeMap<String, Vec<String>>,
    rows: HashMap<String, Vec<Value>>,
    marks: HashMap<String, Vec<(String, Entry)>>,
    keyless: Vec<String>,
    pub entry_keys: HashMap<String, BTreeSet<String>>,
}

impl World {
    fn rank(&self, state: &str) -> usize {
        self.order
            .iter()
            .position(|s| s == state)
            .unwrap_or(usize::MAX)
    }
}

fn row_state(row: &Value) -> &'static str {
    let outcome = row["outcome"].as_str().unwrap_or("");
    if matches!(outcome, "archived" | "archived-earlier-snapshot") {
        return "open";
    }
    if outcome == "archived-gm-copy" {
        return "gm-full";
    }
    let reason = row["reason"].as_str().unwrap_or("");
    if reason.starts_with("the page would not render whole") {
        // The site served the page and its text is kept (`archive.py`, the REFUSED branch's capture): we read it; only the whole-page snapshot failed. 22 rows on
        // 2026-10-02 (a count of the manifest by reason).
        return "open";
    }
    let code = found_groups(&HTTP, reason).into_iter().next();
    if matches!(code.as_deref(), Some("404" | "410")) {
        return "gone";
    }
    if code.as_deref().is_some_and(|c| c.starts_with('5')) || DOWN.is_match(reason).unwrap_or(false)
    {
        return "down";
    }
    "bot-refused"
}

fn mark_state(m: &Marks) -> Option<&'static str> {
    if m.downloaded {
        Some("gm-full")
    } else if m.partial {
        Some("gm-partial")
    } else if m.paywalled {
        Some("paywalled")
    } else {
        None
    }
}

/// The registry keys an entry names (plan D8): backticked keys, `- Key:` lines, and its links' manifest keys.
fn named_keys(
    e: &Entry,
    keys: &HashSet<&str>,
    url_keys: &HashMap<String, BTreeSet<String>>,
) -> BTreeSet<String> {
    let text = format!("{}\n{}", e.heading, e.body_text());
    let mut found: BTreeSet<String> = found_groups(&TICKED_KEY, &text)
        .into_iter()
        .filter(|k| keys.contains(k.as_str()))
        .collect();
    for line in found_groups(&KEY_LINE, &text) {
        found.extend(
            line.split(',')
                .map(strip)
                .filter(|k| keys.contains(k))
                .map(str::to_owned),
        );
    }
    for url in found_groups(&LINK, &text) {
        found.extend(url_keys.get(&url).into_iter().flatten().cloned());
    }
    found
}

/// `sorted(glob.glob(pattern))`: the non-hidden files of `dir` with this extension, as full-path strings.
fn listed(dir: &Path, ext: &str) -> Vec<PathBuf> {
    std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| !e.file_name().to_string_lossy().starts_with('.'))
        .map(|e| e.path())
        .filter(|p| p.extension().is_some_and(|x| x == ext))
        .collect()
}

fn sorted_paths(mut paths: Vec<PathBuf>) -> Vec<PathBuf> {
    paths.sort_by_key(|p| p.display().to_string());
    paths
}

fn subdirs(dir: &Path) -> Vec<PathBuf> {
    std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| !e.file_name().to_string_lossy().starts_with('.'))
        .map(|e| e.path())
        .collect()
}

fn read_keys(root: &Path) -> Result<BTreeMap<String, Vec<String>>, String> {
    let mut keys = BTreeMap::new();
    for path in sorted_paths(listed(&root.join(REGISTRY), "html")) {
        let text = read_text(&path).map_err(text_err)?;
        if let Some(found) = found_groups(&KEY_HEAD, &text).into_iter().next() {
            keys.insert(found, found_groups(&READ, &text));
        }
    }
    Ok(keys)
}

type Rows = (
    HashMap<String, Vec<Value>>,
    HashMap<String, BTreeSet<String>>,
);

fn read_rows(root: &Path) -> Result<Rows, String> {
    let (mut rows, mut urls): Rows = (HashMap::new(), HashMap::new());
    let files = sorted_paths(
        subdirs(&root.join(MANIFEST))
            .iter()
            .flat_map(|d| listed(d, "json"))
            .collect(),
    );
    for path in files {
        let row: Value =
            serde_json::from_str(&read_text(&path).map_err(text_err)?).map_err(text_err)?;
        for key in row["keys"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(Value::as_str)
        {
            rows.entry(key.to_owned()).or_default().push(row.clone());
            for url in ["url", "final_url"]
                .iter()
                .filter_map(|f| row[*f].as_str())
                .filter(|u| !u.is_empty())
            {
                urls.entry(url.to_owned())
                    .or_default()
                    .insert(key.to_owned());
            }
        }
    }
    Ok((rows, urls))
}

/// Everything the tags are derived from.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn load(root: &Path) -> Result<World, String> {
    let doc: Value = serde_json::from_str(&read_text(&root.join(ACCESS)).map_err(text_err)?)
        .map_err(text_err)?;
    let order = doc["states"]
        .as_array()
        .into_iter()
        .flatten()
        .filter_map(|s| s["id"].as_str())
        .map(str::to_owned)
        .collect();
    let recorded = doc["recorded"].as_object().cloned().unwrap_or_default();
    let keys = read_keys(root)?;
    let (rows, url_keys) = read_rows(root)?;
    let known: HashSet<&str> = keys.keys().map(String::as_str).collect();
    let mut marks: HashMap<String, Vec<(String, Entry)>> = HashMap::new();
    let mut keyless = Vec::new();
    let mut entry_keys: HashMap<String, BTreeSet<String>> = HashMap::new();
    let canon = root.join(CANON);
    let text = if canon.is_file() {
        read_text(&canon).map_err(text_err)?
    } else {
        String::new()
    };
    let blocks = parse(&text);
    for e in entries(&blocks) {
        let own = format!("download:{}", e.id);
        let found = named_keys(e, &known, &url_keys);
        let named = if found.is_empty() {
            BTreeSet::from([own.clone()])
        } else {
            found.clone()
        };
        entry_keys.insert(own.clone(), found.clone());
        if found.is_empty() {
            keyless.push(own);
        }
        let date = RECORDED
            .captures(e.recorded.as_deref().unwrap_or(""))
            .ok()
            .flatten()
            .map(|c| c[1].to_owned());
        if let Some(date) = date.filter(|_| e.marks.as_ref().is_some_and(Marks::any)) {
            for key in named {
                marks
                    .entry(key)
                    .or_default()
                    .push((date.clone(), e.clone()));
            }
        }
    }
    Ok(World {
        order,
        recorded,
        keys,
        rows,
        marks,
        keyless,
        entry_keys,
    })
}

/// Rule 1. A Tag with state "" carries only a not-found basis; None where no mark is recorded.
fn from_marks(w: &World, key: &str) -> Option<Tag> {
    let marked = w.marks.get(key)?;
    let giving = marked
        .iter()
        .filter_map(|(d, e)| e.marks.as_ref().and_then(mark_state).map(|s| (d, e, s)));
    if let Some((date, e, state)) =
        giving.min_by_key(|(d, _, s)| (std::cmp::Reverse((*d).clone()), w.rank(s)))
    {
        return Some(Tag::new(
            state,
            Some(date.clone()),
            format!("the GM's mark on entry {}, recorded {date}", e.id),
        ));
    }
    let ids: Vec<&str> = marked.iter().map(|(_, e)| e.id.as_str()).collect();
    Some(Tag::new(
        "",
        None,
        format!("the GM did not find it (entry {})", ids.join(", ")),
    ))
}

fn captured_number(row: &Value) -> i64 {
    let digits: String = row["captured"]
        .as_str()
        .unwrap_or("0")
        .chars()
        .filter(char::is_ascii_digit)
        .take(14)
        .collect();
    -digits.parse::<i64>().unwrap_or(0)
}

fn captured_rank(row: &Value) -> &'static str {
    if row["captured"].as_str().unwrap_or("").is_empty() {
        "~"
    } else {
        ""
    }
}

/// Rules 2 to 4.
fn derived(w: &World, key: &str) -> Tag {
    if key.starts_with("download:") {
        return Tag::new(
            "never-read",
            None,
            "a download-list entry with no registry key and no mark".to_owned(),
        );
    }
    let best = w.rows.get(key).and_then(|rows| {
        rows.iter()
            .min_by_key(|r| (w.rank(row_state(r)), captured_rank(r), captured_number(r)))
    });
    if let Some(best) = best {
        let date: String = best["captured"]
            .as_str()
            .unwrap_or("")
            .chars()
            .take(10)
            .collect();
        let reason = best["reason"].as_str().unwrap_or("");
        let why = if reason.is_empty() {
            String::new()
        } else {
            format!(" ({})", reason.chars().take(80).collect::<String>())
        };
        let basis = format!(
            "the archive manifest: {}{why}, {}",
            best["outcome"].as_str().unwrap_or(""),
            best["url"].as_str().unwrap_or("")
        );
        return Tag::new(row_state(best), Some(date).filter(|d| !d.is_empty()), basis);
    }
    let latest = w.keys.get(key).and_then(|r| r.iter().max());
    match latest {
        Some(read) => Tag::new(
            "open",
            Some(read.clone()),
            "a READ comment in its registry entry; no archive row".to_owned(),
        ),
        None => Tag::new(
            "never-read",
            None,
            "no READ in its registry entry and no archive row".to_owned(),
        ),
    }
}

/// The tag of one registry key or `download:<id>` (plan D9).
pub fn tag(w: &World, key: &str) -> Tag {
    let gm = from_marks(w, key);
    if let Some(found) = gm.as_ref().filter(|t| !t.state.is_empty()) {
        return found.clone();
    }
    let made = derived(w, key);
    let mut hand: Vec<&Value> = w
        .recorded
        .get(key)
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .collect();
    hand.sort_by_key(|r| r["date"].as_str().unwrap_or("").to_owned());
    if let Some(last) = hand.last().filter(|r| {
        made.date
            .as_deref()
            .is_none_or(|d| r["date"].as_str().unwrap_or("") >= d)
    }) {
        return Tag::new(
            last["state"].as_str().unwrap_or(""),
            last["date"].as_str().map(str::to_owned),
            format!(
                "recorded by hand: {}",
                last["reason"].as_str().unwrap_or("")
            ),
        );
    }
    match gm {
        Some(found) => Tag::new(
            &made.state,
            made.date,
            format!("{}; {}", made.basis, found.basis),
        ),
        None => made,
    }
}

/// Every key, sorted, then the keyless entries; a repeated keyless entry once.
#[must_use]
pub fn every(w: &World) -> Vec<(String, Tag)> {
    let mut seen = HashSet::new();
    w.keys
        .keys()
        .chain(w.keyless.iter())
        .filter(|k| seen.insert((*k).clone()))
        .map(|k| (k.clone(), tag(w, k)))
        .collect()
}

/// Record a state by hand (rule 4); refuses an unknown state, a bad date or a reason under two words.
fn set_state(root: &Path, key: &str, state: &str, date: &str, reason: &str) -> Result<(), String> {
    let path = root.join(ACCESS);
    let mut doc: Value =
        serde_json::from_str(&read_text(&path).map_err(text_err)?).map_err(text_err)?;
    let states: Vec<&str> = doc["states"]
        .as_array()
        .into_iter()
        .flatten()
        .filter_map(|s| s["id"].as_str())
        .collect();
    if !states.contains(&state) {
        return Err(format!(
            "`{state}` is not a state - the states are {} ({ACCESS})",
            states.join(", ")
        ));
    }
    if !DATE.is_match(date).unwrap_or(false) {
        return Err(format!(
            "DATE={} - give the date the evidence was seen, YYYY-MM-DD",
            py_repr(&date.into())
        ));
    }
    if words(reason).len() < 2 {
        return Err("REASON= says what the state rests on, in two words or more - the line or page that shows it".to_owned());
    }
    let mut recorded: BTreeMap<String, Value> = doc["recorded"]
        .as_object()
        .cloned()
        .unwrap_or_default()
        .into_iter()
        .collect();
    let row = json!({"state": state, "date": date, "reason": reason});
    let list = recorded.entry(key.to_owned()).or_insert_with(|| json!([]));
    list.as_array_mut()
        .into_iter()
        .for_each(|a| a.push(row.clone()));
    doc["recorded"] = Value::Object(recorded.into_iter().collect());
    std::fs::write(&path, py_dumps(&doc, 1, false) + "\n").map_err(text_err)
}

fn report_all(w: &World, json_out: bool) -> String {
    let tags = every(w);
    if json_out {
        let map: Map<String, Value> = tags.iter().map(|(k, t)| (k.clone(), t.as_json())).collect();
        return py_dumps(&Value::Object(map), 1, false) + "\n";
    }
    let keyed = tags
        .iter()
        .filter(|(k, _)| !k.starts_with("download:"))
        .count();
    let mut out = format!(
        "access-tags: {keyed} registry keys and {} keyless list entries\n",
        tags.len() - keyed
    );
    for state in &w.order {
        let count = tags.iter().filter(|(_, t)| t.state == *state).count();
        let _ = writeln!(out, "  {state:12} {count}");
    }
    out
}

fn report(args: &[String], root: &Path) -> Result<String, String> {
    let json_out = args.iter().any(|a| a == "--json");
    let inline = args.iter().find_map(|a| a.strip_prefix("--key="));
    let key = inline
        .or_else(|| {
            args.windows(2)
                .find(|w| w[0] == "--key")
                .map(|w| w[1].as_str())
        })
        .unwrap_or("");
    let w = load(root)?;
    if key.is_empty() {
        return Ok(report_all(&w, json_out));
    }
    if !w.keys.contains_key(key)
        && !w.keyless.iter().any(|k| k == key)
        && !w.marks.contains_key(key)
    {
        return Err(format!(
            "no registry key or list entry `{key}` - an entry is `download:<id>`"
        ));
    }
    let t = tag(&w, key);
    Ok(if json_out {
        one_line_utf8(&json!({key: t.as_json()})) + "\n"
    } else {
        format!("{key}: {}\n", t.line())
    })
}

/// `entry-keys <id>`: the registry keys that download-list entry names, as JSON; the door `archive_ops.py` reaches this module by (`ask:449-T80-order`).
fn entry_keys(id: &str, root: &Path) -> Reply {
    let found = load(root).map(|w| w.entry_keys.get(&format!("download:{id}")).cloned());
    match found {
        Err(why) => reply(String::new(), format!("access-tags: REFUSED - {why}\n"), 1),
        Ok(None) => reply(
            String::new(),
            format!("archive: no download-list entry {id} in {CANON}\n"),
            1,
        ),
        Ok(Some(keys)) => reply(one_line_utf8(&json!(keys)) + "\n", String::new(), 0),
    }
}

fn valid_flags(args: &[String]) -> bool {
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--json" => i += 1,
            "--key" if i + 1 < args.len() => i += 2,
            a if a.starts_with("--key=") => i += 1,
            _ => return false,
        }
    }
    true
}

/// `l7r-gate record access-tags ...`.
pub fn cli(args: &[String], root: &Path) -> Reply {
    let rest = args.get(1..).unwrap_or(&[]);
    let done = match (args.first().map(String::as_str), rest) {
        (Some("report"), _) if valid_flags(rest) => report(rest, root),
        (Some("set"), [key, state, date, reason]) => {
            set_state(root, key, state, date, reason).map(|()| {
                format!("access-tags: {key} recorded {state} ({date}) in {ACCESS} - commit it\n")
            })
        }
        (Some("entry-keys"), [id]) => return entry_keys(id, root),
        _ => return reply(String::new(), USAGE.to_owned(), 2),
    };
    match done {
        Ok(stdout) => reply(stdout, String::new(), 0),
        Err(why) => reply(String::new(), format!("access-tags: REFUSED - {why}\n"), 1),
    }
}

#[cfg(test)]
mod tests;
