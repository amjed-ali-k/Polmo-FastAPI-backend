from typing import Optional, List

from models.sensordata import SensorReading
from config import settings
from dateutil.parser import isoparse
from datetime import timedelta, datetime

from services.db.cloudant.SensorDB import read_last_values

package = "services.db." + settings.DB
name = "SensorDB"
sensorDB = getattr(__import__(package, fromlist=[name]), name)


def iso_format(dt):
    # Convert Date to Javascript ISO Format
    try:
        utc = dt + dt.utcoffset()
    except TypeError as e:
        utc = dt
    isostring = datetime.strftime(utc, '%Y-%m-%dT%H:%M:%S.{0}Z')
    return isostring.format(int(round(utc.microsecond / 1000.0)))


async def get_last_value(pollutant, node) -> Optional[SensorReading]:
    return await sensorDB.read_last_sensor_value(pollutant, node)


async def get_last_values(pollutant, node, days) -> Optional[List[SensorReading]]:
    # get last date
    last = await sensorDB.read_last_sensor_value(pollutant, node)
    if not last:
        return None
    # calculate dates
    last_date = isoparse(last.time)
    from_date = last_date - timedelta(days=days)
    res = await read_last_values(pollutant, node, iso_format(from_date))
    return res