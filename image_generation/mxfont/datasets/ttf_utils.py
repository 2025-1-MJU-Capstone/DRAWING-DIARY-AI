"""
MX-Font
Copyright (c) 2021-present NAVER Corp.
MIT license
"""

from fontTools.ttLib import TTFont
from PIL import Image, ImageFont, ImageDraw
import numpy as np


def get_defined_chars(fontfile):
    ttf = TTFont(fontfile)
    chars = [chr(y) for y in ttf["cmap"].tables[0].cmap.keys()]
    return chars


def get_filtered_chars(fontpath):
    ttf = read_font(fontpath)
    defined_chars = get_defined_chars(fontpath)
    avail_chars = []

    for char in defined_chars:
        img = np.array(render(ttf, char))
        if img.mean() == 255.:
            pass
        else:
            avail_chars.append(char.encode('utf-16', 'surrogatepass').decode('utf-16'))

    return avail_chars


def read_font(fontfile, size=150):
    font = ImageFont.truetype(str(fontfile), size=size)
    return font

# Pillow 버전문제로 수정
# def render(font, char, size=(128, 128), pad=20):
#     width, height = font.getsize(char)
#     max_size = max(width, height)

#     if width < height:
#         start_w = (height - width) // 2 + pad
#         start_h = pad
#     else:
#         start_w = pad
#         start_h = (width - height) // 2 + pad

#     img = Image.new("L", (max_size+(pad*2), max_size+(pad*2)), 255)
#     draw = ImageDraw.Draw(img)
#     draw.text((start_w, start_h), char, font=font)
#     img = img.resize(size, 2)
#     return img



# 그나마 잘 나옴
# from PIL import Image, ImageDraw, ImageFont

# def render(font, char, size=(128, 128), pad=20):
#     # 기존 코드에서 getsize() → getmask().size 로 대체
#     mask = font.getmask(char)
#     width, height = mask.size
#     max_size = max(width, height)

#     # 기존 코드 로직 유지
#     if width < height:
#         start_w = (height - width) // 2 + pad
#         start_h = pad
#     else:
#         start_w = pad
#         start_h = (width - height) // 2 + pad

#     # (max_size + pad*2) 크기의 임시 이미지에 그리기
#     img = Image.new("L", (max_size + pad*2, max_size + pad*2), 255)
#     draw = ImageDraw.Draw(img)
#     # 글자 채우기(검정색)
#     draw.text((start_w, start_h), char, font=font, fill=0)

#     # 마지막에 원하는 사이즈로 리사이즈
#     # Pillow 9.1 이상이면 Image.Resampling.BILINEAR 쓰는 게 좋음
#     img = img.resize(size, Image.Resampling.BILINEAR)

#     return img



from PIL import Image, ImageDraw, ImageFont

def render(font, char, size=(256, 256), pad=20):
    # 정확한 경계 박스 계산
    bbox = font.getbbox(char)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    max_size = max(width, height)

    # 중심 정렬 계산
    if width < height:
        start_w = (height - width) // 2 + pad
        start_h = pad
    else:
        start_w = pad
        start_h = (width - height) // 2 + pad

    # 흰 배경 이미지 생성
    img = Image.new("L", (max_size + pad*2, max_size + pad*2), 255)
    draw = ImageDraw.Draw(img)

    # bbox 기준으로 위치 보정해서 그리기
    draw.text((start_w - bbox[0], start_h - bbox[1]), char, font=font, fill=0)

    # 최종 사이즈로 리사이즈
    img = img.resize(size, Image.Resampling.BILINEAR)

    return img
