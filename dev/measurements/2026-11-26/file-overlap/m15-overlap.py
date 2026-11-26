#!/usr/bin/env python3
"""m15: how often side-by-side tasks edit the same files, by class. Read-only over git history.

Pinned at PIN on origin/main; commits since 2026-11-19, merges left out. A UNIT is one surviving
"<feature>: T.. ticked (make land)" commit (a tick later reverted is dropped, a re-tick counted once,
a multi-task tick is one unit). Its delta is every commit whose subject head names the feature and one
of its tasks (filings and withdrawals left out), plus the unnamed bookkeeping run just before the tick.
"""
import collections, itertools, json, random, re, subprocess, sys

REPO = '/diagram/.clones/diagram-backlog'
PIN = '248d6f919f'
SINCE = '2026-11-19'
DAY = 86400


def git(*a):
    return subprocess.run(['git', '-C', REPO, *a], capture_output=True, text=True, check=True).stdout


# ---------- commits
commits = []  # oldest first: dict(sha, ct, subj, files)
for block in git('log', PIN, '--no-merges', '--since=' + SINCE, '--format=@@%H%x09%ct%x09%s', '--name-only').split('@@')[1:]:
    lines = block.split('\n')
    sha, ct, subj = lines[0].split('\t', 2)
    commits.append(dict(sha=sha, ct=int(ct), at=int(git('show', '-s', '--format=%at', sha)), subj=subj, files=[f for f in lines[1:] if f]))
commits.reverse()
idx = {c['sha']: i for i, c in enumerate(commits)}


def tasks_in(text):
    out = set()
    for a, b in re.findall(r'T(\d+)(?:-T(\d+))?', text):
        if b and int(b) - int(a) < 60:
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(a))
            if b:
                out.add(int(b))
    return out


TICK = re.compile(r'^(\d{3})-[a-z0-9-]+: (T[\dT ]+) ticked \(make land')
BOOK_SUBJ = re.compile(r"^(the gate's run record|the review passes' ledger rows|the landing'?s?'? escape record|"
                       r"the plan reviews' ledger rows|the review ledger's rows|the push's escape record)")
# reverted ticks: 'Revert "<subject>"' cancels the nearest earlier tick with that subject
dead = set()
for i, c in enumerate(commits):
    m = re.match(r'^Revert "(.*)"$', c['subj'])
    if m:
        for j in range(i - 1, -1, -1):
            if commits[j]['subj'] == m.group(1) and j not in dead:
                dead.add(j)
                break
units = []
seen = {}
for i, c in enumerate(commits):
    m = TICK.match(c['subj'])
    if not m or i in dead:
        continue
    feat, ts = m.group(1), frozenset(tasks_in(m.group(2)))
    if feat not in ('449', '451'):
        continue
    key = (feat, ts)
    if key in seen:  # re-tick: keep the later landing time
        seen[key]['tick'] = i
        seen[key]['ct'] = c['ct']
        continue
    u = dict(feat=feat, tasks=ts, tick=i, ct=c['ct'], commits=set(), named=0)
    seen[key] = u
    units.append(u)

owner = {}
for u in units:
    for t in u['tasks']:
        owner[(u['feat'], t)] = u
HEAD = re.compile(r'^(\d{3})(?:-[a-z0-9-]+)? (T\d[^:]{0,120}?)(?::|$)')
unowned_named = 0
for i, c in enumerate(commits):
    m = HEAD.match(c['subj'])
    if not m or TICK.match(c['subj']):
        continue
    head = m.group(2)
    if re.search(r'\b(filed|withdrawn)\b', head):
        continue
    hit = {id(owner[(m.group(1), t)]): owner[(m.group(1), t)] for t in tasks_in(head) if (m.group(1), t) in owner}
    if not hit:
        unowned_named += 1
    for u in hit.values():
        u['commits'].add(i)
        u['named'] += 1
for u in units:  # the tick, and the unnamed bookkeeping run before it
    u['commits'].add(u['tick'])
    j = u['tick'] - 1
    while j >= 0 and BOOK_SUBJ.match(commits[j]['subj']):
        u['commits'].add(j)
        j -= 1

