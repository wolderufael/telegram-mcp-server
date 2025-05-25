from telethon import TelegramClient
import os
from dotenv import load_dotenv
from telethon.errors import SessionPasswordNeededError

load_dotenv()
api_id = int(os.getenv("TG_API_ID"))
api_hash = os.getenv("TG_API_HASH")
phone = os.getenv("phone")

client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.connect()
    if not await client.is_user_authorized():
        print("You need to log in to Telegram.")
        await client.send_code_request(phone)
        code = input("Enter the code you received: ")
        try:
            await client.sign_in(phone, code)
        except SessionPasswordNeededError:
            password = input("Two-step verification enabled. Enter your password: ")
            await client.sign_in(password=password)
        print("✅ Successfully authenticated with Telegram! Session file created.")
    else:
        print("You are already authenticated. Session file exists.")
    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.get_event_loop().run_until_complete(main()) 