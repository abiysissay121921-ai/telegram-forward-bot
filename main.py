import asyncio
import os
from telethon import TelegramClient, events

# Print immediately to show bot is starting
print("STARTING BOT...", flush=True)

# Get bot token
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN environment variable not set!", flush=True)
    exit(1)

print(f"Bot token found: {BOT_TOKEN[:10]}...", flush=True)

# Your API credentials
API_ID = 37303512
API_HASH = "dff48ddff61546b05d1d507a6c508ee8"

# Channels
source_channels = ["ayuzehabeshanews", "Apostolic_Answers_chat"]
target_channel = "Newswithabiy"
your_link = "https://t.me/Newswithabiy"

print(f"Monitoring: {source_channels}", flush=True)
print(f"Target: {target_channel}", flush=True)

# Create client
client = TelegramClient("bot_session", API_ID, API_HASH)

# Handler for new messages
@client.on(events.NewMessage)
async def handler(event):
    try:
        # Check if message is from a source channel
        chat = await event.get_chat()
        chat_username = chat.username if chat.username else ""
        
        if chat_username in source_channels:
            print(f"Message from {chat_username}: {event.raw_text}", flush=True)
            
            # Prepare message
            text = event.raw_text or ""
            new_text = f"{text}\n\n{your_link}\nሰላም ለእናንተ!"
            
            # Forward
            if event.message.media:
                await client.send_file(target_channel, event.message.media, caption=new_text)
            else:
                await client.send_message(target_channel, new_text)
            
            print("Forwarded successfully!", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

# Main function
async def main():
    print("Connecting to Telegram...", flush=True)
    await client.start(bot_token=BOT_TOKEN)
    print("Connected! Bot is running.", flush=True)
    print(f"Listening for messages...", flush=True)
    await client.run_until_disconnected()

# Run the bot
if __name__ == "__main__":
    print("Starting main...", flush=True)
    asyncio.run(main())
