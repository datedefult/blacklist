
from pydoc import describe
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel

app05 = APIRouter()


# 公共的查询参数函数
async def common_parameters(
        q: Optional[str] = None,
        page: int = 1,
        limit: int = 10
):
    return {"q": q, "page": page, "limit": limit}

# 依赖注入示例
@app05.get("/dependency01")
async def dependency01(commons: dict = Depends(common_parameters)):
    return commons


@app05.get("/dependency02")
def dependency02(commons: dict = Depends(common_parameters)):
    return commons

# 类依赖项
fake_items_db=[{"item_name":"Foo"},{"item_name":"Bar"},{"item_name":"Baz"}]

class CommonQueryParams:
    def __init__(self,
                 q: Optional[str] = None,
                 page: int = 1,
                 limit: int = 10
                 ):
        self.q = q
        self.page = page
        self.limit = limit

@app05.get("/class_as_dependencies")
# 等效写法
async def class_as_dependencies(commons: CommonQueryParams = Depends(CommonQueryParams)):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.page:commons.page + commons.limit]
    response.update({"items": items})
    return response
# async def class_as_dependencies2(commons: CommonQueryParams = Depends()):
#     return commons
# async def class_as_dependencies3(commons = Depends(CommonQueryParams)):
#     return commons


# 子依赖
def query_(q:Optional[str]=None):
    return q

def sub_query_(q:Optional[str]=Depends(query_),
               last_query:Optional[str]=None,
               ):
    if not q:
        return last_query
    return q

@app05.get("/sub_dependency")
async def sub_dependency(
        final_query:str = Depends(sub_query_,use_cache=True),
):
    return {"sub_dependency": final_query}

# 路径操作依赖：路径操作装饰器
async def verify_token(x_toke:str=Header(...)):
    """ 没有返回值的子依赖 """
    if x_toke!='fake-super-secret-token':
        raise HTTPException(status_code=401,detail='x_toke invalid')
    return x_toke

async def verify_key(x_key:str=Header(...)):
    """ 有返回值，但返回值不会被调用 """
    if x_key!='fake-super-secret-token':
        raise HTTPException(status_code=401,detail='x_key invalid')
    return x_key

@app05.get("/dependency_in_path_operation",dependencies=[Depends(verify_token),Depends(verify_key)])
async def dependency_in_path_operation():
    return [{"user":"user01"},{"user":"user02"}]


# 全局依赖
# app05= APIRouter(dependencies=[Depends(verify_token),Depends(verify_key)])

# 带yield的依赖
async def get_db():
    db = 'db_connection'
    try:
        yield db
    finally:
        db.endswith('db_close')


async def dependency_a():
    dep_a = 'generate_dep_a()'
    try:
        yield dep_a
    finally:
        dep_a.endswith('db_close')

async def dependency_b(dep_a=Depends(dependency_a)):
    dep_b = 'generate_dep_b()'
    try:
        yield dep_b
    finally:
        dep_b.endswith(dep_a)

async def dependency_c(dep_b=Depends(dependency_a)):
    dep_c = 'generate_dep_c()'
    try:
        yield dep_c
    finally:
        dep_c.endswith(dep_b)