import asyncio
from telethon import TelegramClient, events
import os
import re
from collections import defaultdict

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

# YOUR SESSION FILE
SESSION_FILE = "bot_1774330681.session"

if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found: {SESSION_FILE}")
    print("Files in directory:")
    for f in os.listdir('.'):
        print(f"   - {f}")
    exit(1)

print(f"\n✅ Session file: {SESSION_FILE}")

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Store forwarded messages
forwarded_messages = set()
# Store albums by group_id
pending_albums = defaultdict(list)
ALBUM_TIMEOUT = 2  # seconds to wait for album messages

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

async def send_album(album_id, chat_username):
    """Send all photos in an album as a single grouped message"""
    if album_id not in pending_albums:
        return
    
    album_messages = pending_albums.pop(album_id)
    
    # Collect all media from the album
    media_list = []
    caption = None
    
    for msg_data in album_messages:
        media_list.append(msg_data['media'])
        if msg_data['caption'] and not caption:
            caption = msg_data['caption']
    
    if media_list:
        try:
            await client.send_file(target_channel, media_list, caption=caption)
            print(f"📸 Forwarded album with {len(media_list)} photos from @{chat_username}")
        except Exception as e:
            print(f"❌ Error sending album: {e}")
            # Fallback: send individually
            for media in media_list:
                await client.send_file(target_channel, media, caption=caption if media == media_list[0] else None)

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        
        # Only process channels in our list
        if hasattr(chat, 'username') and chat.username and chat.username in source_channels:
            
            # Create unique ID for this message
            msg_id = f"{chat.id}_{event.id}"
            
            # Check if already forwarded
            if msg_id in forwarded_messages:
                print(f"⏭️ Skipping duplicate from @{chat.username}")
                return
            
            # Mark as forwarded
            forwarded_messages.add(msg_id)
            if len(forwarded_messages) > 5000:
                forwarded_messages.clear()
            
            print(f"\n📨 From @{chat.username}")
            
            # Prepare caption
            original_text = event.raw_text or ""
            cleaned_text = remove_source_links(original_text)
            
            intro = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
            
            if cleaned_text:
                caption = f"{cleaned_text}\n\n{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            else:
                caption = f"{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            
            if len(caption) > 1024:
                caption = caption[:1020] + "..."
            
            # Handle media
            if event.message.media:
                # Check if this is part of an album (grouped media)
                if hasattr(event.message, 'grouped_id') and event.message.grouped_id:
                    album_id = event.message.grouped_id
                    print(f"📸 Album detected (ID: {album_id})")
                    
                    # Store this message in the album
                    pending_albums[album_id].append({
                        'media': event.message.media,
                        'caption': caption,
                        'chat_username': chat.username
                    })
                    
                    # Schedule album send after a short delay
                    async def send_album_delayed(aid, username):
                        await asyncio.sleep(ALBUM_TIMEOUT)
                        await send_album(aid, username)
                    
                    # Only schedule once per album
                    if len(pending_albums[album_id]) == 1:
                        asyncio.create_task(send_album_delayed(album_id, chat.username))
                else:
                    # Single media (not part of an album)
                    await client.send_file(target_channel, event.message.media, caption=caption)
                    print("📤 Forwarded single media")
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
