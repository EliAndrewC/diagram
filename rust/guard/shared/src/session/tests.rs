use std::path::Path;

use serde_json::json;

use super::Session;

fn scratch(tag: &str) -> crate::tempdir::TempDir {
    let d = crate::tempdir::TempDir::new(&format!("guard-session-{tag}"));
    d
}

fn session(main: &Path, sessions: &Path, transcript: &str, id: &str) -> Session {
    let mut s = Session::from_input(
        &json!({"session_id": id, "cwd": "/nowhere", "transcript_path": transcript}),
    );
    s.main_seam = Some(main.to_string_lossy().into_owned());
    s.sessions_dir = sessions.to_path_buf();
    s
}

#[test]
fn the_claim_map_answers_first_and_is_read_once() {
    let d = scratch("map");
    std::fs::create_dir_all(d.join(".clones/.session-clones")).unwrap();
    std::fs::write(
        d.join(".clones/.session-clones/sid-1"),
        format!("{}/.clones/my-work\n", d.display()),
    )
    .unwrap();
    let s = session(&d, &d.join("none"), "", "sid-1");
    assert_eq!(s.name(), "my-work");
    assert_eq!(s.name(), "my-work");
    assert_eq!(s.reads.get(), 1, "the map read once a process");
    assert_eq!(s.clone_dir(), Some(d.join(".clones/my-work").as_path()));
}

#[test]
fn a_rename_in_the_transcript_names_an_unclaimed_session_in_kebab_case() {
    let d = scratch("title");
    let tp = d.join("t.jsonl");
    std::fs::write(&tp, "{\"type\": \"custom-title\", \"customTitle\": \"Old Name\"}\nnot json custom-title\n{\"type\": \"custom-title\", \"customTitle\": \"Diagram Backlog!\"}\n").unwrap();
    let s = session(&d, &d.join("none"), &tp.to_string_lossy(), "sid-2");
    assert_eq!(
        s.clone_dir(),
        Some(d.join(".clones/diagram-backlog").as_path())
    );
}

#[test]
fn the_sessions_json_names_it_else_and_a_derived_name_is_the_mirrors() {
    let d = scratch("json");
    let sd = d.join("sessions");
    std::fs::create_dir_all(&sd).unwrap();
    std::fs::write(
        sd.join("a.json"),
        r#"{"sessionId": "sid-3", "name": "Mode A work", "nameSource": "user"}"#,
    )
    .unwrap();
    std::fs::write(
        sd.join("b.json"),
        r#"{"id": "sid-4", "name": "whatever", "nameSource": "derived"}"#,
    )
    .unwrap();
    std::fs::write(sd.join("c.txt"), "ignored").unwrap();
    std::fs::write(sd.join("d.json"), "not json").unwrap();
    assert_eq!(session(&d, &sd, "", "sid-3").name(), "mode-a-work");
    let mirror = d.file_name().unwrap().to_string_lossy().into_owned();
    assert_eq!(
        session(&d, &sd, "", "sid-4").name(),
        mirror
            .to_lowercase()
            .replace(|c: char| !c.is_ascii_alphanumeric() && c != '-', "")
    );
    assert_eq!(session(&d, &sd, "", "sid-5").name(), "", "unresolvable");
    assert_eq!(session(&d, &sd, "", "").name(), "", "no session id");
    assert!(session(&d, &d.join("missing"), "", "sid-6")
        .clone_dir()
        .is_none());
}

#[test]
fn the_mirror_is_the_work_trees_top_cut_at_its_clones() {
    let d = scratch("main");
    std::fs::create_dir_all(d.join(".clones/c/.git")).unwrap();
    std::fs::create_dir_all(d.join(".clones/c/sub")).unwrap();
    let mut s = Session::from_input(&json!({"cwd": d.join(".clones/c/sub").to_string_lossy()}));
    s.main_seam = None;
    assert_eq!(s.main(), d.path());
    let mut none = Session::from_input(&json!({"cwd": "/"}));
    none.main_seam = None;
    assert_eq!(none.main(), std::path::Path::new("/diagram"));
    std::fs::create_dir_all(d.join("plain/.git")).unwrap();
    let mut plain = Session::from_input(&json!({"cwd": d.join("plain").to_string_lossy()}));
    plain.main_seam = None;
    assert_eq!(plain.main(), d.join("plain").as_path());
}

