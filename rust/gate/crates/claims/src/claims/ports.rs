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

use std::collections::{BTreeMap, HashMap, HashSet};
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

/// One entry of the map: the unit a `.py` unit became, and the task that ported it.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Port {
    pub to: String,
    pub by: String,
}

/// `.py` uid -> its port.
pub type Ports = BTreeMap<String, Port>;

/// The map at `root` (none where there is no file); a malformed entry is an error naming the form.
///
/// # Errors
///
/// Where the file is not JSON, or an entry is not `"<path>.py::<qualname>": {"to": "<path>::<qualname>", "by": "<feature> <task>"}`.
pub fn load(root: &Path) -> Result<Ports, Fail> {
    let path = root.join(PORTS);
    if !path.is_file() {
        return Ok(Ports::new());
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
        let (to, by) = (field(v, "to"), field(v, "by"));
        if !from.contains(".py::") || !to.contains("::") || by.trim().is_empty() {
            return Err(format!("{PORTS}: the entry `{from}` is not of the form \"<path>.py::<qualname>\": {{\"to\": \"<path>::<qualname>\", \"by\": \"<feature> <task>\"}}"));
        }
        out.insert(
            from.clone(),
            Port {
                to: to.to_owned(),
                by: by.to_owned(),
            },
        );
    }
    Ok(out)
}

/// What becomes of one claim's row on a mapped unit gone from the tree.
#[derive(Debug, PartialEq, Eq)]
pub enum Fate {
    /// Re-keyed to this key.
    Carried(String),
    /// Dropped: a claim of NONE research whose code is now tooling (`ask:449-T148-claims`).
    Dropped,
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
    match cur.get(&new) {
        Some(row) if row.claim.normalized() == text => Fate::Carried(new),
        Some(row) => Fate::Stuck(format!("unported: {key} - {} carries the label `{label}` but reads `{}`, where the Python's claim reads `{text}`: carry the `Research:` line over as it stands, then `make claims-rekey`", port.to, row.claim.normalized())),
        None if cur.uids().contains(&port.to) => Fate::Stuck(format!("unported: {key} - {} carries no claim `{label}`: carry the Python's `Research:` line onto it as it stands (`/// Research: {text}`), then `make claims-rekey`", port.to)),
        None => Fate::Stuck(format!("unported: {key} - {PORTS} maps its unit to {}, which is no unit the claims walk reads: name the port's `path::qualname` there, then `make claims-rekey`", port.to)),
    }
}

/// What `claims rekey` did with the ports: the keys carried, the keys dropped, and the rows left with their fix.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Rekeyed {
    pub carried: Vec<String>,
    pub dropped: Vec<String>,
    pub stuck: Vec<String>,
}

/// Each claim row on a mapped unit gone from `cur` carried onto its port, or dropped, or left with its fix; `text_of` gives a key's
/// claim text from the merge base, for a row that does not hold it.
pub fn carry(
    cur: &Cur,
    index: &mut Index,
    ports: &Ports,
    text_of: &mut dyn FnMut(&str) -> Option<String>,
) -> Rekeyed {
    let uids = cur.uids();
    let mut out = Rekeyed::default();
    let keys: Vec<String> = index.keys().cloned().collect();
    for key in keys {
        let uid = uid_of(&key);
        let Some(port) = ports.get(uid) else { continue };
        if uids.contains(uid) || is(&index[&key], "verdict", "UNCLAIMED") {
            continue;
        }
        let held = field(&index[&key], "claim").to_owned();
        let text = if held.is_empty() {
            text_of(&key)
        } else {
            Some(held)
        };
        match fate(&key, port, cur, text.as_deref()) {
            Fate::Carried(new) => {
                let mut row = index.shift_remove(&key).unwrap_or_default();
                // a row the port's own check already wrote stands: it judged the new code
                if !index.contains_key(&new) {
                    row["ported"] = json!(key);
                    index.insert(new, row);
                }
                out.carried.push(key);
            }
            Fate::Dropped => {
                index.shift_remove(&key);
                out.dropped.push(key);
            }
            Fate::Stuck(why) => out.stuck.push(why),
        }
    }
    out
}

