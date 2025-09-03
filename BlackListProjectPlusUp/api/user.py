from typing import List, Union, Optional

from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from tortoise.exceptions import DBConnectionError

from tortoise.transactions import in_transaction
from BlackListProjectPlusUp.models import BlacklistUserExclusion, BlacklistUser, BlacklistCategory
from BlackListProjectPlusUp.schemas import *
from utils.BaseResponse import success_response, error_response, GeneralResponse


black_user = APIRouter()



@black_user.post('/', response_model=GeneralResponse)
async def create_blacklist_users(request: List[CreateBlacklistUser]):
    """
    批量创建黑名单用户

    功能说明：
    1. 支持批量创建黑名单用户记录
    2. 创建时会自动进行白名单校验：
       - level=3（默认）：仅校验相同category_id的白名单记录
       - level=2：校验相同classification下的所有category白名单记录，若IM相关的属于该级别及以上，则可以被所有品牌账号发推送
       - level=1：校验该target的所有白名单记录
    3. 如果记录已存在或存在于白名单中，则自动跳过

    请求参数：
    - target_id: 目标类型（如 1-uid, 2-设备，3-IP，4-电话，5-邮箱 等，必填）
    - target_value: 目标值（如uid号、设备号等，必填）
    - brand_id: 品牌账号（在category_id属于IM类别时，必填，默认为0）
    - category_id: 分类ID（必填）

    请求体示例：
    - 单条创建: [{"target_id": 1, "target_value": "123", "brand_id":0, "category_id": 1, "modify_user":152, describe:'可以不填'}]
    - 批量创建: [
        {"target_id": 1, "target_value": "123", "brand_id":1, "category_id": 1, "modify_user":152, describe:'可以不填'},
        {"target_id": 1, "target_value": "456", "brand_id":0, "category_id": 2, "modify_user":152}
      ]

    返回结果示例：
    {
        "code": 201,
        "message": "操作结果描述",
        "data": {
            "success_count": 成功数量,
            "failed_count": 失败数量,
            "skipped_count": 跳过数量,
            "skipped_items": [跳过的元素及原因],
            "failed_items": [失败元素及原因]
        }
    }

    错误处理：
    - 400：参数校验失败
    - 404：分类不存在
    - 500：服务器内部错误
    """
    result = CreationResult(success_count=0, failed_count=0, skipped_count=0, skipped_items=[], failed_items=[],
                            removed_from_blacklist=0)

    try:
        async with in_transaction():
            for item in request:
                try:
                    item.target_value = str(item.target_value)
                    # 获取当前category的classification
                    category = await BlacklistCategory.get_or_none(id=item.category_id)
                    if not category:
                        raise ValueError(f"Category {item.category_id} not found")

                    # 检查白名单（按level分级校验）
                    skip_reason = await check_exclusion_levels(item.target_id,item.target_value, item.category_id, category.classification)
                    if skip_reason:
                        result.skipped_count += 1
                        result.skipped_items.append({
                            "data": item.dict(),
                            "reason": skip_reason
                        })
                        continue

                    # 检查是否已存在于黑名单
                    if await BlacklistUser.filter(target_id=item.target_id,
                                                  target_value = item.target_value,
                                                  brand_id = item.brand_id,
                                                  category_id=item.category_id).exists():
                        result.skipped_count += 1
                        result.skipped_items.append({
                            "data": item.dict(),
                            "reason": "Already in blacklist"
                        })
                        continue

                    # 创建黑名单记录
                    await BlacklistUser.create(target_id=item.target_id,
                                               target_value = item.target_value,
                                               brand_id = item.brand_id,
                                               category_id=item.category_id,
                                               modify_user = item.modify_user,
                                               describe = item.describe,
                    )
                    result.success_count += 1


                except Exception as e:
                    result.failed_count += 1
                    result.failed_items.append({
                        "data": item.dict(),
                        "reason": str(e)
                    })

        response_data = {
            "success_count": result.success_count,
            "failed_count": result.failed_count,
            "skipped_count": result.skipped_count,
            "skipped_items": result.skipped_items,
            "failed_items": result.failed_items,
            "removed_from_blacklist": result.removed_from_blacklist
        }

        if result.failed_count > 0:
            return success_response(
                message=f"Batch create completed with {result.failed_count} failures",
                data=response_data,
                code=status.HTTP_207_MULTI_STATUS
            )
        return success_response(
            message="All records created successfully",
            data=response_data,
            code=status.HTTP_201_CREATED
        )

    except Exception as e:
        return error_response(
            message=f"Batch creation failed completely: {str(e)}",
            code=status.HTTP_400_BAD_REQUEST
        )