#[test]
fn the_sessions_dir_defaults_under_home() {
    let env = |k: &str| (k == "HOME").then(|| "/h".to_owned());
    let s = Session::with_env(&json!({}), env);
    assert_eq!(s.sessions_dir, Path::new("/h/.claude/sessions"));
    assert!(s.main_seam.is_none());
    // `${CLONE_SESSIONS_DIR:-${HOME:-/home/agent}/.claude/sessions}`: an empty seam or home is none
    let empty = |_: &str| Some(String::new());
    let s = Session::with_env(&json!({}), empty);
    assert_eq!(s.sessions_dir, Path::new("/home/agent/.claude/sessions"));
    assert!(s.main_seam.is_none());
}

#[test]
fn the_seams_come_from_the_environment() {
    let env = |k: &str| match k {
        "CLONE_SESSIONS_DIR" => Some("/s".to_owned()),
        "CLONE_MAIN" => Some("/m".to_owned()),
        _ => None,
    };
    let s = Session::with_env(&json!({}), env);
    assert_eq!(
        (s.sessions_dir.as_path(), s.main()),
        (Path::new("/s"), Path::new("/m"))
    );
}

#[test]
fn the_gms_messages_are_read_once_and_the_rename_a_line_at_a_time() {
    let d = scratch("messages");
    let tp = d.join("t.jsonl");
    std::fs::write(&tp, "{\"type\": \"custom-title\", \"customTitle\": \"named\"}\n{\"type\": \"user\", \"message\": {\"content\": \"go\"}}\n").unwrap();
    let s = session(&d, &d.join("none"), &tp.to_string_lossy(), "sid-7");
    assert_eq!(s.name(), "named");
    assert_eq!(s.gm_messages(), ["go".to_owned()]);
    assert_eq!(s.gm_messages().len(), 1);
    // the rename and the transcript; a claim map that is not there is no read (feature 449 T143: it was counted as one)
    assert_eq!(s.reads.get(), 2);
    assert!(session(&d, &d, "/no/such", "x").gm_messages().is_empty());
}

/// The guard log's name as `guard_log` took it from `clone-resolve.sh resolve`'s text (feature 449 T143): the claim map's last line after
/// its last `/`, a NUL dropped and a byte that is not UTF-8 Python's surrogate, nothing for a map that cannot be read - while the clone
/// itself still resolves as it did.
#[test]
fn the_logs_name_is_the_last_line_of_the_claim_maps_text() {
    let d = scratch("map-text");
    let map = d.join(".clones/.session-clones");
    std::fs::create_dir_all(&map).unwrap();
    let named = |text: &[u8]| {
        std::fs::write(map.join("sid"), text).unwrap();
        session(&d, &d.join("none"), "", "sid").name()
    };
    assert_eq!(named(b"/m/.clones/one\n/m/.clones/two\n"), "two");
    assert_eq!(named(b"/m/.clones/one\n\n"), "", "the last line empty");
    assert_eq!(named(b"/m/.clones/trailing/"), "");
    assert_eq!(named(b"bare"), "bare");
    assert_eq!(named(b"/m/n\0ul"), "nul");
    assert_eq!(named(b"/m/caf\xff").chars().count(), 4);
    std::fs::write(map.join("sid"), b"/m/caf\xff").unwrap();
    let s = session(&d, &d.join("none"), "", "sid");
    assert!(
        s.clone_dir().is_none(),
        // a map that is not UTF-8 is no clone, as before
    );
    std::fs::remove_file(map.join("sid")).unwrap();
    std::fs::create_dir(map.join("sid")).unwrap();
    assert_eq!(
        session(&d, &d.join("none"), "", "sid").name(),
        "",
        // a directory is no map: the name source next, here none
    );
}

#[test]
fn a_map_that_cannot_be_read_names_nothing() {
    use std::os::unix::fs::PermissionsExt as _;
    let d = scratch("map-locked");
    let map = d.join(".clones/.session-clones");
    std::fs::create_dir_all(&map).unwrap();
    std::fs::write(map.join("sid"), "/m/.clones/x\n").unwrap();
    std::fs::set_permissions(map.join("sid"), std::fs::Permissions::from_mode(0o000)).unwrap();
    let s = session(&d, &d.join("none"), "", "sid");
    // a root run reads it anyway; either way the name is what the text or the failure gives
    let readable = std::fs::read(map.join("sid")).is_ok();
    assert_eq!(s.name(), if readable { "x" } else { "" });
    std::fs::set_permissions(map.join("sid"), std::fs::Permissions::from_mode(0o644)).unwrap();
}

