//! A builder resumed past the cap or after its task landed, and the handoff a refusal names (split from `tests.rs`, which
//! passed the file-scale bar of 1,000 lines at 451 T417).

use super::*;

#[test]
fn a_resume_of_a_builder_past_the_cap_or_landed_is_refused() {
    // past the cap, its task open
    let f = resumed("r-cap", 310_000, "451 T05: build it");
    assert_eq!(
        sent(&f.send(AID, "go on")),
        Some(Said::Resume {
            agent: AID.to_owned(),
            stale: Stale::PastCap(310_000),
            handoff: PathBuf::new()
        })
    );
    // under the cap, its task open: passes
    let f = resumed("r-open", 120_000, "451 T05: build it");
    f.events(&[agent_call(), end("T05", false, "2026-11-20T10:30:00.000Z")]);
    assert_eq!(sent(&f.send(AID, "go on")), None);
    // its task ticked
    f.tasks("- [x] T05 a\n- [ ] T06 b\n");
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
    f.tasks("- [ ] T05 a\n- [ ] T06 b\n");
    // landed in a background `make land`: the `end` line after the Agent call's PostToolUse
    let post = json!({"ev": "PostToolUse", "tool": "Agent", "id": DISPATCH, "aid": AID, "t": "2026-11-20T10:06:00.000Z"});
    f.events(&[
        agent_call(),
        post.clone(),
        end("T05", true, "2026-11-20T10:07:00.000Z"),
    ]);
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
    // a landing that exited 3 but pushed (`landed` true) counts
    let mut three = end("T05", true, "2026-11-20T10:07:00.000Z");
    three["code"] = json!(3);
    f.events(&[agent_call(), post.clone(), three]);
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
    // its only landing refused, another task's landing, and a landing before its dispatch: pass
    for l in [
        end("T05", false, "2026-11-20T10:07:00.000Z"),
        end("T06", true, "2026-11-20T10:07:00.000Z"),
        end("T05", true, "2026-11-20T10:04:59.000Z"),
    ] {
        f.events(&[agent_call(), post.clone(), l]);
        assert_eq!(sent(&f.send(AID, "go on")), None);
    }
    // a defined agent past the cap and landed passes; so does a `to` no path can take, an agent with no meta, and outside a clone
    f.transcript(AID, &[call(900_000)]);
    f.meta(AID, "review-x", "451 T05: review");
    f.events(&[agent_call(), end("T05", true, "2026-11-20T10:07:00.000Z")]);
    assert_eq!(sent(&f.send(AID, "go on")), None);
    f.meta(AID, "general-purpose", "451 T05: build it");
    assert_eq!(sent(&f.send("../x", "go on")), None);
    // an agent with no meta file passes, recorded
    assert_eq!(
        sent(&f.send("a0000000000000000", "go on")),
        Some(Said::ResumeNoMeta("a0000000000000000".to_owned()))
    );
    let mut outside = f.send(AID, "go on");
    outside["cwd"] = json!(f.dir.join("proj"));
    assert_eq!(sent(&outside), None);
}

