"""
SharePoint On-Premises Integration for faneX-ID.
Provides integration with SharePoint On-Premises via REST API.
"""

import base64
import logging
from typing import Any, Dict, Optional

import requests
from requests_ntlm import HttpNtlmAuth
from services.integration_base import Integration
from services.service_registry import service_registry

logger = logging.getLogger(__name__)


class SharePointOnPremIntegration(Integration):
    """SharePoint On-Premises integration."""

    async def async_setup(self) -> bool:
        self.logger.info("Setting up SharePoint On-Premises Integration")

        service_registry.register(
            domain=self.domain,
            service="get_site",
            service_func=self.get_site,
            schema={"site_url": str},
            description="Get SharePoint site information",
        )

        service_registry.register(
            domain=self.domain,
            service="get_list",
            service_func=self.get_list,
            schema={"site_url": str, "list_name": str},
            description="Get SharePoint list",
        )

        service_registry.register(
            domain=self.domain,
            service="create_list_item",
            service_func=self.create_list_item,
            schema={"site_url": str, "list_name": str, "fields": dict},
            description="Create a list item",
        )

        service_registry.register(
            domain=self.domain,
            service="upload_file",
            service_func=self.upload_file,
            schema={
                "site_url": str,
                "library_name": str,
                "file_path": str,
                "file_content": str,
            },
            description="Upload a file to SharePoint",
        )

        service_registry.register(
            domain=self.domain,
            service="set_permissions",
            service_func=self.set_permissions,
            schema={
                "site_url": str,
                "item_path": str,
                "user": str,
                "permission_level": str,
            },
            description="Set permissions on a SharePoint item",
        )

        return True

    def _get_auth(self):
        """Get NTLM authentication."""
        username = self.config.get("username")
        password = self.config.get("password")
        if not username or not password:
            raise ValueError("SharePoint credentials not configured")
        return HttpNtlmAuth(username, password)

    def _get_base_url(self) -> str:
        """Get base SharePoint server URL."""
        url = self.config.get("server_url", "").rstrip("/")
        if not url:
            raise ValueError("SharePoint server URL not configured")
        return url

    async def get_site(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get SharePoint site information."""
        try:
            site_url = data.get("site_url") or self.config.get("default_site")
            if not site_url:
                return {"success": False, "error": "site_url required"}

            url = f"{site_url}/_api/web"
            response = requests.get(url, auth=self._get_auth(), timeout=30)
            response.raise_for_status()

            return {"success": True, "site": response.json()}
        except Exception as e:
            self.logger.error(f"Failed to get SharePoint site: {e}")
            return {"success": False, "error": str(e)}

    async def get_list(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get SharePoint list."""
        try:
            site_url = data.get("site_url") or self.config.get("default_site")
            list_name = data.get("list_name")
            if not site_url or not list_name:
                return {"success": False, "error": "site_url and list_name required"}

            url = f"{site_url}/_api/web/lists/getbytitle('{list_name}')"
            response = requests.get(url, auth=self._get_auth(), timeout=30)
            response.raise_for_status()

            return {"success": True, "list": response.json()}
        except Exception as e:
            self.logger.error(f"Failed to get SharePoint list: {e}")
            return {"success": False, "error": str(e)}

    async def create_list_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a list item."""
        try:
            site_url = data.get("site_url") or self.config.get("default_site")
            list_name = data.get("list_name")
            fields = data.get("fields", {})
            if not site_url or not list_name:
                return {"success": False, "error": "site_url and list_name required"}

            # Get form digest value
            digest_url = f"{site_url}/_api/contextinfo"
            digest_response = requests.post(
                digest_url, auth=self._get_auth(), timeout=30
            )
            digest_response.raise_for_status()
            digest = digest_response.json()["d"]["GetContextWebInformation"][
                "FormDigestValue"
            ]

            # Fetch the list's ListItemEntityTypeFullName to get the correct type name
            list_url = f"{site_url}/_api/web/lists/getbytitle('{list_name}')?$select=ListItemEntityTypeFullName"
            list_response = requests.get(list_url, auth=self._get_auth(), timeout=30)
            list_response.raise_for_status()
            list_data = list_response.json()
            entity_type = list_data["d"]["ListItemEntityTypeFullName"]

            url = f"{site_url}/_api/web/lists/getbytitle('{list_name}')/items"
            headers = {
                "Accept": "application/json;odata=verbose",
                "Content-Type": "application/json;odata=verbose",
                "X-RequestDigest": digest,
            }

            payload = {"__metadata": {"type": entity_type}, **fields}

            response = requests.post(
                url, json=payload, headers=headers, auth=self._get_auth(), timeout=30
            )
            response.raise_for_status()

            self.logger.info(f"SharePoint list item created in {list_name}")
            return {"success": True, "item": response.json()}
        except Exception as e:
            self.logger.error(f"Failed to create SharePoint list item: {e}")
            return {"success": False, "error": str(e)}

    async def upload_file(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a file to SharePoint."""
        try:
            site_url = data.get("site_url") or self.config.get("default_site")
            library_name = data.get("library_name")
            file_path = data.get("file_path")
            file_content = data.get("file_content")

            if not site_url or not library_name or not file_path:
                return {
                    "success": False,
                    "error": "site_url, library_name, and file_path required",
                }

            # Decode base64 content if provided
            if file_content:
                try:
                    content = base64.b64decode(file_content)
                except:
                    content = (
                        file_content.encode()
                        if isinstance(file_content, str)
                        else file_content
                    )
            else:
                return {"success": False, "error": "file_content required"}

            # Get form digest
            digest_url = f"{site_url}/_api/contextinfo"
            digest_response = requests.post(
                digest_url, auth=self._get_auth(), timeout=30
            )
            digest_response.raise_for_status()
            digest = digest_response.json()["d"]["GetContextWebInformation"][
                "FormDigestValue"
            ]

            url = f"{site_url}/_api/web/GetFolderByServerRelativeUrl('{library_name}')/Files/add(url='{file_path}',overwrite=true)"
            headers = {
                "Accept": "application/json;odata=verbose",
                "X-RequestDigest": digest,
            }

            response = requests.post(
                url, data=content, headers=headers, auth=self._get_auth(), timeout=30
            )
            response.raise_for_status()

            self.logger.info(f"File uploaded to SharePoint: {file_path}")
            return {"success": True, "file": response.json()}
        except Exception as e:
            self.logger.error(f"Failed to upload file to SharePoint: {e}")
            return {"success": False, "error": str(e)}

    async def set_permissions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Set permissions on a SharePoint item."""
        try:
            site_url = data.get("site_url") or self.config.get("default_site")
            item_path = data.get("item_path")
            user = data.get("user")
            permission_level = data.get("permission_level")

            if not site_url or not item_path or not user or not permission_level:
                return {"success": False, "error": "All parameters required"}

            # This is a simplified version - full implementation would require more complex CSOM calls
            # For now, we'll use REST API where possible
            self.logger.warning("set_permissions requires CSOM for full functionality")
            return {
                "success": False,
                "error": "Full permission management requires CSOM implementation",
            }
        except Exception as e:
            self.logger.error(f"Failed to set SharePoint permissions: {e}")
            return {"success": False, "error": str(e)}



