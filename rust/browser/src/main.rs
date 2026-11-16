//! `l7r-browser`: the browser crate's commands (feature 449 T146), which `scripts/gates/l7r-gate.sh browser ...` runs.

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let reply = l7r_browser::cli(
        &args,
        &l7r_browser::chromium::env_var,
        &mut std::io::stdin().lock(),
        &mut std::io::stdout().lock(),
    );
    print!("{}", reply.stdout);
    eprint!("{}", reply.stderr);
    std::process::exit(reply.code);
}