/// D2's chain, never the latest start: a builder whose brief names no `T<n>` is read by its FIRST line's task, else the start in force
/// at its dispatch - the Agent line's time, else its first line's, else its transcript's first row.
#[test]
fn a_resumed_builders_task_is_its_first_line_or_the_start_at_its_dispatch() {
    let f = resumed("r-chain", 120_000, "a builder");
    f.starts(&[
        ("T05", "2026-11-20T10:00:00Z"),
        ("T06", "2026-11-20T10:30:00Z"),
    ]);
    let first =
        json!({"ev": "SubagentStart", "aid": AID, "task": "T05", "t": "2026-11-20T10:05:01.000Z"});
    let later = json!({"ev": "PreToolUse", "tool": "Bash", "by": AID, "task": "T06", "t": "2026-11-20T10:40:00.000Z"});
    let t05 = end("T05", true, "2026-11-20T10:20:00.000Z");
    // its first line carries T05, landed since; its later lines and the later start carry the open T06
    f.events(&[agent_call(), first.clone(), later.clone(), t05.clone()]);
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
    // a first line by `by` serves as well, its time the dispatch where no Agent line is found
    let by = json!({"ev": "PreToolUse", "tool": "Read", "by": AID, "task": "T05", "t": "2026-11-20T10:05:02.000Z"});
    f.events(&[by, later.clone(), t05.clone()]);
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
    // no line of its own carries a task: the start in force at the Agent line's time
    f.events(&[agent_call(), t05.clone()]);
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
    // no line at all: its transcript's first row's time is the dispatch (T05 ticked, T06 open - the latest start would pass it)
    f.events(&[]);
    f.tasks("- [x] T05 a\n- [ ] T06 b\n");
    let mut row = call(120_000);
    row["timestamp"] = json!("2026-11-20T10:10:00.000Z");
    f.transcript(AID, &[row]);
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
    // dispatched after T06's start: T06, open, passes
    let mut row = call(120_000);
    row["timestamp"] = json!("2026-11-20T10:31:00.000Z");
    f.transcript(AID, &[row]);
    assert_eq!(sent(&f.send(AID, "go on")), None);
    // a later start another worktree's builder made is passed over, this tree's own read (451 T254)
    let rows = [
        json!({"feature": "451-x", "task": "T06", "utc": "2026-11-20T10:30:00Z", "tree": f.clone()}),
        json!({"feature": "451-x", "task": "T05", "utc": "2026-11-20T10:30:30Z", "tree": "/another/tree"}),
    ];
    let text = rows.map(|r| r.to_string()).join("\n");
    std::fs::write(f.clone().join(".git/task-starts.jsonl"), text).unwrap();
    assert_eq!(sent(&f.send(AID, "go on")), None);
    // the brief's own `T<n>` is read first
    f.meta(AID, "general-purpose", "451 T05: x");
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
}

/// No task found: under the cap it passes with a `no task` record; past the cap the cap check still refuses.
#[test]
fn a_resumed_builder_with_no_task_passes_under_the_cap_only() {
    let f = Fixture::new("r-none", &[call(120_000)], None);
    f.meta(AID, "general-purpose", "a builder");
    assert_eq!(
        sent(&f.send(AID, "go on")),
        Some(Said::ResumeNoTask(AID.to_owned()))
    );
    f.transcript(AID, &[call(310_000)]);
    assert_eq!(
        sent(&f.send(AID, "go on")),
        Some(Said::Resume {
            agent: AID.to_owned(),
            stale: Stale::PastCap(310_000),
            handoff: PathBuf::new()
        })
    );
}

/// The escape, in the `SendMessage`'s summary, in the form the refusal prints; a bare one refused.
#[test]
fn context_ok_in_the_summary_escapes_a_resume() {
    let f = resumed("r-escape", 310_000, "451 T05: build it");
    assert_eq!(
        sent(&f.send(
            AID,
            "CONTEXT_OK=\"its handoff is not yet written\" write it"
        )),
        Some(Said::Escaped("its handoff is not yet written".to_owned()))
    );
    assert!(matches!(
        sent(&f.send(AID, "go on CONTEXT_OK")),
        Some(Said::NoReason(t)) if t.contains("CONTEXT_OK with no reason")
    ));
    // a builder past its own cap sending one is refused by its own cap first
    let mut own = f.input(
        "builder",
        "SendMessage",
        json!({"to": "a0000000000000000", "summary": "x", "message": "x"}),
    );
    own["agent_type"] = json!("general-purpose");
    // in its wrap-up band (451 T417) a resume is no stop point's step; past the ceiling the cap's own refusal
    assert!(matches!(
        verdict(&own),
        Some(Said::BandRefused { what, .. }) if what == "a SendMessage call"
    ));
    f.transcript(AID, &[call(350_000)]);
    assert!(matches!(verdict(&own), Some(Said::Refused { .. })));
}

/// A lone refusal's text, else what was answered.
fn refused(answers: &[Answer]) -> String {
    match answers {
        [Answer::Refuse(t)] => t.clone(),
        other => format!("not refused: {other:?}"),
    }
}

