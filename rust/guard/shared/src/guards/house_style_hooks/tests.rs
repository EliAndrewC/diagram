//! `hm_house.py`'s selftest shapes and the decider's branches (`tests/hooks/test-house-style-hooks.sh`, replayed through the shim, is the verdict). The forbidden words are assembled here, because this hook would correct them typed whole.

use serde_json::{json, Value};

use super::{cased, decide, exempt, plan, report, Report, EM, SPAN};
use crate::protocol::{Answer, Event};
use crate::session::Session;

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
    crate::log::quiet();
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
    // the word it names in a code span (451 T174): the record keeps the text, and the push's house-style delta check refused it bare
    let named = format!("`{WORD}` [the GM own words");
    assert!(matches!(report(&edit(path, WORD)), Report::Refused(t) if t.contains(&named)));
    // ...and a dash, named in words, bare
    let dash = report(&edit(path, "a \u{2014} b"));
    assert!(
        matches!(dash, Report::Refused(t) if t.starts_with("em-dash (U+2014) [the GM own words"))
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
    assert!(matches!(both, Report::Warned(ref t) if t.contains("BOTH spellings")));
    let got = report(&bash(&format!("echo {WORD} >> a.md")));
    assert_eq!(
        updated(&got, "command"),
        Some(format!("echo {WORD_FIXED} >> a.md"))
    );
    // 451 T170: each notice names a word in a code span, so a record keeping the notice holds no bare British word
    assert!(matches!(both, Report::Warned(t) if t.contains(&format!("payload: `{WORD}`."))));
    assert!(
        matches!(got, Report::Corrected(_, ref n, _) if n.contains(&format!("(`{WORD}` -> `{WORD_FIXED}`)")))
    );
    assert_eq!(report(&bash(&format!("grep {WORD} a.md"))), Report::Silent);
    assert_eq!(report(&bash(&format!("cat 'a {WORD}/b'"))), Report::Silent);
}

/// 451 T45: a named path is a file, never a directory on the way to one. T42's replay ran its project under `mktemp -d /tmp/t42/run.XXXX`,
/// and the one run whose letters were `run.py8Q` read `/tmp/t42/run.py` as a named file under /tmp, judged 11 project writes outside the
/// project and left them silent: the verdict turned on the temporary directory's random letters, not on the command.
#[test]
fn a_directory_whose_name_runs_past_an_extension_names_no_file() {
    let write = |dir: &str| {
        report(&bash(&format!(
            "cd /tmp/t45/{dir}/diagram/.clones/c && python3 - <<'PY'\np = 'docs/a.html'\nopen(p, 'w').write('the {WORD}')\nPY"
        )))
    };
    for dir in ["run.ab8Q", "run.py8Q", "run.sh8Q", "run.md8Q", "run.json"] {
        let got = updated(&write(dir), "command");
        assert!(got.is_some_and(|c| c.contains(WORD_FIXED)), "{dir}");
    }
}

