import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel


class Courier_create(BaseModel):
    id_courier: uuid.UUID
    name: str
    districts: List[str]
    # avg_order_complete_time: datetime
    # avg_day_orders: int
    # active_order: dict
