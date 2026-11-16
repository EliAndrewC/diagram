#!/usr/bin/env bash
# failed-open-log.sh - the ONE guard-log entry written without a binary: `l7r-guard.sh`'s "failed-open", where no good guard binary
# has ever been built and the gate's has not been either (feature 449 T143, its plan review: "it is the only record that the guards did
# not run, on exactly the fresh unbuilt tree where nothing else leaves one").
#
# WHY A SECOND WRITER, AND ONLY HERE: every other entry is the Rust's (`l7r-gate log guard`, over `rust/guard/src/shared/log.rs` and
# `shared/session.rs`), and so is this one wherever the gate has a binary. Where neither binary exists there is nothing to run but the
# shell, and `guard_log`'s inline Python - which wrote this entry before T143 - is gone. So this writes, with `jq` and the shell, the
# bytes that Python wrote on this path: its fields in its order, `json.dumps(indent=2)` with every non-ASCII character escaped (`jq -a
# --indent 2` escapes as `ensure_ascii` does), each field `payload.get(k) or ""`, the session's name as `clone-resolve.sh resolve`
# found it (the claim map's last line, else the transcript's last /rename, else the sessions json, kebab-cased), and the file
# `<UTC to the nanosecond>-<pid>.json` written to a temporary and renamed into place. Do not call it from anywhere else: a second
# writer for every entry is what FR-003 forbids.
#
# Its known edges, each a payload Claude Code never sends: a float's digits are jq's shortest form, which is Python's repr but for
# literals jq reads otherwise (`nan` in lower case, which Python refuses); without `iconv`, input that is not UTF-8 alongside a real
# U+FFFD is read as UTF-8; with no `jq` at all (it is in the container image, `setup-dev-env.sh`) the entry is written with the input unread.

# _fo_space: Python's `str.isspace` characters, for the kebab case (`re`'s `\s` in the Python).
_fo_space=$'\t\n\v\f\r\x1c\x1d\x1e\x1f \xc2\x85\xc2\xa0\xe1\x9a\x80\xe2\x80\x80\xe2\x80\x81\xe2\x80\x82\xe2\x80\x83\xe2\x80\x84\xe2\x80\x85\xe2\x80\x86\xe2\x80\x87\xe2\x80\x88\xe2\x80\x89\xe2\x80\x8a\xe2\x80\xa8\xe2\x80\xa9\xe2\x80\xaf\xe2\x81\x9f\xe3\x80\x80'

# _fo_blank <text>: true when Python's `text.strip()` is empty
_fo_blank() {
  local LC_ALL=C.UTF-8
  [[ -z "${1//[$_fo_space]/}" ]]
}

