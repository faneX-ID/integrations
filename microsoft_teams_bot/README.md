# Microsoft Teams Bot Integration

Integration for Microsoft Teams bots. Send messages and interact with Teams channels.

## Overview

This integration provides Microsoft Teams bot functionality for faneX-ID, allowing you to:
- Send messages to Teams channels and chats
- Integrate with the Bot Interpreter system component

## Setup

### Prerequisites

- Azure AD application registration
- Microsoft App ID and App Password

### Configuration

```json
{
  "app_id": "YOUR_APP_ID",
  "app_password": "YOUR_APP_PASSWORD",
  "tenant_id": "YOUR_TENANT_ID" // Optional
}
```

**Configuration Options:**

- `app_id` (required): Microsoft Application (client) ID from Azure AD
- `app_password` (required): Application password from Azure AD
- `tenant_id` (optional): Azure AD tenant ID (uses common if not provided)

## Services

### Send Message

Send a message to a Teams channel or chat:

```json
{
  "channel_id": "19:channel-id@thread.tacv2",
  "message": "Hello from faneX-ID!",
  "message_type": "text"
}
```

### Get Bot Status

Get the status of the Teams bot:

```json
{
  "bot_id": "optional_bot_id"
}
```

### Register with Bot Interpreter

Register this bot with the Bot Interpreter system component:

```json
{
  "bot_id": "my_teams_bot"
}
```

## Usage

1. Register your bot in Azure AD
2. Get your App ID and App Password
3. Configure the integration
4. Optionally register with the Bot Interpreter for unified bot management

## Integration with Bot Interpreter

This integration automatically registers with the Bot Interpreter system component on setup.

