# Chinese (work in progress)

A fork of [flyngmt/ACGC-PC-Port](https://github.com/flyngmt/ACGC-PC-Port) that shows the game's text in Chinese, using the official Chinese translation from **动物森林 (Dòngwù Sēnlín)**, the 2006 iQue Player release of the N64 original.

Nothing Chinese is in this repository. Like the port's game data, it comes from your own copy: `convert.py` reads your Dongwu Senlin ROM and writes the text and font to `chinese/out/`, on your machine only. The format and the code → character table are documented in [jomner/dongwu-senlin-text](https://github.com/jomner/dongwu-senlin-text).

## Status

**Proof of concept works.** On a new game, the mapped messages of the opening show in Chinese, drawn from the iQue's own glyphs, with no crash or freeze.

How it fits together:

- `convert.py` builds the 11 glyph banks, writes every message in the game's byte format (each Chinese character as the new control code `7F 7B bank slot`; iQue line breaks `0x7D` become the GameCube's `0xCD`) and turns `message-map.json` into `zh_map.bin`.
- `pc/src/pc_zh.c` loads `chinese/out/` at startup (`[ZH]` line with `--verbose`); `mMsg_LoadMsgData` swaps in mapped messages; `mFont_CodeSize_get` sizes the new code; `mFontSentence_gppDraw_main` draws it with the bank texture in place of the font; the text cursor (`m_msg_cursol.c_inc`) types it like an ordinary character.
- `message-map.json`: 43 messages from the opening, matched by control-code skeleton (the sequence of pauses, choices and name inserts) against a play-through log. On this stretch the iQue number is the GameCube number minus one.
- Mapping helper: while `chinese/log-messages` exists beside the game, every message it shows is appended to `chinese/seen.txt` with its number and text.

## Known issues (from the first play-test)

1. **Glyphs look rough.** Ragged edges and soft scaling: the iQue's 12×12 glyphs are drawn in the font's 12×16 cells and scaled with filtering. Try nearest-neighbour filtering for the bank textures, check the cell offset (`TOP` in `convert.py`), or upscale the glyphs when converting.
2. **No speech sound (Animalese) on Chinese text.** The voice is chosen per character from the letter; a Chinese glyph has no letter. Give each glyph a sound, e.g. from its pinyin.
3. **The player's answers in choice boxes stay English.** Choices are separate strings, not mapped yet.
4. **Some lines stay English.** Rover's first lines (e.g. 10950, 10952) and a few others matched weakly and were left out; review them.
5. **Character names stay English.** Names come from separate name tables, not messages; the iQue's are in files 1885–1899, still to be decoded.

## Next steps

1. Fix 1 and 2 (look and sound).
2. Map choices (3), the weak matches (4) and names (5).
3. Map automatically: line up the Japanese N64 text (numbered like the iQue's) with the Japanese GameCube text, instead of play-through logs.

## Plan

1. **Load.** `mMsg_LoadMsgData` (`src/game/m_msg_data.c_inc`) loads each message by number. Hook it: if `message-map.json` maps this GameCube message to an iQue one, load that from `out/zh_msg_data.bin` instead.
2. **Map messages.** The iQue script is the N64 game; this is the GameCube game, with much more text. Map the proof-of-concept messages by hand in `message-map.json`. Later, map automatically by lining up the Japanese N64 text (numbered like the iQue's) with the Japanese GameCube text. GameCube-only text stays English unless translated.
3. **Two-byte characters, the e+ way.** [ACreTeam/afe-decomp](https://github.com/ACreTeam/afe-decomp) (Dōbutsu no Mori e+, CC0) adds kanji to this same font code with a parallel "wide" path (`src/game/m_font_wide.c_inc`: `mFontW_*`, `mFont_SetLineStringsW`). Characters are 16-bit: top byte 0 is an ordinary character or control code; any other top byte is a wide character, drawn from a separate 256-glyph texture bank, indexed by the bottom byte. e+ has one such bank. Chinese needs 2,670 characters, so use **11 banks**: top byte = bank 1–11, bottom byte = glyph in it.
4. **Convert on the player's machine** (done). `convert.py` packs the 2,670 glyphs the script uses from the iQue font into 11 bank textures of 256, and re-encodes each iQue message into e+'s 16-bit form (iQue glyph `(second << 7 | (first & 0x7F)) + 128` → bank and slot; control codes kept with top byte 0). Each bank is shaped like this game's own font texture (192×256, 4-bit, 12×16 cells, GameCube tiles), so the existing loader can draw it. Next: port e+'s wide path, choosing among 11 banks instead of one. Message drawing is in `src/game/m_msg_draw_font.c_inc`.
5. **Control codes.** The iQue text uses the same control codes as this game (`0x7F` + code, sizes from ac-decomp's `mFont_cont_info_tbl`), so `{player_name}` and the like should carry over. Check the codes the GameCube added.

## Findings for the next step

- **Hook.** `mMsg_LoadMsgData` is in `src/game/m_msg_main.c_inc` (line 325). It copies the message into `msg_data->text_buf.data`, and already has a `#ifdef TARGET_PC` block that edits particular messages; the Chinese override goes beside it.
- **The message system is one byte per unit.** The buffer, cursor, width and drawing all walk the text with `mFont_CodeSize_get`. e+'s 16-bit text would mean converting all of it.
- **Proof-of-concept shortcut: a new control code.** Control codes are `7F code args`, and everything already sizes and skips them. Add code `0x7B` (the first unused; ac-decomp's table ends at `0x7A`), size 4: `7F 7B bank slot` = draw glyph `slot` from Chinese bank `bank`. Then only drawing (`src/game/m_msg_draw_font.c_inc`, from the bank texture) and width (12 px) need teaching. `convert.py` would write messages in this byte form too. e+'s full 16-bit path can come later.
- **Files.** The port reads files with plain `fopen` (`pc/src/pc_assets.c`). The font texture is the array `FONT_nes_tex_font1` (`mFont_Get_FontTex_p`, `m_font_main.c_inc`).

## Try the converter

```
python chinese/convert.py "path/to/Dongwu Senlin (China).z64"
```
