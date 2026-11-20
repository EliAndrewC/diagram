//! `no-poll-hooks` (features 165, 212, 227, 295; ported from `scripts/hooks/no-poll-hooks.sh`, feature 449 T009): A WAIT THE
//! HARNESS CAN TRACK IS NOT POLLED. A loop that sleeps is refused, but the one permitted wait - watching a file - is backgrounded,
//! given a proof of life and a 90-minute ceiling; a disguised `sleep` is refused; a process pattern that matches its own command is
//! bracketed (a make wait scoped to this tree) or refused; a backgrounded periodic report is sent to a cron. `POLL_OK` and `CRON_OK`
//! with a reason stand it aside. The refusals' words are the shell's; the reasons stand in its comments, kept in git history.
//!
//! Plan T009's decisions: (a) `hm_shape.py`'s wait half is `shared::wait`; (b) the cron's minute is local, asked of `date +%M` on
//! that branch alone; (c) a command's own process pattern is compiled by `fancy-regex`.
//!
//! A RUN THE HARNESS CANNOT TRACK (feature 451 T15, D12, FR-008): a make or cargo job detached by a lone `&` that no `wait` covers,
//! started under `nohup` or `setsid`, or disowned, is refused naming the Bash tool's `run_in_background`; `DETACH_OK` escapes. The
//! command is read by a small walk of its shell structure (`Shell`), never one pattern, since what covers a job is where its `wait`
//! stands: the same shell, unconditional, not backgrounded.
//!
//! A MAIN-SESSION WAIT SLOWER THAN ITS CHECK (feature 451 T16, D13, FR-008): on the two permitted paths - a POLL_OK-escaped wait and
//! the file-watching wait - a loop whose longest `sleep` is over `POLL_CHECK_S`, from a payload with no `agent_id`, is refused naming
//! the same loop at the knob; `SLOW_POLL_OK` escapes, and a builder (a subagent) is not held to it.

use std::path::PathBuf;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log::fire;
use crate::shared::make::{invoked, POS};
use crate::shared::session::Session;
use crate::shared::shape::{strip_heredocs, strip_quotes};
use crate::shared::state::field;
use crate::shared::tool::ask;
use crate::shared::wait::{
    add_ceiling, bracket_pattern, cron_for, file_watching_loop, file_watching_wait, periodic,
    poll_reason, proof_of_life, scope_make_waits, self_matching, sleep_in_loop, WAIT_CEILING_S,
};
use pace::{longest_wait_sleep, slow_poll};

/// The guard.
pub const GUARD: Guard = Guard {
    name: "no-poll-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern)
        .unwrap_or_else(|e| unreachable!("a guard's own pattern: {e}"))
}

static LOOP_WORD: LazyLock<Regex> =
    LazyLock::new(|| re(r"(^|[;&|[:space:]])(while|until|for)[[:space:]]"));
static SLEEP_RE: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(^|[;&|(]|[[:space:]]|\bdo\b|\bthen\b)[\\]?((command|env|busybox)[[:space:]]+)?(/(bin|usr/bin)/)?sleep[[:space:]]+[0-9.]",
    )
});
static DISGUISED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(^|[;&|(]|[[:space:]])([\\]|(command|env|busybox)[[:space:]]+|/(bin|usr/bin)/)sleep[[:space:]]+[0-9.]",
    )
});

static PGREP_F: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?:\A|(?<=[|;&]))(?>[^|;&]*?\b(pgrep|pkill)\b)[^|;&]*[[:space:]]-[a-zA-Z]*f")
});

// A make or cargo run at a command position (D12): `invoked` names a make run's targets, so a goal it cannot read (`make $t`) names
// none, and a cargo run is no make's.
static RUNNER: LazyLock<Regex> =
    LazyLock::new(|| re(&format!(r"{POS}(?:\$\(MAKE\)|make|cargo)(?:[\s;&|)]|$)")));
// A simple command started under nohup or setsid, its options passed over: what follows is what it runs.
static STARTER: LazyLock<Regex> =
    LazyLock::new(|| re(&format!(r"\A{POS}(?:nohup|setsid)\s+(?:-\S+\s+)*")));
