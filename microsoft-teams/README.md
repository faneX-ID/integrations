# Microsoft Teams Integration

Send notifications and alerts to Microsoft Teams channels via webhooks.

## Overview

The Microsoft Teams integration enables faneX-ID to send messages and adaptive cards directly to Teams channels. This is useful for:

- **Enterprise Notifications**: Notify Teams channels about system events
- **Employee Alerts**: Alert HR teams in Teams about onboarding events
- **Workflow Automation**: Send Teams messages when workflows complete
- **Corporate Communication**: Keep teams informed in their primary communication platform

## Features

- **Webhook Support**: Simple webhook-based messaging
- **Message Cards**: Rich formatted message cards
- **Adaptive Cards**: Support for Microsoft Adaptive Cards
- **Custom Theming**: Customizable theme colors
- **Channel Integration**: Send to any Teams channel

## Setup

### Prerequisites

- Microsoft Teams workspace
- Incoming webhook connector configured
- Network connectivity to Microsoft Teams API

### Configuration

Configure via Admin Panel under **Settings > Integrations > Microsoft Teams**.

#### Required Settings

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `webhook_url` | string | ✅ | Microsoft Teams incoming webhook URL |

#### Optional Settings

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `default_theme_color` | string | ❌ | Default theme color for messages (hex code, default: `0078D4`) |

### Creating a Teams Webhook

1. Open Microsoft Teams
2. Navigate to the channel where you want to receive messages
3. Click the **⋯** (three dots) next to the channel name
4. Select **Connectors**
5. Search for **Incoming Webhook** and click **Configure**
6. Give it a name and optionally upload an image
7. Click **Create**
8. Copy the webhook URL
9. Paste it into the `webhook_url` configuration field

## Exposed Services

### `microsoft_teams.send_message`

Send a message card to a Microsoft Teams channel.

**Parameters:**
- `title` (string, required): Message title
- `text` (string, required): Message text
- `theme_color` (string, optional): Theme color (hex code, e.g., `0078D4`)

**Example Workflow Action:**
```yaml
actions:
  - service: microsoft_teams.send_message
    data:
      title: "Employee Onboarded"
      text: "New employee {{ employee.first_name }} {{ employee.last_name }} has been added to the system"
      theme_color: "28a745"
```

### `microsoft_teams.send_card`

Send an adaptive card to Microsoft Teams.

**Parameters:**
- `title` (string, required): Card title
- `sections` (array, required): Array of adaptive card sections

**Example Workflow Action:**
```yaml
actions:
  - service: microsoft_teams.send_card
    data:
      title: "System Status"
      sections:
        - type: "TextBlock"
          text: "System is running normally"
          weight: "Bolder"
        - type: "FactSet"
          facts:
            - title: "Employees"
              value: "{{ employee_count }}"
            - title: "Users"
              value: "{{ user_count }}"
```

## Use Cases

### Employee Onboarding Notification
```yaml
trigger:
  type: event
  event: employee.created
actions:
  - service: microsoft_teams.send_message
    data:
      title: "New Employee Onboarded"
      text: "{{ employee.first_name }} {{ employee.last_name }} ({{ employee.personal_number }}) has been added"
      theme_color: "28a745"
```

### System Alert
```yaml
trigger:
  type: event
  event: system.error
actions:
  - service: microsoft_teams.send_message
    data:
      title: "System Error"
      text: "An error occurred: {{ error.message }}"
      theme_color: "dc3545"
```

## Security Notes

- **Webhook URLs are Secret**: Treat webhook URLs as sensitive credentials
- **Channel Permissions**: Ensure the webhook connector has permission to post to the target channel
- **Rate Limiting**: Teams has rate limits; avoid sending too many messages in quick succession
- **Data Privacy**: Ensure compliance with organizational data policies when sending employee information

## Troubleshooting

### Messages Not Appearing
- Verify the webhook URL is correct and active
- Check that the connector hasn't been removed from the channel
- Ensure the webhook URL hasn't expired (some organizations rotate webhooks)
- Check Teams activity log for errors

### Formatting Issues
- Verify JSON structure for adaptive cards is correct
- Check that theme colors are valid hex codes
- Ensure message text doesn't exceed Teams limits

### Authentication Errors
- Verify webhook URL is valid and not expired
- Check if webhook connector was removed or disabled
- Recreate webhook if necessary

## Changelog

### 1.0.0 (2025-12-13)
- Initial release
- Webhook-based messaging
- Message card support
- Adaptive card support
- Custom theme colors
