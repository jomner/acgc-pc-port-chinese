# Chinese (work in progress)

A fork of [flyngmt/ACGC-PC-Port](https://github.com/flyngmt/ACGC-PC-Port) that shows the game's text in Chinese, using the official Chinese translation from **动物森林 (Dòngwù Sēnlín)**, the 2006 iQue Player release of the N64 original.

Nothing Chinese is in this repository. Like the port's game data, it comes from your own copy: `convert.py` reads your Dongwu Senlin ROM and writes the text and font to `chinese/out/`, on your machine only. The format and the code → character table are documented in [jomner/dongwu-senlin-text](https://github.com/jomner/dongwu-senlin-text).

## Status

Skeleton. The converter works; the port doesn't use its output yet.

**First goal (proof of concept):** Tom Nook's intro and one villager conversation in Chinese, everything else in English.

## Plan

1. **Load.** `mMsg_LoadMsgData` (`src/game/m_msg_data.c_inc`) loads each message by number. Hook it: if `message-map.json` maps this GameCube message to an iQue one, load that from `out/zh_msg_data.bin` instead.
2. **Map messages.** The iQue script is the N64 game; this is the GameCube game, with much more text. Map the proof-of-concept messages by hand in `message-map.json`. Later, map automatically by lining up the Japanese N64 text (numbered like the iQue's) with the Japanese GameCube text. GameCube-only text stays English unless translated.
3. **Two-byte characters, the e+ way.** [ACreTeam/afe-decomp](https://github.com/ACreTeam/afe-decomp) (Dōbutsu no Mori e+, CC0) adds kanji to this same font code with a parallel "wide" path (`src/game/m_font_wide.c_inc`: `mFontW_*`, `mFont_SetLineStringsW`). Characters are 16-bit: top byte 0 is an ordinary character or control code; any other top byte is a wide character, drawn from a separate 256-glyph texture bank, indexed by the bottom byte. e+ has one such bank. Chinese needs 2,670 characters, so use **11 banks**: top byte = bank 1–11, bottom byte = glyph in it.
4. **Convert on the player's machine.** `convert.py` (to do): pack the 2,670 glyphs the script uses from the iQue font into 11 bank textures of 256, and re-encode each iQue message into e+'s 16-bit form (iQue glyph `(second << 7 | (first & 0x7F)) + 128` → bank and slot; control codes kept with top byte 0). Then port e+'s wide path, choosing among 11 banks instead of one. Message drawing is in `src/game/m_msg_draw_font.c_inc`.
5. **Control codes.** The iQue text uses the same control codes as this game (`0x7F` + code, sizes from ac-decomp's `mFont_cont_info_tbl`), so `{player_name}` and the like should carry over. Check the codes the GameCube added.

## Try the converter

```
python chinese/convert.py "path/to/Dongwu Senlin (China).z64"
```
