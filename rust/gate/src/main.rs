//! `l7r-gate`: the gate's tools (feature 449 phase 2) - `lib::cli` decides; this prints its reply and exits with its code.

fn main() {
    // the arguments as bytes (feature 449 T143): `log guard` takes them as `guard_log`'s Python did, `cli_os` hands the rest on as text
    let args: Vec<std::ffi::OsString> = std::env::args_os().skip(1).collect();
    let reply = l7r_gate::cli_os(&args);
    print!("{}", reply.stdout);
    eprint!("{}", reply.stderr);
    std::process::exit(reply.code);
}
