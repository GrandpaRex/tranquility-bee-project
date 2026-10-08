import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from packet_handler import process_packet
import time

def on_receive(packet, interface):
    process_packet(packet)
    
def serial_interface():
    serialInterface = meshtastic.serial_interface.SerialInterface(devPath="/dev/ttyACM0")
    return serialInterface

def shutdown(connection):
    if connection is not None:
        connection.close()
        print("THG1 connection closed")
    
if __name__ == '__main__':
    connection = None
    
    try:
        pub.subscribe(on_receive, "meshtastic.receive")
        connection = serial_interface()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutdown requested")
    except Exception as error:
        print(f"THG1 error: {error}")
    finally:
        shutdown(connection)
