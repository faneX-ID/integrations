# Mattermost Integration

Integration with Mattermost team communication platform via REST API.

## Features

- Send messages to channels
- Create channels
- Get user information
- Full Mattermost REST API support

## Requirements

- `requests>=2.28.0` - HTTP library

## Configuration

### Connection Parameters

- **server_url**: Base URL of your Mattermost instance
- **api_token**: Mattermost personal access token or bot token

## Usage

### Send Message

```python
await service_registry.call("mattermost.send_message", {
    "channel_id": "channel123",
    "message": "Hello from faneX-ID!"
})
```

### Create Channel

```python
await service_registry.call("mattermost.create_channel", {
    "name": "it-support",
    "display_name": "IT Support",
    "type": "P"
})
```

## Notes

- Mattermost is an open-source team communication platform
- Requires personal access token or bot token
- Supports both open (O) and private (P) channels

