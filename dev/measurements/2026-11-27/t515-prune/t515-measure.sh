#!/bin/bash
# T515 measurement, READ-ONLY: stat only (find -printf), never a read of a file's contents (that would move its atime).
# For every profile (a directory holding .fingerprint) of every build directory, what an in-place prune WOULD take:
# units (crate-hash across deps/, .fingerprint/, build/) and incremental crate directories, each judged by its last use
# (the newest mtime of anything in it and atime of any regular file in it) against STALE hours, the newest per key kept.
# MODE=abs: stale when last + STALE < now. MODE=rel: stale when last + STALE < the profile's own last use.
# KEY=crate: newest per crate kept. KEY=kind: newest per crate and fingerprint kind (lib-x, test-lib-x, ...) kept.
STALE=${STALE:-48}; MODE=${MODE:-rel}; ROOT=${ROOT:-$HOME/.cache/l7r-cargo-target}
now=$(date +%s)
for fp in $(find "$ROOT" -mindepth 2 -maxdepth 6 -name .fingerprint -type d); do
  prof=${fp%/.fingerprint}
  for s in deps .fingerprint build incremental; do
    [ -d "$prof/$s" ] || continue
    find "$prof/$s" -mindepth 1 -printf "$s\t%P\t%y\t%T@\t%A@\t%b\t%n\n"
  done | awk -F'\t' -v prof="$prof" -v root="$ROOT/" -v now=$now -v stale=$STALE -v mode=$MODE -v key="${KEY:-crate}" -v list="${LIST:-}" -v sig="${SIG:-nojson}" '
  function unitof(store, e,   n, ext, stem, h) {
    # e: the entry name under the store; a deps file maps to its crate-hash
    if (store != "deps") return e
    n = e; ext = ""
    if (match(n, /\.[a-z]+$/)) { ext = substr(n, RSTART+1); n = substr(n, 1, RSTART-1) }
    if (ext=="rlib"||ext=="rmeta"||ext=="so"||ext=="a") sub(/^lib/, "", n)
    return n
  }
  {
    split($2, p, "/"); e = p[1]
    u = ($1=="incremental" ? "I:" e : "U:" unitof($1, e))
    ent[u] = ent[u] "\n" $1 "/" e
    t = $4 + 0; if ($3=="f" && $5+0 > t && (sig=="all" || (sig=="nojson" && $2 !~ /\.json$/))) t = $5 + 0
    if (t > last[u]) last[u] = t
    if ($3=="f" && ($7+0)==1 || $3!="f") bytes[u] += $6*512
    if ($1==".fingerprint" && $3=="f" && $2 !~ /\.json$/ && $2 !~ /invoked.timestamp/ && $2 !~ /\/dep-/ && $2 !~ /\/output-/) {
      split($2, q, "/"); kinds[u] = kinds[u] " " q[2]
    }
    if (t > plast) plast = t
  }
  END {
    for (u in last) {
      c = substr(u, 3); sub(/-[^-]*$/, "", c)
      k = substr(u,1,2) c
      if (key=="kind" && substr(u,1,2)=="U:") { split(kinds[u], ks, " "); k = k "|" ks[1] }
      if (last[u] > best[k]) best[k] = last[u]
    }
    ref = (mode=="abs" ? now : plast)
    for (u in last) {
      c = substr(u, 3); sub(/-[^-]*$/, "", c)
      k = substr(u,1,2) c
      if (key=="kind" && substr(u,1,2)=="U:") { split(kinds[u], ks, " "); k = k "|" ks[1] }
      if (last[u] < best[k] && last[u] + stale*3600 < ref) {
        if (substr(u,1,2)=="I:") { ib += bytes[u]; ic++ } else { ub += bytes[u]; uc++ }
        if (list != "") print prof ent[u] > list
      }
      if (substr(u,1,2)=="I:") it += bytes[u]; else ut += bytes[u]
    }
    name = prof; sub(root, "", name)
    printf "%s\t%.2f\t%d\t%.2f\t%d\t%.2f\t%.1f\n", name, ub/1e9, uc, ib/1e9, ic, (ut+it)/1e9, (now-plast)/3600
  }'
done | sort | awk -F'\t' 'BEGIN{print "profile\tunits_GB\tunits\tincr_GB\tincr_dirs\tstores_GB\tprofile_idle_h"} {print; split($1,a,"/"); T[a[1]]+=$2+$4; tot+=$2+$4} END{for (t in T) printf "TREE %s %.1f GB\n", t, T[t]; printf "TOTAL %.1f GB\n", tot}'
