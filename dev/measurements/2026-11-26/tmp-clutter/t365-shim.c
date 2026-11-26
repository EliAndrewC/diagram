// t365 measurement shim (LD_PRELOAD): strace is refused in this container (ptrace: Operation not permitted), so the directory
// listings are counted in-process. Counts opendir() of the temp directory (T365_DIR), the readdir64() calls on it, the wall time from
// each opendir to its closedir, and statx/stat of /proc/<pid>; one line a process appended to T365_OUT at exit.
#define _GNU_SOURCE
#include <dirent.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>
static atomic_long n_open, n_open_other, n_readdir, ns_listing, n_proc, n_mkdir;
static __thread DIR *cur; static __thread struct timespec t0;
static const char *want(void){ static const char *w; if(!w){ w=getenv("T365_DIR"); if(!w) w="/tmp"; } return w; }
static int same(const char *p){ const char *w=want(); size_t n=strlen(w); return strncmp(p,w,n)==0 && (p[n]==0 || (p[n]=='/'&&p[n+1]==0)); }
DIR *opendir(const char *p){ static DIR*(*real)(const char*); if(!real) real=dlsym(RTLD_NEXT,"opendir"); DIR*d=real(p);
  if(p&&same(p)){ n_open++; cur=d; clock_gettime(CLOCK_MONOTONIC,&t0);} else n_open_other++; return d; }
struct dirent64 *readdir64(DIR *d){ static struct dirent64*(*real)(DIR*); if(!real) real=dlsym(RTLD_NEXT,"readdir64"); if(d==cur) n_readdir++; return real(d); }
int closedir(DIR *d){ static int(*real)(DIR*); if(!real) real=dlsym(RTLD_NEXT,"closedir");
  if(d&&d==cur){ struct timespec t1; clock_gettime(CLOCK_MONOTONIC,&t1); ns_listing+=(t1.tv_sec-t0.tv_sec)*1000000000L+(t1.tv_nsec-t0.tv_nsec); cur=NULL;} return real(d); }
static int isproc(const char*p){ return p&&strncmp(p,"/proc/",6)==0&&p[6]>='0'&&p[6]<='9'&&!strchr(p+6,'/'); }
int statx(int fd,const char*restrict p,int fl,unsigned m,struct statx*restrict b){ static int(*real)(int,const char*,int,unsigned,struct statx*); if(!real) real=dlsym(RTLD_NEXT,"statx"); if(isproc(p)) n_proc++; return real(fd,p,fl,m,b); }
int mkdir(const char*p,mode_t m){ static int(*real)(const char*,mode_t); if(!real) real=dlsym(RTLD_NEXT,"mkdir"); n_mkdir++; return real(p,m); }
__attribute__((destructor)) static void out(void){ const char*o=getenv("T365_OUT"); if(!o) return; char exe[256]={0}; ssize_t k=readlink("/proc/self/exe",exe,255); if(k<0) exe[0]=0;
  if(!n_open&&!n_proc) { if(!getenv("T365_ALL")) return; }
  FILE*f=fopen(o,"a"); if(!f) return; fprintf(f,"pid=%d exe=%s listings=%ld readdir=%ld listing_ms=%.3f other_opendir=%ld proc_pid_stat=%ld mkdir=%ld\n",getpid(),exe,(long)n_open,(long)n_readdir,ns_listing/1e6,(long)n_open_other,(long)n_proc,(long)n_mkdir); fclose(f); }
