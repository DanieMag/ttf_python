import re

#font_c_file = r"E:\Fonts\chinese_fonts\lv_font_noto_sans_sc_16.c"

font_c_file = r"E:\Fonts\c\chinese-test.c"

# Match cmaps with range_start and range_length
cmap_re = re.compile(r"\.range_start\s*=\s*0x([0-9A-Fa-f]+),\s*\.range_length\s*=\s*(\d+)", re.MULTILINE)

codepoints = []

with open(font_c_file, "r", encoding="utf-8") as f:
    content = f.read()

for m in cmap_re.finditer(content):
    start = int(m.group(1), 16)
    length = int(m.group(2))
    codepoints.extend(range(start, start + length))

print(f"Number of codepoints in font: {len(codepoints)}")

# Print last 50 characters
last_50 = codepoints[-50:]
print("Last 50 characters in font:")
for cp in last_50:
    print(chr(cp), end=" ")

print("\nDone!")

