from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `blacklist_users_aggregate` ADD `describe` VARCHAR(500) COMMENT '加入黑名单的原因';
        ALTER TABLE `blacklist_users_aggregate` ADD `modify_user` INT NOT NULL COMMENT '操作者' DEFAULT 0;
        ALTER TABLE `blacklist_users_aggregate` MODIFY COLUMN `target_id` INT NOT NULL COMMENT '字段类型：1-uid,2-设备,3-IP';
        ALTER TABLE `blacklist_users_exclusion` ADD `modify_user` INT NOT NULL COMMENT '操作者' DEFAULT 0;
        ALTER TABLE `blacklist_users_exclusion` MODIFY COLUMN `target_id` INT NOT NULL COMMENT '字段类型：1-uid,2-设备,3-IP';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `blacklist_users_aggregate` DROP COLUMN `describe`;
        ALTER TABLE `blacklist_users_aggregate` DROP COLUMN `modify_user`;
        ALTER TABLE `blacklist_users_aggregate` MODIFY COLUMN `target_id` INT NOT NULL COMMENT '字段类型：1-uid,2-设备,3-';
        ALTER TABLE `blacklist_users_exclusion` DROP COLUMN `modify_user`;
        ALTER TABLE `blacklist_users_exclusion` MODIFY COLUMN `target_id` INT NOT NULL COMMENT '字段类型：1-uid,2-设备,3-';"""
