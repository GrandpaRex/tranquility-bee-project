import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from services.meshtastic.packet_handler import process_packet
from services.meshtastic.mqtt_publisher import serialize_telemetry
from services.common.mqtt_client import create_mqtt_client
import time

def on_receive(packet, interface, mqtt_client):
    record = process_packet(packet)
    if record is not None:
        message = serialize_telemetry(record)
        result = mqtt_client.publish(
            "tranquility/telemetry/device",
            message,
            qos=1
        )
        print(f"[MQTT] Publish queued: {result.rc}")
    
def serial_interface():
    serialInterface = meshtastic.serial_interface.SerialInterface(devPath="/dev/ttyACM0")
    return serialInterface

def shutdown(connection):
    if connection is not None:
        connection.close()
        print("THG1 connection closed")
    
if __name__ == '__main__':
    connection = None
    mqtt_client = None
    
    try:
        mqtt_client = create_mqtt_client("tranquility-thg1")
        mqtt_client.connect("127.0.0.1", 1883, 60)
        mqtt_client.loop_start()
        def receive_callback(packet, interface):
            on_receive(packet, interface, mqtt_client)
            
        pub.subscribe(receive_callback, "meshtastic.receive")
        connection = serial_interface()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutdown requested")
    except Exception as error:
        print(f"THG1 error: {error}")
    finally:
        if mqtt_client is not None:
            mqtt_client.disconnect()
            mqtt_client.loop_stop()
        shutdown(connection)
