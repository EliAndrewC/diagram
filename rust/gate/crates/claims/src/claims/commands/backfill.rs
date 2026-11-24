//! `claims backfill` and `claims backfill-sections`: rows recorded before their pages, or their sections, were snapshotted.

use std::path::Path;

use serde_json::{json, Map, Value};

use super::super::index::{
    live_rows, page_blocks, save_index, save_store, Cur, Index, PageMemo, Store, INDEX, QUESTIONS,
    STORE,
};
use super::super::triage::{keep_sections, section_texts, SECTION_TEXTS};
use super::super::units::sha;
use super::Out;
use crate::record::repo::Fail;
use crate::record::units::digest;

/// Every procedure-section claim re-keyed to its own line's fingerprint without owing it; how many.
pub(super) fn backfill_sections(cur: &Cur, index: &mut Index, store: &mut Store) -> usize {
    let mut n = 0;
    for row in cur.iter() {
        let Some(Value::Object(was)) = index.get_mut(&row.key) else {
            continue;
        };
        if !row.unit.line_keyed() || was.contains_key("section") {
            continue;
        }
        let old = sha(&format!("{}\x1f{}", row.unit.core, row.claim.normalized()));
        if was.get("code").and_then(Value::as_str) == Some(&old) {
            was.insert("code".into(), json!(row.code));
            was.insert("section".into(), json!(row.unit.core));
            store.insert(
                row.unit.core.clone(),
                json!(row
                    .unit
                    .blocks
                    .iter()
                    .map(|b| digest(&[b]))
                    .collect::<Vec<_>>()),
            );
            n += 1;
        }
    }
    n
}

/// Every row checked at today's research given the pages it was checked at, and those pages snapshotted; how many.
pub(super) fn backfill(
    cur: &Cur,
    index: &mut Index,
    qdir: &Path,
    store: &mut Store,
) -> Result<usize, Fail> {
    let mut memo = PageMemo::default();
    let mut n = 0;
    for row in cur.iter() {
        let Some(Value::Object(was)) = index.get_mut(&row.key) else {
            continue;
        };
        if was.contains_key("pages")
            || was.get("research").and_then(Value::as_str) != Some(&row.research)
            || row.research.is_empty()
        {
            continue;
        }
        let mut pages = Map::new();
        for name in super::super::bundle::read_pages(&row.claim, qdir) {
            let (fp, blocks) = page_blocks(&name, qdir, &mut memo)?;
            pages.insert(name.clone(), json!(fp));
            store.insert(
                fp.clone(),
                json!(blocks.iter().map(|(d, _)| d.clone()).collect::<Vec<_>>()),
            );
        }
        was.insert("pages".into(), Value::Object(pages));
        n += 1;
    }
    Ok(n)
}

/// `claims backfill` and `claims backfill-sections`: rows recorded before their pages, or before their sections, were.
pub(super) fn backfill_cmd(
    cmd: &str,
    root: &Path,
    cur: &Cur,
    index: Index,
    store: Store,
    o: &mut Out,
) -> Result<i32, Fail> {
    let qdir = root.join(QUESTIONS);
    let (mut index, mut store) = (index, store);
    let n = if cmd == "backfill" {
        backfill(cur, &mut index, &qdir, &mut store)?
    } else {
        backfill_sections(cur, &mut index, &mut store)
    };
    let rows = live_rows(cur, &index);
    save_index(&root.join(INDEX), &rows)?;
    save_store(&root.join(STORE), &store)?;
    if cmd != "backfill" {
        // the snapshots it took kept with their words, as a bundle's are (451 T210), in the repository (T215)
        let keys: Vec<String> = cur.iter().map(|r| r.key.clone()).collect();
        let texts = json!({SECTION_TEXTS: section_texts(cur, &keys)});
        keep_sections(root, &texts, &rows, &store)?;
    }
    o.say(&if cmd == "backfill" {
        format!("claims-backfill: {n} row(s) given the pages they were checked at")
    } else {
        format!("claims-backfill-sections: {n} section claim(s) re-keyed to their own line; none owed by it")
    });
    Ok(0)
}
