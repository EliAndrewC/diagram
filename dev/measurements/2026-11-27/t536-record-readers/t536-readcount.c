/* 451 T536: an LD_PRELOAD shim that counts the bytes each process reads of each file - strace is refused in this container
 * (ptrace: Operation not permitted). It wraps open/open64/openat/openat64 (fd -> path), read/pread/pread64/readv and close, and
 * on exit appends "pid<TAB>path<TAB>bytes<TAB>calls" for every path matching T536_PREFIX (a colon-separated list of directory
 * prefixes) to the file T536_LOG. It also logs any open for writing outside T536_SAFE as "WRITE<TAB>path". Children inherit it
 * through LD_PRELOAD, so a gate command's own subprocesses (git, the guard's asks) are counted too.
 * Build: gcc -shared -fPIC -O2 -o t536-readcount.so t536-readcount.c -ldl */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/uio.h>
#include <unistd.h>

#define MAXFD 4096
static char *paths[MAXFD];
static long long bytes[MAXFD], calls[MAXFD];

struct tot { char *path; long long bytes, calls; struct tot *next; };
static struct tot *tots;

static int wanted(const char *p) {
    const char *pre = getenv("T536_PREFIX");
    if (!pre || !p) return 0;
    char buf[4096];
    strncpy(buf, pre, sizeof buf - 1);
    buf[sizeof buf - 1] = 0;
    for (char *s = strtok(buf, ":"); s; s = strtok(NULL, ":"))
        if (strncmp(p, s, strlen(s)) == 0) return 1;
    return 0;
}

static void fold(int fd) {
    if (fd < 0 || fd >= MAXFD || !paths[fd]) return;
    struct tot *t = tots;
    while (t && strcmp(t->path, paths[fd])) t = t->next;
    if (!t) { t = calloc(1, sizeof *t); t->path = paths[fd]; t->next = tots; tots = t; } else free(paths[fd]);
    t->bytes += bytes[fd]; t->calls += calls[fd];
    paths[fd] = NULL; bytes[fd] = calls[fd] = 0;
}

static void opened(int fd, const char *path, int flags) {
    if (fd < 0 || fd >= MAXFD) return;
    char abs[4096];
    if (path[0] != '/') { if (!getcwd(abs, sizeof abs - 2)) return; strcat(abs, "/"); strncat(abs, path, sizeof abs - strlen(abs) - 1); }
    else { strncpy(abs, path, sizeof abs - 1); abs[sizeof abs - 1] = 0; }
    if ((flags & (O_WRONLY | O_RDWR | O_CREAT))) {
        const char *safe = getenv("T536_SAFE"), *log = getenv("T536_LOG");
        if (safe && log && strncmp(abs, safe, strlen(safe)) && strncmp(abs, "/dev/", 5) && strncmp(abs, "/proc/", 6)) {
            FILE *f = fopen(log, "a"); /* our own fopen goes through open, never recursing: it is under T536_SAFE */
            if (f) { fprintf(f, "WRITE\t%s\n", abs); fclose(f); }
        }
    }
    fold(fd);
    if (wanted(abs)) paths[fd] = strdup(abs);
}

#define WRAP_OPEN(name)                                                                     \
    int name(const char *p, int flags, ...) {                                               \
        static int (*real)(const char *, int, ...);                                         \
        if (!real) real = dlsym(RTLD_NEXT, #name);                                          \
        mode_t m = 0;                                                                       \
        if (flags & (O_CREAT | O_TMPFILE)) { va_list a; va_start(a, flags); m = va_arg(a, mode_t); va_end(a); } \
        int fd = real(p, flags, m);                                                         \
        opened(fd, p, flags);                                                               \
        return fd;                                                                          \
    }
WRAP_OPEN(open)
WRAP_OPEN(open64)

#define WRAP_OPENAT(name)                                                                   \
    int name(int d, const char *p, int flags, ...) {                                        \
        static int (*real)(int, const char *, int, ...);                                    \
        if (!real) real = dlsym(RTLD_NEXT, #name);                                          \
        mode_t m = 0;                                                                       \
        if (flags & (O_CREAT | O_TMPFILE)) { va_list a; va_start(a, flags); m = va_arg(a, mode_t); va_end(a); } \
        int fd = real(d, p, flags, m);                                                      \
        opened(fd, p, flags);                                                               \
        return fd;                                                                          \
    }
WRAP_OPENAT(openat)
WRAP_OPENAT(openat64)

static void count(int fd, ssize_t n) {
    if (n > 0 && fd >= 0 && fd < MAXFD && paths[fd]) { bytes[fd] += n; calls[fd]++; }
}

ssize_t read(int fd, void *b, size_t n) {
    static ssize_t (*real)(int, void *, size_t);
    if (!real) real = dlsym(RTLD_NEXT, "read");
    ssize_t r = real(fd, b, n); count(fd, r); return r;
}
ssize_t pread(int fd, void *b, size_t n, off_t o) {
    static ssize_t (*real)(int, void *, size_t, off_t);
    if (!real) real = dlsym(RTLD_NEXT, "pread");
    ssize_t r = real(fd, b, n, o); count(fd, r); return r;
}
ssize_t pread64(int fd, void *b, size_t n, off_t o) {
    static ssize_t (*real)(int, void *, size_t, off_t);
    if (!real) real = dlsym(RTLD_NEXT, "pread64");
    ssize_t r = real(fd, b, n, o); count(fd, r); return r;
}
ssize_t readv(int fd, const struct iovec *v, int c) {
    static ssize_t (*real)(int, const struct iovec *, int);
    if (!real) real = dlsym(RTLD_NEXT, "readv");
    ssize_t r = real(fd, v, c); count(fd, r); return r;
}
int close(int fd) {
    static int (*real)(int);
    if (!real) real = dlsym(RTLD_NEXT, "close");
    fold(fd);
    return real(fd);
}

__attribute__((destructor)) static void done(void) {
    for (int fd = 0; fd < MAXFD; fd++) fold(fd);
    const char *log = getenv("T536_LOG");
    if (!log || !tots) return;
    FILE *f = fopen(log, "a");
    if (!f) return;
    for (struct tot *t = tots; t; t = t->next) fprintf(f, "%d\t%s\t%lld\t%lld\n", getpid(), t->path, t->bytes, t->calls);
    fclose(f);
}
