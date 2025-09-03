from typing import List, Union, Optional

from fastapi import APIRouter, status, Depends, Request
from fastapi.encoders import jsonable_encoder
from tortoise.transactions import in_transaction
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

from BlackListProjectPlusUp.models import BlacklistUserExclusion, BlacklistCategory, BlacklistUser
from BlackListProjectPlusUp.schemas import CreateBlacklistExclusion, ReadBlacklistExclusion, CreationResult, DeleteResult, \
    BlacklistExclusionQueryParams, DeleteBlacklistExclusion
from utils.BaseResponse import success_response, error_response, GeneralResponse
import json

black_exclusion = APIRouter()


@black_exclusion.get('/', response_model=GeneralResponse[List[ReadBlacklistExclusion]], response_model_exclude_unset=True)
@cache(expire=60)  # 删除 key_builder 参数
async def query_exclusions(params: BlacklistExclusionQueryParams = Depends(), request: Request = None):
    """
    统一白名单查询接口

    支持多种查询方式：
    - 无参数: 查询所有白名单记录
    - 仅target_id/target_value: 查询指定目标的白名单记录
    - 仅category_id: 查询指定分类的白名单记录
    - target_id/target_value + category_id: 查询指定目标在指定分类的白名单记录

    请求示例：
    - 查询所有: GET /
    - 查询指定目标: GET /?target_id=1&target_value=xxx
    - 查询指定分类: GET /?category_id=1
    - 查询指定目标和分类: GET /?target_id=1&target_value=xxx&category_id=1
    - 分页查询：GET /?offset=10&limit=20

    返回结果：
    - 返回符合条件的白名单记录列表
    - 如果无记录，返回错误信息
    """
    try:
        # 构建基础查询
        query = BlacklistUserExclusion

        # 添加过滤条件
        if params.target_id is not None:
            query = query.filter(target_id=params.target_id,target_value=params.target_value)
        if params.category_id is not None:
            # 检查分类是否存在
            if not await BlacklistCategory.filter(id=params.category_id).exists():
                return error_response(message=f"Category ID {params.category_id} does not exist", code=status.HTTP_404_NOT_FOUND)
            query = query.filter(category_id=params.category_id)

        # 检查是否存在符合条件的记录
        if not await query.exists():
            error_msg = "No exclusion records found"
            if params.target_id and params.target_value and params.category_id:
                error_msg = f"User {params.target_id,params.target_value} has no exclusions in category {params.category_id}"
            elif params.target_id and params.target_value:
                error_msg = f"User {params.target_id, params.target_value} has no exclusion records"
            elif params.category_id:
                error_msg = f"No exclusions found for category {params.category_id}"

            return error_response(message=error_msg, code=status.HTTP_200_OK)

        # 执行查询
        result = await query.all().offset(params.offset).limit(params.limit)

        return success_response(message="Successfully retrieved exclusion data", data=jsonable_encoder(result),
            code=status.HTTP_200_OK)

    except Exception as e:
        return error_response(message=f"Exclusion query failed: {str(e)}",code=status.HTTP_400_BAD_REQUEST)


@black_exclusion.post('/', response_model=GeneralResponse)
async def create_exclusions(request: List[CreateBlacklistExclusion]):
    """
    批量创建白名单用户

    功能说明：
    1. 创建白名单时会自动从黑名单中移除对应记录
    2. 支持多级别清理规则（通过level字段控制）：
       - level=3（默认）：仅删除相同category_id的黑名单记录
       - level=2：删除同classification下所有category的黑名单记录
       - level=1：删除该target的所有黑名单记录
    3. 支持单条和批量创建

    请求参数：
    - target_id: 目标类型（如1-uid, 2-设备等，必填）
    - target_value: 目标值（如uid号、设备号等，必填）
    - category_id: 分类ID（必填）
    - describe: 描述信息（可选）
    - level: 清理级别（可选，默认3）

    请求体示例：
    [
        {
            "target_id": 1,
            "target_value": "123",
            "category_id": 1,
            "describe": "测试用户",
            "level": 3
        }
    ]

    返回结果：
    {
        "code": 201,
        "message": "操作结果描述",
        "data": {
            "success_count": 成功数量,
            "failed_count": 失败数量,
            "skipped_count": 跳过数量,
            "skipped_items": [...],
            "failed_items": [...],
            "removed_from_blacklist": 清理的黑名单记录数
        }
    }

    错误处理：
    - 400：参数校验失败
    - 404：分类不存在
    - 500：服务器内部错误
    """
    result = CreationResult(success_count=0, failed_count=0, skipped_count=0, skipped_items=[], failed_items=[],
        removed_from_blacklist=0
    )

    try:
        async with in_transaction():
            for item in request:
                try:
                    # 设置默认level=3
                    level = item.level if item.level is not None else 3
                    item.target_value = str(item.target_value)

                    # 检查是否已存在相同记录
                    if await BlacklistUserExclusion.filter(
                            target_id=item.target_id,
                            target_value=item.target_value,
                            category_id=item.category_id).exists():
                        result.skipped_count += 1
                        result.skipped_items.append(item.dict())
                        continue

                    # 根据level清理黑名单
                    removed_count = await clean_blacklist_by_level(
                        target_id=item.target_id,
                        target_value=item.target_value,
                        category_id=item.category_id,
                        level=level
                    )
                    result.removed_from_blacklist += removed_count

                    # 创建白名单记录
                    await BlacklistUserExclusion.create(
                        target_id=item.target_id,
                        target_value=item.target_value,
                        category_id=item.category_id,
                        describe=item.describe,
                        level=level
                    )
                    result.success_count += 1

                except Exception as e:
                    result.failed_count += 1
                    result.failed_items.append({
                        "data": item.dict(),
                        "reason": str(e)
                    })

        response_data = result.dict()
        status_code = status.HTTP_207_MULTI_STATUS if result.failed_count > 0 else status.HTTP_201_CREATED

        await FastAPICache.clear(namespace="blacklist-cache")

        return success_response(
            message=f"Created {result.success_count} exclusions, removed {result.removed_from_blacklist} from blacklist",
            data=response_data,
            code=status_code
        )

    except Exception as e:
        return error_response(
            message=f"Batch creation failed: {str(e)}",
            code=status.HTTP_400_BAD_REQUEST
        )


