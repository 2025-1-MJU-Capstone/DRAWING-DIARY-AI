"""
inference_batch_avg.py
----------------------
Batch inference script for MX-Font using the average of reference glyph images as the style input.

Usage:
    python inference_batch_avg.py --weight /home/ahnwooseob/mxfont/generator.pth --result_dir /home/ahnwooseob/mxfont/generated_glyphs /home/ahnwooseob/mxfont/cfgs/eval.yaml
"""

import argparse
import os
from pathlib import Path

import torch
from PIL import Image
import numpy as np

from sconf import Config
from utils import save_tensor_to_image
from models import Generator

def load_image_tensor(path, size=(128,128)):
    """Load an image from path, convert to grayscale, resize to size, and normalize to [0,1]."""
    img = Image.open(path).convert("L")
    if img.size != size:
        img = img.resize(size, Image.LANCZOS)
    img_array = np.array(img, dtype=np.float32) / 255.0
    tensor = torch.tensor(img_array).unsqueeze(0).unsqueeze(0)  # (1,1,H,W)
    return tensor

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_paths", nargs="+", help="Path(s) to config.yaml")
    parser.add_argument("--weight", required=True, help="Path to weight file (generator.pth)")
    parser.add_argument("--result_dir", required=True, help="Directory to save generated images")
    args, left_argv = parser.parse_known_args()

    cfg = Config(*args.config_paths, default="cfgs/defaults.yaml")
    cfg.argv_update(left_argv)

    result_dir = Path(args.result_dir)
    result_dir.mkdir(parents=True, exist_ok=True)

    # 경로 설정 (고정)
    source_dir = "/home/ahnwooseob/mxfont/source_glyphs"              # 모든 Source Glyphs (PNG, 128x128, 흑백)
    reference_dir = "/home/ahnwooseob/mxfont/reference_images_resized"  # Reference Glyphs (내 손글씨, PNG, 128x128, 흑백)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 모델 파라미터: eval.yaml와 defaults.yaml에 정의된 g_args 사용 (cfg.C, g_args)
    g_kwargs = cfg.get("g_args", {})
    # Generator 초기화: 기존 inference.ipynb와 동일하게.
    gen = Generator(1, cfg.C, 1, **g_kwargs).to(device)
    weight = torch.load(args.weight, map_location=device)
    if "generator_ema" in weight:
        weight = weight["generator_ema"]
    gen.load_state_dict(weight)
    gen.eval()

    # ======== 1. Reference Glyphs: 평균 스타일 이미지 계산 ============
    ref_files = sorted([f for f in os.listdir(reference_dir) if f.endswith(".png")])
    ref_tensors = []
    for fname in ref_files:
        ref_path = os.path.join(reference_dir, fname)
        tensor = load_image_tensor(ref_path).to(device)  # (1,1,128,128)
        ref_tensors.append(tensor)
    # Concatenate: (N,1,128,128)
    ref_stack = torch.cat(ref_tensors, dim=0)
    # 평균 내기 → (1,1,128,128)
    avg_style_img = ref_stack.mean(dim=0, keepdim=True)
    # (선택 사항) 만약 약간의 noise가 있다면 thresholding으로 완전 binary화 할 수도 있음.
    # avg_style_img = (avg_style_img > 0.5).float()

    # ======== 2. Source Glyphs Batch Inference ============
    source_files = sorted([f for f in os.listdir(source_dir) if f.endswith(".png")])
    total = len(source_files)
    print(f"총 {total}개의 Source Glyphs 처리 시작...")
    for idx, fname in enumerate(source_files):
        src_path = os.path.join(source_dir, fname)
        src_tensor = load_image_tensor(src_path).to(device)  # (1,1,128,128)

        with torch.no_grad():
            # 여기서 평균 스타일 이미지를 reference로 사용하여 생성.
            # 기존 eval_ckpt.py에서는 gen.gen_from_style_char(style_imgs, char_imgs)를 사용하지만,
            # 여기서는 style_imgs를 avg_style_img로 대체합니다.
            out = gen.gen_from_style_char(avg_style_img, src_tensor)  # out: (1,1,128,128)

        out_path = result_dir / fname
        save_tensor_to_image(out, out_path)

        if (idx + 1) % 100 == 0:
            print(f"{idx + 1}/{total} 글리프 생성 완료")

    print("✅ 전체 Source Glyphs 배치 추론 완료!")

if __name__ == "__main__":
    main()