# ---------- classes
BOOK = re.compile(r'^(specs/[^/]+/(tasks|tasks-done|plan|plan-done)\.md|specs/[^/]+/(plan-review\.json|arbiter\.jsonl|found\.jsonl)|'
                  r'dev/review-ledger\.md|dev/(bypass-log|run-log|session-records)/|dev/deferred-reviews\.jsonl)')
REG = re.compile(r'^(Makefile|docs/guards\.md|docs/make-targets\.html|dev/guard-messages\.tsv|(.*/)?CLAUDE\.md|'
                 r'rust/gate/src/(lib|main)\.rs|rust/guard/src/(lib|guards|main)\.rs|scripts/container/builder-brief\.md|'
                 r'docs/process-decisions\.md|dev/audits/|dev/claims-(index|pages)\.json|rust/.*Cargo\.(toml|lock))')


def klass(f):
    if BOOK.match(f):
        return 'BOOK'
    if REG.match(f):
        return 'REG'
    if f.startswith('rust/') and f.endswith('.rs'):
        return 'RUST'
    if f.startswith('tests/'):
        return 'TESTS'
    if f.startswith('research/'):
        return 'RESEARCH'
    return 'OTHER'


def crate(f):
    m = re.match(r'^(rust/gate/crates/[^/]+|rust/guard/(?:shared|src)|rust/[^/]+)/', f)
    return m.group(1) if m else None


for u in units:
    fs = set()
    for i in u['commits']:
        fs.update(commits[i]['files'])
    u['files'] = fs
    u['by'] = collections.defaultdict(set)
    for f in fs:
        u['by'][klass(f)].add(f)
    u['crates'] = {crate(f) for f in u['by']['RUST']}
    u['name'] = u['feat'] + ' ' + ' '.join('T%d' % t for t in sorted(u['tasks']))

out = []
P = out.append
N = len(units)
no_named = [u['name'] for u in units if u['named'] == 0]
P('# m15 - task overlap by file class (pinned %s, since %s, features 449 and 451)' % (PIN, SINCE))
P('')
P('Units (surviving ticks): %d (%d of 451, %d of 449); %d multi-task ticks; %d ticks dropped as reverted.' % (
    N, sum(u['feat'] == '451' for u in units), sum(u['feat'] == '449' for u in units),
    sum(len(u['tasks']) > 1 for u in units), len(dead)))
P('Method error: %d units have NO commit named for them (delta = bookkeeping only, their code went in under another subject); '
  '%d task-named commits name no landed unit.' % (len(no_named), unowned_named))
P('Units with no named commit: ' + ', '.join(no_named))
P('')
P('## 1. Class table (units touching each class)')
P('| class | units | % | files touched (distinct) |')
P('|---|---|---|---|')
for k in ('BOOK', 'REG', 'RUST', 'TESTS', 'RESEARCH', 'OTHER'):
    n = sum(1 for u in units if u['by'][k])
    P('| %s | %d | %.0f%% | %d |' % (k, n, 100 * n / N, len(set().union(*[u['by'][k] for u in units]))))
P('| only BOOK (no other class) | %d | %.0f%% | |' % (sum(1 for u in units if not (u['files'] - u['by']['BOOK'])),
                                                    100 * sum(1 for u in units if not (u['files'] - u['by']['BOOK'])) / N))
P('')
P('Top 15 non-bookkeeping files (units touching):')
cnt = collections.Counter(f for u in units for f in u['files'] if klass(f) != 'BOOK')
for f, n in cnt.most_common(15):
    P('- %d  %s  [%s]' % (n, f, klass(f)))
P('')
P('Top 10 Rust crates (units touching):')
cc = collections.Counter(c for u in units for c in u['crates'])
for c, n in cc.most_common(10):
    P('- %d  %s' % (n, c))
P('Top 10 Rust source files:')
rc = collections.Counter(f for u in units for f in u['by']['RUST'])
for f, n in rc.most_common(10):
    P('- %d  %s' % (n, f))

