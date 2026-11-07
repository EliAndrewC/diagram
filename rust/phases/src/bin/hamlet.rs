//! `make hamlet SPEC=<path>`: a pool hamlet rolled from its spec by the Rust driver (feature 444 T42), its map and record written
//! beside the spec as `<name>.svg` and `<name>.json`, and the wall time printed.
//!
//! Research:
//!     the driver's command - NONE: plumbing

use std::path::Path;
use std::time::Instant;

/// `hamlet --cohort <first seed> <count> [archetype]`: each seed rolled through the stages, one line a seed, then the refusals counted and
/// the time taken - the Rust stages' test bed over many seeds (feature 444 T42; the GM 2026-11-07: "focus entirely on our Rust").
fn cohort(first: i64, count: i64, archetype: Option<&str>) {
    let t = Instant::now();
    let mut refused = 0;
    for seed in first..first + count {
        let spec = l7r_phases::driver::cohort_spec(seed, archetype);
        let s = Instant::now();
        match l7r_phases::driver::roll(&spec) {
            Ok(r) => {
                let broke = l7r_phases::driver::check::check(&r);
                let why = r.refusals.first().map_or(String::new(), |w| {
                    format!("  REFUSED: {}", w.chars().take(140).collect::<String>())
                });
                let why = if broke.is_empty() {
                    why
                } else {
                    format!("{why}  BROKE: {}", broke.join("  BROKE: "))
                };
                refused += usize::from(!r.refusals.is_empty() || !broke.is_empty());
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
        "cohort: {count} seed(s) from {first}, {refused} refused or broke a rule, in {:.0} ms",
        t.elapsed().as_secs_f64() * 1000.0
    );
    if refused > 0 {
        std::process::exit(1);
    }
}

/// `hamlet --budget`: the reference hamlet (the deleted `work_budget.py`'s Inashiro) rolled on its seeds at each size, each stage's
/// mean counted operations printed one `stage size mean rolled` line a stage and size, for `make work-budget` to set against
/// `dev/work-budget.json` (feature 443; the GM 2026-11-07: "focus entirely on our Rust code"). Built with the counters on.
fn budget() {
    let mut sums: Vec<(&str, u32, u64, u32)> = Vec::new();
    for size in [10, 20, 40, 80] {
        for seed in [4, 25, 39, 47] {
            // THE BUDGET'S SIZES PAST A HAMLET'S (feature 443): the derivations price 40 and 80 households to read each stage's growth, so
            // the spec is the 10-household one with its households set past the reader's bound
            let mut spec = l7r_phases::driver::spec::parse(&format!(
                r#"{{"name": "Inashiro", "seed": {seed}, "households": 10, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated"}}"#
            ))
            .unwrap_or_default();
            spec.households = size;
            for (stage, n) in l7r_phases::driver::roll(&spec)
                .map(|r| r.by_stage)
                .unwrap_or_default()
            {
                match sums.iter_mut().find(|s| s.0 == stage && s.1 == size) {
                    Some(s) => (s.2, s.3) = (s.2 + n, s.3 + 1),
                    None => sums.push((stage, size, n, 1)),
                }
            }
        }
    }
    for (stage, size, total, rolled) in sums {
        println!("{stage}\t{size}\t{}\t{rolled}", total / u64::from(rolled));
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.get(1).map(String::as_str) == Some("--cohort") {
        let num = |i: usize, d: i64| args.get(i).and_then(|v| v.parse().ok()).unwrap_or(d);
        cohort(num(2, 1), num(3, 48), args.get(4).map(String::as_str));
        return;
    }
    if args.get(1).map(String::as_str) == Some("--budget") {
        budget();
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
