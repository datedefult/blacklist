from datetime import datetime
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel

# 黑名单类别查询参数
class BlacklistCategoryQueryParams(BaseModel):
    """
    黑名单类别查询参数
    支持按id、classification、分页(offset/limit)等多种方式查询
    """
    id: Optional[int] = None
    classification: Optional[int] = None
    offset: int = 0
    limit: int = 100

    class Config:
        json_schema_extra = {
            'example': {
                'id': 1,
                'classification': 0,
                'offset': 0,
                'limit': 100
            }
        }

# 黑名单类别枚举
class CategoryEnum(IntEnum):
    """
    黑名单类别枚举
    0-其他，1-EDM，2-IM，3-社区，4-OA，5-画像类
    """
    OTHER = 0
    EDM = 1
    IM = 2
    COMMUNITY = 3
    OA = 4
    PROFILE = 5

    @classmethod
    def get_label(cls, value: int) -> str:
        return {
            cls.OTHER: "其他",
            cls.EDM: "EDM",
            cls.IM: "IM",
            cls.COMMUNITY: "社区",
            cls.OA: "OA",
            cls.PROFILE: "画像类"
        }.get(value, "未知")

    @classmethod
    def values(cls):
        return [item.value for item in cls]

# 创建黑名单类别结构体
class CreateBlacklistCategory(BaseModel):
    """
    创建黑名单类别请求体
    """
    classification: CategoryEnum
    entry_name: str
    entry_name_en: str
    describe: Optional[str] = ''

    class Config:
        json_schema_extra = {
            'example': {
                "classification": "0",
                "entry_name": "测试tag",
                "entry_name_en": "test tag",
                "describe": '这是一段描述',
            }
        }

# 读取黑名单类别结构体
class ReadBlacklistCategory(CreateBlacklistCategory):
    """
    黑名单类别返回结构体
    """
    id: int
    create_time: datetime
    update_time: datetime
    cls_name: str

    class Config:
        json_schema_extra = {
            'example': {
                'id': 1,
                "classification": "0",
                "cls_name": "其他",
                "entry_name": "测试tag",
                "entry_name_en": "test tag",
                "describe": '这是一段描述',
                'create_time': datetime.now(),
                'update_time': datetime.now(),
            }
        }
        from_attributes = True

# 黑名单类别更新结构体
class CategoryUpdateRequest(BaseModel):
    """
    黑名单类别更新请求体
    可选字段：classification、entry_name、describe
    """
    classification: Optional[int] = None
    entry_name: Optional[str] = None
    entry_name_en: Optional[str] = None
    describe: Optional[str] = None

    class Config:
        json_schema_extra = {
            'example': {
                "classification": 0,
                "entry_name": "测试tag",
                "entry_name_en": "test tag",
                "describe": '这是一段描述',
            }
        }