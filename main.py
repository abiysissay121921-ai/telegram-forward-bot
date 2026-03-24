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
        text = re.sub(rf'@{re.escape(channel)}\b', '', text, flags=re.IGNORECASE)
        text = re.sub(rf'https?://t\.me/{re.escape(channel)}\b', '', text, flags=re.IGNORECASE)
        text = re.sub(rf't\.me/{re.escape(channel)}\b', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'https?://t\.me/\S+', '', text)
    text = re.sub(r't\.me/\S+', '', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()
    
    return text

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        
        # Only process channels in our list
        if chat.username and chat.username in source_channels:
            
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
            
            # FORWARD THE EXACT MESSAGE (PRESERVES ALBUMS)
            if event.message.media:
                # Forward the original message exactly as is
                await client.forward_messages(target_channel, event.message)
                print("📸 Forwarded original media (album preserved)")
                
                # Send caption as a separate message
                if caption:
                    await client.send_message(target_channel, caption)
                    print("📝 Caption sent")
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
