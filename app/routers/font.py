import os
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/generate-font")
async def generate_font(
    images: List[UploadFile] = File(...),  
):
    ttf_path = os.path.join("sample_ttf", "test.ttf")
    if not os.path.exists(ttf_path):
        raise HTTPException(status_code=500, detail="TTF 파일을 찾을 수 없습니다.")

    return FileResponse(
        path=ttf_path,
        media_type="application/octet-stream",
        filename="test.ttf",
    )
