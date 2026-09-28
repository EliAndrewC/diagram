"""Feature 282's review-finding measurements, read from the DRAWN artifacts (the SVG ink, the rendered page, the notes)."""
import re, json, math, sys
def segdist(p,a,b):
    (px,py),(ax,ay),(bx,by)=p,a,b
    dx,dy=bx-ax,by-ay; t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy)))
    return math.hypot(px-ax-t*dx,py-ay-t*dy)
res={}
for h in ['inashiro','kashikawa','mizuguchi','sawada']:
    svg=open(f'pool/hamlets/{h}/{h}.svg').read()
    shares=[]; margins=[]; racklines=0; rackboxes=0; yards=0
    for m in re.finditer(r'<g transform="translate\(([-\d.]+),([-\d.]+)\) rotate\(([-\d.]+)\)"><polygon points="([^"]+)" fill="#D2BE94"(.*?)</g>', svg):
        yards+=1
        poly=[tuple(map(float,p.split(','))) for p in m.group(4).split()]; body=m.group(5)
        mats=[tuple(map(float,r)) for r in re.findall(r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([-\d.]+)" height="([-\d.]+)" fill="#EBDDAE"',body)]
        area=0.5*abs(sum(poly[i][0]*poly[(i+1)%4][1]-poly[(i+1)%4][0]*poly[i][1] for i in range(4)))
        shares.append(len(mats)/(area/18))
        for x,y,w,hh in mats:
            for c in ((x,y),(x+w,y),(x+w,y+hh),(x,y+hh)):
                margins.append(min(segdist(c,poly[i],poly[(i+1)%4]) for i in range(4)))
        racklines+=len(re.findall(r'stroke="#D9B64A"',body)); rackboxes+=len(re.findall(r'<rect(?![^>]*#EBDDAE)',body))
    html=open(f'pool/hamlets/{h}/{h}.html').read()
    res[h]=dict(yards=yards, share_min=round(min(shares),2), share_max=round(max(shares),2), min_margin_ft=round(min(margins),2),
      rack_lines=racklines, rack_boxes=rackboxes, modal_third=html.count('between a third and two thirds of the straw mats'),
      modal_about_half=html.count('about half of the straw mats'), modal_rack_conditional=html.count('where a map draws racks by the houses'))
res['sawada_notes_282']=sum(1 for l in open('pool/hamlets/sawada/sawada.notes.md') if 'feature 282' in l)
print(json.dumps(res))
