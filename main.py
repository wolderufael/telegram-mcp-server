from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
#from dataclasses import dataclass
#from typing import Optional, List, Tuple
from datetime import datetime
import pytz
#import asyncio
import os
from telethon import TelegramClient
from dotenv import load_dotenv
from telethon.errors import SessionPasswordNeededError
import inspect
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

mcp = FastMCP("telegram")

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
    if not client.is_connected():
        await client.connect()
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

    return personal_contacts


@mcp.tool()
async def send_message_by_identifier(identifier: str, message: str):
    """Send a message to a specific user by their name or phone number
    
    Args:
        identifier: The name or phone number of the contact
        message: The message to send
    """
    if not client.is_connected():
        await client.connect()
    target_user = None
    found_name = None
    for dialog in await client.get_dialogs():
        if dialog.is_user and hasattr(dialog.entity, 'bot') and not dialog.entity.bot:
            user = dialog.entity
            full_name = f"{user.first_name} {user.last_name if user.last_name else ''}".strip()
            user_phone = user.phone if user.phone else ''
            
            # Match by name or phone (remove any non-numeric characters from phone for comparison)
            if (full_name.lower() == identifier.lower() or 
                ''.join(filter(str.isdigit, user_phone)) == ''.join(filter(str.isdigit, identifier))):
                target_user = user
                found_name = full_name
                break
    
    if target_user:
        # Send the message
        await client.send_message(target_user, message)
        result = f"Message sent successfully to {found_name}"
    else:
        result = f"Could not find user with identifier: {identifier}"
    
    return result


@mcp.tool()
async def get_last_interaction(identifier: str):
    """Get the last interaction with a contact by their name or phone number
    
    Args:
        identifier: The name or phone number of the contact
    """
    if not client.is_connected():
        await client.connect()
    target_dialog = None
    found_name = None
    for dialog in await client.get_dialogs():
        if dialog.is_user and hasattr(dialog.entity, 'bot') and not dialog.entity.bot:
            user = dialog.entity
            full_name = f"{user.first_name} {user.last_name if user.last_name else ''}".strip()
            user_phone = user.phone if user.phone else ''
            
            # Match by name or phone (remove any non-numeric characters from phone for comparison)
            if (full_name.lower() == identifier.lower() or 
                ''.join(filter(str.isdigit, user_phone)) == ''.join(filter(str.isdigit, identifier))):
                target_dialog = dialog
                found_name = full_name
                break
    
    if target_dialog:
        # Get the last message
        messages = await client.get_messages(target_dialog.entity, limit=1)
        if messages and messages[0]:
            last_msg = messages[0]
            sender = "You" if last_msg.out else found_name
            time = last_msg.date.strftime("%Y-%m-%d %H:%M:%S")
            
            result = {
                "contact": found_name,
                "last_message": {
                    "text": last_msg.message,
                    "sender": sender,
                    "time": time,
                    "is_outgoing": last_msg.out
                }
            }
        else:
            result = {
                "contact": found_name,
                "last_message": None,
                "error": "No messages found"
            }
    else:
        result = {
            "error": f"Could not find contact with identifier: {identifier}"
        }
    
    return result


