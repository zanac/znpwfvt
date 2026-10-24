import sys, znp, pf, step_pf, step_pxps, step_nm2, step_gg, news, t2, rgbscr
def build(log=print):
    reg=bytearray(znp.ORIG)
    # A: profiles (Hase, Patriot), data / password panels
    subs,_=pf.subfiles(znp.get_file(reg,'PFT_SCR.BIN')); d=dict(subs)
    px,n1,_,_=step_pxps.px_panel(d['PXPFT.DAT']); ps,n2,_,_=step_pxps.ps_panel(d['PSPFT.DAT'])
    step_pf.apply(reg, extra={'PXPFT.DAT':px,'PSPFT.DAT':ps})
    # A: VS names, DANGER labels
    step_nm2.apply(reg); step_gg.apply(reg)
    # C: victory newspapers
    for i in news.IDS:
        s,img,info=news.clean_photo(reg,i)
        news.draw_headline(img,news.HEADLINE[i],w=250)
        out,n=s.encode(img.tolist(),limit=s.nch)
        znp.replace_file(reg,'TPIN_S%s.BIN'%i,out)
        dd=bytearray(znp.get_file(reg,'TPIN_T%s.BIN'%i))
        w,h,o=t2.tex_entries(dd)[2]; a=t2.get4(dd,w,h,o)
        b,_,_,_=t2.redo_box(a,news.FINAL[i]); t2.put4(dd,w,h,o,b)
        znp.replace_file(reg,'TPIN_T%s.BIN'%i,bytes(dd))
        log('newspaper %s: chars %d -> %d'%(i,s.nch,n))
    return reg
