// t365 measurement harness: times l7r_shared::tempdir::TempDir::new (the real helper), and a bare read_dir of a directory.
use std::time::Instant;
fn main() {
    let a: Vec<String> = std::env::args().collect();
    let mode = a.get(1).map(String::as_str).unwrap_or("new");
    let n: usize = a.get(2).and_then(|s| s.parse().ok()).unwrap_or(200);
    let mut v = Vec::with_capacity(n);
    let mut entries = 0usize;
    for _ in 0..n {
        let t = Instant::now();
        match mode {
            "new" => { let d = l7r_shared::tempdir::TempDir::new("t365-nomatch"); drop(d); }
            _ => { entries = std::fs::read_dir(&a[3]).map(|r| r.flatten().count()).unwrap_or(0); }
        }
        v.push(t.elapsed().as_secs_f64() * 1e3);
    }
    v.sort_by(|x, y| x.partial_cmp(y).unwrap());
    let sum: f64 = v.iter().sum();
    println!("mode={mode} n={n} entries={entries} tmp={} mean_ms={:.3} median_ms={:.3} p90_ms={:.3} min_ms={:.3} max_ms={:.3}",
        std::env::temp_dir().display(), sum / n as f64, v[n / 2], v[n * 9 / 10], v[0], v[n - 1]);
}
