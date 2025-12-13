# Generic Webhook Integration

Send HTTP requests to any webhook endpoint for custom integrations and automations.

## Overview

The Generic Webhook integration provides a flexible way to send HTTP requests to any external service or API. This is useful for:

- **Custom Integrations**: Connect to services not directly supported
- **API Calls**: Make REST API calls to external systems
- **Webhook Forwarding**: Forward events to external webhook endpoints
- **Third-Party Services**: Integrate with custom or proprietary systems

## Features

- **Multiple HTTP Methods**: Support for GET, POST, PUT, PATCH, DELETE
- **Custom Headers**: Add custom HTTP headers to requests
- **JSON Payloads**: Send structured JSON data
- **Default Configuration**: Set default URL and headers
- **Flexible Usage**: Use in workflows or as standalone service calls

## Setup

### Prerequisites

- Target webhook endpoint or API URL
- Network connectivity to the target endpoint
- Authentication credentials (if required by target service)

### Configuration

Configure via Admin Panel under **Settings > Integrations > Generic Webhook**.

#### Optional Settings

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `default_url` | string | ❌ | Default webhook URL (can be overridden per request) |
| `default_headers` | object | ❌ | Default HTTP headers to include in all requests |
| `timeout` | integer | ❌ | Request timeout in seconds (default: 30) |

### Example Configuration

```json
{
  "default_url": "https://api.example.com/webhook",
  "default_headers": {
    "Authorization": "Bearer YOUR_TOKEN",
    "X-Custom-Header": "value"
  },
  "timeout": 30
}
```

## Exposed Services

### `webhook_generic.send_webhook`

Send a webhook request to any endpoint.

**Parameters:**
- `url` (string, optional): Webhook URL (uses `default_url` if not provided)
- `method` (string, optional): HTTP method - `GET`, `POST`, `PUT`, `PATCH`, `DELETE` (default: `POST`)
- `payload` (object, optional): Request payload (JSON object)
- `headers` (object, optional): Custom HTTP headers (merged with default headers)

**Returns:**
- `status`: "sent"
- `status_code`: HTTP status code
- `response`: Response body (truncated to 500 characters)

**Example Workflow Action:**
```yaml
actions:
  - service: webhook_generic.send_webhook
    data:
      url: "https://api.example.com/events"
      method: "POST"
      payload:
        event: "employee.created"
        employee_id: "{{ employee.id }}"
        employee_name: "{{ employee.first_name }} {{ employee.last_name }}"
      headers:
        "X-Event-Type": "employee-onboarding"
```

### GET Request Example
```yaml
actions:
  - service: webhook_generic.send_webhook
    data:
      url: "https://api.example.com/status"
      method: "GET"
      payload:
        check: "system_health"
```

### PUT Request Example
```yaml
actions:
  - service: webhook_generic.send_webhook
    data:
      url: "https://api.example.com/users/{{ user.id }}"
      method: "PUT"
      payload:
        status: "active"
        last_updated: "{{ timestamp }}"
```

## Use Cases

### Forward Employee Events to External System
```yaml
trigger:
  type: event
  event: employee.created
actions:
  - service: webhook_generic.send_webhook
    data:
      url: "https://hr-system.example.com/api/employees"
      method: "POST"
      payload:
        personal_number: "{{ employee.personal_number }}"
        first_name: "{{ employee.first_name }}"
        last_name: "{{ employee.last_name }}"
        email: "{{ employee.email }}"
        department: "{{ employee.department }}"
      headers:
        "Authorization": "Bearer {{ config.api_token }}"
        "Content-Type": "application/json"
```

### Notify External Monitoring System
```yaml
trigger:
  type: event
  event: system.error
actions:
  - service: webhook_generic.send_webhook
    data:
      url: "https://monitoring.example.com/alerts"
      method: "POST"
      payload:
        severity: "high"
        message: "{{ error.message }}"
        timestamp: "{{ timestamp }}"
        system: "faneX-ID"
```

### Custom API Integration
```yaml
actions:
  - service: webhook_generic.send_webhook
    data:
      url: "https://api.custom-service.com/v1/data"
      method: "POST"
      payload:
        action: "sync"
        data:
          employees: "{{ employee_count }}"
          users: "{{ user_count }}"
      headers:
        "X-API-Key": "{{ config.api_key }}"
        "X-Request-ID": "{{ request_id }}"
```

## Security Notes

- **URLs and Tokens**: Store sensitive URLs and authentication tokens securely
- **HTTPS**: Always use HTTPS for webhook URLs to encrypt data in transit
- **Authentication**: Use headers for authentication (API keys, Bearer tokens, etc.)
- **Input Validation**: Validate webhook responses and handle errors appropriately
- **Rate Limiting**: Be aware of rate limits on target endpoints

## Troubleshooting

### Connection Timeout
- Verify the URL is correct and accessible
- Check network connectivity to the target endpoint
- Increase timeout value if requests are slow
- Verify firewall rules allow outbound connections

### Authentication Errors
- Verify authentication headers are correct
- Check if tokens/keys have expired
- Ensure credentials have required permissions
- Verify authentication method matches target service requirements

### HTTP Errors (4xx, 5xx)
- Check request payload format matches API expectations
- Verify required headers are included
- Review target service documentation for correct request format
- Check target service logs for detailed error messages

### Payload Issues
- Ensure JSON payload is valid
- Verify required fields are included
- Check data types match API expectations
- Review API documentation for correct payload structure

## Best Practices

1. **Use Default Configuration**: Set default URL and headers for common use cases
2. **Error Handling**: Always handle webhook failures in workflows
3. **Logging**: Log webhook calls for debugging and auditing
4. **Retry Logic**: Implement retry logic for transient failures
5. **Validation**: Validate webhook responses before using data

## Changelog

### 1.0.0 (2025-12-13)
- Initial release
- Support for multiple HTTP methods
- Custom headers support
- Default configuration
- JSON payload support