async def clean_blacklist_by_level(target_id: int, target_value: str, category_id: int, level: int) -> int:
    """
    根据白名单级别清理黑名单

    逻辑说明：
    - level=1：删除该target的所有黑名单记录
    - level=2：删除同classification下所有category的该target黑名单记录
    - level=3（默认）：仅删除相同category的该target黑名单记录

    返回删除的记录数
    """
    if level == 1:
        # 删除该uid的所有黑名单记录
        return await BlacklistUser.filter(target_id=target_id,target_value=target_value).delete()

    elif level == 2:
        # 获取当前category的classification
        category = await BlacklistCategory.get(id=category_id)
        # 获取同classification的所有category_id
        category_ids = await BlacklistCategory.filter(
            classification=category.classification
        ).values_list('id', flat=True)
        # 删除这些category下的该uid记录
        return await BlacklistUser.filter(
            target_id=target_id,target_value=target_value,
            category_id__in=category_ids
        ).delete()

    else:  # level=3或未指定
        # 仅删除相同category的记录
        return await BlacklistUser.filter(
            target_id=target_id,target_value=target_value,
            category_id=category_id
        ).delete()

@black_exclusion.delete('/', response_model=GeneralResponse)
async def delete_exclusions(requests: Union[DeleteBlacklistExclusion, List[DeleteBlacklistExclusion]]):
    """
    统一删除白名单用户接口（支持单条和批量）

    支持多种删除方式：
    - 通过id删除
    - 通过target_id+target_value+category_id删除

    请求体示例：
    - 单条删除（通过ID）: {"id": 1}
    - 单条删除（通过target_id+target_value+category_id）: {"target_id": 1, "target_value": "xxx", "category_id": 1}
    - 批量删除: [
        {"id": 1},
        {"target_id": 1, "target_value": "xxx", "category_id": 1}
    ]

    返回结果：
    {
        "code": 200,
        "message": "Record deleted successfully",
        "data": {
            "success_count": 成功数量,
            "failed_count": 失败数量,
            "skipped_count": 跳过数量,
            "skipped_items": [...],
            "failed_items": [...],
            "deleted_items": [...]
        }
    }
    """
    # 统一转为列表处理
    request_list = [requests] if not isinstance(requests, list) else requests

    result = DeleteResult(success_count=0, failed_count=0, skipped_count=0, skipped_items=[], failed_items=[],
        deleted_items=[])

    try:
        async with in_transaction():
            for req in request_list:
                try:
                    req.target_value = str(req.target_value)
                    # 构建查询条件
                    query = BlacklistUserExclusion
                    if req.id is not None:
                        query = query.filter(id=req.id)
                    else:
                        if req.target_id is None or req.target_value is None or req.category_id is None:
                            raise ValueError("Must provide either id or both target_id, target_value and category_id")
                        query = query.filter(target_id=req.target_id,
                        target_value=req.target_value, category_id=req.category_id)

                    # 执行删除
                    exclusion = await query.first()
                    if not exclusion:
                        result.skipped_count += 1
                        result.skipped_items.append(req)
                        continue

                    await exclusion.delete()
                    result.success_count += 1
                    result.deleted_items.append(jsonable_encoder(ReadBlacklistExclusion.model_validate(exclusion)))

                except Exception as e:
                    result.failed_count += 1
                    result.failed_items.append({"request": req.dict(), "reason": str(e)})

        # 构造响应
        response_data = result.dict()
        if isinstance(requests, list):  # 批量请求
            if result.failed_count > 0:
                status_code = status.HTTP_207_MULTI_STATUS
                message = f"Batch delete completed with {result.failed_count} failures"
            else:
                status_code = status.HTTP_200_OK
                message = f"Successfully deleted {result.success_count} records"
        else:  # 单条请求
            if result.success_count > 0:
                status_code = status.HTTP_200_OK
                message = "Record deleted successfully"
            else:
                status_code = status.HTTP_404_NOT_FOUND
                message = "No matching record found"

        await FastAPICache.clear(namespace="blacklist-cache")

        return success_response(message=message, data=response_data, code=status_code)

    except Exception as e:
        return error_response(message=f"Delete operation failed: {str(e)}",
            code=status.HTTP_400_BAD_REQUEST)


