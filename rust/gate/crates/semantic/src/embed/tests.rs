//! The embedder as a program (feature 449 T138): a stand-in launcher speaking `l7r-embed serve`'s protocol, its behavior chosen by the
//! cache folder's name it is handed.

use std::path::{Path, PathBuf};

use l7r_guard::shared::tempdir::TempDir;

use super::{Embed, Program};

/// The stand-in embedder: `ready`, then for each line of texts a vector `[length, 0.5]` a text, or the failure its cache path's name asks
/// for. A shell script, not Python (feature 449 T167: the test starts it seven times, and seven Python starts took 154 ms against
/// FR-008's tenth of a second); a text's length is read from the JSON line, 1 to 3 characters, as the test's texts are.
const FAKE: &str = r#"#!/bin/sh
mode=${4##*/}
[ "$mode" = noready ] && exit 3
[ "$mode" = closed ] && exec 0<&-
printf 'ready\n'
while IFS= read -r line; do
  case $mode in
  err) printf 'err no model\n' ;;
  garbled) printf 'what\n' ;;
  short) printf 'ok 1 2\n\000\000\200\077'; exit 0 ;;
  fewer) printf 'ok 0 2\n' ;;
  *)
    body=${line#[}; body=${body%]}; n=0; vec=''
    while [ -n "$body" ]; do
      item=${body%%,*}; [ "$item" = "$body" ] && body='' || body=${body#*,}
      item=${item#\"}; item=${item%\"}
      case ${#item} in 1) f='\000\000\200\077' ;; 2) f='\000\000\000\100' ;; 3) f='\000\000\100\100' ;; *) exit 9 ;; esac
      vec="$vec$f\\000\\000\\000\\077"; n=$((n+1))
    done
    printf "ok $n 2\\n$vec" ;;
  esac
done
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
