#!/usr/bin/env bash
# t562: the live bytes and file count of the tests' TMPDIRs (/tmp/l7r-tmp) every 2 s. Usage: t562-tmpdu.sh OUT SECONDS
end=$(( $(date +%s) + $2 ))
while [ "$(date +%s)" -lt "$end" ]; do
  printf '%s\t%s\t%s\n' "$(date -u +%T)" "$(du -sb /tmp/l7r-tmp 2>/dev/null | cut -f1)" "$(find /tmp/l7r-tmp 2>/dev/null | wc -l)"
  sleep 2
done > "$1"
