# Vaultwarden Integration

Helper integration for Vaultwarden (self-hosted Bitwarden alternative).

## Overview

Vaultwarden is a self-hosted alternative to Bitwarden that uses a Bitwarden-compatible API. This integration is a helper that references the `bitwarden` integration for all functionality.

## Configuration

This is a helper integration. To use Vaultwarden:

1. Install the `bitwarden` integration
2. Configure the `bitwarden` integration with your Vaultwarden server URL:
   - Set `api_url` to your Vaultwarden server URL (e.g., `https://vaultwarden.example.com/api`)
   - Configure your Vaultwarden API credentials (`client_id` and `client_secret`)

## Usage

All Vaultwarden operations use the `bitwarden` integration services:

```python
# Use bitwarden services with Vaultwarden
await service_registry.call("bitwarden.get_organization", {
    "organization_id": "org-123"
})
```

## Notes

- Vaultwarden API is fully compatible with Bitwarden API
- This helper integration only helps with discovery/search
- All functionality is provided by the `bitwarden` integration
- Configure the `bitwarden` integration with your Vaultwarden server URL

