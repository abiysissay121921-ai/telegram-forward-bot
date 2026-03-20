import asyncio
from telethon import TelegramClient, events
import os

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT (User Account Mode)")
print("=" * 50)

# Your API credentials
API_ID = 37303512
API_HASH = "dff48ddff61546b05d1d507a6c508ee8"

# Source channels to monitor (you must be a member)
source_channels = [
    "ayuzehabeshanews",
    "Apostolic_Answers_chat",
]

# Target channel (your channel)
target_channel = "Newswithabiy"
your_link = "https://t.me/Newswithabiy"

# Your username (for info)
your_username = "yegeta_barya"

print(f"👤 Using account: @{your_username}")
print(f"📡 Monitoring channels: {source_channels}")
print(f"🎯 Forwarding to: @{target_channel}")
print(f"🔗 Your link: {your_link}")

# Create client (uses your account)
client = TelegramClient("user_session", API_ID, API_HASH)

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    try:
        print("\n" + "=" * 50)
        print("🔔 NEW MESSAGE DETECTED!")
        print("=" * 50)
        
        # Get message text
        text = event.raw_text or ""
        print(f"Original: {text[:100]}...")
        
        # Add your signature
        new_text = f"{text}\n\n{your_link}\nሰላም ለእናንተ!"
        
        # Forward the message
        if event.message.media:
            await client.send_file(target_channel, event.message.media, caption=new_text)
            print("📤 Forwarded with media")
        else:
            await client.send_message(target_channel, new_text)
            print(f"📤 Forwarded: {new_text[:50]}...")
            
        print("✅ Successfully forwarded to @Newswithabiy!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("\n🔌 Connecting with your Telegram account...")
    print("📱 You'll need to enter your phone number and verification code\n")
    
    await client.start()
    
    print("\n✅ Connected successfully!")
    me = await client.get_me()
    print(f"👤 Logged in as: @{me.username}")
    print(f"📡 Monitoring: {source_channels}")
    print(f"🎯 Forwarding to: @{target_channel}")
    print("🤖 Bot is running and waiting for messages...")
    print("\n💡 Send a test message to any monitored channel to see it work!\n")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    print("\n🚀 Starting bot...")
    asyncio.run(main())
