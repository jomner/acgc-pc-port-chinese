"""Make the Chinese text and font from your own Dongwu Senlin (iQue) ROM.

    python chinese/convert.py "path/to/Dongwu Senlin (China).z64"

Writes chinese/out/ (git-ignored; it stays on your machine):

  zh_banks.bin      the glyphs the script uses, packed into banks shaped like this
                    game's own font: each bank a 192x256 4-bit (I4) texture, 16x16
                    cells of 12x16 px, in the GameCube's 8x8 tiles; 24,576 bytes each
  zh_msg.bin        every message in this game's own byte format, with each Chinese
                    character as a new control code: 7F 7B bank slot (bank 1-based)
  zh_msg_index.bin  little-endian u32 end offset of each message in zh_msg.bin
  zh_map.bin        message-map.json as little-endian u32 pairs: GameCube message, iQue message

Format details and the code -> character table: https://github.com/jomner/dongwu-senlin-text
"""
import json, os, struct, sys, zlib

FILE_TABLE = 0x21D80
MSG_DATA, MSG_INDEX, FONT_FILE, FONT_OFFSET = 1883, 1884, 1882, 0x128
CELL_W, CELL_H, GLYPH = 12, 16, 12   # bank cell, and the iQue glyph inside it
TOP = 2                              # rows above the 12-row glyph in its 16-row cell
ZH_GLYPH = 0x7B                      # new control code: 7F 7B bank slot (the game's table ends at 0x7A)

# Control code sizes (0x7F, code, arguments), from ac-decomp's mFont_cont_info_tbl.
CONT_SIZES = ([2, 2, 2, 3, 2, 5, 2, 2, 5, 5, 5, 5, 5, 2, 4, 4, 4, 4, 4, 6, 8, 10, 6, 8, 10]
              + [2] * 55 + [6, 3, 3, 3, 3, 2, 4, 4, 3, 3, 3] + [2] * 8
              + [6, 3, 3, 4, 3, 2, 2, 6, 2, 2, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 4, 4, 12, 14])


def read_file(rom, n):
    vs, ve, ps, pe = struct.unpack(">4I", rom[FILE_TABLE + 16 * n:FILE_TABLE + 16 * n + 16])
    return zlib.decompress(rom[ps:pe], -15) if pe else rom[ps:ps + ve - vs]


def parse(data, start, end):
    """One iQue message -> list of ('glyph', number) and ('byte', value) tokens."""
    out, i = [], start
    while i < end:
        b = data[i]
        if b == 0x7F:
            size = CONT_SIZES[data[i + 1]] if data[i + 1] < len(CONT_SIZES) else 2
            out += [("byte", x) for x in data[i:i + size]]
            i += size
        elif b == 0x7D:
            out.append(("byte", b)); i += 1
        elif b >= 0x80:
            out.append(("glyph", ((data[i + 1] << 7) | (b & 0x7F)) + 128)); i += 2
        else:
            out.append(("glyph", b)); i += 1
    return out


def glyph_pixels(font, n):
    """iQue glyph n as 12 rows of 12 4-bit values (sheet: 192 px wide, 16 glyphs per row)."""
    row, col = divmod(n, 16)
    strip = font[row * 1152:(row + 1) * 1152]
    rows = []
    for y in range(GLYPH):
        line = strip[y * 96 + col * 6:y * 96 + col * 6 + 6]
        rows.append([v for b in line for v in (b >> 4, b & 15)])
    return rows


def bank_texture(font, glyphs):
    """Up to 256 glyphs -> one 192x256 I4 texture in GameCube 8x8 tiles."""
    w, h = CELL_W * 16, CELL_H * 16
    px = [[0] * w for _ in range(h)]
    for slot, n in enumerate(glyphs):
        cy, cx = divmod(slot, 16)
        for y, line in enumerate(glyph_pixels(font, n)):
            px[cy * CELL_H + TOP + y][cx * CELL_W:cx * CELL_W + GLYPH] = line
    out = bytearray()
    for by in range(0, h, 8):
        for bx in range(0, w, 8):
            for y in range(by, by + 8):
                for x in range(bx, bx + 8, 2):
                    out.append(px[y][x] << 4 | px[y][x + 1])
    return bytes(out)


def main(path):
    rom = open(path, "rb").read()
    if rom[0x20:0x28] != "动物森林".encode("gb2312"):
        sys.exit("This doesn't look like a decrypted Dongwu Senlin ROM (.z64).")
    data, index = read_file(rom, MSG_DATA), read_file(rom, MSG_INDEX)
    font = read_file(rom, FONT_FILE)[FONT_OFFSET:]
    ends = struct.unpack(f">{len(index) // 4}I", index)
    messages = [parse(data, ends[m - 1], ends[m]) for m in range(1, len(ends))]

    used = sorted({v for msg in messages for kind, v in msg if kind == "glyph"})
    place = {n: (i // 256 + 1, i % 256) for i, n in enumerate(used)}  # glyph -> (bank, slot)
    banks = [used[i:i + 256] for i in range(0, len(used), 256)]

    text, offsets = bytearray(), []
    for msg in messages:
        for kind, v in msg:
            text += bytes([0x7F, ZH_GLYPH, *place[v]]) if kind == "glyph" else bytes([v])
        offsets.append(len(text))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    for old in ("zh_msg_data.bin", "zh_font.bin"):  # from the first version of this script
        if os.path.exists(os.path.join(out, old)):
            os.remove(os.path.join(out, old))
    open(os.path.join(out, "zh_banks.bin"), "wb").write(b"".join(bank_texture(font, b) for b in banks))
    open(os.path.join(out, "zh_msg.bin"), "wb").write(text)
    open(os.path.join(out, "zh_msg_index.bin"), "wb").write(struct.pack(f"<{len(offsets)}I", *offsets))
    pairs = json.load(open(os.path.join(os.path.dirname(out), "message-map.json"), encoding="utf-8"))["map"]
    open(os.path.join(out, "zh_map.bin"), "wb").write(
        b"".join(struct.pack("<2I", int(gc), int(iq)) for gc, iq in pairs.items()))
    print(f"{len(messages)} messages, {len(used)} characters in {len(banks)} banks, written to {out}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python chinese/convert.py <your own Dongwu Senlin ROM (.z64)>")
    main(sys.argv[1])
