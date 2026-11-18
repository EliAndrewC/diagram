//! The two diagnostics' command lines as `argparse` read them (feature 449 T150): positionals and options in any order, a long option
//! by any unambiguous prefix (`--pa` is `--page`), its value as the next word or after `=`, the last of a repeated option kept, `--`
//! ending the options, a word that looks like a negative number a value, and `-h`/`--help` the help. A malformed line exits 2 with
//! empty stdout, held to the Python's; argparse's own stderr wording is not bound (`ask:449-usage-text`), so the refusal is one line
//! naming the tool and the complaint.
//!
//! Research: the diagnostics' arguments - NONE: the command line read, no map decision

/// What an option takes: nothing (a flag), a value, or a value read as an `int` (refused where it is met, as argparse converts it).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Takes {
    Flag,
    Value,
    Int,
}

/// An option: its long name and what it takes.
pub type Opt = (&'static str, Takes);

/// What a line asked: the positionals in order, each option's last value (a flag's is empty), or the help.
#[derive(Debug, PartialEq, Eq)]
pub enum Parsed {
    Run {
        positionals: Vec<String>,
        options: Vec<(&'static str, String)>,
    },
    Help,
}

/// `argparse`'s `_negative_number_matcher`: `^-\d+$|^-\d*\.\d+$`.
fn negative_number(word: &str) -> bool {
    let Some(rest) = word.strip_prefix('-') else {
        return false;
    };
    let digits = |s: &str| !s.is_empty() && s.bytes().all(|b| b.is_ascii_digit());
    digits(rest)
        || rest
            .split_once('.')
            .is_some_and(|(i, f)| i.bytes().all(|b| b.is_ascii_digit()) && digits(f))
}

/// The option `word` names (`--name`, an unambiguous prefix of one, or `-h`), and the value given after `=`; none when it is a
/// positional.
fn option_of(word: &str, opts: &[Opt]) -> Result<Option<(Opt, Option<String>)>, String> {
    if word == "-h" {
        return Ok(Some((("help", Takes::Flag), None)));
    }
    if !word.starts_with('-') || word == "-" || negative_number(word) {
        return Ok(None);
    }
    let Some(long) = word.strip_prefix("--") else {
        return Ok(Some((("", Takes::Flag), None)));
    };
    let (name, value) = match long.split_once('=') {
        Some((n, v)) => (n, Some(v.to_owned())),
        None => (long, None),
    };
    let all = opts.iter().copied().chain([("help", Takes::Flag)]);
    if let Some(exact) = all.clone().find(|(n, _)| *n == name) {
        return Ok(Some((exact, value)));
    }
    let hits: Vec<Opt> = all
        .filter(|(n, _)| !name.is_empty() && n.starts_with(name))
        .collect();
    match hits.as_slice() {
        [one] => Ok(Some((*one, value))),
        [] => Ok(Some((("", Takes::Flag), None))),
        _ => Err(format!("ambiguous option: --{name}")),
    }
}

/// The line read against `opts`. An unknown option is kept aside and refused only at the end, as argparse's extras are - so a later
/// `-h` still answers with the help.
///
/// # Errors
/// The complaint argparse would exit 2 on: an unknown or ambiguous option, a missing value, a value given to a flag, an `int` that is
/// none.
pub fn parse(args: &[String], opts: &[Opt]) -> Result<Parsed, String> {
    let mut positionals = Vec::new();
    let mut options: Vec<(&'static str, String)> = Vec::new();
    let mut unknown: Vec<&str> = Vec::new();
    let mut it = args.iter();
    while let Some(word) = it.next() {
        if word == "--" {
            positionals.extend(it.by_ref().cloned());
            break;
        }
        let Some(((name, takes), given)) = option_of(word, opts)? else {
            positionals.push(word.clone());
            continue;
        };
        if name.is_empty() {
            unknown.push(word);
            continue;
        }
        if name == "help" && given.is_none() {
            return Ok(Parsed::Help);
        }
        let value = match (takes, given) {
            (Takes::Flag, None) => String::new(),
            (Takes::Flag, Some(_)) => {
                return Err(format!("argument --{name}: ignored explicit argument"))
            }
            (_, Some(v)) => v,
            (_, None) => match it.next() {
                Some(v) if !v.starts_with('-') || negative_number(v) || v == "-" => v.clone(),
                _ => return Err(format!("argument --{name}: expected one argument")),
            },
        };
        if takes == Takes::Int {
            py_int(&value).map_err(|e| format!("argument --{name}: {e}"))?;
        }
        options.retain(|(n, _)| *n != name);
        options.push((name, value));
    }
    if !unknown.is_empty() {
        return Err(format!("unrecognized arguments: {}", unknown.join(" ")));
    }
    Ok(Parsed::Run {
        positionals,
        options,
    })
}

/// `int(text)` as an `argparse` `type=int` reads it: surrounding whitespace, a sign, digits with single underscores between them; a
/// value past `i64` held at its bound (a channel delta of 0 to 255 is compared with it, so the bound answers as the true value would).
///
/// # Errors
/// Text that is no integer.
pub fn py_int(text: &str) -> Result<i64, String> {
    let t = text.trim();
    let (negative, digits) = match t.as_bytes().first() {
        Some(b'-') => (true, &t[1..]),
        Some(b'+') => (false, &t[1..]),
        _ => (false, t),
    };
    let ok = !digits.is_empty()
        && !digits.starts_with('_')
        && !digits.ends_with('_')
        && !digits.contains("__")
        && digits.bytes().all(|b| b.is_ascii_digit() || b == b'_');
    if !ok {
        return Err(format!("invalid int value: '{text}'"));
    }
    let mut v: i64 = 0;
    for b in digits.bytes().filter(u8::is_ascii_digit) {
        v = v.saturating_mul(10).saturating_add(i64::from(b - b'0'));
    }
    Ok(if negative { -v } else { v })
}

#[cfg(test)]
mod tests {
    use super::{parse, py_int, Parsed, Takes};

    const OPTS: [(&str, Takes); 3] = [
        ("svg", Takes::Value),
        ("page", Takes::Value),
        ("threshold", Takes::Int),
    ];

    fn run(words: &[&str]) -> Result<Parsed, String> {
        parse(
            &words.iter().map(|w| (*w).to_owned()).collect::<Vec<_>>(),
            &OPTS,
        )
    }

    fn ok(words: &[&str]) -> (Vec<String>, Vec<(&'static str, String)>) {
        match run(words).unwrap() {
            Parsed::Run {
                positionals,
                options,
            } => (positionals, options),
            Parsed::Help => (vec!["<help>".to_owned()], Vec::new()),
        }
    }

    #[test]
    fn options_are_read_as_argparse_reads_them() {
        let (pos, opts) = ok(&[
            "a.png",
            "--pa",
            "p.html",
            "b.svg",
            "--threshold=-3",
            "--page=q.html",
        ]);
        assert_eq!(pos, ["a.png", "b.svg"]);
        assert_eq!(
            opts,
            [
                ("threshold", "-3".to_owned()),
                ("page", "q.html".to_owned())
            ]
        );
        assert_eq!(ok(&["-5", "--", "--page", "-x"]).0, ["-5", "--page", "-x"]);
        assert_eq!(ok(&["--p", "-1.5", "-"]).1, [("page", "-1.5".to_owned())]);
        assert_eq!(run(&["a", "--he"]), Ok(Parsed::Help));
        assert_eq!(ok(&["-h"]).0, ["<help>"]);
        assert!(!super::negative_number("5") && super::negative_number("-.5"));
        assert_eq!(run(&["-h", "--bogus"]), Ok(Parsed::Help));
        assert_eq!(run(&["--bogus", "-x", "-h"]), Ok(Parsed::Help));
        assert!(run(&["--threshold", "x", "-h"])
            .unwrap_err()
            .contains("invalid int"));
        for bad in [
            &["--bogus"][..],
            &["-x"],
            &["--page"],
            &["--page", "-x"],
            &["--help=1"],
            &["--"],
            &["--="],
        ] {
            if bad == ["--"] {
                assert_eq!(ok(bad).0.len(), 0);
                continue;
            }
            assert!(run(bad).is_err(), "{bad:?}");
        }
        let flags = [("vector", Takes::Flag), ("verbose", Takes::Flag)];
        let words = |w: &[&str]| w.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
        assert!(parse(&words(&["--ve"]), &flags)
            .unwrap_err()
            .starts_with("ambiguous"));
        assert!(parse(&words(&["--vector=1"]), &flags).is_err());
        assert_eq!(
            parse(&words(&["--vec"]), &flags),
            Ok(Parsed::Run {
                positionals: vec![],
                options: vec![("vector", String::new())]
            })
        );
    }

    #[test]
    fn an_int_is_python_s() {
        assert_eq!(py_int(" +1_0 "), Ok(10));
        assert_eq!(py_int("-7"), Ok(-7));
        assert_eq!(py_int("99999999999999999999999"), Ok(i64::MAX));
        for bad in ["", "1.5", "_1", "1_", "1__0", "x", "-"] {
            assert!(py_int(bad).is_err(), "{bad}");
        }
    }
}
