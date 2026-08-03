import asyncio
import hashlib
import os
import re

from telethon import TelegramClient, events
from telethon.errors import AuthKeyDuplicatedError, FloodWaitError

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT (full albums + dedup)")
print("=" * 50)

API_ID = int(os.environ.get("API_ID", "37303512"))
API_HASH = os.environ.get("API_HASH", "dff48ddff61546b05d1d507a6c508ee8")
SESSION_FILE = os.environ.get("SESSION_FILE", "ebc_bot_session.session")

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

if not os.path.exists(SESSION_FILE):
    print(f"\n❌ Session file not found: {SESSION_FILE}")
    raise SystemExit(1)
print(f"\n✅ Session file: {SESSION_FILE}")

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

seen_ids = set()
seen_hashes = set()
send_lock = asyncio.Lock()


def remember(cache: set, key, cap: int = 1500):
    if key in cache:
        return False
    cache.add(key)
    if len(cache) > cap:
        cache.clear()
    return True


def content_fingerprint(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text or "").strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def clean_text(text):
    if not text:
        return ""
    for ch in source_channels:
        text = re.sub(rf"@{ch}\b", "", text, flags=re.IGNORECASE)
        text = re.sub(rf"https?://t\.me/{ch}\b", "", text, flags=re.IGNORECASE)
        text = re.sub(rf"t\.me/{ch}\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"https?://t\.me/\S+", "", text)
    text = re.sub(r"t\.me/\S+", "", text)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


def split_message(text, max_len=4000):
    if len(text) <= max_len:
        return [text]
    return [text[i:i + max_len] for i in range(0, len(text), max_len)]


def create_full_message(cleaned):
    intro = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
    if cleaned:
        return f"{cleaned}\n\n{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
    return f"{intro}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"


async def safe_send_file(files, caption):
    async with send_lock:
        try:
            await client.send_file(target_channel, files, caption=caption, parse_mode=None)
        except FloodWaitError as e:
            print(f"⏳ Flood wait: sleeping {e.seconds}s")
            await asyncio.sleep(e.seconds + 1)
            await client.send_file(target_channel, files, caption=caption, parse_mode=None)


async def safe_send_text(chunks):
    async with send_lock:
        first = None
        for i, chunk in enumerate(chunks, start=1):
            try:
                if first is None:
                    first = await client.send_message(target_channel, chunk, parse_mode=None)
                else:
                    await client.send_message(target_channel, chunk, reply_to=first.id, parse_mode=None)
                print(f"📤 Part {i}/{len(chunks)} sent")
                await asyncio.sleep(0.3)
            except FloodWaitError as e:
                print(f"⏳ Flood wait: sleeping {e.seconds}s")
                await asyncio.sleep(e.seconds + 1)
                await client.send_message(target_channel, chunk, parse_mode=None)


@client.on(events.Album)
async def album_handler(event):
    try:
        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return

        grouped_id = event.grouped_id
        if not grouped_id:
            return

        id_key = f"{chat.id}_group_{grouped_id}"
        if not remember(seen_ids, id_key):
            return

        print(f"\n📸 Album detected from @{chat.username}")

        media_items = []
        caption_parts = []
        for msg in event.messages:
            if msg.raw_text:
                caption_parts.append(msg.raw_text)
            if msg.media:
                media_items.append(msg.media)

        if not media_items:
            print("⚠️ No media in album, skipping.")
            return

        combined = "\n".join(caption_parts) if caption_parts else ""
        cleaned = clean_text(combined)
        full = create_full_message(cleaned)

        fingerprint = content_fingerprint(cleaned)
        if fingerprint and not remember(seen_hashes, fingerprint):
            print("🔁 Duplicate story (already posted by another source), skipping.")
            return

        captions = [full] + [""] * (len(media_items) - 1)
        await safe_send_file(media_items, captions)
        print(f"✅ Album: sent all {len(media_items)} media items with caption")

    except Exception as e:
        print(f"❌ Album handler error: {e}")
        import traceback
        traceback.print_exc()


@client.on(events.NewMessage)
async def handler(event):
    try:
        if event.message.grouped_id is not None:
            return

        chat = await event.get_chat()
        if not chat.username or chat.username not in source_channels:
            return

        id_key = f"{chat.id}_{event.id}"
        if not remember(seen_ids, id_key):
            return

        print(f"\n📨 From @{chat.username} (single message)")

        original = event.raw_text or ""
        cleaned = clean_text(original)
        full = create_full_message(cleaned)

        fingerprint = content_fingerprint(cleaned)
        if fingerprint and not remember(seen_hashes, fingerprint):
            print("🔁 Duplicate story (already posted by another source), skipping.")
            return

        if event.message.media:
            print("📎 Single media — sending with caption")
            await safe_send_file(event.message.media, full)
            print("✅ Single media sent with caption")
        else:
            chunks = split_message(full)
            print(f"📝 Splitting into {len(chunks)} parts")
            await safe_send_text(chunks)
            print(f"✅ Done — {len(chunks)} parts sent")

    except Exception as e:
        print(f"❌ Error in handler: {e}")
        import traceback
        traceback.print_exc()


async def main():
    backoff = 10
    while True:
        try:
            print("\n🔌 Connecting...")
            await client.start()
            me = await client.get_me()
            print(f"✅ Connected as @{me.username}")
            print("🤖 Bot running\n")
            backoff = 10
            await client.run_until_disconnected()
        except AuthKeyDuplicatedError:
            print(
                "\n❌ AuthKeyDuplicatedError: this session was used from "
                "another IP/device and is now invalid.\n"
                "   -> Generate a NEW session file, upload it via Railway "
                "variables/volume (not git), and redeploy.\n"
                "   Bot is stopping to avoid a restart-crash loop."
            )
            return
        except Exception as e:
            print(f"⚠️ Main loop error: {e!r}. Retrying in {backoff}s...")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 300)


if __name__ == "__main__":
    asyncio.run(main())
