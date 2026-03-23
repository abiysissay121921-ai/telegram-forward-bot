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

# Use bot.session directly
SESSION_FILE = "bot.session"

if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found: {SESSION_FILE}")
    print("Files in directory:")
    for f in os.listdir('.'):
        print(f"   - {f}")
    exit(1)

size = os.path.getsize(SESSION_FILE)
print(f"\n✅ Session file: {SESSION_FILE} ({size} bytes)")

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Store forwarded messages
forwarded_messages = set()

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        
        # Only process channels in our list
        if chat.username and chat.username in source_channels:
            
            message_id = f"{chat.id}_{event.id}"
            
            # Skip duplicates
            if message_id in forwarded_messages:
                print(f"⏭️ Skipping duplicate from @{chat.username}")
                return
            
            forwarded_messages.add(message_id)
            
            # Clean up old entries
            if len(forwarded_messages) > 5000:
                forwarded_messages.clear()
            
            print(f"\n📨 NEW Message from @{chat.username}")
            text = event.raw_text or ""
            
            # Create final message with intro, content, links, and signature
            intro = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
            
            if text:
                new_text = f"{intro}\n\n{text}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            else:
                new_text = f"{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            
            # Telegram caption limit
            if len(new_text) > 1024:
                new_text = new_text[:1020] + "..."
            
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
    await client.start()
    me = await client.get_me()
    print(f"✅ Connected as: @{me.username}")
    print("🤖 Bot is running and waiting for messages...\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
