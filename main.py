from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional, List, Tuple

load_dotenv()

mcp = FastMCP("docs")

import os
from telethon import TelegramClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API credentials and phone number from environment variables
api_id = int(os.getenv("TG_API_ID"))
api_hash = os.getenv("TG_API_HASH")
phone = os.getenv("phone")

# Initialize the Telegram client
client = TelegramClient('session_name', api_id, api_hash)
   
    
@mcp.tool()
async def get_contacts():
    """Get contacts from Telegram based and list their names"""
    # """Get all contacts from Telegram."""
    await client.start(phone=phone)
    # print("Fetching contacts...")

    # Get all contacts
    contacts = await client.get_dialogs()  # Fetch all dialogs (chats, groups, etc.)
    # for dialog in contacts:
    #     if dialog.is_user:  # Filter only user contacts
    #         user = dialog.entity
    #         # print(f"Name: {user.first_name} {user.last_name}, Phone: {user.phone}")

    # Disconnect the client
    await client.disconnect()
    
    return contacts


if __name__ == "__main__":
    mcp.run(transport="stdio")