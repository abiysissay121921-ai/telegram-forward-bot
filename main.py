import asyncio
from telethon import TelegramClient, events
import os

print("🚀 Bot starting...")

API_ID = 37303512
API_HASH = "dff48ddff61546b05d1d507a6c508ee8"

source_channels = [
    "ayuzehabeshanews",
    "Apostolic_Answers_chat",
]
target_channel = "Newswithabiy"
your_link = "https://t.me/Newswithabiy"

print(f"📡 Monitoring: {source_channels}")
print(f"🎯 Forwarding to: {target_channel}")

# This will use the session file automatically
client = TelegramClient("user_session", API_ID, API_HASH)

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        if chat.username and chat.username in source_channels:
            print(f"📨 Message from @{chat.username}")
            text = event.raw_text or ""
            new_text = f"{text}\n\n{your_link}\nሰላም ለእናንተ!"
            
            if event.message.media:
                await client.send_file(target_channel, event.message.media, caption=new_text)
            else:
                await client.send_message(target_channel, new_text)
            print("✅ Forwarded!")
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    # This will use the existing session without asking for phone
    await client.start()
    print("✅ Bot is running!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
