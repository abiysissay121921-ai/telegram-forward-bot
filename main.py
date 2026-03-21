import asyncio
from telethon import TelegramClient, events
import os

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT")
print("=" * 50)

API_ID = 37303512
API_HASH = "dff48ddff61546b05d1d507a6c508ee8"

# REMOVED Apostolic_Answers_chat - it's a GROUP, not a channel
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

print(f"📡 Monitoring {len(source_channels)} channels:")
for channel in source_channels:
    print(f"   - @{channel}")
print(f"🎯 Forwarding to: @{target_channel}")

session_file = "bot_final_2026.session"

if not os.path.exists(session_file):
    print(f"❌ Session file not found: {session_file}")
    exit(1)

client = TelegramClient(session_file, API_ID, API_HASH)

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        # Only process if it's a channel (not a group)
        if hasattr(chat, 'username') and chat.username and chat.username in source_channels:
            print(f"\n📨 Message from @{chat.username}")
            text = event.raw_text or ""
            new_text = f"{text}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            
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
    await client.start()
    me = await client.get_me()
    print(f"✅ Connected as: @{me.username}")
    print("🤖 Bot is running...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
