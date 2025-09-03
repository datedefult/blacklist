from fastapi import Request, Response
import json
import time
from typing import Callable, Any


from BlackListProjectPlusUp.models import RequestLog

async def iterate_in_chunks(data: bytes, chunk_size: int = 4096):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


# ✅ 提取客户端 IP（支持 X-Forwarded-For）
def get_client_ip(request: Request) -> str:

    # 处理多层代理的情况
    if "x-forwarded-for" in request.headers:
        forwarded_ips = [
            ip.strip()
            for ip in request.headers["x-forwarded-for"].split(",")
            if ip.strip() and not ip.startswith(("10.", "192.168.", "172."))  # 过滤内网IP
        ]
        if forwarded_ips:
            return forwarded_ips[0]

    # 检查其他常见代理头
    proxy_headers = [
        "x-real-ip",
        "cf-connecting-ip",
        "fastly-client-ip",
        "x-client-ip"
    ]
    for header in proxy_headers:
        if header in request.headers:
            return request.headers[header]

    # 最终回退
    return request.client.host if request.client else "unknown"
# def get_client_ip(request: Request) -> str:
#     x_forwarded_for = request.headers.get("x-forwarded-for")
#     if x_forwarded_for:
#         return x_forwarded_for.split(",")[0].strip()
#     if request.client:
#         return request.client.host
#     return "unknown"


# ✅ 中间件主函数，针对请求以及响应结果进行记录
async def log_requests_middleware(request: Request, call_next: Callable) -> Response:
    start_time = time.time()
    request_body = None
    body_bytes = b""

    # 处理请求体
    content_type = request.headers.get("content-type", "")
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        if "multipart/form-data" in content_type:
            request_body = "<文件上传>"
        else:
            try:
                body_bytes = await request.body()
                request_body = body_bytes.decode("utf-8", errors="replace")
            except Exception as e:
                request_body = f"<请求体错误: {str(e)}>"
    else:
        body_bytes = b""

    # 重构 request 流，确保业务仍可读取
    async def receive_gen():
        yield {"type": "http.request", "body": body_bytes, "more_body": False}
    request._receive = receive_gen().__anext__

    try:
        response = await call_next(request)

        # 读取响应体内容
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        # 重建 body_iterator
        response.body_iterator = iterate_in_chunks(response_body)

        # 解析响应体
        response_content_type = response.headers.get("content-type", "")
        if "application/octet-stream" in response_content_type:
            response_content = "<二进制数据>"
        else:
            try:
                response_content = response_body.decode("utf-8", errors="replace")
            except Exception as e:
                response_content = f"<响应体错误: {str(e)}>"
    except Exception as e:
        response_content = f"<服务器错误: {str(e)}>"
        response = Response(content=response_content, status_code=500)

    # 写入日志
    try:
        await RequestLog.create(
            method=request.method,
            path=request.url.path,
            request_body=request_body,
            request_params=dict(request.query_params),
            request_headers=dict(request.headers),
            response_content=response_content,
            response_headers=dict(response.headers),
            status_code=response.status_code,
            duration=(time.time() - start_time) * 1000,
            client_ip=get_client_ip(request),
        )
    except Exception as log_error:
        print(f"[日志写入失败] {log_error}")

    return response
