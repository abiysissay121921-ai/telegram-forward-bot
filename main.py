import asyncio
from telethon import TelegramClient, events
import os
import re

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT")
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
forwarded = set()          # used for deduplication
pending_groups = {}        # grouped_id -> [messages, timer_task]
GROUP_WAIT = 2             # seconds to wait for album completion

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

async def process_group(grouped_id, messages):
    """Forward all media from an album together with the combined caption."""
    try:
        # Remove from pending
        if grouped_id in pending_groups:
            del pending_groups[grouped_id]

        # Collect media and captions
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

        # Combine captions (if multiple) – usually only one has text
        combined_caption = "\n".join(caption_parts) if caption_parts else ""
        cleaned = clean_text(combined_caption)
        full = create_full_message(cleaned)

        # Send as album with the full caption
        await client.send_file(
            target_channel,
            media_list,
            caption=full,
            parse_mode=None,
            album=True
        )
        print(f"✅ Album forwarded with {len(media_list)} media items")

    except Exception as e:
        print(f"❌ Error processing album: {e}")
        import traceback
        traceback.print_exc()

async def handle_group_message(event, grouped_id):
    """Add message to pending group and schedule processing."""
    if grouped_id not in pending_groups:
        pending_groups[grouped_id] = {
            "messages": [],
            "task": None
        }
    # Add message (avoid duplicates)
    if event.message not in pending_groups[grouped_id]["messages"]:
        pending_groups[grouped_id]["messages"].append(event.message)

    # If no timer task, create one
    if pending_groups[grouped_id]["task"] is None:
        async def delayed_process():
            await asyncio.sleep(GROUP_WAIT)
            # Process whatever messages are collected
            await process_group(grouped_id, pending_groups[grouped_id]["messages"])
        task = asyncio.create_task(delayed_process())
        pending_groups[grouped_id]["task"] = task

# ========== MAIN NEW MESSAGE HANDLER ==========
@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return

        # Deduplication by full message ID (only for non-grouped)
        # For grouped, we'll use a separate dedup based on grouped_id
        msg_id = f"{chat.id}_{event.id}"
        if msg_id in forwarded:
            return
        # If it's a grouped message, we'll handle it via buffering
        grouped_id = event.message.grouped_id
        if grouped_id is not None:
            # Check if we already processed this group
            group_key = f"{chat.id}_group_{grouped_id}"
            if group_key in forwarded:
                return
            # Mark that we've seen this group (to avoid duplicate processing)
            # but we only mark after processing, so we'll mark later.
            # For now, just buffer.
            await handle_group_message(event, grouped_id)
            return

        # ---- Non-grouped message (single media or text) ----
        forwarded.add(msg_id)
        if len(forwarded) > 1000:
            forwarded.clear()

        print(f"\n📨 From @{chat.username} (single message)")

        original = event.raw_text or ""
        cleaned = clean_text(original)
        full = create_full_message(cleaned)

        if event.message.media:
            # Single media: send with full caption, no extra text
            print("📎 Single media – sending with caption")
            await client.send_file(
                target_channel,
                event.message.media,
                caption=full,
                parse_mode=None
            )
            print("✅ Media sent with caption")
        else:
            # Text-only: split if needed
            parts = await send_long(target_channel, full)
            print(f"✅ Done – {parts} parts sent")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

# Also listen to Album events as a fallback, but the above should handle all
@client.on(events.Album)
async def album_fallback(event):
    # If the buffering logic didn't catch it, this will still forward as album.
    # However, we'll skip if already processed via the main handler.
    chat = await event.get_chat()
    if not chat.username or chat.username not in source_channels:
        return
    grouped_id = event.grouped_id
    if not grouped_id:
        return
    group_key = f"{chat.id}_group_{grouped_id}"
    if group_key in forwarded:
        return
    # Mark as processed
    forwarded.add(group_key)
    # Collect media and caption
    media_list = [msg.media for msg in event.messages if msg.media]
    if not media_list:
        return
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
    print(f"✅ Album fallback forwarded with {len(media_list)} media items")

async def main():
    print("\n🔌 Connecting...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Connected as @{me.username}")
    print("🤖 Bot running\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