// `"$!"` and `'%1'` unquoted before the quotes are blanked, so `wait "$!"` is read as the `wait $!` it is.
static QUOTED_JOB: LazyLock<Regex> = LazyLock::new(|| re(r#"(["'])(\$!|%[0-9]+)\1"#));
// A SHELL's `-c` just before a quote: the string `strip_quotes` keeps is an interpreter's, and only a shell's is walked as commands
// (a `python3 -c` string is passed over).
static SHELL_C: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?:^|[\s/;&|(])(?:ba|da|z|k)?sh\s+(?:-[A-Za-z-]*\s+)*-[A-Za-z]*c\s+$"));

/// `grep -E`'s reading: a pattern matched against each line alone.
fn grep(p: &Regex, text: &str) -> bool {
    text.split('\n').any(|l| p.is_match(l).unwrap_or(false))
}

/// What one decision reads: the event, its command, the sanitized form, the tree's helpers and the local minute's source.
pub(crate) struct Ctx<'a> {
    pub event: &'a Event,
    pub session: &'a Session,
    pub cmd: String,
    pub scan: String,
    pub lib: PathBuf,
    /// The local minute of the hour, for the periodic report's cron (`date +%M`, T009 decision (b)).
    pub minute: fn() -> u64,
}

impl Ctx<'_> {
    fn log(&self, kind: &str, rule: &str) {
        let shown: String = self.cmd.chars().take(200).collect();
        fire(
            "no-poll",
            kind,
            &shown,
            rule,
            &self.event.input,
            self.session,
        );
    }

    fn helper(&self, name: &str) -> String {
        self.lib.join(name).to_string_lossy().into_owned()
    }

    /// The call with its command (and, where asked, its backgrounding) replaced, and what it is told.
    fn rewrite(&self, command: Option<&str>, background: bool, said: &str) -> Vec<Answer> {
        let mut ti = self
            .event
            .input
            .get("tool_input")
            .cloned()
            .unwrap_or(Value::Null);
        if let Some(c) = command {
            ti["command"] = Value::String(c.to_owned());
        }
        if background {
            ti["run_in_background"] = Value::Bool(true);
        }
        vec![Answer::Rewrite(ti), Answer::Notice(said.to_owned())]
    }
}

/// The local minute of the hour (`date +%M`), 0 where it cannot be read.
fn local_minute() -> u64 {
    ask(std::path::Path::new("/"), "date", &["+%M"], "")
        .out
        .trim()
        .parse()
        .unwrap_or(0)
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let tree = std::env::var("L7R_GUARD_TREE").map_or_else(
        |_| std::env::current_dir().unwrap_or_default(),
        PathBuf::from,
    );
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"))
        .to_owned();
    if cmd.is_empty() {
        return Vec::new();
    }
    // the sanitized command is never empty for a command that is not: the stripping inserts as it removes
    let scan = strip_quotes(&strip_heredocs(&cmd));
    judge(&Ctx {
        event,
        session,
        cmd,
        scan,
        lib: tree.join("scripts/hooks/lib"),
        minute: local_minute,
    })
}

