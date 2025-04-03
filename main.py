from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional, List, Tuple

load_dotenv()

mcp = FastMCP("telegram")

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
    """ Get the names of the contacts """
    await client.start(phone=phone)

    # Get all contacts
    contacts = await client.get_dialogs()  # Fetch all dialogs (chats, groups, etc.)
    personal_contacts = []
    
    for dialog in contacts:
        if dialog.is_user and hasattr(dialog.entity, 'bot') and not dialog.entity.bot:  # Filter only personal user contacts
            user = dialog.entity
            contact_info = {
                'name': f"{user.first_name} {user.last_name if user.last_name else ''}".strip(),
                'phone': user.phone if user.phone else 'No phone',
                'username': f"@{user.username}" if user.username else 'No username'
            }
            personal_contacts.append(contact_info)

    # Disconnect the client
    await client.disconnect()
    
    return personal_contacts


@mcp.tool()
async def send_message_by_name(name: str, message: str):
    """Send a message to a specific user by their name
    
    Args:
        name: The name of the contact to send the message to
        message: The message to send
    """
    await client.start(phone=phone)
    
    # Get all contacts
    contacts = await client.get_dialogs()
    
    # Find the user by name
    target_user = None
    for dialog in contacts:
        if dialog.is_user and hasattr(dialog.entity, 'bot') and not dialog.entity.bot:
            user = dialog.entity
            full_name = f"{user.first_name} {user.last_name if user.last_name else ''}".strip()
            if full_name.lower() == name.lower():
                target_user = user
                break
    
    if target_user:
        # Send the message
        await client.send_message(target_user, message)
        result = f"Message sent successfully to {name}"
    else:
        result = f"Could not find user with name: {name}"
    
    await client.disconnect()
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")