/// ...and a file's extension keeps its letters: a scratch `.jsonl`, a transcript, a `.pyc` written from a program stay outside (a word
/// boundary in place of them turned each into a correction of text under /tmp).
#[test]
fn a_file_named_past_its_extension_is_still_named() {
    for path in [
        "/tmp/a.py",
        "/tmp/x.jsonl",
        "/home/u/.claude/projects/p/s.jsonl",
        "/tmp/x.pyc",
    ] {
        let program = format!("python3 - <<'PY'\nopen('{path}', 'w').write('the {WORD}')\nPY");
        assert_eq!(report(&bash(&program)), Report::Silent, "{path}");
    }
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

/// Feature 449 T242: a JSON record's straight quotes are no quotation to the delta check, so they are corrected; the spans it holds
/// everywhere are kept.
#[test]
fn a_record_s_text_is_americanized_straight_quotes_too() {
    let brit = format!("behavio{}", "ur");
    assert_eq!(
        super::americanize_record(&format!(
            "the {brit} \u{2013} \"{brit}\", \u{201c}{brit}\u{201d}, `{brit}`, <q>{brit}</q>"
        )),
        format!("the behavior - \"behavior\", \u{201c}{brit}\u{201d}, `{brit}`, <q>{brit}</q>")
    );
}

#[test]
fn a_json_value_is_americanized_its_keys_as_written() {
    let brit = format!("behavio{}", "ur");
    let got = super::americanize_json(&serde_json::json!({
        brit.clone(): [format!("a {brit}"), {"n": 3, "t": format!("\"{brit}\"")}], "b": null, "c": true
    }));
    assert_eq!(
        got,
        serde_json::json!({brit.clone(): ["a behavior", {"n": 3, "t": "\"behavior\""}], "b": null, "c": true})
    );
}

/// The CPU time past which a search fails its test, in nanoseconds of its own thread's: 30 s, a CONVENTION and a knob (451 T81), about
/// 10x the spelling scan's 3.2 s on the host's slowest core and 4x its 7.4 s worst with 88 copies at once (measured 2026-11-21, `taskset`
/// and 88 copies of the test binary, each timed around its process - the T81 plan section's item 4).
const CPU_BOUND_NS: u64 = 30_000_000_000;

/// `f`'s answer, or a failure once the thread running it has spent [`CPU_BOUND_NS`] on the CPU (feature 449 T185: a quadratic search,
/// or a scan over an error it repeats, must fail the test rather than hang it). The bound is the work done - that thread's own CPU time,
/// the first field of its `/proc/<pid>/task/<tid>/schedstat` - never the wall time (451 T81): a busy host stretches the wall time, not
/// the work. 20 s of wall time failed this test's good work at a load of 82, and on one CPU shared 16 ways cut the scan off after 1.2 s
/// of its CPU, where it needs 1.6 s.
fn within<T: Send + 'static>(f: impl FnOnce() -> T + Send + 'static) -> T {
    use std::sync::mpsc::{channel, RecvTimeoutError::Timeout};
    let (at, its_stat) = channel();
    let (tx, rx) = channel();
    let _run = std::thread::spawn(move || {
        let me = std::fs::read_link("/proc/thread-self");
        let _ = at.send(me.map(|t| std::path::Path::new("/proc").join(t).join("schedstat")));
        tx.send(f())
    });
    let stat = its_stat.recv().expect("it starts").expect("a Linux /proc");
    loop {
        match rx.recv_timeout(std::time::Duration::from_millis(100)) {
            Ok(answer) => return answer,
            Err(e) => assert_eq!(e, Timeout, "the search panicked"),
        }
        // A thread that sent its answer and ended since has no file: 0, and the next receive takes the answer.
        // no closure here: one that runs only while the file stands is a line no test reaches when the thread has ended
        let stat_text = std::fs::read_to_string(&stat).unwrap_or_default();
        let ns: u64 = stat_text
            .split_whitespace()
            .next()
            .unwrap_or("0")
            .parse()
            .unwrap_or(0);
        assert!(ns < CPU_BOUND_NS, "ran past its CPU bound: {ns} ns");
    }
}

/// A text past a million steps (feature 449 T185, the edit guard T151's search named): the spelling scan's `.flatten()` repeated the
/// error `fancy_regex` gave at its old limit without advancing, so the correction spun; it reads to the end. The text is past that
/// limit by the limit firing on it (451 T81), so a shorter text cannot leave this passing over a scan the limit would cut short.
#[test]
fn a_spelling_past_a_million_steps_is_corrected() {
    let text = format!("{}the {WORD}", "plain words of a long text ".repeat(50_000));
    let old_limit = crate::regex::builder(&format!(r"(?i)\b{WORD}\b"))
        .backtrack_limit(1_000_000)
        .build()
        .unwrap();
    assert!(old_limit.is_match(&text).is_err());
    assert!(within(move || super::americanize(&text)).ends_with(&format!("the {WORD_FIXED}")));
}

