// 451 T392's pricing of the reversal read's options: a temporary test of rust/guard/shared/src/guards/event_log_hooks/reversal/tests.rs,
// run by `make rust-test CRATE=rust/guard/shared` with `memchr` a dependency, then removed; its output is t392-pricing.tsv.

// T392 PRICING (temporary, removed after its run): each option's read over a copy of the real 451 log
#[test]
fn t392_pricing() {
    use std::io::{Read, Seek, SeekFrom};
    use std::time::Instant;
    let s = "/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad";
    let log = format!("{s}/t392-logs/451-time-retro-and-efficiency.jsonl");
    let side = format!("{s}/t392-side-451.jsonl");
    if !std::path::Path::new(&log).is_file() {
        return;
    }
    fn bytes_read(buf: &[u8], path: &Value) -> usize {
        let n = needle(path);
        let key = n.as_deref().unwrap_or(super::EDIT);
        let mut out = 0;
        let mut end = 0;
        for at in memchr::memmem::find_iter(buf, key.as_bytes()) {
            if at < end {
                continue;
            }
            let a = memchr::memrchr(b'\n', &buf[..at]).map_or(0, |i| i + 1);
            let b = memchr::memchr(b'\n', &buf[at..]).map_or(buf.len(), |i| at + i);
            end = b;
            let line = &buf[a..b];
            if let Ok(l) = std::str::from_utf8(line) {
                if candidate(l, n.as_deref()) {
                    out += usize::from(serde_json::from_str::<Value>(l.trim()).is_ok());
                }
            }
        }
        out
    }
    let mut rows = String::new();
    for p in [
        "/diagram/.clones/diagram-backlog/specs/451-time-retro-and-efficiency/plan.md",
        "/diagram/.clones/diagram-backlog-t270/docs/usage.md",
    ] {
        let path = json!(p);
        let mut time = |label: &str, f: &mut dyn FnMut() -> usize| {
            let mut v = Vec::new();
            let mut n = 0;
            for i in 0..=20 {
                let t = Instant::now();
                n = f();
                if i > 0 {
                    v.push(t.elapsed().as_secs_f64() * 1e3);
                }
            }
            v.sort_by(f64::total_cmp);
            rows.push_str(&format!("{p}\t{label}\t{:.2}\t{:.2}\t{n}\n", v[10], v[18]));
        };
        time("read_to_string alone", &mut || std::fs::read_to_string(&log).unwrap().len());
        time("fs::read alone", &mut || std::fs::read(&log).unwrap().len());
        time("fs::read + from_utf8", &mut || std::str::from_utf8(&std::fs::read(&log).unwrap()).unwrap().len());
        time("NOW: read_to_string + line screen + parse", &mut || replaced(&std::fs::read_to_string(&log).unwrap(), &path).0.len());
        time("BYTES: read + memmem of the needle + parse", &mut || bytes_read(&std::fs::read(&log).unwrap(), &path));
        time("SIDE FILE: read_to_string + line screen + parse", &mut || replaced(&std::fs::read_to_string(&side).unwrap(), &path).0.len());
        time("SIDE FILE: bytes + memmem", &mut || bytes_read(&std::fs::read(&side).unwrap(), &path));
        for kib in [64usize, 256, 1024] {
            time(&format!("CHUNKED {kib} KiB: read alone"), &mut || {
                let mut f = std::fs::File::open(&log).unwrap();
                let mut b = vec![0u8; kib * 1024];
                let mut n = 0;
                loop {
                    let k = f.read(&mut b).unwrap();
                    if k == 0 {
                        break n;
                    }
                    n += k;
                }
            });
            time(&format!("CHUNKED {kib} KiB: read + memmem + parse"), &mut || {
                let mut f = std::fs::File::open(&log).unwrap();
                let mut buf: Vec<u8> = Vec::with_capacity(kib * 1024 * 2);
                let mut b = vec![0u8; kib * 1024];
                let mut n = 0;
                loop {
                    let k = f.read(&mut b).unwrap();
                    if k == 0 {
                        break n + bytes_read(&buf, &path);
                    }
                    buf.extend_from_slice(&b[..k]);
                    if let Some(cut) = memchr::memrchr(b'\n', &buf) {
                        n += bytes_read(&buf[..cut], &path);
                        buf.drain(..=cut);
                    }
                }
            });
        }
        time("CHUNKED 256 KiB, STD ONLY: from_utf8 of the whole lines + the line screen + parse", &mut || {
            let mut f = std::fs::File::open(&log).unwrap();
            let mut buf: Vec<u8> = Vec::with_capacity(512 * 1024);
            let mut b = vec![0u8; 256 * 1024];
            let mut n = 0;
            loop {
                let k = f.read(&mut b).unwrap();
                if k == 0 {
                    break n + replaced(std::str::from_utf8(&buf).unwrap(), &path).1;
                }
                buf.extend_from_slice(&b[..k]);
                if let Some(cut) = buf.iter().rposition(|&c| c == b'\n') {
                    n += replaced(std::str::from_utf8(&buf[..cut]).unwrap(), &path).1;
                    buf.drain(..=cut);
                }
            }
        });
        let w = format!("{s}/t392-writer-probe.jsonl");
        let line = std::fs::read_to_string(&side).unwrap().lines().next().unwrap().to_owned() + "\n";
        time("WRITER: one more open + append of an Edit line (the side file's cost)", &mut || {
            use std::io::Write as _;
            std::fs::OpenOptions::new().create(true).append(true).open(&w).unwrap().write_all(line.as_bytes()).unwrap();
            1
        });
        let _ = std::fs::remove_file(&w);
        time("KEPT OFFSET: open + seek + 64 KiB tail", &mut || {
            let mut f = std::fs::File::open(&log).unwrap();
            let len = f.metadata().unwrap().len();
            f.seek(SeekFrom::Start(len.saturating_sub(65536))).unwrap();
            let mut b = Vec::new();
            f.read_to_end(&mut b).unwrap();
            b.len()
        });
        let buf = std::fs::read(&log).unwrap();
        assert_eq!(bytes_read(&buf, &path), replaced(&std::fs::read_to_string(&log).unwrap(), &path).1);
    }
    let load = std::fs::read_to_string("/proc/loadavg").unwrap();
    std::fs::write(format!("{s}/t392-pricing.tsv"), format!("# load {load}{rows}")).unwrap();
}
