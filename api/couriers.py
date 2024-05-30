import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert, select, column
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from models.schemas import Courier_create
from models.models import Courier

couriers_api = APIRouter(tags=["courier"], prefix="/courier")

@couriers_api.post('/')
async def create_courier(
        item: Courier_create,
        db: AsyncSession = Depends(get_session)):
    try:
        stmt = insert(Courier).values(**item.dict())
        await db.execute(stmt)
        await db.commit()
        return item
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Произошла ошибка при добавлении объекта: {e}")



@couriers_api.get('/')
async def get_couriers(db: AsyncSession = Depends(get_session)):
    try:
        stmt = select(Courier.id, Courier.name)
        couriers = await db.execute(stmt)
        return couriers.mappings().all()
    except Exception as e:
        print(e)
        return e


@couriers_api.get('/{id}')
async def get_courier(
        id_courier: uuid.UUID,
        db: AsyncSession = Depends(get_session)):
    try:
        courier = await db.execute(select(Courier).filter(Courier.id == id_courier))
        return courier.mappings().all()
    except Exception as e:
        print(e)
        return e