from services.integration_base import Integration
from services.service_registry import service_registry
import logging
import requests
from requests.auth import HTTPBasicAuth
import base64

class BitwardenIntegration(Integration):
    async def async_setup(self):
        self.logger.info("Setting up Bitwarden Integration")

        service_registry.register(
            domain=self.domain,
            service="get_organization",
            service_func=self.get_organization,
            schema={"organization_id": str},
            description="Get organization information"
        )

        service_registry.register(
            domain=self.domain,
            service="create_member",
            service_func=self.create_member,
            schema={"organization_id": str, "email": str, "collections": list},
            description="Create an organization member"
        )

        service_registry.register(
            domain=self.domain,
            service="get_members",
            service_func=self.get_members,
            schema={"organization_id": str},
            description="Get organization members"
        )

        service_registry.register(
            domain=self.domain,
            service="create_collection",
            service_func=self.create_collection,
            schema={"organization_id": str, "name": str},
            description="Create a collection"
        )

        service_registry.register(
            domain=self.domain,
            service="get_collections",
            service_func=self.get_collections,
            schema={"organization_id": str},
            description="Get organization collections"
        )

        return True

    def _get_api_url(self):
        """Get Bitwarden API URL."""
        return self.config.get("api_url", "https://api.bitwarden.com").rstrip("/")

    def _get_auth_token(self):
        """Get Bitwarden API access token."""
        client_id = self.config.get("client_id")
        client_secret = self.config.get("client_secret")
        if not client_id or not client_secret:
            raise ValueError("Bitwarden credentials not configured")

        api_url = self._get_api_url()
        auth_string = f"{client_id}:{client_secret}"
        auth_header = base64.b64encode(auth_string.encode()).decode()

        response = requests.post(
            f"{api_url}/identity/connect/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {auth_header}"
            },
            data={
                "grant_type": "client_credentials",
                "scope": "api.organization"
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["access_token"]

    async def get_organization(self, data: dict):
        """Get organization information."""
        try:
            api_url = self._get_api_url()
            organization_id = data.get("organization_id") or self.config.get("default_organization_id")
            if not organization_id:
                raise ValueError("organization_id required")

            token = self._get_auth_token()
            response = requests.get(
                f"{api_url}/organizations/{organization_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "organization": response.json()}
        except Exception as e:
            self.logger.error(f"Failed to get Bitwarden organization: {e}")
            raise

    async def create_member(self, data: dict):
        """Create an organization member."""
        try:
            api_url = self._get_api_url()
            organization_id = data.get("organization_id") or self.config.get("default_organization_id")
            email = data.get("email")
            collections = data.get("collections", [])

            if not organization_id or not email:
                raise ValueError("organization_id and email required")

            token = self._get_auth_token()
            payload = {
                "emails": [email],
                "collections": collections
            }

            response = requests.post(
                f"{api_url}/organizations/{organization_id}/members",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            self.logger.info(f"Bitwarden member created: {email}")
            return {"success": True, "member": result}
        except Exception as e:
            self.logger.error(f"Failed to create Bitwarden member: {e}")
            raise

    async def get_members(self, data: dict):
        """Get organization members."""
        try:
            api_url = self._get_api_url()
            organization_id = data.get("organization_id") or self.config.get("default_organization_id")
            if not organization_id:
                raise ValueError("organization_id required")

            token = self._get_auth_token()
            response = requests.get(
                f"{api_url}/organizations/{organization_id}/members",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "members": response.json()}
        except Exception as e:
            self.logger.error(f"Failed to get Bitwarden members: {e}")
            raise

    async def create_collection(self, data: dict):
        """Create a collection."""
        try:
            api_url = self._get_api_url()
            organization_id = data.get("organization_id") or self.config.get("default_organization_id")
            name = data.get("name")

            if not organization_id or not name:
                raise ValueError("organization_id and name required")

            token = self._get_auth_token()
            payload = {"name": name}

            response = requests.post(
                f"{api_url}/organizations/{organization_id}/collections",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            self.logger.info(f"Bitwarden collection created: {name}")
            return {"success": True, "collection": result}
        except Exception as e:
            self.logger.error(f"Failed to create Bitwarden collection: {e}")
            raise

    async def get_collections(self, data: dict):
        """Get organization collections."""
        try:
            api_url = self._get_api_url()
            organization_id = data.get("organization_id") or self.config.get("default_organization_id")
            if not organization_id:
                raise ValueError("organization_id required")

            token = self._get_auth_token()
            response = requests.get(
                f"{api_url}/organizations/{organization_id}/collections",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "collections": response.json()}
        except Exception as e:
            self.logger.error(f"Failed to get Bitwarden collections: {e}")
            raise

