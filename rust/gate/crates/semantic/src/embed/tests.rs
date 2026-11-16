//! The embedder as a program (feature 449 T138): a stand-in launcher speaking `l7r-embed serve`'s protocol, its behavior chosen by the
//! cache folder's name it is handed.

use std::path::{Path, PathBuf};

use l7r_guard::shared::tempdir::TempDir;

use super::{Embed, Program};

const FAKE: &str = r#"#!/usr/bin/env python3
import json, os, struct, sys
mode = os.path.basename(sys.argv[4])
out = sys.stdout.buffer
if mode == "noready":
    sys.exit(3)
if mode == "closed":
    os.close(0)
out.write(b"ready\n"); out.flush()
for line in sys.stdin:
    texts = json.loads(line)
    if mode == "err":
        out.write(b"err no model\n")
    elif mode == "garbled":
        out.write(b"what\n")
    elif mode == "short":
        out.write(b"ok 1 2\n" + struct.pack("<f", 1.0)); out.flush(); sys.exit(0)
    elif mode == "fewer":
        out.write(b"ok 0 2\n")
    else:
        out.write(("ok %d 2\n" % len(texts)).encode() + b"".join(struct.pack("<2f", len(t), 0.5) for t in texts))
    out.flush()
"#;

fn launcher(dir: &Path) -> PathBuf {
    let p = dir.join("l7r-gate.sh");
    l7r_gate_core::write_executable(&p, FAKE);
    p
}

fn texts(t: &[&str]) -> Vec<String> {
    t.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn the_program_answers_in_order_and_refuses_in_words() {
    let dir = TempDir::new("embed-prog");
    let l = launcher(dir.path());
    let mut p = Program::new(&l, Path::new("ok"));
    assert!(p.embed(&[]).unwrap().is_empty());
    assert_eq!(
        p.embed(&texts(&["ab", "c"])).unwrap(),
        [vec![2.0, 0.5], vec![1.0, 0.5]]
    );
    assert_eq!(p.embed(&texts(&["xyz"])).unwrap(), [vec![3.0, 0.5]]);
    drop(p);
    let said = |mode: &str| {
        Program::new(&l, Path::new(mode))
            .embed(&texts(&["a"]))
            .unwrap_err()
            .0
    };
    assert!(said("noready").contains("did not start"));
    assert!(said("closed").contains("the embedder stopped"));
    assert!(said("err").contains("refused: no model"));
    assert!(said("garbled").contains("answered \"what\""));
    assert!(said("short").contains("cut short"));
    assert!(said("fewer").contains("0 vectors for 1 texts"));
    let none = Program::new(&dir.path().join("none"), Path::new("ok"))
        .embed(&texts(&["a"]))
        .unwrap_err()
        .0;
    assert!(none.contains("could not start"));
}
