/* pc_zh.h - Chinese text from the player's own Dongwu Senlin (iQue) ROM.
 *
 * chinese/convert.py turns the player's ROM into chinese/out/; this loads it.
 * Without those files everything here stays off and the game is unchanged. */
#ifndef PC_ZH_H
#define PC_ZH_H

#define PC_ZH_GLYPH_CODE 0x7B /* control code: 7F 7B bank slot */
#define PC_ZH_GLYPH_CODE_SIZE 4
#define PC_ZH_BANK_SIZE (192 * 256 / 2) /* one I4 texture, laid out like the game's font */

/* Loads chinese/out/. Returns 1 when the Chinese text is available. */
int pc_zh_init(void);
int pc_zh_active(void);

/* The Chinese version of GameCube message gc_no, or NULL if it has none. */
const unsigned char* pc_zh_message(int gc_no, unsigned int* size);

/* Glyph bank (1-based), or NULL. */
const unsigned char* pc_zh_bank(int bank);

/* While chinese/log-messages exists, appends each message the game loads
 * (number and readable text) to chinese/seen.txt, for mapping messages. */
void pc_zh_log_message(int gc_no, const unsigned char* data, unsigned int size);

#endif
