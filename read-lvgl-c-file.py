#!/usr/bin/env python3
"""
Read LVGL C font file (lv_font_conv output) and extract the actual Unicode codepoints
by parsing the unicode_list arrays and the cmaps table. Print count and characters.
"""

import re
import sys
import os
import argparse
from itertools import chain

HEX_RE = re.compile(r"0x[0-9A-Fa-f]+")

def parse_unicode_list_arrays(content):
    """
    Find unicode_list_N arrays and return dict name -> [ints].
    Handles uint16_t, uint32_t, static const, etc.
    Example match:
      static const uint16_t unicode_list_0[] = { 0x0, 0x1, 0x41, ... };
    """
    arr_re = re.compile(
        r"(?:static\s+)?(?:const\s+)?(?:uint(?:16|32)_t|int|uint32_t|uint16_t)\s+"
        r"(?P<name>unicode_list_\d+)\s*\[\s*\]\s*=\s*\{(?P<body>.*?)\};",
        re.DOTALL,
    )
    arrays = {}
    for m in arr_re.finditer(content):
        name = m.group("name")
        body = m.group("body")
        hexes = HEX_RE.findall(body)
        values = [int(h, 16) for h in hexes]
        arrays[name] = values
    return arrays

def find_cmaps_blocks(content):
    """
    Find the cmaps array block. It may look like:
    static const lv_font_fmt_txt_cmap_t cmaps[] = {
      {
        .range_start = 32, .range_length = 95, .glyph_id_start = 1
      }, { ... }
    };
    Return list of blocks (strings) for each cmap entry.
    """
    # find the whole cmaps array
    cmaps_array_re = re.compile(
        r"(?s)static\s+const\s+[^{;]*lv_font_fmt_txt_cmap_t\s+cmaps\s*\[\s*\]\s*=\s*\{(?P<body>.*?)\};"
    )
    m = cmaps_array_re.search(content)
    if not m:
        # fallback: find any variable named cmaps
        # try to find 'cmaps[] = { ... };' without type
        cmaps_array_re2 = re.compile(r"(?s)\bcmaps\s*\[\s*\]\s*=\s*\{(?P<body>.*?)\};")
        m = cmaps_array_re2.search(content)
    if not m:
        return []

    body = m.group("body")
    # split top-level '{...},' entries (rudimentary)
    entries = []
    depth = 0
    cur = []
    for ch in body:
        cur.append(ch)
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                # collect full block
                entries.append(''.join(cur))
                cur = []
    # Clean entries
    cleaned = [e.strip().strip(',') for e in entries if e.strip()]
    return cleaned

def parse_cmap_entry(block):
    """
    Parse fields from one cmap block and return a dict with keys:
    range_start (int), range_length (int), glyph_id_start (int),
    unicode_list (str or None), list_length (int or None), type (str or None)
    Works with patterns like '.range_start = 32', '.unicode_list = unicode_list_0'
    """
    result = {
        "range_start": None,
        "range_length": None,
        "glyph_id_start": None,
        "unicode_list": None,
        "list_length": None,
        "type": None,
    }
    # find numeric assignments
    kv_re = re.compile(r"\.(?P<key>[a-zA-Z0-9_]+)\s*=\s*(?P<val>[^,}\n]+)")
    for m in kv_re.finditer(block):
        k = m.group("key").strip()
        v = m.group("val").strip().rstrip(',')
        # clean v
        # if v is a name like unicode_list_0
        if k == "unicode_list":
            name_match = re.search(r"(unicode_list_\d+)", v)
            if name_match:
                result["unicode_list"] = name_match.group(1)
            else:
                result["unicode_list"] = None
            continue
        if k == "type":
            # type may be LV_FONT_FMT_TXT_CMAP_FORMAT0_TINY or similar
            t = v.split()[-1]
            result["type"] = t.strip()
            continue
        # integers: could be hex or decimal
        num_match = re.search(r"0x[0-9A-Fa-f]+|\d+", v)
        if num_match:
            num = int(num_match.group(0), 0)
            if k in result:
                result[k] = num
            else:
                # ignore other keys
                result[k] = num
    return result

