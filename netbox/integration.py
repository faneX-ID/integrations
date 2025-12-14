"""
NetBox Integration for faneX-ID.
Integration for managing NetBox IPAM and DCIM via REST API.
"""

import logging
from typing import Any, Dict, Optional

import requests
from services.integration_base import Integration
from services.service_registry import service_registry

logger = logging.getLogger(__name__)


class NetBoxIntegration(Integration):
    """NetBox integration for IPAM and DCIM management."""

    def __init__(
        self, core=None, config: Dict[str, Any] = None, manifest: Dict[str, Any] = None
    ):
        super().__init__(core, config, manifest)
        self._base_url = None
        self._api_token = None
        self._verify_ssl = True
        self._api_base = None

    async def async_setup(self) -> bool:
        """Set up the NetBox integration and register services."""
        self.logger.info("Setting up NetBox Integration")

        # Get configuration
        self._base_url = self.config.get("base_url", "").rstrip("/")
        self._api_token = self.config.get("api_token", "")
        self._verify_ssl = self.config.get("verify_ssl", True)

        if not self._base_url or not self._api_token:
            self.logger.error("NetBox base_url and api_token are required")
            return False

        self._api_base = f"{self._base_url}/api"

        # Register services
        self.register_service(
            "get_devices",
            self.get_devices,
            schema={
                "site": {"type": "string", "nullable": True},
                "status": {"type": "string", "nullable": True},
                "limit": {"type": "integer", "default": 50},
            },
            description="Get list of devices from NetBox",
        )

        self.register_service(
            "get_device",
            self.get_device,
            schema={"device_id": {"type": "string"}},
            description="Get a specific device by ID or name",
        )

        self.register_service(
            "get_ip_addresses",
            self.get_ip_addresses,
            schema={
                "device": {"type": "string", "nullable": True},
                "status": {"type": "string", "nullable": True},
                "limit": {"type": "integer", "default": 50},
            },
            description="Get list of IP addresses from NetBox",
        )

        self.register_service(
            "get_virtual_machines",
            self.get_virtual_machines,
            schema={
                "cluster": {"type": "string", "nullable": True},
                "status": {"type": "string", "nullable": True},
                "limit": {"type": "integer", "default": 50},
            },
            description="Get list of virtual machines from NetBox",
        )

        self.register_service(
            "create_device",
            self.create_device,
            schema={
                "name": {"type": "string"},
                "device_type": {"type": "string"},
                "site": {"type": "string"},
                "status": {"type": "string", "default": "active"},
                "role": {"type": "string", "nullable": True},
            },
            description="Create a new device in NetBox",
        )

        self.register_service(
            "update_device",
            self.update_device,
            schema={
                "device_id": {"type": "string"},
                "name": {"type": "string", "nullable": True},
                "status": {"type": "string", "nullable": True},
                "role": {"type": "string", "nullable": True},
            },
            description="Update an existing device",
        )

        self.register_service(
            "delete_device",
            self.delete_device,
            schema={"device_id": {"type": "string"}},
            description="Delete a device from NetBox",
        )

        self.register_service(
            "test_connection",
            self.test_connection,
            schema={},
            description="Test connection to NetBox instance",
        )

        return True

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for NetBox API requests."""
        return {
            "Authorization": f"Token {self._api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _make_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a request to the NetBox API."""
        url = f"{self._api_base}/{endpoint.lstrip('/')}"
        headers = self._get_headers()

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                verify=self._verify_ssl,
                timeout=30,
            )
            response.raise_for_status()

            # NetBox returns results in a 'results' field for list endpoints
            if method.upper() == "GET" and "results" in response.json():
                return {"success": True, "data": response.json()}
            else:
                return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"NetBox API request failed: {e}")
            error_msg = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("detail", error_msg)
                except:
                    error_msg = e.response.text or error_msg
            return {"success": False, "error": error_msg}

    def get_devices(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of devices from NetBox."""
        params = {}
        if data.get("site"):
            params["site"] = data.get("site")
        if data.get("status"):
            params["status"] = data.get("status")
        params["limit"] = data.get("limit", 50)

        result = self._make_request("GET", "dcim/devices/", params=params)
        if result.get("success"):
            return {
                "success": True,
                "devices": result["data"].get("results", []),
                "count": result["data"].get("count", 0),
            }
        return result

    def get_device(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific device by ID or name."""
        device_id = data.get("device_id")
        if not device_id:
            return {"success": False, "error": "device_id is required"}

        # Try by ID first, then by name
        result = self._make_request("GET", f"dcim/devices/{device_id}/")
        if not result.get("success"):
            # Try searching by name
            params = {"name": device_id}
            search_result = self._make_request("GET", "dcim/devices/", params=params)
            if search_result.get("success") and search_result["data"].get("results"):
                return {
                    "success": True,
                    "device": search_result["data"]["results"][0],
                }
        return result

    def get_ip_addresses(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of IP addresses from NetBox."""
        params = {}
        if data.get("device"):
            params["device"] = data.get("device")
        if data.get("status"):
            params["status"] = data.get("status")
        params["limit"] = data.get("limit", 50)

        result = self._make_request("GET", "ipam/ip-addresses/", params=params)
        if result.get("success"):
            return {
                "success": True,
                "ip_addresses": result["data"].get("results", []),
                "count": result["data"].get("count", 0),
            }
        return result

    def get_virtual_machines(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of virtual machines from NetBox."""
        params = {}
        if data.get("cluster"):
            params["cluster"] = data.get("cluster")
        if data.get("status"):
            params["status"] = data.get("status")
        params["limit"] = data.get("limit", 50)

        result = self._make_request("GET", "virtualization/virtual-machines/", params=params)
        if result.get("success"):
            return {
                "success": True,
                "virtual_machines": result["data"].get("results", []),
                "count": result["data"].get("count", 0),
            }
        return result

    def create_device(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new device in NetBox."""
        # First, resolve device_type and site to IDs
        device_type_name = data.get("device_type")
        site_name = data.get("site")

        # Get device type ID
        device_type_result = self._make_request("GET", "dcim/device-types/", params={"model": device_type_name})
        if not device_type_result.get("success") or not device_type_result["data"].get("results"):
            return {"success": False, "error": f"Device type '{device_type_name}' not found"}

        device_type_id = device_type_result["data"]["results"][0]["id"]

        # Get site ID
        site_result = self._make_request("GET", "dcim/sites/", params={"slug": site_name})
        if not site_result.get("success") or not site_result["data"].get("results"):
            # Try by name
            site_result = self._make_request("GET", "dcim/sites/", params={"name": site_name})
            if not site_result.get("success") or not site_result["data"].get("results"):
                return {"success": False, "error": f"Site '{site_name}' not found"}

        site_id = site_result["data"]["results"][0]["id"]

        # Prepare device data
        device_data = {
            "name": data.get("name"),
            "device_type": device_type_id,
            "site": site_id,
            "status": data.get("status", "active"),
        }

        if data.get("role"):
            # Get role ID
            role_result = self._make_request("GET", "dcim/device-roles/", params={"name": data.get("role")})
            if role_result.get("success") and role_result["data"].get("results"):
                device_data["role"] = role_result["data"]["results"][0]["id"]

        result = self._make_request("POST", "dcim/devices/", data=device_data)
        if result.get("success"):
            return {"success": True, "device": result["data"]}
        return result

    def update_device(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing device."""
        device_id = data.get("device_id")
        if not device_id:
            return {"success": False, "error": "device_id is required"}

        # Get current device
        device_result = self.get_device({"device_id": device_id})
        if not device_result.get("success"):
            return device_result

        current_device = device_result.get("device") or device_result.get("data", {})

        # Prepare update data
        update_data = {}
        if data.get("name"):
            update_data["name"] = data.get("name")
        if data.get("status"):
            update_data["status"] = data.get("status")
        if data.get("role"):
            # Get role ID
            role_result = self._make_request("GET", "dcim/device-roles/", params={"name": data.get("role")})
            if role_result.get("success") and role_result["data"].get("results"):
                update_data["role"] = role_result["data"]["results"][0]["id"]

        if not update_data:
            return {"success": False, "error": "No fields to update"}

        device_api_id = current_device.get("id")
        if not device_api_id:
            return {"success": False, "error": "Could not determine device API ID"}

        result = self._make_request("PATCH", f"dcim/devices/{device_api_id}/", data=update_data)
        return result

    def delete_device(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a device from NetBox."""
        device_id = data.get("device_id")
        if not device_id:
            return {"success": False, "error": "device_id is required"}

        # Get device to find API ID
        device_result = self.get_device({"device_id": device_id})
        if not device_result.get("success"):
            return device_result

        device = device_result.get("device") or device_result.get("data", {})
        device_api_id = device.get("id")
        if not device_api_id:
            return {"success": False, "error": "Could not determine device API ID"}

        result = self._make_request("DELETE", f"dcim/devices/{device_api_id}/")
        if result.get("success"):
            return {"success": True, "message": f"Device {device_id} deleted"}
        return result

    def test_connection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Test connection to NetBox instance."""
        result = self._make_request("GET", "status/")
        if result.get("success"):
            return {
                "success": True,
                "message": "Connection successful",
                "netbox_version": result["data"].get("netbox-version"),
            }
        return result

