import znp, rgbscr
import numpy as np
def arr(reg,n):
    s=rgbscr.RGBSCR(znp.get_file(reg,n)); return s, np.array(s.decode(),dtype=np.int32)
def to_rgb(a): return np.stack([(a&31),((a>>5)&31),((a>>10)&31)],-1).astype(np.float32)
def from_rgb(c):
    c=np.clip(np.round(c),0,31).astype(np.int32); return 0x8000|c[...,0]|(c[...,1]<<5)|(c[...,2]<<10)
def text_mask(a, y0=88, y1=160, x0=90, x1=470):
    c=to_rgb(a); r,g,b=c[...,0],c[...,1],c[...,2]
    green=(g>=12)&(g>r+4)&(g>b+2)
    m=np.zeros(a.shape,bool); m[y0:y1,x0:x1]=green[y0:y1,x0:x1]
    import cv2
    k=np.ones((5,5),np.uint8)
    return cv2.dilate(m.astype(np.uint8),k,iterations=1).astype(bool)
def align(a,b,mask, rng=6):
    ca=to_rgb(a); cb=to_rgb(b); best=None
    ys,xs=slice(170,320),slice(110,330)
    for dy in range(-rng,rng+1):
        for dx in range(-rng,rng+1):
            sb=np.roll(np.roll(cb,dy,0),dx,1)
            d=np.abs(ca[ys,xs]-sb[ys,xs]).mean()
            if best is None or d<best[0]: best=(d,dy,dx)
    return best