/// The deferred list (`dev/claims-deferred.json`'s `units` and `keys`) re-keyed with its units' ports: a unit to its port, a key to its
/// port's same label, one ported into a tooling crate dropped; whether it changed.
pub fn carry_deferred(deferred: &mut Value, ports: &Ports, cur: &Cur) -> bool {
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
            match ports.get(uid).filter(|_| !uids.contains(uid)) {
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
    let text = l7r_guard::shared::pyjson::dumps(deferred, Some(1), true) + "\n";
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
    let ports = load(root)?;
    if ports.is_empty() {
        return Ok(Rekeyed::default());
    }
    // the merge base is read only for a row to carry that does not hold its claim's text
    let uids = cur.uids();
    let unheld = index.iter().any(|(k, v)| {
        let uid = uid_of(k);
        ports.contains_key(uid) && !uids.contains(uid) && field(v, "claim").is_empty()
    });
    let texts = if unheld {
        base_texts(reader, root)?
    } else {
        HashMap::new()
    };
    let done = carry(cur, index, &ports, &mut |k: &str| texts.get(k).cloned());
    let path = root.join(super::index::DEFERRED);
    if path.is_file() {
        let mut deferred = Value::Object(super::index::load_map(&path)?);
        if carry_deferred(&mut deferred, &ports, cur) {
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
        l7r_guard::shared::py_text::strip(&crate::record::repo::git(root, args)).to_owned()
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

/// What the push's claims gate reads of the merge base for [`unported`].
pub struct Before<'a> {
    pub index: &'a Index,
    /// Every unit's uid at the merge base (its claims or none).
    pub uids: &'a HashSet<String>,
    /// key -> its claim's normalized line, for every claim at the merge base.
    pub texts: &'a HashMap<String, String>,
}

/// The refusal for each claim of the merge base on a `.py` unit this tree no longer has (`gone` decides, the units of every scope)
/// that no move and no port carried; `index` the tree's.
pub fn unported(
    cur: &Cur,
    index: &Index,
    before: &Before,
    ports: &Ports,
    gone: &mut dyn FnMut(&str) -> bool,
) -> Vec<String> {
    let uids = cur.uids();
    let moved: HashSet<String> = super::index::moved(cur, before.index)
        .into_values()
        .collect();
    let mut out = Vec::new();
    for (key, was) in before.index {
        let uid = uid_of(key);
        if !uid.contains(".py::")
            || is(was, "verdict", "UNCLAIMED")
            || !before.uids.contains(uid)
            || uids.contains(uid)
            || moved.contains(key)
            || !gone(uid)
        {
            continue;
        }
        let Some(port) = ports.get(uid) else {
            out.push(format!("unported: {key} - its unit {uid} is deleted, and {PORTS} maps it to no unit: if it was ported, add `\"{uid}\": {{\"to\": \"rust/<crate>/src/<file>.rs::<item>\", \"by\": \"<feature> <task>\"}}` under its `ports` and run `make claims-rekey`; a claim the map cannot carry is a new ask (`make arbiter-ask`), never a hand rewrite (ask:449-phase4-slices Q10)"));
            continue;
        };
        let held = field(was, "claim");
        let text = if held.is_empty() {
            before.texts.get(key).map(String::as_str)
        } else {
            Some(held)
        };
        let rekey = format!("unported: {key} - its port is mapped but its row not yet carried: `make claims-rekey` (make land runs it)");
        match fate(key, port, cur, text) {
            // the old row still in the index is what `rekey` carries; one already gone (a record pruned it) leaves the port's claim
            // owed as new, which the claims round checks in full - no carry is left to run
            Fate::Carried(_) | Fate::Dropped if index.contains_key(key) => out.push(rekey),
            Fate::Carried(_) | Fate::Dropped => {}
            Fate::Stuck(why) => out.push(why),
        }
    }
    out
}

#[cfg(test)]
mod flow;
#[cfg(test)]
mod tests;