# ---------- 2. pairs
def tier(a, b):
    sh = a['files'] & b['files']
    ks = {klass(f) for f in sh}
    if 'RUST' in ks:
        return 'rust-same-file'
    if a['crates'] & b['crates']:
        return 'rust-same-crate-other-file'
    if 'REG' in ks:
        return 'registry'
    if ks - {'BOOK'}:
        return 'other-shared(tests/research/other)'
    if ks:
        return 'bookkeeping-only'
    return 'none'


GEN = {'docs/make-targets.html', 'dev/claims-index.json', 'dev/claims-pages.json'}
TIERS = ['rust-same-file', 'rust-same-crate-other-file', 'registry', 'other-shared(tests/research/other)', 'bookkeeping-only', 'none']
pairs = [(a, b) for a, b in itertools.combinations(units, 2) if abs(a['ct'] - b['ct']) <= DAY]


def pair_table(title, ps):
    P('')
    P('### ' + title + ' (%d pairs)' % len(ps))
    if not ps:
        return
    t = collections.Counter(tier(a, b) for a, b in ps)
    P('| exclusive tier (highest that applies) | pairs | % |')
    P('|---|---|---|')
    for k in TIERS:
        P('| %s | %d | %.1f%% |' % (k, t[k], 100 * t[k] / len(ps)))
    ne = collections.Counter()
    for a, b in ps:
        for k in {klass(f) for f in a['files'] & b['files']}:
            ne[k] += 1
        if a['crates'] & b['crates']:
            ne['same crate (any file)'] += 1
        if any(klass(f) == 'REG' and f not in GEN for f in a['files'] & b['files']):
            ne['REG hand-edited (generated left out)'] += 1
        if 'Makefile' in a['files'] & b['files']:
            ne['Makefile'] += 1
    P('Non-exclusive (pairs sharing >=1 file of the class): ' + '; '.join('%s %d (%.1f%%)' % (k, v, 100 * v / len(ps)) for k, v in sorted(ne.items())))


P('')
P('## 2. Pairwise overlap')
pair_table('All pairs landed within 24 h of each other', pairs)
pair_table('...of which both units have a non-bookkeeping file (real work on both sides)',
           [(a, b) for a, b in pairs if a['files'] - a['by']['BOOK'] and b['files'] - b['by']['BOOK']])
pair_table('Pairs landed within 2 h of each other', [(a, b) for a, b in pairs if abs(a['ct'] - b['ct']) <= 7200])
pair_table('Pairs of SINGLE-task units within 24 h (a batch tick of several tasks inflates every overlap)',
           [(a, b) for a, b in pairs if len(a['tasks']) == 1 and len(b['tasks']) == 1])

