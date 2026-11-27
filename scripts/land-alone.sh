#!/usr/bin/env bash
# land-alone.sh <feature> "<T1 [T2 ...]>" - A TASK LANDS ON ITS OWN (feature 451 T88). `make land` runs this when work is uncommitted in
# the clone (`rust/gate/crates/land/src/land/alone.rs`): the landing runs whole - `make land` again, every refusal and gate of it - in the
# clone's persistent landing worktree, checked out at the clone's HEAD (the task's own commit on the last landed tip), apart from the
# other tasks' unfinished work; then the clone takes the landed tip, its uncommitted work kept.
#
# WHY (measured 2026-11-21, T88's plan section): builders ran three at once 26% of the night's 580 minutes because a landing refused any
# uncommitted file, so tasks landed in batches. Of the three ways: a gate in the clone holds every other builder's writes while it runs
# (gate_write_hooks; 1.12 edits a builder-minute, a 31 s median gate) and judges their half-done files; a set-aside of those files takes
# them from under builders still editing them; judging the task's files alone pushes a tree nobody judged. The worktree's cost: its gate
# reuses the clone's kept results (the keys are the files' contents: a fresh worktree's `make static` 114 s with them, 2,321 s without),
# its own target directory (~/.cache/l7r-cargo-target/<clone>-land) built once and kept, and its disk.
#
# Steps, each refusing with what to do: (1) one landing alone at a time (a lock); (2) THE TASK'S OWN SECTIONS COMMITTED APART (451 T101):
# the feature's plan.md, tasks.md and plan-review.json hold every open task's section, line and verdict, so the clone's HEAD takes a
# commit of each built from HEAD's file with only the landing tasks' own pieces replaced (and the tasks.md line of a task their section
# files, never its section or verdict, 451 T180) - the
# clone's other uncommitted text stays in its files, and the landing's commit holds none of it (T95, CLEAR, could not land alone on
# 2026-11-21: plan.md also held T82's and T97's unreviewed sections); (3) the landing tasks' own other files still uncommitted - a line
# filed under the task names them, an edit's path or a Bash call's `writes` (451 T96: the closing checks' attribution) - refused, named;
# files no task's line names, and another task's by its task, stay in the clone, listed, not landed; (4) the
# worktree created, or reset to the clone's HEAD (it is the tool's: nobody's work lives there); (5) the clone's kept check results and
# suite results seeded where newer (`cp -u`); (6) the landing in the worktree (`L7R_LAND_ALONE=1`: its tree is the landing, its `end` line
# its own); (7) the clone takes the landed tip: HEAD moved, each changed file the clone holds no work in written from the tip, each one it
# does merged three ways with its uncommitted edit kept on top - git's line merge, each hunk both sides only added to taken whole where
# one side's lines hold the other's; a sectioned file (plan.md, tasks.md, plan-review.json, the review ledger) whose line merge
# conflicts merged piece by piece: a section, a task's line, a verdict, a ledger row keyed by its pass (the tip's row kept where both
# answer one), each archive mark a piece of its own (the tick's archive of one section beside another task's edit of the next
# conflicts in text alone; 451 T105: the three shapes the take gave up on, 2026-11-21); only a piece both changed otherwise conflicts,
# every conflict named at once, and a conflict moves nothing.
# Exit: the landing's own code (0 landed, 3 landed with other sessions' edits merged, 2 refused), 6 refused before it ran (the clone's
# landing writes that one's `end` line and exits 2), 4 landed but the clone could not take the tip (it says how to).
set -u
F=${1:?usage: land-alone.sh <feature> "<tasks>"}
T=${2:?usage: land-alone.sh <feature> "<tasks>"}
ROOT=$(git rev-parse --show-toplevel) || exit 2
COMMON=$(git -C "$ROOT" rev-parse --path-format=absolute --git-common-dir) || exit 2
WT=${LAND_ALONE_TREE:-$(dirname "$ROOT")/$(basename "$ROOT")-land}
MAKE=${LAND_ALONE_MAKE:-make}
say() { printf 'land-alone: %s\n' "$*"; }
die() { printf 'land-alone: refused - nothing landed: %s\n' "$*" >&2; exit 6; }
t0=${EPOCHREALTIME/,/.}
lap() { local t=${EPOCHREALTIME/,/.}; awk -v a="$t0" -v b="$t" 'BEGIN { printf "%.1f", b - a }'; t0=$t; }

