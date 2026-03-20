import asyncio
from telethon import TelegramClient, events

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT STARTING")
print("=" * 50)

# Your credentials
api_id = 37303512
api_hash = "dff48dff61546b05d1d507a6c508ee8"

# Source channels (use JUST the username, no @ or https://)
source_channels = [
    "ayuzehabeshanews",
    "Apostolic_Answers_chat",
]

# Target channel (use JUST the username, no @)
target_channel = "AbiyOfficial_bot"
your_link = "https://t.me/AbiyOfficial_bot"

print(f"📡 Monitoring channels: {source_channels}")
print(f"🎯 Forwarding to: {target_channel}")
print(f"🔗 Your link: {your_link}")

# Create the client
client = TelegramClient("bot_session", api_id, api_hash)

# This function runs for every new message
@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    try:
        print("\n" + "=" * 50)
        print("🔔 NEW MESSAGE DETECTED!")
        print("=" * 50)
        
        # Get the message text
        text = event.raw_text or ""
        print(f"Message content: {text[:100]}...")
        
        # Add your signature
        new_text = f"{text}\n\n{your_link}\nሰላም ለእናንተ!"
        
        # Forward the message
        if event.message.media:
            await client.send_file(target_channel, event.message.media, caption=new_text)
            print("📤 Forwarded with media (photo/video/file)")
        else:
            await client.send_message(target_channel, new_text)
            print(f"📤 Forwarded text: {new_text[:50]}...")
        
        print("✅ Successfully forwarded!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Main function
async def main():
    print("\n🔌 Connecting to Telegram...")
    await client.start()
    print("✅ Connected successfully!")
    print(f"\n👀 Bot is now monitoring: {source_channels}")
    print("🤖 Waiting for new messages...")
    print("\n💡 Tip: Send a message to any monitored channel to test!\n")
    await client.run_until_disconnected()

# Start the bot
if __name__ == "__main__":
    print("🚀 Starting bot...")
    asyncio.run(main())
