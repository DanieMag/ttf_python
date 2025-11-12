from fontTools.ttLib import TTFont

# === CONFIGURATION ===
input_font = r"E:\Fonts\chinese_fonts_filtered\NotoSansSC-Regular.ttf"  # Chinese
max_glyphs_per_chunk = 256   # max glyphs per range
start_cp_filter = 0x4E00     # only include codepoints >= 0x4E00

# === LOAD FONT ===
font = TTFont(input_font)
cmap = font.getBestCmap()  # {unicode: glyph_name}

# sort codepoints and filter for Chinese characters
codepoints = sorted(cp for cp in cmap.keys() if cp >= start_cp_filter)

# list to store ranges
ranges_list = []

# === CALCULATE RANGES ===
for i in range(0, len(codepoints), max_glyphs_per_chunk):
    chunk = codepoints[i:i + max_glyphs_per_chunk]
    start_cp = chunk[0]
    end_cp = chunk[-1]
    ranges_list.append(f"0x{start_cp:04X}-0x{end_cp:04X}")

# === PRINT RANGES ===
all_ranges = ",".join(ranges_list)
print("Ranges for conversion (Chinese characters 0x4E00+):")
print(all_ranges)





# from fontTools.ttLib import TTFont
# import os
#
# # === CONFIGURATION ===
# input_font = r"E:\Fonts\chinese_fonts_filtered\NotoSansSC-Regular.ttf"   # your Chinese font file
# output_dir = r"E:\Fonts\chinese_split_fonts"
# start = 0x4E00
# end = 0x9FFF
# block_size = 0x0100  # each chunk is 256 codepoints
#
# os.makedirs(output_dir, exist_ok=True)
#
# # === LOAD FONT ===
# font = TTFont(input_font)
# cmap = font.getBestCmap()  # dictionary {unicode: glyph_name}
#
# # === SPLIT ===
# for block_start in range(start, end + 1, block_size):
#     block_end = min(block_start + block_size - 1, end)
#     block_glyphs = {
#         cp: name for cp, name in cmap.items()
#         if block_start <= cp <= block_end
#     }
#
#     if not block_glyphs:
#         continue  # skip empty ranges
#
#     # Create a copy of the font
#     new_font = TTFont(input_font)
#
#     # Keep only glyphs used in this block (plus mandatory ones)
#     keep_glyphs = set(block_glyphs.values())
#     #keep_glyphs.update([".notdef", ".null", "nonmarkingreturn"])
#     mandatory = [".notdef", ".null", "nonmarkingreturn"]
#     keep_glyphs.update(g for g in mandatory if g in font.getGlyphOrder())
#
#     all_glyphs = set(new_font.getGlyphOrder())
#     remove_glyphs = all_glyphs - keep_glyphs
#
#     # Remove unwanted glyphs
#     for glyph in remove_glyphs:
#         for table_tag in ("glyf", "hmtx", "hhea", "maxp", "cmap"):
#             if table_tag in new_font:
#                 table = new_font[table_tag]
#                 if table_tag == "cmap":
#                     # Remove unmapped codepoints
#                     for cmap_table in table.tables:
#                         cmap_table.cmap = {
#                             cp: g for cp, g in cmap_table.cmap.items()
#                             if g in keep_glyphs
#                         }
#                 elif hasattr(table, "glyphs") and glyph in table.glyphs:
#                     del table.glyphs[glyph]
#                 elif hasattr(table, "metrics") and glyph in table.metrics:
#                     del table.metrics[glyph]
#
#     # Update glyph order
#     new_font.setGlyphOrder(list(keep_glyphs))
#
#     # Save result
#     output_path = os.path.join(
#         output_dir,
#         f"font_{block_start:04X}_{block_end:04X}.ttf"
#
#     )
#     new_font.save(output_path)
#     print(f"Saved {output_path} ({len(block_glyphs)} glyphs)")
#