# The script's Python, one program: `py <mode> <args>` - `stage` (step 2), `split` (step 3), `take` (step 7).
read -r -d '' PYLIB <<'PY'
import datetime, glob, json, os, re, subprocess, sys, tempfile, time
SECTIONED = ('plan.md', 'tasks.md', 'plan-review.json')
# the review ledger, merged at the take by line (451 T105): the clone's `make ledger-owed` rows and the landing's beside them
LEDGER = ('dev/review-ledger.md', 'review-ledger.md')
HEADING = re.compile(r'#{2,4}\s')
# the line a tick leaves where a landed task's section was (`plan/sections.rs`'s ARCHIVE_MARK, feature 375 FR-044): a piece of its
# own, never the tail of the section before it, which the clone may be editing (451 T105, T113's landing)
MARKER = '<!-- plan-archive: '
OWN = re.compile(r'#{2,4}\s+(T\d+[a-z]?)\b')
TASK = re.compile(r'(\s*)- \[[ xX]\] (T\d+[a-z]?)\b')
FILED = re.compile(r'Filed as (T\d+[a-z]?)\b')

def git(root, *a, inp=None, ok=(0,), env=None):
    r = subprocess.run(['git', '-C', root, *a], capture_output=True, input=inp, env=env)
    if r.returncode not in ok:
        sys.exit(f"land-alone: git {' '.join(a)}: {r.stderr.decode(errors='replace').strip()}")
    return r

def dirty_of(root):
    recs, out, i = git(root, 'status', '--porcelain=v1', '-z', '-uall').stdout.decode().split('\0'), set(), 0
    while i < len(recs):
        r, i = recs[i], i + 1
        if len(r) > 3:
            out.add(r[3:])
            i += r[0] in 'RC'
    return out

def row_key(line):
    # a measured ledger row's pass: its check and its cost cells, as `settle::unanswered` answers a pass by them (feature 371)
    cells = [' '.join(c.split()) for c in line.strip()[1:-1].split('|')] if line.strip().startswith('|') else []
    return f'row:{cells[1]}|{cells[8]}|{cells[9]}' if len(cells) == 10 else None

def units(name, text):
    # [(key, text)]: plan.md cut at each heading - one opening with a task id is that task's (`task:T<n>`, plan_text.rs's rule) - and
    # at each archive marker; tasks.md at each task line with the lines indented under it; the ledger at each line, a measured row
    # keyed by its pass; any other piece keyed by its heading or line, counted where repeated
    out, seen, lines = [], {}, text.splitlines(keepends=True)
    def add(key, body):
        if not key.startswith('task:'):
            seen[key] = seen.get(key, 0) + 1
            key = f'{key}#{seen[key]}'
        out.append((key, body))
    if name == LEDGER[1]:
        for l in lines:
            add(row_key(l) or l.rstrip('\n'), l)
        return out
    if name == 'plan.md':
        key, body = 'preamble', []
        for l in lines:
            if HEADING.match(l) or l.startswith(MARKER):
                add(key, ''.join(body))
                m = OWN.match(l)
                key, body = ('task:' + m.group(1)) if m else l.strip(), []
            body.append(l)
        add(key, ''.join(body))
        return out
    i = 0
    while i < len(lines):
        m, j = TASK.match(lines[i]), i + 1
        while m and j < len(lines) and lines[j].strip() and lines[j].startswith((m.group(1) + ' ', m.group(1) + '\t')):
            j += 1
        add('task:' + m.group(2) if m else lines[i], ''.join(lines[i:j]))
        i = j
    return out

def join(us):
    last = len(us) - 1
    return ''.join(b if not b or b.endswith('\n') or k == last else b + '\n' for k, (_, b) in enumerate(us))

def grouped(us):
    out = {}
    for k, b in us:
        out[k] = join([('', out[k]), ('', b)]) if k in out else b
    return list(out.items())

def anchor(out, ours, key, past=()):
    # where `key` goes in `out`: after the piece `ours` puts nearest before it, and after the pieces `past` names that follow it (the
    # tip's own new pieces there - an archived section's markers - go before the clone's)
    first = next((i for i, (k, _) in enumerate(ours) if k == key), 0)
    for k, _ in reversed(ours[:first]):
        if not k.rsplit('#', 1)[0].strip():  # a blank line, repeated everywhere, places nothing
            continue
        at = [i for i, (o, _) in enumerate(out) if o == k]
        if at:
            i = at[-1] + 1
            while i < len(out) and out[i][0] in past:
                i += 1
            return i
    return 0

