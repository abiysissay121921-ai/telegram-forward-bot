import asyncio
from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import AuthKeyDuplicatedError
import os
import re
import sys

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT - LONG MESSAGE FIX")
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

SESSION_FILE = "mysession.session"

# Remove corrupted session if it exists
def clean_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    journal = SESSION_FILE + "-journal"
    if os.path.exists(journal):
        os.remove(journal)

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Store forwarded message IDs to avoid duplicates
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
    current_chunk = ""
    for para in paragraphs:
        if len(para) > max_length:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            sentences = re.split(r'(?<=[.!?])\s+', para)
            temp_chunk = ""
            for sent in sentences:
                if len(temp_chunk) + len(sent) + 2 <= max_length:
                    if temp_chunk:
                        temp_chunk += " " + sent
                    else:
                        temp_chunk = sent
                else:
                    if temp_chunk:
                        chunks.append(temp_chunk)
                    temp_chunk = sent
            if temp_chunk:
                chunks.append(temp_chunk)
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
    if current_chunk:
        chunks.append(current_chunk)
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
        return
    print(f"📝 Message split into {len(chunks)} parts")
    first_message = await client.send_message(
        channel,
        chunks[0],
        reply_to=reply_to,
        parse_mode=None
    )
    print(f"📤 Part 1/{len(chunks)} sent")
    for i, chunk in enumerate(chunks[1:], start=2):
        try:
            await client.send_message(
                channel,
                chunk,
                reply_to=first_message.id,
                parse_mode=None
            )
            print(f"📤 Part {i}/{len(chunks)} sent")
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"❌ Error sending part {i}: {e}")
            await client.send_message(channel, chunk, parse_mode=None)
            print(f"📤 Part {i}/{len(chunks)} sent (without reply)")
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
        print(f"📊 Message length: {len(event.raw_text or '')} characters")

        original = event.raw_text or ""
        cleaned = clean_text(original)
        full_message = create_full_message(cleaned)

        if event.message.media:
            print("📎 Media detected")
            if len(full_message) <= 4096:
                await client.send_file(
                    target_channel,
                    event.message.media,
                    caption=full_message,
                    parse_mode=None
                )
                print("📸 Media sent with caption")
            else:
                chunks = split_message_advanced(full_message)
                await client.send_file(
                    target_channel,
                    event.message.media,
                    caption=chunks[0] if chunks else "",
                    parse_mode=None
                )
                print(f"📸 Media sent with part 1/{len(chunks)}")
                for i, chunk in enumerate(chunks[1:], start=2):
                    await client.send_message(target_channel, chunk, parse_mode=None)
                    print(f"📤 Text part {i}/{len(chunks)} sent")
                    await asyncio.sleep(0.3)
        else:
            parts_sent = await send_long_message(target_channel, full_message)
            print(f"✅ Done! Sent {parts_sent} parts")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    print("\n🔌 Connecting to Telegram...")
    try:
        await client.start()
    except AuthKeyDuplicatedError:
        print("❌ AuthKeyDuplicatedError – session is used elsewhere or corrupted.")
        print("🔄 Removing session file and restarting...")
        clean_session()
        # Recreate client with new session
        global client
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.start()
        print("✅ New session created successfully.")
    except Exception as e:
        print(f"❌ Unexpected error during start: {e}")
        sys.exit(1)

    me = await client.get_me()
    print(f"✅ Connected as: @{me.username}")
    print("🤖 Bot running...")
    print("📏 Max message size: 4096 characters per part")
    print("📚 Long messages will be split automatically\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
