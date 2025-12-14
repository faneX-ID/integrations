# SMTP Email Service Integration

Standard SMTP Email integration for sending notifications.

## Overview

The SMTP Email Service integration provides email sending capabilities via any SMTP server. This is useful for:

- **Custom Mail Servers**: Use your organization's internal mail server
- **Gmail Integration**: Send emails via Gmail SMTP
- **Outlook/Office 365**: Use Microsoft SMTP services
- **Generic Email**: Works with any SMTP-compatible email service

## Features

- **Universal SMTP Support**: Works with any SMTP server
- **TLS/SSL Encryption**: Supports encrypted connections
- **Simple Configuration**: Easy setup with standard SMTP settings
- **Workflow Integration**: Use in workflows for automated emails

## Setup

### Prerequisites

- SMTP server access
- SMTP server credentials (if authentication required)
- Network connectivity to SMTP server

### Configuration

Configure via Admin Panel under **Settings > Integrations > SMTP Email Service**.

#### Required Settings

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `host` | string | ✅ | SMTP server hostname |
| `port` | integer | ✅ | SMTP port (587 for TLS, 465 for SSL, 25 for unencrypted) |
| `username` | string | ✅ | SMTP username (usually email address) |
| `password` | string | ✅ | SMTP password or app-specific password |

#### Optional Settings

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `use_tls` | boolean | ❌ | Enable TLS encryption (default: `true`) |

### Common SMTP Configurations

#### Gmail (via App Password)
- Host: `smtp.gmail.com`
- Port: `587` (TLS) or `465` (SSL)
- Username: Your Gmail address
- Password: App-specific password (not your regular password)
- Use TLS: `true`

**Note**: Enable "Less secure app access" or use App Password in Google Account settings.

#### Outlook / Office 365
- Host: `smtp.office365.com`
- Port: `587` (TLS)
- Username: Your Outlook email address
- Password: Your Outlook password
- Use TLS: `true`

#### Custom Mail Server
- Host: Your mail server hostname
- Port: Usually `587` (TLS) or `25` (unencrypted)
- Username/Password: As provided by your mail server administrator
- Use TLS: `true` (recommended)

## Exposed Services

### `smtp.send_email`

Send an email via SMTP.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject
- `body` (string, required): Email body text

**Example Workflow Action:**
```yaml
actions:
  - service: smtp.send_email
    data:
      to: "user@example.com"
      subject: "Welcome to faneX-ID"
      body: "Hello {{ user.name }}, welcome to the platform!"
```

## Use Cases

### Welcome Email
```yaml
trigger:
  type: event
  event: user.created
actions:
  - service: smtp.send_email
    data:
      to: "{{ user.email }}"
      subject: "Welcome to faneX-ID"
      body: "Hello {{ user.username }}, your account has been created successfully."
```

### Employee Onboarding Notification
```yaml
trigger:
  type: event
  event: employee.created
actions:
  - service: smtp.send_email
    data:
      to: "hr@example.com"
      subject: "New Employee: {{ employee.first_name }} {{ employee.last_name }}"
      body: "A new employee has been added to the system:\n\nName: {{ employee.first_name }} {{ employee.last_name }}\nPersonal Number: {{ employee.personal_number }}\nDepartment: {{ employee.department }}"
```

## Security Notes

- **Use TLS/SSL**: Always use encrypted connections (port 587 with TLS or 465 with SSL)
- **Secure Credentials**: Store SMTP passwords securely in settings
- **App Passwords**: For Gmail, use app-specific passwords instead of your main password
- **Firewall**: Ensure SMTP ports are accessible from your server

## Troubleshooting

### Connection Failed
- Verify host and port are correct
- Check firewall rules allow SMTP connections
- Ensure network connectivity to SMTP server
- Try different ports (587, 465, 25)

### Authentication Failed
- Verify username and password are correct
- For Gmail, ensure you're using an App Password
- Check if server requires authentication
- Verify account is not locked or suspended

### TLS/SSL Errors
- Ensure TLS is enabled if using port 587
- Try SSL (port 465) if TLS fails
- Check server certificate validity
- Verify server supports the encryption method

## Changelog

### 1.0.0 (2025-12-13)
- Initial release
- Generic SMTP support
- TLS/SSL encryption
- Basic email sending

