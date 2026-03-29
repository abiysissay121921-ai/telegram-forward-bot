import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaWebPage
import os
import re
import time

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

# SESSION FILE
SESSION_FILE = "final_bot.session"

# Check if session exists
if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found: {SESSION_FILE}")
    print("Files in directory:")
    for f in os.listdir('.'):
        print(f"   - {f}")
    exit(1)

print(f"\n✅ Session file: {SESSION_FILE}")

# Create client
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Store forwarded messages
forwarded = set()

def clean_text(text):
    """Remove source channel links ONLY - keep all other content"""
    if not text:
        return ""
    # Remove source channel mentions and links
    for ch in source_channels:
        text = re.sub(rf'@{ch}\b', '', text, flags=re.IGNORECASE)
        text = re.sub(rf'https?://t\.me/{ch}\b', '', text, flags=re.IGNORECASE)
        text = re.sub(rf't\.me/{ch}\b', '', text, flags=re.IGNORECASE)
    # Clean up extra newlines but preserve original message structure
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def can_handle_media(message):
    """Check if we can handle this media type"""
    try:
        if not message.media:
            return False, None
        
        # Check for webpages (links) - always handle these
        if isinstance(message.media, MessageMediaWebPage):
            return True, "webpage"
        
        # Check for valid media attributes
        if hasattr(message.media, 'photo') and message.media.photo:
            return True, "photo"
        if hasattr(message.media, 'document') and message.media.document:
            mime = getattr(message.media.document, 'mime_type', '')
            # Skip problematic document types (voice, video notes, stickers)
            if 'voice' in mime.lower() or 'video_note' in mime.lower() or 'sticker' in mime.lower():
                return False, "unsupported"
            return True, "document"
        
        return False, "unknown"
    except Exception as e:
        print(f"⚠️ Media check error: {e}")
        return False, "error"

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return
        
        # Unique ID for message
        msg_id = f"{chat.id}_{event.id}"
        
        # Prevent duplicates
        if msg_id in forwarded:
            return
        
        forwarded.add(msg_id)
        if len(forwarded) > 1000:
            forwarded.clear()
        
        print(f"\n📨 From @{chat.username}")
        
        # Get and clean text (removes source links only)
        original = event.raw_text or ""
        cleaned = clean_text(original)
        
        # Build message - link appears ONCE only
        intro = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
        
        if cleaned:
            # Original content + intro + single link
            msg = f"{cleaned}\n\n{intro}\n\n{your_link}\nሰላም ለእናንተ!"
        else:
            # Just intro + single link
            msg = f"{intro}\n\n{your_link}\nሰላም ለእናንተ!"
        
        if len(msg) > 4096:
            msg = msg[:4090] + "..."
        
        # Handle media messages
        if event.message.media:
            can_handle, media_type = can_handle_media(event.message)
            
            if can_handle:
                try:
                    # Try to send with file
                    await client.send_file(target_channel, event.message.media, caption=msg)
                    print(f"📸 {media_type} sent")
                except Exception as media_error:
                    error_str = str(media_error)
                    if "Constructor ID" in error_str:
                        print(f"⚠️ Unsupported media type, sending text only")
                        await client.send_message(target_channel, msg)
                    else:
                        raise media_error
            else:
                # Skip unsupported media but still send text if available
                print(f"⏭️ Skipped unsupported media from @{chat.username}")
                if cleaned:  # Still send text if available
                    await client.send_message(target_channel, msg)
                    print("📤 Text sent (media skipped)")
                return
        else:
            # Text-only message
            await client.send_message(target_channel, msg)
            print("📤 Text sent")
        
        print("✅ Done!")
        
    except Exception as e:
        error_str = str(e)
        if "Constructor ID" in error_str:
            print(f"⚠️ Skipped problematic message from @{chat.username if 'chat' in locals() else 'unknown'}")
        else:
            print(f"❌ Error: {error_str}")

async def run_bot():
    """Run bot with auto-reconnect"""
    try:
        await client.start()
        me = await client.get_me()
        print(f"✅ Connected as: @{me.username}")
        print("🤖 Bot running...\n")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Disconnected: {e}")
        print("🔄 Reconnecting in 30 seconds...")
        await asyncio.sleep(30)
        return False
    return True

async def main():
    """Main loop with auto-reconnect"""
    while True:
        success = await run_bot()
        if success:
            break
        # Continue loop if reconnect needed

if __name__ == "__main__":
    asyncio.run(main())
