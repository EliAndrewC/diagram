//! A claim carried across a port (feature 449 T166, `ask:449-phase4-slices` Q10: "claims stay keyed to .py units until the cut that
//! deletes those units, and are re-keyed there with claims carry. That cut's landing runs the claims check and lands no claim still
//! keyed to a deleted unit. A claim that carry cannot map is a new ask, never a hand rewrite."). `claims rekey` carries a row whose unit
//! moved with its code intact by an equal code fingerprint ([`super::index::moved`]), which a deleted `.py` unit and its Rust port never
//! share: before T166 a slice that ported and deleted Python stranded its 367 claims' rows, and the next record dropped them.
//!
//! THE PORT MAP, `dev/claims-ports.json` (one shared file beside the index, the deferred list and the page snapshots it re-keys): a slice
//! declares under `ports` which `.py` unit (`path::qualname`) became which unit (`to`, a Rust item's `path::qualname`) and in which task
//! (`by`). One file and not one a slice under `specs/449-rust-codebase/`: the claims tools read a fixed path at every tree (the merge
//! base's too) and the push's claims gate judges it, as they do the index; a port of another feature uses the same map; and `by` names
//! each entry's slice.
//!
//! THE CARRY (`claims rekey`, which `make land` runs before its gate): each index row of a claim on a mapped unit the tree no longer has
//! is re-keyed onto the same label of its `to` unit, provided that unit carries the claim's own text (its `Research:` line carried by
//! the port, read from the row or, for a row recorded before the index held the text, from the merge base's unit) - else the row stays
//! and the carry says what to fix. The row keeps its verdict, note and pages as the record of what was checked, and `ported`, its old
//! key; its code is still the Python's, so the claim is OWED a fresh check of the new code (`ported`, a full check, never a triage or a
//! counter clear), which the landing's claims round gives it. A claim of NONE research whose `to` is in a tooling crate the walk prunes
//! is dropped, as `ask:449-T148-claims` ruled; one citing research there is a new ask. The deferred list follows its units.
//!
//! THE REFUSAL ([`unported`], at the push's claims gate): a claim of the merge base on a `.py` unit the tree no longer has, carried by no
//! move and no port, is refused with the fix - so no claim is dropped by a record that prunes rows of units gone.
//!
//! A RETIRED UNIT (feature 449 T184, `ask:449-T184-elongated-retired`, `ask:449-T184-elongated-retired-2`): a `.py` unit deleted because
//! the research overruled its rule has no port to go to, so the map's `retired` names it with the task that removed it (`by`), the
//! research page that overrules it (`page`, a file in the tree), why, and the claims round's finding against it (`finding`, a claim key
//! of the same label). The push lets its claims go only where the unit is gone and the merge base's row of that `finding` reads DRIFTED
//! or MISLABELED - the evidence an ask would read; the unit's own rows may read any verdict, and anything else is a new ask. `claims
//! rekey` drops its rows and its deferred entries.
//!
//! A REBUILT FILE (feature 449 T152, `ask:449-T152-rebuilt-claims`): a third outcome beside a port and a retirement, so "a claim that
//! carry cannot map" names it before it becomes a new ask. A `.py` file a phase task deleted after rebuilding its job from a SOUND
//! derivation, blind to the old code ("An algorithm is rebuilt, never ported"), has no port by design and was not overruled by
//! research; the map's `rebuilt` names the FILE with that task (`by`), the Rust module or directory doing its job now (`as`) and the
//! task's derivation - the file on the task's `old-code:` line, the derivation its `derivation:` line and in the tree. A unit with its
//! own `ports` or `retired` entry is handled there; `rebuilt` covers the file's other units. The push refuses a rebuilt file still in
//! the tree and lets the old claims go only once nothing under `as` is owed; `claims rekey` drops their rows and deferred entries.
//! No old claim is matched to the new code: its own `Research:` lines, each checked fresh, are the bar ([`rebuilt`]).
//!
//! THREE MORE OUTCOMES OF A PORT (feature 449 T212, the round arbiter's `ask:449-T212-stranded-claims`), each gated exactly so:
//! - A RELABELED claim ([`settle`]): a ports entry marked `"relabeled": true` lets a claim its port does not carry word for word go -
//!   dropped, not carried - only where the merge base's row of that Python claim reads MISLABELED and a target carries a claim of the
//!   same label with a checked row: the port wrote the claims round's correction, and the corrected line was itself checked.
//! - A SPLIT unit ([`fate`]): a ports entry's `to` may be a list - a Python unit whose claims went to several Rust items - and each claim
//!   is carried to the one target whose unit carries its own text.
//! - A NONE claim LEFT BEHIND ([`orphans`]): a claim of NONE research whose unit is gone and whose file a port's cut deleted (no unit of
//!   the file in the tree, a ports entry on one of its units) is dropped only when every other claim of that file is carried or dropped
//!   by these rules - the Python's own literals (a regex group, a memo's size) that no port has. One citing research is never dropped,
//!   nor one a target of its port carries under its own label (a relabel, rule A's under A's gate); either holds its whole file.
//!
//! Anything else is still a new ask: a Python row not MISLABELED, a claim text on no listed target, a stranded claim citing research.

