# Microsoft Graph Exchange Integration

Microsoft Graph integration for Exchange Online email and calendar management.

## Features

- Send emails via Exchange Online
- Get email messages from mailboxes
- Create calendar events
- Manage Exchange Online mailboxes

## Requirements

- `microsoft_graph` base integration (system integration)
- `requests>=2.28.0`

## Configuration

This integration depends on the `microsoft_graph` base integration for authentication. Configure the base integration first.

### Optional Configuration

- **default_from**: Default sender email address

## Usage

### Send Email

```python
await service_registry.call("microsoft_graph_exchange.send_email", {
    "to": ["recipient@example.com"],
    "subject": "Test Email",
    "body": "<p>This is a test email</p>",
    "cc": ["cc@example.com"]
})
```

### Get Messages

```python
await service_registry.call("microsoft_graph_exchange.get_messages", {
    "folder": "inbox",
    "limit": 20
})
```

### Create Calendar Event

```python
await service_registry.call("microsoft_graph_exchange.create_calendar_event", {
    "subject": "Team Meeting",
    "start": "2025-01-15T10:00:00Z",
    "end": "2025-01-15T11:00:00Z",
    "attendees": ["attendee@example.com"]
})
```

## Notes

- Requires Microsoft Graph base integration to be installed and configured
- Uses Microsoft Graph API v1.0
- For on-premises Exchange, use the `exchange_onprem` system integration instead

