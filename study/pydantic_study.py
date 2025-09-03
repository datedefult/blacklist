from datetime import datetime, date
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, constr
from sqlalchemy import Column, Integer, String, ARRAY
from sqlalchemy.orm import declarative_base


class User(BaseModel):
    # 数据验证及规范
    id: int # 无默认值，必填字段
    name: str ='John Snow' # 有默认值，选填字段
    # signup_ts:datetime
    signup_ts: Optional[datetime]=None # 第二种非必传字段
    friends: List[int] = []

# ------------------------------1、第一步认识
external_data = {
    'id':'123',
    'signup_ts':'2025-06-01 23:02:03',
    'friends':['1','878','15',3]
}

suer = User(**external_data)

print(suer.model_dump())

# ------------------------------2、第二步失败处理
try:
    User(id=5,name='dasd',signup_ts=datetime(2025,6,1,23),friends=['dasd',2,3])
except Exception as e:
    print(e.json())

# ------------------------------3、第三步解析数据
print(suer.model_dump())
print(suer.model_dump_json())

# ------------------------------4、第四步解析文件
# 当前文件路径
# path = Path(__file__).parent.absolute()
path = Path('pydantic_tutorial.json').absolute()
path.write_text(suer.model_dump_json())
print(path)

new_user = User.parse_file(path)
print(new_user.model_json_schema())

# ------------------------------5、第五步递归模型
# 在不同的类型中复用
class Sound(BaseModel):
    sound:str

class Dog(BaseModel):
    birthday:date
    weight:float=Optional[None]
    sound:List[Sound]

dog = Dog(birthday=date.today(),weight=66.4,sound=[{'sound':'wa~','sound':'laiik~'}])
print(dog.model_dump())
# ------------------------------6、第六步创建sql ORM模型
# 建立数据库表，非pydantic
Base = declarative_base()
class CompanyOrm(Base):
    __tablename__='companies'
    id = Column(Integer, primary_key=True,nullable=False)
    public_key = Column(String(20),index=True,nullable=False,unique=True)
    name = Column(String(63),unique=True,nullable=False)
    domains = Column(ARRAY(String(255)),nullable=False)
# 校验类，pydantic
class CompanyMode(BaseModel):
    id:int
    # public_key:str
    # constr：限制字符串最大长度
    public_key: constr(max_length=20)
    name:constr(max_length=63)
    domains: List[constr(max_length=255)]

    class Config:
        orm_mode=True
        from_attributes = True

# 验证创建的数据表的类型是否正确
co_orm = CompanyOrm(id=123,public_key='foobar',name='Testing',domains=['example.com','imooc.com'])
print(CompanyMode.model_validate(co_orm))