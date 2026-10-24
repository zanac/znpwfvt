import struct
from PIL import Image
import znp
H=lambda b,o: struct.unpack('>H',b[o:o+2])[0]
U=lambda b,o: struct.unpack('>I',b[o:o+4])[0]
def subfiles(container):
    """container file bytes -> list of [name, bytes] subfiles (chain from +0x20)"""
    o=0x20; out=[]
    while o < len(container)-4:
        s=U(container,o)
        if s==0 or s>len(container): break
        out.append([bytes(container[o+4:o+0x14]).split(b'\0')[0].decode(), bytes(container[o:o+s])]); o+=s
    return out, o
class PF:
    def __init__(s, data):
        s.data=bytearray(data); D=0x20
        s.hdr=[U(s.data,D+i) for i in range(0,0x28,4)]
        s.mapo=D+s.hdr[6]; s.cho=D+s.hdr[7]; s.palo=D+s.hdr[8]; s.nch=s.hdr[3]//128
        s.pal=[H(s.data,s.palo+i*2) for i in range(16)]
        s.map=[H(s.data,s.mapo+i*2) for i in range(1024)]
    def rgb(s,c): return ((c&31)<<3,((c>>5)&31)<<3,((c>>10)&31)<<3)
    def char_pixels(s,idx):
        a=s.cho+idx*128; px=[[0]*16 for _ in range(16)]
        for q in range(4):
            for y in range(8):
                for x in range(8):
                    b=s.data[a+q*32+y*4+x//2]; px[(q>>1)*8+y][(q&1)*8+x]=(b>>4) if x%2==0 else b&15
        return px
    def indexed(s):
        """32x32 chars -> 512x512 list of palette indices"""
        img=[[0]*512 for _ in range(512)]
        for r in range(32):
            for c in range(32):
                w=s.map[r*32+c]; p=s.char_pixels(w&0x3ff)
                for y in range(16): img[r*16+y][c*16:c*16+16]=p[y]
        return img
    def to_image(s, img=None):
        img=img or s.indexed(); im=Image.new('RGB',(512,512)); px=im.load()
        for y in range(512):
            for x in range(512): px[x,y]=s.rgb(s.pal[img[y][x]])
        return im
    def encode(s, img, rows, cols):
        """img: 512x512 indices; rows/cols: the cells of the panel to encode. keeps size."""
        chars={}; order=[]; newmap=list(s.map)
        def cell(r,c): return tuple(tuple(img[r*16+y][c*16:c*16+16]) for y in range(16))
        # char 0 stays what the map outside the panel uses
        for r in range(32):
            for c in range(32):
                if r in rows and c in cols: continue
        used_outside=set(s.map[r*32+c]&0x3ff for r in range(32) for c in range(32) if not (r in rows and c in cols))
        keep={i: tuple(tuple(row) for row in s.char_pixels(i)) for i in used_outside}
        for i,p in keep.items(): chars[p]=i
        nxt=0
        for r in rows:
            for c in cols:
                p=cell(r,c)
                if p not in chars:
                    while nxt in used_outside: nxt+=1
                    chars[p]=nxt; order.append((nxt,p)); nxt+=1
                newmap[r*32+c]=(s.map[r*32+c]&0xfc00)|chars[p]
        if nxt>s.nch: raise ValueError('needs %d chars, has %d'%(nxt,s.nch))
        for i,p in order:
            a=s.cho+i*128
            for q in range(4):
                for y in range(8):
                    for x in range(0,8,2):
                        s.data[a+q*32+y*4+x//2]=(p[(q>>1)*8+y][(q&1)*8+x]<<4)|p[(q>>1)*8+y][(q&1)*8+x+1]
        # clear unused chars
        for i in range(nxt,s.nch):
            if i not in used_outside: s.data[s.cho+i*128:s.cho+i*128+128]=b'\0'*128
        for i,w in enumerate(newmap): s.data[s.mapo+i*2:s.mapo+i*2+2]=struct.pack('>H',w)
        s.map=newmap
        return nxt

def align16(n): return (n+15)&~15
def pf_resize(p, nch):
    """return new file bytes for PF p with nch chars (map/palette kept)"""
    D=0x20; hdr=list(p.hdr)
    old=p.data
    mapb=old[p.mapo:p.mapo+0x800]; pal=old[p.palo:p.palo+0x20]
    chars=bytearray(old[p.cho:p.cho+min(p.nch,nch)*128]); chars+=b'\0'*(nch*128-len(chars))
    hdr[3]=nch*128; hdr[8]=hdr[7]+nch*128
    body=b''.join(struct.pack('>I',h) for h in hdr)+bytes(old[D+0x28:D+hdr[6]])  # header + whatever before map
    body=body+bytes(mapb)
    assert len(body)==hdr[7]
    body+=bytes(chars)+bytes(pal)
    size2=len(body)
    head=bytearray(old[:0x20]); head[0x14:0x18]=struct.pack('>I',size2)
    out=bytearray(head)+body
    out+=b'\0'*(align16(len(out))-len(out)); out[0:4]=struct.pack('>I',len(out))
    return bytes(out)
def container_build(cont, subs):
    """cont: original container bytes; subs: list of [name, bytes]"""
    head=bytearray(cont[:0x20]); body=b''.join(b for n,b in subs)+b'\0'*0x20
    size2=len(body); head[0x14:0x18]=struct.pack('>I',size2)
    out=head+body; out+=b'\0'*(align16(len(out))-len(out)); out[0:4]=struct.pack('>I',len(out))
    return bytes(out)
