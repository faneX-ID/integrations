"""
Home Assistant Integration for faneX-ID.
Provides control and monitoring of Home Assistant devices and services via REST API.
"""

import logging
from typing import Any, Dict, Optional

import requests
from services.integration_base import Integration
from services.service_registry import service_registry

logger = logging.getLogger(__name__)


class HomeAssistantIntegration(Integration):
    """Home Assistant integration for device control and monitoring."""

    def __init__(
        self, core=None, config: Dict[str, Any] = None, manifest: Dict[str, Any] = None
    ):
        super().__init__(core, config, manifest)
        self._base_url = None
        self._access_token = None
        self._verify_ssl = True
        self._api_url = None

    async def async_setup(self) -> bool:
        """Set up the Home Assistant integration and register services."""
        self.logger.info("Setting up Home Assistant Integration")

        # Get configuration
        self._base_url = self.config.get("base_url", "").rstrip("/")
        self._access_token = self.config.get("access_token", "")
        self._verify_ssl = self.config.get("verify_ssl", True)

        if not self._base_url or not self._access_token:
            self.logger.error("Home Assistant base_url and access_token are required")
            return False

        self._api_url = f"{self._base_url}/api"

        # Register all services
        self.register_service(
            "call_service",
            self.call_service,
            schema={
                "domain": {"type": "string"},
                "service": {"type": "string"},
                "entity_id": {"type": "string"},
                "service_data": {"type": "object", "nullable": True},
            },
            description="Call a Home Assistant service",
        )

        self.register_service(
            "get_state",
            self.get_state,
            schema={"entity_id": {"type": "string"}},
            description="Get the state of a Home Assistant entity",
        )

        self.register_service(
            "get_states",
            self.get_states,
            schema={
                "domain": {"type": "string", "nullable": True},
                "entity_id": {"type": "string", "nullable": True},
            },
            description="Get states of all or filtered Home Assistant entities",
        )

        self.register_service(
            "fire_event",
            self.fire_event,
            schema={
                "event_type": {"type": "string"},
                "event_data": {"type": "object", "nullable": True},
            },
            description="Fire a custom event in Home Assistant",
        )

        self.register_service(
            "test_connection",
            self.test_connection,
            schema={},
            description="Test connection to Home Assistant instance",
        )

        return True

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for Home Assistant API requests."""
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    def call_service(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call a Home Assistant service."""
        domain = data.get("domain")
        service = data.get("service")
        entity_id = data.get("entity_id")
        service_data = data.get("service_data", {})

        if not domain or not service:
            return {"success": False, "error": "domain and service are required"}

        url = f"{self._api_url}/services/{domain}/{service}"

        payload = {}
        if entity_id:
            payload["entity_id"] = entity_id
        if service_data:
            payload.update(service_data)

        try:
            response = requests.post(
                url, json=payload, headers=self._get_headers(), verify=self._verify_ssl, timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to call Home Assistant service: {e}")
            return {"success": False, "error": str(e)}

    def get_state(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get the state of a Home Assistant entity."""
        entity_id = data.get("entity_id")
        if not entity_id:
            return {"success": False, "error": "entity_id is required"}

        url = f"{self._api_url}/states/{entity_id}"

        try:
            response = requests.get(
                url, headers=self._get_headers(), verify=self._verify_ssl, timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get Home Assistant state: {e}")
            return {"success": False, "error": str(e)}

    def get_states(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get states of all or filtered Home Assistant entities."""
        url = f"{self._api_url}/states"
        domain = data.get("domain")
        entity_id_pattern = data.get("entity_id")

        try:
            response = requests.get(
                url, headers=self._get_headers(), verify=self._verify_ssl, timeout=10
            )
            response.raise_for_status()
            states = response.json()

            # Apply filters
            if domain:
                states = [s for s in states if s.get("entity_id", "").startswith(f"{domain}.")]
            if entity_id_pattern:
                states = [
                    s for s in states if entity_id_pattern.lower() in s.get("entity_id", "").lower()
                ]

            return {"success": True, "data": states, "count": len(states)}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get Home Assistant states: {e}")
            return {"success": False, "error": str(e)}

    def fire_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fire a custom event in Home Assistant."""
        event_type = data.get("event_type")
        event_data = data.get("event_data", {})

        if not event_type:
            return {"success": False, "error": "event_type is required"}

        url = f"{self._api_url}/events/{event_type}"

        try:
            response = requests.post(
                url, json=event_data, headers=self._get_headers(), verify=self._verify_ssl, timeout=10
            )
            response.raise_for_status()
            return {"success": True, "message": "Event fired successfully"}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fire Home Assistant event: {e}")
            return {"success": False, "error": str(e)}

    def test_connection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Test connection to Home Assistant instance."""
        url = f"{self._api_url}/"

        try:
            response = requests.get(
                url, headers=self._get_headers(), verify=self._verify_ssl, timeout=10
            )
            response.raise_for_status()
            config = response.json()
            return {
                "success": True,
                "message": "Connection successful",
                "version": config.get("version"),
                "location_name": config.get("location_name"),
            }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to connect to Home Assistant: {e}")
            return {"success": False, "error": str(e)}

