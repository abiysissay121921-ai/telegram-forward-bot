import asyncio
from telethon import TelegramClient, events
import os
import re

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT (Fixed Album)")
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

# Store processed IDs (for single messages) and group IDs (for albums)
processed_ids = set()
grouped_buffer = {}          # grouped_id -> {"messages": [], "task": None}
GROUP_WAIT = 5               # seconds to wait for all album parts

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
    """Send long text-only messages in parts (unchanged)."""
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

# ---------- ALBUM BUFFERING FALLBACK ----------
async def process_buffered_group(grouped_id):
    """Forward collected messages as an album."""
    try:
        data = grouped_buffer.pop(grouped_id, None)
        if not data:
            return
        messages = data["messages"]
        if not messages:
            return

        # Extract media and captions
        media_list = []
        caption_parts = []
        for msg in messages:
            if msg.media:
                media_list.append(msg.media)
            if msg.raw_text:
                caption_parts.append(msg.raw_text)

        if not media_list:
            print(f"⚠️ No media in grouped_id {grouped_id}, skipping.")
            return

        # Combine captions (usually only one has text)
        combined = "\n".join(caption_parts) if caption_parts else ""
        cleaned = clean_text(combined)
        full = create_full_message(cleaned)

        # Mark as processed to avoid duplicates
        chat_id = messages[0].chat_id
        key = f"{chat_id}_group_{grouped_id}"
        if key in processed_ids:
            return
        processed_ids.add(key)
        if len(processed_ids) > 1000:
            processed_ids.clear()

        # Send as album
        await client.send_file(
            target_channel,
            media_list,
            caption=full,
            parse_mode=None,
            album=True
        )
        print(f"✅ Album forwarded (buffered) – {len(media_list)} media items, caption length {len(full)}")
    except Exception as e:
        print(f"❌ Error processing buffered album: {e}")
        import traceback
        traceback.print_exc()

async def add_to_buffer(event):
    """Add message to buffer and reset timer."""
    grouped_id = event.message.grouped_id
    if grouped_id not in grouped_buffer:
        grouped_buffer[grouped_id] = {"messages": [], "task": None}

    # Avoid duplicates
    if event.message not in grouped_buffer[grouped_id]["messages"]:
        grouped_buffer[grouped_id]["messages"].append(event.message)

    # Cancel existing timer
    if grouped_buffer[grouped_id]["task"]:
        grouped_buffer[grouped_id]["task"].cancel()

    # Start new timer
    async def delayed():
        try:
            await asyncio.sleep(GROUP_WAIT)
            await process_buffered_group(grouped_id)
        except asyncio.CancelledError:
            pass
    task = asyncio.create_task(delayed())
    grouped_buffer[grouped_id]["task"] = task

# ---------- PRIMARY ALBUM HANDLER ----------
@client.on(events.Album)
async def album_handler(event):
    try:
        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return

        grouped_id = event.grouped_id
        if not grouped_id:
            return

        # Mark as processed to avoid duplicate processing (e.g., from buffer)
        key = f"{chat.id}_group_{grouped_id}"
        if key in processed_ids:
            return
        processed_ids.add(key)
        if len(processed_ids) > 1000:
            processed_ids.clear()

        # Cancel any pending buffer for this group
        if grouped_id in grouped_buffer:
            if grouped_buffer[grouped_id]["task"]:
                grouped_buffer[grouped_id]["task"].cancel()
            grouped_buffer.pop(grouped_id, None)

        print(f"📸 Album detected from @{chat.username}")

        media_list = [msg.media for msg in event.messages if msg.media]
        if not media_list:
            return

        # Get caption from first message with text
        caption = ""
        for msg in event.messages:
            if msg.raw_text:
                caption = msg.raw_text
                break

        cleaned = clean_text(caption)
        full = create_full_message(cleaned)

        await client.send_file(
            target_channel,
            media_list,
            caption=full,
            parse_mode=None,
            album=True
        )
        print(f"✅ Album forwarded (Album event) – {len(media_list)} media items, caption length {len(full)}")
    except Exception as e:
        print(f"❌ Error in album handler: {e}")
        import traceback
        traceback.print_exc()

# ---------- SINGLE MESSAGE HANDLER ----------
@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return

        grouped_id = event.message.grouped_id

        # If it's part of an album, buffer it (fallback in case Album event didn't fire)
        if grouped_id is not None:
            print(f"📨 Album part from @{chat.username} (grouped_id={grouped_id}) – buffering")
            await add_to_buffer(event)
            return

        # ---- Single (non‑grouped) message ----
        msg_id = f"{chat.id}_{event.id}"
        if msg_id in processed_ids:
            return
        processed_ids.add(msg_id)
        if len(processed_ids) > 1000:
            processed_ids.clear()

        print(f"\n📨 From @{chat.username} (single message)")

        original = event.raw_text or ""
        cleaned = clean_text(original)
        full = create_full_message(cleaned)

        if event.message.media:
            # Single media – send with full caption, NO extra text
            print("📎 Single media – sending with caption attached")
            await client.send_file(
                target_channel,
                event.message.media,
                caption=full,
                parse_mode=None
            )
            print("✅ Media sent with caption")
        else:
            # Text‑only – split if needed
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
