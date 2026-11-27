# the saving estimate of results.md section 4, from runs.tsv: python3 estimate.py > estimate.txt
import csv,statistics as st
RLO,RHI,FLOOR,ROOT=0.46,0.15,0.25,6/9   # carry's worst loaded wall ratio; the sampled module mean; a binary's start; 3 of 9 diffs touch a root file
rows=list(csv.DictReader(open("runs.tsv"),delimiter="\t"))
rr=[r for r in rows if float(r["wall_s"])<=300]
def save(w,r): return max(0.0,w-max(FLOOR,r*w))
print("window 2026-11-26T17:19Z to 2026-11-27T04:54Z = 11.6 h")
for mk in ("rust-test","builder-checks","both"):
    sel=[float(r["wall_s"]) for r in rr if mk=="both" or r["make"]==mk]
    lo=sum(save(w,RLO) for w in sel)*ROOT; hi=sum(save(w,RHI) for w in sel)
    print(f"{mk}: runs {len(sel)}, test wall {sum(sel):.0f} s; saving LOW {lo:.0f} s = {lo/60:.1f} min, HIGH {hi:.0f} s = {hi/60:.1f} min in the window")
for a,b in [(0,22),(22,999)]:
    sel=[float(r["wall_s"]) for r in rr if r["make"]=="rust-test" and r["load1_max"]!="None" and a<=float(r["load1_max"])<b]
    print(f"rust-test at load1 {a}-{b}: runs {len(sel)}, wall {sum(sel):.0f} s, saving LOW {sum(save(w,RLO) for w in sel)*ROOT/60:.1f} min HIGH {sum(save(w,RHI) for w in sel)/60:.1f} min")
w=[float(r["wall_s"]) for r in rr if r["make"]=="rust-test"]
print("rust-test per-run saving, median: LOW",round(st.median([save(x,RLO)*ROOT for x in w]),2),"s HIGH",round(st.median([save(x,RHI) for x in w]),2),"s")