pub(crate) fn judge(cx: &Ctx) -> Vec<Answer> {
    // first, so neither POLL_OK nor CRON_OK is a second way past it, and run_in_background no exemption: a `&` inside a
    // backgrounded call still returns before its job ends
    if let Some(refused) = detach(cx) {
        return refused;
    }
    let ti = cx
        .event
        .input
        .get("tool_input")
        .cloned()
        .unwrap_or(Value::Null);
    if crate::shared::wait::background(&ti) {
        match escape_or_refuse(&cx.cmd, "CRON_OK") {
            Escape::Refused(text) => {
                cx.log("blocked", "CRON_OK-no-reason");
                return vec![Answer::Refuse(text)];
            }
            Escape::Escaped(why) => fire(
                "no-poll",
                "escaped",
                &why,
                "cron-ok",
                &cx.event.input,
                cx.session,
            ),
            Escape::None => {
                if let Some(period) = periodic(&ti, field(&cx.event.input, "cwd")) {
                    cx.log("blocked", "periodic-report");
                    let why = Some(poll_reason(&cx.cmd))
                        .filter(|w| !w.is_empty())
                        .unwrap_or_else(|| "the periodic report".to_owned());
                    return vec![Answer::Refuse(periodic_refusal(
                        &cron_for(period, (cx.minute)()),
                        &format!("{why}: check the state once and report it"),
                    ))];
                }
            }
        }
    }
    // `SLOW_POLL_OK` holds `POLL_OK`, and the escape reader matches a token anywhere: the longer one is never read as the shorter
    match escape_or_refuse(&cx.cmd.replace("SLOW_POLL_OK", "SLOW_POLL"), "POLL_OK") {
        Escape::Refused(text) => {
            cx.log("blocked", "POLL_OK-no-reason");
            return vec![Answer::Refuse(text)];
        }
        Escape::Escaped(why) => {
            if let Some(refused) = slow_poll(cx) {
                return refused;
            }
            fire(
                "no-poll",
                "escaped",
                &why,
                "poll-ok",
                &cx.event.input,
                cx.session,
            );
            if let Some(done) = bracket_self_match(cx, "escaped-self-match", ESCAPED_BRACKET) {
                return done;
            }
            return add_ceiling(&cx.cmd, WAIT_CEILING_S).map_or_else(Vec::new, |ceiled| {
                cx.log("rewrote", "escaped-ceiling");
                cx.rewrite(Some(&ceiled), false, ESCAPED_CEILING)
            });
        }
        Escape::None => {}
    }
    // a loop's `sleep` given a variable (`sleep $N`) is a sleep in a loop too: the digit the patterns ask for once let it through
    // (feature 451 T16)
    if grep(&LOOP_WORD, &cx.scan)
        && (grep(&SLEEP_RE, &cx.scan) && sleep_in_loop(&cx.scan)
            || longest_wait_sleep(cx).is_some())
    {
        if file_watching_loop(&cx.cmd) {
            return slow_poll(cx).unwrap_or_else(|| file_wait(cx, &ti));
        }
        return block(
            cx,
            "this is a busy-wait loop (a loop containing `sleep`).",
            BUSY_WAIT,
            "busy-wait-loop",
        );
    }
    if grep(&DISGUISED, &cx.scan) {
        return block(
            cx,
            "`sleep` was invoked in a form that evades the harness's foreground-sleep block.",
            DISGUISED_WHY,
            "disguised-sleep",
        );
    }
    bracket_self_match(cx, "self-match", BRACKETED).unwrap_or_default()
}

/// A run the harness cannot track refused, or stood aside by `DETACH_OK` and its reason (D12); None where there is none.
fn detach(cx: &Ctx) -> Option<Vec<Answer>> {
    let rule = detached(&cx.cmd)?;
    match escape_or_refuse(&cx.cmd, "DETACH_OK") {
        Escape::Refused(text) => {
            cx.log("blocked", "DETACH_OK-no-reason");
            Some(vec![Answer::Refuse(text)])
        }
        Escape::Escaped(why) => {
            fire(
                "no-poll",
                "escaped",
                &why,
                "detach-ok",
                &cx.event.input,
                cx.session,
            );
            None
        }
        Escape::None => {
            cx.log("blocked", rule);
            Some(vec![Answer::Refuse(detach_refusal(rule))])
        }
    }
}

/// The rule a command breaks by running make or cargo where the harness cannot track it (D12): `detached-nohup` (started under
/// `nohup` or `setsid` at a command position), `detached-disown` (a `disown` after a make or cargo job's `&`, whatever `wait`
/// follows, since a disowned job leaves the job table), `detached-amp` (a lone `&` no `wait` covers). Heredocs and quoted strings are
/// payload, never commands (constitution XVIII); the string after `-c`, which a shell runs, is read as a shell of its own.
pub(crate) fn detached(cmd: &str) -> Option<&'static str> {
    // NO RUNNER OR NO DETACHING WORD, NO WALK: most commands end here, before any pattern compiles (as `invoked` does)
    if !["make", "MAKE", "cargo", "l7r-gate"]
        .iter()
        .any(|w| cmd.contains(w))
        || !["&", "nohup", "setsid"].iter().any(|w| cmd.contains(w))
    {
        return None;
    }
    // a line continuation is a blank to the shell, and to a nohup or setsid read at the start of its command
    let joined = QUOTED_JOB
        .replace_all(&strip_heredocs(cmd), "$2")
        .replace("\\\n", "  ");
    let scan = strip_quotes(&joined);
    let mut sh = Shell {
        src: &scan,
        s: scan.as_bytes(),
        i: 0,
        lists: Vec::new(),
        jobs: Vec::new(),
        waits: Vec::new(),
        disowns: Vec::new(),
        started: false,
    };
    sh.list(None, Stop::Eof);
    let held: Vec<usize> = (0..sh.jobs.len()).filter(|&j| sh.jobs[j].holds).collect();
    if sh.started {
        Some("detached-nohup")
    } else if held
        .iter()
        .any(|&j| sh.disowns.iter().any(|&d| d > sh.jobs[j].amp))
    {
        Some("detached-disown")
    } else {
        held.iter()
            .any(|&j| !sh.covered(j))
            .then_some("detached-amp")
    }
}

