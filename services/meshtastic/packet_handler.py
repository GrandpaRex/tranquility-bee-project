def process_packet(packet):
    if packet is None:
        return
        
    packet_type = packet.get("decoded", {}).get("portnum")
    if packet_type == "TELEMETRY_APP":
        print("Telemetry packet received")
        metrics = packet.get("decoded", {}).get("telemetry", {}).get("deviceMetrics", {})
        battery = metrics.get("batteryLevel")
        voltage = metrics.get("voltage")
        channel = metrics.get("channelUtilization")
        airtime = metrics.get("airUtilTx")
        uptime_hours = None
        if metrics.get("uptimeSeconds") is not None:
            uptime_hours = metrics.get("uptimeSeconds") // 3600
        print("___Metrics___")
        print(f"Battery level: {battery}")
        print(f"Voltage: {voltage}")
        print(f"Channel utilization: {channel}")
        print(f"Airtime: {airtime}")
        print(f"Uptime hours: {uptime_hours}")
    elif packet_type == "TEXT_MESSAGE_APP":
        print("Text message received")
    else:
        print("Other packet type received")
        
    sender = packet.get("fromId", "Missing")
    receiver = packet.get("toId", "Missing")
    rssi = packet.get("rxRssi")
    snr = packet.get("rxSnr")
    print(f"From: {sender} | To: {receiver} | RSSI: {rssi} | SNR: {snr}")