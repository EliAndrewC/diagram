//! The command line (feature 449 T138).

use std::path::Path;

use l7r_guard::shared::tempdir::TempDir;

use super::{cli, options, Network, Opener, Options, Reply};
use crate::testkit::{model_dir, Stand, CONFIG, MAP};

fn words(args: &[&str]) -> Vec<String> {
    args.iter().map(|a| (*a).to_owned()).collect()
}

#[expect(clippy::unnecessary_wraps, reason = "an opener's signature")]
fn stand(_: &Options) -> Result<Box<dyn Network>, String> {
    Ok(Box::new(Stand {
        fail: false,
        batches: Vec::new(),
    }))
}

fn no_net(_: &Options) -> Result<Box<dyn Network>, String> {
    Err("no runtime".to_owned())
}

fn run(args: &[&str], open: &Opener, input: &str) -> (Reply, Vec<u8>) {
    let mut out = Vec::new();
    let reply = cli(
        &words(args),
        &|_| String::new(),
        open,
        &mut input.as_bytes(),
        &mut out,
    );
    (reply, out)
}

struct Shut;

impl std::io::Write for Shut {
    fn write(&mut self, _: &[u8]) -> std::io::Result<usize> {
        Err(std::io::Error::other("closed"))
    }
    fn flush(&mut self) -> std::io::Result<()> {
        Ok(())
    }
}

#[test]
fn serve_answers_through_the_command_line() {
    let dir = TempDir::new("embed-cli");
    let m = dir.path().join("m");
    model_dir(&m, CONFIG, MAP);
    let md = m.to_str().unwrap();
    let (reply, out) = run(
        &["serve", "--model-dir", md, "--threads", "2"],
        &stand,
        "[\"a b\"]\n",
    );
    assert_eq!(reply, Reply::default());
    assert!(out.starts_with(b"ready\nok 1 3\n"));
    assert_eq!(out.len(), "ready\nok 1 3\n".len() + 12);
    // no command, an unknown option, a bad number, no model
    assert_eq!(run(&[], &stand, "").0.code, 2);
    assert_eq!(run(&["serve", "--nope"], &stand, "").0.code, 2);
    assert_eq!(run(&["serve", "--batch", "0"], &stand, "").0.code, 2);
    assert_eq!(run(&["serve", "--threads"], &stand, "").0.code, 2);
    assert_eq!(run(&["serve"], &stand, "").0.code, 2);
    // a cache without the model, no runtime, no tokenizer, an answer that cannot be written
    let cache = dir.path().join("cache");
    let (reply, _) = run(&["serve", "--cache", cache.to_str().unwrap()], &stand, "");
    assert!(
        reply.stderr.starts_with("l7r-embed: the model") && reply.stderr.ends_with("--model-dir\n")
    );
    assert_eq!(reply.code, 1);
    assert_eq!(
        run(&["serve", "--model-dir", md], &no_net, "").0.stderr,
        "l7r-embed: no runtime\n"
    );
    assert_eq!(
        run(&["serve", "--model-dir", "/no/such"], &stand, "")
            .0
            .code,
        1
    );
    let reply = cli(
        &words(&["serve", "--model-dir", md]),
        &|_| String::new(),
        &stand,
        &mut "[]\n".as_bytes(),
        &mut Shut,
    );
    assert!(reply.stderr.contains("could not be written"));
    assert!(std::io::Write::flush(&mut Shut).is_ok());
}

#[test]
fn options_find_the_model_in_the_cache_and_the_pinned_runtime() {
    let dir = TempDir::new("embed-opts");
    let snap = dir.path().join("models--Xenova--bge-m3/snapshots/rev1");
    std::fs::create_dir_all(snap.join("onnx")).unwrap();
    std::fs::write(snap.join("onnx/model_int8.onnx"), "w").unwrap();
    std::fs::create_dir_all(dir.path().join("models--Xenova--bge-m3/refs")).unwrap();
    std::fs::write(
        dir.path().join("models--Xenova--bge-m3/refs/main"),
        "rev1\n",
    )
    .unwrap();
    let var = |k: &str| {
        if k == "HOME" {
            "/h".to_owned()
        } else {
            String::new()
        }
    };
    let o = options(
        &words(&["--cache", dir.path().to_str().unwrap(), "--batch", "3"]),
        &var,
    )
    .unwrap();
    assert_eq!(o.model_dir, snap);
    assert_eq!(o.batch, 3);
    assert!(o.threads >= 1);
    assert!(o
        .runtime
        .starts_with(Path::new("/h/.cache/l7r-onnxruntime")));
    let o = options(&words(&["--model-dir", "d", "--runtime", "r.so"]), &var).unwrap();
    assert_eq!(
        (o.model_dir.to_str(), o.runtime.to_str()),
        (Some("d"), Some("r.so"))
    );
    assert_eq!(super::env_var("L7R_NO_SUCH_VARIABLE_T138"), "");
}
