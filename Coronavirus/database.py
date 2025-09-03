from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'sqlite:///./coronavirus.sqlite3'
# SQLALCHEMY_DATABASE_URL = "postgresql://username:password@host:port/database_name"  # MySQL或PostgreSQL的连接方法

TEST_DATABASE = {
    'host': '192.168.10.3',
    'port': 3307,
    'user': 'root',
    'password': '123456',
    'database': 'test_all'
}
def get_engine(config):
    """
    根据提供的数据库配置返回一个SQLAlchemy engine。

    参数:
    config (dict): 包含数据库配置信息的字典。
        必须包含以下键: 'host', 'user', 'password', 'port', 'database'

    返回:
    SQLAlchemy engine 对象
    """
    host = config['host']
    user = config['user']
    password = config['password']
    port = config['port']
    database = config['database']

    engine = create_engine(
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}",
        echo=True,
        pool_size=5,
    )
    return engine

engine = get_engine(TEST_DATABASE)
# 在SQLAlchemy中，CRUD都是通过会话(session)进行的，所以我们必须要先创建会话，每一个SessionLocal实例就是一个数据库session
# flush()是指发送数据库语句到数据库，但数据库不一定执行写入磁盘；commit()是指提交事务，将变更保存到数据库文件
SessionLocal = sessionmaker(bind=engine,autocommit=False,autoflush=False)

# 创建基本映射类
Base = declarative_base(name='Base')
Base.metadata.create_all(bind=engine)

