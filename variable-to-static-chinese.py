

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
import shutil

src_font = r"E:\Fonts\chinese_fonts\NotoSansSC-VariableFont_wght.ttf"
out_dir = r"E:\Fonts\chinese_fonts_filtered"

# --- Regular 400 ---
vf = TTFont(src_font)
static_regular = instancer.instantiateVariableFont(vf, {"wght": 400})  # do NOT use inplace=True
static_regular.save(out_dir + r"\NotoSansSC-Regular.ttf")
vf.close()

# --- Semibold 600 ---
vf = TTFont(src_font)
static_semibold = instancer.instantiateVariableFont(vf, {"wght": 600})
static_semibold.save(out_dir + r"\NotoSansSC-Semibold.ttf")
vf.close()

print("Done!")










# from fontTools.ttLib import TTFont
# from fontTools.varLib import instancer
#
# # Load variable font
# var_font = TTFont(r"E:\Fonts\chinese_fonts\NotoSansSC-VariableFont_wght.ttf")
#
# # Extract Regular weight (400)
# instancer.instantiateVariableFont(var_font, {"wght": 400}, inplace=True)
# var_font.save(r"E:\Fonts\chinese_fonts_filtered\NotoSansSC-Regular.ttf")
#
# # Reload variable font
# var_font = TTFont(r"E:\Fonts\chinese_fonts\NotoSansSC-VariableFont_wght.ttf")
#
# # Extract Semibold/Medium weight (600)
# instancer.instantiateVariableFont(var_font, {"wght": 600}, inplace=True)
# var_font.save(r"E:\Fonts\chinese_fonts_filtered\NotoSansSC-Semibold.ttf")
