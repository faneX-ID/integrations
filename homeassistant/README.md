# Home Assistant Integration

Integration for controlling and monitoring Home Assistant devices and services via REST API.

## Overview

This integration enables faneX-ID to interact with Home Assistant instances, allowing you to control devices, read sensor values, fire events, and monitor your smart home from faneX-ID workflows.

## Features

- Control Home Assistant devices (lights, switches, climate, etc.)
- Read entity states and sensor values
- Fire custom events in Home Assistant
- Monitor device status
- Integration with faneX-ID workflows

## Setup

### Configuration

```json
{
  "base_url": "https://homeassistant.local:8123",
  "access_token": "your_long_lived_access_token",
  "verify_ssl": true
}
```

**Configuration Options:**

- `base_url` (required): Base URL of your Home Assistant instance (e.g., `https://homeassistant.local:8123`)
- `access_token` (required): Long-lived access token (create in Home Assistant: Profile > Long-Lived Access Tokens)
- `verify_ssl` (optional): Verify SSL certificate (default: `true`, set to `false` for self-signed certificates)

### Creating a Long-Lived Access Token

1. Open Home Assistant
2. Go to your Profile (bottom left)
3. Scroll down to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Give it a name (e.g., "faneX-ID Integration")
6. Copy the token and use it in the integration configuration

## Services

### Call Service

Call a Home Assistant service to control devices:

```json
{
  "domain": "light",
  "service": "turn_on",
  "entity_id": "light.living_room",
  "service_data": {
    "brightness": 255,
    "color_name": "red"
  }
}
```

**Common Services:**

- `light.turn_on` / `light.turn_off`
- `switch.turn_on` / `switch.turn_off`
- `climate.set_temperature`
- `cover.open_cover` / `cover.close_cover`
- `fan.turn_on` / `fan.turn_off`

### Get State

Get the current state of a specific entity:

```json
{
  "entity_id": "light.living_room"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "entity_id": "light.living_room",
    "state": "on",
    "attributes": {
      "brightness": 255,
      "color_name": "red"
    }
  }
}
```

### Get States

Get states of all or filtered entities:

```json
{
  "domain": "light",
  "entity_id": "living_room"
}
```

**Filters:**
- `domain`: Filter by domain (e.g., `light`, `switch`, `sensor`)
- `entity_id`: Filter by entity ID pattern (partial match)

### Fire Event

Fire a custom event in Home Assistant:

```json
{
  "event_type": "fanexid_event",
  "event_data": {
    "action": "user_created",
    "user_id": "12345"
  }
}
```

### Test Connection

Test the connection to your Home Assistant instance:

```json
{}
```

**Response:**
```json
{
  "success": true,
  "message": "Connection successful",
  "version": "2024.1.0",
  "location_name": "Home"
}
```

## Workflow Examples

### Turn on Lights When User Arrives

```yaml
trigger:
  event: employee.created
steps:
  - service: homeassistant.call_service
    data:
      domain: light
      service: turn_on
      entity_id: light.office
      service_data:
        brightness: 200
```

### Monitor Temperature Sensor

```yaml
trigger:
  schedule: "*/5 * * * *"
steps:
  - service: homeassistant.get_state
    data:
      entity_id: sensor.temperature
  - if_condition:
      field: data.state
      operator: gt
      value: 25
    then:
      - service: homeassistant.call_service
        data:
          domain: climate
          service: set_temperature
          entity_id: climate.living_room
          service_data:
            temperature: 22
```

## Notes

- This is a **store integration** (not a system integration) and can be installed/uninstalled
- Requires Home Assistant 2021.3.0 or later
- Long-lived access tokens do not expire (unlike API keys)
- SSL verification can be disabled for self-signed certificates (not recommended for production)
- All API calls have a 10-second timeout
