import asyncio
from telethon import TelegramClient, events
import os

print("=" * 50)
print("🚀 BOT STARTING")
print("=" * 50)

# List all files to see what's there
print("\n📁 Files in directory:")
for file in os.listdir('.'):
    print(f"   - {file}")

API_ID = 37303512
API_HASH = "dff48ddff61546b05d1d507a6c508ee8"

source_channels = [
    "ayuzehabeshanews",
    "Apostolic_Answers_chat",
]
target_channel = "Newswithabiy"
your_link = "https://t.me/Newswithabiy"

print(f"\n📡 Monitoring: {source_channels}")
print(f"🎯 Forwarding to: {target_channel}")

# Check if session file exists
session_file = "user_session.session"
if os.path.exists(session_file):
    print(f"✅ Session file found! Size: {os.path.getsize(session_file)} bytes")
else:
    print(f"❌ Session file NOT found!")

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
        print("✅ Connected successfully!")
        me = await client.get_me()
        print(f"👤 Logged in as: @{me.username}")
        print("\n🤖 Bot is running and waiting for messages...\n")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Failed to start: {e}")

if __name__ == "__main__":
    asyncio.run(main())
