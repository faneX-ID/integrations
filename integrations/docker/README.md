# Docker Integration

Docker integration for managing containers and images on remote Docker hosts.

## Overview

This integration enables faneX-ID to manage Docker containers on local or remote Docker hosts. It supports container lifecycle management, statistics, and log retrieval.

## Features

- List containers on Docker hosts
- Start, stop, and restart containers
- Get container statistics (CPU, memory, network)
- Retrieve container logs
- Support for local and remote Docker hosts (via TCP or Unix socket)

## Setup

### Configuration

```json
{
  "default_timeout": 60
}
```

**Configuration Options:**

- `default_timeout` (optional): Default timeout for Docker operations in seconds (default: `60`)

## Services

### List Containers

List containers on a Docker host:

```json
{
  "host": "192.168.1.100:2375",
  "all": false
}
```

**Host Formats:**
- `local` or `localhost` - Local Docker socket (`unix:///var/run/docker.sock`)
- `192.168.1.100` - Remote host via TCP (default port 2375)
- `192.168.1.100:2376` - Remote host with custom port
- `tcp://192.168.1.100:2375` - Explicit TCP connection
- `unix:///var/run/docker.sock` - Explicit Unix socket

**Response:**
```json
{
  "success": true,
  "containers": [
    {
      "id": "abc123...",
      "name": "nginx",
      "status": "running",
      "image": "nginx:latest"
    }
  ],
  "count": 1
}
```

### Start Container

Start a container:

```json
{
  "host": "192.168.1.100:2375",
  "container_id": "nginx"
}
```

### Stop Container

Stop a container:

```json
{
  "host": "192.168.1.100:2375",
  "container_id": "nginx",
  "timeout": 10
}
```

### Restart Container

Restart a container:

```json
{
  "host": "192.168.1.100:2375",
  "container_id": "nginx"
}
```

### Get Container Stats

Get container statistics:

```json
{
  "host": "192.168.1.100:2375",
  "container_id": "nginx"
}
```

**Response:**
```json
{
  "success": true,
  "container_id": "nginx",
  "stats": {
    "cpu_percent": 2.5,
    "memory_usage": 52428800,
    "memory_limit": 1073741824,
    "network_rx": 1024000,
    "network_tx": 512000
  }
}
```

### Get Container Logs

Get container logs:

```json
{
  "host": "192.168.1.100:2375",
  "container_id": "nginx",
  "tail": 100,
  "since": "10m"
}
```

## Workflow Examples

### Monitor Container Status

```yaml
trigger:
  schedule: "*/5 * * * *"
steps:
  - service: docker.list_containers
    data:
      host: "192.168.1.100:2375"
      all: true
  - if_condition:
      field: containers[0].status
      operator: ne
      value: running
    then:
      - service: docker.start_container
        data:
          host: "192.168.1.100:2375"
          container_id: "{{containers[0].id}}"
```

### Restart Failed Containers

```yaml
trigger:
  schedule: "0 * * * *"
steps:
  - service: docker.list_containers
    data:
      host: "192.168.1.100:2375"
      all: true
  - service: docker.restart_container
    data:
      host: "192.168.1.100:2375"
      container_id: "nginx"
```

## Security Notes

- **Remote Docker Access**: Ensure Docker daemon is properly secured when exposing TCP port
- **TLS**: For production, use TLS-enabled Docker connections (`tcp://` with TLS)
- **Firewall**: Restrict Docker TCP port access to trusted networks
- **Authentication**: Consider using Docker context or certificate-based authentication

## Notes

- This is a **system integration** and cannot be uninstalled
- Requires `docker` Python library
- Supports both local (Unix socket) and remote (TCP) Docker hosts
- Default Docker port is 2375 (unencrypted) or 2376 (TLS)
- Container IDs can be full IDs or container names
- Statistics are returned as a snapshot (not streamed)


