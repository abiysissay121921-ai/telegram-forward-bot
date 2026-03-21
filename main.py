import asyncio
from telethon import TelegramClient, events
import os
import hashlib

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT")
print("=" * 50)

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
    "zena24now",
]

target_channel = "NewsWith_Abiy"
your_link = "https://t.me/NewsWith_Abiy"

print(f"\n📡 Monitoring {len(source_channels)} channels:")
for channel in source_channels:
    print(f"   - @{channel}")
print(f"🎯 Forwarding to: @{target_channel}")

SESSION_FILE = "mysession.session"

if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found: {SESSION_FILE}")
    exit(1)

print(f"\n✅ Session file found: {SESSION_FILE}")

# Store forwarded message IDs to prevent duplicates
forwarded_messages = set()
# Store last 1000 messages to avoid memory issues
MAX_STORED = 1000

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        
        # Only process channels in our list
        if hasattr(chat, 'username') and chat.username and chat.username in source_channels:
            
            # Create a unique ID for this message
            message_id = f"{chat.id}_{event.id}"
            
            # Check if already forwarded
            if message_id in forwarded_messages:
                print(f"⏭️ Skipping duplicate message from @{chat.username}")
                return
            
            # Add to forwarded set
            forwarded_messages.add(message_id)
            
            # Keep set size manageable
            if len(forwarded_messages) > MAX_STORED:
                # Remove oldest 500
                to_remove = list(forwarded_messages)[:500]
                for msg in to_remove:
                    forwarded_messages.remove(msg)
                print(f"🧹 Cleaned up {len(to_remove)} old message records")
            
            print(f"\n📨 NEW Message from @{chat.username}")
            text = event.raw_text or ""
            
            # Add link THREE TIMES + signature
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
    print("\n🔌 Connecting to Telegram...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Connected as: @{me.username}")
    print("🤖 Bot is running and waiting for messages...\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
