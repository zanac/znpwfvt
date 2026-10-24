import znp, pf, build_pf as B, opt_pf as O
def make_panels():
    out={}
    p,img=B.hase(); O.shift_band(img,276,318,-3)
    q=pf.PF(pf.pf_resize(p,75)); n=q.encode(img,range(16,24),range(1,15)); out['P15PFT.DAT']=bytes(q.data); print('hase chars',n)
    p,img=B.patriot()
    q=pf.PF(pf.pf_resize(p,79)); n=q.encode(img,range(16,24),range(1,15)); out['P18PFT.DAT']=bytes(q.data); print('patriot chars',n)
    return out
def apply(reg, extra=None, swap=None):
    cont=znp.get_file(reg,'PFT_SCR.BIN'); subs,_=pf.subfiles(cont)
    new=make_panels(); 
    if extra: new.update(extra)
    d=dict(subs)
    if swap:   # test: show file B in slot A
        for a,b in swap.items():
            data=bytearray(new.get(b,d[b])); data[4:0x14]=d[a][4:0x14]; new[a]=bytes(data)
    subs=[[n, new.get(n,b)] for n,b in subs]
    c2=pf.container_build(cont,subs); print('container %x -> %x'%(len(cont),len(c2)))
    znp.replace_file(reg,'PFT_SCR.BIN',c2)
