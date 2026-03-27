import asyncio
from telethon import TelegramClient, events
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

SESSION_FILE = "my_bot.session"

if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found: {SESSION_FILE}")
    print("Files in directory:")
    for f in os.listdir('.'):
        print(f"   - {f}")
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
        
        if cleaned:
            msg = f"{cleaned}\n\n{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
        else:
            msg = f"{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
        
        if len(msg) > 4096:
            msg = msg[:4090] + "..."
        
        if event.message.media:
            await client.send_file(target_channel, event.message.media, caption=msg)
            print("📸 Media sent")
        else:
            await client.send_message(target_channel, msg)
            print("📤 Text sent")
        print("✅ Done!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def run_bot():
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
    while True:
        success = await run_bot()
        if not success:
            continue
        break

if __name__ == "__main__":
    asyncio.run(main())
