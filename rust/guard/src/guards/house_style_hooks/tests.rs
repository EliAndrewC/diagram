//! `hm_house.py`'s selftest shapes and the decider's branches (`tests/hooks/test-house-style-hooks.sh`, replayed through the shim, is the verdict). The forbidden words are assembled here, because this hook would correct them typed whole.

use serde_json::{json, Value};

use super::{cased, decide, exempt, plan, report, Report, EM, SPAN};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

const WORD: &str = concat!("col", "our");
const WORD_FIXED: &str = "color";

fn run(c: &str) -> (String, Vec<String>, Vec<String>) {
    plan(c, &SPAN)
}

fn bash(cmd: &str) -> Event {
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "cwd": "/repo", "tool_input": {"command": cmd}}),
    }
}

fn edit(path: &str, new: &str) -> Event {
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Edit", "tool_input": {"file_path": path, "new_string": new}}),
    }
}

fn answers(e: &Event) -> Vec<Answer> {
    crate::shared::log::quiet();
    decide(e, &Session::from_input(&e.input))
}

fn updated(r: &Report, key: &str) -> Option<String> {
    match r {
        Report::Corrected(v, _, _) => v.get(key).and_then(Value::as_str).map(str::to_owned),
        _ => None,
    }
}

#[test]
fn a_command_is_corrected_where_it_writes_and_left_where_it_names() {
    assert_eq!(
        run(&format!("cat > a.md <<'EOF'\nthe {WORD} of it\nEOF")).0,
        format!("cat > a.md <<'EOF'\nthe {WORD_FIXED} of it\nEOF")
    );
    assert_eq!(
        run(&format!("echo 'an {WORD} - here' >> a.md")).0,
        format!("echo 'an {WORD_FIXED} - here' >> a.md")
    );
    for named in [
        format!("! grep -qiE '{WORD}' a.md"),
        format!("echo x && grep -c {WORD} a.md"),
        format!("n=$(grep -c {WORD} a.md); echo $n"),
        format!("python3 -c \"re.compile(r'({WORD}|beta)')\""),
        format!("cat docs/{WORD}-notes.md"),
        format!("grep -n $'{EM}' a.md"),
        format!("python3 -c \"t.replace('{EM}', ' - ')\""),
        format!("echo 'the token `{WORD}` is named' >> a.md"),
        format!("python3 - <<'PY'\nWORDS = {{'{WORD}', 'beta'}}\nPY"),
        format!("python3 - <<'PY'\nparts = re.split(r'a {EM} b', t)\nPY"),
    ] {
        assert!(run(&named).1.is_empty(), "{named}");
    }
    assert_eq!(
        run(&format!("python3 - <<'PY'\nt = \"the {WORD} of it\"\nPY"))
            .1
            .len(),
        1
    );
    assert_eq!(run("echo plain").0, "echo plain");
}

#[test]
fn the_fix_shape_is_warned_on_and_left_as_typed() {
    let sed = format!("sed -i 's/{WORD}/beta/' a.md");
    assert_eq!(run(&sed), (sed.clone(), vec![], vec![WORD.to_owned()]));
    assert_eq!(
        run(&format!("git ls-files | xargs sed -i 's/{WORD}/x/'")).2,
        [WORD]
    );
    assert_eq!(run(&format!("find . -exec sed -i s/{WORD}/x/ ;")).2, [WORD]);
    assert_eq!(
        run(&format!(
            "python3 - <<'PY'\nt = t.replace('{WORD}', '{WORD_FIXED}')\nPY"
        ))
        .2,
        [WORD]
    );
}

#[test]
fn a_heredoc_landing_outside_the_project_is_held_whole() {
    let c = format!("make x && cat > /tmp/r.txt <<'EOF'\nthe {WORD}\nEOF\necho the {WORD}");
    assert_eq!(
        run(&c).0,
        format!("make x && cat > /tmp/r.txt <<'EOF'\nthe {WORD}\nEOF\necho the {WORD_FIXED}")
    );
    let unclosed = format!("cat <<'EOF' > /tmp/r.txt\nthe {WORD}");
    assert!(run(&unclosed).1.is_empty());
    let project = format!("cat > /repo/a.md <<'EOF'\nthe {WORD}\nEOF");
    assert_eq!(run(&project).1.len(), 1);
}

