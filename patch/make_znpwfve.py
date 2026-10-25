#!/usr/bin/env python3
"""Build znpwfve.zip (All Japan Pro-Wrestling Featuring Virtua, English
translation) from the original ROM sets. Python 3 standard library only.

usage: make_znpwfve.py ROMDIR [OUTDIR]

ROMDIR must hold znpwfv.zip and the Taiwan program epr20408.13, either in
znpwfvt.zip or inside a merged znpwfv.zip (as znpwfvt/epr20408.13).
The result is OUTDIR/znpwfve.zip (OUTDIR defaults to ROMDIR).
"""
import hashlib, os, sys, zipfile, zlib, lzma, struct

HERE = os.path.dirname(os.path.abspath(__file__))
TAIWAN = ('epr20408.13', 0x1d62fcf6)


def find_member(zips, name, crc):
    """a member of any of the zips with this CRC (the name may have a folder)"""
    for z in zips:
        for info in z.infolist():
            if info.CRC == crc and os.path.basename(info.filename) == name:
                return z.read(info)
    for z in zips:
        for info in z.infolist():
            if info.CRC == crc:
                return z.read(info)
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    romdir = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else romdir
    zips = []
    for n in ('znpwfv.zip', 'znpwfvt.zip'):
        p = os.path.join(romdir, n)
        if os.path.exists(p):
            zips.append(zipfile.ZipFile(p))
    if not zips:
        print('znpwfv.zip not found in ' + romdir)
        return 1

    prog = find_member(zips, *TAIWAN)
    if prog is None:
        print('epr20408.13 (CRC 1d62fcf6, the Taiwan program) not found')
        return 1

    patch = open(os.path.join(HERE, 'znpwfve.dat'), 'rb').read()
    assert patch[:6] == b'ZNPE1\0', 'bad patch file'
    o = 6
    out = [(TAIWAN[0], prog)]
    while o < len(patch):
        names = []
        for _ in range(2):
            n = patch[o]
            names.append(patch[o + 1:o + 1 + n].decode())
            o += 1 + n
        src_crc, dst_crc, size = struct.unpack('>III', patch[o:o + 12])
        o += 12
        xor = lzma.decompress(patch[o:o + size])
        o += size
        src = find_member(zips, names[0], src_crc)
        if src is None:
            print('%s (CRC %08x) not found' % (names[0], src_crc))
            return 1
        dst = bytes(a ^ b for a, b in zip(src, xor))
        if zlib.crc32(dst) != dst_crc:
            print('%s: wrong result' % names[1])
            return 1
        out.append((names[1], dst))

    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, 'znpwfve.zip')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in out:
            z.writestr(name, data)
    print('written ' + path)
    for name, data in out:
        print('  %-14s %8d  %08x  %s' % (name, len(data), zlib.crc32(data),
                                        hashlib.sha1(data).hexdigest()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
