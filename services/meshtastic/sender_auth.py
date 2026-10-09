APPROVED_SENDERS = {
    "!ca27b4f1": "Tranquility Host Node",
    "!f4dd03b6": "THG1 Home Gateway"
}

def is_approved(sender):
    return sender in APPROVED_SENDERS