import base64
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.openai_api_key)
router = APIRouter(prefix="/ai", tags=["ai"])

class ImageRequest(BaseModel):
    feeling: str
    color: str
    title: str
    content: str
    diaryDate: str
    customStyle: str
    model: str = "gpt-4.1-mini"

@router.post("/generate-image")
async def generate_image(req: ImageRequest):
    prompt = f"""
[역할]
당신은 사용자의 일기를 보고 이에 맞는 그림을 그리는 일러스트레이터입니다.
날짜와 일기 제목, 일기 내용을 보고 이에 맞는 그림을 그려야 합니다.

[파라미터]
- feeling: {req.feeling}
- color: {req.color}
- custom: {req.customStyle}
- 제목(title): {req.title}
- 내용(content): {req.content}
- 날짜(diaryDate): {req.diaryDate}

[가이드]
…(생략)…
"""

    try:
        # OpenAI 호출을 threadpool에서 비동기 실행
        response = await run_in_threadpool(
            client.responses.create,
            model=req.model,
            input=prompt,
            tools=[{"type": "image_generation"}],
        )

        # image_generation_call 타입의 결과 중 첫 번째 Base64 문자열 추출
        image_b64 = next(
            (out.result for out in response.output if out.type == "image_generation_call"),
            None
        )

        if not image_b64:
            raise HTTPException(status_code=502, detail="이미지 데이터를 반환받지 못했습니다.")

        # JSON으로 { "base64_ttf": "<인코딩된 문자열>" } 반환
        return JSONResponse(content={"base64_ttf": image_b64})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
