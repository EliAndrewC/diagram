// t508 scratch only: the old prefilters against the stream over copies of the clone's state, at many chunk sizes.
use super::super::{after_first, found, held_after, holds, snaps, CHUNK};
use std::io::Cursor;

fn old_holds(state: &str) -> bool {
    state.split_once("\"plan_holds\":").is_some_and(|(_, rest)| {
        rest.trim_start()
            .strip_prefix('{')
            .is_some_and(|inner| !inner.trim_start().starts_with('}'))
    })
}

#[test]
fn t508_differential() {
    let dir = std::env::var("T508_DIFF").unwrap();
    let mut rows = Vec::new();
    let mut differ = 0;
    let mut names: Vec<_> = std::fs::read_dir(&dir).unwrap().map(|e| e.unwrap().path()).collect();
    names.sort();
    for p in names {
        let text = std::fs::read_to_string(&p).unwrap();
        let (oh, os) = (old_holds(&text), text.contains("\"plan_snaps\""));
        let key = text.find("\"plan_holds\":").unwrap_or(0);
        let snap = text.find("\"plan_snaps\"").unwrap_or(0);
        let mut chunks: Vec<usize> =
            (1..=64).chain([4096, CHUNK - 1, CHUNK, CHUNK + 1, 1 << 20, text.len(), text.len() + 1]).collect();
        // chunk sizes that cut each key at each of its bytes
        for k in 1..13 {
            if key > 0 {
                chunks.push(key + k);
            }
            if snap > 0 {
                chunks.push(snap + k);
            }
        }
        let mut n = 0;
        for c in chunks {
            let nh = after_first(&mut Cursor::new(text.as_bytes()), b"\"plan_holds\":", c, &held_after);
            let ns = after_first(&mut Cursor::new(text.as_bytes()), b"\"plan_snaps\"", c, &found);
            n += 1;
            if nh != oh || ns != os {
                differ += 1;
            }
        }
        let (fh, fs) = (holds(&p), snaps(&p));
        if fh != oh || fs != os {
            differ += 1;
        }
        rows.push(format!(
            "{}\t{} bytes\tplan_holds at {key}\tplan_snaps at {snap}\told holds {oh} snaps {os}\tfile holds {fh} snaps {fs}\t{n} chunk sizes",
            p.file_name().unwrap().to_string_lossy(),
            text.len()
        ));
    }
    let out = format!("{}\ndiffering {differ}\n", rows.join("\n"));
    std::fs::write(std::env::var("T508_OUT").unwrap(), &out).unwrap();
    assert_eq!(differ, 0);
}
