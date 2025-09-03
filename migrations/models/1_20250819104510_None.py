from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `blacklist_categories` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    `classification` INT NOT NULL COMMENT '黑名单类别：0-其他，1-EDM，2-IM，3-社区，4-OA，5-画像类',
    `cls_name` VARCHAR(100) NOT NULL COMMENT '所属类别名称',
    `entry_name` VARCHAR(255) NOT NULL COMMENT '黑名单具体名称',
    `create_time` DATETIME(6) NOT NULL COMMENT 'tag添加时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT 'tag修改时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `describe` VARCHAR(500) COMMENT '规则描述、数据来源表或者其他描述性内容' DEFAULT '',
    KEY `idx_blacklist_c_classif_9c7e01` (`classification`)
) CHARACTER SET utf8mb4 COMMENT='黑名单具体类型，以及来源及规则记录';
CREATE TABLE IF NOT EXISTS `blacklist_users_aggregate` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    `target_id` INT NOT NULL COMMENT '字段类型：1-uid,2-设备,3-',
    `target_value` VARCHAR(500) NOT NULL COMMENT '字段值',
    `brand_id` INT NOT NULL COMMENT '品牌id，在category属于的classification=IM时候才有意义，默认值为0' DEFAULT 0,
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `category_id` INT NOT NULL COMMENT '关联的黑名单类别ID',
    UNIQUE KEY `uid_blacklist_u_target__d07ed3` (`target_id`, `target_value`, `brand_id`, `category_id`),
    CONSTRAINT `fk_blacklis_blacklis_7a27dc3f` FOREIGN KEY (`category_id`) REFERENCES `blacklist_categories` (`id`) ON DELETE CASCADE,
    KEY `idx_blacklist_u_target__970aab` (`target_id`),
    KEY `idx_blacklist_u_target__65e207` (`target_value`)
) CHARACTER SET utf8mb4 COMMENT='所有黑名单字段';
CREATE TABLE IF NOT EXISTS `blacklist_users_exclusion` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    `target_id` INT NOT NULL COMMENT '字段类型：1-uid,2-设备,3-',
    `target_value` VARCHAR(500) NOT NULL COMMENT '字段值',
    `level` INT NOT NULL COMMENT '黑名单级别：1-全部过滤，2-按照所属的classification过滤，3-仅按照category过滤(默认级别)' DEFAULT 3,
    `describe` VARCHAR(500) COMMENT '排除说明',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `category_id` INT NOT NULL COMMENT '关联的黑名单类别ID',
    UNIQUE KEY `uid_blacklist_u_target__fdd0e3` (`target_id`, `target_value`, `category_id`),
    CONSTRAINT `fk_blacklis_blacklis_1299a026` FOREIGN KEY (`category_id`) REFERENCES `blacklist_categories` (`id`) ON DELETE CASCADE,
    KEY `idx_blacklist_u_target__5e72c1` (`target_id`),
    KEY `idx_blacklist_u_target__6d494f` (`target_value`)
) CHARACTER SET utf8mb4 COMMENT='白名单：黑名单排除项';
CREATE TABLE IF NOT EXISTS `blacklist_request_logs` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    `client_ip` VARCHAR(45) COMMENT '客户端IP地址（支持IPv4/IPv6）',
    `method` VARCHAR(10) NOT NULL COMMENT 'HTTP请求方法（如 GET、POST）',
    `path` VARCHAR(255) NOT NULL COMMENT '请求路径（不含查询参数）',
    `request_body` LONGTEXT COMMENT '请求体内容（纯文本或JSON字符串）',
    `request_params` JSON COMMENT '请求查询参数（如 ?id=1&name=abc）',
    `request_headers` JSON COMMENT '请求头信息，JSON格式',
    `response_content` LONGTEXT COMMENT '响应体内容（纯文本或结果描述）',
    `response_headers` JSON COMMENT '响应头信息，JSON格式',
    `status_code` INT NOT NULL COMMENT 'HTTP响应状态码（如 200、404）',
    `duration` DOUBLE NOT NULL COMMENT '请求处理耗时（单位：毫秒）',
    `created_at` DATETIME(6) NOT NULL COMMENT '记录创建时间（自动生成）' DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='接口请求日志记录表，用于记录每一次HTTP请求的详细信息';
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
