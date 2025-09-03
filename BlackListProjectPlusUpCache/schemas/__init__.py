from typing import List, Any
from .category_schemas import *
from .exclusion_schemas import *
from .user_schemas import *


class BaseResult(BaseModel):
    success_count: int
    failed_count: int
    skipped_count: int
    failed_items: List[dict] # 存储失败记录的原始数据和原因
    skipped_items: List[Any]


class CreationResult(BaseResult):
    removed_from_blacklist:Optional[int]  # 记录从黑名单移除的数量

class DeleteResult(BaseResult):
    deleted_items: Optional[List[dict]]
