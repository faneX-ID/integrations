from services.integration_base import Integration
from services.service_registry import service_registry
import logging
import requests
import json

class MicrosoftTeamsIntegration(Integration):
    async def async_setup(self):
        self.logger.info("Setting up Microsoft Teams Integration")

        service_registry.register(
            domain=self.domain,
            service="send_message",
            service_func=self.send_message,
            schema={
                "title": str,
                "text": str,
                "theme_color": str
            },
            description="Send a message to Teams"
        )

        service_registry.register(
            domain=self.domain,
            service="send_card",
            service_func=self.send_card,
            schema={
                "title": str,
                "sections": list
            },
            description="Send an adaptive card to Teams"
        )

        return True

    async def send_message(self, data: dict):
        """Send a message to Microsoft Teams."""
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            raise ValueError("webhook_url not configured")

        title = data.get("title", "Notification")
        text = data.get("text", "")
        theme_color = data.get("theme_color") or self.config.get("default_theme_color", "0078D4")

        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": title,
            "themeColor": theme_color,
            "title": title,
            "text": text
        }

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            self.logger.info("Teams message sent")
            return {"status": "sent"}
        except Exception as e:
            self.logger.error(f"Failed to send Teams message: {e}")
            raise

    async def send_card(self, data: dict):
        """Send an adaptive card to Microsoft Teams."""
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            raise ValueError("webhook_url not configured")

        title = data.get("title", "Card")
        sections = data.get("sections", [])

        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": title,
                                "weight": "Bolder",
                                "size": "Large"
                            }
                        ] + sections
                    }
                }
            ]
        }

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            self.logger.info("Teams card sent")
            return {"status": "sent"}
        except Exception as e:
            self.logger.error(f"Failed to send Teams card: {e}")
            raise
