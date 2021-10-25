from typing import Optional, List
from deta import Deta
from pydantic.types import UUID4
from config import settings
from models.sensordata import NodeDetails, SensorDetails, SensorReading, SensorReadingSL

deta = Deta(settings.DETA_BASE_KEY)  # configure your Deta project
sensor_db = deta.AsyncBase('sensor_data')
sensor_cache_db = deta.AsyncBase('sensor_data_cache')
sensor_details_db = deta.AsyncBase('sensor_details')
node_details_db = deta.AsyncBase('node_details')


async def fetch_node_details(key: UUID4):
    res = await node_details_db.get(key.hex)
    await node_details_db.close()
    return NodeDetails(**res) if res else None


async def fetch_sensor_details(key: UUID4):
    res = await sensor_details_db.get(key.hex)
    await sensor_details_db.close()
    return SensorDetails(**res) if res else None


async def store_data_to_deta_db(sensor_data: SensorReading):
    await sensor_db.put(SensorReadingSL(**sensor_data.dict()).dict())
    await sensor_db.close()
    cache_key = "last_live_" + sensor_data.sensor + "_" + sensor_data.node
    await sensor_cache_db.put(SensorReadingSL(**sensor_data.dict()).dict(), key=cache_key)
    await sensor_cache_db.close()


async def read_last_sensor_value(sensorname, nodeid) -> Optional[SensorReading]:
    key = "last_live_" + sensorname + "_" + nodeid
    try:
        sensordata = await sensor_cache_db.get(str(key))
        await sensor_cache_db.close()
        if sensordata:
            return SensorReading(**sensordata)
        else:
            return None
    except Exception as e:
        print(e)
        return None


async def read_last_sensor_reading(node_id: UUID4, sensor_id: UUID4):
    key = "last_live_" + sensor_id.hex + "_" + node_id.hex
    res = await sensor_cache_db.get(key)
    sensor_cache_db.close()
    return SensorDetails(**res) if res else None