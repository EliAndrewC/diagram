/* What a program a tooling test starts reads, recorded by the C library (feature 383 amendment 3, plan D26).
 *
 * Preloaded (LD_PRELOAD) into every child of a recording tooling test: the C library's ways in to a path are wrapped, and
 * each path under the repository (L7R_TEST_DEP_ROOT) is written to the test's log (L7R_TEST_DEP_LOG) as
 * "<test file>\tc-<kind>\t<path>" - the line Python's own recorder writes (`sitecustomize.py`), its kind marked `c-` so each run
 * can check this recorder against Python's. `file` is a path opened for reading, stat-ed or tested for access; `dir` a directory
 * opened or listed. The test's own process (L7R_TEST_DEP_SELF) is not recorded here: its Python audit hook records it. A path opened for writing is not a read. Built by
 * `tests/tooling/_test_deps.py` with `gcc -shared -fPIC -O2 -ldl`; nothing here may write to stdout or stderr.
 *
 * A wrapper can only see a call that crosses into the library: a call the library makes to itself (fopen's own open, glob's
 * own opendir) does not, which is why fopen, opendir and scandir are wrapped themselves. Whether that leaves a gap is
 * measured, not assumed: every Python child carries both recorders, and a test fails on any file Python saw opened that this
 * did not (`tests/tooling/test_reuse_and_quotes.py`).
 */
#define _GNU_SOURCE
#include <dirent.h>
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>

static __thread int busy;  /* the recorder's own calls are not recorded */

static void normalize(char *p) {  /* "/a/./b/../c" -> "/a/c", in place */
    char out[PATH_MAX];
    size_t n = 0;
    const char *s = p;
    while (*s) {
        while (*s == '/') s++;
        if (!*s) break;
        const char *e = strchr(s, '/');
        size_t len = e ? (size_t)(e - s) : strlen(s);
        if (len == 1 && s[0] == '.') {
        } else if (len == 2 && s[0] == '.' && s[1] == '.') {
            while (n > 0 && out[n - 1] != '/') n--;
            if (n > 0) n--;
        } else if (n + 1 + len < sizeof out) {
            out[n++] = '/';
            memcpy(out + n, s, len);
            n += len;
        }
        s += len;
    }
    if (n == 0) out[n++] = '/';
    out[n] = 0;
    strcpy(p, out);
}

static void note(int dirfd, const char *path, const char *kind) {  /* kind may be replaced below */
    if (busy || !path || !*path) return;
    const char *log = getenv("L7R_TEST_DEP_LOG"), *root = getenv("L7R_TEST_DEP_ROOT"), *file = getenv("L7R_TEST_DEP_FILE");
    if (!log || !root || !file || !*file) return;
    /* git's own reads of the repository are its answer, which the git question replays (plan D18) - not file reads; but a git
     * that reads the repository's own git directory is noted once as `c-git`: a guard suite that clones the real repository
     * reads its content through git, and is never traced (D27). Programs in L7R_TEST_DEP_SKIP (a suite's `cp` building its
     * fixture) are not recorded either: copying is not running. */
    const char *prog = program_invocation_short_name;
    int is_git = strcmp(prog, "git") == 0 || strncmp(prog, "git-", 4) == 0;
    const char *skip = getenv("L7R_TEST_DEP_SKIP");
    if (!is_git && skip) {
        size_t pl = strlen(prog);
        for (const char *q = skip; (q = strstr(q, prog)) != NULL; q += pl)
            if ((q == skip || q[-1] == ' ') && (q[pl] == 0 || q[pl] == ' ')) return;
    }
    const char *self = getenv("L7R_TEST_DEP_SELF");  /* the test's own process records itself, in Python */
    if (self && atol(self) == (long)getpid()) return;
    busy = 1;
    int saved = errno;
    char abs[PATH_MAX];
    if (path[0] == '/') {
        snprintf(abs, sizeof abs, "%s", path);
    } else {
        char base[PATH_MAX] = "";
        if (dirfd != AT_FDCWD && dirfd >= 0) {
            char link[64];
            snprintf(link, sizeof link, "/proc/self/fd/%d", dirfd);
            ssize_t k = readlink(link, base, sizeof base - 1);
            base[k > 0 ? k : 0] = 0;
        } else if (!getcwd(base, sizeof base)) {
            base[0] = 0;
        }
        snprintf(abs, sizeof abs, "%s/%s", base, path);
    }
    normalize(abs);
    /* L7R_TEST_DEP_MAP=scripts: a guard suite's fixture holds a COPY of scripts/ under /tmp; a file the suite runs there is the
     * repository's own file of that name (D27) */
    const char *map = getenv("L7R_TEST_DEP_MAP");
    if (map && *map && strncmp(abs, "/tmp/", 5) == 0) {
        char key[PATH_MAX];
        snprintf(key, sizeof key, "/%s/", map);
        char *at = NULL;
        for (char *q = strstr(abs, key); q; q = strstr(q + 1, key)) at = q;
        if (at) {
            char mapped[PATH_MAX];
            snprintf(mapped, sizeof mapped, "%s%s", root, at);
            snprintf(abs, sizeof abs, "%s", mapped);
        }
    }
    size_t r = strlen(root);
    if (is_git) {
        char gitdir[PATH_MAX];
        snprintf(gitdir, sizeof gitdir, "%s/.git", root);
        if (strncmp(abs, gitdir, strlen(gitdir)) == 0) kind = "git";
        else { errno = saved; busy = 0; return; }
    }
    if (strncmp(abs, root, r) == 0 && (abs[r] == 0 || abs[r] == '/')) {
        char line[PATH_MAX + 512];
        int n = snprintf(line, sizeof line, "%s\tc-%s\t%s\n", file, kind, abs);  /* c-: this recorder's, kept apart to check it */
        int (*real_open)(const char *, int, ...) = (int (*)(const char *, int, ...))dlsym(RTLD_NEXT, "open");
        int fd = real_open(log, O_WRONLY | O_APPEND | O_CREAT | O_CLOEXEC, 0644);
        if (fd >= 0) {
            ssize_t w = write(fd, line, n > 0 && (size_t)n < sizeof line ? (size_t)n : 0);
            (void)w;
            close(fd);
        }
    }
    errno = saved;
    busy = 0;
}

