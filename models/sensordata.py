from enum import Enum
from typing import Optional, List
from pydantic import BaseModel
from pydantic.class_validators import validator
from pydantic.types import UUID4
import datetime


class SensorReading(BaseModel):
    value: float
    sensor: str
    time: datetime.datetime
    node: UUID4


class SensorReadingSL(SensorReading):
    key: float 
    @validator('key', pre=True)
    def generate_key(cls, v, values, **kwargs):
         if 'time' in values:
             return values['time'].timestamp()

    @validator('time')
    def serialize_date(cls, v: datetime.datetime):
        return v.timestamp()

    @validator('node', 'key')
    def serialize_uuid(cls, v:UUID4):
        return v.hex


class SensorPost(SensorReading):
    token: str


class NodeDetailsStatus(str, Enum):
    online = 'online'
    offline = 'offline'
    pending = 'pending'
    dismantled = 'dismantled'
    idle = 'idle'


class NodeType(str, Enum):
    urban = 'urban'
    green = 'green'
    indoor = 'indooor'


class SensorDetailsHardware(BaseModel):
    name: str
    type: str = 'ElectroChemical'
    range: str = "0-1000ppm"


class SensorDetailsConfig(BaseModel):
    min: int = 0
    max: int = 100
    unit: str = 'ppm'
    delay: int = 15000


class SensorDetails(BaseModel):
    key: UUID4
    name: str
    slug: str
    description: str
    hardware: SensorDetailsHardware
    config: SensorDetailsConfig


class NodeDetails(BaseModel):
    _id: UUID4
    name: str
    flavour: NodeType
    status: NodeDetailsStatus
    doc: datetime.datetime
    address: str
    battery: int
    charging: bool
    on: datetime.datetime
    updated: datetime.datetime
    sensors: List[SensorDetails]


class SensorReadingResponse(SensorReading):
    sensor_id: UUID4
