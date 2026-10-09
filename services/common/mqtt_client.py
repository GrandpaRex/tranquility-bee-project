import os
import paho.mqtt.client as mqtt

def create_mqtt_client(client_id):
    username = os.getenv("MQTT_USERNAME")
    password = os.getenv("MQTT_PASSWORD")
    if username is None or password is None:
        raise ValueError("Username or Password is None")
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=client_id
    )
    client.username_pw_set(username, password)

    return client