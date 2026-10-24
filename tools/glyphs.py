import znp, pf
BANDS={'title':(256,273,1),'name':(285,308,12),'move':(340,358,12),'line':(360,380,12)}
SRC={
'P01PFT.DAT':('The Spirit Wolf Reborn','Wolf Hawkfield','Giant Swing'),
'P02PFT.DAT':('South Seas Torpedo','Jeffry McWild','Splash Mountain'),
'P04PFT.DAT':('Rider of the Apocalypse','Mitsuharu Misawa','Tiger Driver'),
'P05PFT.DAT':('Orange Crush','Kenta Kobashi','Lariat'),
'P06PFT.DAT':('Dangerous K','Toshiaki Kawada','Power Bomb'),
'P07PFT.DAT':('Dynamic T','Akira Taue','Throat Chop Drop'),
'P08PFT.DAT':('Giant of the World','Giant Baba','Bigfoot kick'),
'P10PFT.DAT':('Super Nova','Jun Akiyama','Exploder'),
'P11PFT.DAT':('The Unsinkable','Stan Hansen','Western Lariat'),
'P12PFT.DAT':('Doctor Death','Steve Williams','Back Drop'),
'P13PFT.DAT':('Wild Wolf','Johnny Ace','Ace Crusher'),
'P14PFT.DAT':('Windmill of Death','Gary Albright','Full Nelson Suplex'),
}
def segments(img, y0, y1, bg, x0=16, x1=240, bgset=None):
    bgset=bgset or {bg}
    cols=[any(img[y][x] not in bgset for y in range(y0,y1)) for x in range(x0,x1)]
    segs=[]; s=None
    for i,c in enumerate(cols+[False]):
        if c and s is None: s=i
        if not c and s is not None: segs.append((x0+s,x0+i)); s=None
    return segs
def load_pfs():
    reg=bytearray(znp.ORIG)
    subs,_=pf.subfiles(znp.get_file(reg,'PFT_SCR.BIN'))
    return reg, dict(subs)
if __name__=='__main__':
    reg,d=load_pfs()
    for n,(t,nm,mv) in SRC.items():
        img=pf.PF(d[n]).indexed()
        for band,txt in (('title',t),('name',nm),('move',mv)):
            y0,y1,bg=BANDS[band]
            bgset={bg,0} if band!='title' else {1,0}
            sg=segments(img,y0,y1,bg,bgset=bgset)
            if band=='title': sg=[s for s in sg if s[1]-s[0]<20]
            n_chars=len(txt.replace(' ',''))
            print(n,band,len(sg),n_chars, 'OK' if len(sg)==n_chars else 'MISMATCH', sg[:3])

def ink_set(band, th=3):
    return ({0}|set(range(1,13-th+0))) if band=='title' else ({0}|set(range(th+1,13)))
def build_lib(d, th=3):
    lib={'title':{},'name':{},'move':{}}
    spaces={'title':[],'name':[],'move':[]}
    for n,(t,nm,mv) in SRC.items():
        img=pf.PF(d[n]).indexed()
        for band,txt in (('title',t),('name',nm),('move',mv)):
            y0,y1,bg=BANDS[band]
            sg=segments(img,y0,y1,bg,bgset=ink_set(band,th))
            if band=='title': sg=sg[:-1]
            chars=txt.replace(' ','')
            if len(sg)!=len(chars): continue
            # spaces: gap where a word boundary is
            k=0
            for wi,w in enumerate(txt.split(' ')):
                for ci,ch in enumerate(w):
                    x0,x1=sg[k]
                    g=[row[x0:x1] for row in img[y0:y1]]
                    lib[band].setdefault(ch,[]).append((n,x0,x1,g))
                    if ci==len(w)-1 and k+1<len(sg): spaces[band].append(sg[k+1][0]-x1)
                    k+=1
    return lib,spaces
