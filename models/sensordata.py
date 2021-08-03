from typing import Optional

from pydantic import BaseModel


class SensorReading(BaseModel):
    sensor: str
    value: int
    time: str
    node: Optional[str]

