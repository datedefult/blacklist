from typing import List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request,status
from fastapi.templating import Jinja2Templates
from pydantic import HttpUrl
from sqlalchemy.orm import Session


from Coronavirus import crud, schemas
from Coronavirus.database import engine, Base, SessionLocal
from Coronavirus.models import City, Data

application = APIRouter()
# 创建表
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 创建城市
@application.post('/create_city',response_model=schemas.CreateCity)
def create_city(city: schemas.CreateCity,db:Session=Depends(get_db)):
    db_city = crud.get_city_by_name(db=db,name=city.province)
    if db_city:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='City already exists')
    return crud.create_city(db=db,city=city)

# 查询城市
@application.post('/get_city/{city}',response_model=schemas.ReadCity)
def get_city(city:str,db:Session = Depends(get_db)):
    db_city = crud.get_city_by_name(db=db,name=city)
    if db_city is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='City not found')
    return db_city

@application.get('/get_cities',response_model=List[schemas.ReadCity])
def get_cities(skip: int =0, limit: int=100,db:Session = Depends(get_db)):
    cities = crud.get_cities(db=db, skip= skip, limit=limit)
    return cities


# 创建数据
@application.post('/create_data',response_model=schemas.CreateData)
def create_data(city:str,data:schemas.CreateData,db:Session = Depends(get_db)):
    db_city = crud.get_city_by_name(db=db,name=city)
    data = crud.create_city_data(db=db,data=data,city_id=db_city.id)
    return data

@application.get('/get_data',response_model=List[schemas.ReadData])
def get_data(city:str=None,skip:int=0,limit:int=100,db:Session = Depends(get_db)):
    data = crud.get_data(db=db, city=city, skip=skip, limit=limit)
    return data