def splice(name, head, work, keys):
    # HEAD's file with only `keys`' pieces taken from the working file
    out, w = units(name, head), units(name, work)
    for key in keys:
        mine = [u for u in w if u[0] == key]
        at = next((i for i, (k, _) in enumerate(out) if k == key), None)
        out = [u for u in out if u[0] != key]
        at = anchor(out, w, key) if at is None else at
        out[at:at] = mine
    return join(out)

def piece_name(key):
    # a conflicting piece as its file names it: a task's section or line, a ledger row's pass, a heading or line
    if key.startswith('task:'):
        return f"{key[5:]}'s section, changed otherwise on both sides"
    if key.startswith('verdict:'):
        return f"the verdict {key[8:]!r}, changed otherwise on both sides"
    if key.startswith('row:'):
        return f"the ledger row of the pass {key[4:].rsplit('#', 1)[0]!r}, changed otherwise on both sides"
    return f"the piece {key.rsplit('#', 1)[0][:80]!r}, changed otherwise on both sides"

def owner(key):
    m = OWN.match(key)
    return m.group(1) if m else None

def dump(v):
    return json.dumps(v, indent=1, ensure_ascii=False) + '\n'

def stage_review(head, work, tasks):
    # plan-review.json: HEAD's verdicts with the tasks' own entries - `tasks[T]`, its blocks' and its block reviews - taken from work
    h, w = (json.loads(x) if x.strip() else {} for x in (head, work))
    mine = {'blocks': lambda k: owner(k) in tasks, 'tasks': lambda k: k in tasks}
    out = dict(h)
    if 'feature' in w:
        out.setdefault('feature', w['feature'])
    for part, own in mine.items():
        hp, wp = h.get(part, {}), w.get(part, {})
        new = {k: (wp[k] if own(k) else v) for k, v in hp.items() if not own(k) or k in wp}
        new.update((k, v) for k, v in wp.items() if own(k) and k not in hp)
        if new or part in h:
            out[part] = new
    reviews = list(h.get('block_reviews', []))
    reviews += [r for r in w.get('block_reviews', []) if r not in reviews and r.get('blocks') and all(owner(k) in tasks for k in r['blocks'])]
    if reviews or 'block_reviews' in h:
        out['block_reviews'] = reviews
    return head if out == h else dump(out)

def merge3(base, ours, theirs, hunks=True, union=False):
    # git's line merge of three texts, and (`hunks`) of each hunk it leaves where both sides only added lines, the side whose added
    # lines hold the other's in order (the same lines written on both sides, one side's with more: 451 T105) - or, `union` (an
    # append-only `.jsonl` log: the arbiter's, 451 T202), both sides' lines, the clone's first and the tip's it does not hold after;
    # None while any is more
    with tempfile.TemporaryDirectory() as d:
        tmp = [os.path.join(d, k) for k in ('ours', 'base', 'theirs')]
        for t, x in zip(tmp, (ours, base, theirs)):
            open(t, 'wb').write(x)
        r = subprocess.run(['git', 'merge-file', '-p', '--diff3', '--marker-size=31', *tmp], capture_output=True)
    if r.returncode == 0:
        return r.stdout
    if not hunks:
        return None
    if r.returncode < 0 or r.returncode > 127:
        sys.exit(f"land-alone: git merge-file: {r.stderr.decode(errors='replace').strip()}")
    out, part, hunk = [], None, {}
    for l in r.stdout.splitlines(keepends=True):
        mark = l[:32]
        if part is None and mark == b'<' * 31 + b' ':
            part, hunk = 'ours', {'ours': [], 'base': [], 'theirs': []}
        elif part == 'ours' and mark == b'|' * 31 + b' ':
            part = 'base'
        elif part in ('ours', 'base') and l.rstrip(b'\r\n') == b'=' * 31:
            part = 'theirs'
        elif part == 'theirs' and mark == b'>' * 31 + b' ':
            o, t = hunk['ours'], hunk['theirs']
            if hunk['base'] or not (union or holds(o, t) or holds(t, o)):
                return None
            out += o + [x for x in t if x not in o] if union else o if holds(o, t) else t
            part = None
        elif part:
            hunk[part].append(l)
        else:
            out.append(l)
    return b''.join(out)

