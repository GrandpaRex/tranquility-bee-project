import discord
import os
import paho.mqtt.client as mqtt
import json
from services.common.mqtt_client import create_mqtt_client
import asyncio


token = os.getenv("DISCORD_BOT_TOKEN")
channel_id = os.getenv("DISCORD_STATUS_CHANNEL_ID")
if channel_id is None:
    raise ValueError("Discord status channel ID is missing")
channel_id = int(channel_id)
message_id = os.getenv("DISCORD_STATUS_MESSAGE_ID")
if message_id is None:
    raise  ValueError("Discord status message ID is missing")
message_id = int(message_id)
latest_telemetry = {}

intents = discord.Intents.default()
discord_client = discord.Client(intents=intents)

@discord_client.event
async def on_ready():
    print(f"Logged in as {discord_client.user}")
    embed = build_status_embed()
    
    channel = discord_client.get_channel(channel_id)
    if channel is not None:
        message = await channel.fetch_message(message_id)
        await message.edit(embed=embed)
        print("[Discord] Status embed set")
        print(f"[Discord] Status message ID: {message.id}")
    else:
        print(f"[Discord] Channel {channel_id} not found")

    if not hasattr(discord_client, "status_task"):
        discord_client.status_task = asyncio.create_task(update_status_embed())

def on_mqtt_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("[MQTT] Discord bot connected")
        client.subscribe("tranquility/telemetry/device", qos=1)
    else:
        print(f"[MQTT] Connection failed: {reason_code}")

def on_mqtt_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    print(f"[MQTT] Received: {payload}")

    try:
        record = json.loads(payload)
    except json.JSONDecodeError:
        print("[MQTT] Invalid JSON received")
        return

    if discord_client.is_ready():
        discord_client.loop.call_soon_threadsafe(store_telemetry, record)
    
def store_telemetry(record):
    sender = record.get("sender")
    if sender is None:
        return
    latest_telemetry[sender] = record
    print(f"[Telemetry] Tracking {len(latest_telemetry)} node(s): {list(latest_telemetry.keys())}")

def build_status_embed():
    embed = discord.Embed(
        title="🐝 Tranquility Bee Monitor",
        description="Telemetry monitoring system initialized.",
        color=discord.Color.green()
    )

    for sender, record in latest_telemetry.items():
        battery = record.get("battery")
        voltage = record.get("voltage")
        embed.add_field(
            name=f"📡 Node: {sender}",
            value=f"Node: {sender} \nBattery: {battery} \nVoltage: {voltage} V",
            inline=False
        )
    return embed

async def update_status_embed():
    channel = discord_client.get_channel(channel_id)

    if channel is None:
        print("[Discord] Status channel not found")
        return

    message = await channel.fetch_message(message_id)

    while not discord_client.is_closed():
        embed = build_status_embed()
        await message.edit(embed=embed)
        print("[Discord] Status embed updated")
        await asyncio.sleep(30)
    
if __name__ == "__main__":
    mqtt_client = None
        
    try:
        mqtt_client = create_mqtt_client("tranquility-discord")
        mqtt_client.on_connect = on_mqtt_connect
        mqtt_client.on_message = on_mqtt_message
        mqtt_client.connect("127.0.0.1", 1883, 60)
        mqtt_client.loop_start()

        if token is not None:
            discord_client.run(token)
        else:
            print("Discord bot token is missing")
    finally:
        if mqtt_client is not None:
            mqtt_client.disconnect()
            mqtt_client.loop_stop()
