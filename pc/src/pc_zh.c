/* pc_zh.c - Chinese text from the player's own Dongwu Senlin (iQue) ROM; see pc_zh.h. */
#include "pc_zh.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define ZH_DIR "chinese/out/"

static uint8_t* zh_msg;
static uint32_t* zh_index;
static unsigned int zh_index_count;
static uint32_t* zh_map; /* pairs: GameCube message, iQue message */
static unsigned int zh_map_count;
static uint8_t* zh_banks;
static unsigned int zh_bank_count;
static int zh_active;

static uint8_t* zh_load(const char* name, unsigned int* size) {
    FILE* f = fopen(name, "rb");
    uint8_t* buf;
    long sz;

    if (f == NULL) {
        return NULL;
    }
    fseek(f, 0, SEEK_END);
    sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    buf = (uint8_t*)malloc(sz > 0 ? (size_t)sz : 1);
    if (buf != NULL && fread(buf, 1, (size_t)sz, f) != (size_t)sz) {
        free(buf);
        buf = NULL;
    }
    fclose(f);
    *size = (unsigned int)sz;
    return buf;
}

/* The files are little-endian, as convert.py writes them. */
static uint32_t zh_le32(const uint32_t* p) {
    const uint8_t* b = (const uint8_t*)p;
    return b[0] | (b[1] << 8) | (b[2] << 16) | ((uint32_t)b[3] << 24);
}

int pc_zh_init(void) {
    unsigned int msg_size, index_size, map_size, banks_size;

    zh_msg = zh_load(ZH_DIR "zh_msg.bin", &msg_size);
    zh_index = (uint32_t*)zh_load(ZH_DIR "zh_msg_index.bin", &index_size);
    zh_map = (uint32_t*)zh_load(ZH_DIR "zh_map.bin", &map_size);
    zh_banks = zh_load(ZH_DIR "zh_banks.bin", &banks_size);

    if (zh_msg == NULL || zh_index == NULL || zh_map == NULL || zh_banks == NULL) {
        fprintf(stderr, "[ZH] chinese/out/ not found: run chinese/convert.py on your Dongwu Senlin ROM\n");
        zh_active = 0;
        return 0;
    }
    zh_index_count = index_size / 4;
    zh_map_count = map_size / 8;
    zh_bank_count = banks_size / PC_ZH_BANK_SIZE;
    zh_active = 1;
    fprintf(stderr, "[ZH] %u messages, %u mapped, %u glyph banks\n", zh_index_count, zh_map_count, zh_bank_count);
    return 1;
}

int pc_zh_active(void) {
    return zh_active;
}

const unsigned char* pc_zh_message(int gc_no, unsigned int* size) {
    unsigned int i;

    if (!zh_active) {
        return NULL;
    }
    for (i = 0; i < zh_map_count; i++) {
        if (zh_le32(&zh_map[i * 2]) == (uint32_t)gc_no) {
            uint32_t iq = zh_le32(&zh_map[i * 2 + 1]);
            uint32_t start, end;

            if (iq >= zh_index_count) {
                return NULL;
            }
            start = iq == 0 ? 0 : zh_le32(&zh_index[iq - 1]);
            end = zh_le32(&zh_index[iq]);
            *size = end - start;
            return zh_msg + start;
        }
    }
    return NULL;
}

void pc_zh_log_message(int gc_no, const unsigned char* data, unsigned int size) {
    static int checked, logging;
    FILE* f;
    unsigned int i;

    if (!checked) {
        f = fopen("chinese/log-messages", "rb");
        logging = f != NULL;
        if (f != NULL) {
            fclose(f);
        }
        checked = 1;
    }
    if (!logging || (f = fopen("chinese/seen.txt", "a")) == NULL) {
        return;
    }
    fprintf(f, "%d\t", gc_no);
    for (i = 0; i < size; i++) {
        unsigned char c = data[i];

        if (c == 0x7F && i + 1 < size) { /* control code: show its number */
            fprintf(f, "{%02X}", data[i + 1]);
            i++;
        } else if (c == 0xCD) {
            fputc('/', f); /* new line */
        } else {
            fputc(c >= 0x20 && c < 0x7F ? c : '.', f);
        }
    }
    fputc('\n', f);
    fclose(f);
}

const unsigned char* pc_zh_bank(int bank) {
    if (!zh_active || bank < 1 || (unsigned int)bank > zh_bank_count) {
        return NULL;
    }
    return zh_banks + (bank - 1) * PC_ZH_BANK_SIZE;
}
