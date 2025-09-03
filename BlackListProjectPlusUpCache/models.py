from tortoise import fields
from tortoise.models import Model


class BlacklistCategory(Model):
    """
    定义黑名单类型
    """
    id = fields.IntField(pk=True, description="主键ID")
    classification = fields.IntField(index=True, description="黑名单类别：0-其他，1-EDM，2-IM，3-社区，4-OA，5-画像类")
    cls_name = fields.CharField(max_length=100, description="所属类别名称")
    # subtype_num = fields.IntField(description="小分类编号")
    entry_name = fields.CharField(max_length=255, description="黑名单具体名称")
    entry_name_en = fields.CharField(max_length=255,default='', description="黑名单具体名称(English)")
    create_time = fields.DatetimeField(auto_now_add=True, description="tag添加时间")
    update_time = fields.DatetimeField(auto_now=True, description="tag修改时间")
    describe = fields.CharField(max_length=500, default='', null=True,
                                description="规则描述、数据来源表或者其他描述性内容")

    class Meta:
        table = "blacklist_categories"
        # index_together = [("classification", "subtype_num")]  # 普通联合索引
        # unique_together = [("classification", "subtype_num")]  # 联合唯一索引
        table_description = "黑名单具体类型，以及来源及规则记录"

    def __str__(self):
        return f"BlacklistCategory(id={self.id}, classification={self.classification}, entry_name={self.entry_name})"


class BlacklistUser(Model):
    """
    定义黑名单具体用户
    """
    id = fields.IntField(pk=True, description="主键ID")

    target_id = fields.IntField(index=True, description='字段类型：1-uid,2-设备,3-')
    target_value = fields.CharField(max_length=500,index=True, description='字段值')
    brand_id = fields.IntField(default=0, description='品牌id，在category属于的classification=IM时候才有意义，默认值为0')

    # uid = fields.IntField(index=True, description='用户id')
    category = fields.ForeignKeyField("models.BlacklistCategory", related_name="users", db_column="category_id",
                                      description="关联的黑名单类别ID")  # 手动指定数据库字段名
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")

    # delete_time = fields.DatetimeField(description='删除时间',null=True)

    class Meta:
        table = "blacklist_users_aggregate"
        unique_together = [("target_id","target_value","brand_id", "category")]
        table_description = "所有黑名单字段"


class BlacklistUserExclusion(Model):
    """
    定义黑名单某一类型排除项
    """
    id = fields.IntField(pk=True, description="主键ID")

    target_id = fields.IntField(index=True, description='字段类型：1-uid,2-设备,3-')
    target_value = fields.CharField(max_length=500,index=True, description='字段值')

    category = fields.ForeignKeyField("models.BlacklistCategory", related_name="exclusions", db_column="category_id",
                                      description="关联的黑名单类别ID")  # 手动指定数据库字段名
    level = fields.IntField(default=3,null=False,description='黑名单级别：1-全部过滤，2-按照所属的classification过滤，3-仅按照category过滤(默认级别)')
    describe = fields.CharField(max_length=500, description='排除说明', null=True)
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "blacklist_users_exclusion"

        unique_together = [("target_id","target_value", "category")]
        table_description = "白名单：黑名单排除项"


class RequestLog(Model):
    id = fields.IntField(pk=True, description='主键ID')
    client_ip = fields.CharField(max_length=45, null=True, description='客户端IP地址（支持IPv4/IPv6）')
    method = fields.CharField(max_length=10, description='HTTP请求方法（如 GET、POST）')
    path = fields.CharField(max_length=255, description='请求路径（不含查询参数）')
    request_body = fields.TextField(null=True, description='请求体内容（纯文本或JSON字符串）')
    request_params = fields.JSONField(null=True, description='请求查询参数（如 ?id=1&name=abc）')
    request_headers = fields.JSONField(null=True, description='请求头信息，JSON格式')
    response_content = fields.TextField(null=True, description='响应体内容（纯文本或结果描述）')
    response_headers = fields.JSONField(null=True, description='响应头信息，JSON格式')
    status_code = fields.IntField( description='HTTP响应状态码（如 200、404）')
    duration = fields.FloatField(description='请求处理耗时（单位：毫秒）')
    created_at = fields.DatetimeField(auto_now_add=True, description='记录创建时间（自动生成）')

    class Meta:
        table = "blacklist_request_logs"
        table_description = "接口请求日志记录表，用于记录每一次HTTP请求的详细信息"
