import asyncio
import os
import re

from telethon import TelegramClient, events
from telethon.sessions import StringSession

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT")
print("=" * 50)

# ── CONFIG ────────────────────────────────────────────────────────────────────
API_ID   = int(os.environ.get("API_ID", 37303512))
API_HASH = os.environ.get("API_HASH", "dff48ddff61546b05d1d507a6c508ee8")
SESSION  = os.environ.get("SESSION_STRING", "")

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
your_link      = "https://t.me/NewsWith_Abiy"

print(f"\n📡 Monitoring {len(source_channels)} channels:")
for ch in source_channels:
    print(f"   - @{ch}")
print(f"🎯 Forwarding to: @{target_channel}")

# ── SESSION ───────────────────────────────────────────────────────────────────
if SESSION:
    client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
    print("\n✅ Using StringSession (Railway mode)")
else:
    SESSION_FILE = "bot_session.session"
    if not os.path.exists(SESSION_FILE):
        print(f"\n❌ Session file not found: {SESSION_FILE}")
        print("Run setup.py first, or set the SESSION_STRING environment variable.")
        exit(1)
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    print(f"\n✅ Using session file: {SESSION_FILE} (local mode)")

# ── HELPERS ───────────────────────────────────────────────────────────────────
forwarded: set = set()

def clean_text(text: str) -> str:
    if not text:
        return ""
    for ch in source_channels:
        text = re.sub(rf'@{re.escape(ch)}\b', '', text, flags=re.IGNORECASE)
        text = re.sub(rf'https?://t\.me/{re.escape(ch)}\b', '', text, flags=re.IGNORECASE)
        text = re.sub(rf't\.me/{re.escape(ch)}\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'https?://t\.me/\S+', '', text)
    text = re.sub(r't\.me/\S+', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def build_message(cleaned: str) -> str:
    intro  = "የቴሌግራም ቻናላችን join በማድረግ ወቅታዊ መረጃዎችን በቀላሉ ይከታተሉ!"
    footer = f"{intro}\n\n{your_link}\nሰላም ለእናንተ!"
    msg    = f"{cleaned}\n\n{footer}" if cleaned else footer
    if len(msg) > 4096:
        msg = msg[:4090] + "…"
    return msg

# ── EVENT HANDLER ─────────────────────────────────────────────────────────────
@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()

        if not getattr(chat, "username", None):
            return
        if chat.username.lower() not in [c.lower() for c in source_channels]:
            return

        msg_id = f"{chat.id}_{event.id}"
        if msg_id in forwarded:
            print(f"⏭️  Skipping duplicate: {msg_id}")
            return
        forwarded.add(msg_id)
        if len(forwarded) > 1000:
            forwarded.clear()

        print(f"\n📨 New message from @{chat.username}")

        cleaned = clean_text(event.raw_text or "")
        msg     = build_message(cleaned)

        if event.message.media:
            await client.send_file(target_channel, event.message.media, caption=msg)
            print("📸 Media forwarded")
        else:
            await client.send_message(target_channel, msg, link_preview=False)
            print("📤 Text forwarded")

        print("✅ Done!")

    except Exception as e:
        print(f"❌ Error: {e}")

# ── MAIN ──────────────────────────────────────────────────────────────────────
async def main():
    print("\n🔌 Connecting to Telegram...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Connected as: @{me.username}")
    print("🤖 Bot is running...\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
