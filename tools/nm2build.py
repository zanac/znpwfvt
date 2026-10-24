import znp, nm2, statistics
def build_lib(n):
    lib={}; gaps=[]; spaces=[]; centers=[]
    for k,t in nm2.NAMES.items():
        g,_=nm2.glyphs_core(n.block(k),t)
        seq=[]; idx={}
        for ch in t.replace(' ',''):
            i=idx.get(ch,0); seq.append((ch,g[ch][i])); idx[ch]=i+1
        for ch,gl in seq: lib.setdefault(ch,gl)
        # gaps
        words=t.split(' '); p=0
        for wi,w in enumerate(words):
            for ci in range(len(w)):
                if ci+1<len(w): gaps.append(seq[p+1][1][0]-seq[p][1][1])
                elif wi+1<len(words): spaces.append(seq[p+1][1][0]-seq[p][1][1])
                p+=1
        centers.append((seq[0][1][0]+seq[-1][1][1])/2)
    return lib, int(round(statistics.median(gaps))), int(round(statistics.median(spaces))), statistics.median(centers)
def make_P(lib, d=2, S=13):
    """P from B: the upper bowl, below the middle bar only the stem (right edge outlined)"""
    x0,x1,g=lib['B']
    ys=sorted(set(y for y,x in g)); ymid=(ys[0]+ys[-1])//2
    out={}
    for (y,x),v in g.items():
        if y<=ymid+d: out[(y,x)]=v
    for y in ys:
        if y<=ymid+d: continue
        row=sorted(xx for (yy,xx) in g if yy==y); left=row[0]
        for x in range(left,left+S):
            if (y,x) in g: out[(y,x)]=g[(y,x)]
        edge=[(left+S-3,8),(left+S-2,8),(left+S-1,2)]
        for x,v in edge:
            if (y,x) in g and g[(y,x)]: out[(y,x)]=v
    return (x0,x1,out)
def render(lib, text, gap, space, center):
    cur=0; placed=[]
    for i,ch in enumerate(text):
        if ch==' ': cur+=space-gap; continue
        x0,x1,g=lib[ch]; placed.append((cur,g)); cur+= (x1-x0)+gap
    width=cur-gap; off=int(round(center-width/2))
    px=[[0]*512 for _ in range(48)]
    for cx,g in placed:
        for (y,x),v in g.items():
            X=off+cx+x
            if 0<=X<512 and v: px[y][X]=v
    return px