@mcp.tool()
async def get_chat_history(identifier: str, start_date: str = None, end_date: str = None, limit: int = 20):
    """Get chat history with a contact within a specified time span
    
    Args:
        identifier: The name or phone number of the contact
        start_date: Start date in format 'YYYY-MM-DD' (optional)
        end_date: End date in format 'YYYY-MM-DD' (optional)
        limit: Maximum number of messages to return (default 20)
    """ 
    if not client.is_connected():
        await client.connect()
    target_user = None
    found_name = None
    for dialog in await client.get_dialogs():
        if dialog.is_user and hasattr(dialog.entity, 'bot') and not dialog.entity.bot:
            user = dialog.entity
            full_name = f"{user.first_name} {user.last_name if user.last_name else ''}".strip()
            user_phone = user.phone if user.phone else ''
            
            # Match by name or phone (remove any non-numeric characters from phone for comparison)
            if (full_name.lower() == identifier.lower() or 
                ''.join(filter(str.isdigit, user_phone)) == ''.join(filter(str.isdigit, identifier))):
                target_user = user
                found_name = full_name
                break
    
    if not target_user:
        return {"error": f"Could not find user with identifier: {identifier}"}

    # Convert date strings to datetime objects
    try:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC) if start_date else None
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC) if end_date else None
    except ValueError as e:
        return {"error": f"Invalid date format. Please use YYYY-MM-DD format. Error: {str(e)}"}

    # Get messages
    messages = []
    async for message in client.iter_messages(target_user, limit=limit):
        # Skip messages outside the time range if specified
        if start_datetime and message.date < start_datetime:
            continue
        if end_datetime and message.date > end_datetime:
            continue
            
        messages.append({
            "text": message.message,
            "sender": "You" if message.out else found_name,
            "time": message.date.strftime("%Y-%m-%d %H:%M:%S"),
            "is_outgoing": message.out
        })

    result = {
        "contact": found_name,
        "total_messages": len(messages),
        "messages": messages,
        "time_span": {
            "start": start_date if start_date else "beginning",
            "end": end_date if end_date else "now"
        }
    }

    return result


@mcp.tool()
async def get_channel_posts(channel_name: str, start_date: str = None, end_date: str = None, limit: int = 20):
    """Get posts from a Telegram channel within a specified timeframe
    
    Args:
        channel_name: The channel username or name (with or without @ symbol)
        start_date: Start date in format 'YYYY-MM-DD' (optional)
        end_date: End date in format 'YYYY-MM-DD' (optional)
        limit: Maximum number of posts to return (default 20)
    """
    if not client.is_connected():
        await client.connect()
    try:
        # Clean up channel name (remove @ if present)
        channel_username = channel_name.lstrip('@')
        
        # Try to get the channel entity
        try:
            channel = await client.get_entity(channel_username)
        except ValueError:
            # If username doesn't work, try searching in dialogs
            channel = None
            async for dialog in client.iter_dialogs():
                if dialog.is_channel and dialog.title.lower() == channel_name.lower():
                    channel = dialog.entity
                    break
        
        if not channel:
            return {
                "error": f"Could not find channel: {channel_name}"
            }
            
        # Convert date strings to datetime objects if provided
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC) if start_date else None
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC) if end_date else None
        except ValueError as e:
            return {"error": f"Invalid date format. Please use YYYY-MM-DD format. Error: {str(e)}"}
        
        # Get channel info
        channel_info = {
            'title': channel.title if hasattr(channel, 'title') else channel_name,
            'username': f"@{channel.username}" if hasattr(channel, 'username') and channel.username else None,
            'description': channel.about if hasattr(channel, 'about') else None,
            'link': f"https://t.me/{channel.username}" if hasattr(channel, 'username') and channel.username else None
        }
        
        # Get posts
        posts = []
        async for message in client.iter_messages(channel, limit=limit):
            # Skip messages outside the time range if specified
            if start_datetime and message.date < start_datetime:
                continue
            if end_datetime and message.date > end_datetime:
                continue
                
            # Extract message content
            content = {
                'text': message.message if message.message else None,
                'date': message.date.strftime("%Y-%m-%d %H:%M:%S"),
                'views': message.views if hasattr(message, 'views') else None,
                'forwards': message.forwards if hasattr(message, 'forwards') else None,
                'reply_count': message.replies.replies if hasattr(message, 'replies') and message.replies else None,
                'has_media': bool(message.media),
                'media_type': str(message.media.__class__.__name__) if message.media else None,
                'link': f"https://t.me/{channel.username}/{message.id}" if hasattr(channel, 'username') and channel.username else None
            }
            
            posts.append(content)
        
        result = {
            "channel": channel_info,
            "total_posts": len(posts),
            "posts": posts,
            "time_span": {
                "start": start_date if start_date else "beginning",
                "end": end_date if end_date else "now"
            }
        }
        
    except Exception as e:
        result = {
            "error": f"Error fetching channel posts: {str(e)}"
        }
    
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")