from typing import Optional

from pydantic import BaseModel


class SensorReading(BaseModel):
    sensor: str
    value: float
    time: str
    node: Optional[str]


class SensorPost(BaseModel):
     sensor: str
     value: float