#[test]
fn an_edit_is_corrected_with_its_spans_held_out() {
    let got = report(&edit("/r/a.py", &format!("the {WORD} and `{WORD}`")));
    assert_eq!(
        updated(&got, "new_string"),
        Some(format!("the {WORD_FIXED} and `{WORD}`"))
    );
    let dashed = report(&edit("/r/a.py", &format!("a {EM} b")));
    assert_eq!(updated(&dashed, "new_string").as_deref(), Some("a - b"));
    assert_eq!(
        report(&edit("/r/a.md", &format!("\"the {WORD}\""))),
        Report::Silent
    );
    assert!(matches!(
        report(&edit("/r/a.py", &format!("\"the {WORD}\""))),
        Report::Corrected(..)
    ));
    assert_eq!(report(&edit("/tmp/a.md", WORD)), Report::Silent);
    assert_eq!(
        report(&edit("/r/tests/hooks/fixtures/a.json", WORD)),
        Report::Silent
    );
    assert_eq!(report(&edit("/host-l7r-repo/x.md", WORD)), Report::Silent);
    assert_eq!(report(&edit("/r/x/l7r.md", WORD)), Report::Silent);
    assert_eq!(report(&edit("/r/gm-request.md", WORD)), Report::Silent);
    assert_eq!(report(&edit("/r/CLAUDE.md", WORD)), Report::Silent);
    assert_eq!(report(&edit("/r/a.md", "")), Report::Silent);
    let source = format!("<!-- SOURCE: GM NOTES -->{WORD}<!-- END SOURCE -->");
    assert_eq!(report(&edit("/r/a.py", &source)), Report::Silent);
}

#[test]
fn the_gms_own_words_are_only_reported() {
    let path = "specs/100-x/request.md";
    assert!(
        matches!(report(&edit(path, WORD)), Report::Refused(t) if t.contains("[the GM own words"))
    );
    let warned = report(&bash(&format!("echo {WORD} >> specs/100-x/request.md")));
    assert!(matches!(warned, Report::Warned(t) if t.contains("records the GM speaking")));
}

#[test]
fn a_command_written_outside_is_silent_and_one_with_both_is_a_warning() {
    assert_eq!(
        report(&bash(&format!("echo {WORD} > /tmp/x.txt"))),
        Report::Silent
    );
    let both = report(&bash(&format!("echo {WORD} {WORD_FIXED} >> a.md")));
    assert!(matches!(both, Report::Warned(t) if t.contains("BOTH spellings")));
    let got = report(&bash(&format!("echo {WORD} >> a.md")));
    assert_eq!(
        updated(&got, "command"),
        Some(format!("echo {WORD_FIXED} >> a.md"))
    );
    assert_eq!(report(&bash(&format!("grep {WORD} a.md"))), Report::Silent);
    assert_eq!(report(&bash(&format!("cat 'a {WORD}/b'"))), Report::Silent);
}

#[test]
fn a_sed_beside_a_write_is_named_in_the_note_and_an_en_dash_is_corrected() {
    let got = report(&bash(&format!(
        "sed -i s/{WORD}/x/ a.md; echo the {WORD} >> b.md"
    )));
    assert!(
        matches!(got, Report::Corrected(_, ref n, _) if n.contains("Left as typed and NOT corrected"))
    );
    let en = report(&edit("/r/a.py", &format!("a {} b", super::EN)));
    assert_eq!(updated(&en, "new_string").as_deref(), Some("a - b"));
}

#[test]
fn the_answers() {
    assert!(matches!(
        &answers(&bash(&format!("echo {WORD} >> a.md")))[..],
        [Answer::Rewrite(_), Answer::Notice(_)]
    ));
    assert!(matches!(
        &answers(&bash(&format!("sed -i s/{WORD}/x/ a.md")))[..],
        [Answer::Notice(_)]
    ));
    assert!(
        matches!(&answers(&edit("specs/1-x/request.md", WORD))[..], [Answer::Refuse(t)] if t.contains("BLOCKED: house style") && t.contains(concat!("deme", "sne")))
    );
    assert!(answers(&bash("ls")).is_empty());
    let none = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Write"}),
    };
    assert!(answers(&none).is_empty());
}

#[test]
fn case_is_kept() {
    assert_eq!(updated(&Report::Silent, "x"), None);
    assert_eq!(cased("COLOR", "color"), "COLOR");
    assert_eq!(cased("Color", "color"), "Color");
    assert_eq!(cased("color", "color"), "color");
    assert_eq!(cased("Color", ""), "");
    assert!(exempt("a/house_style_words.tsv") && !exempt("a/other.rs"));
}

#[test]
fn a_dash_takes_the_whitespace_python_counts_around_it() {
    assert_eq!(super::americanize("a\u{1c}\u{2014}\u{1f}b"), "a - b");
    assert_eq!(super::americanize("a\u{a0}\u{2013}\u{a0}b"), "a - b");
}

#[test]
fn a_tool_s_text_is_americanized_its_quotations_held_out() {
    let (brit, us) = (format!("gr{}", "ey"), "gray");
    assert_eq!(
        super::americanize(&format!("a {brit} band, <q>a {brit} quoted</q>")),
        format!("a {us} band, <q>a {brit} quoted</q>")
    );
}
