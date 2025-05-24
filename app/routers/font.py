import os
import base64
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Response

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/generate-font")
async def generate_font(
    images: List[UploadFile] = File(...),
):
    ttf_path = os.path.join("sample_ttf", "test.ttf")
    if not os.path.exists(ttf_path):
        raise HTTPException(status_code=500, detail="TTF 파일을 찾을 수 없습니다.")

    with open(ttf_path, "rb") as f:
        data = f.read()
    b64_str = base64.b64encode(data).decode("utf-8")

    return Response(
        content=b64_str,
        media_type="application/base64", 
    )
