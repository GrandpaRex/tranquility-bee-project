import discord
import os

token = os.getenv("DISCORD_BOT_TOKEN")
channel_id = os.getenv("DISCORD_STATUS_CHANNEL_ID")
if channel_id is None:
    raise ValueError("Discord status channel ID is missing")
channel_id = int(channel_id)

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
        await channel.send(embed=embed)
        print("[Discord] Status embed set")
    else:
        print(f"[Discord] Channel {channel_id} not found")
    
if __name__ == "__main__":
    if token is not None:
        client.run(token)
    else:
        print("Discord bot token is mising")