/// What the Python's lookup did with odd records (feature 449 T143): a title or name that is not a string named by its `str()`, a dot
/// file not globbed, `\r` a line's end, Python's whitespace in the kebab case, and a record that is no dict ending the lookup.
#[test]
fn the_name_sources_read_as_the_python_read_them() {
    let d = scratch("odd-names");
    let sd = d.join("sessions");
    std::fs::create_dir_all(&sd).unwrap();
    let tp = d.join("t.jsonl");
    let titled = |text: &str| {
        std::fs::write(&tp, text).unwrap();
        session(&d, &sd, &tp.to_string_lossy(), "sid-t").name()
    };
    assert_eq!(
        titled("{\"type\": \"custom-title\", \"customTitle\": 42}\n"),
        "42"
    );
    assert_eq!(
        titled("{\"type\": \"custom-title\", \"customTitle\": \"a\"}\r{\"type\": \"custom-title\", \"customTitle\": \"b\"}\n"),
        "b",
        // a \r ends a line
    );
    assert_eq!(
        titled("{\"type\": \"custom-title\", \"customTitle\": \"x\\u001fy\"}\n"),
        "x-y"
    );
    assert_eq!(
        titled("{\"type\": \"custom-title\", \"customTitle\": \"   \"}\n"),
        "",
        // blank: the sessions json, here none
    );
    assert_eq!(
        titled("{\"type\": \"custom-title\", \"customTitle\": \"a\"}\n[\"custom-title\"]\n"),
        "",
        // a record that is no dict
    );
    std::fs::write(
        sd.join(".hidden.json"),
        r#"{"id": "sid-j", "name": "hidden"}"#,
    )
    .unwrap();
    std::fs::write(sd.join("n.json"), r#"{"id": "sid-n", "name": 7}"#).unwrap();
    assert_eq!(
        session(&d, &sd, "", "sid-j").name(),
        "",
        // a dot file is not globbed
    );
    assert_eq!(session(&d, &sd, "", "sid-n").name(), "7");
    // a name that is false (`0`) is no name: the mirror's own, as `str(name or "")` was blank
    std::fs::write(sd.join("m.json"), r#"{"id": "sid-zero", "name": 0}"#).unwrap();
    assert_eq!(
        session(&d, &sd, "", "sid-zero").name(),
        session(&d, &sd, "", "sid-derived-like")
            .main()
            .file_name()
            .unwrap()
            .to_string_lossy()
            .to_lowercase()
            .replace(|c: char| !c.is_ascii_alphanumeric() && c != '-', "")
    );
    std::fs::write(sd.join("z.json"), "[1]").unwrap();
    assert_eq!(
        session(&d, &sd, "", "sid-nobody").name(),
        "",
        // a list ends the lookup
    );
    std::fs::create_dir(d.join("dir.jsonl")).unwrap();
    assert_eq!(
        session(&d, &sd, &d.join("dir.jsonl").to_string_lossy(), "sid-n").name(),
        "7",
        // a directory is no transcript
    );
}

#[test]
fn a_transcript_that_cannot_be_opened_names_nothing() {
    use std::os::unix::fs::PermissionsExt as _;
    let d = scratch("locked-transcript");
    let sd = d.join("sessions");
    std::fs::create_dir_all(&sd).unwrap();
    std::fs::write(sd.join("a.json"), r#"{"id": "sid", "name": "listed"}"#).unwrap();
    let tp = d.join("t.jsonl");
    std::fs::write(&tp, "").unwrap();
    std::fs::set_permissions(&tp, std::fs::Permissions::from_mode(0o000)).unwrap();
    let readable = std::fs::File::open(&tp).is_ok();
    let name = session(&d, &sd, &tp.to_string_lossy(), "sid").name();
    assert_eq!(name, if readable { "listed" } else { "" });
    std::fs::set_permissions(&tp, std::fs::Permissions::from_mode(0o644)).unwrap();
}

#[test]
fn a_cwd_that_is_no_directory_has_no_top() {
    let d = scratch("no-top");
    std::fs::create_dir_all(d.join("repo/.git")).unwrap();
    std::fs::write(d.join("repo/file"), "").unwrap();
    for cwd in [
        String::new(),
        d.join("repo/missing").to_string_lossy().into_owned(),
        d.join("repo/file").to_string_lossy().into_owned(),
    ] {
        let mut s = Session::from_input(&json!({ "cwd": cwd }));
        s.main_seam = None;
        assert_ne!(s.main(), d.join("repo").as_path(), "{cwd}");
    }
}
