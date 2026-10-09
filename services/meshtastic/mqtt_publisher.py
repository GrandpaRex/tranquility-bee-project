import json
import paho.mqtt.client as mqtt

def serialize_telemetry(record):
    if record is None:
        return None
    
    message = json.dumps(record)
    return message

def create_mqtt_client():
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="tranquility-thg1"
    )
    return client