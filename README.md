from telethon import TelegramClient, events
import hashlib

api_id = 123456
api_hash = "YOUR_API_HASH"

source_channels = [
    "channel1",
    "channel2",
    "channel3",
    "channel4",
    "channel5"
]

target_channel = "yourchannelusername"
your_link = "https://t.me/yourchannelusername"

posted_messages = set()

client = TelegramClient("session", api_id, api_hash)

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):

    text = event.raw_text or ""

    for ch in source_channels:
        text = text.replace(f"@{ch}", "")

    text = text.replace("t.me", your_link)

    text = text + "\n\n" + your_link + "\nሰላም ለእናንተ!"

    message_hash = hashlib.md5(text.encode()).hexdigest()
    if message_hash in posted_messages:
        return
    posted_messages.add(message_hash)

    if event.message.media:
        await client.send_file(target_channel, event.message.media, caption=text)
    else:
        await client.send_message(target_channel, text)

client.start()
print("Bot running...")
client.run_until_disconnected()
