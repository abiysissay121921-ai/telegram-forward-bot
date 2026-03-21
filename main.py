!pip install telethon
from telethon import TelegramClient
import asyncio
import nest_asyncio
import os

nest_asyncio.apply()

api_id = 37303512
api_hash = "dff48ddff61546b05d1d507a6c508ee8"

SESSION_NAME = "bot"

async def create():
    # Delete old if exists
    if os.path.exists(f"{SESSION_NAME}.session"):
        os.remove(f"{SESSION_NAME}.session")
        print("🗑️ Deleted old session file")
    
    print("\n🔐 Creating new Telegram session...")
    print("=" * 50)
    
    client = TelegramClient(SESSION_NAME, api_id, api_hash)
    
    # This will prompt for phone number and code
    await client.start()
    
    print("\n" + "=" * 50)
    print("✅ SUCCESS!")
    print("=" * 50)
    
    me = await client.get_me()
    print(f"👤 Logged in as: @{me.username}")
    print(f"📱 Phone: {me.phone}")
    
    # Verify file was created
    if os.path.exists(f"{SESSION_NAME}.session"):
        size = os.path.getsize(f"{SESSION_NAME}.session")
        print(f"📁 File: {SESSION_NAME}.session ({size} bytes)")
        
        if size > 1000:
            print("✅ Session file is valid and ready to use!")
        else:
            print("⚠️ WARNING: Session file is only {size} bytes - may be corrupted!")
    else:
        print("❌ ERROR: Session file was not created!")
    
    await client.disconnect()
    print("\n📥 Download this file from the folder icon on the left")

loop = asyncio.get_event_loop()
loop.run_until_complete(create())
