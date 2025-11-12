import os
from fontTools.ttLib import TTFont

def get_unicode_ranges(ttf_path):
    """Extract Unicode ranges from a TTF file as a list of (start, end) tuples."""
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
    """Convert something like '0x0600-0x06FF,0x0750-0x077F' to a list of (start, end) ints."""
    parts = range_str.split(",")
    ranges = []
    for p in parts:
        if "-" in p:
            a, b = p.split("-")
            ranges.append((int(a, 16), int(b, 16)))
        else:
            v = int(p, 16)
            ranges.append((v, v))
    return ranges


def flatten_ranges(ranges):
    """Return a set of all codepoints covered by the given ranges."""
    s = set()
    for a, b in ranges:
        s.update(range(a, b + 1))
    return s


def font_matches_range(font_ranges, target_ranges):
    """Check if the font exactly covers the same codepoints as the target ranges."""
    return flatten_ranges(font_ranges) == flatten_ranges(target_ranges)


def font_contains_range(font_ranges, target_ranges):
    """Check if the font covers all codepoints in the target ranges."""
    font_points = flatten_ranges(font_ranges)
    target_points = flatten_ranges(target_ranges)
    return target_points.issubset(font_points)


def find_fonts_matching_range(folder, target_range_str):
    target_ranges = parse_range_str(target_range_str)
    matching_fonts = []

    for file in os.listdir(folder):
        if file.lower().endswith(".ttf"):
            path = os.path.join(folder, file)
            font_ranges = get_unicode_ranges(path)
            missing = flatten_ranges(parse_range_str(target_range)) - flatten_ranges(font_ranges)
            if missing:
                print(f"Missing {len(missing)} codepoints:")
                print(", ".join(f"0x{cp:04X}" for cp in sorted(missing)))
            if font_contains_range(font_ranges, target_ranges):
                matching_fonts.append(file)

    return matching_fonts


if __name__ == "__main__":
    # --- Edit these ---
    folder = r"E:\Fonts\arabic_fonts"  # Folder containing TTF files
    target_range = "0x0020-0x007D,0x0600-0x06FF,0x0750-0x077F,0x08A0-0x08FF"  # Arabic ranges
#    target_range = "0x0600-0x06FF,0x0750-0x077F,0x08A0-0x08FF,0xFB50-0xFDFF,0xFE70-0xFEFF"  # Arabic ranges

    print(f"Looking for fonts in:\n  {folder}")
    print(f"Target Unicode range(s):\n  {target_range}")
    print("---------------------------------------------------")

    matches = find_fonts_matching_range(folder, target_range)
    if matches:
        print("Fonts that exactly match this Unicode range:")
        for m in matches:
            print(" -", m)
    else:
        print("No fonts exactly match the specified range.")