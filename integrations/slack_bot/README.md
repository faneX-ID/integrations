# Slack Bot Integration

Integration for Slack bots. Send messages and interact with Slack workspaces.

## Overview

This integration provides Slack bot functionality for faneX-ID, allowing you to:
- Send messages to Slack channels and DMs
- Integrate with the Bot Interpreter system component

## Setup

### Prerequisites

- A Slack app with bot token
- Bot token (xoxb-...) from Slack API

### Configuration

```json
{
  "bot_token": "xoxb-your-bot-token",
  "app_token": "xapp-your-app-token" // Optional, for Socket Mode
}
```

**Configuration Options:**

- `bot_token` (required): Slack bot token (xoxb-...)
- `app_token` (optional): Slack app-level token (xapp-...) for Socket Mode

## Services

### Send Message

Send a message to a Slack channel or DM:

```json
{
  "channel": "#general",
  "message": "Hello from faneX-ID!",
  "thread_ts": "1234567890.123456",
  "blocks": []
}
```

### Get Bot Status

Get the status of the Slack bot:

```json
{
  "bot_id": "optional_bot_id"
}
```

### Register with Bot Interpreter

Register this bot with the Bot Interpreter system component:

```json
{
  "bot_id": "my_slack_bot"
}
```

## Usage

1. Create a Slack app in your workspace
2. Get your bot token
3. Configure the integration with your bot token
4. Optionally register with the Bot Interpreter for unified bot management

## Integration with Bot Interpreter

This integration automatically registers with the Bot Interpreter system component on setup.

