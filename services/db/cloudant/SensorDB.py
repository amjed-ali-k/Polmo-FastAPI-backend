import json
from typing import Optional

from ibm_cloud_sdk_core import ApiException
from ibmcloudant.cloudant_v1 import CloudantV1, Document, IndexField, IndexDefinition

from models.sensordata import SensorReading

client = CloudantV1.new_instance()
sensor_db_name = "sensor_data"


async def read_last_sensor_value(sensorname, nodeid) -> Optional[SensorReading]:
    s = {"sensor": {"$eq": sensorname},
         # "node": {"$eq": nodeid}
         }
    sort = [{"time":'desc'}]
    try:
        document = client.post_find(db=sensor_db_name, selector=s, sort=sort, limit=1).get_result()
        if len(document["docs"]) > 0:
            return SensorReading(**document["docs"][0])
        else:
            return None
    except Exception as e:
        print(e)
        return None


async def read_last_values(sensorname, nodeid, fromdate):
    s = {"sensor": {"$eq": sensorname},
         # "node": {"$eq": nodeid}
         "time": {"$gt": fromdate}
         }
    sort = [{"time": 'desc'}]
    try:
        document = client.post_find(db=sensor_db_name, selector=s, sort=sort).get_result()
        print(json.dumps(document, indent=3))
        if len(document["docs"]) > 0:
            print(f'Total results : {len(document["docs"])}')
            results = []
            for item in document["docs"]:
                sensor_reading = SensorReading(**item)
                results.append(sensor_reading)
            return results
        else:
            return None
    except Exception as e:
        print(e)
        return None