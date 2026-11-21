//! The tokenizer as `fastembed` set it up (feature 449 T138).

use l7r_shared::tempdir::TempDir;
use tokenizers::{PaddingDirection, TruncationDirection};

use super::{encode, load};
use crate::testkit::{model_dir, CONFIG, MAP};

fn texts(t: &[&str]) -> Vec<String> {
    t.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn a_batch_is_padded_to_its_longest_with_the_pad_id() {
    let dir = TempDir::new("embed-tok");
    model_dir(dir.path(), CONFIG, MAP);
    let t = load(dir.path()).unwrap();
    let b = encode(&t, &texts(&["a b", "a"])).unwrap();
    assert_eq!((b.rows, b.len), (2, 4));
    assert_eq!(b.ids, vec![0, 4, 5, 2, 0, 4, 2, 1]);
    assert_eq!(b.mask, vec![1, 1, 1, 1, 1, 1, 1, 0]);
    assert_eq!(t.get_truncation().unwrap().max_length, 8192);
    assert_eq!(encode(&t, &[]).unwrap().len, 0);
}

#[test]
fn the_sides_limits_and_pad_come_from_the_configs() {
    let dir = TempDir::new("embed-tok2");
    let m = dir.path().join("m");
    model_dir(
        &m,
        r#"{"model_max_length": 1e30, "max_length": 3, "truncation_side": "left", "padding_side": "left", "pad_token": "c"}"#,
        "",
    );
    std::fs::write(m.join("config.json"), r#"{"pad_token_id": 9}"#).unwrap();
    let t = load(&m).unwrap();
    let tr = t.get_truncation().unwrap();
    assert_eq!(
        (tr.max_length, tr.direction),
        (3, TruncationDirection::Left)
    );
    let p = t.get_padding().unwrap();
    assert_eq!((p.pad_id, p.pad_token.as_str()), (9, "c"));
    assert!(matches!(p.direction, PaddingDirection::Left));
    // the pad token's id from the vocabulary where no config names it
    let n = dir.path().join("n");
    model_dir(
        &n,
        r#"{"model_max_length": 5, "pad_token": "c", "truncation_side": "right", "padding_side": "right"}"#,
        "",
    );
    assert_eq!(load(&n).unwrap().get_padding().unwrap().pad_id, 10);
}

#[test]
fn fastembed_s_refusals() {
    let dir = TempDir::new("embed-tok3");
    let d = dir.path();
    assert!(load(d).unwrap_err().contains("tokenizer.json"));
    model_dir(&d.join("a"), "[]", "");
    std::fs::remove_file(d.join("a/tokenizer_config.json")).unwrap();
    assert!(load(&d.join("a"))
        .unwrap_err()
        .contains("tokenizer_config.json"));
    model_dir(&d.join("b"), "[]", "");
    assert!(load(&d.join("b"))
        .unwrap_err()
        .contains("not a JSON object"));
    model_dir(&d.join("c"), r#"{"model_max_length": true}"#, "");
    assert!(load(&d.join("c"))
        .unwrap_err()
        .contains("maximum context length"));
    model_dir(&d.join("e"), r#"{"model_max_length": 4}"#, "");
    assert!(load(&d.join("e")).unwrap_err().contains("pad token for"));
    model_dir(
        &d.join("f"),
        r#"{"model_max_length": 4, "pad_token": "zz"}"#,
        "",
    );
    assert!(load(&d.join("f")).unwrap_err().contains("resolve an id"));
    model_dir(&d.join("g"), CONFIG, "");
    std::fs::write(d.join("g/config.json"), "{").unwrap();
    assert!(load(&d.join("g")).is_err());
    model_dir(&d.join("h"), CONFIG, "");
    std::fs::write(d.join("h/tokenizer.json"), "{}").unwrap();
    assert!(load(&d.join("h")).is_err());
    std::fs::create_dir_all(d.join("i/tokenizer_config.json")).unwrap();
    std::fs::write(d.join("i/tokenizer.json"), "{}").unwrap();
    assert!(load(&d.join("i")).is_err());
}

#[test]
fn a_tokenizer_s_own_truncation_and_padding_are_kept_where_the_config_is_silent() {
    let dir = TempDir::new("embed-tok4");
    model_dir(dir.path(), r#"{"model_max_length": 6}"#, "");
    let own = crate::testkit::TOKENIZER.replace(
        r#""truncation": null, "padding": null"#,
        r#""truncation": {"direction": "Left", "max_length": 99, "strategy": "LongestFirst", "stride": 0},
           "padding": {"strategy": "BatchLongest", "direction": "Left", "pad_to_multiple_of": 4, "pad_id": 10, "pad_type_id": 1,
                       "pad_token": "c"}"#,
    );
    std::fs::write(dir.path().join("tokenizer.json"), own).unwrap();
    let t = load(dir.path()).unwrap();
    let tr = t.get_truncation().unwrap();
    assert_eq!(
        (tr.max_length, tr.direction),
        (6, TruncationDirection::Left)
    );
    let p = t.get_padding().unwrap();
    assert_eq!(
        (
            p.pad_id,
            p.pad_type_id,
            p.pad_to_multiple_of,
            p.pad_token.as_str()
        ),
        (10, 1, Some(4), "c")
    );
    assert!(matches!(p.direction, PaddingDirection::Left));
    // a config that cannot be read
    let locked = dir.path().join("tokenizer_config.json");
    std::fs::set_permissions(&locked, std::os::unix::fs::PermissionsExt::from_mode(0o000)).unwrap();
    assert!(load(dir.path())
        .unwrap_err()
        .contains("tokenizer_config.json"));
}
