//! `l7r-gate`: the gate's tools (feature 449 phase 2) - `lib::cli` decides; this prints its reply and exits with its code.

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let reply = l7r_gate::cli(&args);
    print!("{}", reply.stdout);
    eprint!("{}", reply.stderr);
    std::process::exit(reply.code);
}
