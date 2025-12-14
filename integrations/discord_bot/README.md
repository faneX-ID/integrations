# Discord Bot Integration

Integration for Discord bots. Send messages and interact with Discord servers and channels.

## Overview

This integration provides Discord bot functionality for faneX-ID, allowing you to:
- Send messages to Discord channels and DMs
- Integrate with the Bot Interpreter system component

## Setup

### Prerequisites

- A Discord application with bot token
- Bot token from Discord Developer Portal

### Configuration

```json
{
  "bot_token": "YOUR_BOT_TOKEN",
  "intents": {
    "guilds": true,
    "messages": true,
    "message_content": false
  }
}
```

**Configuration Options:**

- `bot_token` (required): Discord bot token from Discord Developer Portal
- `intents` (optional): Discord bot intents configuration
  - `guilds` (default: true): Enable guild (server) intents
  - `messages` (default: true): Enable message intents
  - `message_content` (default: false): Enable message content intents (requires privileged gateway intent)

## Services

### Send Message

Send a message to a Discord channel or DM:

```json
{
  "channel_id": "123456789012345678",
  "message": "Hello from faneX-ID!",
  "embed": {
    "title": "Embed Title",
    "description": "Embed Description",
    "color": 3447003
  },
  "reply_to_message_id": "987654321098765432"
}
```

### Get Bot Status

Get the status of the Discord bot:

```json
{
  "bot_id": "optional_bot_id"
}
```

### Register with Bot Interpreter

Register this bot with the Bot Interpreter system component:

```json
{
  "bot_id": "my_discord_bot"
}
```

## Usage

1. Create a Discord application in Discord Developer Portal
2. Create a bot and get your bot token
3. Configure the integration with your bot token
4. Optionally configure intents (message_content requires privileged gateway intent)
5. Optionally register with the Bot Interpreter for unified bot management

## Integration with Bot Interpreter

This integration automatically registers with the Bot Interpreter system component on setup.

## Intents

Discord requires specific intents to be enabled for certain features:
- **Guilds**: Required for basic server functionality
- **Messages**: Required to receive message events
- **Message Content**: Required to read message content (requires privileged gateway intent in Discord Developer Portal)

Make sure to enable the required intents in the Discord Developer Portal under "Bot" > "Privileged Gateway Intents".

