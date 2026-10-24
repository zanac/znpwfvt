import numpy as np, struct, math
import news
def tex_entries(data):
    D=0x20; cnt=struct.unpack('>H',data[D+4:D+6])[0]; out=[]
    for i in range(cnt):
        e=D+0x10+i*12; w,h,m,f,off=struct.unpack('>HHHHI',data[e:e+12]); out.append((w,h,D+off))
    return out
def get4(data,w,h,o):
    a=np.zeros((h,w),np.int32)
    for y in range(h):
        row=data[o+y*w//2:o+(y+1)*w//2]
        for x in range(w//2): a[y,2*x]=row[x]>>4; a[y,2*x+1]=row[x]&15
    return a
def put4(data,w,h,o,a):
    for y in range(h):
        for x in range(w//2): data[o+y*w//2+x]=(int(a[y,2*x])<<4)|int(a[y,2*x+1])
def redo_box(a, text):
    h,w=a.shape
    nz=a!=0
    # top edge per column
    cols=[x for x in range(w) if nz[:,x].any()]
    top={x:np.nonzero(nz[:,x])[0][0] for x in cols}; bot={x:np.nonzero(nz[:,x])[0][-1] for x in cols}
    xs=np.array(cols[20:-20]); ty=np.array([top[x] for x in xs]); by=np.array([bot[x] for x in xs])
    k_top=np.polyfit(xs,ty,1); k_bot=np.polyfit(xs,by,1)
    ang=math.degrees(math.atan(k_top[0]))
    left=min(cols); right=max(cols)
    out=a.copy()
    inner=np.zeros_like(nz)
    for x in range(left+5,right-4):
        t=int(math.ceil(np.polyval(k_top,x)))+4; b=int(np.polyval(k_bot,x))-4
        inner[t:b+1,x]=True
    out[inner]=14
    # text box: in rotated frame
    cy=(np.polyval(k_top,(left+right)/2)+np.polyval(k_bot,(left+right)/2))/2
    bh=int(np.polyval(k_bot,(left+right)/2)-np.polyval(k_top,(left+right)/2))-10
    bw=right-left-16
    size,parts,f,lh=news.wrap_fit(text,'Oswald.ttf','SemiBold',bw-4,bh-2,range(30,9,-1),lead=1.12)
    m=news.text_mask(parts,f,lh,bw,bh,align='center',valign='center')
    from PIL import Image
    im=Image.fromarray((m*255).astype(np.uint8)).rotate(-ang if False else ang*-1, resample=Image.BICUBIC, expand=False)
    m=np.array(im).astype(np.float32)/255
    ox=left+8; oy=int(round(cy-bh/2))
    for y in range(bh):
        for x in range(bw):
            v=m[y,x]; Y=oy+y; X=ox+x
            if 0<=Y<h and 0<=X<w and inner[Y,X]:
                if v>0.6: out[Y,X]=2
                elif v>0.3: out[Y,X]=12
    return out, size, parts, ang