def unblank(text):
    # a piece's lines but its blank ones
    return [l for l in text.splitlines() if l.strip()]

def holds(big, small):
    # `small`'s lines in `big`, in their order
    it = iter(big)
    return all(any(x == y for y in it) for x in small)

def merge_pieces(name, base, ours, theirs):
    # a three-way merge piece by piece: each piece the clone changed put on the tip's; a piece both changed, merged by line (merge3);
    # (text, None), or (None, the piece's key) where the tip changed a piece the clone changed otherwise
    if name == 'plan-review.json':
        return merge_review(*(json.loads(x) if x.strip() else {} for x in (base, ours, theirs)))
    b, o, t = (dict(grouped(units(name, x))) for x in (base, ours, theirs))
    out, olist = list(t.items()), list(o.items())
    past = {k for k in t if k not in b and k not in o}
    for k, v in olist:
        # a piece the clone changed only in its blank lines is no change of the clone's (451 T202: the blank line the clone put after
        # an archive mark the tick then rewrote gave up the take twice on 2026-11-23, T187+T191's and T184+T196's)
        if b.get(k) == v or t.get(k) == v or (k in b and unblank(b[k]) == unblank(v)):
            continue
        if k in b and k not in t:
            return None, k  # the tip archived or removed a piece the clone changed
        if k in t and t[k] != b.get(k):
            if name == LEDGER[1] and k not in b and k.startswith('row:'):
                continue  # one pass answered on both sides: the tip's row answers it, the clone's is dropped
            v = merge3(*(x.encode() for x in (b.get(k, ''), v, t[k])))
            if v is None:
                return None, k
            v = v.decode()
        at = [i for i, (key, _) in enumerate(out) if key == k]
        if at:
            out[at[0]] = (k, v)
        else:
            out.insert(anchor(out, olist, k, past), (k, v))
    for k in b:
        if k not in o and k in t:
            if t[k] != b[k]:
                return None, k
            out = [u for u in out if u[0] != k]
    return join(out), None

def merge_review(b, o, t):
    out = dict(t)
    for k in dict.fromkeys([*b, *o]):
        if k == 'block_reviews':
            out[k] = list(t.get(k, [])) + [r for r in o.get(k, []) if r not in b.get(k, []) and r not in t.get(k, [])]
        elif k in ('blocks', 'tasks'):
            bp, op, tp = b.get(k, {}), o.get(k, {}), dict(t.get(k, {}))
            for kk in dict.fromkeys([*bp, *op]):
                if op.get(kk) == bp.get(kk):
                    continue
                if tp.get(kk) not in (bp.get(kk), op.get(kk)):
                    return None, f'verdict:{k}:{kk}'
                if kk in op:
                    tp[kk] = op[kk]
                else:
                    tp.pop(kk, None)
            out[k] = tp
        elif o.get(k) != b.get(k):
            if t.get(k) not in (b.get(k), o.get(k)):
                return None, f'verdict:{k}'
            out[k] = o[k]
    return dump(out), None

def stage(root, feature, tasks):
    # step 2: the clone's HEAD takes the landing tasks' own pieces of the sectioned files, its working files untouched
    rel, head = f'specs/{feature}', git(root, 'rev-parse', 'HEAD').stdout.decode().strip()
    show = lambda p: git(root, 'show', f'HEAD:{p}', ok=(0, 128)).stdout.decode()
    read = lambda p: open(os.path.join(root, p), encoding='utf-8').read() if os.path.isfile(os.path.join(root, p)) else None
    plan = read(f'{rel}/plan.md') or ''
    own = [u for u in units('plan.md', plan) if u[0] in {'task:' + t for t in tasks}]
    # a task the landing's sections file (`Filed as T<n>`) lands its tasks.md line alone, which the deferral rule needs open in the
    # landed tree (451 T17); its plan section and verdict are its own builder's, never this landing's (451 T180: 449 T351's landing
    # committed T377's filled section and BLOCKED verdict, and its tick refused on that block)
    filed = [f for f in dict.fromkeys(f for _, b in own for f in FILED.findall(b)) if f not in tasks]
    staged = {}
    for f in SECTIONED:
        p, work = f'{rel}/{f}', read(f'{rel}/{f}')
        old = show(p)
        if work is None or work == old:
            continue
        lines = tasks + filed if f == 'tasks.md' else tasks
        new = stage_review(old, work, tasks) if f.endswith('.json') else splice(f, old, work, ['task:' + t for t in lines])
        if new != old:
            staged[p] = new
    if not staged:
        return
    env = dict(os.environ, GIT_INDEX_FILE=os.path.join(git(root, 'rev-parse', '--absolute-git-dir').stdout.decode().strip(), 'land-staged.index'))
    git(root, 'read-tree', head, env=env)
    for p, text in staged.items():
        blob = git(root, 'hash-object', '-w', '--stdin', inp=text.encode()).stdout.decode().strip()
        git(root, 'update-index', '--add', '--cacheinfo', f'100644,{blob},{p}', env=env)
    tree = git(root, 'write-tree', env=env).stdout.decode().strip()
    os.remove(env['GIT_INDEX_FILE'])
    lines = f" and the tasks.md lines of the tasks they file ({' '.join(filed)})" if filed else ''
    msg = f"{feature} {' '.join(tasks)}: their own plan sections, tasks.md lines and verdicts{lines}, apart from the other open tasks' (land-alone, 451 T101)"
    new = git(root, 'commit-tree', tree, '-p', head, '-m', msg).stdout.decode().strip()
    # compare and swap: a landing that moved HEAD meanwhile leaves this one refused, the working files as they were
    git(root, 'update-ref', '-m', 'land-alone: the task\'s own sections', 'HEAD', new, head)
    git(root, 'reset', '-q', '--', *staged)
    print('staged\t' + ' '.join(staged))

