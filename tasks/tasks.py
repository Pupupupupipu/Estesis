from celery import Celery
import redis
import uuid
import json
from celery.schedules import crontab
from sqlalchemy import DateTime
from datetime import datetime, timedelta


celery = Celery('tasks', broker='redis://localhost:6379')

celery.conf.beat_schedule = {
    'create_daily_record': {
        'task': 'create_daily_record',
        'schedule': crontab(minute=0, hour=0),  # Запуск каждый день в 00:00
    },
}
celery.conf.timezone = 'UTC'
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def update_daily_record(data: dict,
                        current_date: str):
    all_orders = redis_client.get(current_date)
    all_orders = json.loads(all_orders)
    all_orders[str(data['order_id'])] = {
        "start_time": str(data['start_time']),
        "lead_time": str(data['lead_time']),
        "status": data['status'],
        "courier_id": str(data['courier_id'])
    }

    redis_client.set(current_date, json.dumps(all_orders))

def time_to_seconds(time_str: str):
    hours, minutes, seconds = map(float, time_str.split(':'))
    time_seconds = timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds()

    return time_seconds

def seconds_to_time(time_seconds: int):
    return f'{int(time_seconds // 3600)}:{int((time_seconds % 3600) // 60)}:{time_seconds % 60}'



@celery.task
def post_order(item: dict):
    current_date = str(datetime.now().date().isoformat())

    order_id = str(item['order_id'])
    order_data = {
        order_id: {
            "start_time": str(item['start_time']),
            "lead_time": str(item['lead_time']),
            "status": item['status'],
            "courier_id": str(item['courier_id'])
        }
    }

    if not redis_client.exists(current_date):
        redis_client.setex(current_date, 60*60*24, json.dumps(order_data))
        # live_time = 60*60*24
        # redis_client.expire(current_date, live_time)
        # redis_client.
    else:
        update_daily_record(item, current_date)



@celery.task
def close_order(courier_id: uuid.UUID,
                order_id: uuid.UUID,
                close_time: DateTime):
    #close order in daily record
    current_date = str(datetime.now().date().isoformat())
    orders_json = redis_client.get(current_date)
    orders = json.loads(orders_json)

    orders[f'{order_id}']['status'] = 2
    lead_time = close_time - datetime.fromisoformat(orders[f'{order_id}']['start_time'])
    orders[f'{order_id}']['lead_time'] = str(lead_time)

    update_order_str = json.dumps(orders)
    redis_client.set(str(current_date), update_order_str)

    #update info about courier
    info_courier = {
        str(courier_id): {
            'start_work': str(datetime.now().date().isoformat()),
            'all_time': str(lead_time),
            'avg_time': str(lead_time),
            'all_orders': 1,
            'avg_orders_closed': 1
        }
    }
    if not redis_client.exists("info_couriers"):
        redis_client.set("info_couriers", json.dumps(info_courier))

    elif str(courier_id) not in json.loads(redis_client.get("info_couriers")):
        couriers = json.loads(redis_client.get("info_couriers"))
        couriers[f'{courier_id}']={
            'start_work': str(datetime.now().date().isoformat()),
            'all_time': str(lead_time),
            'avg_time': str(lead_time),
            'all_orders': 1,
            'avg_orders_closed': 1
        }
        redis_client.set("info_couriers", json.dumps(couriers))
    else:
        couriers = json.loads(redis_client.get("info_couriers"))
        start_work = datetime.fromisoformat(couriers[f'{courier_id}']['start_work']).date()
        count_days = int((datetime.now().date() - start_work).days) + 1

        all_time_sec = time_to_seconds(couriers[f'{courier_id}']['all_time'])
        update_all_time = all_time_sec + time_to_seconds(str(lead_time))
        couriers[f'{courier_id}']['all_time'] = seconds_to_time(update_all_time)

        all_orders = int(couriers[f'{courier_id}']['all_orders'])
        couriers[f'{courier_id}']['all_orders'] = all_orders + 1

        avg_time_seconds = update_all_time / couriers[f'{courier_id}']['all_orders']
        couriers[f'{courier_id}']['avg_time'] = seconds_to_time(avg_time_seconds)

        all_orders = couriers[f'{courier_id}']['all_orders']
        couriers[f'{courier_id}']['avg_orders_closed'] = all_orders / count_days

        redis_client.set("info_couriers", json.dumps(couriers))


