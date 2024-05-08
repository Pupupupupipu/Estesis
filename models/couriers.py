import uuid
from datetime import datetime
from sqlalchemy import Column, String, ARRAY, DateTime, Integer, JSON, Table
from sqlalchemy.dialects.postgresql import UUID

from db import metadata

Courier = Table(
    "courier",
    metadata,
    Column("id_courier", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("name", String, nullable=False),
    Column("districts", ARRAY(String), nullable=False),
    Column("avg_order_complete_time", DateTime, default=datetime.now()),
    Column("avg_day_orders", Integer, default=0),
    Column("active_order", JSON, default={}),
)


