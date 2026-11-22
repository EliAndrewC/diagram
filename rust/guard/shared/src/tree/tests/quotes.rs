//! 451 T112: a quoted string read in time by the walk. `QUOTED` (`(?s)(["'])((?:\\.|(?!\1).)*)\1`) took a backslash and the
//! character after it, or the backslash alone, so a quote no later quote closes, followed by n backslashes, cost its backtracking
//! search 2^n tries: `<a write>; echo it's` and forty escapes, the write each guard reads, held the house style guard, main-tree,
//! gm-tree, make-only, readme, gate-write (while a `make done` ran) and the event log's end past 10 s, killed (measured 2026-11-21,
//! the T112 plan section). The command is walked here in a process of its own - this test run again as that process - under a deadline.

use super::super::{
    blanked, held, pairs_within, plain_quote_body, quotes_to_paths, unheld, walk, PYTHON_C_BEFORE,
};
use super::answers_in_time;

/// The variable that makes a child run walk the command.
const CHILD: &str = "L7R_TREE_QUOTE_IN_TIME";

/// A write, then a quote no later quote closes and forty escapes: 2^40 tries for the backtracking search.
fn unclosed() -> String {
    format!("echo hi > f.md; echo it's {}", "\\n".repeat(40))
}

#[test]
fn a_quote_no_later_quote_closes_is_walked_in_time() {
    if std::env::var_os(CHILD).is_some() {
        let w = walk(&unclosed(), Some("/w"), "", "/home/u");
        let paths: Vec<_> = w.targets.iter().map(|t| t.path.clone()).collect();
        println!("T112 walked {paths:?}");
        return;
    }
    let name = "tree::tests::quotes::a_quote_no_later_quote_closes_is_walked_in_time";
    let (passed, said) = answers_in_time(name, CHILD, 10);
    assert!(passed, "the walk did not answer in 10 s: {said}");
    let walked = said.contains(r#"T112 walked [Some("/w/f.md")]"#);
    assert!(walked, "{said}");
}

/// What `quotes_to_paths` makes of a command with `QUOTED`, the pattern it replaced, built here: its replacement as it stood, but a
/// body that is no plain word held as one word (451 T83), where it was blanked to an empty pair - no piece below holds a parenthesis
/// or a backquote, so every body pairs within itself (`pairs_within`) and none is blanked for its command's sake.
fn by_the_pattern(pattern: &fancy_regex::Regex, cmd: &str) -> (String, Vec<(char, String)>) {
    let mut programs = Vec::new();
    let text = pattern
        .replace_all(cmd, |c: &fancy_regex::Captures| {
            let body = c.get(2).map_or("", |m| m.as_str());
            let quote = c.get(1).map_or("", |m| m.as_str());
            let at = c.get(0).map_or(0, |m| m.start());
            if PYTHON_C_BEFORE.is_match(&cmd[..at]) {
                programs.push((quote.chars().next().unwrap_or('"'), body.to_owned()));
                format!("__py_c_{}__", programs.len() - 1)
            } else if body.is_empty() {
                quote.repeat(2)
            } else if plain_quote_body(body) {
                body.to_owned()
            } else {
                held(quote.chars().next().unwrap_or('"'), body)
            }
        })
        .into_owned();
    (text, programs)
}

/// The scan's reading is the pattern's on every text of up to 6 pieces over a double and a single quote, a backslash, a letter, a
/// newline (a body that is no plain word), a character of two bytes and a `python3 -c ` (a program carried out), and on the empty
/// text: the text it leaves and the programs it carries out.
#[test]
fn the_scan_reads_each_quoted_string_as_the_pattern_read_it() {
    let pattern = crate::regex::build(r#"(?s)(["'])((?:\\.|(?!\1).)*)\1"#).unwrap();
    let pieces = ["\"", "'", "\\", "a", "\n", "é", "python3 -c "];
    let mut texts = vec![String::new()];
    let mut longest = vec![String::new()];
    for _ in 0..6 {
        longest = longest
            .iter()
            .flat_map(|t| pieces.map(|p| format!("{t}{p}")))
            .collect();
        texts.extend(longest.iter().cloned());
    }
    for text in &texts {
        let (scan, old) = (
            quotes_to_paths(text, Vec::new()),
            by_the_pattern(&pattern, text),
        );
        assert_eq!(scan, old, "{text:?}");
    }
}

type Place = (Option<String>, &'static str, &'static str);

/// (path, class, how) of each write of a walk standing in `at`, the mirror `m`, the home `/home/u`.
fn writes(cmd: &str, at: &str, m: &str) -> Vec<Place> {
    let w = walk(cmd, Some(at), m, "/home/u");
    w.targets
        .into_iter()
        .map(|t| (t.path, t.class, t.how))
        .collect()
}

fn at(path: &str, class: &'static str, how: &'static str) -> Place {
    (Some(path.to_owned()), class, how)
}

/// 451 T83: a quoted destination that holds a space or a shell character is the one word its quotes make. Found by T79 (2026-11-21):
/// standing in `/tmp`, `cp /tmp/a "<mirror>/x y"`, `echo x > "<mirror>/a b"` and `mv /tmp/a "<mirror>/(x)"` were let through by
/// main-tree while `cp /tmp/a <mirror>/x` was refused - the body blanked, the copy's destination read from the word before it.
#[test]
fn a_quoted_destination_is_the_word_its_quotes_make() {
    let (_d, m, c) = super::mirror("held");
    let (xy, ab, px) = (format!("{m}/x y"), format!("{m}/a b"), format!("{m}/(x)"));
    let cases = [
        (
            format!("cp /tmp/a \"{m}/x y\""),
            vec![at(&xy, "main", "named")],
        ),
        (
            format!("cp /tmp/a '{m}/x y'"),
            vec![at(&xy, "main", "named")],
        ),
        (
            format!("cp /tmp/a {m}/\"x y\""),
            vec![at(&xy, "main", "named")],
        ),
        (
            format!("echo x > \"{m}/a b\""),
            vec![at(&ab, "main", "named")],
        ),
        (
            format!("echo x >> \"{m}/a b\" 2>&1"),
            vec![at(&ab, "main", "named")],
        ),
        (
            format!("mv /tmp/a \"{m}/(x)\""),
            vec![at("/tmp/a", "elsewhere", "named"), at(&px, "main", "named")],
        ),
        (
            format!("echo x | tee -a \"{m}/a;b\""),
            vec![at(&format!("{m}/a;b"), "main", "named")],
        ),
        (
            format!("sed -i \"s/a b/c/\" \"{m}/x y\""),
            vec![at(&xy, "main", "named")],
        ),
        (
            format!("touch \"{m}/a|b\""),
            vec![at(&format!("{m}/a|b"), "main", "named")],
        ),
        (
            format!("cp /tmp/a \"{c}/x y\""),
            vec![at(&format!("{c}/x y"), "clone", "named")],
        ),
        (
            format!("D={m}; cp /tmp/a \"$D/x y\""),
            vec![at(&xy, "main", "named")],
        ),
        (
            format!("D=\"{m}/x y\"; cp /tmp/a \"$D/f\""),
            vec![at(&format!("{m}/x y/f"), "main", "named")],
        ),
        (
            format!("cd \"{m}/a b\" && touch f"),
            vec![at(&format!("{m}/a b/f"), "main", "shell")],
        ),
        (
            format!("git -C \"{m}/a b\" commit -qm m"),
            vec![at(&ab, "main", "named")],
        ),
        (
            "cp /tmp/a \"/tmp/x y\"".to_owned(),
            vec![at("/tmp/x y", "elsewhere", "named")],
        ),
    ];
    for (cmd, want) in cases {
        let got = writes(&cmd, "/tmp", &m);
        assert_eq!(got, want, "{cmd}");
    }
}

/// 451 T83: a held word hides its own splitting characters from the walk - a quoted text that reads as a write is no write, a quoted
/// script is still the script - and a target's segment shows it blanked, as every guard that reads a segment was shown it before.
#[test]
fn a_held_word_hides_its_text_and_shows_its_segment_as_before() {
    let (_d, m, _c) = super::mirror("held-text");
    let cases = [
        (format!("echo \"x > {m}/f; touch {m}/g\""), vec![]),
        (
            format!("git commit -m \"a; touch {m}/g\""),
            vec![at("/tmp", "elsewhere", "shell")],
        ),
        (
            "sed -i \"s/a b/c/\" /tmp/f".to_owned(),
            vec![at("/tmp/f", "elsewhere", "named")],
        ),
        (
            format!("cp /tmp/a \"$(pwd)/x y\" && cd {m} && cp /tmp/a \"$(pwd)/x y\""),
            vec![
                at("/tmp/x y", "elsewhere", "shell"),
                at(&format!("{m}/x y"), "main", "shell"),
            ],
        ),
    ];
    for (cmd, want) in cases {
        let got = writes(&cmd, "/tmp", &m);
        assert_eq!(got, want, "{cmd}");
    }
    let w = walk(
        &format!("cp /tmp/a \"{m}/x y\" 'b c' && echo \"<<x\" > '{m}/a b'"),
        Some("/tmp"),
        &m,
        "/home/u",
    );
    let shown: Vec<&str> = w.targets.iter().map(|t| t.segment.as_str()).collect();
    assert_eq!(shown, ["cp /tmp/a \"\" ''", "echo \"\" > ''"]);
}

/// 451 T83: a stand-in reads back to the character it hides, a private-use character that hides none is kept, in a place and in
/// a shown segment, a stand-in outside a held word (an arithmetic's) is shown as what it hides, and a body whose parentheses or
/// backquotes do not pair is told apart.
#[test]
fn a_stand_in_reads_back_and_nothing_else_does() {
    let word = held('"', "/a b;{c}");
    let back = unheld(&word);
    assert_eq!(back, "/a b;{c}");
    // a double-quoted body's `$(...)` is left for the walk, its own parentheses nested, and an unclosed `$(` is hidden
    let nested = held('"', "a $(b (c)) d").contains("$(b (c))");
    assert!(nested);
    let unclosed = held('"', "x $(y").contains("$(");
    assert!(!unclosed);
    let other = "\u{F0041}/x";
    let kept = unheld(other);
    assert_eq!(kept, other);
    let seg = format!("cp \u{F0020}x {word} \u{F0041}");
    let shown = blanked(&seg);
    assert_eq!(shown, "cp  x \"\" \u{F0041}");
    let pairs: Vec<bool> = ["(a)", "a)", "(a", "`a`", "`a", "$(a (b))"]
        .iter()
        .map(|b| pairs_within(b))
        .collect();
    assert_eq!(pairs, [true, false, false, true, false, true]);
}

/// 451 T83: what holding a word would have read wrongly, measured on T79's corpus - a substitution's nested quotes, which the scan
/// pairs flat (`"$(dirname "$F")"` is `"$(dirname "`, `$F` and `")"`), read as before, its place scratch, not a place nothing is
/// known of; and a `touch` option's value, held as one word, no file written.
#[test]
fn a_piece_of_a_substitution_and_an_option_value_are_no_held_place() {
    let (_d, m, _c) = super::mirror("held-not");
    let cases = [
        (
            "F=/tmp/s/v.json; mkdir -p \"$(dirname \"$F\")\"",
            vec![at("/tmp/s/v.json", "elsewhere", "named")],
        ),
        (
            "touch -d \"2 hours ago\" /tmp/f",
            vec![at("/tmp/f", "elsewhere", "named")],
        ),
        (
            "touch -d '-600 seconds' /tmp/f -t 202611211200 /tmp/g",
            vec![
                at("/tmp/f", "elsewhere", "named"),
                at("/tmp/g", "elsewhere", "named"),
            ],
        ),
        (
            "touch -r \"/tmp/a b\" /tmp/f",
            vec![at("/tmp/f", "elsewhere", "named")],
        ),
        // one body read across a substitution, and the command's every body is read as before: its redirect's place unknown
        (
            "echo \"$(cat \"x\")\" > \"/tmp/a b\"",
            vec![(None, "main", "shell")],
        ),
    ];
    for (cmd, want) in cases {
        let got = writes(cmd, &m, &m);
        assert_eq!(got, want, "{cmd}");
    }
}

/// 451 T83: a held double-quoted body's plain `$(...)` is the substitution it is outside quotes (`mkdir -p "$(dirname $F)"` makes
/// F's directory), one holding a quote is a place nothing is known of, and a held brace is no `${` reading the command to its end.
#[test]
fn a_held_words_substitution_and_braces_read_as_outside_quotes() {
    let (_d, m, _c) = super::mirror("held-sub");
    let cases = [
        (
            "F=/tmp/s/v.json; mkdir -p \"$(dirname $F)\"",
            vec![at("/tmp/s", "elsewhere", "named")],
        ),
        (
            "F=/tmp/s/v.json; cp /tmp/a \"$(dirname $F)/x y\"",
            vec![at("/tmp/s/x y", "elsewhere", "named")],
        ),
        (
            "S=/tmp/s; echo x > \"$S/b-$(echo $a | tr -d ' -').out\"",
            vec![(None, "elsewhere", "named")],
        ),
        (
            "cp /tmp/a \"$(git rev-parse --show-toplevel)/x y\"",
            vec![(None, "main", "shell")],
        ),
        (
            "sed -i 's/a b/${#c/' /tmp/f && cp /tmp/a /tmp/g",
            vec![
                at("/tmp/f", "elsewhere", "named"),
                at("/tmp/g", "elsewhere", "named"),
            ],
        ),
        (
            "echo \"${HOME}/a b\" && cp /tmp/a \"${HOME}/x y\"",
            vec![at("/home/u/x y", "elsewhere", "named")],
        ),
    ];
    for (cmd, want) in cases {
        let got = writes(cmd, &m, &m);
        assert_eq!(got, want, "{cmd}");
    }
}

/// 451 T83: a held double-quoted body's `\$(` is an escaped dollar, no substitution, where `\\$(` is a backslash and one, and a
/// `$((` is arithmetic. Found by the walk's diff on T79's corpus (bx#57058, 2026-11-21): `bash -c "...Y='\$(touch $W/out/RAN5)'..."`,
/// a probe whose marker shows the touch never runs, read as a write of RAN5.
#[test]
fn an_escaped_dollar_and_an_arithmetic_are_no_substitution() {
    let (_d, m, _c) = super::mirror("held-escape");
    let q = at("/tmp/q", "elsewhere", "named");
    let cases = [
        ("echo \"\\$(touch /tmp/r)\"", vec![]),
        ("echo \"\\\\$(touch /tmp/q)\"", vec![q.clone()]),
        (
            "echo \"\\$(touch /tmp/r) $(touch /tmp/q)\"",
            vec![q.clone()],
        ),
        ("echo \"n=$((a > b))\"", vec![]),
        ("echo \"n=$((a > b)) $(touch /tmp/q)\"", vec![q.clone()]),
        // outside quotes, misread so before 451 T83 too: `$((o>200?o-200:1))` was a write of `200?o-200:1` (ux#1441, in the clone)
        ("echo $((a > b)) $((o>200?o-200:1))", vec![]),
        // a parenthesis inside an arithmetic nests, its `)` closing no arithmetic
        ("echo $(( (a > b) * 2 )) $(( (n) > (m) ))", vec![]),
        ("echo $(( $(touch /tmp/q; echo 1) > 0 ))", vec![q.clone()]),
        ("(( n > 3 )) && touch /tmp/q", vec![q.clone()]),
        (
            "for ((i=5; i>0; i--)); do touch /tmp/q; done",
            vec![q.clone()],
        ),
        ("if (( n > 3 )); then touch /tmp/q; fi", vec![q.clone()]),
        // as bash 5.3 reads them: an inner parenthesis closing before the outer is subshells, any other `((` arithmetic
        ("((touch /tmp/q) | wc)", vec![q.clone()]),
        ("echo $((touch /tmp/q) && echo x)", vec![q.clone()]),
        ("((cd /tmp; touch /tmp/r))", vec![]),
    ];
    for (cmd, want) in cases {
        let got = writes(cmd, "/tmp", &m);
        assert_eq!(got, want, "{cmd}");
    }
    let w = walk("echo $((a > b)) > /tmp/q", Some("/tmp"), &m, "/home/u");
    let shown: Vec<&str> = w.targets.iter().map(|t| t.segment.as_str()).collect();
    assert_eq!(shown, ["echo $((a > b)) > /tmp/q"]);
}
