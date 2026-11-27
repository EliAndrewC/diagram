//! A RUN ENDS AT ITS PROGRAM'S EXIT (feature 451 T364, found by T340): `run_in` read its program's output with `Command::output`, which
//! returns only when every holder of the pipes has closed them, so a process a test left behind with its stdout held the gate's test
//! phase for that process's life (measured 2026-11-26 in the pool tree diagram-backlog-t270, three runs at load 9.7 to 11.4: the
//! binary exited at 2.00 to 2.04 s, the pipe ended at 5.16 to 5.18 s). Here each pipe is read on a thread of its own while the run
//! waits on the program; once it has exited, the readers get `DRAIN` to reach the pipe's end. A pipe still open after that is cut
//! only where another process holds it (`holders`, read from `/proc`): what was read is taken, and the holders are named on stderr
//! under `HELD`, one line that `answer` shows on a green crate too, so the leak is seen rather than waited for. Where none holds it
//! the only writer has exited and the reader is merely late (a loaded machine), so the run waits for the pipe's end: a cut there
//! would lose the output's tail - a test build's last `executable` lines among it. Failing the crate on a leak, and ending those
//! processes, is 451 T363's.

use std::fmt::Write as _;
use std::io::Read;
use std::os::fd::AsRawFd;
use std::os::unix::fs::MetadataExt;
use std::sync::{mpsc, Arc, Mutex, PoisonError};
use std::time::{Duration, Instant};

/// How long, after the program's exit, the readers have to reach the pipes' end before the run asks who still holds them: what is
/// left then is at most a pipe's buffer each, so this is slack for a loaded machine's scheduling, and it is what a leak now costs, a
/// tenth of the 3.1 s T340's cost. A GUESS knob: a late reader no other process holds is waited for, never cut, so it loses no output.
const DRAIN: Duration = Duration::from_millis(250);

/// The opening of the line that names a pipe still held after its program exited.
pub(super) const HELD: &str = "rust-checks: HELD";

/// One pipe, read to its end on a thread of its own.
pub(super) struct Reader {
    got: Arc<Mutex<Vec<u8>>>,
    ended: mpsc::Receiver<()>,
    inode: u64,
}

impl Reader {
    pub(super) fn start<P: Read + AsRawFd + Send + 'static>(mut pipe: P) -> Reader {
        let inode =
            std::fs::metadata(format!("/proc/self/fd/{}", pipe.as_raw_fd())).map_or(0, |m| m.ino());
        let got = Arc::new(Mutex::new(Vec::new()));
        let (tell, ended) = mpsc::channel();
        let into = Arc::clone(&got);
        std::thread::spawn(move || {
            let mut chunk = [0u8; 8192];
            while let Ok(n @ 1..) = pipe.read(&mut chunk) {
                into.lock()
                    .unwrap_or_else(PoisonError::into_inner)
                    .extend_from_slice(&chunk[..n]);
            }
            let _ = tell.send(());
        });
        Reader { got, ended, inode }
    }

    /// Has the pipe ended by `deadline` (none: wait for its end)? Asked at most once a pipe after its end, which is told once.
    fn ended_by(&self, deadline: Option<Instant>) -> bool {
        let Some(d) = deadline else {
            let _ = self.ended.recv();
            return true;
        };
        !matches!(
            self.ended
                .recv_timeout(d.saturating_duration_since(Instant::now())),
            Err(mpsc::RecvTimeoutError::Timeout)
        )
    }

    /// What the pipe held when asked.
    fn text(&self) -> String {
        String::from_utf8_lossy(&self.got.lock().unwrap_or_else(PoisonError::into_inner))
            .into_owned()
    }
}

/// The two pipes' text once the program has exited, and the `HELD` line naming what still holds either, on the end of stderr.
pub(super) fn ended(program: &str, out: &Reader, err: &Reader) -> (String, String) {
    let deadline = Some(Instant::now() + DRAIN);
    let open: Vec<&Reader> = [out, err]
        .into_iter()
        .filter(|r| !r.ended_by(deadline))
        .collect();
    let held = if open.is_empty() {
        Vec::new()
    } else {
        holders(&[out.inode, err.inode])
    };
    if held.is_empty() {
        // nothing else holds a pipe still open: its reader is late, never cut
        for r in open {
            r.ended_by(None);
        }
    }
    let (stdout, mut stderr) = (out.text(), err.text());
    if !held.is_empty() {
        let _ = writeln!(
            stderr,
            "{HELD}: {program} exited, but its output is still held by {} - the run read what was there and went on; fix: kill \
             and wait what the test starts (451 T363)",
            held.join(", ")
        );
    }
    (stdout, stderr)
}

/// A pipe whose only other holder writes after `late`, the reader's end then: a test's stand-in for a reader the machine is slow to
/// run, which `ended` waits for rather than cut.
#[cfg(test)]
pub(super) fn late_pipe(late: Duration, text: &'static str) -> Reader {
    let (read, mut write) = std::io::pipe().unwrap_or_else(|e| unreachable!("{e}"));
    std::thread::spawn(move || {
        std::thread::sleep(late);
        let _ = std::io::Write::write_all(&mut write, text.as_bytes());
    });
    Reader::start(read)
}

/// Each process but this one with a descriptor on one of the pipes, as `pid N (its command line)`, read from `/proc`.
fn holders(inodes: &[u64]) -> Vec<String> {
    let wanted: Vec<String> = inodes.iter().map(|i| format!("pipe:[{i}]")).collect();
    let me = std::process::id().to_string();
    let mut found = Vec::new();
    for entry in std::fs::read_dir("/proc").into_iter().flatten().flatten() {
        let pid = entry.file_name().to_string_lossy().into_owned();
        let fds = std::fs::read_dir(entry.path().join("fd"))
            .into_iter()
            .flatten()
            .flatten();
        let holds = pid != me
            && pid.bytes().all(|b| b.is_ascii_digit())
            && fds
                .filter_map(|fd| std::fs::read_link(fd.path()).ok())
                .any(|l| wanted.iter().any(|w| l.as_os_str() == w.as_str()));
        if holds {
            let line = std::fs::read(entry.path().join("cmdline")).unwrap_or_default();
            let words: Vec<String> = line
                .split(|b| *b == 0)
                .filter(|w| !w.is_empty())
                .map(|w| String::from_utf8_lossy(w).into_owned())
                .collect();
            found.push(format!("pid {pid} ({})", words.join(" ")));
        }
    }
    found.sort();
    found
}

/// The `HELD` lines of a green crate's run, each after the crate's name, for `answer` to say: a green run's stderr is not shown.
pub(super) fn held_on(shown: &str, stderr: &str) -> String {
    stderr
        .lines()
        .filter(|l| l.starts_with(HELD))
        .map(|l| format!("{shown}: {l}\n"))
        .collect()
}
