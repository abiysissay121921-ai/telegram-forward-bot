import asyncio
from telethon import TelegramClient, events
import os
import re

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT")
print("=" * 50)

API_ID = 37303512
API_HASH = "dff48ddff61546b05d1d507a6c508ee8"

# ALL SOURCE CHANNELS
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
    "atc_news",
    "seledadotio",
    "AAU_GENERAL",
]

target_channel = "NewsWith_Abiy"
your_link = "https://t.me/NewsWith_Abiy"

print(f"\n📡 Monitoring {len(source_channels)} channels:")
for channel in source_channels:
    print(f"   - @{channel}")
print(f"🎯 Forwarding to: @{target_channel}")

# SESSION FILE
SESSION_FILE = "mysession.session"

if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found: {SESSION_FILE}")
    print("Files in directory:")
    for f in os.listdir('.'):
        print(f"   - {f}")
    exit(1)

print(f"\n✅ Session file: {SESSION_FILE}")

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Store forwarded message IDs to prevent duplicates
forwarded_messages = set()

def remove_source_links(text):
    """Remove ALL source channel links and mentions"""
    if not text:
        return ""
    
    for channel in source_channels:
        # Remove @channelname
        text = re.sub(rf'@{re.escape(channel)}\b', '', text, flags=re.IGNORECASE)
        # Remove https://t.me/channelname
        text = re.sub(rf'https?://t\.me/{re.escape(channel)}\b', '', text, flags=re.IGNORECASE)
        # Remove t.me/channelname
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
        if hasattr(chat, 'username') and chat.username and chat.username in source_channels:
            
            # Create unique ID to prevent duplicates
            message_id = f"{chat.id}_{event.id}"
            
            # Skip if already forwarded
            if message_id in forwarded_messages:
                print(f"⏭️ Skipping duplicate from @{chat.username}")
                return
            
            # Mark as forwarded
            forwarded_messages.add(message_id)
            
            # Keep memory in check
            if len(forwarded_messages) > 5000:
                forwarded_messages.clear()
            
            print(f"\n📨 From @{chat.username}")
            
            # Get original text and remove source links
            original_text = event.raw_text or ""
            cleaned_text = remove_source_links(original_text)
            
            # Create intro message
            intro = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
            
            # Build final caption
            if cleaned_text:
                caption = f"{cleaned_text}\n\n{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            else:
                caption = f"{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            
            # Telegram caption limit
            if len(caption) > 1024:
                caption = caption[:1020] + "..."
            
            # Forward the message AS-IS (preserves albums, multiple photos, videos)
            if event.message.media:
                # Send media with caption - automatically preserves albums
                await client.send_file(target_channel, event.message.media, caption=caption)
                print("📤 Forwarded with media (album preserved)")
            else:
                # Text only
                await client.send_message(target_channel, caption)
                print("📤 Forwarded text")
            
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
