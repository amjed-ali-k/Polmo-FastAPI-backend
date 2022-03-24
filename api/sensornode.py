from datetime import datetime
import json, os
from typing import List

import aiofiles
from fastapi import HTTPException, APIRouter
from starlette import status
from config import settings
from models.sensordata import SensorReading, SensorPost
from services.db.deta.SensorDB import store_data_to_deta_db
from services.sensor import get_last_value, get_last_values

r = APIRouter()
tagname = 'SensorNode'
valid_sensors = ['NH3', 'Humidity', 'Temperature', 'H2S', 'NO2', 'CO2', 'CH4', 'CO', 'PM1.0', 'PM2.5', 'PM10', 'O3', 'SO2']


@r.get('/sensor/details/polmo/1.0', tags=[tagname])
async def get_sensor_hardware_details():
    async with aiofiles.open(os.getcwd() + '/docs/' + 'sensors.json', mode='r') as f:
        sensors = json.loads(await f.read())
    return sensors


@r.get('/sensor/node/{node}/last/all', response_model=List[SensorReading], tags=[tagname])
async def get_last_reading_for_all_gases(node:str):
    print(f'Requested for {node}')
    result = []
    for pollutant in valid_sensors:
        res = await get_last_value(pollutant, node)
        if res:
            result.append(res)
    return result


@r.get('/sensor/node/{node}/last/{pollutant}/', response_model=SensorReading, tags=[tagname])
async def get_last_reading(node: str, pollutant: str):
    if pollutant not in valid_sensors:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Sensor name is invalid")
    res = await get_last_value(pollutant, node)
    if not res:
        raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail="No data available")
    return res


@r.get('/sensor/node/{node}/last/{pollutant}/days/{days}', response_model=List[SensorReading], tags=[tagname])
async def get_last_days_reading(node: str, pollutant: str, days: int):
    if pollutant not in valid_sensors:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Sensor name is invalid")
    res = await get_last_values(pollutant, node, days)
    if not res:
        raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail="No data available")
    return res


@r.post('/update/value/', tags=[tagname])
async def add_sensor_reading(reading: SensorReading):
    # if reading.token != settings.SECRET_KEY:
    #     raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Token is invalid")
    data = SensorReading(**reading.dict(), time= datetime.fromtimestamp(reading.time).isoformat())
    store_data_to_deta_db(data)
    return "Success"