def edit_inputs(lines):
    # each Edit end's call - its `old_string` and `new_string` - read from its agent's transcript (`<projects>/*/<sid>.jsonl`, or
    # `<sid>/subagents/agent-<by>.jsonl`) by its tool-use id; None where any cannot be read (the event line carries only digests)
    projects = os.environ.get('L7R_PROJECTS_DIR') or os.path.expanduser('~/.claude/projects')
    want, out = {}, {}
    for d in lines:
        if d is None or not d.get('id') or not d.get('sid'):
            return None
        tail = f"{d['sid']}/subagents/agent-{d['by']}.jsonl" if d.get('by') else f"{d['sid']}.jsonl"
        found = glob.glob(os.path.join(projects, '*', tail))
        if not found:
            return None
        want.setdefault(found[0], set()).add(d['id'])
    for path, ids in want.items():
        for l in open(path, errors='replace'):
            if '"tool_use"' not in l or not any(i in l for i in ids):
                continue
            try:
                blocks = json.loads(l)['message']['content']
            except (ValueError, KeyError, TypeError):
                continue
            for b in blocks if isinstance(blocks, list) else []:
                if isinstance(b, dict) and b.get('id') in ids and isinstance(b.get('input'), dict):
                    i = b['input']
                    out[b['id']] = (str(i.get('old_string', '')), str(i.get('new_string', '')), i.get('replace_all') is True)
    return [out[d['id']] for d in lines] if all(d['id'] in out for d in lines) else None

def inside(line, s):
    # is the diff's `line` one an edit's string `s` wrote: a whole line of it, the string itself within the line (an edit inside one
    # line), or its first line's end or last line's start (a string cut mid-line)
    if not line.strip() or not s.strip():
        return False
    parts = s.split('\n')
    if len(parts) == 1:
        return s.strip() in line
    first, last = parts[0], parts[-1]
    return line in parts[1:-1] or (first.strip() and line.endswith(first)) or (last.strip() and line.startswith(last))

def leaves_change(root, rel, lines):
    # (451 T202) does a task's run of edits of `rel` leave a change of its own: a hunk of the file's uncommitted diff with a line one
    # of its edits wrote (`new_string`) or removed (`old_string`)? T197's builder added the REJUDGE= lines to the Makefile and took them
    # out again, and T195+T197's landing was refused on T198's lines there (observed 2026-11-23). A write no Edit's strings show (a
    # Write, a Bash call's), or an Edit whose call cannot be read, leaves one: failing toward the refusal, never a landing short of
    # the task's own edit. A `replace_all` edit's string is one the file repeats, so another task's line holding it is no line the
    # edit wrote (451 T202's MODE 4, D8): its one-line string counts only as one of its replacements - the line with the string put
    # back on the hunk's other side.
    calls = edit_inputs(lines)
    if calls is None:
        return True
    diff = git(root, 'diff', '-U0', 'HEAD', '--', rel).stdout.decode(errors='replace').splitlines()
    hunks, hunk = [], None
    for l in diff:
        if l.startswith('@@'):
            hunk = []
            hunks.append(hunk)
        elif hunk is not None and l[:1] in '+-' and not l.startswith(('+++', '---')):
            hunk.append(l)
    def wrote(l, h, old, new, every):
        if not inside(l[1:], new if l[0] == '+' else old):
            return False
        if not every or '\n' in old or '\n' in new:
            return True
        return ('-' + l[1:].replace(new, old) if l[0] == '+' else '+' + l[1:].replace(old, new)) in h
    return any(wrote(l, h, *call) for h in hunks for l in h for call in calls)