pub mod rebuilt;

use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::path::Path;

use serde_json::{json, Value};

use super::grammar::parse_claim;
use super::index::{field, is, Cur, Index};
use super::units::walked;
use crate::record::repo::{fail, read_text, Fail};

/// The port map's path.
pub const PORTS: &str = "dev/claims-ports.json";
/// Why a carried row is owed: its code changed language, so its check is a full one (Q10: "That cut's landing runs the claims check").
pub const PORTED: &str = "ported";

/// One entry of the map: the unit a `.py` unit became (`to`, the first of a list `to` names, the rest in `also`), the task that ported
/// it, and whether its port wrote a claims round's correction of a claim's label (`relabeled`, `ask:449-T212-stranded-claims`).
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Port {
    pub to: String,
    pub by: String,
    pub also: Vec<String>,
    pub relabeled: bool,
}

impl Port {
    /// Every unit the entry names, `to` first.
    #[must_use]
    pub fn targets(&self) -> Vec<&str> {
        std::iter::once(self.to.as_str())
            .chain(self.also.iter().map(String::as_str))
            .collect()
    }
}

/// `.py` uid -> its port.
pub type Ports = BTreeMap<String, Port>;

/// One `retired` entry: a `.py` unit deleted, not ported, because the research overruled its rule (`ask:449-T184-elongated-retired`).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Retired {
    pub by: String,
    /// The research page that overrules the unit's rule, `research/questions/<file>.html`.
    pub page: String,
    pub why: String,
    /// The key (`<path>::<qualname>#<label>`) of the claims round's finding that the research is against the rule.
    pub finding: String,
}

/// `.py` uid -> its retirement.
pub type Retirements = BTreeMap<String, Retired>;

/// The whole map: its ports, its retired units and its rebuilt files.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Map {
    pub ports: Ports,
    pub retired: Retirements,
    pub rebuilt: rebuilt::Rebuilds,
}

impl From<Ports> for Map {
    fn from(ports: Ports) -> Self {
        Self {
            ports,
            retired: Retirements::new(),
            rebuilt: rebuilt::Rebuilds::new(),
        }
    }
}

/// The verdicts of a retirement's `finding` row at the merge base that let its claims go: the claims round found the research against the
/// rule, DRIFTED or MISLABELED, read off that row alone - never the retired unit's own rows, which may read any verdict
/// (`ask:449-T184-elongated-retired`, `ask:449-T184-elongated-retired-2`; any other verdict is a new ask).
pub const RETIRABLE: &[&str] = &["DRIFTED", "MISLABELED"];

/// The map at `root` (none where there is no file); a malformed entry is an error naming the form.
///
/// # Errors
///
/// Where the file is not JSON, or an entry is not `"<path>.py::<qualname>": {"to": "<path>::<qualname>", "by": "<feature> <task>"}`,
/// or a `retired` entry is not `"<path>.py::<qualname>": {"by": ..., "page": "research/questions/<file>.html", "why": ..., "finding":
/// "<path>::<qualname>#<label>"}`, names a
/// page the tree does not hold, or retires a unit `ports` also maps; or a `rebuilt` entry is not of its form or not tied to its phase
/// task ([`rebuilt`]).
pub fn load(root: &Path) -> Result<Map, Fail> {
    let path = root.join(PORTS);
    if !path.is_file() {
        return Ok(Map::default());
    }
    let doc: Value = serde_json::from_str(&read_text(&path)?)
        .map_err(|e| format!("json.decoder.JSONDecodeError: {PORTS}: {e}"))?;
    let mut out = Ports::new();
    let empty = serde_json::Map::new();
    for (from, v) in doc
        .get("ports")
        .and_then(Value::as_object)
        .unwrap_or(&empty)
    {
        let by = field(v, "by");
        // `to` one unit or a list of them (a split unit, `ask:449-T212-stranded-claims`)
        let to: Vec<&str> = match v.get("to") {
            Some(Value::Array(list)) => list
                .iter()
                .map(|t| t.as_str().unwrap_or_default())
                .collect(),
            _ => vec![field(v, "to")],
        };
        let relabeled = match v.get("relabeled") {
            None => Some(false),
            Some(flag) => flag.as_bool(),
        };
        let formed = from.contains(".py::")
            && !to.is_empty()
            && to.iter().all(|t| t.contains("::"))
            && !by.trim().is_empty();
        let (Some(relabeled), true) = (relabeled, formed) else {
            return Err(format!("{PORTS}: the entry `{from}` is not of the form \"<path>.py::<qualname>\": {{\"to\": \"<path>::<qualname>\" (or a list of them), \"by\": \"<feature> <task>\"}} (and \"relabeled\": true where its port corrected a MISLABELED claim)"));
        };
        out.insert(
            from.clone(),
            Port {
                to: to[0].to_owned(),
                by: by.to_owned(),
                also: to[1..].iter().map(|t| (*t).to_owned()).collect(),
                relabeled,
            },
        );
    }
    let retired = load_retired(root, &doc, &out)?;
    let rebuilt = rebuilt::load_rebuilt(root, &doc)?;
    Ok(Map {
        ports: out,
        retired,
        rebuilt,
    })
}

