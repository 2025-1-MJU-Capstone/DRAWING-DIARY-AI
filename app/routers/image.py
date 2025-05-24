import io
import base64
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
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
1. custom은 사용자가 추가적으로 희망하는 그림 스타일입니다. custom parameter가 있는 경우 해당 내용을 우선적으로 반영해야 합니다.
2. 사용자 시점에서의 그림이 아닌 3인칭 관찰자 시점에서 확인할 수 있을 것 같은 그림을 그려야합니다.
3. 사용자가 원하는 그림의 느낌을 아래처럼 설명합니다. feeling parameter를 받으면 아래 가이드에서 해당하는 가이드를 반영해주세요
    1. realistic: 실제사진같은 현실적인 분위기. 선명하면서도 사진과 비슷한 결과가 나오는 그림을 그립니다.
    2. cinematic: 영화같은 격동적인 분위기. 정적인 일기에서는 차분하면서도 강렬한 그림을, 동적인 일기에서는 역동적이면서 화려한 그림을 그립니다.
    3. storybook: 동화처럼 아기자기한 분위기. 지브리스타일의 그림이나 짱구 스타일의 그림처럼 어린 아이가 좋아할 것 같은 그림을 그립니다.
4. 사용자가 원하는 그림의 색감을 아래처럼 설명합니다. color parameter를 받으면 아래 가이드에서 해당하는 가이드를 반영해주세요.
    1. crayon:  색연필과 크레파스로 그린 그림
    2. paint: 물감으로 그린 그림. 수채화 물감으로 그린 느낌을 의미합니다.
    3. pencil: 연필로 그린 그림. 흑백으로 그린 그림이자 연필의 질감을 잘 표현해야합니다.
5.  일기 내용을 충실히 따라야 합니다. 일기 내용에서 사용자가 강하게 표현한 부분을 찾아 이를 묘사해야합니다. 그림을 그리기 전 일기 내용을 꼼꼼히 확인하고 중요한 키워드를 찾아내서 이를 묘사해주세요.
6. 일기 내용과 무관한 배경이나 소품은 피해주세요. 그림에 텍스트가 들어가지 않도록 해주세요. 만약 사용자가 텍스트가 들어가길 희망하는 경우 최대한 짧게 텍스트를 작성해주시고, 한글이 깨지지 않도록 주의해주세요.

"""

    try:
        response = await run_in_threadpool(
            client.responses.create,
            model=req.model,
            input=prompt,
            tools=[{"type": "image_generation"}],
        )

        image_data = [
            out.result
            for out in response.output
            if out.type == "image_generation_call"
        ]
        if not image_data:
            raise HTTPException(502, "이미지 데이터를 반환받지 못했습니다.")

        image_bytes = base64.b64decode(image_data[0])
        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))