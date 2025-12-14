# Telegram Bot Integration

Integration for Telegram bots. Send and receive messages through Telegram.

## Overview

This integration provides Telegram bot functionality for faneX-ID, allowing you to:
- Send messages through Telegram bots
- Receive and process incoming messages
- Integrate with the Bot Interpreter system component

## Setup

### Prerequisites

- A Telegram bot token from [@BotFather](https://t.me/botfather)

### Configuration

```json
{
  "bot_token": "YOUR_BOT_TOKEN",
  "webhook_url": "https://your-domain.com/webhook/telegram" // Optional
}
```

**Configuration Options:**

- `bot_token` (required): Telegram bot token from @BotFather
- `webhook_url` (optional): Webhook URL for receiving messages (if not provided, polling is used)

## Services

### Send Message

Send a message through Telegram:

```json
{
  "chat_id": "123456789",
  "message": "Hello from faneX-ID!",
  "parse_mode": "Markdown",
  "reply_to_message_id": 123
}
```

### Get Bot Status

Get the status of the Telegram bot:

```json
{
  "bot_id": "optional_bot_id"
}
```

### Register with Bot Interpreter

Register this bot with the Bot Interpreter system component:

```json
{
  "bot_id": "my_telegram_bot"
}
```

## Usage

1. Create a bot with @BotFather on Telegram
2. Get your bot token
3. Configure the integration with your bot token
4. Optionally register with the Bot Interpreter for unified bot management

## Integration with Bot Interpreter

This integration automatically registers with the Bot Interpreter system component on setup, allowing you to manage it through the unified bot interface.

