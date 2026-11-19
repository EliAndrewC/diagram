//! `l7r-pool`: the pool walk's own program (feature 449 T220) - the work-budget review's counting run (`counts <tree>`, a counting build
//! alone) and the walk's commands, from the tree `L7R_GATE_TREE` names (the wrapper's), else the working directory.
//!
//! Research: plumbing - NONE: prints the command's reply

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let tree = std::env::var("L7R_GATE_TREE").unwrap_or_else(|_| ".".to_owned());
    let (out, err, code) = l7r_gate_pool::cli(&args, std::path::Path::new(&tree));
    // written, not `print!`ed: a reader gone (a closed pipe) is no panic
    let _ = std::io::Write::write_all(&mut std::io::stdout(), out.as_bytes());
    let _ = std::io::Write::write_all(&mut std::io::stderr(), err.as_bytes());
    std::process::exit(code);
}
