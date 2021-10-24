from typing import Optional, List

from models.sensordata import SensorReading
from config import settings
from dateutil.parser import isoparse
from datetime import timedelta, datetime


package = "services.db." + settings.DB
name = "SensorDB"
sensorDB = getattr(__import__(package, fromlist=[name]), name)
from services.db.deta import SensorDB as DetaDB

def iso_format(dt):
    # Convert Date to Javascript ISO Format
    try:
        utc = dt + dt.utcoffset()
    except TypeError as e:
        utc = dt
    isostring = datetime.strftime(utc, '%Y-%m-%dT%H:%M:%S.{0}Z')
    return isostring.format(int(round(utc.microsecond / 1000.0)))


async def get_last_value(pollutant, node) -> Optional[SensorReading]:
    return await DetaDB.read_last_sensor_value(pollutant, node)

