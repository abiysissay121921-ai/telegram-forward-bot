import asyncio
from telethon import TelegramClient, events
import os
import re
import time
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
    "atc_news",
    "seledadotio",
]

target_channel = "NewsWith_Abiy"
your_link = "https://t.me/NewsWith_Abiy"

print(f"\n📡 Monitoring {len(source_channels)} channels:")
for channel in source_channels:
    print(f"   - @{channel}")
print(f"🎯 Forwarding to: @{target_channel}")

SESSION_FILE = "session.session"

if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found: {SESSION_FILE}")
    print("Files in directory:")
    for f in os.listdir('.'):
        print(f"   - {f}")
    exit(1)

print(f"\n✅ Session file: {SESSION_FILE}")

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Store forwarded message IDs with timestamp
forwarded_ids = {}
forwarded_hashes = {}
DUPLICATE_WINDOW = 5  # seconds

def remove_source_links(text):
    if not text:
        return ""
    for channel in source_channels:
        text = re.sub(rf'@{re.escape(channel)}\b', '', text, flags=re.IGNORECASE)
        text = re.sub(rf'https?://t\.me/{re.escape(channel)}\b', '', text, flags=re.IGNORECASE)
        text = re.sub(rf't\.me/{re.escape(channel)}\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'https?://t\.me/\S+', '', text)
    text = re.sub(r't\.me/\S+', '', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()
    return text

def get_message_hash(message):
    """Create a unique hash for the message content"""
    text = message.raw_text or ""
    if message.media:
        # For media, use message ID + chat ID
        return f"{message.chat_id}_{message.id}"
    # For text, hash the content
    return hashlib.md5(text.encode()).hexdigest()

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        if chat.username and chat.username in source_channels:
            
            # Create unique ID for this message
            message_id = f"{chat.id}_{event.id}"
            message_hash = get_message_hash(event.message)
            current_time = time.time()
            
            # Check by ID
            if message_id in forwarded_ids:
                last_time = forwarded_ids[message_id]
                if current_time - last_time < DUPLICATE_WINDOW:
                    print(f"⏭️ SKIPPING DUPLICATE (ID): {message_id}")
                    return
            
            # Check by content hash
            if message_hash in forwarded_hashes:
                last_time = forwarded_hashes[message_hash]
                if current_time - last_time < DUPLICATE_WINDOW:
                    print(f"⏭️ SKIPPING DUPLICATE (HASH): {message_hash}")
                    return
            
            # Mark as forwarded
            forwarded_ids[message_id] = current_time
            forwarded_hashes[message_hash] = current_time
            
            # Clean up old entries (older than 1 minute)
            for msg_id in list(forwarded_ids.keys()):
                if current_time - forwarded_ids[msg_id] > 60:
                    del forwarded_ids[msg_id]
            for h in list(forwarded_hashes.keys()):
                if current_time - forwarded_hashes[h] > 60:
                    del forwarded_hashes[h]
            
            print(f"\n📨 NEW MESSAGE: {message_id} from @{chat.username}")
            
            original_text = event.raw_text or ""
            cleaned_text = remove_source_links(original_text)
            intro = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
            
            if cleaned_text:
                caption = f"{cleaned_text}\n\n{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            else:
                caption = f"{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            
            if len(caption) > 1024:
                caption = caption[:1020] + "..."
            
            if event.message.media:
                await client.send_file(target_channel, event.message.media, caption=caption)
                print("📸 Media sent with caption")
            else:
                await client.send_message(target_channel, caption)
                print("📤 Text sent")
            print("✅ Done!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("\n🔌 Connecting to Telegram...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Connected as: @{me.username}")
    print("🤖 Bot running...\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
