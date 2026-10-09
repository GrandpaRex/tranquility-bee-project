import json
def serialize_telemetry(record):
    if record is None:
        return None
    
    message = json.dumps(record)
    return message