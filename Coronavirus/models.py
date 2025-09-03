from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func, ForeignKey, Date
from sqlalchemy.orm import relationship
from .database import Base

class City(Base):
    __tablename__ = 'test_city'
    id = Column(Integer, primary_key=True,index=True, autoincrement=True, nullable=False)
    province = Column(String(100),unique=True, nullable=False,comment='省/直辖市')
    country = Column(String(100), nullable=False,comment='国家')
    country_code = Column(String(100), nullable=False,comment='国家代码')
    country_population = Column(BigInteger, nullable=False,comment='国家人口')
    data = relationship('Data', back_populates='city') # 'Data'是关联的类名；back_populates来指定反向访问的属性名称

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    # # 排序方法
    # __mapper_args__ = {"order_by": country_code}

    def __repr__(self):
        return f"{self.country}_{self.province}"

class Data(Base):
    __tablename__ = 'test_data'
    id = Column(Integer, primary_key=True,index=True, autoincrement=True, nullable=False)
    # 外键
    city_id = Column(Integer, ForeignKey('test_city.id'), nullable=False)
    date = Column(Date,  nullable=False,comment='数据日期')
    confirmed = Column(BigInteger,default=0,nullable=False,comment='确诊人数')
    deaths = Column(BigInteger,default=0,nullable=False,comment='死亡人数')
    recovered =  Column(BigInteger,default=0,nullable=False,comment='痊愈人数')
    city = relationship('City', back_populates='data') # 'City'是关联的类名；back_populates来指定反向访问的属性名称

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    # __mapper_args__ = {"order_by": date.desc()}  # 按日期降序排列

    def __repr__(self):
        return f'{repr(self.date)}：确诊{self.confirmed}例'

    """ 附上三个SQLAlchemy教程

    SQLAlchemy的基本操作大全 
        http://www.taodudu.cc/news/show-175725.html

    Python3+SQLAlchemy+Sqlite3实现ORM教程 
        https://www.cnblogs.com/jiangxiaobo/p/12350561.html

    SQLAlchemy基础知识 Autoflush和Autocommit
        https://zhuanlan.zhihu.com/p/48994990
    """