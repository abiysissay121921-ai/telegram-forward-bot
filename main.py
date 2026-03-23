import asyncio
from telethon import TelegramClient, events
import os

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

SESSION_FILE = "mysession.session"

if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found: {SESSION_FILE}")
    print("Files in directory:")
    for f in os.listdir('.'):
        print(f"   - {f}")
    exit(1)

print(f"\n✅ Session file: {SESSION_FILE}")

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

forwarded_messages = set()

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        if chat.username and chat.username in source_channels:
            msg_id = f"{chat.id}_{event.id}"
            if msg_id in forwarded_messages:
                return
            forwarded_messages.add(msg_id)
            if len(forwarded_messages) > 5000:
                forwarded_messages.clear()
            
            print(f"\n📨 From @{chat.username}")
            text = event.raw_text or ""
            
            # Intro message
            intro = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
            
            # Prepare caption
            if text:
                caption = f"{text}\n\n{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            else:
                caption = f"{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            
            if len(caption) > 1024:
                caption = caption[:1020] + "..."
            
            # Handle media
            if event.message.media:
                # Check if it's a group of media (album)
                if hasattr(event.message, 'grouped_id') and event.message.grouped_id:
                    # Get all messages in the same album
                    print("📸 Found album/grouped media")
                    # For albums, we need to send all media together
                    # Telethon handles this automatically when using send_file with multiple files
                    # But since we're in a handler for one message, we need to collect all
                    # For simplicity, we'll forward as is - Telethon preserves albums when forwarding
                    await client.send_file(target_channel, event.message.media, caption=caption)
                    print("📤 Forwarded album/media with caption")
                else:
                    # Single media
                    await client.send_file(target_channel, event.message.media, caption=caption)
                    print("📤 Forwarded single media")
            else:
                # Text only
                await client.send_message(target_channel, caption)
                print(f"📤 Forwarded text")
            
            print("✅ Done!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("\n🔌 Connecting...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Connected as: @{me.username}")
    print("🤖 Bot running...\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
