//! INT AND TERM REMOVE A PROCESS'S DIRECTORIES TOO (feature 449 T101; the GM 2026-11-11: "remove it on exit, including failure and
//! interrupt"). A process ended by a signal it does not catch never runs a `Drop`, so a `make rust-test` stopped with Ctrl-C, or a
//! command a timeout ended with TERM, left every `TempDir` it held. The first `TempDir` of a process catches INT and TERM: the handler
//! only writes the signal's number to a pipe, which a signal handler may do, and a thread waiting on that pipe removes every `TempDir`
//! the process still holds and exits as the signal would have (128 + its number). A signal the process was started ignoring - a
//! background job's INT - stays ignored. Only a SIGKILL, which no process can catch, leaves them to the next `TempDir` of their tag
//! (`sweep_dead`).
//!
//! The crate's one use of `unsafe`: `pipe(2)`, `write(2)` and `signal(2)` from the C library std already links, there being no safe
//! form of them in std.

use std::io::Read;
use std::os::fd::FromRawFd;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicI32, Ordering};
use std::sync::{Mutex, Once};

/// Every `TempDir` this process holds.
static LIVE: Mutex<Vec<PathBuf>> = Mutex::new(Vec::new());
/// The pipe's write end, set before any handler is installed.
static WRITE_END: AtomicI32 = AtomicI32::new(-1);

const SIGINT: i32 = 2;
const SIGTERM: i32 = 15;
/// `SIG_IGN`: the disposition of a signal the process was started ignoring.
const IGNORED: usize = 1;

extern "C" {
    fn pipe(fds: *mut i32) -> i32;
    fn write(fd: i32, buf: *const u8, count: usize) -> isize;
    fn signal(signum: i32, handler: usize) -> usize;
}

/// The handler: the signal's number, one byte, down the pipe - nothing else, since a handler may call only what is async-signal-safe.
extern "C" fn on_signal(signum: i32) {
    let byte = u8::try_from(signum).unwrap_or(0);
    // SAFETY: write(2) is async-signal-safe, and the descriptor is the pipe's write end, stored before this handler was installed
    let _ = unsafe { write(WRITE_END.load(Ordering::Relaxed), &raw const byte, 1) };
}

/// `path` is held: removed if INT or TERM ends the process first. The first call catches the two signals.
pub(super) fn hold(path: &Path) {
    static CATCH: Once = Once::new();
    CATCH.call_once(catch);
    if let Ok(mut live) = LIVE.lock() {
        live.push(path.to_path_buf());
    }
}

/// `path` is no longer held: its `Drop` ran, or it was kept.
pub(super) fn release(path: &Path) {
    if let Ok(mut live) = LIVE.lock() {
        live.retain(|p| p != path);
    }
}

fn catch() {
    let mut fds = [-1_i32; 2];
    // SAFETY: pipe(2) writes two new descriptors into the two-element array it is given
    let made = unsafe { pipe(fds.as_mut_ptr()) };
    if made == 0 {
        listen(fds);
    }
}

/// The thread on the pipe's read end, then the two signals caught.
fn listen(fds: [i32; 2]) {
    WRITE_END.store(fds[1], Ordering::Relaxed);
    // SAFETY: the read end is this process's own new descriptor, owned by the file from here on and by nothing else
    let mut read = unsafe { std::fs::File::from_raw_fd(fds[0]) };
    std::thread::spawn(move || {
        let mut byte = [0_u8];
        if read.read_exact(&mut byte).is_ok() {
            remove_and_exit(i32::from(byte[0]));
        }
    });
    for signum in [SIGINT, SIGTERM] {
        // SAFETY: the handler only writes one byte to a pipe; a disposition the process started with as ignored is put back
        unsafe {
            let before = signal(signum, on_signal as usize);
            signal(
                signum,
                [on_signal as usize, IGNORED][usize::from(before == IGNORED)],
            );
        }
    }
}

/// On INT or TERM: every directory still held removed, then the exit the signal would have made.
fn remove_and_exit(signum: i32) -> ! {
    let live = LIVE.lock().map(|l| l.clone()).unwrap_or_default();
    for path in live {
        let _ = std::fs::remove_dir_all(path);
    }
    std::process::exit(128 + signum)
}
