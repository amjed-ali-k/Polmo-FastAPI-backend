from typing import List

from fastapi import Depends, HTTPException, APIRouter, Header
from starlette import status

from models.sensordata import SensorReading
from services.sensor import get_last_value, get_last_values

r = APIRouter()
tagname = 'SensorNode'
valid_sensors = ['NO2', 'CO2', 'CH4', 'CO', 'PM1.0', 'PM2.0', 'PM10', 'O3', 'SO2']


@r.get('/sensor/{node}/{pollutant}/last/', response_model=SensorReading, tags=[tagname])
async def get_last_reading(node: str, pollutant: str):
    if pollutant not in valid_sensors:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Sensor name is invalid")
    res = await get_last_value(pollutant, node)
    if not res:
        raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail="No data available")
    return res


@r.get('/sensor/{node}/{pollutant}/days/{days}', response_model=List[SensorReading], tags=[tagname])
async def get_last_days_reading(node: str, pollutant: str, days:int):
    if pollutant not in valid_sensors:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Sensor name is invalid")
    res = await get_last_values(pollutant, node, days)
    if not res:
        raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail="No data available")
    return res