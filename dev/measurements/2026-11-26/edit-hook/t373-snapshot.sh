#!/bin/bash
# t373: snapshot of every real place a hook could write: line counts, sizes and mtimes. Run before and after; diff.
G=/diagram/.clones/diagram-backlog/.git
{
for d in $G/l7r-events $G/l7r-events-dispatches $G/l7r-cache $G/l7r-lists $G/l7r-said /diagram/.git/l7r-events ~/.cache/l7r ~/.claude/guard-log ~/.claude/logs; do
  [ -e "$d" ] && find "$d" -maxdepth 2 -type f -printf '%p %s %T@\n' 2>/dev/null
done
find $G -maxdepth 1 -type f -printf '%p %s %T@\n'
find /diagram/.git -maxdepth 1 -type f -printf '%p %s %T@\n'
find /diagram/.clones -maxdepth 1 -type f -printf '%p %s %T@\n'
find ~/.cache -maxdepth 2 -newermt '-2 hours' -printf '%p %s %T@\n' 2>/dev/null | head -200
} | sort
