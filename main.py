import asyncio
from telethon import TelegramClient, events
import os
import hashlib
import re

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
    "AAUMEREJA",
    "AAUNEWS1",
]

target_channel = "NewsWith_Abiy"
your_link = "https://t.me/NewsWith_Abiy"

print(f"\n📡 Monitoring {len(source_channels)} channels:")
for channel in source_channels:
    print(f"   - @{channel}")
print(f"🎯 Forwarding to: @{target_channel}")

# Try different session file names
SESSION_FILE = "bot.session"
if not os.path.exists(SESSION_FILE):
    # Try alternative session names
    alt_files = ["bot_session.session", "mybot.session", "clean_session.session", "final_bot.session"]
    for alt in alt_files:
        if os.path.exists(alt):
            SESSION_FILE = alt
            break

if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found!")
    print("Files in directory:")
    for f in os.listdir('.'):
        print(f"   - {f}")
    exit(1)

size = os.path.getsize(SESSION_FILE)
print(f"\n✅ Session file: {SESSION_FILE} ({size} bytes)")

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Store forwarded messages to prevent duplicates
forwarded_messages = set()
forwarded_hashes = set()
MAX_STORED = 5000

def clean_text(text):
    """Remove source channel links and mentions from text"""
    if not text:
        return ""
    
    # Remove source channel usernames and links
    for channel in source_channels:
        # Remove @username
        text = re.sub(rf'@{re.escape(channel)}\b', '', text, flags=re.IGNORECASE)
        # Remove https://t.me/username
        text = re.sub(rf'https?://t\.me/{re.escape(channel)}\b', '', text, flags=re.IGNORECASE)
        # Remove t.me/username
        text = re.sub(rf't\.me/{re.escape(channel)}\b', '', text, flags=re.IGNORECASE)
    
    # Remove any remaining t.me links
    text = re.sub(r'https?://t\.me/\S+', '', text)
    text = re.sub(r't\.me/\S+', '', text)
    
    # Remove multiple spaces and blank lines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    text = text.strip()
    
    return text

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        
        # Only process channels in our list
        if chat.username and chat.username in source_channels:
            
            # Create unique ID for this message
            message_id = f"{chat.id}_{event.id}"
            
            # Check if already forwarded by ID
            if message_id in forwarded_messages:
                print(f"⏭️ Skipping duplicate from @{chat.username}")
                return
            
            # Get original text
            text = event.raw_text or ""
            
            # Create content hash for text messages (to catch edited messages)
            if text:
                content_hash = hashlib.md5(text.encode()).hexdigest()
                if content_hash in forwarded_hashes:
                    print(f"⏭️ Skipping duplicate content from @{chat.username}")
                    return
                forwarded_hashes.add(content_hash)
            
            # Mark as forwarded
            forwarded_messages.add(message_id)
            
            # Clean up old entries
            if len(forwarded_messages) > MAX_STORED:
                to_remove = list(forwarded_messages)[:1000]
                for msg in to_remove:
                    forwarded_messages.remove(msg)
            
            if len(forwarded_hashes) > MAX_STORED:
                to_remove = list(forwarded_hashes)[:1000]
                for h in to_remove:
                    forwarded_hashes.remove(h)
            
            print(f"\n📨 NEW Message from @{chat.username}")
            
            # Clean the text - REMOVE ALL ORIGINAL SOURCE LINKS
            clean_text_content = clean_text(text)
            
            # Create the final message with intro, cleaned content, your links, and signature
            intro = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
            
            # Build final text
            if clean_text_content:
                new_text = f"{intro}\n\n{clean_text_content}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            else:
                new_text = f"{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            
            # Telegram caption limit is 1024 characters
            if len(new_text) > 1024:
                print(f"⚠️ Message too long ({len(new_text)} chars), truncating...")
                new_text = new_text[:1020] + "..."
            
            # Send the message
            if event.message.media:
                await client.send_file(target_channel, event.message.media, caption=new_text)
                print("📤 Forwarded with media")
            else:
                await client.send_message(target_channel, new_text)
                print(f"📤 Forwarded: {new_text[:80]}...")
            print("✅ Done!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("\n🔌 Connecting to Telegram...")
    try:
        await client.start()
        me = await client.get_me()
        print(f"✅ Connected as: @{me.username}")
        print("🤖 Bot is running and waiting for messages...\n")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