/// The map's `retired` entries, each held to its form, its page a file at `root` and its unit mapped by no port.
fn load_retired(root: &Path, doc: &Value, ports: &Ports) -> Result<Retirements, Fail> {
    let mut out = Retirements::new();
    let empty = serde_json::Map::new();
    for (uid, v) in doc
        .get("retired")
        .and_then(Value::as_object)
        .unwrap_or(&empty)
    {
        let (by, page, why) = (field(v, "by"), field(v, "page"), field(v, "why"));
        let finding = field(v, "finding");
        let found = finding.split_once("::").is_some_and(|(path, rest)| {
            !path.is_empty()
                && rest
                    .split_once('#')
                    .is_some_and(|(q, l)| !q.is_empty() && !l.is_empty())
        });
        let paged = page.starts_with("research/questions/")
            && Path::new(page).extension().is_some_and(|e| e == "html")
            && !page.contains("..");
        if !uid.contains(".py::")
            || by.trim().is_empty()
            || why.trim().is_empty()
            || !paged
            || !found
        {
            return Err(format!("{PORTS}: the retired entry `{uid}` is not of the form \"<path>.py::<qualname>\": {{\"by\": \"<feature> <task>\", \"page\": \"research/questions/<file>.html\", \"why\": \"<one line>\", \"finding\": \"<path>::<qualname>#<label>\"}} (`finding` the key of the claims round's DRIFTED or MISLABELED finding against its rule)"));
        }
        if !root.join(page).is_file() {
            return Err(format!("{PORTS}: the retired entry `{uid}` names the page {page}, which is no file in the tree: name the research page that overrules its rule (`ls research/questions/`)"));
        }
        if ports.contains_key(uid) {
            return Err(format!("{PORTS}: `{uid}` is both retired and under `ports`: a unit is ported or retired, never both - keep the one that is true"));
        }
        out.insert(
            uid.clone(),
            Retired {
                by: by.to_owned(),
                page: page.to_owned(),
                why: why.to_owned(),
                finding: finding.to_owned(),
            },
        );
    }
    Ok(out)
}

/// What becomes of one claim's row on a mapped unit gone from the tree.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Fate {
    /// Re-keyed to this key.
    Carried(String),
    /// Dropped: a claim of NONE research whose code is now tooling (`ask:449-T148-claims`).
    Dropped,
    /// Dropped, not carried: a MISLABELED claim its `relabeled` port corrected, the corrected claim's checked key here
    /// (`ask:449-T212-stranded-claims`).
    Relabeled(String),
    /// Left as it stands, and why, with the fix.
    Stuck(String),
}

fn uid_of(key: &str) -> &str {
    key.rsplit_once('#').map_or(key, |p| p.0)
}

/// Is `path` code the claims walk prunes - a tooling crate's, which holds no claim (feature 449 T146, T165)?
fn tooling(path: &str) -> bool {
    path.strip_prefix("rust/")
        .is_some_and(|inner| !walked(inner))
}

