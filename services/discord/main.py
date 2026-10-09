import discord
import os
import paho.mqtt.client as mqtt
import json
from services.common.mqtt_client import create_mqtt_client


token = os.getenv("DISCORD_BOT_TOKEN")
channel_id = os.getenv("DISCORD_STATUS_CHANNEL_ID")
if channel_id is None:
    raise ValueError("Discord status channel ID is missing")
channel_id = int(channel_id)
message_id = os.getenv("DISCORD_STATUS_MESSAGE_ID")
if message_id is None:
    raise  ValueError("Discord status message ID is missing")
message_id = int(message_id)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    embed = discord.Embed(
        title="🐝 Tranquility Bee Monitor",
        description="Telemetry monitoring system initialized.",
        color=discord.Color.green()
    )

    embed.add_field(
        name="📡 THG1 Gateway",
        value="Awaiting telemetry...",
        inline=False
    )
    
    channel = client.get_channel(channel_id)
    if channel is not None:
        message = await channel.fetch_message(message_id)
        await message.edit(embed=embed)
        print("[Discord] Status embed set")
        print(f"[Discord] Status message ID: {message.id}")
    else:
        print(f"[Discord] Channel {channel_id} not found")

def on_mqtt_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("[MQTT] Discord bot connected")
        client.subscribe("tranquility/telemetry/device", qos=1)
    else:
        print(f"[MQTT] Connection failed: {reason_code}")
    
def on_mqtt_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    print(f"[MQTT] Received: {payload}")
    
if __name__ == "__main__":
    mqtt_client = None
        
    try:
        mqtt_client = create_mqtt_client("tranquility-discord")
        mqtt_client.on_connect = on_mqtt_connect
        mqtt_client.on_message = on_mqtt_message
        mqtt_client.connect("127.0.0.1", 1883, 60)
        mqtt_client.loop_start()

        if token is not None:
            client.run(token)
        else:
            print("Discord bot token is missing")
    finally:
        if mqtt_client is not None:
            mqtt_client.disconnect()
            mqtt_client.loop_stop()
