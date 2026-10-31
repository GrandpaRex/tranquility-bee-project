import discord
import os
import paho.mqtt.client as mqtt
import json
from services.common.mqtt_client import create_mqtt_client
import asyncio
import time


token = os.getenv("DISCORD_BOT_TOKEN")
channel_id = os.getenv("DISCORD_STATUS_CHANNEL_ID")
if channel_id is None:
    raise ValueError("Discord status channel ID is missing")
channel_id = int(channel_id)
message_id = os.getenv("DISCORD_STATUS_MESSAGE_ID")
if message_id is None:
    raise  ValueError("Discord status message ID is missing")
NODE_MESSAGES_FILE = "/srv/tranquility/discord/node_messages.json"
STATUS_MESSAGE_FILE = "/srv/tranquility/discord/status_message_id.txt"
message_id = int(message_id)
# Restore the current status message ID if one was saved
try:
    with open(STATUS_MESSAGE_FILE, "r") as file:
        message_id = int(file.read().strip())
except FileNotFoundError:
    pass
latest_telemetry = {}
last_heard = {}
node_message_ids = {}

intents = discord.Intents.default()
discord_client = discord.Client(intents=intents)

async def update_bot_message(channel, embed):
    global message_id

    try:
        # Try to update the existing status message
        message = await channel.fetch_message(message_id)
        await message.edit(embed=embed)

    except discord.NotFound:
        # The old message was deleted, so recreate it
        print("[Discord] Main status message missing. Recreating...")

        message = await channel.send(embed=embed)
        message_id = message.id

        # Save the replacement message ID
        temp_file = STATUS_MESSAGE_FILE + ".tmp"

        with open(temp_file, "w") as file:
            file.write(str(message_id))

        os.replace(temp_file, STATUS_MESSAGE_FILE)

        print(f"[Discord] New status message ID: {message_id}")

    return message

@discord_client.event
async def on_ready():
    print(f"Logged in as {discord_client.user}")

    channel = discord_client.get_channel(channel_id)

    if channel is not None:
        embed = build_bot_embed()
        message = await update_bot_message(channel, embed)

        print("[Discord] Status embed set")
        print(f"[Discord] Status message ID: {message.id}")
    else:
        print(f"[Discord] Channel {channel_id} not found")

    if not hasattr(discord_client, "status_task"):
        discord_client.status_task = asyncio.create_task(
            update_status_embed()
        )

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
    # Save the latest telemetry received from this node
    latest_telemetry[sender] = record
    
    # Record when the homehost received this telemetry
    last_heard[sender] = discord.utils.utcnow()
    
    print(f"[Telemetry] Tracking {len(latest_telemetry)} node(s): {list(latest_telemetry.keys())}")

def load_node_message_ids():
    try:
        with open(NODE_MESSAGES_FILE, "r") as file:
            node_message_ids = json.load(file)
    except FileNotFoundError:
        return {}

    return node_message_ids

def save_node_message_ids():
    temp_file = NODE_MESSAGES_FILE + ".tmp"

    # Write our dictionary to the temporary file
    with open(temp_file, "w") as file:
        json.dump(node_message_ids, file)

    # Replace the original after closing the temporary file
    os.replace(temp_file, NODE_MESSAGES_FILE)
    
async def update_node_embeds():
    channel = discord_client.get_channel(channel_id)

    if channel is None:
        print("[Discord] Node status channel not found")
        return
    
    for sender, record in latest_telemetry.items():
        # Build an embed for this node
        embed = build_node_embed(sender, record)

        # Check if the node already has a Discord message
        if sender in node_message_ids:
            try:   
                print(f"[Discord] Updating existing node: {sender}")
                message = await channel.fetch_message(node_message_ids[sender])
                await message.edit(embed=embed)
            
            except discord.NotFound:
                print(f"[Discord] Existing node not found, creating a new node: {sender}")
                message = await channel.send(embed=embed)
                node_message_ids[sender] = message.id
                save_node_message_ids()
        else:
            print(f"[Discord] Creating new node: {sender}")
            message = await channel.send(embed=embed)
            node_message_ids[sender] = message.id
            save_node_message_ids()

def build_bot_embed():
    is_online = discord_client.is_ready()
    
    if is_online:
        color_status=discord.Color.green()
        status_text="🟢 Online"
    else:
        color_status=discord.Color.yellow()
        status_text="🟡 Starting Up"
    
    embed = discord.Embed(
        title="🐝 Tranquility Bee Monitor",
        description="Telemetry monitoring system initialized.",
        color=color_status
    )
    
    embed.add_field(
        name="Status",
        value=status_text,
        inline=False
    )
    
    return embed

def build_node_embed(sender, record):
    heard_at = last_heard.get(sender)
    
    if heard_at is None:
        health_status = "⚪ Unknown"
        heard_display = "Unknown"
        color_status = discord.Color.grey()
    else:
        heard_display = discord.utils.format_dt(heard_at, "R")
        age_seconds = (discord.utils.utcnow() - heard_at).total_seconds()
        if age_seconds < 300:
            health_status = "🟢 Online"
            color_status = discord.Color.green()
        elif 300 <= age_seconds <= 900:
            health_status = "🟡 Stale"
            color_status = discord.Color.yellow()
        elif age_seconds > 900:
            health_status = "🔴 Offline"
            color_status = discord.Color.red()
        
    embed = discord.Embed(
        title=f"📡 Node: {sender}",
        color=color_status
    )

    battery = record.get("battery")
    voltage = record.get("voltage")

    # Meshtastic uses values above 100 for external power
    if isinstance(battery, (int, float)) and battery > 100:
        battery_display = "External Power"
    elif battery is None:
        battery_display = "Unknown"
    else:
        battery_display = f"{battery}%"

    voltage_display = (
        f"{voltage} V" if voltage is not None else "Unknown"
    )
    
    embed.add_field(
        name="Status",
        value=health_status,
        inline=False
    )

    embed.add_field(
        name="Telemetry",
        value=(
            f"Battery: {battery_display}\n"
            f"Voltage: {voltage_display}\n"
            f"📶 Last Heard: {heard_display}"
        ),
        inline=False
    )

    # The Discord embed refreshes every 30 seconds
    embed.add_field(
        name="🕒 Last Updated",
        value=discord.utils.format_dt(
            discord.utils.utcnow(), style="T"
        ),
        inline=False
    )
    
    return embed

async def update_status_embed():
    channel = discord_client.get_channel(channel_id)

    if channel is None:
        print("[Discord] Status channel not found")
        return

    while not discord_client.is_closed():
        embed = build_bot_embed()

        await update_bot_message(channel, embed)
        print("[Discord] Status embed updated")

        await update_node_embeds()

        await asyncio.sleep(30)
    
if __name__ == "__main__":
    mqtt_client = None
    # Restore saved Discord node message IDs
    node_message_ids.update(load_node_message_ids())
        
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