/// Whether `text` runs make or cargo: a make goal `invoked` reads (the one detector, D1), or a goal-less make or a cargo at a
/// command position.
fn holds(text: &str) -> bool {
    !invoked(text).is_empty() || RUNNER.is_match(text).unwrap_or(false)
}

/// Where a list ends: the end of the command, a closing character (`)`, a quote, a backtick), or one of the reserved words.
#[derive(Clone, Copy, PartialEq)]
enum Stop {
    Eof,
    Close(u8),
    Words(&'static [&'static str]),
}

const IF: Stop = Stop::Words(&["then", "elif", "else", "fi"]);
const LOOP: Stop = Stop::Words(&["do", "done"]);
const ARM: Stop = Stop::Words(&[";;", ";&", "esac"]);

/// A job put in the background: where its `&` stands, the list and item it is, and whether it runs make or cargo.
struct Job {
    amp: usize,
    list: usize,
    item: usize,
    holds: bool,
}

/// A `wait` that may cover a job: the first command of its and-or list, alone in its pipeline, not backgrounded; its words.
struct Wait {
    at: usize,
    list: usize,
    item: usize,
    args: Vec<String>,
}

/// The walk over a sanitized command: each list's place in the one above it while that keeps the shell (None: the top, or a shell
/// of its own - a `( )`, a `$( )`, a backtick, a `-c` string, a pipeline's part or a backgrounded group), and what was found.
struct Shell<'a> {
    src: &'a str,
    s: &'a [u8],
    i: usize,
    lists: Vec<Option<(usize, usize)>>,
    jobs: Vec<Job>,
    waits: Vec<Wait>,
    disowns: Vec<usize>,
    started: bool,
}

