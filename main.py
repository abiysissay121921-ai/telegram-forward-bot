import asyncio
from telethon import TelegramClient, events
import os
import re
import time

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT - LONG MESSAGE FIX")
print("=" * 50)

API_ID = 37303512
API_HASH = "dff48ddff61546b05d1d507a6c508ee8"

source_channels = [
    "ayuzehabeshanews",
    "Addis_News",
    "NatnaelMekonnen21",
    "TikvahUniversity",
    "abiyselol",
    "zena24now",
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

# Store forwarded message IDs to avoid duplicates
forwarded = set()

def clean_text(text):
    """Clean text by removing source channel mentions and URLs"""
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

def split_message_advanced(text, max_length=4000):
    """
    Advanced message splitter that preserves formatting
    and ensures each chunk is under the limit
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    
    # Try to split by paragraphs first
    paragraphs = text.split('\n\n')
    current_chunk = ""
    
    for para in paragraphs:
        # If a single paragraph is too long, split it by sentences
        if len(para) > max_length:
            # Save current chunk first
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            
            # Split long paragraph by sentences
            sentences = para.replace('!', '.\n').replace('?', '.\n').split('. ')
            temp_chunk = ""
            
            for sent in sentences:
                if len(temp_chunk) + len(sent) + 2 <= max_length:
                    if temp_chunk:
                        temp_chunk += ". " + sent
                    else:
                        temp_chunk = sent
                else:
                    if temp_chunk:
                        chunks.append(temp_chunk)
                    temp_chunk = sent
            
            if temp_chunk:
                chunks.append(temp_chunk)
        
        # Normal paragraph
        else:
            if len(current_chunk) + len(para) + 2 <= max_length:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    # If no chunks were created (fallback), split by character
    if not chunks:
        for i in range(0, len(text), max_length):
            chunks.append(text[i:i+max_length])
    
    return chunks

def create_full_message(cleaned_text):
    """Create the full message with intro and link"""
    intro = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
    
    if cleaned_text:
        return f"{cleaned_text}\n\n{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
    else:
        return f"{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"

async def send_long_message(channel, message, reply_to=None):
    """
    Send a long message by splitting it into parts
    """
    # Split the message
    chunks = split_message_advanced(message)
    
    if not chunks:
        return
    
    print(f"📝 Message split into {len(chunks)} parts")
    
    # Send first part
    first_message = await client.send_message(
        channel, 
        chunks[0],
        reply_to=reply_to
    )
    print(f"📤 Part 1/{len(chunks)} sent")
    
    # Send remaining parts as replies to the first message
    for i, chunk in enumerate(chunks[1:], start=2):
        try:
            await client.send_message(
                channel,
                chunk,
                reply_to=first_message.id
            )
            print(f"📤 Part {i}/{len(chunks)} sent")
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.3)
            
        except Exception as e:
            print(f"❌ Error sending part {i}: {e}")
            # Try without reply if reply fails
            await client.send_message(channel, chunk)
            print(f"📤 Part {i}/{len(chunks)} sent (without reply)")
            await asyncio.sleep(0.3)
    
    return len(chunks)

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return
        
        # Check if already forwarded
        msg_id = f"{chat.id}_{event.id}"
        if msg_id in forwarded:
            return
        
        forwarded.add(msg_id)
        if len(forwarded) > 1000:
            forwarded.clear()
        
        print(f"\n📨 From @{chat.username}")
        print(f"📊 Message length: {len(event.raw_text or '')} characters")
        
        # Get and clean the text
        original = event.raw_text or ""
        cleaned = clean_text(original)
        
        # Create the full message with intro and link
        full_message = create_full_message(cleaned)
        
        # Check if media exists
        if event.message.media:
            print("📎 Media detected")
            
            # If message is short, send with caption
            if len(full_message) <= 4096:
                await client.send_file(
                    target_channel, 
                    event.message.media, 
                    caption=full_message
                )
                print("📸 Media sent with caption")
            else:
                # Long message with media
                # Send media with first part as caption
                chunks = split_message_advanced(full_message)
                
                await client.send_file(
                    target_channel, 
                    event.message.media, 
                    caption=chunks[0] if chunks else ""
                )
                print(f"📸 Media sent with part 1/{len(chunks)}")
                
                # Send remaining parts
                for i, chunk in enumerate(chunks[1:], start=2):
                    await client.send_message(target_channel, chunk)
                    print(f"📤 Text part {i}/{len(chunks)} sent")
                    await asyncio.sleep(0.3)
        else:
            # Text only message
            parts_sent = await send_long_message(target_channel, full_message)
            print(f"✅ Done! Sent {parts_sent} parts")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    print("\n🔌 Connecting to Telegram...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Connected as: @{me.username}")
    print("🤖 Bot running...")
    print("📏 Max message size: 4096 characters per part")
    print("📚 Long messages will be split automatically\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
