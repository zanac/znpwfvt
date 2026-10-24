import make_pf as M, compose_pf as C, pf
from PIL import Image
def hase():
    p,img,t=M.base_panel('P15PFT.DAT')
    jp=pf.PF(C.d['P15PFT.DAT']).indexed(); kw=pf.PF(C.d['P06PFT.DAT']).indexed()
    M.text(img,'title','Meteor of the Big Dipper',x=20)
    M.text(img,'name','Hiroshi Hase',center=128)
    M.text(img,'move','Northern Lights Suplex',x=22)
    C.copy(jp,208,358,224,382,img,208,358)        # T
    C.copy(kw,147,358,188,382,img,164,358)        # (Grab! )
    C.copy(jp,124,358,140,382,img,144,358)        # H
    return p,img
def patriot():
    p,img,t=M.base_panel('P18PFT.DAT')
    jp=pf.PF(C.d['P18PFT.DAT']).indexed(); hs=pf.PF(C.d['P11PFT.DAT']).indexed(); wl=pf.PF(C.d['P12PFT.DAT']).indexed()
    M.text(img,'title','Patriotic Warrior',x=20)
    M.text(img,'name','The Patriot',center=128)
    M.text(img,'move','Full Nelson Buster',x=22)
    C.copy(hs,20,360,120,374,img,20,362)          # More than 80 Rage
    C.copy(wl,121,365,189,376,img,234-68,353)     # From Behind (upper right)
    C.copy(jp,185,361,234,380,img,185,364)        # B up C (lower right)
    return p,img
if __name__=='__main__':
    for f,n in ((hase,'hase'),(patriot,'patriot')):
        p,img=f()
        p.to_image(img).crop((0,240,256,400)).resize((768,480),Image.NEAREST).save(n+'_v2.png')
