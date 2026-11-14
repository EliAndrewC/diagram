//! `l7r-gate measure spec <feature> <name> [args...]`: the past features' measurement scripts that still run, each one command (feature
//! 449 T139, `ask:449-phase3-remainder` Q4: "The measurement scripts the census marks 'works' ... are NOT in the class: they stay phase 3
//! and are ported").
//!
//! One gate command per past measurement, so a recorded `command` in a `specs/*/measurements.json` names the port the way the
//! `record agent-census` and `measure push-check-times` entries already do, and `make figures` re-runs it from the tree's top as it ran
//! the Python. Each port keeps its script's reading of the world: the ones that read their own tree (`Path(__file__)`) read `root`, the
//! tree's top; the ones that read the working directory (261's `pool/hamlets`, 430's `dev/run-log/`) read `cwd`. Wherever the Python
//! raised, the port fails with exit 1, its stdout up to that point kept, as the traceback left it.

mod hamlets;
mod inventory;
mod runs;

use std::path::Path;

use serde_json::{Map, Value};

use super::events::Raised;
use super::reply;
use crate::Reply;

/// What one port printed and the exit it chose, or what it raised.
type Ran = Result<i32, Raised>;

const USAGE: &str = "usage: l7r-gate measure spec 238 inventory-shares [--record] | 239 change-size <from> <to> [--record] | 242 inventory-census [--record | --per-page] | 261 board-well|brook-turn|row-spread [--rev <sha>] <map>... | 261 fixtures-and-board | 430 full-reasons | 432 triage-price\n";

/// `l7r-gate measure spec <feature> <name> [args...]`.
#[must_use]
pub fn cli(args: &[String], root: &Path, cwd: &Path) -> Reply {
    let rest = args.get(2..).unwrap_or(&[]);
    let mut out = String::new();
    let ran = match (
        args.first().map(String::as_str),
        args.get(1).map(String::as_str),
    ) {
        (Some("238"), Some("inventory-shares")) => inventory::shares(rest, root, &mut out),
        (Some("239"), Some("change-size")) => runs::change_size(rest, root, &mut out),
        (Some("242"), Some("inventory-census")) => inventory::census(rest, root, &mut out),
        (Some("261"), Some("board-well")) => hamlets::board_well(rest, cwd, &mut out),
        (Some("261"), Some("brook-turn")) => hamlets::brook_turn(rest, cwd, &mut out),
        (Some("261"), Some("fixtures-and-board")) => hamlets::fixtures_and_board(cwd, &mut out),
        (Some("261"), Some("row-spread")) => hamlets::row_spread(rest, cwd, &mut out),
        (Some("430"), Some("full-reasons")) => runs::full_reasons(cwd, &mut out),
        (Some("432"), Some("triage-price")) => runs::triage_price(root, &mut out),
        _ => return reply(String::new(), USAGE.to_owned(), 2),
    };
    match ran {
        Ok(code) => reply(out, String::new(), code),
        Err(raised) => reply(
            out,
            format!("measure spec {} {}: {raised}\n", args[0], args[1]),
            1,
        ),
    }
}

/// The command a port writes into its own figures under `--record`: the rewritten form of the Python's `COMMAND` (FR-001).
fn command(feature: &str, name: &str, args: &str) -> String {
    format!("scripts/gates/l7r-gate.sh measure spec {feature} {name}{args}")
}

/// `rec = json.loads(path.read_text()) if path.exists() else {}`, each entry set, then `json.dumps(rec, indent=1, sort_keys=True) + "\n"`
/// written: the one way all three recording scripts wrote their feature's `measurements.json`.
fn record(path: &Path, entries: Vec<(&str, Value)>) -> Result<(), Raised> {
    let mut rec = if path.exists() {
        let text = super::events::read_text(path)?;
        match serde_json::from_str::<Value>(&text).map_err(|e| format!("JSONDecodeError: {e}"))? {
            Value::Object(map) => map,
            _ => return Err("TypeError: the figures file holds no object".to_owned()),
        }
    } else {
        Map::new()
    };
    for (key, entry) in entries {
        rec.insert(key.to_owned(), entry);
    }
    let text = l7r_guard::shared::pyjson::dumps(
        &l7r_guard::shared::pyjson::sorted(&Value::Object(rec)),
        Some(1),
        true,
    );
    std::fs::write(path, text + "\n").map_err(|e| format!("OSError: {}: {e}", path.display()))
}

#[cfg(test)]
mod tests;
