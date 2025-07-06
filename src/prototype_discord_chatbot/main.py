from dotenv import load_dotenv
import os

load_dotenv()

import discord

intents = discord.Intents.default()
intents.message_content = True  # 핵심
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"{client.user} is ready.")

@client.event
async def on_message(message):
    print("on_message============")
    print(message)
    if message.author.bot:
        return  # 자기 자신/다른 봇은 무시
    print(message.content)
    if client.user in message.mentions:
        # GPT에 유저 메시지 전달
        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()
        
        await message.channel.send("test")

client.run(os.getenv("DISCORD_BOT_TOKEN"))