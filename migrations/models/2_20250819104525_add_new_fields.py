from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `blacklist_categories` ADD `entry_name_en` VARCHAR(255) NOT NULL COMMENT '黑名单具体名称(English)' DEFAULT '';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `blacklist_categories` DROP COLUMN `entry_name_en`;"""