async def check_exclusion_levels(target_id: int, target_value: str, category_id: int, classification: int) -> Optional[str]:
    """
    检查白名单级别限制
    返回None表示可以通过，返回str表示跳过原因

    规则说明：
    - level=1：完全阻止该target的所有黑名单创建
    - level=2：阻止同classification下所有category的黑名单创建
    - level=3（默认）：仅阻止相同category的黑名单创建
    """
    # 获取所有该用户的白名单记录
    exclusions = await BlacklistUserExclusion.filter(target_id=target_id,target_value=target_value).prefetch_related('category')

    for exclusion in exclusions:
        # level=1：完全阻止
        if exclusion.level == 1:
            return f"UID blocked by level=1 exclusion (category_id={exclusion.category_id})"

        # level=2：同classification阻止
        if exclusion.level == 2:
            # 获取白名单记录的classification
            excl_classification = exclusion.category.classification
            if classification == excl_classification:
                return f"UID blocked by level=2 exclusion (same classification {classification})"

        # level=3：相同category阻止（默认）
        if (exclusion.level == 3 or exclusion.level is None) and exclusion.category_id == category_id:
            return f"UID blocked by level=3 exclusion (category_id={category_id})"

    return None


@black_user.get('/', response_model_exclude_unset=True)
async def query_blacklist_users(params: BlacklistUserQueryParams = Depends()):
    """
    统一黑名单查询接口

    支持以下查询方式：
    - 无参数: 查询所有黑名单记录
    - 仅target_id/target_value: 查询指定目标的黑名单记录
    - 仅category_id: 查询指定分类的黑名单记录
    - 仅classification: 查询指定分类的黑名单记录
    - target_id/target_value + category_id: 查询指定目标在指定分类的黑名单记录
    - target_id/target_value + classification: 查询指定目标在指定分类的黑名单记录
    - 分页查询：offset/limit

    返回结果示例：
    - 返回符合条件的黑名单记录列表
    - 如果无记录，返回404
    """
    try:
        # 1. 处理 classification 参数，获取对应的 category_ids
        category_ids = None
        if params.classification is not None:
            categories = await BlacklistCategory.filter(classification=params.classification).values('id')
            category_ids = [cat['id'] for cat in categories]

            # 如果没有找到任何 category，直接返回空结果
            if not category_ids:
                return error_response(
                    message=f"No categories found for classification {params.classification}",
                    code=status.HTTP_404_NOT_FOUND
                )

        # 2. 构建查询条件（动态构建 filter_params）
        filter_params = {}
        if params.target_id is not None:
            filter_params['target_id'] = params.target_id
        if params.target_value is not None:
            filter_params['target_value'] = params.target_value
        if params.brand_id !=0:
            filter_params['brand_id'] = params.brand_id
        if category_ids is not None:
            filter_params['category_id__in'] = category_ids
        if params.category_id is not None:
            filter_params['category_id'] = params.category_id

        # 3. 直接查询数据（避免先 exists() 再 all()）
        query = BlacklistUser.filter(**filter_params)
        total_length = await query.count()
        result = await query.offset(params.offset).limit(params.limit).all()

        # 4. 如果结果为空，构造错误信息
        if not result:
            error_msg = "No matching blacklist records found"
            if params.target_id and params.target_value and category_ids:
                if len(category_ids) == 1:
                    error_msg = f"target_id/target_value {params.target_value} has no blacklist record in category {category_ids[0]}"
                else:
                    error_msg = f"target_id/target_value {params.target_value} has no blacklist records in categories {category_ids}"
            elif params.target_id and params.target_value:
                error_msg = f"target_id/target_value {params.target_value} has no blacklist records"
            elif category_ids:
                if len(category_ids) == 1:
                    error_msg = f"Classification {params.classification} category id {category_ids[0]} does not exist user"
                else:
                    error_msg = f"Categories {category_ids} do not exist"
            elif params.category_id:
                error_msg = f"Category {params.category_id} does not exist"

            return error_response(
                message=error_msg,
                data=[],
                code=status.HTTP_200_OK
            )

        # 5. 返回查询结果
        return {
            'message':f"Successfully retrieved blacklist records",
            'data':jsonable_encoder(result),
            'count':total_length,
            'code':status.HTTP_200_OK
        }

    except Exception as e:
        return error_response(
            message=f"error:{str(e)}",
            data=[],
            code=status.HTTP_400_BAD_REQUEST
        )







