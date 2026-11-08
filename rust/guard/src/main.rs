//! `l7r-guard`: the guards' one process (feature 449 phase 1) - `lib::cli` decides; this prints its reply and exits with its code.

use std::io::Read;

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut stdin = String::new();
    if !matches!(
        args.first().map(String::as_str),
        Some("--version" | "--self-check")
    ) {
        let _ = std::io::stdin().read_to_string(&mut stdin);
    }
    let reply = l7r_guard::cli(&args, &stdin, &l7r_guard::guards());
    print!("{}", reply.stdout);
    eprint!("{}", reply.stderr);
    std::process::exit(reply.code);
}
