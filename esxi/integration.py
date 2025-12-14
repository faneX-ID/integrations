"""
VMware ESXi Integration for faneX-ID.
Integration for managing VMware ESXi hosts and virtual machines via vSphere REST API.
"""

import logging
from typing import Any, Dict, Optional

import requests
from requests.auth import HTTPBasicAuth
from services.integration_base import Integration
from services.service_registry import service_registry

logger = logging.getLogger(__name__)


class ESXiIntegration(Integration):
    """VMware ESXi integration for VM management."""

    def __init__(
        self, core=None, config: Dict[str, Any] = None, manifest: Dict[str, Any] = None
    ):
        super().__init__(core, config, manifest)
        self._host = None
        self._username = None
        self._password = None
        self._verify_ssl = False
        self._session_id = None
        self._api_base = None

    async def async_setup(self) -> bool:
        """Set up the ESXi integration and register services."""
        self.logger.info("Setting up ESXi Integration")

        # Get configuration
        self._host = self.config.get("host", "").rstrip("/")
        self._username = self.config.get("username", "")
        self._password = self.config.get("password", "")
        self._verify_ssl = self.config.get("verify_ssl", False)

        if not self._host or not self._username or not self._password:
            self.logger.error("ESXi host, username, and password are required")
            return False

        # Determine API base URL
        if self._host.startswith("http://") or self._host.startswith("https://"):
            self._api_base = f"{self._host}/api"
        else:
            self._api_base = f"https://{self._host}/api"

        # Authenticate
        auth_success = await self._authenticate()
        if not auth_success:
            self.logger.error("Failed to authenticate with ESXi host")
            return False

        # Register services
        self.register_service(
            "list_vms",
            self.list_vms,
            schema={},
            description="List all virtual machines on the ESXi host",
        )

        self.register_service(
            "get_vm_info",
            self.get_vm_info,
            schema={"vm_id": {"type": "string"}},
            description="Get information about a specific VM",
        )

        self.register_service(
            "power_on_vm",
            self.power_on_vm,
            schema={"vm_id": {"type": "string"}},
            description="Power on a virtual machine",
        )

        self.register_service(
            "power_off_vm",
            self.power_off_vm,
            schema={"vm_id": {"type": "string"}},
            description="Power off a virtual machine",
        )

        self.register_service(
            "restart_vm",
            self.restart_vm,
            schema={"vm_id": {"type": "string"}},
            description="Restart a virtual machine",
        )

        self.register_service(
            "get_vm_power_state",
            self.get_vm_power_state,
            schema={"vm_id": {"type": "string"}},
            description="Get the power state of a VM",
        )

        self.register_service(
            "test_connection",
            self.test_connection,
            schema={},
            description="Test connection to ESXi host",
        )

        return True

    async def _authenticate(self) -> bool:
        """Authenticate with ESXi host and get session ID."""
        try:
            url = f"{self._api_base}/session"
            response = requests.post(
                url,
                auth=HTTPBasicAuth(self._username, self._password),
                verify=self._verify_ssl,
                timeout=10,
            )
            response.raise_for_status()
            self._session_id = response.json()
            return True
        except Exception as e:
            self.logger.error(f"ESXi authentication failed: {e}")
            return False

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with session ID."""
        return {
            "vmware-api-session-id": self._session_id,
            "Content-Type": "application/json",
        }

    def list_vms(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """List all virtual machines on the ESXi host."""
        try:
            url = f"{self._api_base}/vcenter/vm"
            response = requests.get(
                url, headers=self._get_headers(), verify=self._verify_ssl, timeout=30
            )
            response.raise_for_status()
            vms = response.json()

            # Simplify VM list
            vm_list = []
            for vm in vms.get("value", []):
                vm_list.append(
                    {
                        "vm": vm.get("vm"),
                        "name": vm.get("name"),
                        "power_state": vm.get("power_state"),
                        "cpu_count": vm.get("cpu", {}).get("count"),
                        "memory_mb": vm.get("memory", {}).get("size_MiB"),
                    }
                )

            return {"success": True, "vms": vm_list, "count": len(vm_list)}
        except Exception as e:
            self.logger.error(f"Failed to list VMs: {e}")
            return {"success": False, "error": str(e)}

    def get_vm_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a specific VM."""
        vm_id = data.get("vm_id")
        if not vm_id:
            return {"success": False, "error": "vm_id is required"}

        try:
            url = f"{self._api_base}/vcenter/vm/{vm_id}"
            response = requests.get(
                url, headers=self._get_headers(), verify=self._verify_ssl, timeout=30
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"Failed to get VM info for {vm_id}: {e}")
            return {"success": False, "error": str(e)}

    def power_on_vm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Power on a virtual machine."""
        vm_id = data.get("vm_id")
        if not vm_id:
            return {"success": False, "error": "vm_id is required"}

        try:
            url = f"{self._api_base}/vcenter/vm/{vm_id}/power/start"
            response = requests.post(
                url, headers=self._get_headers(), verify=self._verify_ssl, timeout=30
            )
            response.raise_for_status()
            return {"success": True, "message": f"VM {vm_id} powered on"}
        except Exception as e:
            self.logger.error(f"Failed to power on VM {vm_id}: {e}")
            return {"success": False, "error": str(e)}

    def power_off_vm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Power off a virtual machine."""
        vm_id = data.get("vm_id")
        if not vm_id:
            return {"success": False, "error": "vm_id is required"}

        try:
            url = f"{self._api_base}/vcenter/vm/{vm_id}/power/stop"
            response = requests.post(
                url, headers=self._get_headers(), verify=self._verify_ssl, timeout=30
            )
            response.raise_for_status()
            return {"success": True, "message": f"VM {vm_id} powered off"}
        except Exception as e:
            self.logger.error(f"Failed to power off VM {vm_id}: {e}")
            return {"success": False, "error": str(e)}

    def restart_vm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Restart a virtual machine."""
        vm_id = data.get("vm_id")
        if not vm_id:
            return {"success": False, "error": "vm_id is required"}

        try:
            url = f"{self._api_base}/vcenter/vm/{vm_id}/power/reset"
            response = requests.post(
                url, headers=self._get_headers(), verify=self._verify_ssl, timeout=30
            )
            response.raise_for_status()
            return {"success": True, "message": f"VM {vm_id} restarted"}
        except Exception as e:
            self.logger.error(f"Failed to restart VM {vm_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_vm_power_state(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get the power state of a VM."""
        vm_id = data.get("vm_id")
        if not vm_id:
            return {"success": False, "error": "vm_id is required"}

        try:
            url = f"{self._api_base}/vcenter/vm/{vm_id}/power"
            response = requests.get(
                url, headers=self._get_headers(), verify=self._verify_ssl, timeout=30
            )
            response.raise_for_status()
            state = response.json()
            return {"success": True, "vm_id": vm_id, "power_state": state.get("state")}
        except Exception as e:
            self.logger.error(f"Failed to get power state for VM {vm_id}: {e}")
            return {"success": False, "error": str(e)}

    def test_connection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Test connection to ESXi host."""
        if not self._session_id:
            auth_success = await self._authenticate()
            if not auth_success:
                return {"success": False, "error": "Authentication failed"}

        try:
            url = f"{self._api_base}/vcenter/vm"
            response = requests.get(
                url, headers=self._get_headers(), verify=self._verify_ssl, timeout=10
            )
            response.raise_for_status()
            return {
                "success": True,
                "message": "Connection successful",
                "host": self._host,
            }
        except Exception as e:
            self.logger.error(f"ESXi connection test failed: {e}")
            return {"success": False, "error": str(e)}