@black_user.post('/bulk-check-optimized', response_model=GeneralResponse, response_model_exclude_unset=True)
async def bulk_check_users_in_blacklist_optimized(request: List[BlacklistUserCheckParams]):
    """
    批量检查目标是否在某一具体类的黑名单中

    **校验IM相关的黑名单一定要传入具体的brand_id**

    请求体示例：
    [
        {"target_id": 1, "target_value": "123", "brand_id": 1, "category_id": 1},
        {"target_id": 1, "target_value": "456", "brand_id": 0, "category_id": 2}
    ]

    返回示例：
    {
        "code": 200,
        "message": "Success",
        "data": [true, false]
    }
    """
    try:
        batch_size = 200
        results = []

        for i in range(0, len(request), batch_size):
            batch = request[i:i + batch_size]

            # 查询所有匹配项
            target_ids = list({user.target_id for user in batch})
            target_values = list({str(user.target_value) for user in batch})
            brand_ids = list({user.brand_id for user in batch})
            category_ids = list({user.category_id for user in batch})

            existing_records = await BlacklistUser.filter(
                target_id__in=target_ids,
                target_value__in=target_values,
                brand_id__in=brand_ids,
                category_id__in=category_ids
            ).values_list('target_id', 'target_value', 'brand_id', 'category_id')

            # 构建结果
            existing_set = set(existing_records)
            results.extend([
                (user.target_id, user.target_value, user.brand_id, user.category_id) in existing_set
                for user in batch
            ])

        return success_response(data=results)

    except Exception as e:
        return error_response(
            message=f"Failed to check blacklist status: {str(e)}",code=status.HTTP_400_BAD_REQUEST
        )



@black_user.delete('/', response_model=GeneralResponse, response_model_exclude_unset=True)
async def delete_blacklist_users(requests: Union[DeleteBlacklistUser, List[DeleteBlacklistUser]]):
    """
    统一删除黑名单用户接口（支持单条和批量）

    支持通过id或(target_id, target_value, category_id)删除。

    请求体示例：
    - 单条删除（通过ID）: {"id": 1}
    - 单条删除（通过target_id+target_value+brand_id+category_id）: {"target_id": 1, "target_value": "xxx", "brand_id":0, "category_id": 1}
    - 批量删除: [
        {"id": 1},
        {"target_id": 1, "target_value": "xxx", "brand_id":0, "category_id": 1}
      ]

    返回结果示例：
    {
        "code": 200,
        "message": "Successfully deleted 1 records",
        "data": {
            "success_count": 成功数量,
            "failed_count": 失败数量,
            "skipped_count": 跳过数量,
            "skipped_items": [跳过的items],
            "failed_items": [失败项及原因],
            "deleted_items": [成功删除的记录详情]
        }
    }
    """
    # 统一转为列表处理
    request_list = [requests] if not isinstance(requests, list) else requests

    result = DeleteResult(success_count=0,
                          failed_count=0,
                          skipped_count=0,
                          skipped_items=[],
                          failed_items=[],
                          deleted_items=[])

    try:
        async with in_transaction():
            for req in request_list:
                try:
                    # Build query
                    query = BlacklistUser
                    if req.id is not None:
                        query = query.filter(id=req.id)
                    else:
                        if req.target_id is None or req.target_value is None or req.category_id is None:
                            raise ValueError("Must provide either id or both uid and category_id")
                        req.target_value = str(req.target_value)
                        query = query.filter(target_id=req.target_id,
                                             target_value= req.target_value,
                                             category_id=req.category_id,
                                             brand_id=req.brand_id)

                    # Execute deletion
                    user = await query.first()
                    if not user:
                        result.skipped_count += 1
                        result.skipped_items.append(req)
                        continue

                    await user.delete()
                    result.success_count += 1
                    result.deleted_items.append(
                        jsonable_encoder(ReadBlacklistUser.model_validate(user, from_attributes=True)))


                except Exception as e:
                    result.failed_count += 1
                    result.failed_items.append({"request": req.dict(), "reason": str(e)})

        # Prepare response
        response_data = result.dict()
        if isinstance(requests, list):  # Batch request
            if result.failed_count > 0:
                status_code = status.HTTP_207_MULTI_STATUS
                message = f"Batch deletion completed with {result.failed_count} failures"
            else:
                status_code = status.HTTP_200_OK
                message = f"Successfully deleted {result.success_count} records"
        else:  # Single request
            if result.success_count > 0:
                status_code = status.HTTP_200_OK
                message = "Record deleted successfully"
            else:
                status_code = status.HTTP_404_NOT_FOUND
                message = "No matching record found"

        return success_response(message=message, data=response_data, code=status_code)

    except Exception as e:
        return error_response(message= str(e),code=status.HTTP_400_BAD_REQUEST)


