from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum

# uvicorn fastapi_study:test_app --reload
test_app = FastAPI()

class CityInfo(BaseModel):
    """
    数据校验
    """
    province: str
    city: str
    # 可选传入
    is_affected: Optional[bool]=None

class ModelName(str, Enum):
    """
    可选项校验
    """
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@test_app.get("/")
async def hello_world():
    return {'hello':'hello world'}

@test_app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@test_app.get("/city/{city}")
async def result(city:str,query_string:Optional[str]=None):
    return {'city':city,'query_string':query_string}

@test_app.put("/city/{city}")
async def result(city:str,city_info:CityInfo):
    return {'city':city,'province':city_info.province,'is_affected':city_info.is_affected}