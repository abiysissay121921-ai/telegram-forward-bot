import asyncio
from telethon import TelegramClient, events
import os

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT")
print("=" * 50)

# Bot token
BOT_TOKEN = "8602729297:AAGog9z7FVCs8--IoajFT4JlS3vwga8pxUI"

API_ID = 37303512
API_HASH = "dff48ddff61546b05d1d507a6c508ee8"

source_channels = [
    "ayuzehabeshanews",
    "Addis_News",
    "NatnaelMekonnen21",
    "tikvahethiopia",
    "eliasmeseret",
    "TikvahUniversity",
    "abiyselol",
]

target_channel = "NewsWith_Abiy"
your_link = "https://t.me/NewsWith_Abiy"

print(f"\n🤖 Using bot token")
print(f"📡 Monitoring {len(source_channels)} channels:")
for channel in source_channels:
    print(f"   - @{channel}")
print(f"🎯 Forwarding to: @{target_channel}")

# Create client with bot token
client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

forwarded_messages = set()

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        if chat.username and chat.username in source_channels:
            msg_id = f"{chat.id}_{event.id}"
            if msg_id in forwarded_messages:
                return
            forwarded_messages.add(msg_id)
            print(f"\n📨 From @{chat.username}")
            text = event.raw_text or ""
            new_text = f"{text}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            if event.message.media:
                await client.send_file(target_channel, event.message.media, caption=new_text[:1024])
            else:
                await client.send_message(target_channel, new_text[:4096])
            print("✅ Forwarded")
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("\n🔌 Connecting...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Connected as: @{me.username}")
    print("🤖 Bot running...\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
