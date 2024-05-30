import json

from fastapi import APIRouter, Depends, HTTPException
import aioredis
from datetime import datetime, time
from sqlalchemy import select, insert, update
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from models.models import Courier
from models.models import Order
from models.schemas import Open_order
from tasks.tasks import post_order, close_order as redis_close_order

orders_api = APIRouter(tags=["order"], prefix="/order")

redis = aioredis.from_url('redis://localhost:6379')
@orders_api.post('/')
async def open_order(
        order: Open_order,
        db: AsyncSession = Depends(get_session)):
    try:
        couriers = await db.execute(select(Courier))
        couriers = couriers.scalars().all()
        free_couriers = [courier for courier in couriers if courier.active_order == None]

        if not free_couriers:
            raise HTTPException(status_code=400, detail="No suitable courier available for this order.")

        couriers_in_same_district = [courier for courier in free_couriers if order.district in courier.districts]

        if not couriers_in_same_district:
            raise HTTPException(status_code=400, detail="No suitable courier available for this order.")

        courier = couriers_in_same_district[0]
        stmt = insert(Order).values( 
             id_courier=courier.id,
             name=order.name,
             district=order.district, 
             status = 1)
        result_order = await db.execute(stmt)
        await db.commit()

        order_id = result_order.inserted_primary_key[0]

        await db.execute(
            update(Courier)
            .where(Courier.id == courier.id)
            .values(active_order={"order_id": str(order_id), "order_name": order.name})
        )
        await db.commit()

        post_order.delay({
            "courier_id": courier.id,
            "start_time": datetime.now(),
            "lead_time": datetime.now(),
            "status": 1,
            "order_id": order_id})

        return {"order_id": order_id, "courier_id": courier.id}
    except Exception as e:
        print(e)
        return e
    

@orders_api.get('/{id}')
async def get_order(id: uuid.UUID,
                    db: AsyncSession = Depends(get_session)):
        try:
            order = await db.execute(select(Order).filter(Order.id == id))
            order = order.scalars().first()

            if order is None:
                raise HTTPException(status_code=500, detail="Order is not exist")
            
            return({
                 "id": order.id,
                 "status": order.status
            })
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=f"Error: {e}")

@orders_api.post('/{id}')
async def close_order(id: uuid.UUID,
                      db: AsyncSession = Depends(get_session)):
    try:
        order = await db.execute(select(Order).filter(Order.id == id))
        order = order.scalars().first()

        if order is None:
            raise HTTPException(status_code=500, detail="Order is not exist")
        if order.status != 1:
            raise HTTPException(status_code=500, detail="Order already closed")
        order.status = 2

        redis_close_order(order.id_courier, order.id, datetime.now())
        update_info_json = await redis.get("info_couriers")
        update_info = json.loads(update_info_json)

        time_str = update_info[f'{order.id_courier}']['avg_time']
        time_str = time_str.split('.')[0]
        hours, minutes, seconds = map(int, time_str.split(':'))

        await db.execute(
            update(Courier)
            .where(Courier.id == order.id_courier)
            .values(
                active_order=None,
                avg_day_orders=int(update_info[f'{order.id_courier}']['avg_orders_closed']),
                avg_order_complete_time=time(hour=hours, minute=minutes, second=seconds)
            ))
        await db.commit()
        print("AAAAAAAAAAAAA", datetime.now(), datetime.utcnow().date())

        return("Order closed")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}")

