def process_packet(packet):
    if packet is None:
        return
        
    packet_type = packet.get("decoded", {}).get("portnum")
    if packet_type == "TELEMETRY_APP":
        print("Telemetry packet received")
        print(packet)
    elif packet_type == "TEXT_MESSAGE_APP":
        print("Text message received")
    else:
        print("Other packet type received")
        
    sender = packet.get("fromId", "Missing")
    receiver = packet.get("toId", "Missing")
    rssi = packet.get("rxRssi")
    snr = packet.get("rxSnr")
    print(f"From: {sender} | To: {receiver} | RSSI: {rssi} | SNR: {snr}")