/// The refusals' text and records: the fresh dispatch with the handoff file, the escape in the summary, the permit for what follows.
#[test]
fn a_resumes_refusal_names_the_fresh_dispatch_and_the_handoff() {
    crate::shared::log::quiet();
    let f = resumed("r-text", 310_000, "451 T05: build it");
    let ask = |input: Value| {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input,
        };
        answer(&e, &Session::from_input(&e.input), Path::new("/"), &none)
    };
    // no handoff written: the file it would write, and the one resume that writes it
    let text = refused(&ask(f.send(AID, "go on")));
    let named = f.handoffs().join(format!("T05-{AID}.md"));
    assert!(text.contains("310000 tokens, past the cap of 300000"));
    assert!(text.contains(&named.display().to_string()), "{text}");
    assert!(text.contains("not written yet"), "{text}");
    assert!(
        text.contains("CONTEXT_OK=\"<reason>\" (two words or more) in the SendMessage's summary")
    );
    assert!(text.contains(&format!("make context-ok AID={AID} WHY=")));
    // 451 T428: what a resumed builder may still run, at each edge of its wrap-up band
    let edges =
        "its stop point's steps and its handoff up to 340000 tokens,\nand only its handoff past";
    assert!(text.contains(edges), "{text}");
    assert!(!text.contains("still refused every call"));
    // a handoff written under another task's name is the one named
    std::fs::create_dir_all(f.handoffs()).unwrap();
    let written = f.handoffs().join(format!("T04-{AID}.md"));
    std::fs::write(&written, "done; left").unwrap();
    let text = refused(&ask(f.send(AID, "go on")));
    assert!(text.contains(&written.display().to_string()) && !text.contains("not written yet"));
    assert!(text.contains("Dispatch a fresh builder"), "{text}");
    // 451 T352: a builder whose brief names its handoff: the brief's file, unwritten then written, before the agent-named one
    f.transcript(
        AID,
        &[brief_row(&f.handoffs(), &["T05-build.md"]), call(310_000)],
    );
    let briefed = f.handoffs().join("T05-build.md");
    let text = refused(&ask(f.send(AID, "go on")));
    assert!(text.contains(&written.display().to_string()), "{text}");
    std::fs::write(&briefed, "built").unwrap();
    let text = refused(&ask(f.send(AID, "go on")));
    assert!(text.contains(&briefed.display().to_string()) && !text.contains("not written yet"));
    std::fs::remove_file(&written).unwrap();
    std::fs::remove_file(&briefed).unwrap();
    let text = refused(&ask(f.send(AID, "go on")));
    assert!(text.contains(&briefed.display().to_string()) && text.contains("not written yet"));
    // landed: the next task's brief
    f.transcript(AID, &[call(120_000)]);
    f.tasks("- [x] T05 a\n");
    let text = refused(&ask(f.send(AID, "go on")));
    assert!(text.contains("T05 has landed or is ticked"), "{text}");
    // the escape, no task and an open builder pass
    assert!(ask(f.send(AID, "CONTEXT_OK=\"the handoff needs a pass\" go")).is_empty());
    f.tasks("- [ ] T05 a\n");
    assert_eq!(refused(&ask(f.send(AID, "go on"))), "not refused: []");
    let g = Fixture::new("r-text-none", &[call(120_000)], None);
    g.meta(AID, "general-purpose", "a builder");
    assert!(ask(g.send(AID, "go on")).is_empty());
    // an agent with no meta file passes, its record written
    assert!(ask(g.send("a0000000000000000", "go on")).is_empty());
}

