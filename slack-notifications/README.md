# Slack Notifications Integration

Send notifications and alerts to Slack channels via webhooks or API.

## Overview

The Slack Notifications integration enables faneX-ID to send messages and alerts directly to Slack channels. This is useful for:

- **System Alerts**: Notify teams about critical system events
- **Employee Notifications**: Alert HR teams about new employee onboarding
- **Workflow Automation**: Send notifications when workflows complete
- **Team Communication**: Keep teams informed about important events

## Features

- **Webhook Support**: Simple webhook-based messaging
- **API Integration**: Full Slack API support (optional)
- **Rich Formatting**: Support for attachments and formatted messages
- **Custom Channels**: Send to any Slack channel
- **Alert Types**: Color-coded alerts (good, warning, danger)

## Setup

### Prerequisites

- Slack workspace with admin access
- Incoming webhook URL (or Bot Token for advanced features)
- Network connectivity to Slack API

### Configuration

Configure via Admin Panel under **Settings > Integrations > Slack Notifications**.

#### Required Settings

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `webhook_url` | string | ✅ | Slack incoming webhook URL |
| `default_channel` | string | ❌ | Default channel for notifications |

#### Optional Settings

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `api_token` | string | ❌ | Slack Bot Token (for advanced features) |

### Creating a Slack Webhook

1. Go to your Slack workspace
2. Navigate to **Apps** > **Incoming Webhooks**
3. Click **Add to Slack**
4. Select the channel where messages should be sent
5. Copy the webhook URL
6. Paste it into the `webhook_url` configuration field

## Exposed Services

### `slack_notifications.send_message`

Send a simple message to a Slack channel.

**Parameters:**
- `channel` (string, optional): Slack channel name or ID (default: configured default_channel)
- `message` (string, required): Message text to send
- `username` (string, optional): Custom username for the bot
- `icon_emoji` (string, optional): Emoji icon for the message

**Example Workflow Action:**
```yaml
actions:
  - service: slack_notifications.send_message
    data:
      channel: "#hr-team"
      message: "New employee {{ employee.first_name }} {{ employee.last_name }} has been onboarded"
      username: "faneX-ID Bot"
      icon_emoji: ":tada:"
```

### `slack_notifications.send_alert`

Send a formatted alert with color coding to Slack.

**Parameters:**
- `channel` (string, optional): Slack channel name or ID
- `title` (string, required): Alert title
- `message` (string, required): Alert message text
- `color` (string, optional): Alert color - `good` (green), `warning` (yellow), or `danger` (red). Default: `warning`

**Example Workflow Action:**
```yaml
actions:
  - service: slack_notifications.send_alert
    data:
      channel: "#alerts"
      title: "System Error"
      message: "An error occurred in the employee sync process: {{ error.message }}"
      color: "danger"
```

## Use Cases

### Employee Onboarding Notification
```yaml
trigger:
  type: event
  event: employee.created
actions:
  - service: slack_notifications.send_message
    data:
      channel: "#hr-team"
      message: "🎉 New employee {{ employee.first_name }} {{ employee.last_name }} ({{ employee.personal_number }}) has been added to the system"
```

### System Error Alert
```yaml
trigger:
  type: event
  event: system.error
actions:
  - service: slack_notifications.send_alert
    data:
      channel: "#devops"
      title: "Critical System Error"
      message: "Error: {{ error.message }}\nTime: {{ timestamp }}"
      color: "danger"
```

## Security Notes

- **Webhook URLs are Secret**: Treat webhook URLs as sensitive credentials
- **Channel Permissions**: Ensure the webhook has permission to post to the target channel
- **Rate Limiting**: Slack has rate limits; avoid sending too many messages in quick succession
- **Token Security**: If using API tokens, store them securely and rotate regularly

## Troubleshooting

### Messages Not Appearing
- Verify the webhook URL is correct and active
- Check that the webhook hasn't been revoked in Slack
- Ensure the channel name is correct (include `#` for public channels)
- Check Slack workspace logs for errors

### Authentication Errors
- Verify webhook URL is valid
- If using API token, ensure it has required scopes
- Check token expiration

### Rate Limiting
- Slack limits webhook messages; implement delays if sending many messages
- Consider batching notifications
- Use Slack's API for high-volume scenarios

## Changelog

### 1.0.0 (2025-12-13)
- Initial release
- Webhook-based messaging
- Alert formatting with colors
- Custom channel support