static void note_open(int dirfd, const char *path, int flags) {
    if ((flags & O_ACCMODE) == O_RDONLY) note(dirfd, path, (flags & O_DIRECTORY) ? "dir" : "file");
}

#define REAL(name) static void *real_##name; if (!real_##name) real_##name = dlsym(RTLD_NEXT, #name)
#define CALL(name, type) ((type)real_##name)

#define OPEN_LIKE(name)                                                     \
    int name(const char *path, int flags, ...) {                            \
        REAL(name);                                                         \
        mode_t mode = 0;                                                    \
        if (flags & (O_CREAT | O_TMPFILE)) {                                \
            va_list ap; va_start(ap, flags); mode = va_arg(ap, mode_t); va_end(ap); \
        }                                                                   \
        note_open(AT_FDCWD, path, flags);                                   \
        return ((int (*)(const char *, int, ...))real_##name)(path, flags, mode);                              \
    }
OPEN_LIKE(open)
OPEN_LIKE(open64)

#define OPENAT_LIKE(name)                                                   \
    int name(int dirfd, const char *path, int flags, ...) {                 \
        REAL(name);                   \
        mode_t mode = 0;                                                    \
        if (flags & (O_CREAT | O_TMPFILE)) {                                \
            va_list ap; va_start(ap, flags); mode = va_arg(ap, mode_t); va_end(ap); \
        }                                                                   \
        note_open(dirfd, path, flags);                                      \
        return ((int (*)(int, const char *, int, ...))real_##name)(dirfd, path, flags, mode);                       \
    }
OPENAT_LIKE(openat)
OPENAT_LIKE(openat64)

int __open_2(const char *path, int flags) { REAL(__open_2); note_open(AT_FDCWD, path, flags); return CALL(__open_2, int (*)(const char *, int))(path, flags); }
int __open64_2(const char *path, int flags) { REAL(__open64_2); note_open(AT_FDCWD, path, flags); return CALL(__open64_2, int (*)(const char *, int))(path, flags); }
int __openat_2(int d, const char *path, int flags) { REAL(__openat_2); note_open(d, path, flags); return CALL(__openat_2, int (*)(int, const char *, int))(d, path, flags); }
int __openat64_2(int d, const char *path, int flags) { REAL(__openat64_2); note_open(d, path, flags); return CALL(__openat64_2, int (*)(int, const char *, int))(d, path, flags); }

static int read_mode(const char *mode) { return mode && mode[0] == 'r' && !strchr(mode, '+'); }
FILE *fopen(const char *path, const char *mode) { REAL(fopen); if (read_mode(mode)) note(AT_FDCWD, path, "file"); return CALL(fopen, FILE *(*)(const char *, const char *))(path, mode); }
FILE *fopen64(const char *path, const char *mode) { REAL(fopen64); if (read_mode(mode)) note(AT_FDCWD, path, "file"); return CALL(fopen64, FILE *(*)(const char *, const char *))(path, mode); }

int stat(const char *path, struct stat *st) { REAL(stat); note(AT_FDCWD, path, "file"); return CALL(stat, int (*)(const char *, struct stat *))(path, st); }
int lstat(const char *path, struct stat *st) { REAL(lstat); note(AT_FDCWD, path, "file"); return CALL(lstat, int (*)(const char *, struct stat *))(path, st); }
int stat64(const char *path, struct stat64 *st) { REAL(stat64); note(AT_FDCWD, path, "file"); return CALL(stat64, int (*)(const char *, struct stat64 *))(path, st); }
int lstat64(const char *path, struct stat64 *st) { REAL(lstat64); note(AT_FDCWD, path, "file"); return CALL(lstat64, int (*)(const char *, struct stat64 *))(path, st); }
int fstatat(int d, const char *path, struct stat *st, int fl) { REAL(fstatat); if (!(fl & AT_EMPTY_PATH) || (path && *path)) note(d, path, "file"); return CALL(fstatat, int (*)(int, const char *, struct stat *, int))(d, path, st, fl); }
int fstatat64(int d, const char *path, struct stat64 *st, int fl) { REAL(fstatat64); if (!(fl & AT_EMPTY_PATH) || (path && *path)) note(d, path, "file"); return CALL(fstatat64, int (*)(int, const char *, struct stat64 *, int))(d, path, st, fl); }
int statx(int d, const char *path, int fl, unsigned int mask, struct statx *st) { REAL(statx); if (!(fl & AT_EMPTY_PATH) || (path && *path)) note(d, path, "file"); return CALL(statx, int (*)(int, const char *, int, unsigned int, struct statx *))(d, path, fl, mask, st); }
int access(const char *path, int m) { REAL(access); note(AT_FDCWD, path, "file"); return CALL(access, int (*)(const char *, int))(path, m); }
int faccessat(int d, const char *path, int m, int fl) { REAL(faccessat); note(d, path, "file"); return CALL(faccessat, int (*)(int, const char *, int, int))(d, path, m, fl); }
int euidaccess(const char *path, int m) { REAL(euidaccess); note(AT_FDCWD, path, "file"); return CALL(euidaccess, int (*)(const char *, int))(path, m); }
int eaccess(const char *path, int m) { REAL(eaccess); note(AT_FDCWD, path, "file"); return CALL(eaccess, int (*)(const char *, int))(path, m); }
ssize_t readlink(const char *path, char *buf, size_t n) { REAL(readlink); note(AT_FDCWD, path, "file"); return CALL(readlink, ssize_t (*)(const char *, char *, size_t))(path, buf, n); }
ssize_t readlinkat(int d, const char *path, char *buf, size_t n) { REAL(readlinkat); note(d, path, "file"); return CALL(readlinkat, ssize_t (*)(int, const char *, char *, size_t))(d, path, buf, n); }
DIR *opendir(const char *path) { REAL(opendir); note(AT_FDCWD, path, "dir"); return CALL(opendir, DIR *(*)(const char *))(path); }
int scandir(const char *path, struct dirent ***list, int (*sel)(const struct dirent *), int (*cmp)(const struct dirent **, const struct dirent **)) {
    REAL(scandir);
    note(AT_FDCWD, path, "dir");
    return CALL(scandir, int (*)(const char *, struct dirent ***, int (*)(const struct dirent *), int (*)(const struct dirent **, const struct dirent **)))(path, list, sel, cmp);
}
int scandir64(const char *path, struct dirent64 ***list, int (*sel)(const struct dirent64 *), int (*cmp)(const struct dirent64 **, const struct dirent64 **)) {
    REAL(scandir64);
    note(AT_FDCWD, path, "dir");
    return CALL(scandir64, int (*)(const char *, struct dirent64 ***, int (*)(const struct dirent64 *), int (*)(const struct dirent64 **, const struct dirent64 **)))(path, list, sel, cmp);
}

/* node's libuv reaches openat and statx by number through syscall() */
long syscall(long number, ...) {
    REAL(syscall);
    va_list ap;
    va_start(ap, number);
    long a[6];
    for (int i = 0; i < 6; i++) a[i] = va_arg(ap, long);
    va_end(ap);
#ifdef SYS_openat
    if (number == SYS_openat) note_open((int)a[0], (const char *)a[1], (int)a[2]);
#endif
#ifdef SYS_statx
    if (number == SYS_statx && (!((int)a[2] & AT_EMPTY_PATH) || (a[1] && *(const char *)a[1]))) note((int)a[0], (const char *)a[1], "file");
#endif
#ifdef SYS_open
    if (number == SYS_open) note_open(AT_FDCWD, (const char *)a[0], (int)a[1]);
#endif
    return CALL(syscall, long (*)(long, ...))(number, a[0], a[1], a[2], a[3], a[4], a[5]);
}