/// A heredoc body this guard leaves unblanked (`<<\EOF`, which `HEREDOC_BODY` does not read and the walk carries out) holding `text`
/// and then a quote no later quote closes before forty escapes: 2^40 tries for the backtracking search of a quoted string (451 T108).
fn unclosed_in_body(text: &str) -> String {
    format!(
        "cat <<\\EOF > f.md\n{WORD} {text}'{}\nEOF",
        "\\n".repeat(40)
    )
}

/// 451 T108: the separators' mask read the command's quoted strings with that search (`QUOTED_SPAN`); before the fix the guard gave
/// no answer on the command in 10 s (measured 2026-11-21, the T108 plan section), and the plan, under [`within`]'s bound, none.
#[test]
fn a_quote_nothing_closes_is_masked_in_time() {
    let (out, notes, _) = within(|| run(&unclosed_in_body("it")));
    assert!(out.contains(WORD_FIXED) && !out.contains(WORD), "{out}");
    assert!(!notes.is_empty());
}

/// 451 T108: a Python `re` call's pattern was held by the same search after its `(` (`HELD_SHAPES`); an unclosed one is read in time.
#[test]
fn a_pattern_argument_nothing_closes_is_held_in_time() {
    let (out, notes, _) = within(|| run(&unclosed_in_body("re.compile(")));
    assert!(out.contains(WORD_FIXED) && !out.contains(WORD), "{out}");
    assert!(!notes.is_empty());
}

/// Every text of up to `n` of `pieces`, the empty one among them.
fn texts_of(pieces: &[&str], n: usize) -> Vec<String> {
    let (mut texts, mut longest) = (vec![String::new()], vec![String::new()]);
    for _ in 0..n {
        longest = longest
            .iter()
            .flat_map(|t| pieces.iter().map(move |p| format!("{t}{p}")))
            .collect();
        texts.extend(longest.iter().cloned());
    }
    texts
}

/// 451 T108: the mask blanks the quoted strings the pattern it replaced (`QUOTED_SPAN`, built here) found, on every text to 6
/// characters over a double and a single quote, a backslash, a letter, a newline and a character of two bytes.
#[test]
fn the_mask_blanks_the_quoted_strings_the_pattern_found() {
    let pattern = crate::regex::build(r#"(?s)(["'])(?:\\.|(?!\1).)*\1"#).unwrap();
    for text in texts_of(&["\"", "'", "\\", "a", "\n", "é"], 6) {
        let mut bytes = text.as_bytes().to_vec();
        for m in pattern.find_iter(&text).map_while(Result::ok) {
            bytes[m.start() + 1..m.end() - 1].fill(b' ');
        }
        let (got, want) = (super::masked(&text), String::from_utf8_lossy(&bytes));
        assert_eq!(got, want, "{text:?}");
    }
}

/// 451 T108: the `re` calls' arguments are held where the shape they replaced (built here) held them, on every text of up to 5 of
/// these pieces - two calls, one with a blank before its argument, a prefix, the quotes, a backslash, a letter, a newline and `é`.
#[test]
fn a_pattern_argument_is_held_where_the_shape_held_it() {
    let shape = crate::regex::build(r#"(?s)re\.(?:compile|search|match|fullmatch|split|sub|subn|findall|finditer)\(\s*[rbuf]{0,2}(['"])(?:\\.|(?!\1).)*\1"#).unwrap();
    let pieces = [
        "re.compile(",
        "re.subn( ",
        "r",
        "'",
        "\"",
        "\\",
        "a",
        "\n",
        "é",
    ];
    for text in texts_of(&pieces, 5) {
        let want: Vec<(usize, usize)> = shape
            .find_iter(&text)
            .map_while(Result::ok)
            .map(|m| (m.start(), m.end()))
            .collect();
        let got: Vec<(usize, usize)> = super::re_call_patterns(&text)
            .into_iter()
            .map(|(a, b, _)| (a, b))
            .collect();
        assert_eq!(got, want, "{text:?}");
    }
}