impl Shell<'_> {
    fn at(&self, b: u8) -> bool {
        self.s.get(self.i) == Some(&b)
    }

    fn at2(&self, two: &[u8]) -> bool {
        self.s[self.i..].starts_with(two)
    }

    /// Whether the reserved word `w` stands here, a word of its own.
    fn word_at(&self, w: &str) -> bool {
        self.s[self.i..].starts_with(w.as_bytes())
            && self
                .s
                .get(self.i + w.len())
                .is_none_or(|b| b" \t\n;&|)".contains(b))
    }

    /// Spaces, tabs, a line continuation, a comment, and newlines where asked, passed over.
    fn blanks(&mut self, newlines: bool) {
        while let Some(&b) = self.s.get(self.i) {
            match b {
                b' ' | b'\t' | b'\r' => self.i += 1,
                b'\n' if newlines => self.i += 1,
                b'#' => {
                    while self.s.get(self.i).is_some_and(|c| *c != b'\n') {
                        self.i += 1;
                    }
                }
                _ => break,
            }
        }
    }

    /// A list, to its stop: the reserved word that ended it, or None at the end of the command.
    fn list(&mut self, up: Option<(usize, usize)>, stop: Stop) -> Option<&'static str> {
        let id = self.lists.len();
        self.lists.push(up);
        let mut item = 0;
        loop {
            self.blanks(true);
            let &b = self.s.get(self.i)?;
            let ended = match stop {
                Stop::Close(c) => (b == c).then_some(""),
                Stop::Words(ws) => ws.iter().copied().find(|w| self.word_at(w)),
                Stop::Eof => None,
            };
            if let Some(k) = ended {
                self.i += k.len().max(1);
                return Some(k);
            }
            if b == b';' {
                self.i += 1;
                continue;
            }
            let before = self.i;
            self.and_or(id, item, stop);
            item += 1;
            // a stray `)` ends no command and starts none
            if self.i == before {
                self.i += 1;
            }
        }
    }

    /// Lists made since `mark` that hung from (`list`, `item`) cut from it: they run in a shell of their own.
    fn unshell(&mut self, mark: usize, list: usize, item: usize) {
        for l in &mut self.lists[mark..] {
            if *l == Some((list, item)) {
                *l = None;
            }
        }
    }

    /// One and-or list, item `item` of list `list`: a job where a lone `&` ends it, a covering `wait`'s candidate where its first
    /// pipeline is one.
    fn and_or(&mut self, list: usize, item: usize, stop: Stop) {
        let (start, mark) = (self.i, self.lists.len());
        let wait = self.pipeline(list, item, stop);
        while self.at2(b"&&") || self.at2(b"||") {
            self.i += 2;
            self.blanks(true);
            self.pipeline(list, item, stop);
        }
        if self.at(b'&') {
            let amp = self.i;
            self.i += 1;
            self.unshell(mark, list, item);
            let holds = holds(self.src.get(start..amp).unwrap_or_default());
            self.jobs.push(Job {
                amp,
                list,
                item,
                holds,
            });
        } else if let Some(args) = wait {
            self.waits.push(Wait {
                at: start,
                list,
                item,
                args,
            });
        }
    }

    /// A pipeline: its first command's `wait` words where it is the only command; each part of a longer one its own shell.
    fn pipeline(&mut self, list: usize, item: usize, stop: Stop) -> Option<Vec<String>> {
        let mark = self.lists.len();
        let wait = self.command(list, item, stop);
        if !self.at(b'|') || self.at2(b"||") {
            return wait;
        }
        while self.at(b'|') && !self.at2(b"||") {
            self.i += 1 + usize::from(self.s.get(self.i + 1) == Some(&b'&'));
            self.blanks(true);
            self.command(list, item, stop);
        }
        self.unshell(mark, list, item);
        None
    }

    /// One command: a compound's body walked as lists of this shell (a `( )` as one of its own), then its words; a simple command's
    /// `wait` words returned, its `disown` and its start under `nohup` or `setsid` noted.
    fn command(&mut self, list: usize, item: usize, stop: Stop) -> Option<Vec<String>> {
        self.blanks(false);
        let (start, up) = (self.i, Some((list, item)));
        let head = if self.at(b'(') {
            self.i += 1;
            self.list(None, Stop::Close(b')'));
            true
        } else if self.word_at("{") {
            self.i += 1;
            self.list(up, Stop::Words(&["}"]));
            true
        } else if self.word_at("if") {
            self.i += 2;
            while matches!(self.list(up, IF), Some("then" | "elif" | "else")) {}
            true
        } else if self.word_at("while") || self.word_at("until") {
            self.i += 5;
            while self.list(up, LOOP) == Some("do") {}
            true
        } else if self.word_at("for") {
            self.i += 3;
            self.skip_to("do", stop);
            self.list(up, Stop::Words(&["done"]));
            true
        } else if self.word_at("case") {
            self.i += 4;
            self.skip_to("in", stop);
            self.arms(up);
            true
        } else {
            false
        };
        let mut words = Vec::new();
        loop {
            self.blanks(false);
            match self.s.get(self.i) {
                None | Some(b';' | b'\n' | b'|' | b')') => break,
                Some(b'&') if self.s.get(self.i + 1) != Some(&b'>') => break,
                Some(&b) if stop == Stop::Close(b) => break,
                _ => words.push(self.word(stop)),
            }
        }
        if head {
            return None;
        }
        let first = words.first().map(String::as_str);
        if first == Some("disown") {
            self.disowns.push(start);
        }
        let span = self.src.get(start..self.i).unwrap_or_default();
        if STARTER
            .find(span)
            .ok()
            .flatten()
            .is_some_and(|m| holds(&span[m.end()..]))
        {
            self.started = true;
        }
        (first == Some("wait")).then(|| {
            // a redirection is no job named, nor the file a lone operator (`2> /dev/null`) takes
            let (mut args, mut operand) = (Vec::new(), false);
            for w in &words[1..] {
                if operand {
                    operand = false;
                } else if w.contains(['<', '>']) {
                    operand = w.ends_with(['<', '>']);
                } else {
                    args.push(w.clone());
                }
            }
            args
        })
    }

    /// Whether the quote here opens a string a shell runs: one just after `sh`, `bash`, `dash` or `zsh` and its `-c`.
    fn shell_runs(&self) -> bool {
        let before = &self.src[..self.i];
        let from = (before.len().saturating_sub(64)..=before.len())
            .find(|&k| before.is_char_boundary(k))
            .unwrap_or(0);
        SHELL_C.is_match(&before[from..]).unwrap_or(false)
    }

    /// A quoted string no shell runs passed over to its close, a `\` escaping inside double quotes.
    fn skip_quote(&mut self, q: u8) {
        self.i += 1;
        while let Some(&c) = self.s.get(self.i) {
            self.i += 1;
            if c == q {
                return;
            }
            if c == b'\\' && q == b'"' {
                self.i = (self.i + 1).min(self.s.len());
            }
        }
    }

    /// A `for` or `case` head's words passed over, to its `do` or `in`.
    fn skip_to(&mut self, word: &str, stop: Stop) {
        loop {
            self.blanks(true);
            if self.i >= self.s.len() || self.word_at(word) {
                self.i = (self.i + word.len()).min(self.s.len());
                return;
            }
            let before = self.i;
            self.word(stop);
            self.i += usize::from(self.i == before);
        }
    }

    /// A `case`'s arms: each pattern passed over to its `)`, each arm walked to its `;;`, `;&` or the `esac`.
    fn arms(&mut self, up: Option<(usize, usize)>) {
        loop {
            self.blanks(true);
            if self.i >= self.s.len() || self.word_at("esac") {
                self.i = (self.i + 4).min(self.s.len());
                return;
            }
            while self.s.get(self.i).is_some_and(|b| *b != b')') {
                self.i += 1;
            }
            self.i = (self.i + 1).min(self.s.len());
            if !matches!(self.list(up, ARM), Some(";;" | ";&")) {
                return;
            }
        }
    }

    /// One word, a `$( )`, `( )`, backtick or quoted span inside it walked as a shell of its own (a quoted span left after the
    /// blanking is the string after `-c`, or empty).
    fn word(&mut self, stop: Stop) -> String {
        let start = self.i;
        while let Some(&b) = self.s.get(self.i) {
            match b {
                b' ' | b'\t' | b'\n' | b';' | b'|' | b')' => break,
                b'&' if self.i > start || self.s.get(self.i + 1) != Some(&b'>') => break,
                _ if stop == Stop::Close(b) => break,
                b'\\' => self.i = (self.i + 2).min(self.s.len()),
                b'>' | b'<' if matches!(self.s.get(self.i + 1), Some(b'&' | b'|')) => self.i += 2,
                b'"' | b'\'' if !self.shell_runs() => self.skip_quote(b),
                b'(' | b'`' | b'"' | b'\'' => {
                    self.i += 1;
                    self.list(None, Stop::Close(if b == b'(' { b')' } else { b }));
                }
                _ => self.i += 1,
            }
        }
        self.src.get(start..self.i).unwrap_or_default().to_owned()
    }

    /// Whether job `j` is covered: a `wait` later in its own list that waits for it - bare, `wait $!` with no other job's `&`
    /// between, or `wait %N` naming its number among the command's jobs - or a bare `wait` in a list above it of the same shell
    /// (after a loop or an `if`, `$!` and `%N` name one run of the job alone).
    fn covered(&self, j: usize) -> bool {
        let (mut list, mut item, mut own) = (self.jobs[j].list, self.jobs[j].item, true);
        loop {
            if self
                .waits
                .iter()
                .any(|w| w.list == list && w.item > item && self.covers(w, j, own))
            {
                return true;
            }
            let Some((l, i)) = self.lists[list] else {
                return false;
            };
            (list, item, own) = (l, i, false);
        }
    }

    fn covers(&self, w: &Wait, j: usize, own: bool) -> bool {
        let last = self.jobs.iter().rposition(|k| k.amp < w.at);
        w.args.is_empty()
            || own
                && w.args
                    .iter()
                    .any(|a| *a == format!("%{}", j + 1) || (a == "$!" && last == Some(j)))
    }
}

