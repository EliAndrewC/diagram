//! The embedder (feature 449 T138, phase 4's S4; the round arbiter's `ask:449-phase4-slices` Q11: "a Rust embedder runs the same BGE-M3
//! weights (fastembed-rs or ort over the same ONNX) against the stored index"). It turns texts into BGE-M3's vectors as
//! `semantic_index.py`'s `model_embed` did through `fastembed`: the same files from the mirror's model cache, the same tokenizer settings,
//! the same batches of eight, the same ONNX session on half the cores, the first token's state normalized as numpy normalized it. Its own
//! binary: the gate's `semantic` crate runs `l7r-embed serve` through `scripts/gates/l7r-gate.sh embed` and never compiles ONNX Runtime.
//!
//! [`paths`] finds the model and the runtime, [`tok`] loads the tokenizer, [`pool`] normalizes, [`serve`] answers, [`model`] runs ONNX
//! Runtime (the one part only the real model reaches: `tests/hooks/test-l7r-gate.sh` drives it, the unit tests a stand-in [`Network`]).

pub mod model;
pub mod paths;
pub mod pool;
pub mod serve;
pub mod tok;

use std::path::PathBuf;

/// What a command prints and its exit status.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Reply {
    pub stdout: String,
    pub stderr: String,
    pub code: i32,
}

fn refuse(stderr: String, code: i32) -> Reply {
    Reply {
        stdout: String::new(),
        stderr,
        code,
    }
}

/// The network: one batch's token ids and attention mask in, each row's first-token state out (`n * dim` floats) with `dim`.
pub trait Network {
    /// # Errors
    /// The runtime refused the batch.
    fn cls(
        &mut self,
        ids: Vec<i64>,
        mask: Vec<i64>,
        n: usize,
        len: usize,
    ) -> Result<(Vec<f32>, usize), String>;
}

/// What opens the network for a command's options (ONNX Runtime in the binary, a stand-in in the tests).
pub type Opener = dyn Fn(&Options) -> Result<Box<dyn Network>, String>;

/// `serve`'s options: where the model is, the runtime, the threads and the batch.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Options {
    pub model_dir: PathBuf,
    pub runtime: PathBuf,
    pub threads: usize,
    pub batch: usize,
}

const USAGE: &str =
    "usage: l7r-embed serve (--cache DIR | --model-dir DIR) [--threads N] [--batch N] [--runtime LIB]\n";

fn number(flag: &str, value: Option<&String>) -> Result<usize, String> {
    value
        .and_then(|v| v.parse().ok())
        .filter(|&n| n > 0)
        .ok_or_else(|| format!("l7r-embed: {flag} wants a positive number\n{USAGE}"))
}

/// `serve`'s options from its arguments and the environment.
///
/// # Errors
/// An unknown option, a bad number, or no model named.
pub fn options(args: &[String], var: &dyn Fn(&str) -> String) -> Result<Options, String> {
    let mut cache = None;
    let mut model_dir = None;
    let mut threads = None;
    let mut batch = serve::BATCH;
    let mut runtime = None;
    let mut it = args.iter();
    while let Some(a) = it.next() {
        match a.as_str() {
            "--cache" => cache = it.next().map(PathBuf::from),
            "--model-dir" => model_dir = it.next().map(PathBuf::from),
            "--threads" => threads = Some(number(a, it.next())?),
            "--batch" => batch = number(a, it.next())?,
            "--runtime" => runtime = it.next().map(PathBuf::from),
            other => return Err(format!("l7r-embed: unknown option {other:?}\n{USAGE}")),
        }
    }
    let model_dir = match (model_dir, cache) {
        (Some(d), _) => d,
        (None, Some(c)) => {
            paths::snapshot(&c, paths::REPO).map_err(|e| format!("l7r-embed: {e}\n"))?
        }
        (None, None) => return Err(USAGE.to_owned()),
    };
    Ok(Options {
        model_dir,
        runtime: runtime.unwrap_or_else(|| paths::runtime(var)),
        threads: threads.unwrap_or_else(|| paths::threads(&paths::online_cpus())),
        batch,
    })
}

/// The command line: `serve` reading requests from `input` and answering on `output` (the process's stdin and stdout), the network
/// opened by `open` (ONNX Runtime in the binary, a stand-in in the tests).
#[must_use]
pub fn cli(
    args: &[String],
    var: &dyn Fn(&str) -> String,
    open: &Opener,
    input: &mut dyn std::io::BufRead,
    output: &mut dyn std::io::Write,
) -> Reply {
    if args.first().map(String::as_str) != Some("serve") {
        return refuse(USAGE.to_owned(), 2);
    }
    let o = match options(&args[1..], var) {
        Ok(o) => o,
        // a usage error is argparse's 2; a model not in the cache is a refusal, 1
        Err(e) => {
            return refuse(
                e.clone(),
                if e.starts_with("l7r-embed: the model") {
                    1
                } else {
                    2
                },
            )
        }
    };
    let started = tok::load(&o.model_dir).and_then(|t| Ok((t, open(&o)?)));
    match started {
        Ok((mut t, mut net)) => match serve::serve(&mut t, net.as_mut(), o.batch, input, output) {
            Ok(()) => Reply::default(),
            Err(e) => refuse(format!("l7r-embed: {e}\n"), 1),
        },
        Err(e) => refuse(format!("l7r-embed: {e}\n"), 1),
    }
}

/// The environment, as [`options`] reads it.
#[must_use]
pub fn env_var(name: &str) -> String {
    std::env::var(name).unwrap_or_default()
}

#[cfg(test)]
pub(crate) mod testkit;

#[cfg(test)]
mod tests;
