from fontTools.ttLib import TTFont

ttf_path = r"E:\Fonts\arabic_fonts_filtered\noto-sans-arabic-600.ttf"
#ttf_path = r"E:\Fonts\chinese_fonts_filtered\NotoSansSC-Regular.ttf"
# font = TTFont(ttf_path)
#
# cmap = font['cmap'].getBestCmap()
#
# # Filter Chinese codepoints (CJK Unified Ideographs)
# chinese_points = [cp for cp in cmap.keys() if cp >= 0x4E00]
#
# # Take the last 50 codepoints
# last_50 = sorted(chinese_points)[-50:]
#
# # Print the actual characters
# for cp in last_50:
#     print(chr(cp), end=' ')
#
# font.close()


#ttf_path = r"E:\Fonts\chinese_fonts_filtered\NotoSansSC-Regular.ttf"
font = TTFont(ttf_path)

cmap = font['cmap'].getBestCmap()

# Print first 50 Chinese characters
for cp in sorted([k for k in cmap if k >= 0x4E00])[:50]:
    print(chr(cp), end=' ')
