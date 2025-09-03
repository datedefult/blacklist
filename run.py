from urllib.request import Request

from fastapi import FastAPI
import uvicorn


from starlette.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from BlackListProject import black_category,black_user,black_exclusion
from Coronavirus import application
from Tutotial import app03, app04, app05, app06,app07
from connections import TORTOISE_ORM
app = FastAPI(
    title='黑名单接口',
    description='黑名单任务接口支持，支持黑名单种类的操作，白名单用户操作 ，黑名单用户操作',
    version='1.1.0',
    docs_url='/docs',
    redoc_url='/redocs',
    # dependencies=[Depends(verify_token),Depends(verify_key)]
)


register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # 如果数据库为空，则自动生成对应表单，生产环境不要开
    add_exception_handlers=True,  # 生产环境不要开，会泄露调试信息
)

# 静态文件挂载
app.mount(path='/static', app=StaticFiles(directory='./Coronavirus/static'), name='static')


# from fastapi.responses import PlainTextResponse
# from fastapi.exceptions import RequestValidationError,HTTPException
# # 重新异常处理类
# @app.exception_handler(HTTPException)
# async def exception_handler(request: Request, exc: HTTPException):
#     """
#
#     :param request: 参数不能省略
#     :param exc:
#     :return:
#     """
#
#     return PlainTextResponse(str(exc.detail), status_code=exc.status_code)
#
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     """
#
#     :param request:
#     :param exc:
#     :return:
#     """
#     return PlainTextResponse(str(exc.errors), status_code=400)




app.include_router(app03, prefix='/app03',tags=['app03 请求参数校验'])
app.include_router(app04, prefix='/app04',tags=['app04 响应处理和FastAPI配置'])
app.include_router(app05, prefix='/app05',tags=['app05 FastAPI依赖注入系统'])
app.include_router(app06, prefix='/app06',tags=['app06 安全认证和授权'])
app.include_router(app07, prefix='/app07',tags=['app07 FastAPI的数据库操作和多应用的目录结构设计'])
app.include_router(application, prefix='/application',tags=['数据库操作api'])

app.include_router(black_category,prefix='/blacklist/category',tags=['黑名单种类'])
app.include_router(black_user,prefix='/blacklist/user',tags=['黑名单用户'])
app.include_router(black_exclusion,prefix='/blacklist/exclusion',tags=['白名单用户'])

if __name__ == '__main__':
    uvicorn.run('run:app', host='0.0.0.0', port=8000, reload=True,workers=2)

