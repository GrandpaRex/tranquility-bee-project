import json
import paho.mqtt.client as mqtt
import os

def serialize_telemetry(record):
    if record is None:
        return None
    
    message = json.dumps(record)
    return message

def create_mqtt_client():
    username = os.getenv("MQTT_USERNAME")
    password = os.getenv("MQTT_PASSWORD")
    if username is None or password is None:
        raise ValueError("Username or Password is None")
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="tranquility-thg1"
    )
    client.username_pw_set(username, password)
    
    return client