fn detach_refusal(rule: &str) -> String {
    let what = match rule {
        "detached-nohup" => "a make or cargo run is started under nohup or setsid, so it outlives the call and nothing tracks its end",
        "detached-disown" => "a make or cargo job is disowned: it leaves the shell's job table, so no `wait` covers it and nothing tracks its end",
        _ => "a make or cargo job is put in the background with a lone `&` and no `wait` covers it, so the call returns while it runs and nothing tracks its end",
    };
    format!(
        "BLOCKED (no-poll): {what} (feature 451 FR-008: T225's `make static &` sat untracked, research R4).\n\nDo this instead: run it \
as the Bash call itself with run_in_background: true; its completion notice wakes you.\nA job kept in the call passes when a `wait` \
after it covers it - in the same shell, unconditional, not itself backgrounded, and bare,\n`wait $!` with no other `&` between, or \
`wait %N` naming the job - since the call then returns only when the run ends.\nEscape: DETACH_OK=\"<reason>\" in the command.\n"
    )
}

/// The permitted wait - a file watched - made safe: backgrounded, given a proof of life and a ceiling.
fn file_wait(cx: &Ctx, ti: &Value) -> Vec<Answer> {
    let proof = proof_of_life(&cx.cmd, &cx.helper("writer-alive.sh"));
    if let Some(refused) = refuse_self_match(cx, proof.as_deref().unwrap_or(&cx.cmd)) {
        return refused;
    }
    let ceil = add_ceiling(proof.as_deref().unwrap_or(&cx.cmd), WAIT_CEILING_S);
    let bg = file_watching_wait(ti);
    if proof.is_none() && ceil.is_none() && bg {
        cx.log("permitted", "detached-file-wait");
        return Vec::new();
    }
    let rule = if !bg {
        "backgrounded-file-wait"
    } else if proof.is_some() {
        "proof-of-life"
    } else {
        "wait-ceiling"
    };
    cx.log("rewrote", rule);
    let mut said = Vec::new();
    if !bg {
        said.push(BACKGROUNDED);
    }
    if proof.is_some() {
        said.push(PROOF);
    }
    if ceil.is_some() {
        said.push(CEILING);
    }
    said.push("A wait on a process or a network call is still refused.");
    cx.rewrite(ceil.as_deref().or(proof.as_deref()), true, &said.join(" "))
}

