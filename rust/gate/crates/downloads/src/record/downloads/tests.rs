//! The list's parsing, ingest, sync, add and the push check, on scratch repositories.

use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::process::Command;

use super::check::{check, failing, problems, selftest, selftest_failures};
use super::ingest::{inbox_matches, ingest, merge, report, sync, IngestResult};
use super::parse::{by_id, entries, parse, render, strip, words, Block, Entry, Marks};
use super::{add, cli_at, option, options, sorted, today, Ctx, CANON, STATE};
use crate::checks::scratch;

const BLANK: &str = "- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found\n- [ ] Found elsewhere (only with downloaded or partial) - where:\n- Saved as (optional, the file's name):";

fn owned(items: &[&str]) -> Vec<String> {
    items.iter().map(|s| (*s).to_owned()).collect()
}

fn put(root: &Path, rel: &str, text: &str) {
    let path = root.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn git(root: &Path, args: &[&str]) {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .unwrap();
    assert!(done.status.success());
}

fn repo(tag: &str) -> PathBuf {
    let root = scratch(tag);
    git(&root, &["init", "-q"]);
    git(&root, &["config", "user.email", "t@t"]);
    git(&root, &["config", "user.name", "t"]);
    root
}

fn commit(root: &Path) {
    git(root, &["add", "-A"]);
    git(root, &["commit", "-q", "-m", "c", "--allow-empty"]);
}

fn head(root: &Path) -> String {
    crate::cohort::git(root, &["rev-parse", "HEAD"])
        .1
        .trim()
        .to_owned()
}

fn ctx(root: &Path, inbox: &Path) -> Ctx {
    Ctx {
        root: root.to_owned(),
        copy: inbox.join("TO-DOWNLOAD.md"),
        python: "true".to_owned(),
        timeout: 2.0,
    }
}

fn entry_text(id: &str, title: &str, body: &str) -> String {
    format!("### {id}. {title}\n\n{BLANK}\n{body}\n")
}

fn access(root: &Path) {
    put(
        root,
        "research/source-access.json",
        r#"{"states":[{"id":"open"},{"id":"gm-full"},{"id":"gm-partial"},{"id":"paywalled"},{"id":"bot-refused"},{"id":"down"},{"id":"gone"},{"id":"never-read"}]}"#,
    );
}

fn no_sets() -> (HashSet<String>, HashSet<String>, HashMap<String, String>) {
    (HashSet::new(), HashSet::new(), HashMap::new())
}

#[test]
fn whitespace_helpers_take_pythons_four_separators_too() {
    assert_eq!(strip("\x1c a \x1f"), "a");
    assert_eq!(words(" a\x1db  c "), ["a", "b", "c"]);
}

#[test]
fn parse_and_render_are_an_identity_for_any_text() {
    for text in [
        "",
        "plain\n",
        "# T\n\n### 1. A\n\n- [ ] x\n",
        "### 1. A\n## Sub\ntext\n### 2. B",
        "### H3. High\n",
    ] {
        assert_eq!(render(&parse(text)), text);
    }
    let full = format!(
        "# T\n{}\n{}",
        entry_text("1", "A", "- Marks recorded 2026-01-02 (x)\n- body"),
        entry_text("H2", "B", "- b")
    );
    assert_eq!(render(&parse(&full)), full);
    let blocks = parse(&full);
    let found: Vec<&Entry> = entries(&blocks).collect();
    assert_eq!(
        found[0].recorded.as_deref(),
        Some("- Marks recorded 2026-01-02 (x)")
    );
    assert_eq!(found[0].body, ["- body", ""]);
    assert_eq!(found[1].id, "H2");
    assert!(Block::Text("x".to_owned()).item_mut().is_none());
}

#[test]
fn marks_are_read_and_written_in_their_form() {
    let text = "### 1. A\n\n- Mark: [x] downloaded | [X] partial (abstract or excerpt) | [ ] paywalled | [ ] not found\n- [x] Found elsewhere (only with downloaded or partial) - where: a shop \n- Saved as (optional, the file's name): f.pdf\n- body";
    let blocks = parse(text);
    let marks = entries(&blocks).next().unwrap().marks.clone().unwrap();
    assert!(marks.downloaded && marks.partial && !marks.paywalled && marks.elsewhere);
    assert_eq!(
        (marks.where_from.as_str(), marks.saved.as_str()),
        ("a shop", "f.pdf")
    );
    assert!(marks.lines()[1].ends_with("where: a shop") && marks.lines()[2].ends_with(" f.pdf"));
    // a lookalike: no blank line, or a mark line out of its form, leaves the lines in the body
    for odd in ["### 1. A\n- Mark: nope\n\n\n\n", "### 1. A\n\nnot a mark\nx\ny\nz\n", "### 1. A\n\n- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found\nnot two\nx\n", "### 1. A\n\n- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found\n- [ ] Found elsewhere (only with downloaded or partial) - where:\nnot three\n"] {
        let blocks = parse(odd);
        assert!(entries(&blocks).next().unwrap().marks.is_none(), "{odd}");
    }
}

#[test]
fn contradictions_and_their_resolution() {
    let m = |f: fn(&mut Marks)| {
        let mut marks = Marks::default();
        f(&mut marks);
        marks
    };
    assert!(m(|x| x.elsewhere = true)
        .problem()
        .contains("found elsewhere"));
    assert!(m(|x| {
        x.not_found = true;
        x.paywalled = true;
    })
    .problem()
    .contains("not found"));
    assert_eq!(m(|x| x.partial = true).problem(), "");
    assert!(m(|x| x.downloaded = true).any() && !Marks::default().any());
    let ticked = Marks {
        not_found: true,
        downloaded: true,
        elsewhere: true,
        where_from: "w".to_owned(),
        saved: "s".to_owned(),
        ..Marks::default()
    };
    let done = ticked.resolved("downloaded").unwrap();
    assert!(
        done.downloaded
            && !done.not_found
            && done.elsewhere
            && done.where_from == "w"
            && done.saved == "s"
    );
    let gone = ticked.resolved("not-found").unwrap();
    assert!(
        gone.not_found && !gone.elsewhere && gone.where_from.is_empty() && gone.saved.is_empty()
    );
    assert!(
        ticked.resolved("paywalled").unwrap().paywalled
            && ticked.resolved("partial").unwrap().partial
    );
    assert_eq!(
        ticked.resolved("bad").unwrap_err(),
        "MARK= takes one of downloaded, partial, paywalled, not-found, not 'bad'"
    );
}

#[test]
fn a_later_id_overwrites_at_the_first_position() {
    let text = "### 1. A\nfirst\n### 2. B\nx\n### 1. C\nsecond\n";
    let blocks = parse(text);
    let (order, at) = by_id(&blocks);
    assert_eq!(order, ["1", "2"]);
    assert_eq!(
        super::parse::entry_ref(&blocks, at["1"]).heading,
        "### 1. C"
    );
}

#[test]
fn merge_records_marks_and_holds_text_edits() {
    let e = |id, body| entry_text(id, id, body);
    let canon = [
        e("1", "body"),
        e("2", "body"),
        e("3", "body"),
        e("4", "session"),
        e("5", "body"),
        e("6", "body"),
    ]
    .join("\n");
    let base = [
        e("1", "body"),
        e("2", "body"),
        e("3", "body"),
        e("4", "body"),
        e("5", "body"),
        e("6", "body"),
    ]
    .join("\n");
    let tick = |id: &str, body: &str, line1: &str| {
        format!("### {id}. {id}\n\n{line1}\n- [ ] Found elsewhere (only with downloaded or partial) - where:\n- Saved as (optional, the file's name): s{id}.pdf\n{body}\n")
    };
    let mark = "- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found";
    let bad = "- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [x] not found";
    let copy = [
        tick("1", "body", mark),
        tick("2", "body", bad),
        e("3", "edited"),
        e("4", "edited"),
        e("5", "dropped"),
        e("6", "kept"),
        e("9", "new"),
        tick("7", "body", mark),
    ]
    .join("\n");
    let canon = canon + "\n" + &e("7", "body");
    let (keep, drop, resolve) = (
        HashSet::from(["6".to_owned()]),
        HashSet::from(["5".to_owned()]),
        HashMap::new(),
    );
    let (text, out) = merge((&canon, &copy, &base), "2026-02-03", &keep, &drop, &resolve).unwrap();
    assert_eq!(out.recorded, ["1", "7"]);
    assert_eq!(out.refused[0].0, "2");
    assert_eq!(out.pending.len(), 3);
    assert_eq!(
        out.pending[0].1.lines().next().unwrap(),
        "--- at the last sync"
    );
    assert!(out.pending[1].1.starts_with("CONFLICT"));
    assert_eq!(out.pending[2].0, "7");
    assert_eq!(out.dropped, ["5"]);
    assert_eq!(out.kept, ["6"]);
    assert_eq!(out.unknown, ["9"]);
    assert_eq!(out.saved.len(), 3);
    assert!(text.contains("- Marks recorded 2026-02-03"));
    assert!(text.contains("kept") && !text.contains("dropped"));
    // a named resolution records the state the GM meant; a bad one refuses before anything is written
    let resolve = HashMap::from([("2".to_owned(), "downloaded".to_owned())]);
    let (_, out) = merge((&canon, &copy, &base), "d", &keep, &drop, &resolve).unwrap();
    assert!(out.recorded.contains(&"2".to_owned()) && out.refused.is_empty());
    let resolve = HashMap::from([("2".to_owned(), "bad".to_owned())]);
    assert!(merge((&canon, &copy, &base), "d", &keep, &drop, &resolve).is_err());
    // a resolve naming marks that do not contradict changes nothing
    let resolve = HashMap::from([("1".to_owned(), "partial".to_owned())]);
    let (text, _) = merge((&canon, &copy, &base), "d", &keep, &drop, &resolve).unwrap();
    assert!(text.contains("[x] downloaded"));
}

#[test]
fn a_copy_entry_the_base_lacks_is_a_pending_text_edit() {
    let e = |id, body| entry_text(id, id, body);
    let (keep, drop, resolve) = no_sets();
    let (_, out) = merge(
        (&e("1", "a"), &e("1", "b"), "# nothing\n"),
        "d",
        &keep,
        &drop,
        &resolve,
    )
    .unwrap();
    assert_eq!(out.pending.len(), 1);
    assert!(!out.pending[0].1.starts_with("CONFLICT"));
}

fn synced(tag: &str, canon: &str) -> (PathBuf, PathBuf) {
    let root = repo(tag);
    let inbox = scratch(&format!("{tag}-inbox"));
    put(&root, CANON, canon);
    access(&root);
    commit(&root);
    (root, inbox)
}

#[test]
fn sync_writes_the_copy_then_refuses_changes_not_ingested() {
    let canon = format!("# T\n\n{}", entry_text("1", "A", "- body"));
    let (root, inbox) = synced("sync", &canon);
    let c = ctx(&root, &inbox);
    let commit_id = sync(&c, "2026-03-04").unwrap();
    assert_eq!(commit_id, head(&root));
    assert_eq!(std::fs::read_to_string(&c.copy).unwrap(), canon);
    let state = std::fs::read_to_string(root.join(STATE)).unwrap();
    assert!(state.contains("\"synced\": {\n  \"commit\""));
    // an unchanged copy syncs again
    assert!(sync(&c, "2026-03-05").is_ok());
    // the copy changed: named, with the ingest fix
    std::fs::write(&c.copy, canon.replace("[ ] downloaded", "[x] downloaded")).unwrap();
    assert!(sync(&c, "d").unwrap_err().starts_with(
        "the GM's copy holds changes not yet ingested: 1 - run `make downloads-ingest`"
    ));
    // and an entry it holds that the list lacks, and text outside any entry
    std::fs::write(&c.copy, format!("{canon}{}", entry_text("2", "B", "x"))).unwrap();
    assert!(sync(&c, "d")
        .unwrap_err()
        .contains("2 (not in the canonical list"));
    std::fs::write(&c.copy, format!("# Another title\n{canon}")).unwrap();
    assert!(sync(&c, "d")
        .unwrap_err()
        .contains("text outside any entry"));
    // before any sync, the other lead and fix
    std::fs::remove_file(root.join(STATE)).unwrap();
    let err = sync(&c, "d").unwrap_err();
    assert!(
        err.starts_with("the GM's copy changed since the import, before any sync")
            && err.contains("then sync")
    );
    // uncommitted changes to the list refuse
    std::fs::remove_file(&c.copy).unwrap();
    put(&root, CANON, &format!("{canon}x"));
    assert!(sync(&c, "d").unwrap_err().contains("uncommitted changes"));
}

#[test]
fn ingest_records_marks_and_the_state_only_when_clean() {
    let canon = format!("# T\n\n{}", entry_text("1", "A", "- body"));
    let (root, inbox) = synced("ingest", &canon);
    let c = ctx(&root, &inbox);
    let (keep, drop, resolve) = no_sets();
    assert!(ingest(&c, &keep, &drop, &resolve, "d")
        .unwrap_err()
        .contains("never been synced"));
    sync(&c, "2026-03-04").unwrap();
    std::fs::write(&c.copy, canon.replace("[ ] downloaded", "[x] downloaded")).unwrap();
    let out = ingest(&c, &keep, &drop, &resolve, "2026-03-06").unwrap();
    assert_eq!(out.recorded, ["1"]);
    assert!(std::fs::read_to_string(root.join(STATE))
        .unwrap()
        .contains("\"ingested\""));
    assert!(std::fs::read_to_string(root.join(CANON))
        .unwrap()
        .contains("- Marks recorded 2026-03-06"));
    // a pending text edit leaves the state unwritten
    std::fs::remove_file(root.join(STATE)).unwrap();
    let was = std::fs::read_to_string(&c.copy).unwrap();
    std::fs::write(&c.copy, was.replace("- body", "- edited")).unwrap();
    put(
        &root,
        STATE,
        &format!("{{\"synced\": {{\"commit\": \"{}\"}}}}", head(&root)),
    );
    let out = ingest(&c, &keep, &drop, &resolve, "d").unwrap();
    assert_eq!(out.pending.len(), 1);
    assert!(!std::fs::read_to_string(root.join(STATE))
        .unwrap()
        .contains("\"ingested\""));
}

#[test]
fn a_sync_recorded_before_the_329_move_is_read_at_the_old_path() {
    let root = repo("pre329");
    let inbox = scratch("pre329-inbox");
    let old = format!("# T\n\n{}", entry_text("1", "A", "- body"));
    put(&root, &format!(".claude/skills/diagram/{CANON}"), &old);
    commit(&root);
    let past = head(&root);
    put(&root, CANON, &old);
    access(&root);
    commit(&root);
    let c = ctx(&root, &inbox);
    put(
        &root,
        STATE,
        &format!("{{\"synced\": {{\"commit\": \"{past}\"}}}}"),
    );
    std::fs::write(&c.copy, &old).unwrap();
    let (keep, drop, resolve) = no_sets();
    assert!(ingest(&c, &keep, &drop, &resolve, "d").is_ok());
    put(&root, STATE, "{\"synced\": {\"commit\": \"nope\"}}");
    assert!(ingest(&c, &keep, &drop, &resolve, "d")
        .unwrap_err()
        .contains("cannot be read"));
}

#[test]
fn the_report_names_what_happened() {
    let root = repo("report");
    access(&root);
    let out = IngestResult {
        recorded: owned(&["1", "2"]),
        refused: vec![("3".to_owned(), "why".to_owned())],
        pending: vec![("4".to_owned(), "the diff".to_owned())],
        kept: owned(&["5"]),
        dropped: Vec::new(),
        unknown: owned(&["9"]),
        saved: vec![("1".to_owned(), "a.pdf".to_owned())],
    };
    put(
        &root,
        "research/sources/010-works-cited/0010-key-one.html",
        "<h3 id=\"key-one\">x</h3>\n",
    );
    put(&root, CANON, &entry_text("1", "`key-one`", "- body"));
    let (text, code) = report(&out, &root).unwrap();
    assert_eq!(code, 1);
    assert!(text.contains("downloads: ingest - marks recorded on 2 entries (1, 2)"));
    assert!(text.contains("  NOT RECORDED 3: why - ask the GM which they meant, then MARK=3=<downloaded|partial|paywalled|not-found>"));
    assert!(text.contains("  NOT IN THE LIST 9"));
    assert!(text
        .contains("  TEXT EDIT 4 - pending; KEEP=4 records it, DROP=4 discards it:\nthe diff\n"));
    assert!(text.contains("  text kept: 5; dropped: -"));
    assert!(text.contains("  saved-as files named: 1=a.pdf"));
    assert!(text.contains(
        "  access key-one: never-read (no date) - no READ in its registry entry and no archive row"
    ));
    assert!(text.contains("  access download:2: never-read (no date)"));
    assert!(text.ends_with("; sync stays refused until nothing is pending\n"));
    let quiet = IngestResult {
        dropped: owned(&["1"]),
        ..IngestResult::default()
    };
    let (text, code) = report(&quiet, &root).unwrap();
    assert_eq!(code, 0);
    assert!(text.starts_with("downloads: ingest - marks recorded on 0 entries\n"));
    assert!(text.contains("  text kept: -; dropped: 1"));
    assert!(text.ends_with(&format!("  commit {CANON} and {STATE}\n")));
    let empty = IngestResult::default();
    assert!(!report(&empty, &root).unwrap().0.contains("text kept"));
}

#[test]
fn inbox_matches_only_names_present_files() {
    let inbox = scratch("matches");
    put(&inbox, "here.pdf", "x");
    let saved = vec![
        ("1".to_owned(), "here.pdf".to_owned()),
        ("2".to_owned(), "gone.pdf".to_owned()),
        ("3".to_owned(), "a/b.pdf".to_owned()),
    ];
    assert_eq!(
        inbox_matches(&saved, &inbox),
        [("1".to_owned(), "here.pdf".to_owned())]
    );
}

#[test]
fn the_push_check_holds_the_list_append_only() {
    let one = format!("# T\n\n{}", entry_text("1", "A", "- body"));
    let two = format!("{one}{}", entry_text("2", "B", "- b"));
    assert!(problems(Some(&one), &two).is_empty());
    assert!(problems(None, &one).is_empty());
    assert!(problems(Some(&two), &one)[0].starts_with("entries 2 are gone"));
    let swapped = format!(
        "# T\n\n{}{}",
        entry_text("2", "B", "- b"),
        entry_text("1", "A", "- body")
    );
    assert!(problems(Some(&two), &swapped)
        .iter()
        .any(|p| p.contains("reordered")));
    let doubled = format!("{one}{}", entry_text("1", "A", "- body"));
    assert!(problems(None, &doubled)[0].starts_with("entry 1 appears twice"));
    let bare = format!("{one}### 3. C\n\n- c\n");
    assert!(problems(Some(&one), &bare)[0].contains("no mark lines"));
    let high = format!("{one}{}", entry_text("H1", "H", "- h"));
    assert!(problems(Some(&one), &high)[0].contains("entry H1 is not appended"));
    let low = format!("{}{one}", entry_text("0", "Z", "- z"));
    assert!(problems(Some(&one), &low)[0].contains("entry 0 is not appended"));
    let root = repo("check");
    assert!(check(&root, "origin/main").is_empty());
    put(&root, CANON, &one);
    commit(&root);
    assert!(check(&root, "HEAD").is_empty());
    assert!(check(&root, "no-such-ref").is_empty());
    put(&root, CANON, "# T\n");
    assert!(check(&root, "HEAD")[0].contains("gone"));
}

#[test]
fn the_selftest_passes_and_a_failure_is_named() {
    assert!(selftest_failures().is_empty());
    assert_eq!(failing(&[(true, "a"), (false, "b")]), ["b"]);
    assert_eq!(selftest(&[]).code, 0);
    let bad = selftest(&["a thing"]);
    assert_eq!(
        (bad.code, bad.stderr.as_str()),
        (1, "downloads selftest: a thing\n")
    );
}

fn draft(title: &str, pointer: &str) -> String {
    format!("### NEW. {title}\n- **[t](https://a)**\n- Fallback: see [x](https://b)\n- **Rests on it:** {pointer}\n- Blocked by: none\n")
}

#[test]
fn add_takes_the_next_number_across_the_clones_and_the_ledger() {
    let mirror = repo("addm");
    put(
        &mirror,
        CANON,
        &format!("# T\n\n{}", entry_text("3", "A", "- a")),
    );
    let clones = mirror.join(".clones");
    let root = clones.join("mine");
    let other = clones.join("other");
    std::fs::create_dir_all(&root).unwrap();
    put(
        &root,
        CANON,
        &format!("# T\n\n{}", entry_text("3", "A", "- a")),
    );
    put(&other, CANON, &entry_text("7", "O", "- o"));
    put(
        &root,
        "research/questions/0001-q.html",
        "<!-- tags: subject=money, x; -->",
    );
    put(
        &root,
        "research/questions/0002-r.html",
        "<!-- tags: subject=houses; -->",
    );
    let c = ctx(&root, &scratch("addm-inbox"));
    let text = draft("Moneyed", "research/questions/0001-q.html")
        + &draft("Plain", "research/questions/0002-r.html");
    let ids = add::add(&c, &text).unwrap();
    assert_eq!(ids, ["8", "9"]);
    let list = std::fs::read_to_string(root.join(CANON)).unwrap();
    assert!(list.contains("### 8. [money] Moneyed") && list.contains("### 9. [diagram] Plain"));
    let ledger = std::fs::read_to_string(mirror.join(".specify/download-ids.jsonl")).unwrap();
    assert!(ledger.starts_with("{\"n\": 8, \"clone\": ") && ledger.contains("+00:00"));
    // the ledger holds a number past every list: the next add sees it, and a bad row refuses
    put(&mirror, ".specify/download-ids.jsonl", "{\"n\": 40}\n\n");
    assert_eq!(
        add::add(&c, &draft("T", "research/contents.json#a-section")).unwrap(),
        ["41"]
    );
    put(&mirror, ".specify/download-ids.jsonl", "not json\n");
    assert!(add::add(&c, &draft("T", "research/contents.json#a-section")).is_err());
}

#[test]
fn a_held_lock_is_a_refusal_naming_the_file() {
    let root = repo("addlock");
    put(&root, CANON, "# T\n");
    let mut c = ctx(&root, &scratch("addlock-inbox"));
    c.timeout = 0.05;
    let path = root.join(".specify/download-ids.lock");
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    let held = std::fs::OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .open(&path)
        .unwrap();
    assert!(l7r_guard::shared::tool::flock(&held, "-n"));
    let err = add::add(&c, &draft("T", "research/contents.json#a-section")).unwrap_err();
    assert!(
        err.starts_with("could not take the prefix lock within 0.05s:") && err.contains("(fuser ")
    );
    drop(held);
}

#[test]
fn a_draft_is_checked_for_its_parts() {
    let root = repo("drafts");
    put(&root, CANON, "# T\n");
    let c = ctx(&root, &scratch("drafts-inbox"));
    assert_eq!(
        add::add(&c, "  \n").unwrap_err(),
        "the draft holds no `### NEW. <the work>` entry"
    );
    assert!(add::add(&c, "not a heading\n")
        .unwrap_err()
        .contains("is headed `### NEW."));
    let err = add::add(&c, "### NEW. Empty\n").unwrap_err();
    for part in [
        "a link line",
        "`- Fallback:`",
        "`- **Rests on it:**`",
        "`- Blocked by:`",
        "a pointer in Rests on it",
    ] {
        assert!(err.contains(part), "{part}: {err}");
    }
    assert!(err.starts_with("draft entry 'Empty' lacks:"));
    let err = add::add(&c, &draft("T", "research/questions/9999-none.html")).unwrap_err();
    assert!(err.contains("pointers that exist (research/questions/9999-none.html - none such)"));
    // an unknown section, a page with no subject and a missing page are all diagram; the money section is money
    let list = "research/contents.json#money research/questions/9999-none.html".to_owned();
    assert!(
        add::tag_all(&format!("{}{list}\n", "### 1. T\n"), &root.join("research"))
            .contains("[money]")
    );
    let text = "### 2. [money] Old\nresearch/questions/9999-none.html\n### 3. X\nresearch/contents.json#other\n";
    let tagged = add::tag_all(text, &root.join("research"));
    assert!(tagged.contains("### 2. [diagram] Old") && tagged.contains("### 3. [diagram] X"));
    assert!(tagged.contains("research/contents.json#other"));
}

#[test]
fn the_import_writes_the_list_once_and_the_status_table_ticks() {
    let gm = "# Title\nintro\n### 1. Done\n- body\n### 7. Closed\n- b\n### 20. Open\n- b\n";
    let hr = "# High\n### H1. H\n- h\n\n";
    let text = add::import_list(gm, hr);
    assert!(text.starts_with("# Title\n\n**This is the canonical list"));
    assert!(text.contains("<!-- high-risk: imported from specs/312-uncited-source-catalog/high-risk-sources.md -->\n## High\n"));
    let blocks = parse(&text);
    let by_name: HashMap<&str, &Entry> = entries(&blocks).map(|e| (e.id.as_str(), e)).collect();
    assert!(by_name["1"].marks.as_ref().unwrap().downloaded && by_name["1"].recorded.is_some());
    assert!(by_name["7"].marks.as_ref().unwrap().not_found && by_name["7"].recorded.is_some());
    assert!(!by_name["20"].marks.as_ref().unwrap().any() && by_name["20"].recorded.is_none());
    assert!(!by_name["H1"].marks.as_ref().unwrap().any());
}

#[test]
fn options_read_both_spellings_and_refuse_the_rest() {
    let (found, plain) = options(
        &owned(&["--keep", "1 2", "--drop=3", "word"]),
        &["keep", "drop"],
    )
    .unwrap();
    assert_eq!(option(&found, "keep", ""), "1 2");
    assert_eq!(option(&found, "drop", ""), "3");
    assert_eq!(option(&found, "mark", "z"), "z");
    assert_eq!(plain, ["word"]);
    assert!(options(&owned(&["--nope", "1"]), &["keep"]).is_none());
    assert!(options(&owned(&["--keep"]), &["keep"]).is_none());
}

#[test]
fn state_keys_are_sorted_as_sort_keys_writes_them() {
    let v = serde_json::json!({"b": {"d": 1, "c": 2}, "a": [1]});
    assert_eq!(
        crate::logs::py_dumps(&sorted(&v), 1, true),
        "{\n \"a\": [\n  1\n ],\n \"b\": {\n  \"c\": 2,\n  \"d\": 1\n }\n}"
    );
    assert_eq!(today().len(), 10);
}

fn run(args: &[&str], c: &Ctx) -> crate::Reply {
    cli_at(&owned(args), c)
}

#[test]
fn every_verb_answers_through_the_command_line() {
    let canon = format!(
        "# T\n\n{}",
        entry_text("1", "`alpha`", "- body research/contents.json#money")
    );
    let (root, inbox) = synced("verbs", &canon);
    let mut c = ctx(&root, &inbox);
    assert_eq!(run(&["nonsense"], &c).code, 2);
    assert_eq!(run(&[], &c).code, 2);
    assert_eq!(run(&["add"], &c).code, 2);
    assert_eq!(run(&["sync", "extra"], &c).code, 2);
    assert_eq!(run(&["sync", "--what=1"], &c).code, 2);
    assert_eq!(run(&["selftest"], &c).code, 0);
    let tagged = run(&["tag"], &c);
    assert_eq!(
        tagged.stdout,
        "downloads: tagged 1 entries - 1 money, 0 diagram\n"
    );
    let added = run(&["add", "/no/such/file.md"], &c);
    assert!(
        added.code == 1
            && added
                .stderr
                .starts_with("downloads: REFUSED - /no/such/file.md:")
    );
    put(
        &root,
        "drafts/d.md",
        &draft("T", "research/contents.json#a-section"),
    );
    let added = run(&["add", "drafts/d.md"], &c);
    assert_eq!(
        added.stdout,
        format!("downloads: appended 2 to {CANON} - commit it; the GM sees it at the next sync\n")
    );
    let abs = root.join("drafts/d.md").display().to_string();
    assert_eq!(run(&["add", &abs], &c).code, 0);
    git(&root, &["checkout", "-q", CANON]);
    assert_eq!(run(&["check", "--base", "HEAD"], &c).code, 0);
    put(&root, CANON, "# T\n");
    let refused = run(&["check", "--base", "HEAD"], &c);
    assert!(refused.code == 1 && refused.stderr.starts_with("downloads: entries 1 are gone"));
    git(&root, &["checkout", "-q", CANON]);
    let synced_out = run(&["sync"], &c);
    assert!(synced_out
        .stdout
        .starts_with("downloads: the GM's copy replaced from research/to-download.md at "));
    // ingest: the marks recorded, a saved file passed to the archive step, its exit joined to the report's
    std::fs::write(
        &c.copy,
        canon
            .replace("[ ] downloaded", "[x] downloaded")
            .replace("name):", "name): f.pdf"),
    )
    .unwrap();
    put(&inbox, "f.pdf", "x");
    let argv = inbox.join("argv");
    let stub = inbox.join("stub");
    crate::write_executable(
        &stub,
        &format!(
            "#!/bin/sh\necho child out\necho child err >&2\necho \"$@\" > {}\nexit 0\n",
            argv.display()
        ),
    );
    c.python = stub.display().to_string();
    let ingested = run(
        &[
            "ingest",
            "--keep",
            "",
            "--drop",
            "",
            "--mark",
            "1=downloaded junk",
        ],
        &c,
    );
    assert_eq!(ingested.code, 0, "{}", ingested.stderr);
    assert!(
        ingested.stdout.contains("marks recorded on 1 entries (1)")
            && ingested.stdout.ends_with("child out\n")
    );
    assert_eq!(ingested.stderr, "child err\n");
    let seen = std::fs::read_to_string(&argv).unwrap();
    assert!(seen.contains("scripts/record/archive_ops.py inbox --match=f.pdf=1"));
    crate::write_executable(&stub, "#!/bin/sh\nexit 7\n");
    assert_eq!(run(&["ingest"], &c).code, 7);
    c.python = inbox.join("no-such-interpreter").display().to_string();
    assert_eq!(run(&["ingest"], &c).code, 1);
}

#[test]
fn import_runs_once_through_the_command_line() {
    let root = repo("import");
    let inbox = scratch("import-inbox");
    let c = ctx(&root, &inbox);
    put(
        &root,
        "specs/312-uncited-source-catalog/high-risk-sources.md",
        "# High\n### H1. H\n- h\n",
    );
    put(&inbox, "TO-DOWNLOAD.md", "# Title\n### 1. Done\n- b\n");
    put(&root, "research/.keep", "");
    let done = run(&["import"], &c);
    assert_eq!(
        done.stdout,
        format!("downloads: imported 2 entries into {CANON}\n")
    );
    assert!(std::fs::read_to_string(root.join(STATE))
        .unwrap()
        .contains("\"imported\""));
    let again = run(&["import"], &c);
    assert_eq!(
        again.stderr,
        format!("downloads: REFUSED - {CANON} exists - the import runs once\n")
    );
    let other = inbox.join("named.md");
    std::fs::write(&other, "# Title\n").unwrap();
    std::fs::remove_file(root.join(CANON)).unwrap();
    assert_eq!(
        run(
            &[
                "import",
                "--gm",
                &other.display().to_string(),
                "--high-risk",
                "specs/312-uncited-source-catalog/high-risk-sources.md"
            ],
            &c
        )
        .code,
        0
    );
}

#[test]
fn a_named_mark_that_is_not_a_state_refuses_before_anything_is_written() {
    let canon = format!("# T\n\n{}", entry_text("1", "A", "- body"));
    let (root, inbox) = synced("badmark", &canon);
    let c = ctx(&root, &inbox);
    sync(&c, "2026-03-04").unwrap();
    std::fs::write(
        &c.copy,
        canon
            .replace("[ ] downloaded", "[x] downloaded")
            .replace("[ ] not found", "[x] not found"),
    )
    .unwrap();
    let resolve = HashMap::from([("1".to_owned(), "nope".to_owned())]);
    let (keep, drop, _) = no_sets();
    let err = ingest(&c, &keep, &drop, &resolve, "d").unwrap_err();
    assert!(err.starts_with("MARK= takes one of"));
    assert_eq!(std::fs::read_to_string(root.join(CANON)).unwrap(), canon);
}

#[test]
fn a_line_that_is_no_heading_is_left_as_it_stands() {
    assert_eq!(add::tagged("plain text", "money"), "plain text");
}

#[test]
fn a_bad_state_file_refuses() {
    let root = repo("badstate");
    put(&root, CANON, "# T\n");
    put(&root, STATE, "not json");
    let c = ctx(&root, &scratch("badstate-inbox"));
    assert!(sync(&c, "d").is_err());
}

#[test]
fn the_command_line_reads_the_gm_s_inbox_from_the_environment() {
    let root = crate::checks::scratch("downloads-cli");
    assert_eq!(super::cli(&["no-such-verb".to_owned()], &root).code, 2);
}
