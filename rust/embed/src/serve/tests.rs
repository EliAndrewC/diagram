//! The serve loop (feature 449 T138).

use l7r_guard::shared::tempdir::TempDir;

use super::{embed, serve};
use crate::testkit::{model_dir, Stand, CONFIG, MAP};

fn f32s(bytes: &[u8]) -> Vec<f32> {
    bytes
        .chunks(4)
        .map(|c| f32::from_le_bytes([c[0], c[1], c[2], c[3]]))
        .collect()
}

#[test]
fn texts_go_in_batches_and_come_back_normalized() {
    let tmp = TempDir::new("embed-serve");
    model_dir(tmp.path(), CONFIG, MAP);
    let mut t = crate::tok::load(tmp.path()).unwrap();
    let mut net = Stand {
        fail: false,
        batches: Vec::new(),
    };
    let texts: Vec<String> = ["a", "b", "a b", "b a b"]
        .iter()
        .map(|s| (*s).to_owned())
        .collect();
    let (v, dim) = embed(&t, &mut net, &texts, 3).unwrap();
    assert_eq!((v.len(), dim, net.batches.clone()), (12, 3, vec![3, 1]));
    let squares: f32 = v[..3].iter().map(|x| x * x).sum();
    assert!((squares - 1.0).abs() < 1e-6);
    let mut out = Vec::new();
    let input = "[\"a\", \"b\"]\nnot json\n[]\n";
    serve(&mut t, &mut net, 8, &mut input.as_bytes(), &mut out).unwrap();
    let head = b"ready\nok 2 3\n";
    assert!(out.starts_with(head));
    let after = &out[head.len() + 24..];
    let text = String::from_utf8(after.to_vec()).unwrap();
    assert!(text.starts_with("err a request is a JSON array of texts"));
    assert!(text.ends_with("ok 0 0\n"));
    let first = f32s(&out[head.len()..head.len() + 12]);
    assert_eq!(first.len(), 3);
    let mut failing = Stand {
        fail: true,
        batches: Vec::new(),
    };
    let mut out = Vec::new();
    serve(
        &mut t,
        &mut failing,
        8,
        &mut "[\"a\"]\n".as_bytes(),
        &mut out,
    )
    .unwrap();
    assert_eq!(
        String::from_utf8(out).unwrap(),
        "ready\nerr refused whole\n"
    );
}