/// A refusal naming what to do instead.
fn block(cx: &Ctx, reason: &str, alternative: &str, rule: &str) -> Vec<Answer> {
    cx.log("blocked", rule);
    vec![Answer::Refuse(format!(
        "BLOCKED (no-poll): {reason}\n{alternative}\n\nDo this instead: run the work with run_in_background and act on the completion \
notification; the harness\nre-invokes you. For EXTERNAL state the harness cannot see (a port, a remote queue), put POLL_OK and what \
you\nare waiting for in the command."
    ))]
}

/// A process pattern that matches `cmd`'s own text refused: the waiting shell finds itself and the wait never ends.
fn refuse_self_match(cx: &Ctx, cmd: &str) -> Option<Vec<Answer>> {
    let hit = self_matching(cmd).into_iter().next()?;
    cx.log("blocked", "self-match-launch");
    Some(vec![Answer::Refuse(format!(
        "BLOCKED (no-poll): the process pattern {hit} matches this command's own text - it launches, or names, what it\nwaits for - \
so the waiting shell finds itself and the wait never ends (2026-09-30: four hours past a finished roll).\nWait on the launched \
process by its PID (`cmd > log 2>&1 & pid=$!; until ! kill -0 $pid; do sleep 10; done`), or on\nits log with run_in_background, \
or on a make run with `scripts/gates/l7r-gate.sh own-make <target>`. A make or cargo run itself\nis launched as the Bash call with \
run_in_background, never detached (feature 451 D12)."
    ))])
}

