from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Path, Query, Depends,Cookie,Header
from enum import Enum
from datetime import date
app03 = APIRouter()


@app03.get("/path/parameters")
def path_param01():
    return {'message': 'This is a message 03'}


@app03.get("/path/{parameters}")
def path_param01(parameters: str):
    return {'message': parameters}


class CityName(str, Enum):
    Beijing = 'Beijing China'
    Shanghai = 'Shanghai China'


@app03.get("/enum/{city}")
async def latest(city: CityName):
    if city == CityName.Beijing:
        return {'city_name': city, 'confirmed': 119, 'death': 8}

    elif city == CityName.Shanghai:
        return {'city_name': city, 'confirmed': 12, 'death': 8}

    else:
        return {'city_name': city, 'latest': 'Unknown'}


# 传递文件路径
@app03.get("/file/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


@app03.get('/check/{num}')
def path_parameters(
        num: int = Path(..., title='Your number', ge=1, le=10)
):
    return {'num': num}


# 分页查询
@app03.get('/query')
def page_limit(page: int = 1, limit: Optional[int] = None):
    if limit:
        return {'page': page, 'limit': limit}
    return {'page': page}


# bool类型转化
@app03.get('/query/bool/conversion')
def type_conversion(par: bool = False):
    return {'par': par}


@app03.get('/query/validation')
def query_param_validation(
        value: str = Query(..., min_length=1, max_length=100, regex='^[a-zA-Z0-9]+$'),

        values: List[str] = Query(['V1', 'V2'], alias='alias_name'),
):
    return {'value': value, 'values': values}


# 请求体 混合参数
class CityInfo(BaseModel):
    name: str = Field(..., examples=['Beijing', 'Shanghai'])
    country: str = Field(..., examples=['China', 'United Kingdom'])
    country_code: str = Field(..., examples=['Beijing', 'Shanghai'])
    country_population: int = Field(default=800, ge=800, title='Country Population', description='国家人口')

    class Config:
        schema_extra = {
            'example': {
                "name": "Beijing",
                "country": "China",
                "country_code": 'CN',
                "country_population": 800,

            }
        }


@app03.get('/request_body/city')
def city_info(city: CityInfo):
    return city.model_dump_json()


@app03.put('/request_body/country')
def mix_city_info(
        name: str,
        city01: CityInfo,
        city02: CityInfo,
        confirmed: int = Query(default=0, ge=0, description='Confirmed Cases'),
        death: int = Query(default=0, ge=0, description='Death Cases'),

):
    if name == "Shanghai":
        return {"Shanghai": {'confirmed': confirmed, 'death': death}}
    return city01.dict(), city02.dict()


# 定义请求体
class Data(BaseModel):
    city:List[CityInfo]=None # 嵌套请求体定义
    date:date
    confirmed:int = Field(default=0, ge=0, description='Confirmed Cases')
    death:int = Field(default=0, ge=0, description='Death Cases')
    recovered:int = Field(default=0, ge=0, description='Recovered Cases')


@app03.put('/request_body/nested')
def nested_models(data: Data):
    return data

@app03.get('/cookie')
def cookie(cookie_id:Optional[str] = Cookie(None)):
    return {'cookie_id': cookie_id}

@app03.get('/header')
def header(
        user_agent:Optional[str] = Header(None,convert_underscores=True),
        x_token:List[str] = Header(None,convert_underscores=True),
           ):
    #
    """
    convert_underscores：将user_agent转化为user-agent
    :param user_agent:
    :param x_token:
    :return:
    """
    return {'user_agent': user_agent, 'x_token': x_token}