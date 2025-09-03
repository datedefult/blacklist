TORTOISE_ORM3 = {
    'connections': {
        'BlackListProject3': {
            # 'engine': 'tortoise.backends.asyncpg',  PostgreSQL
            'engine': 'tortoise.backends.mysql',  # MySQL or Mariadb
            'credentials': {
                'host': '192.168.10.3',
                'port': '3307',
                'user': 'root',
                'password': '123456',
                'database': 'test_all',
                'minsize': 1,
                'maxsize': 5,
                'charset': 'utf8mb4',
                "echo": True
            }
        },
    },
    'apps': {
        'models': {
            'models': ['BlackListProjectPlusUp.models', "aerich.models"],
            'default_connection': 'BlackListProject3',

        }
    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai',
    "log_level": None,  # 禁用日志
}