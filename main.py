import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, RPCError
from telethon.tl.types import MessageMediaWebPage
import os
import re
import time
import sys

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT")
print("=" * 50)
sys.stdout.flush()  # Force flush output

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
sys.stdout.flush()

# SESSION FILE
SESSION_FILE = "final_bot.session"

# Check if session exists
if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found: {SESSION_FILE}")
    print("Files in directory:")
    for f in os.listdir('.'):
        print(f"   - {f}")
    sys.stdout.flush()
    exit(1)

print(f"\n✅ Session file: {SESSION_FILE}")
sys.stdout.flush()

# Create client with connection parameters
client = TelegramClient(
    SESSION_FILE, 
    API_ID, 
    API_HASH,
    connection_retries=5,
    retry_delay=3,
    request_retries=10
)

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
        
        if isinstance(message.media, MessageMediaWebPage):
            return True, "webpage"
        
        if hasattr(message.media, 'photo') and message.media.photo:
            return True, "photo"
            
        if hasattr(message.media, 'document') and message.media.document:
            mime = getattr(message.media.document, 'mime_type', '')
            if 'voice' in mime.lower() or 'video_note' in mime.lower() or 'sticker' in mime.lower():
                return False, "unsupported"
            return True, "document"
        
        return False, "unknown"
    except Exception as e:
        print(f"⚠️ Media check error: {e}")
        sys.stdout.flush()
        return False, "error"

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
        sys.stdout.flush()
        
        original = event.raw_text or ""
        cleaned = clean_text(original)
        
        intro = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
        
        if cleaned:
            msg = f"{cleaned}\n\n{intro}\n\n{your_link}\nሰላም ለእናንተ!"
        else:
            msg = f"{intro}\n\n{your_link}\nሰላም ለእናንተ!"
        
        if len(msg) > 4096:
            msg = msg[:4090] + "..."
        
        if event.message.media:
            can_handle, media_type = can_handle_media(event.message)
            
            if can_handle:
                try:
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
                print(f"⏭️ Skipped unsupported media from @{chat.username}")
                if cleaned:
                    await client.send_message(target_channel, msg)
                    print("📤 Text sent (media skipped)")
                return
        else:
            await client.send_message(target_channel, msg)
            print("📤 Text sent")
        
        print("✅ Done!")
        sys.stdout.flush()
        
    except FloodWaitError as e:
        print(f"⏳ Rate limited. Waiting {e.seconds} seconds...")
        sys.stdout.flush()
        await asyncio.sleep(e.seconds)
    except Exception as e:
        error_str = str(e)
        if "Constructor ID" in error_str:
            print(f"⚠️ Skipped problematic message")
        else:
            print(f"❌ Error: {error_str}")
        sys.stdout.flush()

async def run_bot():
    """Run bot with auto-reconnect"""
    try:
        print("🔄 Connecting to Telegram...")
        sys.stdout.flush()
        
        await client.start()
        me = await client.get_me()
        print(f"✅ Connected as: @{me.username}")
        print("🤖 Bot running...\n")
        sys.stdout.flush()
        
        # Keep the bot running
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ Disconnected: {e}")
        sys.stdout.flush()
        print("🔄 Reconnecting in 10 seconds...")
        sys.stdout.flush()
        await asyncio.sleep(10)
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
