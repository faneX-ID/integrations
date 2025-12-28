import base64
import logging

import requests
from requests.auth import HTTPBasicAuth
from services.integration_base import Integration
from services.service_registry import service_registry


class NextcloudIntegration(Integration):
    async def async_setup(self):
        self.logger.info("Setting up Nextcloud Integration")

        service_registry.register(
            domain=self.domain,
            service="upload_file",
            service_func=self.upload_file,
            schema={"remote_path": str, "file_content": str},
            description="Upload a file to Nextcloud"
        )

        service_registry.register(
            domain=self.domain,
            service="create_share",
            service_func=self.create_share,
            schema={"path": str, "share_type": int, "permissions": int},
            description="Create a file share"
        )

        service_registry.register(
            domain=self.domain,
            service="get_user",
            service_func=self.get_user,
            schema={"user_id": str},
            description="Get user information"
        )

        return True

    def _get_auth(self):
        """Get authentication."""
        username = self.config.get("username")
        password = self.config.get("password")
        if not username or not password:
            raise ValueError("Nextcloud credentials not configured")
        return HTTPBasicAuth(username, password)

    def _get_base_url(self):
        """Get base Nextcloud URL."""
        url = self.config.get("server_url", "").rstrip("/")
        if not url:
            raise ValueError("Nextcloud server URL not configured")
        return url

    async def upload_file(self, data: dict):
        """Upload a file to Nextcloud."""
        base_url = self._get_base_url()
        remote_path = data.get("remote_path", "").lstrip("/")
        file_content = data.get("file_content", "")

        if not remote_path:
            raise ValueError("remote_path required")

        # Decode base64 content
        try:
            content = base64.b64decode(file_content)
        except:
            content = file_content.encode() if isinstance(file_content, str) else file_content

        try:
            response = requests.put(
                f"{base_url}/remote.php/dav/files/{self.config.get('username')}/{remote_path}",
                data=content,
                auth=self._get_auth(),
                timeout=30
            )
            response.raise_for_status()
            self.logger.info(f"File uploaded to Nextcloud: {remote_path}")
            return {"success": True, "path": remote_path}
        except Exception as e:
            self.logger.error(f"Failed to upload file to Nextcloud: {e}")
            raise

    async def create_share(self, data: dict):
        """Create a file share."""
        base_url = self._get_base_url()
        path = data.get("path", "")
        share_type = data.get("share_type", 3)  # Default to public link
        permissions = data.get("permissions", 1)

        if not path:
            raise ValueError("path required")

        try:
            response = requests.post(
                f"{base_url}/ocs/v2.php/apps/files_sharing/api/v1/shares",
                params={
                    "path": path,
                    "shareType": share_type,
                    "permissions": permissions
                },
                auth=self._get_auth(),
                headers={"OCS-APIRequest": "true"},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            self.logger.info(f"Nextcloud share created: {path}")
            return {"success": True, "share": result}
        except Exception as e:
            self.logger.error(f"Failed to create Nextcloud share: {e}")
            raise

    async def get_user(self, data: dict):
        """Get user information."""
        base_url = self._get_base_url()
        user_id = data.get("user_id", "")

        if not user_id:
            raise ValueError("user_id required")

        try:
            response = requests.get(
                f"{base_url}/ocs/v2.php/cloud/users/{user_id}",
                auth=self._get_auth(),
                headers={"OCS-APIRequest": "true"},
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "user": response.json()}
        except Exception as e:
            self.logger.error(f"Failed to get Nextcloud user: {e}")
            raise


