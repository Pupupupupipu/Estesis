from typing import List
from pydantic import BaseModel


class Courier_create(BaseModel):
    name: str
    districts: List[str]


class Open_order(BaseModel):
    name: str
    district: str




