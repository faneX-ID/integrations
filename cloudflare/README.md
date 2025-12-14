# Cloudflare Integration

Integration for Cloudflare API. Manage DNS records, zones, and Cloudflare services.

## Overview

This integration provides Cloudflare API functionality for faneX-ID, allowing you to:
- Manage DNS records (create, update, delete, list)
- Manage Cloudflare zones
- Purge Cloudflare cache

## Setup

### Prerequisites

- Cloudflare account
- API token or API key + email

### Configuration

**Option 1: API Token (Recommended)**
```json
{
  "api_token": "YOUR_API_TOKEN"
}
```

**Option 2: API Key + Email**
```json
{
  "api_key": "YOUR_API_KEY",
  "email": "your-email@example.com"
}
```

**Configuration Options:**

- `api_token` (required if not using API key): Cloudflare API token with appropriate permissions
- `api_key` (required if not using API token): Cloudflare API key
- `email` (required if using API key): Cloudflare account email

## Services

### List Zones

List all Cloudflare zones:

```json
{
  "name": "example.com",
  "status": "active"
}
```

### Get Zone

Get details of a specific zone:

```json
{
  "zone_id": "zone-id-here"
}
```

### List DNS Records

List DNS records for a zone:

```json
{
  "zone_id": "zone-id-here",
  "type": "A",
  "name": "subdomain"
}
```

### Create DNS Record

Create a new DNS record:

```json
{
  "zone_id": "zone-id-here",
  "type": "A",
  "name": "subdomain.example.com",
  "content": "192.0.2.1",
  "ttl": 3600,
  "proxied": false
}
```

### Update DNS Record

Update an existing DNS record:

```json
{
  "zone_id": "zone-id-here",
  "record_id": "record-id-here",
  "content": "192.0.2.2",
  "ttl": 7200
}
```

### Delete DNS Record

Delete a DNS record:

```json
{
  "zone_id": "zone-id-here",
  "record_id": "record-id-here"
}
```

### Purge Cache

Purge Cloudflare cache for a zone:

```json
{
  "zone_id": "zone-id-here",
  "purge_everything": true
}
```

Or purge specific files/tags:

```json
{
  "zone_id": "zone-id-here",
  "files": ["https://example.com/file.css", "https://example.com/file.js"],
  "tags": ["tag1", "tag2"]
}
```

## Usage

1. Create an API token in Cloudflare dashboard (or use API key + email)
2. Configure the integration with your credentials
3. Use the services to manage DNS records and zones

## API Token Permissions

When creating an API token, ensure it has the following permissions:
- Zone: Read, Edit
- DNS: Read, Edit
- Cache Purge: Purge
