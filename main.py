import os
import asyncio
from telethon import TelegramClient, events
import hashlib

# Your API credentials
api_id = 37303512
api_hash = "dff48dff61546b05d1d507a6c508ee8"

# IMPORTANT: Use JUST the username (remove https://t.me/ and @)
source_channels = [
    "ayuzehabeshanews",  # Just the username part
    "Apostolic_Answers_chat",  # Just the username part
]

# IMPORTANT: Remove @ symbol from target
target_channel = "AbiyOfficial_bot"  # Without @
your_link = "https://t.me/AbiyOfficial_bot"

posted_messages = set()
client = TelegramClient("session", api_id, api_hash)

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    try:
        print(f"📨 New message detected!")  # Debug line
        text = event.raw_text or ""
        
        # Clean the text
        for ch in source_channels:
            text = text.replace(f"@{ch}", "")
            text = text.replace(f"https://t.me/{ch}", "")
        
        # Replace t.me links
        text = text.replace("t.me", your_link)
        
        # Add signature
        text = text + "\n\n" + your_link + "\nሰላም ለእናንተ!"
        
        # Prevent duplicates
        message_hash = hashlib.md5(text.encode()).hexdigest()
        if message_hash in posted_messages:
            print("⚠️ Duplicate, skipping")
            return
        posted_messages.add(message_hash)
        
        if len(posted_messages) > 1000:
            posted_messages.clear()
        
        # Forward the message
        if event.message.media:
            await client.send_file(target_channel, event.message.media, caption=text)
            print("📤 Forwarded with media")
        else:
            await client.send_message(target_channel, text)
            print(f"📤 Forwarded: {text[:50]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("🚀 Starting bot...")
    await client.start()
    print("✅ Bot connected successfully!")
    print(f"📡 Monitoring these channels: {source_channels}")
    print(f"🎯 Forwarding to: {target_channel}")
    print("🤖 Waiting for messages...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
