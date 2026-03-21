import asyncio
from telethon import TelegramClient, events
import os

print("=" * 50)
print("🚀 BOT STARTING")
print("=" * 50)

print("\n📁 Files in directory:")
for file in os.listdir('.'):
    print(f"   - {file}")

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

print(f"\n📡 Monitoring {len(source_channels)} channels:")
for channel in source_channels:
    print(f"   - @{channel}")
print(f"🎯 Forwarding to: @{target_channel}")
print(f"🔗 Your channel link: {your_link}")

# NEW SESSION FILE NAME
session_file = "bot_working_final.session"

if os.path.exists(session_file):
    size = os.path.getsize(session_file)
    print(f"✅ Session file found! Name: {session_file}, Size: {size} bytes")
else:
    print(f"❌ Session file NOT found: {session_file}")
    exit(1)

client = TelegramClient(session_file, API_ID, API_HASH)

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        if chat.username and chat.username in source_channels:
            print(f"\n📨 Message from @{chat.username}")
            text = event.raw_text or ""
            new_text = f"{text}\n\n{your_link}\nሰላም ለእናንተ!"
            
            if event.message.media:
                await client.send_file(target_channel, event.message.media, caption=new_text)
                print("📤 Forwarded with media")
            else:
                await client.send_message(target_channel, new_text)
                print(f"📤 Forwarded: {new_text[:50]}...")
            print("✅ Done!")
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    try:
        print("\n🔌 Connecting to Telegram...")
        await client.start()
        me = await client.get_me()
        print(f"✅ Connected successfully!")
        print(f"👤 Logged in as: @{me.username}")
        print("\n🤖 Bot is running and waiting for messages...\n")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Failed to start: {e}")

if __name__ == "__main__":
    asyncio.run(main())
