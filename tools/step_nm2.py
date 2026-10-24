import znp, nm2, nm2build as B
def apply(reg):
    n=nm2.NM2(znp.get_file(reg,'NM2T_SCR.BIN'))
    lib,gap,space,center=B.build_lib(n); lib['P']=B.make_P(lib)
    for k,t in ((2,'Player'),(8,'Player'),(14,'Hiroshi Hase'),(17,'The Patriot')):
        n.put_block(k,B.render(lib,t,gap,space,center))
    znp.replace_file(reg,'NM2T_SCR.BIN',bytes(n.data))
