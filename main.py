import asyncio
from telethon import TelegramClient, events
import os
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
    "atc_news",
    "seledadotio",
]

target_channel = "EBC_News_Official"
your_link = "https://t.me/EBC_News_Official"

print(f"\n📡 Monitoring {len(source_channels)} channels:")
for channel in source_channels:
    print(f"   - @{channel}")
print(f"🎯 Forwarding to: @{target_channel}")

SESSION_FILE = "mysession.session"

if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found: {SESSION_FILE}")
    exit(1)

print(f"\n✅ Session file: {SESSION_FILE}")

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

forwarded = set()

def clean_text(text):
    if not text:
        return ""
    for ch in source_channels:
        text = re.sub(rf'@{ch}\b', '', text, flags=re.IGNORECASE)
        text = re.sub(rf'https?://t\.me/{ch}\b', '', text, flags=re.IGNORECASE)
        text = re.sub(rf't\.me/{ch}\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'https?://t\.me/\S+', '', text)
    text = re.sub(r't\.me/\S+', '', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def split_long_message(text, max_length=4096):
    """Split long message into chunks of max_length"""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    lines = text.split('\n')
    current_chunk = ""
    
    for line in lines:
        # If adding this line exceeds limit, save current chunk and start new one
        if len(current_chunk) + len(line) + 1 > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line
        else:
            if current_chunk:
                current_chunk += "\n" + line
            else:
                current_chunk = line
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def create_message(cleaned_text, intro, link):
    """Create formatted message with intro and link"""
    if cleaned_text:
        return f"{cleaned_text}\n\n{intro}\n\n{link}\n{link}\n{link}\nሰላም ለእናንተ!"
    else:
        return f"{intro}\n\n{link}\n{link}\n{link}\nሰላም ለእናንተ!"

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return
        
        msg_id = f"{chat.id}_{event.id}"
        if msg_id in forwarded:
            return
        
        forwarded.add(msg_id)
        if len(forwarded) > 1000:
            forwarded.clear()
        
        print(f"\n📨 From @{chat.username}")
        
        original = event.raw_text or ""
        cleaned = clean_text(original)
        
        intro = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
        
        # Create the full message
        full_message = create_message(cleaned, intro, your_link)
        
        # Split if too long
        message_chunks = split_long_message(full_message)
        
        # Send the first chunk with media (if media exists)
        if event.message.media:
            # Send media with first chunk as caption
            await client.send_file(
                target_channel, 
                event.message.media, 
                caption=message_chunks[0] if message_chunks else ""
            )
            print("📸 Media sent with first part")
            
            # Send remaining chunks as text messages
            for chunk in message_chunks[1:]:
                await client.send_message(target_channel, chunk)
                print(f"📤 Text part {message_chunks.index(chunk)+1} sent")
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
        else:
            # No media - send all chunks as text
            for i, chunk in enumerate(message_chunks):
                await client.send_message(target_channel, chunk)
                print(f"📤 Part {i+1}/{len(message_chunks)} sent")
                # Small delay between messages
                await asyncio.sleep(0.5)
        
        print(f"✅ Done! ({len(message_chunks)} parts)")
        
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
