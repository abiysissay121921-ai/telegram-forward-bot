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

# Your API credentials (from my.telegram.org)
API_ID = 37303512
API_HASH = "dff48ddff61546b05d1d507a6c508ee8"

# Source channels to monitor (JUST the username, no @ or https://)
source_channels = [
    "ayuzehabeshanews",
    "Apostolic_Answers_chat",
]

# Target channel
target_channel = "Newswithabiy"
your_link = "https://t.me/Newswithabiy"

print(f"🤖 Bot Token: {'✓' if BOT_TOKEN else '✗'}")
print(f"🔑 API ID: {API_ID}")
print(f"📡 Monitoring channels: {source_channels}")
print(f"🎯 Forwarding to: @{target_channel}")
print(f"🔗 Your channel link: {your_link}")

# Create client
client = TelegramClient("forward_bot", API_ID, API_HASH)

async def main():
    print("\n🔌 Connecting to Telegram with bot token...")
    
    try:
        # Start the client with bot token
        await client.start(bot_token=BOT_TOKEN)
        print("✅ Connected successfully!")
        
        # Get bot info
        me = await client.get_me()
        print(f"🤖 Bot username: @{me.username}")
        print(f"📝 Bot name: {me.first_name}")
        
        print(f"\n👀 Monitoring these channels:")
        for channel in source_channels:
            print(f"   - @{channel}")
        
        print(f"\n🎯 Forwarding to: @{target_channel}")
        print("🤖 Bot is running and waiting for messages...")
        print("\n💡 Send a test message to any monitored channel to see it work!\n")
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure your bot token is correct")
        print("2. Make sure the bot is added to the channels")
        print("3. Make sure the bot has admin rights in target channel")
        return
    
    # Event handler for new messages
    @client.on(events.NewMessage(chats=source_channels))
    async def handler(event):
        try:
            print("\n" + "=" * 50)
            print("🔔 NEW MESSAGE DETECTED!")
            print("=" * 50)
            
            # Get the message text
            text = event.raw_text or ""
            print(f"Original message: {text[:100]}...")
            
            # Get sender info
            sender = await event.get_sender()
            print(f"From: {sender.username if sender.username else 'Unknown'}")
            
            # Add your signature and link
            new_text = f"{text}\n\n{your_link}\nሰላም ለእናንተ!"
            
            # Forward the message
            if event.message.media:
                await client.send_file(target_channel, event.message.media, caption=new_text)
                print("📤 Forwarded with media (photo/video/file)")
            else:
                await client.send_message(target_channel, new_text)
                print(f"📤 Forwarded text: {new_text[:50]}...")
                
            print("✅ Successfully forwarded to @Newswithabiy!")
            
        except Exception as e:
            print(f"❌ Error in handler: {e}")
    
    # Keep the bot running
    await client.run_until_disconnected()

if __name__ == "__main__":
    print("\n🚀 Starting bot script...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
