import asyncio
from telethon import TelegramClient, events
import os

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT")
print("=" * 50)

API_ID = 37303512
API_HASH = "dff48ddff61546b05d1d507a6c508ee8"

# SOURCE CHANNELS (ONLY CHANNELS)
source_channels = [
    "ayuzehabeshanews",
    "Addis_News",
    "NatnaelMekonnen21",
    "tikvahethiopia",
    "eliasmeseret",
    "TikvahUniversity",
    "abiyselol",
]

# TARGET CHANNEL
target_channel = "NewsWith_Abiy"
your_link = "https://t.me/NewsWith_Abiy"

print(f"\n📡 Monitoring {len(source_channels)} channels:")
for channel in source_channels:
    print(f"   - @{channel}")
print(f"🎯 Forwarding to: @{target_channel}")
print(f"🔗 Your link: {your_link}")

# SESSION FILE NAME
SESSION_FILE = "final_bot.session"

if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found: {SESSION_FILE}")
    print("Files in directory:")
    for f in os.listdir('.'):
        print(f"   - {f}")
    exit(1)

# Check file size
size = os.path.getsize(SESSION_FILE)
print(f"\n✅ Session file found: {SESSION_FILE}")
print(f"📏 File size: {size} bytes")

if size < 1000:
    print(f"⚠️ WARNING: Session file is only {size} bytes - may be corrupted!")
    exit(1)

# Store forwarded messages to prevent duplicates
forwarded_messages = set()
MAX_STORED = 1000

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        
        # Only process channels in our list
        if hasattr(chat, 'username') and chat.username and chat.username in source_channels:
            
            # Unique ID for this message
            message_id = f"{chat.id}_{event.id}"
            
            # Check for duplicates
            if message_id in forwarded_messages:
                print(f"⏭️ Skipping duplicate from @{chat.username}")
                return
            
            forwarded_messages.add(message_id)
            
            # Clean up old entries to prevent memory issues
            if len(forwarded_messages) > MAX_STORED:
                to_remove = list(forwarded_messages)[:500]
                for msg in to_remove:
                    forwarded_messages.remove(msg)
                print(f"🧹 Cleaned up {len(to_remove)} old records")
            
            print(f"\n📨 NEW Message from @{chat.username}")
            text = event.raw_text or ""
            
            # Add link 3 times + signature
            new_text = f"{text}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            
            # Telegram caption limit is 1024 characters
            if len(new_text) > 1024:
                print(f"⚠️ Message too long ({len(new_text)} chars), truncating...")
                new_text = new_text[:1020] + "..."
            
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