def extract_codepoints_from_cmaps(content):
    """
    Return set of actual Unicode codepoints present in the font, by parsing cmaps and unicode_list arrays.
    """
    arrays = parse_unicode_list_arrays(content)
    cmap_blocks = find_cmaps_blocks(content)
    codepoints = set()

    for block in cmap_blocks:
        info = parse_cmap_entry(block)
        rs = info.get("range_start")
        rl = info.get("range_length")
        ulist_name = info.get("unicode_list")
        # If there's a unicode_list, values are offsets from range_start
        if rs is None:
            continue
        if ulist_name and ulist_name in arrays:
            offsets = arrays[ulist_name]
            for off in offsets:
                codepoints.add(rs + int(off))
        else:
            # otherwise add the full dense range
            if rl is None:
                # try to guess range_length from other patterns (rare)
                # fallback: if glyph_id_start present and block contains a pattern .range_length = N, etc.
                continue
            for cp in range(rs, rs + rl):
                codepoints.add(cp)
    return codepoints

def try_extract_unicode_from_other_patterns(content):
    """
    Extra fallback: some lv_font_conv versions emit 'unicode_list' arrays
    with names or emit lists inline. This tries to find other arrays like
    'static const uint16_t unicode_list_0[] = {...};' that we missed.
    We'll just gather all hex literals in the file that are >= 0x80 to avoid ASCII-only captures.
    """
    all_hex = HEX_RE.findall(content)
    ints = [int(h,16) for h in all_hex]
    # keep codepoints above 0x7F to avoid ASCII noise
    return set(i for i in ints if i >= 0x80)

def parse_font_file(path, show_chars=True, limit=None):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Try robust extraction via cmaps and unicode_list arrays
    cps = extract_codepoints_from_cmaps(content)

    # If we got nothing (or suspiciously small), fallback to broader scanning
    if len(cps) < 256:
        # gather additional likely codepoints (but avoid ascii-only results)
        fallback = try_extract_unicode_from_other_patterns(content)
        cps |= fallback

    cps = sorted(cps)
    # Prepare printable characters
    chars = []
    for cp in cps:
        try:
            ch = chr(cp)
            # We consider printable any that Python reports printable or CJK/Arabic categories
            # but avoid control chars
            if not ch.isspace():
                chars.append((cp, ch))
            else:
                # keep spaces and newlines as visible tokens optionally
                chars.append((cp, ch))
        except:
            continue

    # Optionally limit number of chars to print
    if limit is not None and len(chars) > limit:
        chars_to_print = chars[:limit]
    else:
        chars_to_print = chars

    return {
        "codepoints": cps,
        "char_tuples": chars_to_print,
        "total_codepoints": len(cps),
    }

def print_report(path, show_chars=True, limit=None):
    res = parse_font_file(path, show_chars=show_chars, limit=limit)
    print(f"\nFile: {os.path.basename(path)}")
    print(f"  Codepoints found: {res['total_codepoints']}")
    if show_chars:
        print("\n Characters (codepoint -> glyph):")
        for cp, ch in res['char_tuples']:
            # print hex and character; for safety, escape if non-printable
            try:
                if ch.isprintable():
                    print(f"  0x{cp:04X} -> {ch}")
                else:
                    # show representative name
                    print(f"  0x{cp:04X} -> (non-printable)")
            except:
                print(f"  0x{cp:04X} -> (error printing)")

def main():
    parser = argparse.ArgumentParser(description="Parse LVGL .c font file and print included Unicode codepoints and characters.")
    parser.add_argument("file", help="path to lvgl generated C file")
    parser.add_argument("--no-chars", action="store_true", help="don't print character list")
    parser.add_argument("--limit", type=int, default=200, help="limit number of characters printed (default 200)")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print("File not found:", args.file)
        sys.exit(1)

    print_report(args.file, show_chars=not args.no_chars, limit=args.limit)

if __name__ == "__main__":
    main()