/// A `pgrep -f`/`pkill -f` pattern bracketed so it cannot find its own shell, a make wait scoped to this tree, a ceiling added -
/// the rewrite, or a refusal, or None where the command has no such pattern to fix.
fn bracket_self_match(cx: &Ctx, rule: &str, context: &str) -> Option<Vec<Answer>> {
    if !grep(&PGREP_F, &cx.scan) {
        return None;
    }
    let scoped = scope_make_waits(
        &cx.cmd,
        &format!("{} own-make", cx.helper("../../gates/l7r-gate.sh")),
    );
    let fixed = bracket_pattern(scoped.as_deref().unwrap_or(&cx.cmd)).or(scoped);
    if let Some(refused) = refuse_self_match(cx, fixed.as_deref().unwrap_or(&cx.cmd)) {
        return Some(refused);
    }
    let mut fixed = fixed?;
    let mut context = context.to_owned();
    if let Some(ceiled) = add_ceiling(&fixed, WAIT_CEILING_S) {
        fixed = ceiled;
        context += " A ceiling was added to the loop: past 90 minutes it prints WAIT TIMED OUT and exits 4, so a wait that can never end still wakes you.";
    }
    let rule = if fixed.contains(" own-make ") {
        SCOPED.clone_into(&mut context);
        format!("{rule}-scoped")
    } else {
        rule.to_owned()
    };
    cx.log("rewrote", &rule);
    Some(cx.rewrite(Some(&fixed), false, &context))
}

fn periodic_refusal(cron: &str, prompt: &str) -> String {
    format!(
        "BLOCKED (no-poll): a periodic report kept as a backgrounded watcher loses its schedule when its exit lands while\nthe session \
cannot run (2026-09-30: twice across a usage-limit window, about two hours of reports each). A cron\nkeeps the schedule by \
itself:\n\n  CronCreate(cron=\"{cron}\", recurring=true, prompt=\"{prompt}\")\n\nPut in the prompt what one report checks. (It fires \
while the session is idle and lasts 7 days.) A wait for an\nevent - a file, a finished queue - stays a backgrounded watcher. Escape: \
CRON_OK=\"<reason>\".\n"
    )
}

const BUSY_WAIT: &str = "Waiting in a loop burns wall-clock at full model-turn cost and, for anything the harness tracks, it
is pure waste: a backgrounded Bash command notifies you the moment it exits.";
const DISGUISED_WHY: &str = "The harness blocks foreground `sleep` on purpose; `command sleep`, `/bin/sleep` and `env sleep`
are the same thing wearing a hat. Whatever you were about to wait for, there is a better signal for
it - a completion notification for harness-tracked work, or POLL_OK for genuinely external state.";
const BRACKETED: &str = "The process-match pattern was bracketed for you: a literal pattern is an argument of the command line being \
searched, so it always finds the searching shell itself and the wait never ends. Corrected rather than refused - the refusal used to \
cost a round trip to say the same thing.";
const ESCAPED_BRACKET: &str = "POLL_OK permitted this wait, and its process-match pattern was bracketed for you: a literal pattern is \
an argument of the command line being searched, so it always finds the searching shell itself and the loop never ends (2026-09-08: an \
escaped waiter on a detached page-check looped for hours on a gate that finished in 7 s). The escape decides whether you may wait; it \
does not make the pattern correct.";
const ESCAPED_CEILING: &str = "POLL_OK permitted this wait, and a ceiling was added to its loop: past 90 minutes it prints WAIT TIMED \
OUT and exits 4, so a wait that can never end still wakes you (2026-09-30: four hours lost to one that never ended).";
const SCOPED: &str = "A wait on a make run was scoped to this working tree (l7r-gate.sh own-make <target>): pgrep searches the whole host, and \
other sessions' runs of the same target held a waiter open for six hours after its own run had ended. A harness-tracked run \
(run_in_background) needs no waiter at all.";
const BACKGROUNDED: &str = "This file-watching wait was BACKGROUNDED for you (run_in_background): in the foreground it would have held \
the whole turn at model-turn cost. Its output - including whatever follows the loop - arrives as a completion notification, so spend \
the turn on the next thing.";
const PROOF: &str = "A PROOF-OF-LIFE check was added to the loop: `writer-alive.sh <the file you are watching>`, which asks the kernel \
whether anything still holds that file open and when it was last written. Without it the wait outlives its producer - a detached run \
that is killed (this container OOM-kills them) stops writing, the pattern never appears, and the loop runs until somebody notices. \
When the loop ends, read what the log DOES have: if the helper printed a line, the run is gone and the log is truncated, not finished.";
const CEILING: &str = "A CEILING was added to the loop: past 90 minutes it prints WAIT TIMED OUT and exits 4, so a wait whose line \
never comes still ends and wakes you (2026-09-30: four hours lost to a wait that could not end).";

mod pace;
#[cfg(test)]
mod tests;
