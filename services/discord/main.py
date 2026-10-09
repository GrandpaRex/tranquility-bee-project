import discord
import os

token = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    
if __name__ == "__main__":
    if token is not None:
        client.run(token)
    else:
        print("Discord bot token is mising")