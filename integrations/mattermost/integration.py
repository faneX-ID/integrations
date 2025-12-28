import logging

import requests
from services.integration_base import Integration
from services.service_registry import service_registry


class MattermostIntegration(Integration):
    async def async_setup(self):
        self.logger.info("Setting up Mattermost Integration")

        service_registry.register(
            domain=self.domain,
            service="send_message",
            service_func=self.send_message,
            schema={"channel_id": str, "message": str},
            description="Send a message to a channel"
        )

        service_registry.register(
            domain=self.domain,
            service="create_channel",
            service_func=self.create_channel,
            schema={"name": str, "display_name": str, "type": str},
            description="Create a channel"
        )

        service_registry.register(
            domain=self.domain,
            service="get_user",
            service_func=self.get_user,
            schema={"user_id": str},
            description="Get user information"
        )

        return True

    def _get_headers(self):
        """Get API headers."""
        api_token = self.config.get("api_token")
        if not api_token:
            raise ValueError("Mattermost API token not configured")
        return {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def _get_base_url(self):
        """Get base Mattermost URL."""
        url = self.config.get("server_url", "").rstrip("/")
        if not url:
            raise ValueError("Mattermost server URL not configured")
        return url

    async def send_message(self, data: dict):
        """Send a message to a channel."""
        base_url = self._get_base_url()
        channel_id = data.get("channel_id", "")
        message = data.get("message", "")

        if not channel_id or not message:
            raise ValueError("channel_id and message required")

        post_data = {
            "channel_id": channel_id,
            "message": message
        }

        try:
            response = requests.post(
                f"{base_url}/api/v4/posts",
                json=post_data,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            self.logger.info(f"Mattermost message sent to channel: {channel_id}")
            return {"success": True, "post_id": result.get("id")}
        except Exception as e:
            self.logger.error(f"Failed to send Mattermost message: {e}")
            raise

    async def create_channel(self, data: dict):
        """Create a channel."""
        base_url = self._get_base_url()
        name = data.get("name", "")
        display_name = data.get("display_name", "")
        channel_type = data.get("type", "P")

        if not name:
            raise ValueError("name required")

        channel_data = {
            "name": name,
            "display_name": display_name or name,
            "type": channel_type
        }

        try:
            response = requests.post(
                f"{base_url}/api/v4/channels",
                json=channel_data,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            self.logger.info(f"Mattermost channel created: {name}")
            return {"success": True, "channel_id": result.get("id")}
        except Exception as e:
            self.logger.error(f"Failed to create Mattermost channel: {e}")
            raise

    async def get_user(self, data: dict):
        """Get user information."""
        base_url = self._get_base_url()
        user_id = data.get("user_id", "")

        if not user_id:
            raise ValueError("user_id required")

        try:
            response = requests.get(
                f"{base_url}/api/v4/users/{user_id}",
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "user": response.json()}
        except Exception as e:
            self.logger.error(f"Failed to get Mattermost user: {e}")
            raise