def split(root, events, feature, tasks):
    # step 3: the landing tasks' own files - those a line filed under one of them names, by the closing checks' attribution
    # (`scripts/gates/closing-checks.sh`, 451 T86, T93; read here since 451 T96): an edit tool's end its path, a Bash call's end
    # (`PostToolUse` or `PostToolUseFailure`) a file of its `writes` - the exact path, never a directory's files; not a fallback line; not
    # one older than the file's last commit or than its own task's last landing (`<feature>: T.. ticked (make land)`). A line's task is
    # its editor's - the task the editing agent's brief names, its builder's or its page session's, the clone's mark only for the main
    # session's own lines (451 T161, `event_log_hooks/filed.rs`) - so another builder's edit made under this landing's mark is not its own
    dirty = dirty_of(root)
    since, last, landed, at = time.time() - 7 * 86400, {}, {}, 0
    for l in git(root, 'log', '--since=7.days', '--format=@%ct %s', '--name-only').stdout.decode().splitlines():
        if l.startswith('@'):
            at, _, subject = l[1:].partition(' ')
            at = int(at)
            m = re.match(r'(\S+): ((?:T\d+ )+)ticked \(make land\)', subject)
            for t in (m.group(2).split() if m else []):
                landed.setdefault((m.group(1), t), at)
        elif l:
            last.setdefault(l, at)
    pre, own, named, others, calls = root.rstrip('/') + '/', set(), set(), {}, {}
    sectioned = {f'specs/{feature}/{f}' for f in SECTIONED}
    for p in sorted(glob.glob(os.path.join(events, '*.jsonl'))):
        stem = os.path.basename(p)[:-6]
        for l in open(p, errors='replace'):
            edit = '"PostToolUse"' in l and '"cat":"edit"' in l
            if not edit and '"writes":' not in l:
                continue
            try:
                d = json.loads(l)
            except ValueError:
                continue
            if d.get('fallback') or not d.get('task') or not str(d.get('ev', '')).startswith('PostToolUse'):
                continue
            writes = d.get('writes') if isinstance(d.get('writes'), list) else []
            rels = {w[len(pre):] for w in ([d.get('path', '')] if edit else []) + writes if isinstance(w, str) and w.startswith(pre)} & dirty
            at = datetime.datetime.fromisoformat(d['t'].replace('Z', '+00:00')).timestamp() if rels else 0
            if at < landed.get((stem, d['task']), 0):
                continue
            mine = d['task'] in tasks and (stem == feature or stem.startswith(feature + '-'))
            for rel in rels:
                if at < last.get(rel, since):
                    continue
                named.add(rel)
                # the sectioned files are staged by section (step 2): what is left uncommitted in them is other tasks'
                if mine and rel not in sectioned:
                    own.add(rel)
                    calls.setdefault(rel, []).append(d if edit and d.get('tool') == 'Edit' else None)
                elif not mine and rel not in sectioned:
                    others.setdefault(rel, set()).add(d['task'])
    put_back = {r for r in own if not leaves_change(root, r, calls[r])}
    own -= put_back
    for r in sorted(own):
        print('own\t' + r)
    for r in sorted(put_back):
        print('putback\t' + r)
    for r in sorted(dirty - named):
        print('unnamed\t' + r)
    # another task's, listed by task, so a line filed under a wrong number is seen (451 T96: T101's builder, briefed as T100, wrote
    # ready.rs, speckit.rs and land-alone.sh under T100, and T82-T101's list named none of them)
    by = {}
    for r in sorted(set(others) - own):
        for t in sorted(others[r]):
            by.setdefault(t, []).append(r)
    for t, rs in sorted(by.items()):
        print('other\t' + t + ': ' + ' '.join(rs))