/// The fate of the row `key` on a unit gone from `cur`, ported as `port`; `text` the claim's normalized line, where it can be read.
#[must_use]
pub fn fate(key: &str, port: &Port, cur: &Cur, text: Option<&str>) -> Fate {
    let label = key.rsplit_once('#').map_or("", |p| p.1);
    let new = format!("{}#{label}", port.to);
    let Some(text) = text else {
        return Fate::Stuck(format!("unported: {key} - its claim's text is in neither its index row nor the merge base, so no port can be checked to carry it: a new ask (`make arbiter-ask`), never a hand rewrite (ask:449-phase4-slices Q10)"));
    };
    let to_path = port.to.split_once("::").map_or("", |p| p.0);
    if tooling(to_path) {
        if parse_claim(text).is_ok_and(|c| c.backing == "NONE") {
            return Fate::Dropped;
        }
        return Fate::Stuck(format!("unported: {key} - mapped to {}, a tooling crate the claims walk prunes, and it cites research: a new ask (`make arbiter-ask`), never a hand rewrite (ask:449-T148-claims drops only a claim of NONE research)", port.to));
    }
    // a split unit's claim goes to the one target carrying its own text (`ask:449-T212-stranded-claims`)
    let mut carrying = port
        .targets()
        .into_iter()
        .map(|t| format!("{t}#{label}"))
        .filter(|k| cur.get(k).is_some_and(|row| row.claim.normalized() == text));
    if let Some(at) = carrying.next() {
        return Fate::Carried(at);
    }
    if !port.also.is_empty() {
        return Fate::Stuck(format!("unported: {key} - its claim's text (`{text}`) is on none of its targets ({}): a new ask (`make arbiter-ask`), never a hand rewrite (ask:449-T212-stranded-claims)", port.targets().join(", ")));
    }
    match cur.get(&new) {
        Some(row) => Fate::Stuck(format!("unported: {key} - {} carries the label `{label}` but reads `{}`, where the Python's claim reads `{text}`: carry the `Research:` line over as it stands, then `make claims-rekey`", port.to, row.claim.normalized())),
        None if cur.uids().contains(&port.to) => Fate::Stuck(format!("unported: {key} - {} carries no claim `{label}`: carry the Python's `Research:` line onto it as it stands (`/// Research: {text}`), then `make claims-rekey`", port.to)),
        None => Fate::Stuck(format!("unported: {key} - {PORTS} maps its unit to {}, which is no unit the claims walk reads: name the port's `path::qualname` there, then `make claims-rekey`", port.to)),
    }
}

/// [`fate`], and where it leaves a claim stuck on a port marked `relabeled`, rule A (`ask:449-T212-stranded-claims`): the claim goes, not
/// carried, only where `verdict` - the merge base's row of it - reads MISLABELED and one of its targets carries a claim of its label
/// whose row in `index` is checked; else the stuck claim names which of the three failed.
#[must_use]
pub fn settle(
    key: &str,
    port: &Port,
    cur: &Cur,
    index: &Index,
    verdict: &str,
    text: Option<&str>,
) -> Fate {
    let found = fate(key, port, cur, text);
    if !port.relabeled || !matches!(found, Fate::Stuck(_)) {
        return found;
    }
    let label = key.rsplit_once('#').map_or("", |p| p.1);
    let ask = "a new ask (`make arbiter-ask`), never a hand rewrite (ask:449-T212-stranded-claims)";
    let Some(at) = port
        .targets()
        .into_iter()
        .map(|t| format!("{t}#{label}"))
        .find(|k| cur.get(k).is_some())
    else {
        return Fate::Stuck(format!("unported: {key} - its port is marked `relabeled`, but none of its targets ({}) carries a claim `{label}`: {ask}", port.targets().join(", ")));
    };
    if verdict != "MISLABELED" {
        let read = Some(verdict)
            .filter(|v| !v.is_empty())
            .unwrap_or("no verdict");
        return Fate::Stuck(format!("unported: {key} - its port is marked `relabeled`, but the merge base's row of it reads {read}, where only MISLABELED lets it go: {ask}"));
    }
    if index
        .get(&at)
        .is_none_or(|row| field(row, "verdict").is_empty())
    {
        return Fate::Stuck(format!("unported: {key} - its port is marked `relabeled`, but {at} has no checked row: check it in the claims round (`make claims-owed`), then `make claims-rekey`"));
    }
    Fate::Relabeled(at)
}

/// One claim of a gone `.py` unit as the two passes read it: its key, what its port made of it (None: no port names its unit) and its
/// claim's text where it can be read.
pub type Settled = (String, Option<Fate>, Option<String>);

/// Rule C (`ask:449-T212-stranded-claims`): the keys of the claims of NONE research left on no unit - stuck, or on no port - whose file
/// a port's cut deleted (no unit of it in `cur`, a ports entry on one of its units), where every other claim of the file in `settled`
/// is carried or dropped. A claim one of its port's targets carries under its own label is no claim left on no unit - its label went
/// with the port, so it is rule A's to let go, under A's gate, or a new ask - and like a claim citing research it holds its whole file.
#[must_use]
pub fn orphans(settled: &[Settled], cur: &Cur, map: &Map) -> HashSet<String> {
    let file_of = |k: &str| k.split_once("::").map_or(k, |p| p.0).to_owned();
    let in_tree: HashSet<String> = cur.uids().iter().map(|u| file_of(u)).collect();
    let ported: HashSet<String> = map.ports.keys().map(|u| file_of(u)).collect();
    let candidate = |(k, _, t): &Settled| {
        let label = k.rsplit_once('#').map_or("", |p| p.1);
        let labeled = map.ports.get(uid_of(k)).is_some_and(|p| {
            p.targets()
                .into_iter()
                .any(|to| cur.get(&format!("{to}#{label}")).is_some())
        });
        let none = t
            .as_deref()
            .is_some_and(|t| parse_claim(t).is_ok_and(|c| c.backing == "NONE"));
        none && !labeled
    };
    let left = |(_, f, _): &Settled| matches!(f, None | Some(Fate::Stuck(_)));
    let held: HashSet<String> = settled
        .iter()
        .filter(|s| left(s) && !candidate(s))
        .map(|(k, _, _)| file_of(k))
        .collect();
    settled
        .iter()
        .filter(|s| {
            let file = file_of(&s.0);
            left(s)
                && candidate(s)
                && ported.contains(&file)
                && !in_tree.contains(&file)
                && !held.contains(&file)
        })
        .map(|(k, _, _)| k.clone())
        .collect()
}

