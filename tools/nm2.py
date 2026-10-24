import znp, struct
from PIL import Image
NAMES={0:'Wolf Hawkfield',1:'Jeffry McWild',3:'Mitsuharu Misawa',4:'Kenta Kobashi',5:'Toshiaki Kawada',6:'Akira Taue',7:'Giant Baba',9:'Jun Akiyama',10:'Stan Hansen',11:'Steve Williams',12:'Johnny Ace',13:'Gary Albright'}
class NM2:
    def __init__(s, data):
        s.data=bytearray(data); s.cho=0x20+0x1028
        s.pal=[struct.unpack('>H',s.data[0x20+0x3a028+i*2:0x20+0x3a028+i*2+2])[0] for i in range(16)]
    def block(s,k):
        px=[[0]*512 for _ in range(48)]
        for r in range(3):
            for c in range(32):
                base=s.cho+(k*96+r*32+c)*128
                for q in range(4):
                    for y in range(8):
                        for x in range(8):
                            b=s.data[base+q*32+y*4+x//2]; px[r*16+(q>>1)*8+y][c*16+(q&1)*8+x]=(b>>4) if x%2==0 else b&15
        return px
    def put_block(s,k,px):
        for r in range(3):
            for c in range(32):
                base=s.cho+(k*96+r*32+c)*128
                for q in range(4):
                    for y in range(8):
                        for x in range(0,8,2):
                            a=px[r*16+(q>>1)*8+y][c*16+(q&1)*8+x]; b=px[r*16+(q>>1)*8+y][c*16+(q&1)*8+x+1]
                            s.data[base+q*32+y*4+x//2]=(a<<4)|b
    def image(s,px):
        im=Image.new('RGB',(len(px[0]),len(px))); p=im.load()
        for y,row in enumerate(px):
            for x,v in enumerate(row):
                c=s.pal[v]; p[x,y]=((c&31)<<3,((c>>5)&31)<<3,((c>>10)&31)<<3) if v else (40,0,40)
        return im
def components(px):
    H=len(px); W=len(px[0]); seen=[[False]*W for _ in range(H)]; comps=[]
    for y in range(H):
        for x in range(W):
            if px[y][x] and not seen[y][x]:
                st=[(y,x)]; seen[y][x]=True; pts=[]
                while st:
                    cy,cx=st.pop(); pts.append((cy,cx))
                    for dy in (-1,0,1):
                        for dx in (-1,0,1):
                            ny,nx=cy+dy,cx+dx
                            if 0<=ny<H and 0<=nx<W and px[ny][nx] and not seen[ny][nx]:
                                seen[ny][nx]=True; st.append((ny,nx))
                comps.append(pts)
    return comps
def glyphs_of(px, text):
    comps=components(px)
    boxes=[[min(x for y,x in c),max(x for y,x in c),c] for c in comps]
    boxes.sort(key=lambda b:(b[0]+b[1])/2)
    merged=[]
    for b in boxes:
        if merged:
            m=merged[-1]; ov=min(m[1],b[1])-max(m[0],b[0])
            if ov>0 and ov>=0.5*min(m[1]-m[0],b[1]-b[0]):
                m[0]=min(m[0],b[0]); m[1]=max(m[1],b[1]); m[2]=m[2]+b[2]; continue
        merged.append(b)
    chars=text.replace(' ','')
    if len(merged)!=len(chars): return None, len(merged)
    out={}
    xs=[(m[0],m[1]) for m in merged]
    for ch,m in zip(chars,merged):
        out.setdefault(ch,[]).append((m[0],m[1],m[2]))
    return out, xs

def glyphs_core(px, text, core=lambda v: v>=11):
    H=len(px); W=len(px[0])
    cpx=[[1 if core(v) else 0 for v in row] for row in px]
    comps=components(cpx)
    comps=[c for c in comps if len(c)>=3]
    boxes=[[min(x for y,x in c),max(x for y,x in c),c] for c in comps]
    boxes.sort(key=lambda b:(b[0]+b[1])/2)
    merged=[]
    for b in boxes:
        if merged:
            m=merged[-1]; ov=min(m[1],b[1])-max(m[0],b[0])
            if ov>0 and ov>=0.5*min(m[1]-m[0],b[1]-b[0]):
                m[0]=min(m[0],b[0]); m[1]=max(m[1],b[1]); m[2]=m[2]+b[2]; continue
        merged.append(b)
    chars=text.replace(' ','')
    if len(merged)!=len(chars): return None, [(m[0],m[1]) for m in merged]
    # assign every nonzero pixel to nearest core component (by distance to its pixel set, approx by x within row)
    lab=[[-1]*W for _ in range(H)]
    for i,m in enumerate(merged):
        for (y,x) in m[2]: lab[y][x]=i
    # BFS growth from cores over nonzero pixels
    from collections import deque
    q=deque((y,x) for y in range(H) for x in range(W) if lab[y][x]>=0)
    while q:
        y,x=q.popleft()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<H and 0<=nx<W and px[ny][nx] and lab[ny][nx]<0:
                lab[ny][nx]=lab[y][x]; q.append((ny,nx))
    out={}
    for i,ch in enumerate(chars):
        pts=[(y,x) for y in range(H) for x in range(W) if lab[y][x]==i]
        x0=min(x for y,x in pts); x1=max(x for y,x in pts)+1
        g={(y,x-x0):px[y][x] for y,x in pts}
        out.setdefault(ch,[]).append((x0,x1,g))
    return out, None
