import uuid
from datetime import time
from sqlalchemy import Column, String, ARRAY, Integer, JSON, ForeignKey, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Courier (Base):
    __tablename__ = "courier"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    districts = Column(ARRAY(String), nullable=False)
    avg_order_complete_time = Column(Time, default=time(0,0,0))
    avg_day_orders = Column(Integer, default=0)
    active_order = Column(JSON, default=None)

class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_courier = Column(UUID(as_uuid=True), ForeignKey(Courier.id))
    name = Column(String, nullable=False)
    district = Column(String, nullable=False)
    status = Column(Integer, default=None)



