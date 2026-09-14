import re,json,pathlib,urllib.parse
S=open("research/SOURCES.html").read()
def regurl(key):
    m=re.search(rf'<h3 id="{re.escape(key)}"><code>{re.escape(key)}</code></h3>\n<p>(.*?)</p>',S,re.S)
    if not m: return None
    b=re.sub(r"<!--.*?-->","",m.group(1)); u=re.search(r'href="(https?://[^"]+)"',b) or re.search(r"\((https?://\S+)\)",b)
    return u.group(1) if u else ""
_all=re.findall(r'<h3 id="([a-z0-9-]+)"><code>\1</code></h3>',S)
def key_for_url(url):
    c={url,urllib.parse.unquote(url)}
    for k in _all:
        u=regurl(k)
        if u and (u in c or urllib.parse.unquote(u) in c): return k
    return None
J=lambda lang,en,orig: {"language":lang,"translation":en,"original":orig}
JA=lambda en,ja: J("Japanese",en,ja); ZH=lambda en,zh: J("Chinese",en,zh)
def reg(cit,what,why,used): return {"citation":cit,"what":what,"why":why,"used":used}
W=lambda name,url: f'{name} ({url})'
class Page:
    def __init__(self,page,NEW):
        self.page=page; self.P=pathlib.Path(f"research/{page}"); self.s=self.P.read_text(); self.miss=[]; self.N=[]
        self.NEW=NEW; self.KEY={}
        for k,u in NEW.items():
            ex=key_for_url(u); self.KEY[k]=ex or k
            if ex: print("existing key for",u,"->",ex)
    def rx(self,old,new,label):
        s2,n=re.subn(old,new,self.s,count=1,flags=re.S)
        if n: self.s=s2; print("ok",label)
        else: self.miss.append(label)
    def save(self): self.P.write_text(self.s); print("MISSES:",self.miss)
    def url(self,key): return self.NEW.get(key) or regurl(key) or ""
    def C(self,line,frag,key,quote=None,gloss=None,extra=None,registry=None,fn=None,**kw):
        key=self.KEY.get(key,key); d={"line":line,"sentence":frag,"form":"citation","key":key,"url":self.url(key)}
        if quote: d["quote"]=quote
        d.update(kw)
        if gloss: d["gloss"]=gloss
        if extra:
            for x in extra:
                x["key"]=self.KEY.get(x["key"],x["key"]); x["url"]=self.url(x["key"])
                if "registry" in x and f'<h3 id="{x["key"]}">' in S: del x["registry"]
            d["extra"]=extra
        if registry and f'<h3 id="{key}">' not in S: d["registry"]=registry
        if fn: d["fn"]=fn
        self.N.append(d)
    def A(self,line,frag,searched,fn=None):
        d={"line":line,"sentence":frag,"form":"absence","searched":searched}
        if fn: d["fn"]=fn
        self.N.append(d)
    def dump(self,name):
        json.dump(self.N,open(name,"w"),ensure_ascii=False,indent=1); print(len(self.N),"notes ->",name)

def wpat(text):
    """A tag-tolerant, wrap-tolerant regex for a visible-text span: tags may sit between any two characters, a space may be any run of whitespace or tags."""
    out=[]
    for ch in text:
        T=r"(?:<sup class=\"fn\">.*?</sup>|<[^>]+>)*"
        out.append(r"(?:\s|<sup class=\"fn\">.*?</sup>|<[^>]+>)+" if ch==" " else T+re.escape(ch))
    return "".join(out)
def wsub(self,old,new,label):
    # a footnote mark inside the matched span is kept: it is moved to the end of the replacement
    m=re.search(wpat(old),self.s,flags=re.S)
    if not m: self.miss.append(label); return
    sups="".join(re.findall(r'<sup class="fn">.*?</sup>',m.group(0),flags=re.S))
    self.s=self.s[:m.start()]+new+sups+self.s[m.end():]; print("ok",label,("(+%d marks kept)"%len(re.findall("<sup",sups)) if sups else ""))
Page.wsub=wsub
