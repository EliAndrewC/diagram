//! `l7r-mode-a`: the Mode A engine's command (feature 449 T168), which `scripts/gates/l7r-gate.sh mode-a ...` runs.
//!
//! Research:
//!     the binary - NONE: prints the command's reply

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let tree = std::env::var("L7R_GATE_TREE").unwrap_or_else(|_| ".".to_owned());
    let reply = l7r_mode_a::cli(&args, std::path::Path::new(&tree));
    // written, not `print!`ed: a reader gone (a closed pipe) is no panic
    let _ = std::io::Write::write_all(&mut std::io::stdout(), reply.stdout.as_bytes());
    let _ = std::io::Write::write_all(&mut std::io::stderr(), reply.stderr.as_bytes());
    std::process::exit(reply.code);
}
