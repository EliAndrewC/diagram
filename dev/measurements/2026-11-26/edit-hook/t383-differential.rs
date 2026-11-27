// 451 T383: the differential of the screen against the full parse, as it ran inside rust/guard/shared/src/guards/event_log_hooks/reversal/tests.rs
// (so it called the crate's own candidate, needle and replaced), then was removed. Run: T383_LOGS=<a copy of the clone's .git/l7r-events> T383_OUT=<tsv> make rust-test CRATE=rust/guard/shared

/// TEMPORARY (451 T383's differential, removed after its run): every log under `T383_LOGS`, read-only.
#[test]
fn t383_differential_over_the_real_logs() {
    use std::collections::BTreeMap;
    use std::fmt::Write as _;
    let Ok(dir) = std::env::var("T383_LOGS") else { return };
    let mut out = String::new();
    let mut logs: Vec<_> = std::fs::read_dir(&dir).unwrap().filter_map(Result::ok).map(|e| e.path()).filter(|p| p.extension().is_some_and(|x| x == "jsonl")).collect();
    logs.sort();
    let (mut tl, mut te, mut tp, mut todd, mut tmiss, mut tdiff, mut tparsed) = (0, 0, 0, 0, 0, 0, 0usize);
    for log in logs {
        let text = std::fs::read_to_string(&log).unwrap();
        let mut by: BTreeMap<String, (Value, Vec<Value>)> = BTreeMap::new();
        let (mut lines, mut edits, mut missed, mut marker) = (0, 0, 0, 0);
        for l in text.lines() {
            lines += 1;
            if l.contains("\"Edit\"") { marker += 1; }
            let Ok(e) = serde_json::from_str::<Value>(l.trim()) else { continue };
            if e.get("ev") == Some(&Value::from("PreToolUse")) && e.get("tool") == Some(&Value::from("Edit")) {
                edits += 1;
                let p = e.get("path").cloned();
                // a line with no path key is matched by no path the parse compares (Some(path) only)
                let Some(p) = p else { continue };
                if !candidate(l, needle(&p).as_deref()) { missed += 1; }
                by.entry(p.to_string()).or_insert_with(|| (p.clone(), Vec::new())).1.push(e.get("old").cloned().unwrap_or(Value::Null));
            }
        }
        let odd = by.values().filter(|(p, _)| needle(p).is_none()).count();
        let (mut differ, mut parsed, mut most) = (0, 0usize, 0usize);
        for (p, olds) in by.values() {
            let (got, n) = replaced(&text, p);
            if &got != olds { differ += 1; }
            parsed += n;
            most = most.max(n);
        }
        writeln!(out, "{}\tlines={lines}\tlines_with_Edit_marker={marker}\tpretooluse_edit_lines={edits}\tdistinct_paths={}\tpaths_screened_by_tool_alone={odd}\tlines_the_screen_dropped={missed}\tpaths_whose_result_differs={differ}\tparsed_all_paths={parsed}\tmost_parsed_for_one_path={most}", log.file_name().unwrap().to_string_lossy(), by.len()).unwrap();
        tl += lines; te += edits; tp += by.len(); todd += odd; tmiss += missed; tdiff += differ; tparsed += parsed;
    }
    writeln!(out, "TOTAL\tlines={tl}\tpretooluse_edit_lines={te}\tdistinct_paths={tp}\tpaths_screened_by_tool_alone={todd}\tlines_the_screen_dropped={tmiss}\tpaths_whose_result_differs={tdiff}\tparsed_all_paths={tparsed}").unwrap();
    std::fs::write(std::env::var("T383_OUT").unwrap(), &out).unwrap();
    assert_eq!((tmiss, tdiff), (0, 0), "{out}");
}
