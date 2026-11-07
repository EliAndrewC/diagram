//! `make hamlet SPEC=<path>`: a pool hamlet rolled from its spec by the Rust driver (feature 444 T42), its map and record written
//! beside the spec as `<name>.svg` and `<name>.json`, and the wall time printed.
//!
//! Research:
//!     the driver's command - NONE: plumbing

use std::path::Path;
use std::time::Instant;

/// `hamlet --cohort <first seed> <count>`: each seed rolled through the stages, one line a seed, then the refusals counted and
/// the time taken - the Rust stages' test bed over many seeds (feature 444 T42; the GM 2026-11-07: "focus entirely on our Rust").
fn cohort(first: i64, count: i64) {
    let t = Instant::now();
    let mut refused = 0;
    for seed in first..first + count {
        let spec = l7r_phases::driver::cohort_spec(seed);
        let s = Instant::now();
        match l7r_phases::driver::roll(&spec) {
            Ok(r) => {
                let why = r.refusals.first().map_or(String::new(), |w| {
                    format!("  REFUSED: {}", w.chars().take(140).collect::<String>())
                });
                refused += usize::from(!r.refusals.is_empty());
                println!(
                    "{} hh={} {} form={} {:.1} ms - {}{why}",
                    spec.name,
                    spec.households,
                    r.plan.archetype,
                    r.plan.knob("settlement_form"),
                    s.elapsed().as_secs_f64() * 1000.0,
                    r.stages.join(",")
                );
            }
            Err(e) => {
                refused += 1;
                println!("{} hh={} FAILED: {e}", spec.name, spec.households);
            }
        }
    }
    println!(
        "cohort: {count} seed(s) from {first}, {refused} refused, in {:.0} ms",
        t.elapsed().as_secs_f64() * 1000.0
    );
    if refused > 0 {
        std::process::exit(1);
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.get(1).map(String::as_str) == Some("--cohort") {
        let num = |i: usize, d: i64| args.get(i).and_then(|v| v.parse().ok()).unwrap_or(d);
        cohort(num(2, 1), num(3, 48));
        return;
    }
    let Some(spec_path) = std::env::args().nth(1) else {
        eprintln!("hamlet: a spec path is required - make hamlet SPEC=pool/hamlets/<name>/<name>.spec.json");
        std::process::exit(2);
    };
    let t = Instant::now();
    let text = std::fs::read_to_string(&spec_path).unwrap_or_else(|e| {
        eprintln!("hamlet: cannot read {spec_path}: {e}");
        std::process::exit(2);
    });
    let spec = l7r_phases::driver::spec::parse(&text).unwrap_or_else(|e| {
        eprintln!("hamlet: {spec_path}: {e}");
        std::process::exit(2);
    });
    let rolled = l7r_phases::driver::roll(&spec).unwrap_or_else(|e| {
        eprintln!("hamlet: {e}");
        std::process::exit(1);
    });
    let dir = Path::new(&spec_path)
        .parent()
        .unwrap_or_else(|| Path::new("."));
    let stem = spec.name.to_lowercase();
    for (ext, body) in [
        ("svg", rolled.svg.clone()),
        ("json", l7r_phases::driver::manifest(&rolled)),
    ] {
        let out = dir.join(format!("{stem}.driver.{ext}"));
        if let Err(e) = std::fs::write(&out, body) {
            eprintln!("hamlet: cannot write {}: {e}", out.display());
            std::process::exit(1);
        }
    }
    println!(
        "hamlet: {} rolled through {} in {:.1} ms - {}/{stem}.driver.svg and .json",
        spec.name,
        rolled.stages.join(", "),
        t.elapsed().as_secs_f64() * 1000.0,
        dir.display()
    );
}
