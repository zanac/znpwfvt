import make_pf as M, compose_pf as C, pf, itertools
def uniq(img):
    s=set()
    for r in range(16,24):
        for c in range(1,15):
            s.add(tuple(tuple(img[r*16+y][c*16:c*16+16]) for y in range(16)))
    return len(s)
def shift_band(img, y0, y1, dy, x0=16, x1=240, bg=12):
    rows=[img[y][x0:x1] for y in range(y0,y1)]
    for y in range(y0+min(0,dy), y1+max(0,dy)):
        if 0<=y<512: img[y][x0:x1]=[bg]*(x1-x0) if True else None
    for i,r in enumerate(rows):
        img[y0+dy+i][x0:x1]=list(r)