@black_exclusion.put('/', response_model=GeneralResponse)
async def update_exclusions(request: CreateBlacklistExclusion):
    """
      更新白名单记录

      功能说明：
      1. 支持两种更新方式（优先级从高到低）：
         - 通过ID更新：{"id": 1, ...}
         - 通过target_id+target_value+category_id更新：{"target_id": 1, "target_value": "xxx", "category_id": 1, ...}

      2. 可更新字段：
         - describe：更新描述信息
         - level：更新级别并自动触发对应黑名单清理

      3. level更新规则：
         - level=None：仅更新描述，不清理黑名单
         - level=3：删除该目标在相同category下的黑名单记录
         - level=2：删除该目标在相同classification下的所有category记录
         - level=1：删除该目标所有黑名单记录

      请求示例：
      ```
      {
          "id": 1,                     // 必须提供id或target_id+target_value+category_id
          "describe": "新描述内容",     // 可选
          "level": 2                   // 可选，修改后会触发对应清理
      }
      ```
      返回结果：
      ```
      {
          "code": 200,                 // 状态码
          "message": "操作结果描述",     // 包含清理记录数信息
          "data": {
              "updated_record": {      // 更新后的记录详情
                  "id": 1,
                  "target_id": 1,
                  "target_value": "xxx",
                  "category_id": 1,
                  "level": 2,
                  "describe": "新描述内容",
                  "create_time": "2023-01-01T00:00:00"
              },
              "removed_from_blacklist": 3  // 本次操作清理的黑名单记录数
          }
      }
      ```
      典型场景：
      1. 修改描述（不改变level）：
         - 请求：{"id": 1, "describe": "更新描述"}
         - 响应：message="更新成功"

      2. 提升level（3→1）：
         - 请求：{"target_id": 1, "target_value": "xxx", "category_id": 1, "level": 1}
         - 响应：message="更新成功，并清理了N条黑名单记录"

      错误处理：
      - 400：参数缺失（未提供id或target_id+target_value+category_id）
      - 404：记录不存在
      - 500：服务器内部错误
      """
    try:
        # 参数校验
        if request.id is None and (request.target_id is None or request.target_value is None or request.category_id is None):
            return error_response(message="Invalid parameters. Must provide either id or both target_id, target_value and category_id",
                                  code=status.HTTP_400_BAD_REQUEST)


        # 获取记录（包含预加载category）
        query = BlacklistUserExclusion.all().prefetch_related('category')
        if request.id is not None:
            exclusion = await query.filter(id=request.id).first()
        else:
            request.target_value = str(request.target_value)
            exclusion = await query.filter(
                target_id=request.target_id,
                target_value=request.target_value,
                category_id=request.category_id
            ).first()

        if not exclusion:
            return error_response(message="Record not found",
                                  code=status.HTTP_404_NOT_FOUND)
        # 判断是否需要清理黑名单
        old_level = exclusion.level if exclusion.level is not None else 3
        new_level = request.level if request.level is not None else old_level
        need_clean = (request.level is not None) and (new_level != old_level)

        # 准备更新数据
        update_data = {}
        if request.describe is not None:
            update_data['describe'] = request.describe
        if request.level is not None:
            update_data['level'] = request.level

        async with in_transaction():
            # 执行黑名单清理
            removed_count = 0
            if need_clean:
                removed_count = await clean_blacklist_by_level(
                    target_id=exclusion.target_id,
                    target_value=exclusion.target_value,
                    category_id=exclusion.category_id,
                    level=new_level
                )

            # 更新白名单记录
            if update_data:
                await BlacklistUserExclusion.filter(id=exclusion.id).update(**update_data)
                exclusion = await BlacklistUserExclusion.get(id=exclusion.id)

        return success_response(
            message=f"Update successful{' and cleaned ' + str(removed_count) + ' blacklist records' if need_clean else ''}",
            data={
                "updated_record": jsonable_encoder(exclusion),
                "removed_from_blacklist": removed_count
            }
        )

    except Exception as e:
        return error_response(
            message=f"Update error: {str(e)}",
            code=status.HTTP_400_BAD_REQUEST
        )