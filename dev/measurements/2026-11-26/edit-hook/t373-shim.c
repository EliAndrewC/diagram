// t373 measurement shim (LD_PRELOAD; strace is refused in this container). One line an event appended to T373_OUT:
//   <monotonic ms> <pid> <ppid> START <argv>        a process image begins (constructor)
//   <monotonic ms> <pid> <ppid> END reads=<n> writes=<n> spawns=<n>   it exits (destructor; an image replaced by exec has no END)
//   <monotonic ms> <pid> <ppid> SPAWN <path>        fork / vfork / posix_spawn(p) / execve / execvp is called
//   <monotonic ms> <pid> <ppid> OPENW|OPENR <path>  open / open64 / openat / openat64 / fopen / fopen64 (W: any write flag or O_CREAT)
//   <monotonic ms> <pid> <ppid> MKDIR|RENAME|UNLINK <path>
#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <spawn.h>
#include <stdarg.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>
static atomic_long n_r, n_w, n_s;
static double now(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec*1e3+t.tv_nsec/1e6; }
static void say(const char*k,const char*d){ const char*o=getenv("T373_OUT"); if(!o) return; char b[4600];
  int n=snprintf(b,sizeof b,"%.3f %d %d %s %s\n",now(),getpid(),getppid(),k,d?d:""); if(n>(int)sizeof b) n=sizeof b;
  static int(*ro)(const char*,int,...); if(!ro) ro=dlsym(RTLD_NEXT,"open"); int fd=ro(o,O_WRONLY|O_APPEND|O_CREAT,0644); if(fd<0) return; (void)!write(fd,b,n); close(fd); }
__attribute__((constructor)) static void in(void){ char c[4000]={0}; FILE*(*rf)(const char*,const char*)=dlsym(RTLD_NEXT,"fopen"); FILE*f=rf("/proc/self/cmdline","r"); size_t k=0;
  if(f){ k=fread(c,1,sizeof c-1,f); fclose(f);} for(size_t i=0;i+1<k;i++) if(!c[i]) c[i]=' '; if(k>600) c[600]=0; say("START",c); }
__attribute__((destructor)) static void out(void){ char b[120]; snprintf(b,sizeof b,"reads=%ld writes=%ld spawns=%ld",(long)n_r,(long)n_w,(long)n_s); say("END",b); }
static void op(const char*p,int fl){ if(fl&(O_WRONLY|O_RDWR|O_CREAT|O_APPEND|O_TRUNC)){ n_w++; say("OPENW",p);} else { n_r++; say("OPENR",p);} }
#define OPEN2(name) int name(const char*p,int fl,...){ static int(*r)(const char*,int,...); if(!r) r=dlsym(RTLD_NEXT,#name); mode_t m=0; if(fl&O_CREAT){va_list a;va_start(a,fl);m=va_arg(a,mode_t);va_end(a);} op(p,fl); return r(p,fl,m); }
OPEN2(open) OPEN2(open64)
#define OPENAT(name) int name(int d,const char*p,int fl,...){ static int(*r)(int,const char*,int,...); if(!r) r=dlsym(RTLD_NEXT,#name); mode_t m=0; if(fl&O_CREAT){va_list a;va_start(a,fl);m=va_arg(a,mode_t);va_end(a);} op(p,fl); return r(d,p,fl,m); }
OPENAT(openat) OPENAT(openat64)
#define FOPEN(name) FILE* name(const char*p,const char*m){ static FILE*(*r)(const char*,const char*); if(!r) r=dlsym(RTLD_NEXT,#name); op(p,(m&&(strchr(m,'w')||strchr(m,'a')||strchr(m,'+')))?O_WRONLY:0); return r(p,m); }
FOPEN(fopen) FOPEN(fopen64)
int mkdir(const char*p,mode_t m){ static int(*r)(const char*,mode_t); if(!r) r=dlsym(RTLD_NEXT,"mkdir"); n_w++; say("MKDIR",p); return r(p,m); }
int rename(const char*a,const char*b){ static int(*r)(const char*,const char*); if(!r) r=dlsym(RTLD_NEXT,"rename"); n_w++; say("RENAME",b); return r(a,b); }
int unlink(const char*p){ static int(*r)(const char*); if(!r) r=dlsym(RTLD_NEXT,"unlink"); n_w++; say("UNLINK",p); return r(p); }
pid_t fork(void){ static pid_t(*r)(void); if(!r) r=dlsym(RTLD_NEXT,"fork"); n_s++; say("SPAWN","fork"); return r(); }
int posix_spawn(pid_t*pid,const char*p,const posix_spawn_file_actions_t*fa,const posix_spawnattr_t*at,char*const av[],char*const ev[]){ static int(*r)(pid_t*,const char*,const posix_spawn_file_actions_t*,const posix_spawnattr_t*,char*const[],char*const[]); if(!r) r=dlsym(RTLD_NEXT,"posix_spawn"); n_s++; say("SPAWN",p); return r(pid,p,fa,at,av,ev); }
int posix_spawnp(pid_t*pid,const char*p,const posix_spawn_file_actions_t*fa,const posix_spawnattr_t*at,char*const av[],char*const ev[]){ static int(*r)(pid_t*,const char*,const posix_spawn_file_actions_t*,const posix_spawnattr_t*,char*const[],char*const[]); if(!r) r=dlsym(RTLD_NEXT,"posix_spawnp"); n_s++; say("SPAWN",p); return r(pid,p,fa,at,av,ev); }
int execve(const char*p,char*const av[],char*const ev[]){ static int(*r)(const char*,char*const[],char*const[]); if(!r) r=dlsym(RTLD_NEXT,"execve"); say("SPAWN",p); return r(p,av,ev); }
int execvp(const char*p,char*const av[]){ static int(*r)(const char*,char*const[]); if(!r) r=dlsym(RTLD_NEXT,"execvp"); say("SPAWN",p); return r(p,av); }
