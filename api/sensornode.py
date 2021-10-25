import json
import os
from typing import List
import aiofiles
from fastapi import HTTPException, APIRouter
from pydantic.types import UUID4
from starlette import status
from config import settings
from models.sensordata import NodeDetails, SensorDetails, SensorReading, SensorPost, SensorReadingResponse
from services.db.deta.SensorDB import fetch_node_details, fetch_sensor_details, read_last_sensor_reading, store_data_to_deta_db
from services.sensor import get_last_value

r = APIRouter()
tagname = 'SensorNode'
valid_sensors = ['NH3', 'Humidity', 'Temperature', 'H2S', 'NO2',
                 'CO2', 'CH4', 'CO', 'PM1.0', 'PM2.5', 'PM10', 'O3', 'SO2']


@r.get('/sensor/details/polmo/1.0', tags=[tagname])
async def get_sensor_hardware_details():
    async with aiofiles.open(os.getcwd() + '/docs/' + 'sensors.json', mode='r') as f:
        sensors = json.loads(await f.read())
    return sensors


@r.get('/sensor/node/{node}/last/all', response_model=List[SensorReading], tags=[tagname])
async def get_last_reading_for_all_gases(node: str):
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
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Sensor name is invalid")
    res = await get_last_value(pollutant, node)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_206_PARTIAL_CONTENT, detail="No data available")
    return res


@r.post('/update/value/', tags=[tagname])
async def add_sensor_reading(reading: SensorPost):
    if reading.token != settings.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Token is invalid")
    data = SensorReading(**reading.dict())
    store_data_to_deta_db(data)
    return "Success"


# NEW ROUTES


@r.get('/node/{node_id}/details/', response_model=NodeDetails, tags=[tagname])
async def get_node_details_from_node_id(node_id: UUID4):
    res = await fetch_node_details(node_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return res

@r.get('/sensor/{sensor_id}/details/', response_model=SensorDetails, tags=[tagname])
async def get_sensor_details_from_sensor_id(sensor_id: UUID4):
    res = await fetch_sensor_details(sensor_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return res

@r.get('/node/{node_id}/latest/{sensor_id}/', response_model=SensorReadingResponse, tags=[tagname])
async def get_latest_sensor_readings_from_individual_sensor(node_id: UUID4, sensor_id: UUID4):
    reading = await read_last_sensor_reading(node_id, sensor_id)
    if not reading:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    sensor = await fetch_sensor_details(sensor_id)
    if not sensor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return SensorReadingResponse(**reading.dict(), sensor_id=sensor.key)

@r.get('/node/{node_id}/latest/all/', response_model=List[SensorReadingResponse], tags=[tagname])
async def get_latest_sensor_readings_from_all_available_sensors(node_id: UUID4):
    node = await fetch_node_details(node_id)
    res = []
    for sensor in node.sensors:
        try:
            _sensor = await read_last_sensor_reading(node_id, sensor.key)
            if _sensor:
                res.append(SensorReadingResponse(**_sensor.dict()))
        except:
            continue
    return res

    
@r.get('/history/last/{range}/{sensor_id}', response_model=List[SensorReadingResponse], tags=[tagname])
async def fetch_previous_readings_from_individual_sensor(node_id):
    pass