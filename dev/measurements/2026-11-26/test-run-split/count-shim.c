// 451 T315: an LD_PRELOAD shim that COUNTS the file calls of a test run and of every process it starts (strace is refused in the
// container). Counters live in one shared file, T315_COUNTS, mapped by every process, so a fork, an exec and an _exit lose nothing.
// A LOWER BOUND: a file glibc opens for itself (fopen) does not pass through these symbols.
// build: gcc -O2 -shared -fPIC -o count-shim.so count-shim.c -ldl
#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

enum { CREAT, MKDIR, UNLINK, RMDIR, RENAME, FSYNC, FDATASYNC, SYNC_RANGE, EXEC, N };
static long fallback[N];
static long *c = fallback;

__attribute__((constructor)) static void init(void) {
    const char *p = getenv("T315_COUNTS");
    if (!p) return;
    int fd = open(p, O_RDWR);
    if (fd < 0) return;
    void *m = mmap(0, sizeof(long) * N, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    close(fd);
    if (m != MAP_FAILED) { c = m; __sync_fetch_and_add(&c[EXEC], 1); }
}
#define BUMP(i) __sync_fetch_and_add(&c[i], 1)
#define REAL(name) static typeof(name) *real; if (!real) real = dlsym(RTLD_NEXT, #name)

static mode_t mode_of(int flags, va_list ap) { return (flags & (O_CREAT | O_TMPFILE)) ? va_arg(ap, mode_t) : 0; }
int open(const char *p, int f, ...) { REAL(open); va_list a; va_start(a, f); mode_t m = mode_of(f, a); va_end(a); if (f & O_CREAT) BUMP(CREAT); return real(p, f, m); }
int open64(const char *p, int f, ...) { REAL(open64); va_list a; va_start(a, f); mode_t m = mode_of(f, a); va_end(a); if (f & O_CREAT) BUMP(CREAT); return real(p, f, m); }
int openat(int d, const char *p, int f, ...) { REAL(openat); va_list a; va_start(a, f); mode_t m = mode_of(f, a); va_end(a); if (f & O_CREAT) BUMP(CREAT); return real(d, p, f, m); }
int openat64(int d, const char *p, int f, ...) { REAL(openat64); va_list a; va_start(a, f); mode_t m = mode_of(f, a); va_end(a); if (f & O_CREAT) BUMP(CREAT); return real(d, p, f, m); }
int creat(const char *p, mode_t m) { REAL(creat); BUMP(CREAT); return real(p, m); }
int mkdir(const char *p, mode_t m) { REAL(mkdir); BUMP(MKDIR); return real(p, m); }
int mkdirat(int d, const char *p, mode_t m) { REAL(mkdirat); BUMP(MKDIR); return real(d, p, m); }
int unlink(const char *p) { REAL(unlink); BUMP(UNLINK); return real(p); }
int unlinkat(int d, const char *p, int f) { REAL(unlinkat); BUMP((f & AT_REMOVEDIR) ? RMDIR : UNLINK); return real(d, p, f); }
int rmdir(const char *p) { REAL(rmdir); BUMP(RMDIR); return real(p); }
int rename(const char *a, const char *b) { REAL(rename); BUMP(RENAME); return real(a, b); }
int renameat(int d, const char *a, int e, const char *b) { REAL(renameat); BUMP(RENAME); return real(d, a, e, b); }
int fsync(int fd) { REAL(fsync); BUMP(FSYNC); return real(fd); }
int fdatasync(int fd) { REAL(fdatasync); BUMP(FDATASYNC); return real(fd); }
int sync_file_range(int fd, off64_t o, off64_t n, unsigned int f) { REAL(sync_file_range); BUMP(SYNC_RANGE); return real(fd, o, n, f); }