@black_user.post('/check-all-black', response_model=GeneralResponse, response_model_exclude_unset=True)
async def check_all_category(requests: Union[BlacklistAllCheckParams, List[BlacklistAllCheckParams]]):
    """
    校验目标值所属的所有的类型的黑名单

    请求体示例：
    ```
     [
        {"target_id": 1, "target_value": "value_1"},
        {"target_id": 1, "target_value": "value_2"},
        ...
      ]
    ```

    返回结果示例：
    ```
     {
        "code": 200,
        "message": "Success",
        "data": [
            {
                "target_id": 1,
                "target_value": "uid",
                "result": [
                    {
                        "category_id": 1,
                        "entry_name": "测试tag",
                        "black_flag": false
                    },
                    ...
                ]
            },
            ...
        ]
    }
    ```
    """
    try:
        # 验证请求
        if not requests:
            return error_response(
                message="Request data cannot be empty",
                code=status.HTTP_400_BAD_REQUEST
            )

        request_list = [requests] if not isinstance(requests, list) else requests

        # 验证请求的item
        for item in request_list:
            if not hasattr(item, 'target_id') or not hasattr(item, 'target_value'):
                return error_response(
                    message="Each request item must contain target_id and target_value",
                    code=status.HTTP_400_BAD_REQUEST
                )
            if not isinstance(item.target_id, int) or item.target_id <= 0:
                return error_response(
                    message="target_id must be a positive integer",
                    code=status.HTTP_400_BAD_REQUEST
                )
            if not isinstance(item.target_value, str) or not item.target_value.strip():
                return error_response(
                    message="target_value must be a non-empty string",
                    code=status.HTTP_400_BAD_REQUEST
                )

        # 获取所有黑名单分类
        try:
            all_categories = await BlacklistCategory.all().values(
                "id", "entry_name","classification"
            )
            if not all_categories:
                return error_response(
                    message="No blacklist categories found",
                    code=status.HTTP_404_NOT_FOUND
                )

        except Exception:
            return error_response(
                message="Failed to query blacklist categories",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 构建结果列表
        response_data = []

        for request_item in request_list:
            target_value = str(request_item.target_value)
            target_id = request_item.target_id

            try:
                # 查询该目标值存在的所有黑名单分类
                existing_entries = await BlacklistUser.filter(
                    target_id=target_id,
                    target_value=target_value
                ).values_list("category_id","brand_id")

                # 构建 {category_id: [brand_ids]} 的映射
                existing_category_ids = set()
                category_brands_map = {}
                for cat_id, brand_id in existing_entries:
                    existing_category_ids.add(cat_id)
                    if cat_id not in category_brands_map:
                        category_brands_map[cat_id] = []
                    if brand_id:  # 确保brand_id不为空
                        category_brands_map[cat_id].append(brand_id)


                # 构建该目标值的检查结果
                category_results = []
                for category in all_categories:
                    category_results.append({
                        "category_id": category["id"],
                        "entry_name": category["entry_name"],
                        "classification":category["classification"],
                        "black_flag": category["id"] in existing_category_ids,
                        "black_brand": category_brands_map.get(category["id"], [])  # 新增品牌列表
                    })

                # 添加到响应数据中
                response_data.append({
                    "target_id": target_id,
                    "target_value": target_value,
                    "result": category_results
                })

            except DBConnectionError:
                # 对于单个目标值查询失败，不中断整个流程，返回部分结果
                response_data.append({
                    "target_id": target_id,
                    "target_value": target_value,
                    "result": [],
                    "error": "Database connection error"
                })
                continue
            except Exception:
                response_data.append({
                    "target_id": target_id,
                    "target_value": target_value,
                    "result": [],
                    "error": "Query failed"
                })
                continue

        return success_response(data=response_data)

    except ValueError as ve:
        return error_response(
            message=f"Invalid parameter value: {str(ve)}",
            code=status.HTTP_400_BAD_REQUEST
        )
    except Exception:
        return error_response(
            message="Internal server error",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@black_user.post('/return-blacklist-value', response_model=GeneralResponse, response_model_exclude_unset=True)
async def check_value_blacklist(request:BlacklistQuickCheck):
    """
    快速校验那些值在指定的黑名单中，并返回存在于校验类型黑名单中的值

    请求体示例：
    ```
    {
        "brand_id": 159,
        "category_id": 2,
        "target_id": 1,
        "target_value":[111,222,333,444]
    },
    ```

    返回结果示例：
    ```
    {
        "code": 200,
        "message": "Success",
        "data": [ 在黑名单中的字段值列表 ]
    }
    ```
    """

    try:
        # 验证请求
        if not request:
            return error_response(
                message="Request data cannot be empty",
                code=status.HTTP_400_BAD_REQUEST
            )


        request.target_value = [str(request.target_value)] if not isinstance(request.target_value, list) else [str(v) for v in request.target_value]

        matched_records = await BlacklistUser.filter(
            target_id=request.target_id,
            brand_id=request.brand_id,
            category_id=request.category_id,
            target_value__in=request.target_value
        ).values_list('target_value', flat=True)

        return success_response(message=f"Found {len(matched_records)} items matching the blacklist",data=matched_records)

    except ValueError as ve:
        return error_response(
            message=f"Invalid parameter value: {str(ve)}",
            code=status.HTTP_400_BAD_REQUEST
        )
    except Exception:
        return error_response(
            message="Internal server error",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@black_user.post('/return-all-black-brand', response_model=GeneralResponse, response_model_exclude_unset=True)
async def query_black_brands(request:BlacklistBlackBrand):
    """
    返回目标字段拉黑的所有的品牌

    请求体示例：
    ```
    {
        "target_id": 1,
        "target_value":[111,222,333,444]
    },
    ```

    返回结果示例：
    ```
    {
        "code": 200,
        "message": "Success",
        "data": [ {
            "target_value": val_1
            "black_brand": [brand_id_1, brand_id_2, brand_id_3,xxx]
        } ,
        {
            "target_value": val_2
            "black_brand": [brand_id_1, brand_id_2, brand_id_3,xxx]
        } ,...
        ]
    }
    ```

    """
    try:
        # 验证请求
        if not request:
            return error_response(
                message="Request data cannot be empty",
                code=status.HTTP_400_BAD_REQUEST
            )

        request.target_value = [str(request.target_value)] if not isinstance(request.target_value, list) else [str(v) for v in request.target_value]

        # 获取IM类别下的所有category_id
        category_ids = await BlacklistCategory.filter(
            classification=2
        ).values_list('id', flat=True)

        existing_entries = await BlacklistUser.filter(
            target_id=request.target_id,
            target_value__in=request.target_value,
            category_id__in=category_ids  # 外键的classification属于IM类别
        ).exclude(
            brand_id=0
        ).values_list('target_value','brand_id')


        # 构建 {category_id: [brand_ids]} 的映射
        category_brands_map = {}
        for target_value, brand_id in existing_entries:
            if target_value not in category_brands_map:
                category_brands_map[target_value] = []
            if brand_id:  # 确保brand_id不为空
                category_brands_map[target_value].append(brand_id)


        # 构建结果数据
        black_brand_result = [
            {
                "target_value": val,
                "black_brand": category_brands_map.get(val,[])
            }
            for val in request.target_value
        ]

        return success_response(data=black_brand_result)


    except ValueError as ve:
        return error_response(
            message=f"Invalid parameter value: {str(ve)}",
            code=status.HTTP_400_BAD_REQUEST
        )
    except Exception:
        return error_response(
            message="Internal server error",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )