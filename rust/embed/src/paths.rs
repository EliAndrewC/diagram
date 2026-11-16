//! Where the model and the runtime are, and how many threads (feature 449 T138).
//!
//! THE MODEL is the one `fastembed` downloaded for `semantic_index.py` (`Xenova/bge-m3`'s 8-bit build) into the mirror's
//! `.specify/model-cache/`, in Hugging Face's cache layout: `models--Xenova--bge-m3/refs/main` names the snapshot, its directory holds
//! the files. This crate never downloads one (the brief and Q11: the same weights); a cache without it is refused with the fix.
//!
//! THE RUNTIME is the ONNX Runtime `scripts/container/onnxruntime.pin` pins and `install-onnxruntime.sh` installs; `L7R_ONNXRUNTIME`
//! names another library, `L7R_ONNXRUNTIME_HOME` moves the install, as it moves the script's.

use std::path::{Path, PathBuf};

/// The model's repository and its file, as `semantic_index.py` registered them with `fastembed` (`sources=ModelSource(hf="Xenova/bge-m3")`,
/// `model_file="onnx/model_int8.onnx"`).
pub const REPO: &str = "Xenova/bge-m3";
pub const MODEL_FILE: &str = "onnx/model_int8.onnx";

/// The pin file, read at build time: one source for the script that installs the runtime and this crate.
pub const PIN: &str = include_str!("../../../scripts/container/onnxruntime.pin");

/// A `NAME=value` line of the pin file.
#[must_use]
pub fn pinned(name: &str) -> String {
    PIN.lines()
        .find_map(|l| l.strip_prefix(name)?.strip_prefix('='))
        .unwrap_or_default()
        .to_owned()
}

/// The runtime's library: `L7R_ONNXRUNTIME`, else the pinned version under `L7R_ONNXRUNTIME_HOME` (default `~/.cache/l7r-onnxruntime`).
#[must_use]
pub fn runtime(var: &dyn Fn(&str) -> String) -> PathBuf {
    let named = var("L7R_ONNXRUNTIME");
    if !named.is_empty() {
        return PathBuf::from(named);
    }
    let home = var("L7R_ONNXRUNTIME_HOME");
    let base = if home.is_empty() {
        PathBuf::from(var("HOME")).join(".cache/l7r-onnxruntime")
    } else {
        PathBuf::from(home)
    };
    let v = pinned("ONNXRUNTIME_VERSION");
    base.join(&v).join(format!(
        "onnxruntime-linux-x64-{v}/lib/libonnxruntime.so.{v}"
    ))
}

/// The snapshot directory of `repo` in the cache `cache`, holding the model's file.
///
/// # Errors
/// The cache does not hold the model: the message names what is missing and the fix.
pub fn snapshot(cache: &Path, repo: &str) -> Result<PathBuf, String> {
    let base = cache.join(format!("models--{}", repo.replace('/', "--")));
    let refs = base.join("refs/main");
    let rev = std::fs::read_to_string(&refs).unwrap_or_default();
    let dir = base.join("snapshots").join(rev.trim());
    if rev.trim().is_empty() || !dir.join(MODEL_FILE).is_file() {
        return Err(format!(
            "the model {repo} ({MODEL_FILE}) is not in {} - the semantic index reads the files fastembed fetched there (feature 447); \
             copy that cache from the host's mirror `.specify/model-cache/`, or name a directory holding the model's files with --model-dir",
            cache.display()
        ));
    }
    Ok(dir)
}

/// The CPUs online, as `/sys/devices/system/cpu/online` lists them (empty where it cannot be read).
#[must_use]
pub fn online_cpus() -> String {
    std::fs::read_to_string("/sys/devices/system/cpu/online").unwrap_or_default()
}

/// Half the cores (`max(1, os.cpu_count() // 2)`, `semantic_index.py`'s `threads=`): the containers share the machine and a 10 GB memory
/// cap, and a run of the full model at every core was killed (2026-10-29). `os.cpu_count()` is the CPUs online, which `online` lists
/// as ranges (`0-21`, `0,2-3`); not the affinity mask or the cgroup quota Rust's `available_parallelism` reads.
#[must_use]
pub fn threads(online: &str) -> usize {
    let count: usize = online
        .trim()
        .split(',')
        .filter(|r| !r.is_empty())
        .map(|r| match r.split_once('-') {
            Some((a, b)) => match (a.parse::<usize>(), b.parse::<usize>()) {
                (Ok(a), Ok(b)) if b >= a => b - a + 1,
                _ => 0,
            },
            None => usize::from(r.parse::<usize>().is_ok()),
        })
        .sum();
    let count = if count == 0 {
        std::thread::available_parallelism().map_or(2, std::num::NonZero::get)
    } else {
        count
    };
    (count / 2).max(1)
}

#[cfg(test)]
mod tests;
