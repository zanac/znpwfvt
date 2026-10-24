import txt
import os
FONTB=os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fonts'),'DejaVuSans-Bold.ttf')
FONTC=os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fonts'),'DejaVuSansCondensed-Bold.ttf')
def clear(img, x0,y0,x1,y1, bg, only=None):
    for y in range(y0,y1):
        for x in range(x0,x1):
            if only is None or img[y][x] in only: img[y][x]=bg
def draw(img, x0,y0,x1,y1, text, font=FONTB, size=10, fg=1, bg=12, align='left', y_off=0, stretch=1.0, x_off=0):
    w=x1-x0; h=y1-y0
    g,tw=txt.render(text,font,size,w,h,align=align,y_off=y_off,stretch=stretch,x_off=x_off)
    if tw>w-1 and stretch==1.0:
        g,tw=txt.render(text,font,size,w,h,align=align,y_off=y_off,stretch=(w-1)/tw,x_off=x_off)
    for y in range(h):
        for x in range(w):
            v=g[y][x]
            if v>=0.06: img[y0+y][x0+x]=int(round(bg+(fg-bg)*v))
    return tw
