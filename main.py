import asyncio
from telethon import TelegramClient, events
import os
import re

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT (One Media per Album)")
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
for ch in source_channels:
    print(f"   - @{ch}")
print(f"🎯 Forwarding to: @{target_channel}")

SESSION_FILE = "mysession.session"
if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found: {SESSION_FILE}")
    exit(1)
print(f"\n✅ Session file: {SESSION_FILE}")

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
processed = set()          # For single messages and album group IDs

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

def split_message(text, max_len=4000):
    if len(text) <= max_len:
        return [text]
    chunks = []
    for i in range(0, len(text), max_len):
        chunks.append(text[i:i+max_len])
    return chunks

def create_full_message(cleaned):
    intro = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
    if cleaned:
        return f"{cleaned}\n\n{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
    else:
        return f"{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"

async def send_long(channel, message):
    chunks = split_message(message)
    if not chunks:
        return
    print(f"📝 Splitting into {len(chunks)} parts")
    first = await client.send_message(channel, chunks[0], parse_mode=None)
    for i, chunk in enumerate(chunks[1:], start=2):
        try:
            await client.send_message(channel, chunk, reply_to=first.id, parse_mode=None)
            print(f"📤 Part {i}/{len(chunks)} sent")
            await asyncio.sleep(0.3)
        except:
            await client.send_message(channel, chunk, parse_mode=None)
    return len(chunks)

# ========== ALBUM HANDLER – takes only the first media ==========
@client.on(events.Album)
async def album_handler(event):
    try:
        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return

        grouped_id = event.grouped_id
        if not grouped_id:
            return

        # Prevent duplicate processing
        key = f"{chat.id}_group_{grouped_id}"
        if key in processed:
            return
        processed.add(key)
        if len(processed) > 1000:
            processed.clear()

        print(f"\n📸 Album detected from @{chat.username}")

        # Find the first media message
        first_media_msg = None
        caption_parts = []
        for msg in event.messages:
            if msg.raw_text:
                caption_parts.append(msg.raw_text)
            if msg.media and first_media_msg is None:
                first_media_msg = msg

        if not first_media_msg:
            print("⚠️ No media found in album, skipping.")
            return

        combined_caption = "\n".join(caption_parts) if caption_parts else ""
        cleaned = clean_text(combined_caption)
        full = create_full_message(cleaned)

        # Send only the first media with the full caption
        await client.send_file(
            target_channel,
            first_media_msg.media,
            caption=full,
            parse_mode=None
        )

        total_media = len([m for m in event.messages if m.media])
        print(f"✅ Album: forwarded first media (1 of {total_media}) with caption length {len(full)}")

    except Exception as e:
        print(f"❌ Error in album handler: {e}")
        import traceback
        traceback.print_exc()

# ========== SINGLE MESSAGE HANDLER (skips album parts) ==========
@client.on(events.NewMessage)
async def handler(event):
    try:
        # If this message belongs to an album, skip it (album handler will process it)
        if event.message.grouped_id is not None:
            return

        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return

        msg_id = f"{chat.id}_{event.id}"
        if msg_id in processed:
            return
        processed.add(msg_id)
        if len(processed) > 1000:
            processed.clear()

        print(f"\n📨 From @{chat.username} (single message)")

        original = event.raw_text or ""
        cleaned = clean_text(original)
        full = create_full_message(cleaned)

        if event.message.media:
            # Single media: send with caption, no extra text
            print("📎 Single media – sending with caption")
            await client.send_file(
                target_channel,
                event.message.media,
                caption=full,
                parse_mode=None
            )
            print("✅ Single media sent with caption")
        else:
            # Text‑only: split if needed
            parts = await send_long(target_channel, full)
            print(f"✅ Done – {parts} parts sent")

    except Exception as e:
        print(f"❌ Error in handler: {e}")
        import traceback
        traceback.print_exc()

async def main():
    print("\n🔌 Connecting...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Connected as @{me.username}")
    print("🤖 Bot running\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