# actually concurrent: start marks in different trees, intervals [last start before landing, landing] overlapping
starts = collections.defaultdict(list)
try:
    import datetime
    for l in open(REPO + '/.git/task-starts.jsonl'):
        try:
            d = json.loads(l)
        except ValueError:
            continue
        ts = datetime.datetime.strptime(d['utc'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc).timestamp()
        starts[(d['feature'][:3], int(d['task'][1:]) if d['task'][1:].isdigit() else -1)].append((ts, d.get('tree', '')))
except OSError:
    pass
for u in units:
    named = [commits[i]['at'] for i in u['commits'] if HEAD.match(commits[i]['subj']) and not TICK.match(commits[i]['subj'])]
    first = min(named) if named else u['ct']
    ss = [s for t in u['tasks'] for s in starts.get((u['feat'], t), []) if s[0] <= first]
    u['start'] = max(ss) if ss else None
    u['carried'] = any(commits[i]['ct'] - commits[i]['at'] > 60 for i in u['commits'])
conc = []
for a, b in pairs:
    if a['start'] and b['start'] and a['start'][0] < b['ct'] and b['start'][0] < a['ct']:
        conc.append((a, b))
P('')
P('Units with a start mark before landing: %d of %d; distinct trees among them: %s' % (
    sum(1 for u in units if u['start']), N, dict(collections.Counter(u['start'][1].rsplit('/', 1)[-1] for u in units if u['start']))))
P('Units with a commit carried over from a worktree (author time != commit time): %d' % sum(u['carried'] for u in units))
pair_table('Pairs IN FLIGHT TOGETHER (each: last start mark before its first named commit, to its landing; the intervals overlap). '
           'An upper bound on side-by-side work: a started task may sit idle', conc)
pair_table('...of which landed in different ticks AND at least one was carried over from a worktree', [(a, b) for a, b in conc if a['carried'] or b['carried']])
for a, b in [(a, b) for a, b in conc if a['carried'] and b['carried']]:
    sh = sorted(f for f in a['files'] & b['files'] if klass(f) != 'BOOK')
    P('- both carried: %s || %s: %s; shared non-bookkeeping: %s' % (a['name'], b['name'], tier(a, b), ', '.join(sh)[:200] or 'none'))

# ---------- registry census: consecutive touches of one registry file by different units within 24 h
def hunks(sha, f):
    hs = []
    for m in re.finditer(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', git('show', '-U0', '--format=', sha, '--', f), re.M):
        o, ol, n, nl = int(m.group(1)), int(m.group(2) or 1), int(m.group(3)), int(m.group(4) or 1)
        hs.append((o, ol, n, nl))
    return hs


c2u = collections.defaultdict(list)
for u in units:
    for i in u['commits']:
        c2u[i].append(u)
touch = collections.defaultdict(list)
for i, c in enumerate(commits):
    for f in c['files']:
        if klass(f) == 'REG':
            touch[f].append(i)
census = []
for f, ti in touch.items():
    for i, j in zip(ti, ti[1:]):
        if len(c2u[i]) != 1 or len(c2u[j]) != 1 or c2u[i][0] is c2u[j][0]:
            continue
        a, b = c2u[i][0], c2u[j][0]
        if abs(a['ct'] - b['ct']) > DAY:
            continue
        ha, hb = hunks(commits[i]['sha'], f), hunks(commits[j]['sha'], f)
        if not ha or not hb:
            continue
        # A's new-side ranges and B's old-side ranges are both in the file as A left it (no commit between touches f)
        ra = [(n, n + max(nl, 1) - 1) for (_, _, n, nl) in ha]
        rb = [(o, o + max(ol, 1) - 1) for (o, ol, _, _) in hb]
        gap = min(max(x0 - y1, y0 - x1, 0) for x0, x1 in ra for y0, y1 in rb)
        size = int(git('cat-file', '-s', commits[i]['sha'] + ':' + f) or 0)
        nlines = git('show', commits[i]['sha'] + ':' + f).count('\n')
        eof = max(x1 for _, x1 in ra) >= nlines and max(y1 for _, y1 in rb) >= nlines
        rewrite = any(ol > 0 and nl > 0 and o <= n + nl - 1 and n <= o + ol - 1 for (o, ol, _, _) in hb for (_, _, n, nl) in ha)
        census.append(dict(f=f, a=a['name'], b=b['name'], gap=gap, eof=eof, ha=len(ha), hb=len(hb), rewrite=rewrite,
                           region='SAME' if gap <= 1 else ('NEAR(<=3)' if gap <= 3 else 'DISTINCT')))
P('')
P('## 2b. Registry edits: consecutive touches of one registry file by two different units landed within 24 h')
P('(no other commit touched the file between; SAME = hunks overlap or abut, git would conflict; NEAR = within 3 lines, '
  'merges but inside each other\'s context; DISTINCT = clean merge)')
P('| file | consecutive pairs | SAME | NEAR | DISTINCT | SAME at end of file |')
P('|---|---|---|---|---|---|')
byf = collections.defaultdict(list)
for r in census:
    byf[re.sub(r'^dev/audits/.*', 'dev/audits/*', r['f'])].append(r)
tot = collections.Counter()
for f, rs in sorted(byf.items(), key=lambda kv: -len(kv[1])):
    c = collections.Counter(r['region'] for r in rs)
    e = sum(1 for r in rs if r['eof'] and r['region'] == 'SAME')
    tot.update(c)
    tot['eof'] += e
    tot['n'] += len(rs)
    if len(rs) >= 3:
        P('| %s | %d | %d | %d | %d | %d |' % (f, len(rs), c['SAME'], c['NEAR(<=3)'], c['DISTINCT'], e))
P('| ALL registry files | %d | %d | %d | %d | %d |' % (tot['n'], tot['SAME'], tot['NEAR(<=3)'], tot['DISTINCT'], tot['eof']))
hand = [r for r in census if r['f'] not in ('docs/make-targets.html', 'dev/claims-index.json', 'dev/claims-pages.json')]
c = collections.Counter(r['region'] for r in hand)
P('Hand-edited only (generated make-targets.html, claims-index.json, claims-pages.json left out): %d pairs - SAME %d, NEAR %d, DISTINCT %d' % (
    len(hand), c['SAME'], c['NEAR(<=3)'], c['DISTINCT']))
same = [r for r in hand if r['region'] == 'SAME']
P('Of the %d SAME: %d the later unit REWROTE lines the earlier one had just written (a real clash); %d only inserted beside them (adjacent rows, mechanical).' % (
    len(same), sum(r['rewrite'] for r in same), sum(not r['rewrite'] for r in same)))
random.seed(15)
P('')
P('Sample of 15 (seed 15, hand-edited files, at most 3 a file):')
random.shuffle(hand)
per = collections.Counter()
shown = 0
for r in hand:
    if per[r['f']] >= 3 or shown >= 15:
        continue
    per[r['f']] += 1
    shown += 1
    P('- %s: %s then %s - %s (nearest hunks %d lines apart; %d and %d hunks)%s' % (
        r['f'], r['a'], r['b'], r['region'], r['gap'], r['ha'], r['hb'], (' [rewrote the same lines]' if r['rewrite'] else '') + (' [both at end of file]' if r['eof'] else '')))

# ---------- 4. mod lines
P('')
P('## 4. Same crate, different file: shared module-list lines')
MOD = re.compile(r'^\+\s*(?:pub(?:\([a-z]+\))? )?mod \w+;')
modadds = collections.defaultdict(lambda: collections.defaultdict(list))  # file -> unit name -> lines
cur = None
log = git('log', PIN, '--no-merges', '--since=' + SINCE, '-p', '-U0', '--format=@@%H', '--', 'rust')
f = None
for l in log.split('\n'):
    if l.startswith('@@') and len(l) == 42:
        cur = idx.get(l[2:])
    elif l.startswith('+++ b/'):
        f = l[6:]
    elif MOD.match(l) and cur is not None and len(c2u[cur]) >= 1:
        for u in c2u[cur]:
            modadds[f][id(u)].append(l[1:].strip())
byid = {id(u): u for u in units}
modpairs = []
for f, d in modadds.items():
    for x, y in itertools.combinations(d, 2):
        a, b = byid[x], byid[y]
        if abs(a['ct'] - b['ct']) <= DAY:
            modpairs.append((f, a['name'], b['name']))
P('Units that added a `mod` line: %d; files receiving mod lines from >=2 units: %d' % (
    len({x for d in modadds.values() for x in d}), sum(1 for d in modadds.values() if len(d) >= 2)))
P('Same-24h pairs both adding a `mod` line to the SAME file: %d (of %d pairs in the window)' % (len(modpairs), len(pairs)))
for f, n in collections.Counter(p[0] for p in modpairs).most_common(8):
    P('- %d  %s' % (n, f))
sc = [(a, b) for a, b in pairs if tier(a, b) == 'rust-same-crate-other-file']
sc_reg = sum(1 for a, b in sc if any(klass(x) == 'REG' and x != 'docs/make-targets.html' for x in a['files'] & b['files']))
sc_tests = sum(1 for a, b in sc if any(klass(x) == 'TESTS' for x in a['files'] & b['files']))
P('Of the %d same-crate-different-file pairs: %d also share a hand-edited registry file, %d share a tests/ file.' % (len(sc), sc_reg, sc_tests))

json.dump([dict(name=u['name'], ct=u['ct'], files=sorted(u['files'])) for u in units],
          open(sys.argv[1] if len(sys.argv) > 1 else '/dev/null', 'w'))
print('\n'.join(out))
