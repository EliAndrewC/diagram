import re,pathlib,sys
def addfold(fn, tid, path, note):
    p=pathlib.Path(fn); t=p.read_text()
    m=re.search(rf"^## {tid} .*?\n(.*?)(?=^## |\Z)", t, re.S|re.M)
    blk=m.group(0)
    nb=re.sub(r"^(- fold: .*)$", lambda x: x.group(1)+", "+path, blk, count=1, flags=re.M)
    if re.search(r"^- note:", blk, re.M):
        nb=re.sub(r"^(- note: .*)$", lambda x: x.group(1)+" "+note, nb, count=1, flags=re.M)
    else:
        nb=nb.replace("- size:", f"- note: {note}\n- size:",1)
    p.write_text(t.replace(blk,nb)); print(fn, tid, "ok")
if __name__=="__main__": addfold(*sys.argv[1:5])
