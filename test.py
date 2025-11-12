import re

# Load the C file
with open(r"E:\Fonts\c\arabic-test.c", "r", encoding="utf-8") as f:
    c_code = f.read()

# Regex to find each cmap block
cmap_pattern = re.compile(
    r"\{\s*\.range_start\s*=\s*(\d+),\s*\.range_length\s*=\s*(\d+),\s*\.glyph_id_start\s*=\s*(\d+),"
    r".*?\.list_length\s*=\s*(\d+),\s*\.type\s*=\s*([A-Z0-9_]+)\s*\}",
    re.DOTALL
)

cmaps = []

for match in cmap_pattern.finditer(c_code):
    range_start = int(match.group(1))
    range_length = int(match.group(2))
    glyph_id_start = int(match.group(3))
    list_length = int(match.group(4))
    cmap_type = match.group(5)

    cmaps.append({
        "range_start": range_start,
        "range_length": range_length,
        "glyph_id_start": glyph_id_start,
        "list_length": list_length,
        "type": cmap_type
    })

# Print results
for cmap in cmaps:
    print(f"range_start: 0x{cmap['range_start']:04X}")
    print(f"range_length: 0x{cmap['range_length']:04X}")
    print(f"glyph_id_start: 0x{cmap['glyph_id_start']:04X}")
    print(f"list_length: 0x{cmap['list_length']:04X}")
    print(f"type: {cmap['type']}")
    print("-" * 30)

    #print(cmap)
