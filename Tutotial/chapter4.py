

from typing import Optional, Union, List

from fastapi import APIRouter, status, Form, File, UploadFile, HTTPException
from pydantic import BaseModel,EmailStr
from sqlalchemy import True_

app04 = APIRouter()

# 响应模型
class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    mobile: str ='10086'
    address: str=None
    full_name: Optional[str]=None

class UserOut(BaseModel):
    username: str
    email: EmailStr
    mobile: str ='10086'
    address: str=None
    full_name: Optional[str]=None


users = {
    "user01":{
        'username': 'Tom',
        'password': 'www123',
        'email': 'user01@ads.com',
        'mobile': '1534747',
        'address': 'uhbhjv',
        'full_name': None

    },
    "user02": {
        'username': 'Jerry',
        'password': '15115qwe',
        'email': 'user02@jett.com',
        'mobile': '1534747',
        'address': 'uhbhjv',
        'full_name': None
    },
}

# 路径操作
@app04.post('/response_model',response_model=UserOut,response_model_exclude_unset=True)
async def response_model(user:UserIn):
    print(user.username)
    return users['user01']

@app04.post('/response_model/attributes',
            # response_model=UserOut,
            # response_model=Union[UserOut,UserOut],


            response_model = List[UserOut],
            # # 列出需要返回的
            # response_model_include=['filed1','filed2','filed3'],
            # # 列出不需要返回的
            # response_model_exclude=['filed1', 'filed2', 'filed3']

            )
async def response_model_attributes(user:UserIn):
    print(user.username)
    del user.password
    return [user,user]

# 响应状态码
@app04.post('/status_code',status_code=status.HTTP_200_OK)
async def status_attr():
    print(type(status.HTTP_200_OK))
    return status.HTTP_200_OK

# 表单数据处理
@app04.put('/login',status_code=status.HTTP_200_OK)
async def login(
        user:str=Form(...),
        password:str = Form(...)
                ):
    return {'username':user,'password':password}

# 单文件多文件上传
@app04.post('/smallfiles',status_code=status.HTTP_200_OK)
async def small_file_(file:bytes = File(...)):
    """
    单小文件上传
    :param file:
    :return:
    """
    return {'file_size':len(file)}

@app04.post('/smallfiles',status_code=status.HTTP_200_OK)
async def small_files_(files:List[bytes] = File(...)):
    """
    多个小文件上传
    :param files:
    :return:
    """
    return {'file_size':len(files)}
@app04.post('/bigfile',status_code=status.HTTP_200_OK)
async def big_file_(file:UploadFile = File(...)):
    """
    单大文件上传
    :param file:
    :return:
    """
    content = await file.read()
    print(content)
    return {'filename':file.filename}

@app04.post('/bigfiles',status_code=status.HTTP_200_OK)
async def big_files_(files:List[UploadFile] = File(...)):
    """
    多大文件上传
    :param files:
    :return:
    """
    for file in files:
        content = await file.read()
        print(content)
    return {'filename':files[0].filename,'content_type':files[0].content_type}

# 路径操作配置
@app04.post(
    "/path_operation_configuration",
    response_model=UserOut,
    # tags=["Path","Operation","Configuration"],
    summary="This is a test summary",
    description="This is a test description",
    response_description="This is a test response_description",
    # 是否废弃
    deprecated=True,
    status_code=status.HTTP_200_OK,
)
async def path_operation_configuration(user:UserIn):
    """
    Path Operation Configuration 路径操作配置演示
    :param user: 用户信息，pydantic
    :return: 返回结果字典
    """

    return user.dict()


# 常见错误处理
@app04.get('/http_exception')
async def http_exception(city:str):
    if city!='Shanghai':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='City not found!',headers={'X-Error': 'Error'})
    return {'city':city}

@app04.get('/http_exception/{city_id}')
async def override_http_exception(city_id:int):
    if city_id==1:
        raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT,detail='dasdihi!',headers={'X-Error': 'Error'})
    return {'city_id':city_id}

