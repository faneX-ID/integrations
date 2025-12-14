# VMware ESXi Integration

Integration for managing VMware ESXi hosts and virtual machines via vSphere REST API.

## Overview

This integration enables faneX-ID to manage VMware ESXi hosts and virtual machines using the vSphere REST API. It provides functionality to list VMs, check power states, and control VM power operations.

## Features

- List all virtual machines on ESXi host
- Get detailed VM information
- Power on/off virtual machines
- Restart virtual machines
- Check VM power state
- Test connection to ESXi host

## Setup

### Configuration

```json
{
  "host": "esxi.example.com",
  "username": "root",
  "password": "password123",
  "verify_ssl": false
}
```

**Configuration Options:**

- `host` (required): ESXi hostname or IP address
- `username` (required): ESXi username (typically `root`)
- `password` (required): ESXi password
- `verify_ssl` (optional): Verify SSL certificate (default: `false`, as ESXi often uses self-signed certificates)

### Requirements

- ESXi 6.5 or later (with vSphere REST API enabled)
- vSphere REST API must be enabled on the ESXi host

## Services

### List VMs

List all virtual machines on the ESXi host:

```json
{}
```

**Response:**
```json
{
  "success": true,
  "vms": [
    {
      "vm": "vm-123",
      "name": "Ubuntu Server",
      "power_state": "POWERED_ON",
      "cpu_count": 2,
      "memory_mb": 4096
    }
  ],
  "count": 1
}
```

### Get VM Info

Get detailed information about a specific VM:

```json
{
  "vm_id": "vm-123"
}
```

### Power On VM

Power on a virtual machine:

```json
{
  "vm_id": "vm-123"
}
```

### Power Off VM

Power off a virtual machine:

```json
{
  "vm_id": "vm-123"
}
```

### Restart VM

Restart a virtual machine:

```json
{
  "vm_id": "vm-123"
}
```

### Get VM Power State

Get the current power state of a VM:

```json
{
  "vm_id": "vm-123"
}
```

**Response:**
```json
{
  "success": true,
  "vm_id": "vm-123",
  "power_state": "POWERED_ON"
}
```

### Test Connection

Test connection to ESXi host:

```json
{}
```

## Workflow Examples

### Start VM on Schedule

```yaml
trigger:
  schedule: "0 8 * * 1-5"
steps:
  - service: esxi.power_on_vm
    data:
      vm_id: "vm-123"
```

### Monitor VM Power State

```yaml
trigger:
  schedule: "*/5 * * * *"
steps:
  - service: esxi.get_vm_power_state
    data:
      vm_id: "vm-123"
  - if_condition:
      field: power_state
      operator: ne
      value: POWERED_ON
    then:
      - service: esxi.power_on_vm
        data:
          vm_id: "vm-123"
```

### List All VMs

```yaml
trigger:
  schedule: "0 * * * *"
steps:
  - service: esxi.list_vms
    data: {}
```

## Notes

- This is a **store integration** (not a system integration) and can be installed/uninstalled
- Requires ESXi 6.5 or later with vSphere REST API enabled
- Uses vSphere REST API (not SOAP API)
- SSL verification is disabled by default due to self-signed certificates on ESXi
- VM IDs can be obtained from the `list_vms` service
- Power operations are asynchronous; the API returns immediately
- Requires valid ESXi credentials with appropriate permissions
