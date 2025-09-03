import json
import os
import time

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi_cache.backends.redis import RedisBackend
from starlette.responses import RedirectResponse
from tortoise.contrib.fastapi import register_tortoise
import redis.asyncio as redis
from BlackListProjectPlusUp import black_category, black_user, black_exclusion
from BlackListProjectPlusUp.middle import log_requests_middleware

from connections import TORTOISE_ORM3
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

load_dotenv('.env')

from utils.LogsColor import setup_logger
# 接管日志
logging = setup_logger(level=os.getenv("APP_LOG_LEVEL", "info").upper())

def get_dependencies():
    """ 根据环境变量生成动态验证依赖列表 """
    deps = []

    if os.getenv("ENABLE_IP_VERIFY", "false").lower() == "true":
        from utils.Verify import verify_ip
        deps.append(Depends(verify_ip))
        logging.info("Authentication enabled: IP Verification")

    if os.getenv("ENABLE_TOKEN_VERIFY", "false").lower() == "true":
        from utils.Verify import verify_token
        deps.append(Depends(verify_token))
        logging.info("Authentication enabled: Token Authentication")

    if os.getenv("ENABLE_KEY_VERIFY", "false").lower() == "true":
        from utils.Verify import verify_key
        deps.append(Depends(verify_key))
        logging.info("Authentication enabled: Key Validation")

    return deps or None  # 返回None表示无认证


app = FastAPI(
        title='黑名单接口',
        description="""
测试版本黑名单任务接口支持，支持黑名单种类的操作，白名单用户操作，黑名单用户操作
```
target_id: 1-uid, 2-设备，3-IP，4-电话，5-邮箱
```
"""
        ,
        version='2.0.0',
        docs_url='/docs',
        redoc_url='/redocs',
        # dependencies=[Depends(verify_token), Depends(verify_key)]
        dependencies=get_dependencies(),
)

# 添加中间件
app.middleware("http")(log_requests_middleware)

# @app.on_event("startup")
# async def startup():
#     # 初始化缓存：开发阶段使用内存缓存，生产建议用 Redis
#     # FastAPICache.init(InMemoryBackend(), prefix="blacklist")
#     r = redis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
#     FastAPICache.init(RedisBackend(r), prefix="blacklist-cache")


register_tortoise(
        app,
        config=TORTOISE_ORM3,
        # generate_schemas=True,  # 如果数据库为空，则自动生成对应表单，生产环境不要开
        # add_exception_handlers=True,  # 生产环境不要开
)

app.include_router(black_category, prefix='/blacklist/category', tags=['黑名单种类'])
app.include_router(black_user, prefix='/blacklist/user', tags=['黑名单用户'])
app.include_router(black_exclusion, prefix='/blacklist/exclusion', tags=['白名单用户'])

if __name__ == '__main__':
    uvicorn.run('black_tasks_run_plusup:app', host='0.0.0.0', port=8000, reload=True, workers=1)
