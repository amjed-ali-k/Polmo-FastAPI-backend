from typing import Optional, List

from deta import Deta
from config import settings
from models.sensordata import SensorReading

deta = Deta(settings.DETA_BASE_KEY)  # configure your Deta project
sensor_db = deta.Base('sensor_data')
sensor_cache_db = deta.Base('sensor_data_cache')


def store_data_to_deta_db(sensor_data: SensorReading):
    sensor_db.put(sensor_data.dict())
    cache_key = "last_" + sensor_data.sensor + "_" + sensor_data.node
    sensor_cache_db.put(sensor_data.dict(), key=cache_key)


async def read_last_sensor_value(sensorname, nodeid) -> Optional[SensorReading]:
    _id = "last_" + sensorname + "_" + nodeid
    try:
        sensordata = sensor_cache_db.get(str(_id))
        if sensordata:
            return SensorReading(**sensordata)
        else:
            return None
    except Exception as e:
        print(e)
        return None
