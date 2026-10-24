import os
"""ZNPWFV asset toolkit: cart region <-> ROM chips, file groups."""
import struct, os
CHIPS=[('mpr20400.2',0x0400000),('mpr20401.3',0x0800000),('mpr20402.4',0x0c00000),('mpr20403.5',0x1000000),('mpr20404.6',0x1400000),('mpr20399.1',0x1800000),('mpr20405.8',0x1c00000),('mpr20406.9',0x2000000),('mpr20407.10',0x2400000)]
GROUPS=[0x400000,0x700000,0x800000,0x1100000,0x1c00000,0x2300000]
GROUP_END={0x400000:0x700000,0x700000:0x800000,0x800000:0x1100000,0x1100000:0x1c00000,0x1c00000:0x2300000,0x2300000:0x2800000}
U=lambda b,o: struct.unpack('>I',b[o:o+4])[0]

def load_region(romdir, epr):
    reg=bytearray(b'\xff'*0x2800000)
    d=open(os.path.join(romdir,epr),'rb').read()
    reg[1:0x200000:2]=d
    reg[0x200000:0x300000]=d; reg[0x300000:0x400000]=d
    for n,o in CHIPS:
        x=open(os.path.join(romdir,n),'rb').read()
        reg[o:o+len(x):2]=x[1::2]; reg[o+1:o+len(x):2]=x[0::2]
    return reg

def chip_bytes(reg, off):
    b=bytearray(0x400000); s=reg[off:off+0x400000]
    b[0::2]=s[1::2]; b[1::2]=s[0::2]
    return bytes(b)

def walk(reg, start):
    o=start; out=[]
    while True:
        s=U(reg,o)
        if s==0: break
        name=bytes(reg[o+4:o+0x14]).split(b'\0')[0].decode()
        out.append([name, bytes(reg[o:o+s])]); o+=s
    return out

def find(reg, name):
    for g in GROUPS:
        for i,(n,b) in enumerate(walk(reg,g)):
            if n==name: return g,i
    raise KeyError(name)

def rebuild(reg, g, files):
    o=g; end=GROUP_END[g]
    blob=b''.join(f[1] for f in files)
    if g+len(blob)+4>end: raise ValueError('group %x overflow by %x'%(g,g+len(blob)+4-end))
    old_end=g+sum(len(b) for n,b in walk(reg,g))
    reg[g:g+len(blob)]=blob
    # clear what followed (old tail and end marker)
    stop=max(old_end+4, g+len(blob)+4)
    reg[g+len(blob):stop]=b'\0'*(stop-g-len(blob))
    return g+len(blob)

def replace_file(reg, name, data, inplace=True):
    """data: the whole file (size field, name, body). In place: padded to the
    old size, so no other file moves (the patch stays small)"""
    g,i=find(reg,name)
    if inplace:
        old=walk(reg,g)[i][1]
        if len(data)>len(old): raise ValueError('%s grows: %x > %x'%(name,len(data),len(old)))
        o=g+sum(len(b) for n,b in walk(reg,g)[:i])
        data=bytearray(data)+b'\0'*(len(old)-len(data)); data[0:4]=struct.pack('>I',len(old))
        reg[o:o+len(old)]=data
        return o+len(old)
    files=walk(reg,g)
    data=bytearray(data); data[0:4]=struct.pack('>I',len(data))
    files[i][1]=bytes(data)
    return rebuild(reg,g,files)

def get_file(reg, name):
    g,i=find(reg,name); return walk(reg,g)[i][1]

ORIG=None   # the original cart region, set by build_patch.py before the other modules load
def load_region_zips(zips):
    """the cart region from the original zips (members found by CRC)"""
    import zipfile, zlib
    want={'epr20398.13':0x3fb56a0b}
    want.update({'mpr20400.2':0x1edfbe05,'mpr20401.3':0x99e98937,'mpr20402.4':0x4572aa60,'mpr20403.5':0x26a8e13e,
                 'mpr20404.6':0x0b70275d,'mpr20399.1':0xc178a96e,'mpr20405.8':0xf53337b7,'mpr20406.9':0xb677c175,'mpr20407.10':0x58356050})
    got={}
    for p in zips:
        z=zipfile.ZipFile(p)
        for i in z.infolist():
            for n,c in want.items():
                if i.CRC==c: got[n]=z.read(i)
    missing=[n for n in want if n not in got]
    if missing: raise SystemExit('missing ROMs: '+' '.join(missing))
    import tempfile
    d=tempfile.mkdtemp()
    for n,b in got.items(): open(os.path.join(d,n),'wb').write(b)
    return load_region(d,'epr20398.13')
