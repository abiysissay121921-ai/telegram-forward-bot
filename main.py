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
forwarded = set()               # For single messages and album group IDs
pending_groups = {}             # grouped_id -> {"messages": [], "task": None}
GROUP_WAIT = 3                  # seconds to wait for all album parts

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

        # Collect media and caption
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

        # Mark as processed (prevent duplicate)
        group_key = f"{chat_id}_group_{grouped_id}"  # chat_id needed here? We'll get from first message
        # Actually we need chat id – we can get from messages[0]
        chat_id = messages[0].chat_id
        key = f"{chat_id}_group_{grouped_id}"
        forwarded.add(key)

        # Send as album with the full caption
        await client.send_file(
            target_channel,
            media_list,
            caption=full,
            parse_mode=None,
            album=True
        )
        print(f"✅ Album forwarded with {len(media_list)} media items (caption length: {len(full)})")

    except Exception as e:
        print(f"❌ Error processing album: {e}")
        import traceback
        traceback.print_exc()

async def schedule_group(grouped_id, message):
    """Add message to pending group and schedule/reset timer."""
    if grouped_id not in pending_groups:
        pending_groups[grouped_id] = {"messages": [], "task": None}

    # Add message (avoid duplicates)
    if message not in pending_groups[grouped_id]["messages"]:
        pending_groups[grouped_id]["messages"].append(message)

    # Cancel existing timer if any
    if pending_groups[grouped_id]["task"]:
        pending_groups[grouped_id]["task"].cancel()

    # Create new timer
    async def delayed_process():
        try:
            await asyncio.sleep(GROUP_WAIT)
            # Process whatever messages are collected
            await process_group(grouped_id, pending_groups[grouped_id]["messages"])
        except asyncio.CancelledError:
            pass  # Timer was reset
    task = asyncio.create_task(delayed_process())
    pending_groups[grouped_id]["task"] = task

# ========== MAIN NEW MESSAGE HANDLER ==========
@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return

        grouped_id = event.message.grouped_id

        # If it's part of an album, buffer it
        if grouped_id is not None:
            print(f"📨 Album part from @{chat.username} (grouped_id={grouped_id})")
            await schedule_group(grouped_id, event.message)
            return

        # ---- Non-grouped message (single media or text) ----
        msg_id = f"{chat.id}_{event.id}"
        if msg_id in forwarded:
            return
        forwarded.add(msg_id)
        if len(forwarded) > 1000:
            forwarded.clear()

        print(f"\n📨 From @{chat.username} (single message)")

        original = event.raw_text or ""
        cleaned = clean_text(original)
        full = create_full_message(cleaned)

        if event.message.media:
            # Single media: send with full caption, NO extra text
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
        print(f"❌ Error in handler: {e}")
        import traceback
        traceback.print_exc()

# ========== FALLBACK ALBUM HANDLER (if buffering fails) ==========
@client.on(events.Album)
async def album_fallback(event):
    try:
        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return
        grouped_id = event.grouped_id
        if not grouped_id:
            return
        group_key = f"{chat.id}_group_{grouped_id}"
        if group_key in forwarded:
            return  # Already processed by buffering
        forwarded.add(group_key)

        print(f"📸 Album fallback triggered from @{chat.username}")
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
        print(f"✅ Album fallback forwarded with {len(media_list)} media items")
    except Exception as e:
        print(f"❌ Error in album fallback: {e}")
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
