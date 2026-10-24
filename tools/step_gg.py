import znp, txt, struct
import os
F=os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fonts'),'DejaVuSansCondensed-Bold.ttf')
CHO=0x20+0x202c; MAPO=0x20+0x2c
CELLS={'R.':[190],'L.':[191],'ELBOW':[27,28],'KNEE':[35,36],'NECK':[37,94],'BACK':[100,131]}
# AGG rows (file offset of the row start) and their labels as lists of words (cells after b80b)
ROWS={0x8e0:['NECK'],0xaa0:['R.','ELBOW'],0xc60:['L.','ELBOW'],0xe20:['BACK'],0xfe0:['R.','KNEE'],0x19a0:['L.','KNEE']}
def put_char(a, i, px):
    for q in range(4):
        for y in range(8):
            for x in range(0,8,2):
                p0=px[(q>>1)*8+y][(q&1)*8+x]; p1=px[(q>>1)*8+y][(q&1)*8+x+1]
                a[CHO+i*128+q*32+y*4+x//2]=(p0<<4)|p1
def word_pixels(word):
    w=16*len(CELLS[word]); avail=w-1
    g,tw=txt.render(word,F,10,w,16,y_off=3)
    if tw>avail:
        g,tw=txt.render(word,F,10,w,16,y_off=3,stretch=avail/tw)
    px=[[15]*w for _ in range(16)]
    for y in range(16):
        for x in range(w):
            v=g[y][x]
            if v>=0.08: px[y][x]=max(1,min(12,1+round(v*11)))
    return px
def apply(reg):
    a=bytearray(znp.get_file(reg,'AGG_SCR.BIN'))
    for word,cells in CELLS.items():
        px=word_pixels(word)
        for k,ci in enumerate(cells):
            put_char(a,ci,[row[k*16:(k+1)*16] for row in px])
    for row,words in ROWS.items():
        o=row+0x1c
        for w in words:
            for ci in CELLS[w]:
                a[o:o+2]=struct.pack('>H',0xb000|ci); o+=2
    znp.replace_file(reg,'AGG_SCR.BIN',bytes(a))
