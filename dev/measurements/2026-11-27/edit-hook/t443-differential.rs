
// 451 T443 DIFFERENTIAL (temporary, appended to rust/guard/shared/src/guards/event_log_hooks/reversal/index/tests.rs, run once by
// make rust-test CRATE=rust/guard/shared, then removed): the derived index's answer against the FULL PARSE of every line, over a copy
// of every log of the real clone's .git/l7r-events/, in three states - COLD (no index, for every path), WARM (the index covering the
// whole log), GROWN (an index of a prefix cut at an arbitrary byte, mid-line included, the rest then appended to the same inode,
// restored before each path's ask so every path meets the catch-up).
#[test]
fn t443_differential() {
    use std::collections::BTreeMap;
    let s = "/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad";
    let Ok(rd) = std::fs::read_dir(format!("{s}/t443-logs")) else { return };
    let mut logs: Vec<_> = rd.filter_map(Result::ok).map(|e| e.path()).filter(|p| p.extension().is_some_and(|x| x == "jsonl")).collect();
    logs.sort();
    let work = std::path::PathBuf::from(format!("{s}/t443-diff-work"));
    let mut out = String::from("log\tbytes\tlines\tedit_lines\tpaths\tcold_differing\twarm_differing\tgrown_cuts\tgrown_differing\n");
    let (mut tl, mut te, mut tp, mut tc, mut tw, mut tg) = (0, 0, 0, 0, 0, 0);
    for src in logs {
        let text = std::fs::read_to_string(&src).unwrap();
        let mut by: BTreeMap<String, (Value, Vec<Value>)> = BTreeMap::new();
        for l in text.lines() {
            let Ok(e) = serde_json::from_str::<Value>(l.trim()) else { continue };
            if e.get("ev") == Some(&Value::from("PreToolUse")) && e.get("tool") == Some(&Value::from("Edit")) {
                if let Some(p) = e.get("path") {
                    by.entry(p.to_string()).or_insert_with(|| (p.clone(), Vec::new())).1.push(e.get("old").cloned().unwrap_or(Value::Null));
                }
            }
        }
        let _ = std::fs::remove_dir_all(&work);
        std::fs::create_dir_all(&work).unwrap();
        let log = work.join(src.file_name().unwrap());
        let idx = index_path(&log).unwrap();
        std::fs::write(&log, &text).unwrap();
        let (mut cold, mut warm, mut grown) = (0, 0, 0);
        for (p, want) in by.values() {
            let _ = std::fs::remove_file(&idx);
            cold += usize::from(ask(&log, p) != *want);
        }
        ask(&log, &Value::Null);
        assert_eq!(covered(&log), Some(text.len() as u64));
        for (p, want) in by.values() {
            warm += usize::from(ask(&log, p) != *want);
        }
        let n = text.len();
        let cuts = [n * 37 / 100, n * 71 / 100 + 13, n.saturating_sub(5)];
        for &cut in &cuts {
            std::fs::write(&log, &text.as_bytes()[..cut]).unwrap();
            let _ = std::fs::remove_file(&idx);
            let first = by.values().next().map(|v| v.0.clone()).unwrap_or(Value::Null);
            ask(&log, &first);
            let prefix = std::fs::read(&idx).unwrap();
            OpenOptions::new().append(true).open(&log).unwrap().write_all(&text.as_bytes()[cut..]).unwrap();
            for (p, want) in by.values() {
                std::fs::write(&idx, &prefix).unwrap();
                grown += usize::from(ask(&log, p) != *want);
            }
        }
        let lines = text.lines().count();
        let edits: usize = by.values().map(|v| v.1.len()).sum();
        out.push_str(&format!("{}\t{n}\t{lines}\t{edits}\t{}\t{cold}\t{warm}\t{}\t{grown}\n", src.file_name().unwrap().to_string_lossy(), by.len(), cuts.len()));
        (tl, te, tp, tc, tw, tg) = (tl + lines, te + edits, tp + by.len(), tc + cold, tw + warm, tg + grown);
    }
    let _ = std::fs::remove_dir_all(&work);
    out.push_str(&format!("ALL\t-\t{tl}\t{te}\t{tp}\t{tc}\t{tw}\t-\t{tg}\n"));
    std::fs::write(format!("{s}/t443-differential.tsv"), out).unwrap();
    assert_eq!((tc, tw, tg), (0, 0, 0));
}
