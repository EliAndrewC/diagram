import math
def _o(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def segs_cross(p1,p2,p3,p4):
    d1,d2,d3,d4=_o(p3,p4,p1),_o(p3,p4,p2),_o(p1,p2,p3),_o(p1,p2,p4)
    if ((d1>0)!=(d2>0)) and ((d3>0)!=(d4>0)): return True
    def on(a,b,c): return abs(_o(a,b,c))<1e-12 and min(a[0],b[0])-1e-9<=c[0]<=max(a[0],b[0])+1e-9 and min(a[1],b[1])-1e-9<=c[1]<=max(a[1],b[1])+1e-9
    return on(p3,p4,p1) or on(p3,p4,p2) or on(p1,p2,p3) or on(p1,p2,p4)
def pt_seg(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; L=dx*dx+dy*dy
    t=0.0 if L==0 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/L))
    return math.hypot(p[0]-(a[0]+t*dx), p[1]-(a[1]+t*dy))
def seg_seg(a,b,c,d):
    if segs_cross(a,b,c,d): return 0.0
    return min(pt_seg(a,c,d),pt_seg(b,c,d),pt_seg(c,a,b),pt_seg(d,a,b))
def in_poly(p,poly):
    x,y=p; n=len(poly); inside=False; j=n-1
    for i in range(n):
        xi,yi=poly[i]; xj,yj=poly[j]
        if ((yi>y)!=(yj>y)) and x < (xj-xi)*(y-yi)/((yj-yi) or 1e-18)+xi: inside=not inside
        j=i
    return inside
def poly_seg(poly, a, b, closed=True):
    """True min distance from a polyline/polygon to segment ab; 0 on any intersection or containment."""
    n=len(poly); rng=range(n) if closed else range(n-1)
    best=min(seg_seg(poly[i],poly[(i+1)%n],a,b) for i in rng)
    if closed and best>0 and (in_poly(a,poly) or in_poly(b,poly)): return 0.0
    return best
def rect(cx,cy,w,h,rot):
    th=math.radians(rot); cs,sn=math.cos(th),math.sin(th)
    return [(cx+x*cs-y*sn, cy+x*sn+y*cs) for x,y in ((-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2))]


def selftest() -> None:
    """The three cases the record claims for this file. A distance that cannot return 0 on an
    intersection is what produced the wrong clearances in rounds 2 and 3 of this feature's review;
    these asserts are what stop that measure being written a fourth time."""
    r = rect(0, 0, 8, 6, 0)
    assert poly_seg(r, (-10, 0), (10, 0)) == 0.0, "a stub driven THROUGH the footprint must be 0"
    assert poly_seg(r, (-1, 0), (1, 0)) == 0.0, "a stub wholly INSIDE the footprint must be 0"
    assert abs(poly_seg(r, (-10, 10), (10, 10)) - 7.0) < 1e-9, "a clear gap must be the gap"
    # an OPEN polyline must not be closed behind our back: the same segment is 0 against the ring
    chain = [(-5.0, -5.0), (5.0, -5.0), (5.0, 5.0), (-5.0, 5.0)]
    assert poly_seg(chain, (-1, 0), (1, 0), closed=False) == 4.0, "an open chain does not enclose"
    assert poly_seg(chain, (-1, 0), (1, 0), closed=True) == 0.0, "...but the closed ring does"
    print("measure_geom selftest ok")


if __name__ == "__main__":
    selftest()
