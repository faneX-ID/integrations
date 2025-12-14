# SoSafe Integration

Integration with SoSafe security awareness platform API.

## Features

- Report phishing attempts
- Get user security awareness status
- Basic SoSafe API integration

## Requirements

- `requests>=2.28.0` - HTTP library

## Configuration

### Connection Parameters

- **api_url**: SoSafe API URL
- **api_key**: SoSafe API key
- **tenant_id**: SoSafe tenant ID (optional)

## Usage

### Report Phishing

```python
await service_registry.call("sosafe.report_phishing", {
    "url": "https://suspicious-site.com",
    "sender": "phishing@example.com",
    "description": "Suspicious email received"
})
```

### Get User Status

```python
await service_registry.call("sosafe.get_user_status", {
    "user_email": "user@example.com"
})
```

## Notes

- **Important**: SoSafe public API documentation is limited
- API endpoints and structure may need adjustment based on your SoSafe instance
- Contact SoSafe support for detailed API documentation
- This integration provides basic functionality based on available information
- For technical details on the phishing report button, see: https://de.support.sosafe.de/adok/technische-details-zum-phishing-meldebutton

