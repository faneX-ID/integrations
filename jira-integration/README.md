# Jira Integration

Create and manage Jira tickets for employee onboarding, IT requests, and workflow automation.

## Overview

The Jira Integration enables faneX-ID to automatically create and manage Jira tickets. This is useful for:

- **Employee Onboarding**: Automatically create IT tickets for new employee setup
- **Access Requests**: Create tickets for access provisioning
- **Workflow Automation**: Trigger ticket creation based on system events
- **Issue Tracking**: Track employee-related issues and requests

## Features

- **Ticket Creation**: Automatically create Jira tickets
- **Ticket Updates**: Update existing tickets with new information
- **Ticket Retrieval**: Get ticket information and status
- **Label Support**: Add labels to tickets for categorization
- **Assignee Management**: Assign tickets to specific users

## Setup

### Prerequisites

- Jira Cloud or Jira Server instance
- Jira account with API access
- API token (for Jira Cloud) or username/password (for Jira Server)
- Network connectivity to Jira instance

### Configuration

Configure via Admin Panel under **Settings > Integrations > Jira Integration**.

#### Required Settings

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `server_url` | string | ✅ | Base URL of your Jira instance (e.g., `https://yourcompany.atlassian.net`) |
| `username` | string | ✅ | Jira username or email address |
| `api_token` | string | ✅ | Jira API token (Cloud) or password (Server) |

#### Optional Settings

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `default_project` | string | ❌ | Default project key for ticket creation |

### Creating a Jira API Token (Cloud)

1. Log in to your Jira instance
2. Go to **Account Settings** > **Security**
3. Click **Create API Token**
4. Give it a label (e.g., "faneX-ID Integration")
5. Copy the generated token
6. Paste it into the `api_token` configuration field

### Jira Server Authentication

For Jira Server, use your username and password directly. The integration will use HTTP Basic Authentication.

## Exposed Services

### `jira_integration.create_ticket`

Create a new Jira ticket.

**Parameters:**
- `project_key` (string, required): Jira project key (e.g., `IT`, `HR`)
- `issue_type` (string, required): Issue type - `Task`, `Story`, `Bug`, `Epic`, etc.
- `summary` (string, required): Ticket summary/title
- `description` (string, required): Ticket description
- `assignee` (string, optional): Assignee username or email
- `labels` (array, optional): Array of label strings

**Returns:**
- `status`: "created"
- `ticket_key`: Jira ticket key (e.g., `IT-123`)
- `url`: Full URL to the ticket

**Example Workflow Action:**
```yaml
actions:
  - service: jira_integration.create_ticket
    data:
      project_key: "IT"
      issue_type: "Task"
      summary: "Onboard new employee: {{ employee.first_name }} {{ employee.last_name }}"
      description: |
        New employee requires:
        - User account creation
        - Email setup
        - Access to HR systems
        - Hardware provisioning

        Employee Details:
        - Personal Number: {{ employee.personal_number }}
        - Department: {{ employee.department }}
        - Start Date: {{ employee.entry_date }}
      assignee: "it-team@example.com"
      labels:
        - "onboarding"
        - "employee"
    id: ticket_created
    then:
      - service: slack_notifications.send_message
        data:
          message: "Created Jira ticket {{ ticket_created.result.ticket_key }} for {{ employee.first_name }}"
```

### `jira_integration.get_ticket`

Get ticket information.

**Parameters:**
- `ticket_key` (string, required): Jira ticket key (e.g., `IT-123`)

**Returns:**
- `key`: Ticket key
- `summary`: Ticket summary
- `status`: Current status
- `assignee`: Assignee display name (if assigned)

**Example Workflow Action:**
```yaml
actions:
  - service: jira_integration.get_ticket
    data:
      ticket_key: "IT-123"
```

### `jira_integration.update_ticket`

Update an existing ticket.

**Parameters:**
- `ticket_key` (string, required): Jira ticket key
- `fields` (object, required): Fields to update (e.g., `{"summary": "New title", "description": "New description"}`)

**Example Workflow Action:**
```yaml
actions:
  - service: jira_integration.update_ticket
    data:
      ticket_key: "IT-123"
      fields:
        description: "Updated description with new information"
        labels: ["onboarding", "completed"]
```

## Use Cases

### Automatic Onboarding Ticket
```yaml
trigger:
  type: event
  event: employee.created
actions:
  - service: jira_integration.create_ticket
    data:
      project_key: "IT"
      issue_type: "Task"
      summary: "Onboard {{ employee.first_name }} {{ employee.last_name }}"
      description: "New employee onboarding request for {{ employee.personal_number }}"
      labels: ["onboarding", "urgent"]
```

### Update Ticket on Employee Sync
```yaml
trigger:
  type: event
  event: employee.updated
conditions:
  - field: "action_type"
    operator: "equals"
    value: "department_change"
actions:
  - service: jira_integration.create_ticket
    data:
      project_key: "HR"
      issue_type: "Task"
      summary: "Department change for {{ employee.first_name }} {{ employee.last_name }}"
      description: "Employee moved from {{ old_department }} to {{ employee.department }}"
```

## Security Notes

- **API Tokens are Secret**: Store API tokens securely
- **Permissions**: Ensure the Jira user has permissions to create tickets in target projects
- **Rate Limiting**: Jira has rate limits; avoid creating too many tickets in quick succession
- **Data Privacy**: Ensure compliance with data protection regulations when including employee information

## Troubleshooting

### Authentication Failed
- Verify username and API token are correct
- For Jira Cloud, ensure you're using an API token, not your password
- For Jira Server, verify username/password are correct
- Check if account is locked or requires 2FA

### Ticket Creation Failed
- Verify project key exists and is accessible
- Check that issue type is valid for the project
- Ensure user has permission to create tickets in the project
- Verify required fields are provided

### Connection Errors
- Verify server URL is correct and accessible
- Check network connectivity to Jira instance
- Ensure firewall allows connections to Jira
- For Jira Server, verify SSL certificate is valid

## Changelog

### 1.0.0 (2025-12-13)
- Initial release
- Ticket creation
- Ticket retrieval
- Ticket updates
- Label and assignee support

