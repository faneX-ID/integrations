import json
import logging

import requests
from services.integration_base import Integration
from services.service_registry import service_registry


class SlackIntegration(Integration):
    async def async_setup(self):
        self.logger.info("Setting up Slack Integration")

        # Register services
        service_registry.register(
            domain=self.domain,
            service="send_message",
            service_func=self.send_message,
            schema={
                "channel": str,
                "message": str,
                "username": str,
                "icon_emoji": str
            },
            description="Send a message to Slack"
        )

        service_registry.register(
            domain=self.domain,
            service="send_alert",
            service_func=self.send_alert,
            schema={
                "channel": str,
                "title": str,
                "message": str,
                "color": str
            },
            description="Send an alert to Slack"
        )

        return True

    async def send_message(self, data: dict):
        """Send a simple message to Slack."""
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            raise ValueError("webhook_url not configured")

        channel = data.get("channel") or self.config.get("default_channel", "#general")
        message = data.get("message", "")
        username = data.get("username", "faneX-ID")
        icon_emoji = data.get("icon_emoji", ":robot_face:")

        payload = {
            "channel": channel,
            "text": message,
            "username": username,
            "icon_emoji": icon_emoji
        }

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            self.logger.info(f"Slack message sent to {channel}")
            return {"status": "sent", "channel": channel}
        except Exception as e:
            self.logger.error(f"Failed to send Slack message: {e}")
            raise

    async def send_alert(self, data: dict):
        """Send a formatted alert to Slack."""
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            raise ValueError("webhook_url not configured")

        channel = data.get("channel") or self.config.get("default_channel", "#alerts")
        title = data.get("title", "Alert")
        message = data.get("message", "")
        color = data.get("color", "warning")

        payload = {
            "channel": channel,
            "attachments": [
                {
                    "color": color,
                    "title": title,
                    "text": message,
                    "footer": "faneX-ID",
                    "ts": int(__import__("time").time())
                }
            ]
        }

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            self.logger.info(f"Slack alert sent to {channel}")
            return {"status": "sent", "channel": channel, "color": color}
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {e}")
            raise


