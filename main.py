import asyncio
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters
import os

print("=" * 50)
print("🚀 TELEGRAM FORWARD BOT")
print("=" * 50)

# Bot token
BOT_TOKEN = "8602729297:AAGog9z7FVCs8--IoajFT4JlS3vwga8pxUI"

# Source channels (channel usernames)
source_channels = [
    "ayuzehabeshanews",
    "Addis_News",
    "NatnaelMekonnen21",
    "tikvahethiopia",
    "eliasmeseret",
    "TikvahUniversity",
    "abiyselol",
]

target_channel = "NewsWith_Abiy"
your_link = "https://t.me/NewsWith_Abiy"

print(f"\n🤖 Bot: @AbiyOfficial_bot")
print(f"📡 Monitoring {len(source_channels)} channels:")
for channel in source_channels:
    print(f"   - @{channel}")
print(f"🎯 Forwarding to: @{target_channel}")

# Store forwarded message IDs
forwarded_messages = set()

async def handle_message(update: Update, context):
    try:
        message = update.channel_post or update.message
        if not message:
            return
        
        chat = message.chat
        if not chat.username or chat.username not in source_channels:
            return
        
        msg_id = f"{chat.id}_{message.message_id}"
        if msg_id in forwarded_messages:
            print(f"⏭️ Skipping duplicate from @{chat.username}")
            return
        
        forwarded_messages.add(msg_id)
        if len(forwarded_messages) > 1000:
            forwarded_messages.clear()
        
        print(f"\n📨 NEW Message from @{chat.username}")
        text = message.text or message.caption or ""
        new_text = f"{text}\n\n{your_link}\n{your_link}\n{your_link}\nሰላም ለእናንተ!"
        
        # Forward the message
        if message.photo:
            photo = message.photo[-1].file_id
            await context.bot.send_photo(chat_id=target_channel, photo=photo, caption=new_text[:1024])
            print("📤 Forwarded photo")
        elif message.video:
            await context.bot.send_video(chat_id=target_channel, video=message.video.file_id, caption=new_text[:1024])
            print("📤 Forwarded video")
        elif message.document:
            await context.bot.send_document(chat_id=target_channel, document=message.document.file_id, caption=new_text[:1024])
            print("📤 Forwarded document")
        elif message.text:
            await context.bot.send_message(chat_id=target_channel, text=new_text[:4096])
            print(f"📤 Forwarded text: {new_text[:50]}...")
        else:
            print(f"⚠️ Unknown message type from @{chat.username}")
        
        print("✅ Done!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("\n🔌 Connecting to Telegram...")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.ALL, handle_message))
    
    await application.initialize()
    await application.start()
    print("✅ Bot is running!")
    print("🤖 Waiting for messages...\n")
    
    # Keep the bot running
    await application.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
