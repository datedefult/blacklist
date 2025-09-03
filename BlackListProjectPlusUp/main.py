from connections import TORTOISE_ORM


from fastapi import FastAPI
from contextlib import asynccontextmanager
from tortoise.contrib.fastapi import register_tortoise
from BlackListProjectPlusUp.middle import log_requests_middleware
from BlackListProjectPlusUp.api import black_category, black_user, black_exclusion

def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # 启动阶段：注册数据库
        register_tortoise(
            app,
            config=TORTOISE_ORM,
            generate_schemas=True,  # 开发阶段使用
            # add_exception_handlers=True,
        )
        yield

    app = FastAPI(
        title='黑名单接口',
        description='黑名单任务接口，支持黑名单种类的操作，白名单用户操作，黑名单用户操作',
        lifespan=lifespan,
        version='1.0.0',
        docs_url='/docs',
        redoc_url='/redocs',
    )

    app.middleware("http")(log_requests_middleware)

    app.include_router(black_category, prefix='/blacklist/category', tags=['黑名单种类'])
    app.include_router(black_user, prefix='/blacklist/user', tags=['黑名单用户'])
    app.include_router(black_exclusion, prefix='/blacklist/exclusion', tags=['白名单用户'])

    return app
