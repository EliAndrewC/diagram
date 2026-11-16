use super::{blocked, domains, host, load, refusal, type_name, Rule};
use crate::shared::pyjson::value_repr;
use crate::shared::tempdir::TempDir;
use serde_json::json;

fn dir_with(text: Option<&str>) -> TempDir {
    let d = TempDir::new("guard-blocked");
    if let Some(t) = text {
        std::fs::write(d.join(super::DOMAINS), t).unwrap();
    }
    d
}

/// Each answer is `blocked.domains` / `blocked.host` on the same input (observed 2026-11-16, `CPython` 3.13).
#[test]
fn the_list_is_read_as_the_python_reads_it() {
    let d = dir_with(None);
    assert_eq!(domains(&d).unwrap(), Vec::<Rule>::new());
    let good = r#"{"domains": [{"domain": ".Grokipedia.com.", "reason": "AI", "approved": {"date": "2026-10-02", "words": "block it"}}]}"#;
    let d = dir_with(Some(good));
    let rules = domains(&d).unwrap();
    assert_eq!(rules[0].matches, "grokipedia.com");
    assert_eq!(rules[0].approved, "2026-10-02: block it");
    assert!(blocked("https://www.grokipedia.com/x", &rules).is_some());
    assert!(blocked("notgrokipedia.com", &rules).is_none());
    assert_eq!(
        refusal("u", &rules[0], "this WebFetch"),
        "this WebFetch refused: u is on the blocked list (blocked-domains.json: grokipedia.com - AI; approved 2026-10-02: block it). Find the same fact on another page; a blocked site is never read, cited or recorded."
    );
    let place = d.join(super::DOMAINS).to_string_lossy().into_owned();
    let no_ok = dir_with(Some(r#"{"domains": [{"domain": "a.com", "reason": "r"}]}"#));
    let e = domains(&no_ok).unwrap_err();
    assert_eq!(e.kind, "BlockedListError");
    assert!(e.message.ends_with("{'domain': 'a.com', 'reason': 'r'} carries no approval - every entry names the GM's approval as \"approved\": {\"date\": \"YYYY-MM-DD\", \"words\": \"<the GM's words>\"}"));
    let short = dir_with(Some(r#"{"domains": [{"domain": "a.com"}]}"#));
    assert!(domains(&short)
        .unwrap_err()
        .message
        .ends_with("{'domain': 'a.com'} needs its domain and its reason"));
    assert_eq!(
        domains(&dir_with(Some("nope"))).unwrap_err().kind,
        "JSONDecodeError"
    );
    assert_eq!(
        domains(&dir_with(Some("[1]"))).unwrap_err().message,
        "'list' object has no attribute 'get'"
    );
    assert_eq!(
        domains(&dir_with(Some(r#"{"domains": 3}"#)))
            .unwrap_err()
            .message,
        "'int' object is not iterable"
    );
    assert!(domains(&dir_with(Some(r#"{"domains": {"k": 1}}"#)))
        .unwrap_err()
        .message
        .ends_with("'k' needs its domain and its reason"));
    assert!(domains(&dir_with(Some(r#"{"domains": "ab"}"#)))
        .unwrap_err()
        .message
        .ends_with("'a' needs its domain and its reason"));
    let number = dir_with(Some(r#"{"domains": [{"domain": 5, "reason": "r"}]}"#));
    assert_eq!(
        domains(&number).unwrap_err().message,
        "'int' object has no attribute 'lower'"
    );
    std::fs::create_dir(d.join("sub")).unwrap();
    std::fs::create_dir(d.join("sub").join(super::DOMAINS)).unwrap();
    assert_eq!(
        load(&d.join("sub"), super::DOMAINS, "domain")
            .unwrap_err()
            .kind,
        "OSError"
    );
    assert!(place.ends_with("blocked-domains.json"));
}

#[test]
fn a_host_is_read_as_urlsplit_reads_it() {
    for (url, want) in [
        ("https://User@Example.COM:8080/a", "example.com"),
        ("example.com/path", "example.com"),
        ("http://[::1]:80/", "::1"),
        ("http://[bad/", "bad"),
        ("  ftp://a.b./x", "a.b"),
        ("1x://h/", "1x"),
        ("", ""),
    ] {
        assert_eq!(host(url), want, "{url}");
    }
    let types = [
        json!(null),
        json!(true),
        json!(1.5),
        json!(1),
        json!("s"),
        json!([]),
        json!({}),
    ];
    let names: Vec<&str> = types.iter().map(type_name).collect();
    assert_eq!(
        names,
        ["NoneType", "bool", "float", "int", "str", "list", "dict"]
    );
    assert_eq!(
        value_repr(&json!({"a": [1, "b", null]})),
        "{'a': [1, 'b', None]}"
    );
}
