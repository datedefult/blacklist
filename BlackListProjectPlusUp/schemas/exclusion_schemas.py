from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel


# 白名单排除项查询参数
class BlacklistExclusionQueryParams(BaseModel):
    """
    白名单排除项查询参数
    支持按target_id、target_value、category_id、分页(offset/limit)等方式查询
    """
    target_id: Optional[int] = None
    target_value: Optional[Union[str, int]] = None
    category_id: Optional[int] = None
    offset: int = 0
    limit: int = 100

    class Config:
        json_schema_extra = {
            'example': {
                'target_id': 1,
                'target_value': 'uid/number',
                'category_id': 1,
                'offset': 0,
                'limit': 100
            }
        }


# 删除白名单排除项结构体
class DeleteBlacklistExclusion(BaseModel):
    """
    删除白名单排除项请求体
    可通过id或(target_id, target_value, category_id)删除
    """
    id: Optional[int] = None
    target_id: Optional[int] = None
    target_value: Optional[Union[str, int]] = None
    category_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            'example': {
                'id': 1,
                'target_id': 1,
                'target_value': 'uid/number',
                'category_id': 1
            }
        }


# 创建白名单排除项结构体
class CreateBlacklistExclusion(DeleteBlacklistExclusion):
    """
    创建白名单排除项请求体
    """
    describe: Optional[str] = None
    level: Optional[int] = 3
    modify_user:int


    class Config:
        json_schema_extra = {
            'example': {
                'target_id': 1,
                'target_value': 'uid/number',

                "describe": '这是一段描述',
                'category_id': 1,
                "level": 3,
                "modify_user": 1
            }
        }


# 读取白名单排除项结构体
class ReadBlacklistExclusion(CreateBlacklistExclusion):
    """
    白名单排除项返回结构体
    """
    id: int
    create_time: datetime

    class Config:
        json_schema_extra = {
            'example': {
                'id': 1,
                'target_id': 1,
                'target_value': 'uid/number',
                "describe": '这是一段描述',
                'category_id': 1,
                "level": 3,
                'create_time': datetime.now(),
            }
        }
        from_attributes = True