/// What `claims rekey` did with the ports: the keys carried, the keys dropped, the rows left with their fix, the keys of a retired
/// unit dropped with the pages that overrule them, and the keys of a rebuilt file's units dropped with the derivations rebuilt from.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Rekeyed {
    pub carried: Vec<String>,
    pub dropped: Vec<String>,
    pub stuck: Vec<String>,
    pub retired: Vec<String>,
    pub retired_pages: BTreeSet<String>,
    pub rebuilt: Vec<String>,
    pub rebuilt_derivations: BTreeSet<String>,
    /// Rule A's keys, dropped (`ask:449-T212-stranded-claims`).
    pub relabeled: Vec<String>,
    /// Rule C's keys, dropped.
    pub orphaned: Vec<String>,
}

/// Each claim row on a mapped unit gone from `cur` carried onto its port, or dropped, or left with its fix, and each on a retired unit
/// or on a unit of a rebuilt file (one no longer in the tree) gone dropped, and rule C's NONE claims left behind dropped ([`orphans`]);
/// `text_of` gives a key's claim text from the merge base, for a row that does not hold it.
pub fn carry(
    cur: &Cur,
    index: &mut Index,
    map: &Map,
    text_of: &mut dyn FnMut(&str) -> Option<String>,
) -> Rekeyed {
    let uids = cur.uids();
    let ported: HashSet<&str> = map.ports.keys().map(|u| file_part(u)).collect();
    let mut out = Rekeyed::default();
    let mut settled: Vec<Settled> = Vec::new();
    let keys: Vec<String> = index.keys().cloned().collect();
    for key in keys {
        let uid = uid_of(&key);
        if uids.contains(uid) || is(&index[&key], "verdict", "UNCLAIMED") {
            continue;
        }
        if let Some(gone) = map.retired.get(uid) {
            index.shift_remove(&key);
            out.retired_pages.insert(gone.page.clone());
            out.retired.push(key);
            continue;
        }
        let port = map.ports.get(uid);
        if port.is_none() {
            if let Some(rb) = rebuilt::of(&map.rebuilt, uid).filter(|rb| !rb.present) {
                index.shift_remove(&key);
                out.rebuilt_derivations.insert(rb.derivation.clone());
                out.rebuilt.push(key);
                continue;
            }
            // an unmapped unit is rule C's business only in a file a port's cut deleted
            if !uid.contains(".py::") || !ported.contains(file_part(uid)) {
                continue;
            }
        }
        let held = field(&index[&key], "claim").to_owned();
        let text = if held.is_empty() {
            text_of(&key)
        } else {
            Some(held)
        };
        let verdict = field(&index[&key], "verdict").to_owned();
        let found = port.map(|p| settle(&key, p, cur, index, &verdict, text.as_deref()));
        settled.push((key, found, text));
    }
    let orphaned = orphans(&settled, cur, map);
    for (key, found, _) in settled {
        if orphaned.contains(&key) {
            index.shift_remove(&key);
            out.orphaned.push(key);
            continue;
        }
        match found {
            None => {}
            Some(Fate::Carried(new)) => {
                let mut row = index.shift_remove(&key).unwrap_or_default();
                // a row the port's own check already wrote stands: it judged the new code
                if !index.contains_key(&new) {
                    row["ported"] = json!(key);
                    index.insert(new, row);
                }
                out.carried.push(key);
            }
            Some(Fate::Dropped) => {
                index.shift_remove(&key);
                out.dropped.push(key);
            }
            Some(Fate::Relabeled(_)) => {
                index.shift_remove(&key);
                out.relabeled.push(key);
            }
            Some(Fate::Stuck(why)) => out.stuck.push(why),
        }
    }
    out
}

/// A key's or uid's file: what precedes its `::`.
fn file_part(key: &str) -> &str {
    key.split_once("::").map_or(key, |p| p.0)
}