/// D9's permit, end to end: the resume escaped, `make context-ok`'s grant (the guard-edit permit's store, keyed
/// `<clone>/context-cap:<agent id>`), and the builder's next call past the cap passing, recorded; another agent's permit is no permit.
#[test]
fn a_resume_escaped_then_permitted_lets_the_builders_next_call_through() {
    crate::shared::log::quiet();
    let f = resumed("r-permit", 350_000, "451 T05: build it");
    assert!(crate::shared::tool::ask(
        Path::new("/"),
        "git",
        &["init", "-q", &f.clone().to_string_lossy()],
        ""
    )
    .ok());
    // the resume, escaped
    assert!(matches!(
        sent(&f.send(AID, "CONTEXT_OK=\"one pass to write its handoff\" go")),
        Some(Said::Escaped(_))
    ));
    // before the permit, its next call is refused
    assert!(matches!(
        verdict(&f.bash("builder", "make quick")),
        Some(Said::Refused { .. })
    ));
    // another agent's permit does nothing
    let other = format!("{}/context-cap:a0000000000000000", f.clone().display());
    let args = |k: &str| {
        [
            "grant".to_owned(),
            k.to_owned(),
            "the resumed builder finishes its step".to_owned(),
        ]
    };
    assert_eq!(cli(&args(&other)).code, 0);
    assert!(matches!(
        verdict(&f.bash("builder", "make quick")),
        Some(Said::Refused { .. })
    ));
    // the grant, keyed as `make context-ok` keys it; a key with no agent id is no guard file
    let key = permit_key(&f.clone(), AID);
    assert_eq!(key, format!("{}/context-cap:{AID}", f.clone().display()));
    // its grant says what it grants, in its own words, not guard-edit's
    let grant = cli(&args(&key));
    assert_eq!(grant.code, 0);
    assert!(grant.stdout.starts_with(&format!(
        "context-ok: agent {AID} may pass the context cap until "
    )));
    assert!(grant
        .stdout
        .ends_with(" - the resumed builder finishes its step\n"));
    let store = std::fs::read_to_string(f.clone().join(".git/l7r-guard-permits.jsonl")).unwrap();
    assert!(store.contains(&format!("\"file\":\"{key}\"")), "{store}");
    assert_eq!(
        cli(&args(&format!("{}/context-cap:", f.clone().display()))).code,
        2
    );
    // the next call passes, its permit's reason recorded; the hook's entry passes it too
    assert_eq!(
        verdict(&f.bash("builder", "make quick")),
        Some(Said::Permitted(
            "the resumed builder finishes its step".to_owned()
        ))
    );
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: f.bash("builder", "make quick"),
    };
    assert!(answer(&e, &Session::from_input(&e.input), Path::new("/"), &none).is_empty());
    // a permit an hour old is spent
    let late = |k: &str| (k == "L7R_PERMIT_NOW").then(|| format!("{}", now(&none) + 3601.0));
    assert!(matches!(
        judge(
            &f.bash("builder", "make quick"),
            Path::new("/"),
            &late,
            CONTEXT_CAP_TOKENS,
            &no_clone
        ),
        Some(Said::Refused { .. })
    ));
}

// ---- 451 T60: the handoff under the session's clone, whatever the call's cwd ----

impl Fixture {
    /// A mirror beside the clone (`mirror/.git`), its claim map giving the pinned session the tree `claim`, or no entry.
    fn mirror(&self, claim: Option<&Path>) -> PathBuf {
        let m = self.dir.join("mirror");
        let map = m.join(".clones/.session-clones");
        std::fs::create_dir_all(m.join(".git")).unwrap();
        std::fs::create_dir_all(&map).unwrap();
        let sid = map.join(pinned("builder")["session_id"].as_str().unwrap());
        match claim {
            Some(c) => std::fs::write(&sid, c.display().to_string()).unwrap(),
            None => std::fs::remove_file(&sid).unwrap_or_default(),
        }
        std::fs::canonicalize(m).unwrap()
    }

    /// The session of `input`, its seams this fixture's: the mirror its `CLONE_MAIN`, an empty sessions directory, no real `HOME`.
    fn seated(&self, input: &Value) -> Session {
        let seam = |p: PathBuf| Some(p.display().to_string());
        Session::with_env(input, |k| match k {
            "CLONE_MAIN" => seam(self.dir.join("mirror")),
            "CLONE_SESSIONS_DIR" => seam(self.dir.join("no-sessions")),
            // `HOME`, the one other key it asks
            _ => seam(self.dir.to_path_buf()),
        })
    }
}

