//! `make hamlet SPEC=<path>`: a pool hamlet rolled from its spec by the Rust driver (feature 444 T42), its map and record written
//! beside the spec as `<name>.svg` and `<name>.json`, and the wall time printed.
//!
//! Research:
//!     the driver's command - NONE: plumbing

use std::path::Path;
use std::time::Instant;

fn main() {
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
