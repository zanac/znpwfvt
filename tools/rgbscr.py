import struct
from PIL import Image
U=lambda b,o: struct.unpack('>I',b[o:o+4])[0]
def align16(n): return (n+15)&~15
class RGBSCR:
    """VDP2 32768-colour cell screen: 2-word pattern names, 16x16 chars of 512 bytes"""
    def __init__(s, data):
        s.data=bytes(data); D=0x20
        s.hdr=[U(s.data,D+i) for i in range(0,0x28,4)]
        s.mapo=D+s.hdr[6]; s.cho=D+s.hdr[7]
        s.nmap=(s.hdr[7]-s.hdr[6])//4
        s.ents=[U(s.data,s.mapo+i*4) for i in range(s.nmap)]
        s.base=min(e&0x7fff for e in s.ents)
        s.pages=s.nmap//1024
        s.nch=s.hdr[3]//512
    def size(s): return (512*min(2,s.pages), 512*((s.pages+1)//2))
    def cellpos(s,i):
        pg=i//1024; r=(i%1024)//32; c=i%32
        return (pg&1)*512+c*16, (pg>>1)*512+r*16
    def char(s, cn):
        a=s.cho+cn*32; px=[]
        for y in range(16):
            row=[]
            for x in range(16):
                q=(y//8)*2+(x//8); o=a+q*128+((y%8)*8+(x%8))*2
                row.append(struct.unpack('>H',s.data[o:o+2])[0])
            px.append(row)
        return px
    def decode(s):
        W,H=s.size(); img=[[0]*W for _ in range(H)]
        for i,e in enumerate(s.ents):
            cn=(e&0x7fff)-s.base; hf=(e>>30)&1; vf=(e>>31)&1
            px=s.char(cn); X,Y=s.cellpos(i)
            for y in range(16):
                for x in range(16):
                    img[Y+(15-y if vf else y)][X+(15-x if hf else x)]=px[y][x]
        return img
    @staticmethod
    def to_image(img):
        im=Image.new('RGB',(len(img[0]),len(img))); p=im.load()
        for y,row in enumerate(img):
            for x,c in enumerate(row): p[x,y]=((c&31)<<3,((c>>5)&31)<<3,((c>>10)&31)<<3)
        return im
    def encode(s, img, limit=None):
        import numpy as np
        chars={}; order=[]; idx=[]
        for i,e in enumerate(s.ents):
            X,Y=s.cellpos(i); hf=(e>>30)&1; vf=(e>>31)&1
            rows=[img[Y+y][X:X+16] for y in range(16)]
            if vf: rows=rows[::-1]
            if hf: rows=[r[::-1] for r in rows]
            cell=tuple(tuple(r) for r in rows)
            if cell not in chars: chars[cell]=len(order); order.append(cell)
            idx.append(chars[cell])
        if limit is not None and len(order)>limit:
            A=np.array(order,dtype=np.int32)
            rgb=np.stack([A&31,(A>>5)&31,(A>>10)&31],-1).reshape(len(order),-1).astype(np.float32)
            alive=list(range(len(order))); remap=list(range(len(order)))
            while len(alive)>limit:
                R=rgb[alive]; best=None
                d=((R[:,None,:]-R[None,:,:])**2).sum(-1); np.fill_diagonal(d,1e18)
                a,b=np.unravel_index(np.argmin(d),d.shape)
                ka,kb=alive[a],alive[b]
                for j in range(len(remap)):
                    if remap[j]==kb: remap[j]=ka
                alive.remove(kb)
            newidx={k:n for n,k in enumerate(alive)}
            order=[order[k] for k in alive]
            idx=[newidx[remap[i]] for i in idx]
        # stable slots: a cell the original file already has keeps its slot,
        # the new ones take the slots nobody uses any more
        orig_cells={}
        for k in range(s.nch):
            c=s.char(k*16); orig_cells.setdefault(tuple(tuple(r) for r in c),k)
        slot=[None]*len(order); used=set()
        for j,cell in enumerate(order):
            k=orig_cells.get(cell)
            if k is not None and k not in used: slot[j]=k; used.add(k)
        free=[k for k in range(max(s.nch,len(order))) if k not in used]
        for j in range(len(order)):
            if slot[j] is None: slot[j]=free.pop(0)
        n=max(slot)+1
        full=[None]*n
        for j,k in enumerate(slot): full[k]=order[j]
        blank=tuple(tuple([0]*16) for _ in range(16))
        for k in range(n):
            if full[k] is None:
                c=s.char(k*16) if k<s.nch else None
                full[k]=tuple(tuple(r) for r in c) if c else blank
        order=full
        ents=[(e&0x3fff8000)|(s.base+slot[idx[i]]*16) for i,e in enumerate(s.ents)]
        D=0x20; hdr=list(s.hdr); hdr[3]=len(order)*512
        body=b''.join(struct.pack('>I',h) for h in hdr)+s.data[D+0x28:D+hdr[6]]
        body+=b''.join(struct.pack('>I',e) for e in ents)
        assert len(body)==hdr[7]
        cb=bytearray()
        for cell in order:
            for q in range(4):
                for y in range(8):
                    for x in range(8):
                        cb+=struct.pack('>H',cell[(q>>1)*8+y][(q&1)*8+x])
        body+=bytes(cb)
        # keep whatever followed the chars (nothing for these files)
        tail=s.data[s.cho+s.hdr[3]: D+(U(s.data,0x14))] if U(s.data,0x14)>s.hdr[7]+s.hdr[3] else b''
        body+=tail
        head=bytearray(s.data[:0x20]); head[0x14:0x18]=struct.pack('>I',len(body))
        out=head+body; out+=b'\0'*(align16(len(out)+8)-len(out)) if False else b''
        out+=b'\0'*(align16(len(out))-len(out))
        out[0:4]=struct.pack('>I',len(out)); return bytes(out), len(order)
