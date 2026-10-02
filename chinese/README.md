# Chinese (work in progress)

A fork of [flyngmt/ACGC-PC-Port](https://github.com/flyngmt/ACGC-PC-Port) that shows the game's text in Chinese, using the official Chinese translation from **动物森林 (Dòngwù Sēnlín)**, the 2006 iQue Player release of the N64 original.

Nothing Chinese is in this repository. Like the port's game data, it comes from your own copy: `convert.py` reads your Dongwu Senlin ROM and writes the text and font to `chinese/out/`, on your machine only. The format and the code → character table are documented in [jomner/dongwu-senlin-text](https://github.com/jomner/dongwu-senlin-text).

## Status

The converter is done: `convert.py` builds the glyph banks and writes every message in this game's byte format, each Chinese character as the new control code `7F 7B bank slot` (`0x7B` is the first code this port doesn't use). All 11,791 messages walk cleanly with that code sized 4. The port doesn't use the output yet.

**First goal (proof of concept):** Tom Nook's intro and one villager conversation in Chinese, everything else in English.

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
