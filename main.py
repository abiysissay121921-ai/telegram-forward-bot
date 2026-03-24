import asyncio
from telethon import TelegramClient, events
import os
import re
import time

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT")
print("=" * 50)

# Your API credentials
API_ID = 37303512
API_HASH = "dff48ddff61546b05d1d507a6c508ee8"

# Source channels (only channels you are a member of)
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

# Target channel
target_channel = "NewsWith_Abiy"
your_link = "https://t.me/NewsWith_Abiy"

print(f"\n📡 Monitoring {len(source_channels)} channels:")
for channel in source_channels:
    print(f"   - @{channel}")
print(f"🎯 Forwarding to: @{target_channel}")

# Session file - CHANGE THIS TO YOUR SESSION FILE NAME
SESSION_FILE = "my_bot.session"

# Check if session file exists
if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found: {SESSION_FILE}")
    print("Files in directory:")
    for f in os.listdir('.'):
        print(f"   - {f}")
    exit(1)

# Check session file size
size = os.path.getsize(SESSION_FILE)
print(f"\n✅ Session file: {SESSION_FILE} ({size} bytes)")

if size < 1000:
    print(f"❌ Session file is corrupted (too small)")
    exit(1)

# Create client
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Store forwarded messages to prevent duplicates
forwarded_messages = set()

def clean_text(text):
    """Remove all source channel links and mentions"""
    if not text:
        return ""
    
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
    
    # Clean up formatting
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
            
            # Check for duplicates
            if message_id in forwarded_messages:
                print(f"⏭️ Skipping duplicate: {message_id}")
                return
            
            # Mark as forwarded immediately
            forwarded_messages.add(message_id)
            
            # Clean up old entries to prevent memory issues
            if len(forwarded_messages) > 5000:
                forwarded_messages.clear()
            
            print(f"\n📨 NEW MESSAGE: {message_id} from @{chat.username}")
            
            # Get original text and clean it
            original_text = event.raw_text or ""
            cleaned_text = clean_text(original_text)
            
            # Create intro message
            intro = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
            
            # Build final message
            if cleaned_text:
                final_message = f"{cleaned_text}\n\n{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            else:
                final_message = f"{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            
            # Telegram message limit
            if len(final_message) > 4096:
                final_message = final_message[:4090] + "..."
            
            # Send the message
            if event.message.media:
                await client.send_file(target_channel, event.message.media, caption=final_message)
                print("📸 Media sent with caption")
            else:
                await client.send_message(target_channel, final_message)
                print("📤 Text sent")
            
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

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
