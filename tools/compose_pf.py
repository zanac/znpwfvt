import glyphs, pf, statistics
from PIL import Image
reg,d=glyphs.load_pfs()
lib,sp=glyphs.build_lib(d)
GAP={'title':1,'name':1,'move':1}
SPACE={b:int(statistics.median(sp[b]))-GAP[b] for b in sp}
INV=lambda v: 13-v if 1<=v<=12 else v
def glyph(band, ch):
    if ch in lib[band]: return lib[band][ch][0][3]
    if band=='title' and ch in lib['move']:
        g=lib['move'][ch][0][3]
        # move band 18 rows (340-358) -> title 17 rows (256-273): align baseline, invert colours
        return [[INV(v) for v in row] for row in g[0:17]]
    if band=='name' and ch in lib['move']:
        return scaled('move',ch,'name','H')
    raise KeyError((band,ch))
def ink_rows(g, band):
    ink=(lambda v: 1<=v<=6) if band!='title' else (lambda v: 7<=v<=12)
    ys=[y for y,row in enumerate(g) if any(ink(v) for v in row)]
    return ys[0], ys[-1]+1
def scaled(src_band, ch, dst_band, ref):
    from PIL import Image
    g=lib[src_band][ch][0][3]; r=lib[dst_band][ref][0][3]
    a0,a1=ink_rows(g,src_band); b0,b1=ink_rows(r,dst_band)
    k=(b1-b0)/(a1-a0)
    w=len(g[0]); H=len(r)
    lum=lambda v: (12-v)/11.0 if 1<=v<=12 else 0.0
    im=Image.new('F',(w,a1-a0))
    for y in range(a0,a1):
        for x in range(w): im.putpixel((x,y-a0),lum(g[y][x]))
    nw=max(1,round(w*k)); im=im.resize((nw,b1-b0),Image.LANCZOS)
    out=[[12]*nw for _ in range(H)]
    for y in range(b1-b0):
        for x in range(nw):
            v=min(1.0,max(0.0,im.getpixel((x,y)))); out[b0+y][x]=12-round(v*11)
    return out
def strip(band, text):
    h=glyphs.BANDS[band][1]-glyphs.BANDS[band][0]; bg=glyphs.BANDS[band][2]
    cols=[]
    for i,ch in enumerate(text):
        if ch==' ': cols+= [[bg]*h]*SPACE[band]; continue
        g=glyph(band,ch); w=len(g[0])
        for x in range(w): cols.append([g[y][x] if y<len(g) else bg for y in range(h)])
        if i+1<len(text) and text[i+1]!=' ': cols+=[[bg]*h]*GAP[band]
    return cols   # list of columns
def paste(img, band, cols, x0):
    y0=glyphs.BANDS[band][0]
    for i,col in enumerate(cols):
        for y,v in enumerate(col):
            if v not in (0,): img[y0+y][x0+i]=v
def fill(img, x0,y0,x1,y1,v):
    for y in range(y0,y1):
        for x in range(x0,x1): img[y][x]=v
def copy(src, x0,y0,x1,y1, dst, dx,dy):
    for y in range(y0,y1):
        for x in range(x0,x1): dst[dy+y-y0][dx+x-x0]=src[y][x]
