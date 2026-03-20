import asyncio
from telethon import TelegramClient, events
import os

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT STARTING")
print("=" * 50)

# Your credentials
api_id = 37303512
api_hash = "dff48dff61546b05d1d507a6c508ee8"

# Source channels
source_channels = [
    "ayuzehabeshanews",
    "Apostolic_Answers_chat",
]

target_channel = "AbiyOfficial_bot"
your_link = "https://t.me/AbiyOfficial_bot"

print(f"📡 Monitoring: {source_channels}")
print(f"🎯 Forwarding to: {target_channel}")
print(f"🔗 Your link: {your_link}")

# Create client
client = TelegramClient("bot_session", api_id, api_hash)

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    try:
        print("\n🔔 NEW MESSAGE RECEIVED!")
        text = event.raw_text or ""
        
        # Add your signature
        new_text = f"{text}\n\n{your_link}\nሰላም ለእናንተ!"
        
        # Forward
        if event.message.media:
            await client.send_file(target_channel, event.message.media, caption=new_text)
            print("📤 Forwarded with media")
        else:
            await client.send_message(target_channel, new_text)
            print(f"📤 Forwarded: {new_text[:50]}...")
            
        print("✅ Done!")
    except Exception as e:
        print(f"❌ Error in handler: {e}")

async def main():
    try:
        print("\n🔌 Connecting to Telegram...")
        print("📱 You will be asked for your phone number and verification code")
        print("💡 Make sure to enter them correctly\n")
        
        # Start the client
        await client.start()
        
        print("\n✅ Connected successfully!")
        print(f"👀 Bot is now monitoring: {source_channels}")
        print("🤖 Waiting for messages...")
        print("\n💡 Send a test message to any monitored channel to see it work!\n")
        
        # Keep the bot running
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Check your API ID and Hash are correct")
        print("2. Make sure your phone number is correct with country code")
        print("3. Try again in a few minutes")
        raise

if __name__ == "__main__":
    print("\n🚀 Starting bot script...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