def take(root, tip, feature):
    # step 7: the tip, or - the clone committed since the landing began - a merge of the two, made without touching the tree
    old = git(root, 'rev-parse', 'HEAD').stdout.decode().strip()
    if git(root, 'merge-base', '--is-ancestor', old, tip, ok=(0, 1)).returncode == 0:
        new = tip
    else:
        r = git(root, 'merge-tree', '--write-tree', old, tip, ok=(0, 1))
        if r.returncode:
            sys.exit('land-alone: the clone\'s commits since the landing began conflict with the landed tip')
        tree = r.stdout.decode().split('\n')[0]
        new = git(root, 'commit-tree', tree, '-p', old, '-p', tip, '-m', f'Merge the landed {tip[:10]} into the clone (land-alone, 451 T88)').stdout.decode().strip()
    changed = [p for p in git(root, 'diff', '--no-renames', '--name-only', '-z', old, new).stdout.decode().split('\0') if p]
    dirty = dirty_of(root)
    show = lambda c, p: git(root, 'show', f'{c}:{p}', ok=(0, 128)).stdout
    here = lambda p: open(os.path.join(root, p), 'rb').read() if os.path.isfile(os.path.join(root, p)) else b''
    sectioned = {f'specs/{feature}/{f}': f for f in SECTIONED}
    sectioned[LEDGER[0]] = LEDGER[1]
    def merged(p, ours):
        # (the merged bytes, None), or (None, what conflicts): git's line merge; a sectioned file whose line merge conflicts merged
        # piece by piece, its conflict named by the piece (a JSON or ledger hunk is never taken whole); any other, its pure-addition
        # hunks taken (merge3)
        base, theirs = show(old, p), show(new, p)
        out = merge3(base, ours, theirs, p not in sectioned, p.endswith('.jsonl'))
        if out is not None:
            return out, None
        if p not in sectioned:
            return None, 'a hunk both changed otherwise'
        text, key = merge_pieces(sectioned[p], base.decode(), ours.decode(), theirs.decode())
        if text is None:
            return None, piece_name(key)
        return text.encode(), None
    # every merge first, so a conflict moves nothing, and every conflict named at once
    held, conflicts = {}, []
    for p in changed:
        if p in dirty:
            ours = here(p)
            out, why = merged(p, ours)
            held[p] = (ours, out)
            if why:
                conflicts.append(f'{p} - the landing\'s change and the clone\'s uncommitted edit conflict: {why}')
    if conflicts:
        sys.exit('land-alone: ' + '; '.join(conflicts))
    git(root, 'update-ref', '-m', f'land-alone: take {new[:10]}', 'HEAD', new, old)
    if changed:
        git(root, 'reset', '-q', '--', *changed)
    gone = [p for p in changed if p not in held and git(root, 'cat-file', '-e', f'{new}:{p}', ok=(0, 1, 128)).returncode]
    for p in gone:
        if os.path.lexists(os.path.join(root, p)):
            os.remove(os.path.join(root, p))
    put = [p for p in changed if p not in held and p not in gone]
    if put:
        git(root, 'checkout-index', '-f', '--', *put)
    for p, (ours, out) in held.items():
        if here(p) != ours:  # a builder wrote it since it was read: merged again from what it holds now
            out, why = merged(p, here(p))
            if why:
                sys.exit(f'land-alone: {p}, written while the clone took the tip, conflicts with the landing\'s change: {why} - the clone is at {new[:10]}, the file as it was')
        os.makedirs(os.path.dirname(os.path.join(root, p)) or root, exist_ok=True)
        t = os.path.join(root, p + '.land-alone')
        open(t, 'wb').write(out)
        os.replace(t, os.path.join(root, p))
    print(f'land-alone: {len(changed)} file(s) moved to {new[:10]}, {len(held)} of them merged with the clone\'s uncommitted edits')

mode, args = sys.argv[1], sys.argv[2:]
if mode == 'stage':
    stage(args[0], args[1], args[2].replace(',', ' ').split())
elif mode == 'split':
    split(args[0], args[1], args[2], args[3].replace(',', ' ').split())
else:
    take(*args)
PY
py() { python3 -I -c "$PYLIB" "$@"; }

# (1) one landing alone at a time
exec 9>"$COMMON/land-alone.lock"
flock -n 9 || die "another landing alone holds $COMMON/land-alone.lock - land this after it"

