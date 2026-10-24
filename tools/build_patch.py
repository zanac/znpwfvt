#!/usr/bin/env python3
"""Rebuild the English graphics and the patch from the original ROMs.

usage: build_patch.py ZNPWFV_ZIP [OUT_DAT]

Needs Python 3 with numpy, Pillow and opencv-python. The result is the
patch read by patch/make_znpwfve.py (default: ../patch/znpwfve.dat).
"""
import os, sys, lzma, zlib, struct
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import znp

def main():
    if len(sys.argv)<2: print(__doc__); return 1
    znp.ORIG=bytes(znp.load_region_zips(sys.argv[1:2]))
    out=sys.argv[2] if len(sys.argv)>2 else os.path.join(HERE,'..','patch','znpwfve.dat')
    import build_all
    reg=build_all.build()
    blob=b'ZNPE1\0'
    for (src,o),dst in zip(znp.CHIPS[-2:],('znpe20406.9','znpe20407.10')):
        a=znp.chip_bytes(reg,o); b=znp.chip_bytes(znp.ORIG,o)
        x=lzma.compress(bytes(p^q for p,q in zip(a,b)))
        for s in (src.encode(),dst.encode()): blob+=struct.pack('B',len(s))+s
        blob+=struct.pack('>III',zlib.crc32(b),zlib.crc32(a),len(x))+x
        print('%-13s CRC %08x'%(dst,zlib.crc32(a)))
    open(out,'wb').write(blob); print('written',out)
    return 0
if __name__=='__main__': sys.exit(main())
