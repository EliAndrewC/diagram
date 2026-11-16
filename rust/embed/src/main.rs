//! `l7r-embed`: the embedder's command (feature 449 T138), which `scripts/gates/l7r-gate.sh embed ...` runs.

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let reply = l7r_embed::cli(
        &args,
        &l7r_embed::env_var,
        &l7r_embed::model::open,
        &mut std::io::stdin().lock(),
        &mut std::io::stdout().lock(),
    );
    // written, not `print!`ed: a reader gone (a closed pipe) is no panic
    let _ = std::io::Write::write_all(&mut std::io::stdout(), reply.stdout.as_bytes());
    let _ = std::io::Write::write_all(&mut std::io::stderr(), reply.stderr.as_bytes());
    std::process::exit(reply.code);
}
