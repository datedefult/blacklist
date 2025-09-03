import os

from fastapi import APIRouter, Depends, HTTPException, Header
from starlette.requests import Request


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

async def verify_ip(request: Request):
    """
    IP白名单验证依赖项
    使用方式：在路由中添加 dependencies=[Depends(verify_ip)]
    """
    # 获取客户端IP
    client_ip = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.client.host
    )

    # 从环境变量加载白名单
    allowed_ips = os.getenv("ALLOWED_IPS", "").split(",")

    if client_ip not in allowed_ips:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied for IP: {client_ip}"
        )
    return client_ip