/// The deferred list (`dev/claims-deferred.json`'s `units` and `keys`) re-keyed with its units' ports: a unit to its port, a key to its
/// port's same label, one ported into a tooling crate, retired or of a rebuilt file dropped; whether it changed.
pub fn carry_deferred(deferred: &mut Value, map: &Map, cur: &Cur) -> bool {
    let uids = cur.uids();
    let mut changed = false;
    for part in ["units", "keys"] {
        let Some(list) = deferred.get_mut(part).and_then(Value::as_array_mut) else {
            continue;
        };
        let mut kept = Vec::new();
        for v in list.drain(..) {
            let entry = v.as_str().unwrap_or_default().to_owned();
            let uid = uid_of(&entry);
            let rebuilt = !map.ports.contains_key(uid)
                && rebuilt::of(&map.rebuilt, uid).is_some_and(|rb| !rb.present);
            if (map.retired.contains_key(uid) || rebuilt) && !uids.contains(uid) {
                changed = true;
                continue;
            }
            match map.ports.get(uid).filter(|_| !uids.contains(uid)) {
                None => kept.push(v),
                Some(port) => {
                    changed = true;
                    if !tooling(port.to.split_once("::").map_or("", |p| p.0)) {
                        kept.push(json!(format!("{}{}", port.to, &entry[uid.len()..])));
                    }
                }
            }
        }
        *list = kept;
    }
    changed
}

/// The deferred list written back as it is kept: `json.dumps(indent=1)`, its keys in their order.
///
/// # Errors
///
/// Where the file cannot be written.
pub fn save_deferred(root: &Path, deferred: &Value) -> Result<(), Fail> {
    let text = l7r_shared::pyjson::dumps(deferred, Some(1), true) + "\n";
    std::fs::write(root.join(super::index::DEFERRED), text).map_err(fail)
}

/// `claims rekey`'s ports at `root`: [`carry`] over `index`, a row without its claim's text read from the merge base with origin/main
/// (HEAD where there is none) - built once, and only for such a row - and the deferred list re-keyed and written where it moved.
///
/// # Errors
///
/// Where the map, the base or the deferred list cannot be read or written.
pub fn rekey_ports(
    reader: &mut super::scope::Reader,
    root: &Path,
    cur: &Cur,
    index: &mut Index,
) -> Result<Rekeyed, Fail> {
    let map = load(root)?;
    if map.ports.is_empty() && map.retired.is_empty() && map.rebuilt.is_empty() {
        return Ok(Rekeyed::default());
    }
    // the merge base is read only for a row to carry that does not hold its claim's text
    let uids = cur.uids();
    let unheld = index.iter().any(|(k, v)| {
        let uid = uid_of(k);
        let in_cut = map.ports.keys().any(|u| file_part(u) == file_part(uid));
        (map.ports.contains_key(uid) || in_cut)
            && !uids.contains(uid)
            && field(v, "claim").is_empty()
    });
    let texts = if unheld {
        base_texts(reader, root)?
    } else {
        HashMap::new()
    };
    let done = carry(cur, index, &map, &mut |k: &str| texts.get(k).cloned());
    let path = root.join(super::index::DEFERRED);
    if path.is_file() {
        let mut deferred = Value::Object(super::index::load_map(&path)?);
        if carry_deferred(&mut deferred, &map, cur) {
            save_deferred(root, &deferred)?;
        }
    }
    Ok(done)
}

/// What `claims rekey` says of its ports, printed only where it did something; its exit: 1 where a row is left stuck, else 0.
pub fn say(done: &Rekeyed, o: &mut super::commands::Out) -> i32 {
    if !done.carried.is_empty() || !done.dropped.is_empty() {
        o.say(&format!("claims-rekey: {} claim row(s) carried to their port ({PORTS}), each owed a full check of its new code ({PORTED}); {} dropped, a claim of NONE research ported into a tooling crate (ask:449-T148-claims)", done.carried.len(), done.dropped.len()));
    }
    if !done.relabeled.is_empty() {
        o.say(&format!("claims-rekey: {} claim row(s) of a `relabeled` port dropped, not carried: each MISLABELED at the merge base, its corrected claim checked on its port (ask:449-T212-stranded-claims)", done.relabeled.len()));
    }
    if !done.orphaned.is_empty() {
        o.say(&format!("claims-rekey: {} claim row(s) of NONE research dropped, left on no unit in a file a port's cut deleted whose every other claim was carried or dropped (ask:449-T212-stranded-claims)", done.orphaned.len()));
    }
    if !done.retired.is_empty() {
        let pages: Vec<&str> = done.retired_pages.iter().map(String::as_str).collect();
        o.say(&format!("claims-rekey: {} claim row(s) of a retired unit dropped ({PORTS}'s `retired`), its rule overruled by {} (ask:449-T184-elongated-retired)", done.retired.len(), pages.join(", ")));
    }
    if !done.rebuilt.is_empty() {
        let derivations: Vec<&str> = done
            .rebuilt_derivations
            .iter()
            .map(String::as_str)
            .collect();
        o.say(&format!("claims-rekey: {} claim row(s) of a rebuilt file dropped ({PORTS}'s `rebuilt`), its job rebuilt from {}, the rebuilt code's own claims each checked fresh (ask:449-T152-rebuilt-claims)", done.rebuilt.len(), derivations.join(", ")));
    }
    for why in &done.stuck {
        o.say(&format!("claims-rekey: {why}"));
    }
    i32::from(!done.stuck.is_empty())
}

