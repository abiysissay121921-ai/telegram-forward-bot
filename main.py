import asyncio
from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import AuthKeyDuplicatedError  # correct import
import os
import re
import sys

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT - FINAL FIX")
print("=" * 50)

API_ID = 37303512
API_HASH = "dff48ddff61546b05d1d507a6c508ee8"   # correct hash

# --- EDIT THESE LINES IF NEEDED ---
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
# ----------------------------------

print(f"\n📡 Monitoring {len(source_channels)} channels:")
for ch in source_channels:
    print(f"   - @{ch}")
print(f"🎯 Forwarding to: @{target_channel}")

SESSION_FILE = "mysession.session"

def clean_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    journal = SESSION_FILE + "-journal"
    if os.path.exists(journal):
        os.remove(journal)

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

def split_message_advanced(text, max_length=4000):
    if len(text) <= max_length:
        return [text]
    chunks = []
    paragraphs = text.split('\n\n')
    current = ""
    for para in paragraphs:
        if len(para) > max_length:
            if current:
                chunks.append(current)
                current = ""
            sentences = re.split(r'(?<=[.!?])\s+', para)
            temp = ""
            for sent in sentences:
                if len(temp) + len(sent) + 2 <= max_length:
                    temp = temp + " " + sent if temp else sent
                else:
                    if temp:
                        chunks.append(temp)
                    temp = sent
            if temp:
                chunks.append(temp)
        else:
            if len(current) + len(para) + 2 <= max_length:
                current = current + "\n\n" + para if current else para
            else:
                if current:
                    chunks.append(current)
                current = para
    if current:
        chunks.append(current)
    if not chunks:
        for i in range(0, len(text), max_length):
            chunks.append(text[i:i+max_length])
    return chunks

def create_full_message(cleaned_text):
    intro = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
    if cleaned_text:
        return f"{cleaned_text}\n\n{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
    else:
        return f"{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"

async def send_long_message(channel, message, reply_to=None):
    chunks = split_message_advanced(message)
    if not chunks:
        return 0
    print(f"📝 Split into {len(chunks)} parts")
    first = await client.send_message(channel, chunks[0], reply_to=reply_to, parse_mode=None)
    print(f"📤 Part 1/{len(chunks)} sent")
    for i, chunk in enumerate(chunks[1:], start=2):
        try:
            await client.send_message(channel, chunk, reply_to=first.id, parse_mode=None)
            print(f"📤 Part {i}/{len(chunks)} sent")
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"❌ Error sending part {i}: {e} – sending without reply")
            await client.send_message(channel, chunk, parse_mode=None)
            await asyncio.sleep(0.3)
    return len(chunks)

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
        print(f"📊 Message length: {len(event.raw_text or '')} chars")

        original = event.raw_text or ""
        cleaned = clean_text(original)
        full_message = create_full_message(cleaned)

        if event.message.media:
            print("📎 Media detected")
            # Send media with a VERY SHORT caption to avoid 1024‑char limit
            await client.send_file(
                target_channel,
                event.message.media,
                caption="📎",
                parse_mode=None
            )
            print("📸 Media sent (caption: 📎)")
            # Now send the full text as separate messages
            parts = await send_long_message(target_channel, full_message)
            print(f"✅ Done! Sent {parts} text parts")
        else:
            # Text‑only message
            parts = await send_long_message(target_channel, full_message)
            print(f"✅ Done! Sent {parts} parts")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    print("\n🔌 Connecting to Telegram...")
    try:
        await client.start()
    except AuthKeyDuplicatedError:
        print("❌ AuthKeyDuplicatedError – session used elsewhere or corrupted.")
        print("🔄 Deleting session file and restarting...")
        clean_session()
        global client
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.start()
        print("✅ New session created successfully.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

    me = await client.get_me()
    print(f"✅ Connected as: @{me.username}")
    print("🤖 Bot running...")
    print("📏 Max message size: 4096 chars per part")
    print("📚 Long messages will be split automatically\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
