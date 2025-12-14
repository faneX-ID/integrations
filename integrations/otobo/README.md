# Otobo Integration

Integration with Otobo ticket system (Open Source). Create and manage tickets, users, and workflows.

## Features

- Create and manage tickets
- Add articles to tickets
- Update ticket information
- Full Otobo REST API support

## Requirements

- `requests>=2.28.0` - HTTP library

## Configuration

### Connection Parameters

- **server_url**: Base URL of your Otobo instance
- **username**: Otobo API username
- **password**: Otobo API password
- **default_queue**: Default queue for ticket creation (optional)

## Usage

### Create Ticket

```python
await service_registry.call("otobo.create_ticket", {
    "title": "New Employee Onboarding",
    "queue": "IT Support",
    "priority": "3 normal",
    "customer_user": "user@example.com",
    "article": {
        "Subject": "New Employee Onboarding",
        "Body": "Please create accounts for new employee..."
    }
})
```

### Get Ticket

```python
await service_registry.call("otobo.get_ticket", {
    "ticket_id": 12345
})
```

### Add Article

```python
await service_registry.call("otobo.add_article", {
    "ticket_id": 12345,
    "subject": "Update",
    "body": "Accounts have been created."
})
```

## Notes

- Otobo is an open-source ticket system based on OTRS
- Requires Otobo REST API to be enabled
- API authentication uses HTTP Basic Auth


