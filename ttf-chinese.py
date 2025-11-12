import os
from fontTools.ttLib import TTFont
from shutil import copy2

# -----------------------------
# Configuration
# -----------------------------

# Folder containing your downloaded Chinese TTF files
CHINESE_INPUT_DIR = r"E:\Fonts\chinese_fonts"
# Folder where filtered fonts will be copied
CHINESE_OUTPUT_DIR = r"E:\Fonts\chinese_fonts_filtered"
os.makedirs(CHINESE_OUTPUT_DIR, exist_ok=True)

# Unicode ranges for Chinese (common + compatibility)
CHINESE_RANGE_STR = "0x3400-0x4DBF,0x4E00-0x9FFF,0xF900-0xFAFF"

# Allow for missing codepoints since many fonts are subsets
MISSING_TOLERANCE = 5000  # Adjust for your use case

# -----------------------------
# Helper Functions
# -----------------------------

def get_unicode_ranges(ttf_path):
    """Return a list of (start, end) tuples representing codepoints in the font."""
    try:
        font = TTFont(ttf_path)
        cmap = font["cmap"].getBestCmap()
        points = sorted(cmap.keys())
        font.close()
    except Exception as e:
        print(f"Error reading {ttf_path}: {e}")
        return []

    if not points:
        return []

    ranges = []
    start = prev = points[0]
    for cp in points[1:]:
        if cp != prev + 1:
            ranges.append((start, prev))
            start = cp
        prev = cp
    ranges.append((start, prev))
    return ranges

def parse_range_str(range_str):
    ranges = []
    for part in range_str.split(","):
        if "-" in part:
            a, b = part.split("-")
            ranges.append((int(a,16), int(b,16)))
        else:
            v = int(part,16)
            ranges.append((v,v))
    return ranges

def flatten_ranges(ranges):
    s = set()
    for a,b in ranges:
        s.update(range(a,b+1))
    return s

def font_missing_from_target(font_ranges, target_ranges):
    font_points = flatten_ranges(font_ranges)
    target_points = flatten_ranges(target_ranges)
    return target_points - font_points

# -----------------------------
# Main Filtering Function
# -----------------------------

def filter_chinese_fonts(input_dir, output_dir, target_range_str, tolerance):
    target_ranges = parse_range_str(target_range_str)

    for file in os.listdir(input_dir):
        if file.lower().endswith(".ttf"):
            path = os.path.join(input_dir, file)
            font_ranges = get_unicode_ranges(path)
            missing = font_missing_from_target(font_ranges, target_ranges)

            if len(missing) == 0:
                print(f"{file} ✅ Full coverage")
            elif len(missing) <= tolerance:
                print(f"{file} ⚠️ Missing {len(missing)} codepoints (tolerated)")
            else:
                print(f"{file} ⚠️ Missing {len(missing)} codepoints (subset font)")

            # Copy all fonts regardless of missing codepoints
            copy2(path, os.path.join(output_dir, file))

# -----------------------------
# Run
# -----------------------------

filter_chinese_fonts(CHINESE_INPUT_DIR, CHINESE_OUTPUT_DIR, CHINESE_RANGE_STR, MISSING_TOLERANCE)

print("All done — filtered fonts saved in:", CHINESE_OUTPUT_DIR)
