from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from models.schemas import Courier_create
from models.couriers import Courier as CourierModel

couriers_api = APIRouter(tags=["courier"], prefix="/courier")

@couriers_api.post('/')
async def create_courier(
        item: Courier_create,
        db: AsyncSession = Depends(get_session)):
    try:
        stmt = insert(CourierModel).values(**item.dict())
        await db.execute(stmt)
        await db.commit()
        return item
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Произошла ошибка при добавлении объекта: {e}")



@couriers_api.get('/')
async def get_couriers(db: AsyncSession = Depends(get_session)):
    try:
        couriers = await db.execute(select(CourierModel))
        print(couriers)
        return couriers.scalars().all()
    except Exception as e:
        return e