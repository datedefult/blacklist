from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from utils.BaseResponse import success_response, error_response, GeneralResponse



from enum import IntEnum
from typing import List, Union
from fastapi import status
from BlackListProjectPlusUp.models import BlacklistCategory
from BlackListProjectPlusUp.schemas import ReadBlacklistCategory, CreateBlacklistCategory, CategoryEnum, \
    CategoryUpdateRequest, BlacklistCategoryQueryParams


black_category = APIRouter()

@black_category.get("/", response_model=GeneralResponse[Union[List[ReadBlacklistCategory], ReadBlacklistCategory]])
async def query_categories(params: BlacklistCategoryQueryParams = Depends()):
    """
    统一的黑名单类别查询接口

    **<p style="color:red;">此处回传的id即为后续所有接口中的category_id</p>**

    支持多种查询模式：
    - 查询所有类别：不传参数（或只传offset/limit）
    - 根据ID查询：id=1（返回单个条目）
    - 根据classification查询：classification=1
    - 组合查询：id + classification（AND条件过滤）

    请求示例：
    - 查询所有：GET /
    - 根据ID查询：GET /?id=1
    - 根据classification查询：GET /?classification=1
    - 分页查询：GET /?offset=10&limit=20

    返回结果：
    - 当通过ID查询时返回单个条目
    - 其他查询类型返回列表
    """
    try:
        # 构建基础查询
        query = BlacklistCategory

        # 应用过滤条件
        if params.id is not None:
            query = query.filter(id=params.id)
        if params.classification is not None:
            query = query.filter(classification=params.classification)

        # 处理ID查询（返回单个条目）
        if params.id is not None:
            category = await query.first()
            if not category:
                return error_response(message=f"Category ID {params.id} not found",
                    code=status.HTTP_200_OK)

            return success_response(message="Successfully retrieved category",
                data=jsonable_encoder(ReadBlacklistCategory.model_validate(category, from_attributes=True)),
                code=status.HTTP_200_OK)

        # 处理列表查询
        categories = await query.all().offset(params.offset).limit(params.limit).all()

        return success_response(message="Successfully retrieved categories",
            data=jsonable_encoder([ReadBlacklistCategory.model_validate(c, from_attributes=True) for c in categories]),
            code=status.HTTP_200_OK)

    except Exception as e:
        return error_response(message=f"Category query failed: {str(e)}", code=status.HTTP_200_OK)


@black_category.post("/", response_model=GeneralResponse)
async def create_category(data: CreateBlacklistCategory):
    """
    创建新的黑名单类别

    - classification: 0-其他，1-EDM，2-IM，3-社区，4-OA，5-画像类

    请求体示例：
    ```
    {
        "classification": 1,
        "entry_name": "example",
        "describe": "描述信息"
    }
    ```
    返回结果示例：
    - 成功创建返回新类别信息
    - 如果entry_name已存在，返回错误信息
    """
    exists = await BlacklistCategory.get_or_none(entry_name=data.entry_name)
    if exists:
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"entry_name '{data.entry_name}' 已存在")
        return error_response(
            message=f"Entry name '{data.entry_name}' already exists. Please choose a different name to create a new entry, or use the PUT method to update the existing one.",
            data=jsonable_encoder(ReadBlacklistCategory.model_validate(exists, from_attributes=True)),
            code=status.HTTP_400_BAD_REQUEST, )
    
    exists_en = await BlacklistCategory.get_or_none(entry_name_en=data.entry_name_en)
    if exists_en:
        return error_response(
            message=f"Entry english name '{data.entry_name_en}' already exists. Please choose a different name to create a new entry, or use the PUT method to update the existing one.",
            data=jsonable_encoder(ReadBlacklistCategory.model_validate(exists_en, from_attributes=True)),
            code=status.HTTP_400_BAD_REQUEST )
    
    created = await BlacklistCategory.create(
        classification=data.classification.value if isinstance(data.classification, IntEnum) else data.classification,
        cls_name=CategoryEnum.get_label(data.classification),
        entry_name=data.entry_name,
        entry_name_en=data.entry_name_en,
        describe=data.describe
    )
    return success_response(message="Category insert successfully",
        data=jsonable_encoder(ReadBlacklistCategory.model_validate(created, from_attributes=True)),
        code=status.HTTP_200_OK)


@black_category.delete("/{cat_id}", response_model=GeneralResponse)
async def delete_category(cat_id: int):
    """
    删除指定ID的黑名单类别

    请求示例：
    - DELETE /{cat_id}

    返回结果示例：
    - 成功删除返回被删除的类别信息
    - 如果ID不存在，返回错误信息
    """
    try:
        # 查询是否存在该分类
        category = await BlacklistCategory.get_or_none(id=cat_id)
        if not category:
            return error_response(message=f"Category {category} is not exist",
                code=status.HTTP_404_NOT_FOUND)

        # 删除该分类
        await category.delete()

        return success_response(message=f"Category with ID {cat_id} has been successfully deleted",
            data=jsonable_encoder(ReadBlacklistCategory.model_validate(category, from_attributes=True)),
            code=status.HTTP_200_OK)



    except Exception as e:
        # 捕获其他异常并返回错误信息
        return error_response(message=f"Invalid classification value: {str(e)}",code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@black_category.put("/{cat_id}", response_model=GeneralResponse)
async def update_category(cat_id: int, request: CategoryUpdateRequest):
    """
    更新指定ID的黑名单类别

    请求体示例：
    ```
    {
        "entry_name": "new_name",
        "classification": 2,
        "describe": "更新描述"
    }
    ```
    返回结果示例：
    - 成功更新返回更新后的类别信息
    - 如果ID不存在或参数无效，返回错误信息
    """
    category = await BlacklistCategory.get_or_none(id=cat_id)

    if not category:
        return error_response(message=f"Category {cat_id} does not exist",code=status.HTTP_404_NOT_FOUND)

    # 更新 entry_name
    if request.entry_name is not None and request.entry_name.strip() != '':
        if request.entry_name != category.entry_name:
            exists = await BlacklistCategory.get_or_none(entry_name=request.entry_name)
            if exists:
                return error_response(message="Entry name already exists and info in detail",
                    data=jsonable_encoder(ReadBlacklistCategory.model_validate(exists, from_attributes=True)),
                    code=status.HTTP_400_BAD_REQUEST, )
            category.entry_name = request.entry_name

    # 更新 classification
    if request.classification is not None and request.classification != '':
        if request.classification not in CategoryEnum.values():
            allowed_values = CategoryEnum.values()
            return error_response(message=f"Invalid classification value.Classification {request.classification} is not allowed. Allowed values are: {allowed_values}",
                code=status.HTTP_400_BAD_REQUEST)
        category.classification = request.classification
        category.cls_name = CategoryEnum.get_label(request.classification)

    # 更新 describe
    if request.describe is not None and request.describe != '':
        category.describe = request.describe
        
    # 更新 entry_name_en
    if request.entry_name_en is not None and request.entry_name_en != '':
        if request.entry_name_en != category.entry_name_en:
            exists = await BlacklistCategory.get_or_none(entry_name_en=request.entry_name_en)
            if exists:
                return error_response(message="Entry english name already exists and info in detail",
                    data=jsonable_encoder(ReadBlacklistCategory.model_validate(exists, from_attributes=True)),
                    code=status.HTTP_400_BAD_REQUEST, )
            category.entry_name_en = request.entry_name_en
    
    await category.save()

    return success_response(message="Category updated successfully",
        data=jsonable_encoder(ReadBlacklistCategory.model_validate(category, from_attributes=True)),
        code=status.HTTP_200_OK)
