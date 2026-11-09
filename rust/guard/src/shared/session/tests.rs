use std::path::{Path, PathBuf};

use serde_json::json;

use super::Session;

fn scratch(tag: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!("l7r-guard-session-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
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
    assert_eq!(s.main(), d.as_path());
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
    assert_eq!(s.reads.get(), 3);
    assert!(session(&d, &d, "/no/such", "x").gm_messages().is_empty());
}