/// key -> its claim's normalized line for every claim at the merge base with origin/main, or HEAD.
fn base_texts(
    reader: &mut super::scope::Reader,
    root: &Path,
) -> Result<HashMap<String, String>, Fail> {
    let git = |args: &[&str]| {
        l7r_shared::py_text::strip(&crate::record::repo::git(root, args)).to_owned()
    };
    let mut base = git(&["merge-base", "HEAD", "origin/main"]);
    if base.is_empty() {
        base = git(&["rev-parse", "HEAD"]);
    }
    if base.is_empty() {
        return Ok(HashMap::new());
    }
    let tmp = super::temp_dir("ports");
    std::fs::create_dir_all(&tmp).map_err(fail)?;
    super::report::base_tree("git", root, &base, &tmp)?;
    Ok(super::scope::all_units(reader, &tmp, true, true)?
        .iter()
        .flat_map(|(u, _)| u.claims.iter().map(|c| (u.key(c), c.normalized())))
        .collect())
}

/// What the push's claims gate reads of the merge base for [`unported`], and the claims the tree owes.
pub struct Before<'a> {
    pub index: &'a Index,
    /// Every unit's uid at the merge base (its claims or none).
    pub uids: &'a HashSet<String>,
    /// key -> its claim's normalized line, for every claim at the merge base.
    pub texts: &'a HashMap<String, String>,
    /// The keys the tree owes a check (`make claims-owed`): a rebuilt file's old claims wait on those under its `as` paths.
    pub owed: &'a [String],
}