# (2) the landing tasks' own sections of plan.md, tasks.md and plan-review.json committed apart from the other open tasks'
staged=$(py stage "$ROOT" "$F" "$T") || die "the task's own sections could not be committed apart (above)"
[ -z "$staged" ] || say "committed $T's own sections apart from the other open tasks' ($(printf '%s\n' "$staged" | sed -n 's/^staged\t//p')) ($(lap) s)"

# (3) the landing tasks' own other files: those a line filed under one of them names (an edit's path, a Bash call's `writes`), newer than
# the file's last commit and than its task's last landing
split=$(py split "$ROOT" "${L7R_EVENTS_DIR:-$COMMON/l7r-events}" "$F" "$T") || die "the event log could not be read (above)"
own=$(printf '%s\n' "$split" | sed -n 's/^own\t//p')
[ -z "$own" ] || die "$T's own edits are uncommitted - commit them, then land again: git -C $ROOT commit -m \"<what>\" -- $(printf '%s ' $own)"
putback=$(printf '%s\n' "$split" | sed -n 's/^putback\t//p')
[ -z "$putback" ] || say "left uncommitted in the clone, not $T's own: its edits there were put back, leaving no change of its own (451 T202): $(printf '%s ' $putback | cut -c1-600)"
unnamed=$(printf '%s\n' "$split" | sed -n 's/^unnamed\t//p')
[ -z "$unnamed" ] || say "left uncommitted in the clone, not landed (no task's line names them: a write the walk cannot see - a make target's, a generator's - is named by none): $(printf '%s ' $unnamed | cut -c1-600)"
other=$(printf '%s\n' "$split" | sed -n 's/^other\t//p')
[ -z "$other" ] || say "left uncommitted in the clone, another task's, not landed (a line filed under a wrong task number shows here): $(printf '%s; ' "${other//$'\n'/; }" | cut -c1-600)"

# (4) the worktree at the clone's HEAD
head=$(git -C "$ROOT" rev-parse HEAD) || exit 2
if [ -e "$WT/.git" ]; then
  git -C "$WT" reset -q --hard && git -C "$WT" clean -fdq && git -C "$WT" checkout -q --detach "$head" \
    || die "the landing worktree $WT could not be moved to $head (above)"
else
  git -C "$ROOT" worktree add -q --detach "$WT" "$head" || die "the landing worktree $WT could not be added (above)"
fi
say "worktree $WT at ${head:0:10} ($(lap) s)"

# (5) the clone's kept results, where newer: a crate's or suite's result is keyed by its inputs' contents, so the clone's builders'
# closing checks on the task's own files serve the landing (measured 2026-11-21: every crate's lint, test, format and dead reused)
gd=$(git -C "$WT" rev-parse --absolute-git-dir) || exit 2
# NOT review-verdicts or approach-owed.json (451 T442): the review gate, the checkpoint, the discharges and the approach gate read them
# from the common git dir, which this worktree shares, so nothing read the copies (2026-11-22's three reviews refused as unrecorded
# were the gate reading the worktree's own dir)
# NOT hooks-test (451 T281): the suites' stamps are read from the common git dir, so nothing read the copy (since commit d7456c4c8d),
# and the tree's own hooks-test/messages is now its store of rendered guard messages - the copy would fill it with the clone's
for d in rust-checks; do
  [ -d "$COMMON/$d" ] && mkdir -p "$gd/$d" && cp -a -u "$COMMON/$d/." "$gd/$d/"
done
say "kept results seeded ($(lap) s)"

# (6) the landing, whole, in the worktree
( cd "$WT" && L7R_LAND_ALONE=1 SYNC_BACKUP=off $MAKE --no-print-directory land F="$F" T="$T" NOTE="${LAND_NOTE:-}" \
    BOXES="${LAND_BOXES:-}" COVER_OK="${COVER_OK:-}" )
rc=$?
say "the landing in the worktree exited $rc ($(lap) s)"
[ "$rc" = 0 ] || [ "$rc" = 3 ] || exit "$rc"

# (7) the clone takes the landed tip
tip=$(git -C "$WT" rev-parse HEAD) || exit 4
if py take "$ROOT" "$tip" "$F"; then
  say "the clone took ${tip:0:10}, its uncommitted work kept ($(lap) s)"
  exit "$rc"
fi
printf 'land-alone: landed %s; the clone could not take %s (above) - its uncommitted work is untouched: once it is committed, git -C %s merge %s\n' "$T" "${tip:0:10}" "$ROOT" "${tip:0:10}" >&2
exit 4