/// RED FIRST (451 T60): a builder whose shell was reset to the mirror is named its handoff under the SESSION's clone (the claim map,
/// as `clone_sync_hooks` routes an edit), its Write there passes and one to the mirror's `.git/l7r-handoffs` is refused; a resume
/// sent from the mirror names the clone's file, and `make context-ok`'s grant from the clone lets the call through. Where the session
/// resolves no clone, or one that is no work tree, the call's cwd gives the tree, as before.
#[test]
fn a_call_from_the_mirror_names_the_handoff_in_the_sessions_clone() {
    crate::shared::log::quiet();
    let f = Fixture::new("mirror", &[call(350_000)], Some("T60"));
    f.briefed("T60");
    let mirror = f.mirror(Some(&f.clone()));
    let from = |mut input: Value| {
        input["cwd"] = json!(mirror);
        input
    };
    let ask = |input: Value| {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input: from(input),
        };
        answer(&e, &f.seated(&e.input), Path::new("/"), &none)
    };
    let write = |file: &Path| {
        f.input(
            "builder",
            "Write",
            json!({"file_path": file, "content": "x"}),
        )
    };
    let handoff = f.handoffs().join(format!("T60-{AID}.md"));
    let stray = mirror
        .join(".git/l7r-handoffs")
        .join(format!("T60-{AID}.md"));
    assert_eq!(
        ask(f.bash("builder", "make quick")),
        vec![Answer::Refuse(refusal(350_000, &handoff, false))]
    );
    assert!(ask(write(&handoff)).is_empty());
    assert!(matches!(ask(write(&stray)).as_slice(), [Answer::Refuse(_)]));
    // a resume sent from the mirror names the clone's file
    f.meta(AID, "general-purpose", "451 T60: build it");
    f.tasks("- [ ] T60 a\n");
    let text = refused(&ask(f.send(AID, "go on")));
    assert!(text.contains(&handoff.display().to_string()), "{text}");
    // the session resolving no clone, or a directory that is no work tree: the cwd's tree, today's file
    let mirrored = mirror.join(".git/l7r-handoffs").display().to_string();
    for claim in [None, Some(f.dir.join("gone"))] {
        f.mirror(claim.as_deref());
        let text = refused(&ask(f.bash("builder", "make quick")));
        assert!(text.contains(&mirrored), "{text}");
    }
    // `make context-ok`'s grant, keyed by the clone it runs in, lets the mirror's call through
    f.mirror(Some(&f.clone()));
    assert!(crate::shared::tool::ask(
        Path::new("/"),
        "git",
        &["init", "-q", &f.clone().to_string_lossy()],
        ""
    )
    .ok());
    let key = permit_key(&f.clone(), AID);
    assert_eq!(
        cli(&[
            "grant".to_owned(),
            key,
            "the builder writes its handoff".to_owned()
        ])
        .code,
        0
    );
    assert!(ask(f.bash("builder", "make quick")).is_empty());
}

/// 451 T359: a start undone by `make task-unstart` is not the start in force at a builder's dispatch - the one before it is.
#[test]
fn a_start_undone_is_not_the_start_in_force_at_a_dispatch() {
    let f = resumed("r-undone", 120_000, "a builder");
    f.events(&[]);
    f.tasks("- [x] T05 a\n- [ ] T06 b\n");
    let mut row = call(120_000);
    row["timestamp"] = json!("2026-11-20T10:31:00.000Z");
    f.transcript(AID, &[row]);
    f.starts(&[
        ("T05", "2026-11-20T10:00:00Z"),
        ("T06", "2026-11-20T10:30:00Z"),
    ]);
    assert_eq!(sent(&f.send(AID, "go on")), None);
    let log = f.clone().join(".git/task-starts.jsonl");
    let undo = json!({"unstart": {"feature": "451-x", "task": "T06"}, "tree": "/t", "utc": "2026-11-20T10:30:30Z"});
    let text = std::fs::read_to_string(&log).unwrap();
    std::fs::write(&log, format!("{text}{undo}\n")).unwrap();
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
}
