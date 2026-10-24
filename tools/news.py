import numpy as np, cv2, struct
from PIL import Image, ImageDraw, ImageFont
import znp, rgbscr, photo
import os
FD=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fonts')+os.sep
IDS=['01','02','04','05','06','07','08','10','11','12','13','14']
HEADLINE={
'01':'His howl echoes through the arena',
'02':'Will he go pro wrestler for good?',
'04':'A trade fair of incredible moves',
'05':'Kobashi Kobashi Kobashi Kobashi Kobagi~',
'06':'Locked tight: the Youthful Stretch Plum',
'07':'Anyone at all: a storm of throat chops',
'08':'Even Misawa, like a carp...',
'10':'Does he have a grudge against Kawada?',
'11':"It's not just the lariat, you know",
'12':'A real bargain sale of fierce fights',
'13':'Shorter hair, lighter moves',
'14':'Right after this, that terrifying suplex show began.',
}
FINAL={
'01':'Even his karaoke is getting better!',
'02':'This might pay better than fishing, Jeff!',
'04':'The packed crowd held its breath!',
'05':"We've been waiting for this moment!",
'06':'I knew Kawada would do it!',
'07':"Is this Taue? He's a different man!",
'08':"Sure to top this year's 10 biggest news!",
'10':'Rising fast, now a threat to those above!',
'11':'Burning Texas spirit explodes!',
'12':'With this, I could quit being a killer (doctor)!',
'13':'Somebody stop Ace!',
'14':"Anyone who objects, step up. I'm the strongest!",
}
def font(name, size, var=None):
    f=ImageFont.truetype(FD+name, size)
    if var: f.set_variation_by_name(var)
    return f
def wrap_fit(text, fontname, var, maxw, maxh, sizes, scale=4, maxlines=3, lead=0.95):
    words=text.split(' ')
    for size in sizes:
        f=font(fontname, size*scale, var)
        for nl in range(1, maxlines+1):
            # greedy balanced split into nl lines
            best=None
            import itertools
            for cuts in itertools.combinations(range(1,len(words)), nl-1):
                parts=[' '.join(words[a:b]) for a,b in zip((0,)+cuts, cuts+(len(words),))]
                w=max(f.getlength(p) for p in parts)/scale
                if best is None or w<best[0]: best=(w,parts)
            if best is None: continue
            lh=size*lead
            if best[0]<=maxw and lh*nl<=maxh: return size, best[1], f, lh
    raise ValueError('does not fit: '+text)
def text_mask(parts, f, lh, w, h, scale=4, align='left', angle=0.0, stretch=1.0, valign='top'):
    W=int(w*scale)*2; H=int(h*scale)*3
    im=Image.new('L',(W,H),0); d=ImageDraw.Draw(im)
    y=h*scale//2; maxw=max(f.getlength(p) for p in parts)
    for p in parts:
        tw=f.getlength(p)
        x=scale*4 if align=='left' else scale*4+(maxw-tw)/2
        d.text((x,y),p,font=f,fill=255); y+=lh*scale
    bb=im.getbbox()
    im=im.crop(bb)
    tw=im.width/scale; th=im.height/scale
    k=min(1.0,(w-1)/tw,(h-1)/th)
    nw=max(1,int(round(tw*k))); nh=max(1,int(round(th*k)))
    small=im.resize((nw,nh),Image.LANCZOS)
    out=Image.new('L',(w,h),0)
    ox=0 if align=='left' else (w-nw)//2
    oy=0 if valign=='top' else (h-nh)//2
    out.paste(small,(ox,oy))
    if angle: out=out.rotate(angle, resample=Image.BICUBIC)
    return np.array(out).astype(np.float32)/255.0

def green_mask(a, y0, y1, x0=90, x1=470):
    c=photo.to_rgb(a); r,g,b=c[...,0],c[...,1],c[...,2]
    m=np.zeros(a.shape,bool)
    gm=(g>=12)&(g>r+4)&(g>b+2)
    m[y0:y1,x0:x1]=gm[y0:y1,x0:x1]
    return cv2.dilate(m.astype(np.uint8),np.ones((5,5),np.uint8),iterations=1).astype(bool)
def find_shift(a,b):
    ca=photo.to_rgb(a); cb=photo.to_rgb(b); best=None
    for dy in range(-40,41):
        for dx in range(-20,21):
            sb=cb[180-dy:300-dy,140-dx:300-dx]
            d=np.abs(ca[180:300,140:300]-sb).mean()
            if best is None or d<best[0]: best=(d,dy,dx)
    return best
def clean_photo(reg, i):
    s,a=photo.arr(reg,'TPIN_S%s.BIN'%i); s2,b=photo.arr(reg,'STTP_S%s.BIN'%i)
    d,dy,dx=find_shift(a,b)
    mt=green_mask(a,88,162)
    mj=green_mask(b,88,190)
    H,W=a.shape
    out=a.copy(); hole=np.zeros(a.shape,bool)
    ys,xs=np.nonzero(mt)
    for y,x in zip(ys,xs):
        sy,sx=y-dy,x-dx
        if d<0.5 and 0<=sy<H and 0<=sx<W and not mj[sy,sx]: out[y,x]=b[sy,sx]
        else: hole[y,x]=True
    if hole.any():
        rgb=(photo.to_rgb(out)*8).astype(np.uint8)
        rgb=cv2.inpaint(rgb, hole.astype(np.uint8), 4, cv2.INPAINT_TELEA)
        fix=photo.from_rgb(rgb.astype(np.float32)/8)
        out[hole]=fix[hole]
    return s,out,(d,dy,dx,int(hole.sum()))
GREEN=(6,20,10); EDGE=(27,26,25)
def draw_headline(img, text, x0=102, y0=96, w=262, h=66):
    size,parts,f,lh=wrap_fit(text,'Oswald.ttf','Bold',w-8,h-6,range(44,11,-1),lead=0.98)
    m=np.zeros((h,w),np.float32); m[4:h-2,0:w-4]=text_mask(parts,f,lh,w-4,h-6)
    edge=cv2.dilate((m>0.25).astype(np.uint8),np.ones((3,3),np.uint8)).astype(np.float32)
    edge=cv2.GaussianBlur(edge,(3,3),0.6)
    c=photo.to_rgb(img[y0:y0+h,x0:x0+w])
    e=np.clip(edge,0,1)[...,None]; t=np.clip(m,0,1)[...,None]
    c=c*(1-e)+np.array(EDGE)*e
    c=c*(1-t)+np.array(GREEN)*t
    img[y0:y0+h,x0:x0+w]=photo.from_rgb(c)
    return size,parts
