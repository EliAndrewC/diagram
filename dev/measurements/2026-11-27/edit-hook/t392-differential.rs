// 451 T392's differential: a temporary test appended to rust/guard/shared/src/guards/event_log_hooks/reversal/tests.rs (using its parse_all,
// the full parse of every line, as the oracle), run once by make rust-test CRATE=rust/guard/shared over a copy of the real clone's 34 logs, then removed.

// T392 DIFFERENTIAL (temporary, removed after its run): the chunked byte read against the FULL PARSE of every line, over a copy of
// every log of the real clone's .git/l7r-events/
#[test]
fn t392_differential() {
    use std::collections::BTreeMap;
    let s = "/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad";
    let dir = format!("{s}/t392-logs");
    let Ok(rd) = std::fs::read_dir(&dir) else { return };
    let mut logs: Vec<_> = rd.filter_map(Result::ok).map(|e| e.path()).collect();
    logs.sort();
    let mut out = String::from("log\tlines\tedit_lines_used\tdropped\tpaths\tpaths_differing\n");
    let (mut tl, mut tu, mut td, mut tp, mut tx) = (0, 0, 0, 0, 0);
    for log in logs {
        let text = std::fs::read_to_string(&log).unwrap();
        // the full parse's lines, by path, in order: the oracle
        let mut by: BTreeMap<String, (Value, Vec<Value>)> = BTreeMap::new();
        for l in text.lines() {
            let Ok(e) = serde_json::from_str::<Value>(l.trim()) else { continue };
            if e.get("ev") == Some(&Value::from("PreToolUse")) && e.get("tool") == Some(&Value::from("Edit")) {
                let p = e.get("path").cloned().unwrap_or(Value::Null);
                by.entry(p.to_string()).or_insert_with(|| (p.clone(), Vec::new())).1.push(e.get("old").cloned().unwrap_or(Value::Null));
            }
        }
        let (mut used, mut dropped, mut differ) = (0, 0, 0);
        for (p, want) in by.values() {
            assert_eq!(*want, parse_all(&text, p));
            let got = replaced(std::fs::File::open(&log).unwrap(), p, CHUNK).0;
            used += want.len();
            // a line dropped: an old the full parse keeps that the new read's list lacks (multiset)
            let mut left = got.clone();
            for w in want {
                if let Some(i) = left.iter().position(|g| g == w) { left.remove(i); } else { dropped += 1; }
            }
            differ += usize::from(got != *want);
        }
        let n = text.lines().count();
        out.push_str(&format!("{}\t{n}\t{used}\t{dropped}\t{}\t{differ}\n", log.file_name().unwrap().to_string_lossy(), by.len()));
        (tl, tu, td, tp, tx) = (tl + n, tu + used, td + dropped, tp + by.len(), tx + differ);
    }
    out.push_str(&format!("ALL\t{tl}\t{tu}\t{td}\t{tp}\t{tx}\n"));
    std::fs::write(format!("{s}/t392-differential.tsv"), out).unwrap();
    assert_eq!((td, tx), (0, 0));
}