/// The refusal for each claim of the merge base on a `.py` unit this tree no longer has (`gone` decides, the units of every scope)
/// that no move, no port, no retirement and no rebuild carried; `index` the tree's. A retired unit is refused while it is still in the
/// tree, and its claim where its `finding` is not a merge-base row of the same label the claims round found DRIFTED or MISLABELED
/// (`ask:449-T184-elongated-retired-2`); a rebuilt file while it is still in the tree, and its units' claims while a claim under its
/// `as` paths is owed ([`rebuilt::refusals`], `ask:449-T152-rebuilt-claims`).
pub fn unported(
    cur: &Cur,
    index: &Index,
    before: &Before,
    map: &Map,
    gone: &mut dyn FnMut(&str) -> bool,
) -> Vec<String> {
    let uids = cur.uids();
    let moved: HashSet<String> = super::index::moved(cur, before.index)
        .into_values()
        .collect();
    // each refusal in the merge base's order: a line already written, or a claim of a gone unit settled in two passes (rule C reads
    // the whole file first, `ask:449-T212-stranded-claims`)
    let mut lines: Vec<Result<String, Settled>> = Vec::new();
    let mut stranded: BTreeMap<String, Vec<String>> = BTreeMap::new();
    // a retired unit still in the tree: `gone` is asked only where its claims are not (it answers for every scope's units)
    let mut present: BTreeSet<&str> = map
        .retired
        .keys()
        .map(String::as_str)
        .filter(|u| uids.contains(*u))
        .collect();
    for (key, was) in before.index {
        let uid = uid_of(key);
        if let Some(gone_by) = map.retired.get(uid) {
            if present.contains(uid)
                || is(was, "verdict", "UNCLAIMED")
                || !before.uids.contains(uid)
                || moved.contains(key)
            {
                continue;
            }
            if !gone(uid) {
                present.insert(map.retired.get_key_value(uid).map_or(uid, |p| p.0.as_str()));
                continue;
            }
            if let Some(why) = retired_refusal(key, gone_by, before.index, index) {
                lines.push(Ok(why));
            }
            continue;
        }
        if !uid.contains(".py::")
            || is(was, "verdict", "UNCLAIMED")
            || !before.uids.contains(uid)
            || uids.contains(uid)
            || moved.contains(key)
            || !gone(uid)
        {
            continue;
        }
        let held = field(was, "claim");
        let text = if held.is_empty() {
            before.texts.get(key).cloned()
        } else {
            Some(held.to_owned())
        };
        let Some(port) = map.ports.get(uid) else {
            if rebuilt::of(&map.rebuilt, uid).is_some() {
                let file = uid.split_once("::").map_or(uid, |p| p.0);
                stranded
                    .entry(file.to_owned())
                    .or_default()
                    .push(key.clone());
                continue;
            }
            lines.push(Err((key.clone(), None, text)));
            continue;
        };
        let found = settle(
            key,
            port,
            cur,
            index,
            field(was, "verdict"),
            text.as_deref(),
        );
        lines.push(Err((key.clone(), Some(found), text)));
    }
    let settled: Vec<Settled> = lines.iter().filter_map(|l| l.clone().err()).collect();
    let orphaned = orphans(&settled, cur, map);
    let mut out = Vec::new();
    for line in lines {
        let (key, found, _) = match line {
            Ok(why) => {
                out.push(why);
                continue;
            }
            Err(claim) => claim,
        };
        let uid = uid_of(&key);
        let rekey = format!("unported: {key} - its port is mapped but its row not yet carried: `make claims-rekey` (make land runs it)");
        match found {
            // the old row still in the index is what `rekey` carries or drops; one already gone (a record pruned it, or rekey dropped
            // it) leaves nothing to run - a carried claim's port owed as new, which the claims round checks in full
            _ if orphaned.contains(&key) && index.contains_key(&key) => out.push(rekey),
            _ if orphaned.contains(&key) => {}
            Some(Fate::Carried(_) | Fate::Dropped | Fate::Relabeled(_)) if index.contains_key(&key) => out.push(rekey),
            Some(Fate::Carried(_) | Fate::Dropped | Fate::Relabeled(_)) => {}
            Some(Fate::Stuck(why)) => out.push(why),
            None => out.push(format!("unported: {key} - its unit {uid} is deleted, and {PORTS} maps it to no unit: if it was ported, add `\"{uid}\": {{\"to\": \"rust/<crate>/src/<file>.rs::<item>\", \"by\": \"<feature> <task>\"}}` under its `ports` and run `make claims-rekey`; if the research overruled its rule, name it under `retired` with the `finding` key whose claims round found it DRIFTED or MISLABELED (`{{\"by\": \"<feature> <task>\", \"page\": \"research/questions/<file>.html\", \"why\": \"<one line>\", \"finding\": \"<path>::<qualname>#<label>\"}}`, ask:449-T184-elongated-retired-2); if a phase task deleted its file after rebuilding its job from a derivation, name the file under `rebuilt` (`\"<path>.py\": {{\"by\": \"<feature> <task>\", \"as\": \"<the Rust module doing its job now>\", \"derivation\": \"<the task's derivation>\"}}`, the file on that task's `old-code:` line, ask:449-T152-rebuilt-claims); a claim the map cannot carry is a new ask (`make arbiter-ask`), never a hand rewrite (ask:449-phase4-slices Q10)")),
        }
    }
    for uid in present {
        out.push(format!("unported: {uid} - retired but still present: {PORTS}'s `retired` names a unit deleted because the research overruled its rule; delete the unit, or take it out of `retired`"));
    }
    out.extend(rebuilt::refusals(
        &map.rebuilt,
        &stranded,
        before.owed,
        &|k| index.contains_key(k),
    ));
    out
}

/// The refusal, if any, of the merge-base claim `key`, whose unit `gone_by` retired and the tree no longer has: a new ask where its
/// `finding` is not in the merge base's index (`base`), reads no verdict of [`RETIRABLE`] or names another label; else `make
/// claims-rekey` while its row stands in the tree's `index`, and none once it is dropped (`ask:449-T184-elongated-retired-2`).
fn retired_refusal(key: &str, gone_by: &Retired, base: &Index, index: &Index) -> Option<String> {
    let label = |k: &str| k.rsplit_once('#').map_or("", |p| p.1).to_owned();
    let why = match base.get(&gone_by.finding) {
        None => Some("is no key of the merge base's index".to_owned()),
        Some(row) if !RETIRABLE.contains(&field(row, "verdict")) => Some(format!(
            "reads {} at the merge base",
            Some(field(row, "verdict"))
                .filter(|v| !v.is_empty())
                .unwrap_or("no verdict")
        )),
        Some(_) if label(&gone_by.finding) != label(key) => Some(format!(
            "names the label `{}`, not `{}`",
            label(&gone_by.finding),
            label(key)
        )),
        Some(_) => None,
    };
    if let Some(why) = why {
        return Some(format!("unported: {key} - {PORTS} retires its unit ({}, {}), but its `finding` {} {why}: retire only a claim whose claims round found the research against it: name that finding's key under `finding`; else a new ask (`make arbiter-ask`) (ask:449-T184-elongated-retired-2)", gone_by.by, gone_by.page, gone_by.finding));
    }
    index.contains_key(key).then(|| format!("unported: {key} - its unit is retired ({}) but its row not yet dropped: `make claims-rekey` (make land runs it)", gone_by.page))
}

#[cfg(test)]
mod flow;
#[cfg(test)]
mod tests;
