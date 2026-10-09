from .sender_auth import is_approved
def process_packet(packet):
    if packet is None:
        return
        
    packet_type = packet.get("decoded", {}).get("portnum")
    if packet_type == "TELEMETRY_APP":
        sender = packet.get("fromId") or packet.get("from")
        if isinstance(sender, int):
            sender = f"!{sender:08x}"
        if not is_approved(sender):
            print(f"[Auth] Rejected packet from {sender}")
            return None
        receiver = packet.get("toId", "Missing")
        rssi = packet.get("rxRssi")
        snr = packet.get("rxSnr")
        metrics = packet.get("decoded", {}).get("telemetry", {}).get("deviceMetrics", {})
        if not metrics:
            return None
        battery = metrics.get("batteryLevel")
        voltage = metrics.get("voltage")
        channel = metrics.get("channelUtilization")
        airtime = metrics.get("airUtilTx")
        uptime_hours = None
        if metrics.get("uptimeSeconds") is not None:
            uptime_hours = metrics.get("uptimeSeconds") // 3600
        record = {
             "sender": sender,
             "receiver": receiver,
             "rssi": rssi,
             "snr": snr,
             "battery": battery,
             "voltage": voltage,
             "channel": channel,
             "airtime": airtime,
             "uptime_hours": uptime_hours
        }
        return record
    elif packet_type == "TEXT_MESSAGE_APP":
        print("Text message received")
    else:
        print("Other packet type received")