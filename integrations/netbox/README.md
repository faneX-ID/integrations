# NetBox Integration

Integration for managing NetBox IPAM and DCIM via REST API.

## Overview

This integration enables faneX-ID to interact with NetBox instances for managing devices, IP addresses, virtual machines, and other infrastructure components. NetBox is an open-source IPAM and DCIM tool for network infrastructure management.

## Features

- List and manage devices
- Query IP addresses
- Manage virtual machines
- Create, update, and delete devices
- Filter by site, status, and other attributes
- Test connection to NetBox instance

## Setup

### Configuration

```json
{
  "base_url": "https://netbox.example.com",
  "api_token": "your_api_token_here",
  "verify_ssl": true
}
```

**Configuration Options:**

- `base_url` (required): Base URL of your NetBox instance (e.g., `https://netbox.example.com`)
- `api_token` (required): NetBox API token (create in NetBox: User > API Tokens)
- `verify_ssl` (optional): Verify SSL certificate (default: `true`)

### Creating an API Token

1. Log in to NetBox
2. Go to your User Profile (top right)
3. Navigate to "API Tokens"
4. Click "Add Token"
5. Give it a name (e.g., "faneX-ID Integration")
6. Set expiration (optional)
7. Copy the token and use it in the integration configuration

## Services

### Get Devices

Get list of devices from NetBox:

```json
{
  "site": "datacenter-1",
  "status": "active",
  "limit": 50
}
```

**Response:**
```json
{
  "success": true,
  "devices": [
    {
      "id": 1,
      "name": "switch-01",
      "device_type": {...},
      "site": {...},
      "status": {...},
      "primary_ip": {...}
    }
  ],
  "count": 1
}
```

### Get Device

Get a specific device by ID or name:

```json
{
  "device_id": "switch-01"
}
```

### Get IP Addresses

Get list of IP addresses:

```json
{
  "device": "switch-01",
  "status": "active",
  "limit": 50
}
```

### Get Virtual Machines

Get list of virtual machines:

```json
{
  "cluster": "production",
  "status": "active",
  "limit": 50
}
```

### Create Device

Create a new device in NetBox:

```json
{
  "name": "router-01",
  "device_type": "Cisco ISR 4331",
  "site": "datacenter-1",
  "status": "active",
  "role": "router"
}
```

### Update Device

Update an existing device:

```json
{
  "device_id": "router-01",
  "status": "offline",
  "role": "backup-router"
}
```

### Delete Device

Delete a device from NetBox:

```json
{
  "device_id": "router-01"
}
```

### Test Connection

Test connection to NetBox instance:

```json
{}
```

**Response:**
```json
{
  "success": true,
  "message": "Connection successful",
  "netbox_version": "4.0.0"
}
```

## Workflow Examples

### Monitor Device Status

```yaml
trigger:
  schedule: "*/5 * * * *"
steps:
  - service: netbox.get_devices
    data:
      site: "datacenter-1"
      status: "active"
  - service: netbox.get_device
    data:
      device_id: "switch-01"
  - if_condition:
      field: device.status.value
      operator: ne
      value: active
    then:
      - service: mail.send_plain_email
        data:
          to_email: "admin@company.com"
          subject: "Device Status Alert"
          body: "Device switch-01 is not active"
```

### Create Device on Provisioning

```yaml
trigger:
  event: device.provisioned
steps:
  - service: netbox.create_device
    data:
      name: "{{event.data.hostname}}"
      device_type: "{{event.data.device_type}}"
      site: "{{event.data.site}}"
      status: "active"
      role: "{{event.data.role}}"
```

## Notes

- This is a **store integration** (not a system integration) and can be installed/uninstalled
- Requires NetBox 3.0 or later
- API token must have appropriate permissions for the operations you want to perform
- Device types, sites, and roles must exist in NetBox before creating devices
- Filtering by name/slug is case-sensitive in some NetBox versions
- All API calls have a 30-second timeout

