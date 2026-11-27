// t373: prices of the levers, std only (rustc -O), each the median of 15 runs after 2 warm-ups, ms.
//   t373-levers <transcript.jsonl> <event-log.jsonl> <edited path as the log writes it>
// (a) the transcript read as session.rs `titled` does it today: every line, lossy text, a substring test.
// (b) the same answer from the END: 64 KiB blocks read backwards until a line holding `"type":"custom-title"` is whole.
// (c) the event log as event_log_hooks.rs `reversal` reads it today, WITHOUT its JSON parse of every line: read whole, count lines.
// (d) the event log read whole and only the lines that hold the edited path's text kept (the lines a parse would then see).
// (c) and (d) bound the lever from below and above: today's cost less (d) is what a substring screen before the parse saves.
use std::io::{BufRead, Read, Seek, SeekFrom};
use std::time::Instant;

fn med(mut v: Vec<f64>) -> f64 {
    v.sort_by(|a, b| a.partial_cmp(b).unwrap());
    v[v.len() / 2]
}

fn time(name: &str, f: &dyn Fn() -> usize) {
    let mut v = Vec::new();
    let mut got = 0;
    for i in 0..17 {
        let t = Instant::now();
        got = f();
        if i >= 2 {
            v.push(t.elapsed().as_secs_f64() * 1e3);
        }
    }
    println!("{name}: median_ms={:.1} answer={got}", med(v));
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let (transcript, log, path) = (a[1].clone(), a[2].clone(), a[3].clone());
    let t = transcript.clone();
    time("(a) transcript, every line (today's titled)", &move || {
        let f = std::fs::File::open(&t).unwrap();
        let mut n = 0;
        for raw in std::io::BufReader::new(f).split(b'\n').map_while(Result::ok) {
            for part in raw.split(|b| *b == b'\r') {
                if String::from_utf8_lossy(part).contains("custom-title") {
                    n += 1;
                }
            }
        }
        n
    });
    let t = transcript.clone();
    time("(b) transcript, backwards to the last custom-title record", &move || {
        let mut f = std::fs::File::open(&t).unwrap();
        let mut end = f.metadata().unwrap().len();
        let mut tail: Vec<u8> = Vec::new();
        let mut read = 0usize;
        while end > 0 {
            let at = end.saturating_sub(65536);
            let mut block = vec![0u8; (end - at) as usize];
            f.seek(SeekFrom::Start(at)).unwrap();
            f.read_exact(&mut block).unwrap();
            read += block.len();
            block.extend_from_slice(&tail);
            tail = block;
            end = at;
            // whole lines only: the first line of the buffer may be cut unless the file's start is reached
            let from = if at == 0 { 0 } else { tail.iter().position(|b| *b == b'\n').map_or(tail.len(), |i| i + 1) };
            let text = String::from_utf8_lossy(&tail[from..]);
            if text.lines().rev().any(|l| l.contains("\"type\":\"custom-title\"")) {
                return read;
            }
        }
        read
    });
    let l = log.clone();
    time("(c) event log, read whole and lines counted (no parse)", &move || std::fs::read_to_string(&l).unwrap_or_default().lines().count());
    let l = log.clone();
    time("(d) event log, read whole, lines holding the path kept", &move || {
        let needle = format!("\"path\":\"{path}\"");
        std::fs::read_to_string(&l).unwrap_or_default().lines().filter(|x| x.contains("\"tool\":\"Edit\"") && x.contains(&needle)).count()
    });
}
