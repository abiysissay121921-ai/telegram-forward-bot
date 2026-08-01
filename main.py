import asyncio
from telethon import TelegramClient, events
import os
import re

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT (Single Photo per Album)")
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

processed = set()                # For single messages and group keys
pending_groups = {}              # grouped_id -> {"messages": [], "task": None}
GROUP_WAIT = 6                   # seconds to wait for all album parts

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
    """Send long text‑only messages in parts (unchanged)."""
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

# ---------- ALBUM PROCESSING (SEND ONLY FIRST MEDIA) ----------
async def process_album(grouped_id, messages):
    """Send only the first media from the album with the combined caption."""
    try:
        if grouped_id in pending_groups:
            del pending_groups[grouped_id]

        # Find the first message that has media
        first_media_msg = None
        caption_parts = []
        for msg in messages:
            if msg.raw_text:
                caption_parts.append(msg.raw_text)
            if msg.media and first_media_msg is None:
                first_media_msg = msg

        if not first_media_msg:
            print(f"⚠️ No media in grouped_id {grouped_id}, skipping.")
            return

        combined = "\n".join(caption_parts) if caption_parts else ""
        cleaned = clean_text(combined)
        full = create_full_message(cleaned)

        chat_id = messages[0].chat_id
        key = f"{chat_id}_group_{grouped_id}"
        if key in processed:
            return
        processed.add(key)
        if len(processed) > 1000:
            processed.clear()

        # Send only the first media with the full caption
        await client.send_file(
            target_channel,
            first_media_msg.media,
            caption=full,
            parse_mode=None
        )
        print(f"✅ Album → sent first media (1 of {len([m for m in messages if m.media])}) with caption length {len(full)}")

    except Exception as e:
        print(f"❌ Error processing album: {e}")
        import traceback
        traceback.print_exc()

async def buffer_album(event):
    """Add message to buffer and reset the timer."""
    grouped_id = event.message.grouped_id
    if grouped_id not in pending_groups:
        pending_groups[grouped_id] = {"messages": [], "task": None}

    if event.message not in pending_groups[grouped_id]["messages"]:
        pending_groups[grouped_id]["messages"].append(event.message)

    if pending_groups[grouped_id]["task"]:
        pending_groups[grouped_id]["task"].cancel()

    async def delayed():
        try:
            await asyncio.sleep(GROUP_WAIT)
            await process_album(grouped_id, pending_groups[grouped_id]["messages"])
        except asyncio.CancelledError:
            pass
    task = asyncio.create_task(delayed())
    pending_groups[grouped_id]["task"] = task

# ---------- ALBUM EVENT FALLBACK (also send only first) ----------
@client.on(events.Album)
async def album_fallback(event):
    try:
        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return
        grouped_id = event.grouped_id
        if not grouped_id:
            return
        key = f"{chat.id}_group_{grouped_id}"
        if key in processed:
            return
        processed.add(key)
        if len(processed) > 1000:
            processed.clear()

        # Cancel any pending buffer for this group
        if grouped_id in pending_groups:
            if pending_groups[grouped_id]["task"]:
                pending_groups[grouped_id]["task"].cancel()
            pending_groups.pop(grouped_id, None)

        print(f"📸 Album fallback from @{chat.username}")

        # Find first media and caption
        first_media = None
        caption_parts = []
        for msg in event.messages:
            if msg.raw_text:
                caption_parts.append(msg.raw_text)
            if msg.media and first_media is None:
                first_media = msg.media

        if not first_media:
            return

        combined = "\n".join(caption_parts) if caption_parts else ""
        cleaned = clean_text(combined)
        full = create_full_message(cleaned)

        await client.send_file(
            target_channel,
            first_media,
            caption=full,
            parse_mode=None
        )
        print(f"✅ Album fallback → sent first media with caption")

    except Exception as e:
        print(f"❌ Error in album fallback: {e}")
        import traceback
        traceback.print_exc()

# ---------- MAIN NEW MESSAGE HANDLER ----------
@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return

        grouped_id = event.message.grouped_id

        if grouped_id is not None:
            print(f"📨 Album part from @{chat.username} (grouped_id={grouped_id}) – buffering")
            await buffer_album(event)
            return

        # ---- Single (non‑grouped) message ----
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
            print("📎 Single media – sending with caption")
            await client.send_file(
                target_channel,
                event.message.media,
                caption=full,
                parse_mode=None
            )
            print("✅ Single media sent with caption")
        else:
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
