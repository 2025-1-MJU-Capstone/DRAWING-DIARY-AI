from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
from app.routers.font  import router as font_router
from app.routers.image import router as image_router

app.include_router(image_router)
app.include_router(font_router)
class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}
