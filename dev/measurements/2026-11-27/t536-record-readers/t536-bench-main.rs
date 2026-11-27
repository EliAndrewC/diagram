//! 451 T536: the in-process cost of reading each of 451's large records WHOLE, the way its readers do, on a copy (warm page cache).
//! Usage: t536bench <file> <mode> [runs]; modes: bytes (fs::read), lines (read_to_string + lines), json (serde_json::Value, the whole
//! parse: plan/status.rs, plan/task.rs, plan/bundle.rs, arbiter/bundle/reviews.rs), edit_lines (touch.rs::edit_lines: lossy UTF-8,
//! each line filtered on "PostToolUse" and an edit or writes key, the kept lines parsed), landings (set_down_hooks::landings: lines
//! filtered on src land and step end, parsed). Prints the median and min milliseconds of `runs` runs and what each run found.
use std::time::Instant;
fn main() {
    let a: Vec<String> = std::env::args().collect();
    let (path, mode) = (&a[1], a[2].as_str());
    let runs: usize = a.get(3).and_then(|r| r.parse().ok()).unwrap_or(7);
    let mut ms = Vec::new();
    let mut found = 0usize;
    for _ in 0..runs {
        let t = Instant::now();
        found = match mode {
            "bytes" => std::fs::read(path).unwrap().len(),
            "lines" => std::fs::read_to_string(path).unwrap().lines().count(),
            "json" => {
                let v: serde_json::Value = serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
                v.as_object().map_or(0, |o| o.len())
            }
            "edit_lines" => {
                let text = String::from_utf8_lossy(&std::fs::read(path).unwrap()).into_owned();
                text.lines()
                    .filter(|l| l.contains("\"PostToolUse\"") && (l.contains("\"cat\":\"edit\"") || l.contains("\"writes\"")))
                    .filter_map(|l| serde_json::from_str::<serde_json::Value>(l).ok())
                    .count()
            }
            "landings" => {
                let text = std::fs::read_to_string(path).unwrap();
                text.lines()
                    .filter(|l| l.contains(r#""src":"land""#) && l.contains(r#""step":"end""#))
                    .filter_map(|l| serde_json::from_str::<serde_json::Value>(l).ok())
                    .count()
            }
            _ => panic!("mode"),
        };
        ms.push(t.elapsed().as_secs_f64() * 1000.0);
    }
    ms.sort_by(|x, y| x.partial_cmp(y).unwrap());
    println!("{path}\t{mode}\tmedian {:.1} ms\tmin {:.1} ms\tn={runs}\tfound {found}", ms[ms.len() / 2], ms[0]);
}
