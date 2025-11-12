import urllib.request
import json
import os
from fontTools.ttLib import TTFont

# -----------------------------
# Configuration
# -----------------------------
OUTPUT_DIR = r"E:\Fonts\arabic_fonts_filtered"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Arabic Noto font IDs
arabic_ids = [
    "noto-sans-arabic",
    "noto-naskh-arabic",
    "noto-kufi-arabic"
]

#arabic_ids = [
#    "noto-sans-arabic",
#    "noto-sans-arabic-ui",
#    "noto-naskh-arabic",
#    "noto-naskh-arabic-ui",
#    "noto-kufi-arabic"
#]

BASE_URL = "https://gwfh.mranftl.com/api/fonts/"

# Unicode ranges to check (covers full Arabic + basic Latin)
TARGET_RANGE_STR = (
    "0x0020-0x007D,"  # Latin (omit tilde)
    "0x0600-0x06FF,"  # Arabic
    "0x0750-0x077F,"  # Arabic Supplement
    "0x08A0-0x08FF"   # Arabic Extended-A
)

#TARGET_RANGE_STR = (
#    "0x0020-0x007D,"   # Latin (omit tilde)
#    "0x0600-0x06FF,"   # Arabic
#    "0x0750-0x077F,"   # Arabic Supplement
#    "0x08A0-0x08FF"   # Arabic Extended-A
#    "0xFB50-0xFDFF,"   # Presentation A
#    "0xFE70-0xFEFF"    # Presentation B
#)

# Allow up to N missing codepoints (e.g. 5)
MISSING_TOLERANCE = 5

# -----------------------------
# Helper Functions
# -----------------------------

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
    """Convert '0x0600-0x06FF,0x0750-0x077F' to list of (start, end) ints."""
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


def font_missing_from_target(font_ranges, target_ranges):
    """Return missing codepoints (set difference)."""
    font_points = flatten_ranges(font_ranges)
    local_target_points = flatten_ranges(target_ranges)
    return local_target_points - font_points


# -----------------------------
# Main Script
# -----------------------------

target_ranges = parse_range_str(TARGET_RANGE_STR)
target_points = flatten_ranges(target_ranges)

for fid in arabic_ids:
    print(f"Processing {fid} …")
    url = f"{BASE_URL}{fid}?subsets=arabic"

    try:
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"  Failed to get info for {fid}: {e}")
        continue

    for variant in data.get('variants', []):
        ttf_url = variant.get('ttf')
        if not ttf_url:
            continue

        fname = f"{fid}-{variant['id']}.ttf"
        fpath = os.path.join(OUTPUT_DIR, fname)
        print(f"  Downloading {fname} …")

        try:
            urllib.request.urlretrieve(ttf_url, fpath)
        except Exception as e:
            print(f"    Failed download {fname}: {e}")
            continue

        # Check Unicode coverage
        font_ranges = get_unicode_ranges(fpath)
        missing = font_missing_from_target(font_ranges, target_ranges)

        if len(missing) == 0:
            print(f"    ✅ Full coverage of target range")
        elif len(missing) <= MISSING_TOLERANCE:
            print(f"    ⚠️ Missing {len(missing)} codepoints (tolerated)")
        else:
            print(f"    ❌ Missing {len(missing)} codepoints → removing")
            os.remove(fpath)

print("Done — filtered fonts saved in:", OUTPUT_DIR)
