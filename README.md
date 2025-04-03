# Telegram MCP Server

A powerful Telegram integration server that provides various tools for managing contacts, sending messages, and retrieving channel information through MCP (Multi-Client Protocol).

## Features

- **Contact Management**

  - Get list of contacts
  - Search contacts
  - Get last interactions

- **Messaging**

  - Send messages to contacts by name or phone number
  - Get chat history with date range filtering
  - View last interactions

- **Channel Features**
  - Get posts from channels
  - Search channels
  - View channel information
  - Filter posts by date range

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher (for npx installation)
- Telegram API credentials (api_id and api_hash)
- A Telegram account

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/telegram-MCP-server.git
cd telegram-MCP-server
```

2. Install required dependencies:

```bash
uv venv .venv  # Create a virtual environment
source .venv/bin/activate  # Activate it (Linux/macOS)
.\venv\Scripts\activate  # Activate it (Windows)
uv pip install

```

3. Create a `.env` file in the project root with your Telegram credentials:

```env
TG_API_ID=your_api_id
TG_API_HASH=your_api_hash
phone=your_phone_number  # Format: +1234567890
```

## Integration with Cursor/Claude Desktop

Copy the below json with the appropriate {{PATH}} values:

```json
{
  "mcpServers": {
    "whatsapp": {
      "command": "{{PATH_TO_UV}}", // Run `which uv` and place the output here
      "args": [
        "--directory",
        "{{PATH_TO_SRC}}/whatsapp-mcp/whatsapp-mcp-server", // cd into the repo, run `pwd` and enter the output here + "/whatsapp-mcp-server"
        "run",
        "main.py"
      ]
    }
  }
}
```

For **Claude**, save this as `claude_desktop_config.json` in your Claude Desktop configuration directory at:

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

For **Cursor**, save this as `mcp.json` in your Cursor configuration directory at:

```
~/.cursor/mcp.json
```

## Tool Documentation

### get_contacts()

Returns a list of all your Telegram contacts with their names, phone numbers, and usernames.

### send_message_by_identifier(identifier: str, message: str)

Sends a message to a contact identified by either their name or phone number.

- `identifier`: Contact's name or phone number
- `message`: Text message to send

### get_last_interaction(identifier: str)

Returns the most recent message exchanged with a specific contact.

- `identifier`: Contact's name or phone number

### get_chat_history(identifier: str, start_date: str = None, end_date: str = None, limit: int = 20)

Retrieves chat history with a contact within a specified timeframe.

- `identifier`: Contact's name or phone number
- `start_date`: Optional start date (YYYY-MM-DD)
- `end_date`: Optional end date (YYYY-MM-DD)
- `limit`: Maximum number of messages to return

### get_channel_posts(channel_name: str, start_date: str = None, end_date: str = None, limit: int = 20)

Gets posts from a Telegram channel.

- `channel_name`: Channel username or name
- `start_date`: Optional start date (YYYY-MM-DD)
- `end_date`: Optional end date (YYYY-MM-DD)
- `limit`: Maximum number of posts to return

## Error Handling

The server includes comprehensive error handling for:

- Invalid credentials
- Network issues
- Rate limiting
- Invalid parameters
- Permission errors

## Security Considerations

- Store API credentials securely
- Never share your `.env` file
- Use environment variables in production
- Implement rate limiting for production use
- Monitor usage and implement logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Telethon library for Telegram API integration
- FastMCP for the server framework
