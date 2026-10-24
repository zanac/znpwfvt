import znp, pf, pftext as T, collections
def mode(img,x0,y0,x1,y1):
    return collections.Counter(img[y][x] for y in range(y0,y1) for x in range(x0,x1)).most_common(1)[0][0]
def px_panel(data):
    p=pf.PF(data); img=p.indexed()
    for (y0,y1,t) in ((104,120,'System RAM'),(248,264,'Cartridge RAM')):
        bg=mode(img,28,y0,150,y1)
        T.clear(img,28,y0,182,y1,bg, only=set(range(1,13))-{bg})
        for y in range(y1,y1+4):
            for x in range(28,182):
                if img[y][x] not in (0,) and img[y-1][x]!=img[y][x] and y>=y1: pass
        T.draw(img,30,y0,150,y1,t,size=11,fg=1,bg=bg,y_off=2)
    n=p.encode(img, range(4,24), range(1,15)); return bytes(p.data), n, p, img
def ps_panel(data):
    q=pf.PF(data); im2=q.indexed()
    T.clear(im2,30,398,230,440,12, only=set(range(1,12)))
    T.clear(im2,30,452,230,484,12, only=set(range(1,12)))
    T.draw(im2,34,401,228,418,'The password was not',size=11,fg=1,bg=12,align='center',y_off=3)
    T.draw(im2,34,419,228,437,'entered correctly.',size=11,fg=1,bg=12,align='center',y_off=3)
    T.draw(im2,34,458,228,478,'Password accepted.',size=11,fg=1,bg=12,align='center',y_off=4)
    n=q.encode(im2, range(4,31), range(1,29)); return bytes(q.data), n, q, im2
