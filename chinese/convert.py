"""Copy the Chinese text and font out of your own Dongwu Senlin (iQue) ROM.

    python chinese/convert.py "path/to/Dongwu Senlin (China).z64"

Writes chinese/out/ (git-ignored; it stays on your machine):
  zh_msg_data.bin   the iQue message data, as stored (file 1883)
  zh_msg_index.bin  its index: big-endian u32 end offsets (file 1884)
  zh_font.bin       the 12x12 glyph sheet: 4-bit, 192 px wide, 16 glyphs per row (file 1882 from 0x128)

Format details and the code -> character table: https://github.com/jomner/dongwu-senlin-text
"""
import os, struct, sys, zlib

FILE_TABLE = 0x21D80


def read_file(rom, n):
    vs, ve, ps, pe = struct.unpack(">4I", rom[FILE_TABLE + 16 * n:FILE_TABLE + 16 * n + 16])
    return zlib.decompress(rom[ps:pe], -15) if pe else rom[ps:ps + ve - vs]


def main(path):
    rom = open(path, "rb").read()
    if rom[0x20:0x28] != "动物森林".encode("gb2312"):
        sys.exit("This doesn't look like a decrypted Dongwu Senlin ROM (.z64).")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    for name, data in (("zh_msg_data.bin", read_file(rom, 1883)),
                       ("zh_msg_index.bin", read_file(rom, 1884)),
                       ("zh_font.bin", read_file(rom, 1882)[0x128:])):
        open(os.path.join(out, name), "wb").write(data)
    print("Written to", out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python chinese/convert.py <your own Dongwu Senlin ROM (.z64)>")
    main(sys.argv[1])
