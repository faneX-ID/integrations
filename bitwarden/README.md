# Bitwarden Integration

Integration with Bitwarden password manager API for managing organizations, members, collections, and groups.

## Features

- Get organization information
- Create and manage organization members
- Create and manage collections
- Full Bitwarden Public API support

## Requirements

- `requests>=2.28.0` - HTTP library

## Configuration

### Connection Parameters

- **api_url**: Bitwarden API URL (default: https://api.bitwarden.com)
- **client_id**: Bitwarden API client ID
- **client_secret**: Bitwarden API client secret
- **default_organization_id**: Default organization ID (optional)

## Usage

### Get Organization

```python
await service_registry.call("bitwarden.get_organization", {
    "organization_id": "org-123"
})
```

### Create Member

```python
await service_registry.call("bitwarden.create_member", {
    "organization_id": "org-123",
    "email": "user@example.com",
    "collections": ["collection-123"]
})
```

### Create Collection

```python
await service_registry.call("bitwarden.create_collection", {
    "organization_id": "org-123",
    "name": "IT Department"
})
```

## Notes

- Requires Bitwarden API credentials (client ID and secret)
- Supports both Bitwarden Cloud and self-hosted instances
- For Vaultwarden (self-hosted alternative), use the vaultwarden helper integration which references this integration

