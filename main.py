import asyncio
from telethon import TelegramClient, events
import os
import re
import time

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

processed = set()          # for deduplication (single messages and groups)
buffers = {}               # chat_id -> {"msg_ids": set(), "messages": [], "task": None}
BUFFER_WINDOW = 6          # seconds – messages within this window are grouped

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

async def process_buffer(chat_id):
    """Process the buffered messages for a chat."""
    data = buffers.pop(chat_id, None)
    if not data:
        return
    messages = data.get("messages", [])
    if not messages:
        return

    # Combine captions and find first media
    caption_parts = []
    first_media = None
    for msg in messages:
        if msg.raw_text:
            caption_parts.append(msg.raw_text)
        if msg.media and first_media is None:
            first_media = msg.media

    combined = "\n".join(caption_parts) if caption_parts else ""
    cleaned = clean_text(combined)
    full = create_full_message(cleaned)

    # Deduplicate based on chat + first message ID
    key = f"{chat_id}_{messages[0].id}"
    if key in processed:
        print(f"⏩ Skipping already processed buffer for chat {chat_id}")
        return
    processed.add(key)
    if len(processed) > 1000:
        processed.clear()

    if first_media:
        # Send only the first media with full caption
        await client.send_file(
            target_channel,
            first_media,
            caption=full,
            parse_mode=None
        )
        total_media = len([m for m in messages if m.media])
        print(f"✅ Album: sent first media (1 of {total_media}) with caption length {len(full)}")
    else:
        # Text-only – send as text (split if needed)
        print(f"📝 Text-only message, sending as text")
        await send_long(target_channel, full)

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return

        chat_id = chat.id

        # Initialize buffer for this chat
        if chat_id not in buffers:
            buffers[chat_id] = {"msg_ids": set(), "messages": [], "task": None}

        # Add message (avoid duplicates using message.id)
        msg_id = event.message.id
        if msg_id not in buffers[chat_id]["msg_ids"]:
            buffers[chat_id]["msg_ids"].add(msg_id)
            buffers[chat_id]["messages"].append(event.message)

        # Cancel existing timer
        if buffers[chat_id]["task"]:
            try:
                buffers[chat_id]["task"].cancel()
            except:
                pass

        # Start new timer
        async def delayed():
            try:
                await asyncio.sleep(BUFFER_WINDOW)
                await process_buffer(chat_id)
            except asyncio.CancelledError:
                pass  # Timer was reset
            except Exception as e:
                print(f"❌ Error in delayed task: {e}")
                import traceback
                traceback.print_exc()

        task = asyncio.create_task(delayed())
        buffers[chat_id]["task"] = task

        print(f"📨 Buffered message from @{chat.username} (buffer size: {len(buffers[chat_id]['messages'])})")

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
