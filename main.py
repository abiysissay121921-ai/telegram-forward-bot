import asyncio
from telethon import TelegramClient, events
import os

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT STARTING")
print("=" * 50)

# Get bot token from Railway variables
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not set in Railway variables!")
    print("Please add BOT_TOKEN in Variables tab")
    exit(1)

# Source channels to monitor (JUST the username, no @ or https://)
source_channels = [
    "ayuzehabeshanews",
    "Apostolic_Answers_chat",
]

# Target channel (YOUR NEW CHANNEL)
target_channel = "Newswithabiy"  # Just the username, no @
your_link = "https://t.me/Newswithabiy"

print(f"🤖 Bot Token: ✓")
print(f"📡 Monitoring channels: {source_channels}")
print(f"🎯 Forwarding to: @{target_channel}")
print(f"🔗 Your channel link: {your_link}")

# Create client with bot token
client = TelegramClient("forward_bot", api_id=0, api_hash="").start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    try:
        print("\n" + "=" * 50)
        print("🔔 NEW MESSAGE DETECTED!")
        print("=" * 50)
        
        # Get the message text
        text = event.raw_text or ""
        print(f"Original message: {text[:100]}...")
        
        # Add your signature and link
        new_text = f"{text}\n\n{your_link}\nሰላም ለእናንተ!"
        
        # Forward the message
        if event.message.media:
            # Message has photo, video, or file
            await client.send_file(target_channel, event.message.media, caption=new_text)
            print("📤 Forwarded with media (photo/video/file)")
        else:
            # Text only message
            await client.send_message(target_channel, new_text)
            print(f"📤 Forwarded text: {new_text[:50]}...")
            
        print("✅ Successfully forwarded to @Newswithabiy!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("\n🔌 Connecting to Telegram...")
    await client.start()
    print("✅ Connected successfully!")
    print(f"👀 Monitoring these channels: {source_channels}")
    print(f"🎯 Forwarding to: @{target_channel}")
    print("🤖 Bot is running and waiting for messages...")
    print("\n💡 Send a test message to any monitored channel to see it work!\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    print("\n🚀 Starting bot script...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