# _fo_kebab <name>: `re.sub(r'\s+', '-', re.sub(r'[^a-z0-9\s-]', '', name.lower()).strip())`
_fo_kebab() {
  local LC_ALL=C.UTF-8 n=${1,,} ext
  n=${n//[!a-z0-9${_fo_space}-]/}
  while [[ -n "$n" && "${n:0:1}" == [$_fo_space] ]]; do n=${n:1}; done
  while [[ -n "$n" && "${n: -1}" == [$_fo_space] ]]; do n=${n:0:${#n}-1}; done
  ext=$(shopt -p extglob); shopt -s extglob
  n=${n//+([$_fo_space])/-}
  eval "$ext"
  printf '%s' "$n"
}

# _fo_name <tree>: the name `guard_log` recorded from `clone-resolve.sh resolve` for $INPUT - or nothing
_fo_name() {
  local tree=$1 sid tp cwd top main sdir f out line title found='' name='' source='' crash=''
  # the three string fields as the resolver's Python read them: a string, else ""; a NUL dropped; input not JSON reads none
  [[ "$INPUT" == $'\xef\xbb\xbf'* ]] && return 0
  { IFS= read -r -d '' sid; IFS= read -r -d '' tp; IFS= read -r -d '' cwd; } < <(printf '%s' "$INPUT" | jq -j -s 'def s: if type == "string" then gsub("\u0000"; "") else "" end;
    (if length == 1 then .[0] else null end) | if type == "object" then [(.session_id|s), (.transcript_path|s), (.cwd|s)] else ["", "", ""] end | map(. + "\u0000") | add' 2>/dev/null)
  [ -n "$sid" ] || return 0
  top=$(git -C "${cwd:-/nonexistent}" rev-parse --show-toplevel 2>/dev/null || true)
  case "$top" in
    */.clones/*) main=${top%%/.clones/*} ;;
    "") main=$tree ;;
    *) main=$top ;;
  esac
  main=${CLONE_MAIN:-$main}
  sdir=${CLONE_SESSIONS_DIR:-${HOME:-/home/agent}/.claude/sessions}
  if [ -f "$main/.clones/.session-clones/$sid" ]; then
    out=$(cat "$main/.clones/.session-clones/$sid" 2>/dev/null | tail -1)
    printf '%s' "${out##*/}"
    return 0
  fi
  # the transcript's last /rename: a record that is no dict ended the Python's lookup with nothing
  if [ -n "$tp" ] && [ -f "$tp" ]; then
    [ -r "$tp" ] || return 0
    # read straight from jq: a shell variable cannot hold the NUL that separates the titles
    while IFS= read -r -d '' line; do
      [ "$line" = $'\x01crash' ] && crash=1
      [ "$line" = $'\x01crash' ] || _fo_blank "$line" || { title=$line; found=1; }
    done < <(grep -a 'custom-title' "$tp" 2>/dev/null | tr '\r' '\n' | grep -a 'custom-title' | jq -R -j 'def py: if . == null or . == false or . == 0 or . == "" or . == [] or . == {} then "" elif type == "string" then . else tojson end;
      (try fromjson catch "\u0001skip") as $r | if $r == "\u0001skip" then empty elif ($r|type) != "object" then "\u0001crash\u0000"
      elif $r.type == "custom-title" then ($r.customTitle|py) + "\u0000" else empty end' 2>/dev/null)
    [ -n "$crash" ] && return 0
    [ -n "$found" ] && { name=$title; source=transcript; }
  fi
  if [ -z "$found" ] && [ -d "$sdir" ]; then
    while IFS= read -r -d '' f; do
      [[ "$(head -c3 "$f" 2>/dev/null)" == $'\xef\xbb\xbf' ]] && continue
      # three NUL-ended fields straight from jq (a variable cannot hold a NUL): what it found, the name, its source
      out='' name='' source=''
      { IFS= read -r -d '' out; IFS= read -r -d '' name; IFS= read -r -d '' source; } < <(jq -j -s --arg sid "$sid" 'def py: if . == null or . == false or . == 0 or . == "" or . == [] or . == {} then "" elif type == "string" then . else tojson end;
        (if length == 1 then .[0] else error("not one document") end)
        | if type != "object" then "crash\u0000" elif ([.id, .sessionId, .session_id] | index($sid)) != null
        then "found\u0000" + (.name|py) + "\u0000" + (.nameSource | if type == "string" then . else "" end) + "\u0000" else "no\u0000" end' "$f" 2>/dev/null)
      [ "$out" = crash ] && return 0
      [ "$out" = found ] && { found=1; break; }
    done < <(find "$sdir" -mindepth 1 -maxdepth 1 -name '*.json' ! -name '.*' -print0 2>/dev/null)
  fi
  [ -n "$found" ] || return 0
  if [ "$source" = derived ] || _fo_blank "$name"; then
    name=${main%/}; name=${name##*/}
  fi
  _fo_kebab "$name"
}

# _fo_surrogates <text>: each byte of <text> that UTF-8 cannot take marked (\x01SUR<hex>\x02), which the entry's text writes as the
# `\udcXX` Python's `surrogateescape` argv carried into `json.dumps` (a claim map's bytes reach the name as they stand)
_fo_surrogates() {
  local LC_ALL=C s=$1 out='' i=0 n b need j c ok
  n=${#s}
  while (( i < n )); do
    printf -v b '%d' "'${s:i:1}"
    (( b < 0 )) && (( b += 256 ))
    if (( b < 0x80 )); then out+=${s:i:1}; (( i++ )); continue; fi
    need=0
    if (( b >= 0xc2 && b <= 0xdf )); then need=1; elif (( b >= 0xe0 && b <= 0xef )); then need=2; elif (( b >= 0xf0 && b <= 0xf4 )); then need=3; fi
    ok=$(( need > 0 && i + need < n + 0 + 1 ))
    for (( j = 1; ok && j <= need; j++ )); do
      (( i + j < n )) || { ok=0; break; }
      printf -v c '%d' "'${s:i+j:1}"; (( c < 0 )) && (( c += 256 ))
      (( c >= 0x80 && c <= 0xbf )) || ok=0
    done
    if (( ok )); then out+=${s:i:need+1}; (( i += need + 1 )); else printf -v c '%02x' "$b"; out+=$'\x01'SUR$c$'\x02'; (( i++ )); fi
  done
  printf '%s' "$out"
}

# _fo_utf8 <text>: true when <text> is UTF-8 (`json.load(open(...))` raised on bytes that are not): iconv's answer, else jq's - its
# U+FFFD for a byte it could not read, absent from a text that holds no real one
_fo_utf8() {
  if command -v iconv >/dev/null 2>&1; then printf '%s' "$1" | iconv -f UTF-8 -t UTF-8 >/dev/null 2>&1; return; fi
  [[ "$1" == *$'\xef\xbf\xbd'* ]] && return 0
  ! printf '%s' "$1" | jq -c '..|strings' 2>/dev/null | grep -q $'\xef\xbf\xbd'
}

# failed_open_log <detail> <tree>: the entry, as `guard_log l7r-guard failed-open <detail> failed-open` wrote it with $INPUT and $SID
failed_open_log() {
  local detail=$1 tree=$2 dir ts f name payload utc text sidenv=${SID:-unknown}
  dir=${GUARD_LOG_DIR:-$HOME/.claude/guard-log}
  mkdir -p "$dir" 2>/dev/null || return 0
  ts=$(date -u +%Y%m%dT%H%M%S%6N 2>/dev/null || date -u +%Y%m%dT%H%M%S)
  f="$dir/$ts-$$.json"
  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  if ! command -v jq >/dev/null 2>&1; then
    # no jq: the input unread (a known edge, the header), the fields as the Python wrote them for an input of `{}`
    local s=$sidenv; case "$s" in unknown|nosession|"") s=unknown ;; esac
    s=${s//\\/\\\\}; s=${s//\"/\\\"}
    detail=${detail:0:200}; detail=${detail//\\/\\\\}; detail=${detail//\"/\\\"}
    text=$(printf '{\n  "utc": "%s",\n  "guard": "l7r-guard",\n  "event": "failed-open",\n  "rule": "failed-open",\n  "session": "%s",\n  "session_name": "%s",\n  "cwd": "",\n  "tool": "",\n  "transcript": "",\n  "detail": "%s",\n  "command": "",\n  "context": null\n}' "$utc" "$s" "$s" "$detail")
  else
    # the input as the writer's `json.load(open(...))` read it: one JSON document, UTF-8, no byte-order mark - else `{}`
    payload=$INPUT
    if [[ "$INPUT" == $'\xef\xbb\xbf'* ]] || ! printf '%s' "$INPUT" | jq -e -s 'length == 1' >/dev/null 2>&1; then
      payload='{}'
    elif ! _fo_utf8 "$INPUT"; then
      payload='{}'
    fi
    name=$(_fo_surrogates "$(_fo_name "$tree")")
    # a number written as Python's `json.dumps` writes what `json.load` made of it: an integer's digits kept ("-0" is 0), a float its
    # repr (".0" on a whole one, "-0.0", Infinity past the double's range, NaN) - carried out of jq as a marked string, unmarked below
    text=$(printf '%s' "$payload" | jq -a --indent 2 --arg utc "$utc" --arg detail "$detail" --arg name "$name" --arg sidenv "$sidenv" '
      def falsy: . == null or . == false or . == 0 or . == "" or . == [] or . == {};
      def or_(d): if falsy then d else . end;
      def pynum: tojson as $lit |
        if ($lit | test("^-?[0-9]+$")) then (if ($lit | test("^-0+$")) then "0" else $lit end)
        elif isnan then "NaN"
        elif (fabs >= 1.7976931348623157e+308) and ($lit | test("^-?1\\.7976931348623157e\\+?308$") | not) then (if . < 0 then "-Infinity" else "Infinity" end)
        else ((. + 0) | tojson) as $t |
          if (. == 0) and ($lit | startswith("-")) then "-0.0"
          elif ($t | test("[.eE]")) then $t else $t + ".0" end
        end | "\u0000NUM:" + .;
      def nums: walk(if type == "number" then pynum else . end);
      (if type == "object" then . else {} end) as $p
      | (($p.tool_input // {}) | if type == "object" then . else {} end) as $ti
      | ($p.session_id | or_(if ($sidenv == "unknown" or $sidenv == "nosession") then "" else $sidenv end | or_("unknown"))) as $session
      | {utc: $utc, guard: "l7r-guard", event: "failed-open", rule: "failed-open", session: $session,
         session_name: ($name | or_($session)), cwd: ($p.cwd | or_("")), tool: ($p.tool_name | or_("")),
         transcript: ($p.transcript_path | or_("")), detail: $detail[0:200], command: ($ti.command | or_($ti.file_path | or_(""))),
         context: null} | nums' 2>/dev/null) || return 0
    text=$(printf '%s' "$text" | sed -E -e 's/"\\u0000NUM:([^"]*)"/\1/g' -e 's/\\u0001SUR([0-9a-f]{2})\\u0002/\\udc\1/g')
  fi
  printf '%s' "$text" > "$f.tmp" 2>/dev/null && mv -f "$f.tmp" "$f" 2>/dev/null
  return 0
}
