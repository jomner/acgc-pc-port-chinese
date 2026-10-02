# Animal Crossing PC Port · 中文

**Animal Crossing (GameCube) on PC, with its dialogue in Chinese.**

The Chinese is the game's own official translation: **动物森林 (Dòngwù Sēnlín)**, released in 2006 for the iQue Player, China's version of the Nintendo 64. That release was the N64 original, Animal Forest; this project carries its text into the GameCube game, running on [flyngmt's PC port](https://github.com/flyngmt/ACGC-PC-Port).

> **Work in progress.** Nothing is playable in Chinese yet. See [Progress](#progress).

## What you need

- Your own **Animal Crossing (USA)** GameCube disc image, as for the PC port itself.
- Your own **Dongwu Senlin** iQue ROM (decrypted `.z64`).
- Python 3, to convert the ROM once.

No game text, font or image is in this repository. The Chinese is made on your machine, from your copy.

## How it works

1. `python chinese/convert.py <your Dongwu Senlin ROM>` reads the Chinese script and font out of your ROM and writes them to `chinese/out/`.
2. When the game starts, it loads those files. Any message listed in `chinese/message-map.json` is shown in its Chinese version instead.
3. Each Chinese character is a small code in the text that tells the game to draw that glyph from one of 11 Chinese glyph sheets, through the game's own text drawing, so speech sounds, colours and pauses keep working.

Without `chinese/out/`, the game runs exactly as the PC port does.

## Progress

- [x] Read the Chinese script and font from the iQue ROM ([dongwu-senlin-text](https://github.com/jomner/dongwu-senlin-text))
- [x] Convert them into a form the port can use
- [x] Load them at startup, swap in mapped messages, draw the glyphs
- [x] Build: compiles cleanly with MSYS2 MINGW32 and loads all 11,791 messages and 11 glyph banks at startup (run with `--verbose` to see the `[ZH]` line)
- [ ] Match the first messages: Tom Nook's welcome and one villager conversation
- [ ] Match messages automatically, through the Japanese versions of both games

The GameCube game has far more text than the N64 original (the island, NES games, new characters), so text the iQue release never had will stay in English.

## Building

Build as the PC port: see [its instructions](docs/PC-PORT-README.md). Then run the converter once and keep `chinese/out/` beside the game.

## Credits

- [flyngmt/ACGC-PC-Port](https://github.com/flyngmt/ACGC-PC-Port): the PC port this is built on (its own README is kept at [docs/PC-PORT-README.md](docs/PC-PORT-README.md)).
- [ACreTeam/ac-decomp](https://github.com/ACreTeam/ac-decomp), the GameCube decompilation underneath it; [ACreTeam/afe-decomp](https://github.com/ACreTeam/afe-decomp), whose kanji support showed the way.
- iQue's 2006 Chinese localization of Animal Forest.

Licensed as the PC port is: see [LICENSE](LICENSE). Animal Crossing and Dòngwù Sēnlín © Nintendo / iQue. An unofficial fan project, not affiliated with either.
