from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Union, List


# 黑名单用户检查参数
class BlacklistUserCheckParams(BaseModel):
    """
    检查目标是否在指定类别黑名单中的参数
    """
    target_id: int
    target_value: Union[int, str]
    brand_id:Optional[int] = 0
    category_id: int

    class Config:
        json_schema_extra = {
            'example': {
                'target_id': 1,
                'target_value': 'uid/number',
                'brand_id': 0,
                'category_id': 2
            }
        }

# 校验所有类型的黑名单种类
class BlacklistAllCheckParams(BaseModel):
    """
    检查目标所属的所有黑名单种类
    """
    target_id: int
    target_value: Union[str,int]
    class Config:
        json_schema_extra = {
            'example': {
                'target_id': 1,
                'target_value': 'uid/number',

            }
        }


# 黑名单用户查询参数
class BlacklistUserQueryParams(BaseModel):
    """
    黑名单用户查询参数
    支持按target_id、target_value、brand_id、category_id、classification、分页(offset/limit)等方式查询
    """
    target_id: Optional[int] = None
    target_value: Optional[Union[str,int]] = None
    brand_id:Optional[int] = 0
    category_id: Optional[int] = None
    classification: Optional[str] = None  # 分类名称参数
    offset: int = 0
    limit: int = 100

    class Config:
        json_schema_extra = {
            'example': {
                'target_id': 1,
                'target_value': 'uid/number',
                'brand_id': 0,
                'category_id': 2,
                'classification': 3,
                'offset': 0,
                'limit': 100
            }
        }

# 创建黑名单用户结构体
class CreateBlacklistUser(BaseModel):
    """
    创建黑名单用户请求体
    """
    target_id: int
    target_value: Union[str, int]
    brand_id:Optional[int] = 0
    category_id: int

    class Config:
        json_schema_extra = {
            'example': {
                'target_id': 1,
                'target_value': 'uid/number',
                'brand_id': 0,
                'category_id': 2
            }
        }

# 删除黑名单用户结构体
class DeleteBlacklistUser(CreateBlacklistUser):
    """
    删除黑名单用户请求体
    可通过id或(target_id, target_value,brand_id, category_id)删除
    """
    id: Optional[int] = None

    class Config:
        json_schema_extra = {
            'example': {
                'id': 1,
                'target_id': 1,
                'target_value': 'uid/number',
                'brand_id': 0,
                'category_id': 2
            }
        }

# 读取黑名单用户结构体
class ReadBlacklistUser(CreateBlacklistUser):
    """
    黑名单用户返回结构体
    """
    id: int
    create_time: datetime

    class Config:
        json_schema_extra = {
            'example': {
                'id': 1,
                'target_id': 1,
                'target_value': 'uid/number',
                'brand_id': 0,
                'category_id': 2,
                'create_time': datetime.now(),
            }
        }
        from_attributes = True


# 校验那些数据在黑名单中，简易传输版
class BlacklistQuickCheck(BaseModel):
    target_id: int
    target_value: Union[str,int,List[str],List[int]]
    brand_id:Optional[int] = 0
    category_id: int

    class Config:
        json_schema_extra = {
            'example': {
                'target_id': 1,
                'target_value': ['uid1','uid2','uid3','uid4'],
                'brand_id': 0,
                'category_id': 2,

            }
        }
        from_attributes = True

class BlacklistBlackBrand(BaseModel):
    """
    返回所有拉黑的品牌
    """
    target_id: int
    target_value: Union[str,int,List[str],List[int]]

    class Config:
        json_schema_extra = {
            'example': {
                'target_id': 1,
                'target_value': ['uid1','uid2','uid3','uid4'],

            }
        }
        from_attributes = True