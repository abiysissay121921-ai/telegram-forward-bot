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

# Target channel
target_channel = "Newswithabiy"
your_link = "https://t.me/Newswithabiy"

print(f"🤖 Bot Token: {'✓' if BOT_TOKEN else '✗'}")
print(f"📡 Monitoring channels: {source_channels}")
print(f"🎯 Forwarding to: @{target_channel}")
print(f"🔗 Your channel link: {your_link}")

# Correct way to use bot token with Telethon
# We need valid API credentials, but we'll use the bot token to connect
# Get these from https://my.telegram.org
API_ID = 37303512  # Your API ID from earlier
API_HASH = "dff48dff61546b05d1d507a6c508ee8"  # Your API Hash

print(f"🔑 Using API ID: {API_ID}")

# Create client with API credentials
client = TelegramClient("forward_bot", API_ID, API_HASH)

async def main():
    print("\n🔌 Connecting to Telegram with bot token...")
    
    # Start the client with bot token
    await client.start(bot_token=BOT_TOKEN)
    
    print("✅ Connected successfully!")
    print(f"👀 Monitoring: {source_channels}")
    print(f"🎯 Forwarding to: @{target_channel}")
    print("🤖 Bot is running and waiting for messages...")
    print("\n💡 Send a test message to any monitored channel to see it work!\n")
    
    # Set up the event handler
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
                await client.send_file(target_channel, event.message.media, caption=new_text)
                print("📤 Forwarded with media")
            else:
                await client.send_message(target_channel, new_text)
                print(f"📤 Forwarded text: {new_text[:50]}...")
                
            print("✅ Successfully forwarded to @Newswithabiy!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Keep the bot running
    await client.run_until_disconnected()

if __name__ == "__main__":
    print("\n🚀 Starting bot script...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
