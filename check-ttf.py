from fontTools.ttLib import TTFont

ttf_path = r"E:\Fonts\chinese_fonts_filtered\NotoSansSC-Regular.ttf"
font = TTFont(ttf_path)

cmap = font['cmap'].getBestCmap()
print(f"Number of codepoints in font: {len(cmap)}")

# Example: print first 20 Chinese codepoints
chinese_points = [cp for cp in cmap.keys() if cp >= 0x4E00]
print("Sample Chinese codepoints:", [hex(cp) for cp in chinese_points[:20]])

font.close()
