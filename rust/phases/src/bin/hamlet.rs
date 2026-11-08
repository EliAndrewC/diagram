//! `make hamlet SPEC=<path>`: a pool hamlet rolled from its spec by the Rust driver (feature 444 T42), its map and record written
//! beside the spec as `<name>.driver.svg` and `<name>.driver.json`, and the wall time printed.
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
/// counted operations printed one `seed size stage ops` line a roll and stage, then its counters one `... key n` line each, for `make work-budget` to set against
/// `dev/work-budget.json` (feature 443; the GM 2026-11-07: "focus entirely on our Rust code"). Built with the counters on.
fn budget() {
    for size in [10, 20, 40, 80] {
        for seed in [4, 25, 39, 47] {
            // THE BUDGET'S SIZES PAST A HAMLET'S (feature 443): the derivations price 40 and 80 households to read each stage's
            // growth, so the spec is the 10-household one with its households set past the reader's bound
            let mut spec = l7r_phases::driver::spec::parse(&format!(
                r#"{{"name": "Inashiro", "seed": {seed}, "households": 10, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated"}}"#
            ))
            .unwrap_or_default();
            spec.households = size;
            let rolled = l7r_phases::driver::roll(&spec);
            for (stage, counts) in rolled.map(|r| r.by_stage).unwrap_or_default() {
                println!(
                    "{seed}\t{size}\t{stage}\t{}",
                    l7r_phases::driver::ops(&counts)
                );
                for (key, n) in counts {
                    println!("{seed}\t{size}\t{stage}\t{key}\t{n}");
                }
            }
        }
    }
}

/// A seed's first failure, or None where it rolls clean: a stage's error, a refusal, or a rule the finished map breaks.
fn verdict(seed: i64, form: &str) -> Option<String> {
    let spec = l7r_phases::driver::cohort_spec(seed, (form != "comb").then_some(form));
    match l7r_phases::driver::roll(&spec) {
        Err(e) => Some(format!("FAILED: {e}")),
        Ok(r) => r
            .refusals
            .first()
            .map(|w| format!("REFUSED: {w}"))
            .or_else(|| {
                l7r_phases::driver::check::check(&r)
                    .first()
                    .map(|b| format!("BROKE: {b}"))
            }),
    }
    .map(|w| w.chars().take(160).collect::<String>().replace('\n', " "))
}

/// `hamlet --seeds <pool> <n>`: NO FIXED SEEDS (the GM 2026-11-07: "We should probably avoid fixed seeds because of overfitting ...
/// If a seed fails then we want to keep testing it until it succeeds, after which point it gets dropped from the fixed pool and when
/// there are no known bugs then we have no fixed seeds"). Every seed of the pool - one line a seed, `<seed> <form> <its first
/// failure>` - is rolled again and dropped once it rolls clean; then `n` fresh seeds of each form from a start the clock draws, a
/// failing one added to the pool. The pool is written back; any failure exits 1. The start is printed, so `make cohort SEED=<start>
/// N=<n> FIELD=<form>` rolls the same seeds again.
fn seeds(pool: &str, n: i64) {
    let t = Instant::now();
    let text = std::fs::read_to_string(pool).unwrap_or_default();
    let clock = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.subsec_nanos());
    let start = l7r_phases::driver::seeds::FRESH_FROM + i64::from(clock % 1_000_000_000);
    let r = l7r_phases::driver::seeds::run(&text, n, start, verdict);
    for line in &r.lines {
        println!("{line}");
    }
    if r.pool != text {
        if let Err(e) = std::fs::write(pool, &r.pool) {
            eprintln!("seeds: cannot write {pool}: {e}");
            std::process::exit(2);
        }
    }
    println!(
        "seeds: the pool {} seed(s) ({} still failing, {} dropped), {n} fresh seed(s) of each of {} forms from {start} ({} failed, added \
         to the pool), in {:.0} ms",
        r.failing + r.fixed,
        r.failing,
        r.fixed,
        l7r_phases::driver::seeds::FORMS.len(),
        r.added,
        t.elapsed().as_secs_f64() * 1000.0
    );
    if r.failing + r.added > 0 {
        std::process::exit(1);
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.get(1).map(String::as_str) == Some("--cohort") {
        let num = |i: usize, d: i64| args.get(i).and_then(|v| v.parse().ok()).unwrap_or(d);
        cohort(num(2, 1), num(3, 48), args.get(4).map(String::as_str));
        return;
    }
    if args.get(1).map(String::as_str) == Some("--seeds") {
        seeds(
            args.get(2).map_or("dev/known-seeds.txt", String::as_str),
            args.get(3).and_then(|v| v.parse().ok()).unwrap_or(200),
        );
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
