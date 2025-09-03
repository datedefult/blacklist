# cache_utils.py

from typing import Callable, Optional, Awaitable, Union, Any, Tuple, Dict
from fastapi import Request, Response
from fastapi_cache import FastAPICache

# ========= user 缓存 KeyBuilder =========
async def get_user_cache_key(
    func: Callable,
    namespace: Optional[str],
    request: Request,
    response: Optional[Response],
    *args: Tuple[Any, ...],
    **kwargs: Dict[str, Any],
) -> str:
    params = kwargs.get("params") or kwargs  # 获取 Pydantic 参数对象或字典
    if "target_id" in params:
        return (
            f"user:query:target_id={params.get('target_id')}:target_value={params.get('target_value')}:"
            f"category_id={params.get('category_id')}:classification={params.get('classification')}:"
            f"offset={params.get('offset')}:limit={params.get('limit')}"
        )
    else:
        return (
            f"user:check:target_id={params.get('target_id')}:target_value={params.get('target_value')}:"
            f"category_id={params.get('category_id')}"
        )


async def clear_user_cache(target_id=None, target_value=None, category_id=None):
    pattern = "user:*"
    if target_id:
        pattern += f"*:target_id={target_id}:*"
    if target_value:
        pattern += f"*:target_value={target_value}:*"
    if category_id:
        pattern += f"*:category_id={category_id}:*"
    await FastAPICache.clear(namespace=pattern)


# ========= category 缓存 KeyBuilder =========
async def get_category_cache_key(
    func: Callable,
    namespace: Optional[str],
    request: Request,
    response: Optional[Response],
    *args: Tuple[Any, ...],
    **kwargs: Dict[str, Any],
) -> str:
    params = kwargs.get("params") or kwargs
    return (
        f"category:{params.get('id')}:{params.get('name')}:"
        f"{params.get('classification')}"
    )


async def clear_category_cache(category_id=None, classification=None):
    pattern = "category:*"
    if category_id:
        pattern += f"*:id={category_id}:*"
    if classification:
        pattern += f"*:classification={classification}:*"
    await FastAPICache.clear(namespace=pattern)


# ========= exclusion 缓存 KeyBuilder =========
async def get_exclusion_cache_key(
    func: Callable,
    namespace: Optional[str],
    request: Request,
    response: Optional[Response],
    *args: Tuple[Any, ...],
    **kwargs: Dict[str, Any],
) -> str:
    params = kwargs.get("params") or kwargs
    return (
        f"exclusion:{params.get('target_id')}:{params.get('target_value')}:"
        f"{params.get('level')}"
    )


async def clear_exclusion_cache(target_id=None, target_value=None, level=None):
    pattern = "exclusion:*"
    if target_id:
        pattern += f"*:target_id={target_id}:*"
    if target_value:
        pattern += f"*:target_value={target_value}:*"
    if level:
        pattern += f"*:level={level}:*"
    await FastAPICache.clear(namespace=pattern)
