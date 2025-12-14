# Calendar Sync Integration

Sync employee events, onboarding dates, and important dates with Google Calendar or Microsoft Outlook.

## Overview

The Calendar Sync integration enables faneX-ID to create and manage calendar events in Google Calendar or Microsoft Outlook. This is useful for:

- **Employee Onboarding**: Create calendar events for new employee start dates
- **Anniversary Tracking**: Set reminders for employee anniversaries
- **Meeting Scheduling**: Automatically schedule meetings for onboarding processes
- **Event Management**: Sync important dates from employee data to calendars

## Features

- **Multi-Provider Support**: Works with Google Calendar and Microsoft Outlook
- **Event Creation**: Create calendar events with details
- **Event Listing**: List upcoming events
- **Attendee Management**: Add attendees to events
- **Location Support**: Include location information in events
- **Timezone Support**: Configure timezone for events

## Setup

### Prerequisites

- Google Calendar API access or Microsoft Graph API access
- OAuth access token or API key
- Network connectivity to calendar service APIs

### Configuration

Configure via Admin Panel under **Settings > Integrations > Calendar Sync**.

#### Required Settings

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `provider` | string | ✅ | Calendar provider - `google` or `outlook` |
| `api_key` | string | ✅ | OAuth access token or API key |

#### Optional Settings

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `calendar_id` | string | ❌ | Calendar ID (for Google) or calendar name (default: `primary`) |
| `timezone` | string | ❌ | Timezone for events (e.g., `Europe/Berlin`, default: `UTC`) |

### Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Calendar API**
4. Create credentials (OAuth 2.0 Client ID or Service Account)
5. Generate access token using OAuth flow
6. Copy the access token to `api_key` configuration

**Note**: For production use, implement OAuth 2.0 flow for token refresh.

### Microsoft Outlook Setup

1. Go to [Azure Portal](https://portal.azure.com/)
2. Register an application in Azure Active Directory
3. Grant **Calendars.ReadWrite** permission
4. Generate access token using OAuth 2.0 flow
5. Copy the access token to `api_key` configuration

**Note**: For production use, implement OAuth 2.0 flow for token refresh.

## Exposed Services

### `calendar_sync.create_event`

Create a calendar event.

**Parameters:**
- `title` (string, required): Event title
- `description` (string, optional): Event description
- `start_time` (string, required): Event start time (ISO 8601 format, e.g., `2025-12-13T10:00:00Z`)
- `end_time` (string, required): Event end time (ISO 8601 format)
- `attendees` (array, optional): Array of attendee email addresses
- `location` (string, optional): Event location

**Returns:**
- `status`: "created"
- `event_id`: Calendar event ID

**Example Workflow Action:**
```yaml
actions:
  - service: calendar_sync.create_event
    data:
      title: "Onboarding: {{ employee.first_name }} {{ employee.last_name }}"
      description: |
        New employee onboarding session

        Employee Details:
        - Personal Number: {{ employee.personal_number }}
        - Department: {{ employee.department }}
        - Position: {{ employee.position }}
      start_time: "{{ employee.entry_date }}T09:00:00Z"
      end_time: "{{ employee.entry_date }}T17:00:00Z"
      attendees:
        - "{{ employee.email }}"
        - "hr@example.com"
        - "{{ employee.manager }}@example.com"
      location: "Conference Room A"
```

### `calendar_sync.list_events`

List upcoming calendar events.

**Parameters:**
- `start_date` (string, optional): Start date for filtering (ISO 8601 date format)
- `end_date` (string, optional): End date for filtering (ISO 8601 date format)

**Returns:**
- `events`: Array of event objects
- `count`: Number of events found

**Example Workflow Action:**
```yaml
actions:
  - service: calendar_sync.list_events
    data:
      start_date: "2025-12-01"
      end_date: "2025-12-31"
```

## Use Cases

### Employee Onboarding Calendar Event
```yaml
trigger:
  type: event
  event: employee.created
actions:
  - service: calendar_sync.create_event
    data:
      title: "Onboarding: {{ employee.first_name }} {{ employee.last_name }}"
      description: "First day onboarding for new employee"
      start_time: "{{ employee.entry_date }}T09:00:00Z"
      end_time: "{{ employee.entry_date }}T17:00:00Z"
      attendees:
        - "{{ employee.email }}"
        - "hr@example.com"
      location: "Main Office"
```

### Employee Anniversary Reminder
```yaml
trigger:
  type: schedule
  cron: "0 9 * * *"
conditions:
  - field: "employee.anniversary_date"
    operator: "equals"
    value: "{{ today }}"
actions:
  - service: calendar_sync.create_event
    data:
      title: "{{ employee.first_name }} {{ employee.last_name }} - {{ years }} Year Anniversary"
      description: "Celebrate {{ employee.first_name }}'s work anniversary!"
      start_time: "{{ today }}T12:00:00Z"
      end_time: "{{ today }}T13:00:00Z"
      attendees:
        - "hr@example.com"
        - "{{ employee.manager }}@example.com"
```

### Department Meeting
```yaml
trigger:
  type: schedule
  cron: "0 9 * * 1"
actions:
  - service: calendar_sync.create_event
    data:
      title: "Weekly {{ department }} Meeting"
      description: "Weekly team sync meeting"
      start_time: "{{ next_monday }}T10:00:00Z"
      end_time: "{{ next_monday }}T11:00:00Z"
      location: "Conference Room B"
```

## Security Notes

- **Access Tokens**: Store OAuth tokens securely; implement token refresh for production
- **API Keys**: Treat API keys as sensitive credentials
- **Calendar Permissions**: Ensure the service account or user has appropriate calendar permissions
- **Data Privacy**: Ensure compliance with data protection regulations when syncing employee information
- **Token Expiration**: Implement token refresh mechanism for long-running integrations

## Troubleshooting

### Authentication Errors
- Verify API key/access token is valid and not expired
- For Google Calendar, ensure OAuth token has `calendar` scope
- For Outlook, ensure token has `Calendars.ReadWrite` permission
- Check if token needs to be refreshed

### Event Creation Failed
- Verify date/time format is correct (ISO 8601)
- Check that start_time is before end_time
- Ensure calendar_id exists and is accessible
- Verify timezone is valid

### Calendar Not Found
- For Google Calendar, verify calendar_id is correct (use `primary` for default calendar)
- Check that the calendar is accessible with current credentials
- Verify calendar sharing settings

### Timezone Issues
- Ensure timezone is set correctly in configuration
- Use UTC for consistency across timezones
- Verify ISO 8601 date format includes timezone information

## Changelog

### 1.0.0 (2025-12-13)
- Initial release
- Google Calendar support
- Microsoft Outlook support
- Event creation and listing
- Attendee and location support


