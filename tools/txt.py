from PIL import Image, ImageDraw, ImageFont
def render(text, font, size, w, h, align='left', y_off=0, x_off=0, scale=4, track=0, stretch=1.0):
    """intensity grid h x w in 0..1 (antialiased text)"""
    f=ImageFont.truetype(font, size*scale)
    # measure
    widths=[f.getlength(c) for c in text]
    tw=sum(widths)+track*scale*(len(text)-1)
    im=Image.new('L',(int(tw)+8*scale, h*scale*2),0); d=ImageDraw.Draw(im)
    x=4*scale
    asc,desc=f.getmetrics()
    for c,wc in zip(text,widths):
        d.text((x, 0), c, font=f, fill=255); x+=wc+track*scale
    bbox=im.getbbox()
    if not bbox: return [[0.0]*w for _ in range(h)]
    im=im.crop((bbox[0],0,bbox[2],im.height))
    tw_px=im.width/scale*stretch
    im=im.resize((max(1,int(round(tw_px*scale))), im.height))
    small=im.resize((max(1,int(round(tw_px))), im.height//scale), Image.LANCZOS)
    out=[[0.0]*w for _ in range(h)]
    if align=='left': ox=x_off
    elif align=='center': ox=(w-small.width)//2+x_off
    else: ox=w-small.width+x_off
    # vertical: cap top at y_off
    sb=small.getbbox() or (0,0,0,0)
    for y in range(small.height):
        for x in range(small.width):
            Y=y-sb[1]+y_off; X=ox+x
            if 0<=Y<h and 0<=X<w: out[Y][X]=max(out[Y][X], small.getpixel((x,y))/255.0)
    return out, small.width
