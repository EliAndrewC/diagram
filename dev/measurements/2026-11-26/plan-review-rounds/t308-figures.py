# Candidate figure rules replayed over every digest-exact reviewed section: which unlabeled sentences would each newly refuse?
import json,re,collections,hashlib,os
S=os.path.dirname(os.path.abspath(__file__))
rows=[x for x in json.load(open(S+'/t308-rounds.json')) if x['first']<'2026-11-26T19:42' and x['sec'] and hashlib.sha256(x['sec'].encode()).hexdigest()==x['sha']]
NOUNS=r"(?:captions?|lines?|cases?|files?|pages?|calls?|callers?|crates?|suites?|tests?|rows?|keys?|entries|entry|findings?|differences?|mismatches?|runs?|sites?|commits?|bytes?|KB|KiB|tokens?|questions?|sources?|modules?|functions?|mutations?|outputs?|hits?|fragments?|footnotes?|URLs?|domains?|processes|process|invocations?)"
C={'F1 k/M-suffixed count':re.compile(r"(?<![\w.-])\d[\d,]*(?:\.\d+)?[kKM]\s*"+NOUNS+r"(?![\w-])"),
   'F2 N-odd unit':re.compile(r"(?<![\w.-])\d[\d,]*-odd\s+(?:seconds?|minutes?|hours?|s|ms|min|days?|GB|MB|KB|%)\b"),
   'F3 N of M':re.compile(r"(?<![\w.-])\d[\d,]* of (?:the |its |those |these )?\d[\d,]*(?![\w.-]|\s*%)")}
LABEL=re.compile(r"(?i)\bobserved \d{4}-\d\d-\d\d\b|\bm:[\w.-]+|\b(?:GUESS|CONVENTION|DEVIATION|UNRESEARCHED|ACCURATE|ATTESTED|SILENT)\b|research/questions/|\bknob\b|\bR\d+\b")
def labeled(s): return bool(LABEL.search(s)) or (re.search(r'(?i)\bmeasured\b',s) and re.search(r'\b20\d\d-\d\d-\d\d\b',s) and '(' in s)
NOTFIG=re.compile(r"\b\d{4}-\d\d-\d\d(?:T\d\d:\d\d(?::\d\d)?Z?)?\b|\b\d\d:\d\d(?::\d\d)?Z?\b|\b(?:FR|SC)-\d+[a-z]?\b|\b[TDA]\d+[a-z]?\b")
SPLIT=re.compile(r"(?<=\.)\s+|\n\s*\n|\n(?=\s*(?:[-*] |\d+\. |#|\|))")
hits=collections.defaultdict(list)
for x in rows:
    text=re.sub(r"(?ms)^```.*?^```"," ",x['sec'])
    for sent in SPLIT.split(text):
        bare=NOTFIG.sub(' ',re.sub(r"`[^`\n]*`"," ",sent))
        for name,p in C.items():
            m=p.search(bare)
            if m and not labeled(sent): hits[name].append((x['task'],x['first'][5:16],x['verdict'],m.group(0),sent.strip()[:150]))
for name,h in hits.items():
    secs={(a,b) for a,b,*_ in h}
    print(f'## {name}: {len(h)} sentences in {len(secs)} of {len(rows)} reviewed sections')
    seen=set()
    for a,b,v,m,s in h:
        if (a,m) in seen: continue
        seen.add((a,m)); print('  ',a,b,v,'|',m,'|',s[:110])
