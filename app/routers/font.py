import os
import base64
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/generate-font")
async def generate_font(
    images: List[UploadFile] = File(...),
):
    # 1) TTF 파일 경로 확인
    ttf_path = os.path.join("sample_ttf", "test.ttf")
    if not os.path.exists(ttf_path):
        raise HTTPException(status_code=500, detail="TTF 파일을 찾을 수 없습니다.")

    # 2) 파일 읽어서 Base64 인코딩
    with open(ttf_path, "rb") as f:
        data = f.read()
    b64_str = base64.b64encode(data).decode("utf-8")

    # 3) JSON({ "base64_image": "<base64 문자열>" }) 으로 반환
    return JSONResponse(
        content={"base64_image": b64_str}
    )
