from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `blacklist_users_aggregate` MODIFY COLUMN `modify_user` INT NOT NULL COMMENT '操作者id' DEFAULT 0;
        ALTER TABLE `blacklist_users_exclusion` MODIFY COLUMN `modify_user` INT NOT NULL COMMENT '操作者id' DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `blacklist_users_aggregate` MODIFY COLUMN `modify_user` INT NOT NULL COMMENT '操作者' DEFAULT 0;
        ALTER TABLE `blacklist_users_exclusion` MODIFY COLUMN `modify_user` INT NOT NULL COMMENT '操作者' DEFAULT 0;"""
