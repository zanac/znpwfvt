import compose_pf as C, glyphs, pf
from PIL import Image
D=C.d
def bar_end(img, y=258):
    # last white pixel of the title bar on a row
    xs=[x for x in range(16,240) if img[y][x] in (1,2,3)]
    return xs[-1]
def base_panel(jp_name, tmpl='P06PFT.DAT'):
    p=pf.PF(D[jp_name]); img=p.indexed()
    t=pf.PF(D[tmpl]).indexed()
    # title band: template bar, text erased
    C.copy(t,16,256,240,273,img,16,256)
    end=bar_end(t,262)
    for y in range(256,273):
        for x in range(16,end-12):
            if img[y][x] not in (0,): img[y][x]=1
    # name band, special attacks bar (template), move band, line band
    C.fill(img,16,273,240,320,12)
    C.copy(t,16,320,240,340,img,16,320)
    C.fill(img,16,340,240,383,12)
    return p, img, t
def text(img, band, s, x=None, center=None, right=None):
    cols=C.strip(band,s)
    if center is not None: x=center-len(cols)//2
    if right is not None: x=right-len(cols)
    C.paste(img,band,cols,x); return x, x+len(cols)
