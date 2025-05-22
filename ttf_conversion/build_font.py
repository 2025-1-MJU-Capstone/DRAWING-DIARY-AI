import os
import fontforge

BASE_DIR = "/mnt/c/Users/82102/Desktop/my_font"
PNG_DIR = PNG_DIR = os.path.join(BASE_DIR, "reference_images_resized")
SVG_DIR = os.path.join(BASE_DIR, "svgs")
TTF_PATH = os.path.join(BASE_DIR, "MyKoreanFont.ttf")

# SVG 폴더 생성
os.makedirs(SVG_DIR, exist_ok=True)

# Step 1: PNG → SVG (벡터화)
for file in os.listdir(PNG_DIR):
    if file.endswith(".png"):
        name = os.path.splitext(file)[0]
        input_png = os.path.join(PNG_DIR, file)
        output_svg = os.path.join(SVG_DIR, f"{name}.svg")
        
        os.system(f'convert "{input_png}" -threshold 50% temp.pbm')
        os.system(f'potrace temp.pbm -s -o "{output_svg}"')
        print(f"✅ {file} → {name}.svg")

if os.path.exists("temp.pbm"):
    os.remove("temp.pbm")

# Step 2: SVG → TTF
font = fontforge.font()
font.encoding = 'UnicodeFull'


font.fontname = "MyKoreanFont"
font.familyname = "MyKoreanFont"
font.fullname = "MyKoreanFont"

for file in os.listdir(SVG_DIR):
    if file.endswith(".svg"):
        char = os.path.splitext(file)[0]
        codepoint = ord(char)
        svg_path = os.path.join(SVG_DIR, file)

        glyph = font.createChar(codepoint)
        glyph.importOutlines(svg_path)
        glyph.autoHint()
        print(f"🧩 Inserted {char} at U+{codepoint:04X}")

font.generate(TTF_PATH)
print(f"\n🎉 폰트 생성 완료: {TTF_PATH}")
