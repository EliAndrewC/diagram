//! `l7r-rust`: the `rust` verb of `l7r-gate` alone (feature 449 T93) - `scripts/gates/l7r-gate.sh rust <cmd> ...` runs this with the
//! words after `rust`, its reply the same as `l7r-gate rust <cmd> ...`.

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let reply = l7r_gate_rustc::rustc::cli(&args);
    print!("{}", reply.stdout);
    eprint!("{}", reply.stderr);
    std::process::exit(reply.code);
}
