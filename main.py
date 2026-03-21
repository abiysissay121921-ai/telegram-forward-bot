import asyncio
from telethon import TelegramClient, events
import os

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT (Bot Token Mode)")
print("=" * 50)

# Bot token
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8602729297:AAGog9z7FVCs8--IoajFT4JlS3vwga8pxUI")

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not set!")
    exit(1)

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
]

target_channel = "NewsWith_Abiy"
your_link = "https://t.me/NewsWith_Abiy"

print(f"\n🤖 Bot Token: {BOT_TOKEN[:10]}...")
print(f"📡 Monitoring {len(source_channels)} channels:")
for channel in source_channels:
    print(f"   - @{channel}")
print(f"🎯 Forwarding to: @{target_channel}")

# NO SESSION FILE NEEDED!
client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

forwarded_messages = set()
MAX_STORED = 1000

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        
        if hasattr(chat, 'username') and chat.username and chat.username in source_channels:
            message_id = f"{chat.id}_{event.id}"
            
            if message_id in forwarded_messages:
                print(f"⏭️ Skipping duplicate from @{chat.username}")
                return
            
            forwarded_messages.add(message_id)
            
            if len(forwarded_messages) > MAX_STORED:
                to_remove = list(forwarded_messages)[:500]
                for msg in to_remove:
                    forwarded_messages.remove(msg)
            
            print(f"\n📨 NEW Message from @{chat.username}")
            text = event.raw_text or ""
            new_text = f"{text}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
            
            if len(new_text) > 1024:
                new_text = new_text[:1020] + "..."
            
            if event.message.media:
                await client.send_file(target_channel, event.message.media, caption=new_text)
                print("📤 Forwarded with media")
            else:
                await client.send_message(target_channel, new_text)
                print(f"📤 Forwarded: {new_text[:50]}...")
            print("✅ Done!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("\n🔌 Connecting to Telegram with bot token...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Connected as: @{me.username}")
    print("🤖 Bot is running and waiting for messages...\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
