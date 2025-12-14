# Exchange On-Premises Integration

Integration with Exchange On-Premises via EWS (Exchange Web Services) API.

## Features

- Send emails
- Access mailbox information
- Create and manage calendar events
- Get calendar events for date ranges

## Requirements

- Exchange Management Shell (for OnPrem) or ExchangeOnlineManagement module
- For Exchange OnPrem: Exchange Management Tools installed
- For Exchange Online: `Install-Module ExchangeOnlineManagement`

## Configuration

### Connection Parameters

- **server_url**: Exchange Web Services URL (e.g., https://mail.example.com/EWS/Exchange.asmx)
- **username**: Exchange username (domain\\username or email)
- **password**: Exchange password
- **default_from**: Default sender email address (optional)

## Usage

### Send Email

```python
await service_registry.call("exchange_onprem.send_email", {
    "to": ["recipient@example.com"],
    "subject": "Test Email",
    "body": "This is a test email",
    "cc": ["cc@example.com"]
})
```

### Create Calendar Event

```python
await service_registry.call("exchange_onprem.create_calendar_event", {
    "subject": "Team Meeting",
    "start": "2025-01-15T10:00:00Z",
    "end": "2025-01-15T11:00:00Z",
    "attendees": ["attendee1@example.com", "attendee2@example.com"]
})
```

### Get Calendar Events

```python
await service_registry.call("exchange_onprem.get_calendar_events", {
    "start_date": "2025-01-15",
    "end_date": "2025-01-20"
})
```

## Notes

- For Exchange OnPrem: Requires Exchange Management Shell on Exchange server or management workstation
- For Exchange Online: Uses ExchangeOnlineManagement PowerShell module
- Full calendar management requires Exchange Web Services (EWS) API
- For advanced calendar features, consider using Microsoft Graph Exchange integration
