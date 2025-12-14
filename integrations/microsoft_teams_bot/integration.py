"""
Microsoft Teams Bot Integration for faneX-ID
Provides Microsoft Teams bot functionality for sending messages.
"""

import logging
from typing import Any, Dict, Optional

from services.integration_base import Integration
from services.service_registry import service_registry
from services.event_bus import event_bus

logger = logging.getLogger(__name__)


class MicrosoftTeamsBotIntegration(Integration):
    """Microsoft Teams bot integration."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app_id: Optional[str] = None
        self._app_password: Optional[str] = None
        self._tenant_id: Optional[str] = None

    async def async_setup(self) -> bool:
        """Set up the Microsoft Teams Bot integration."""
        self.logger.info("Setting up Microsoft Teams Bot Integration")

        # Get configuration
        self._app_id = self.config.get("app_id")
        self._app_password = self.config.get("app_password")
        self._tenant_id = self.config.get("tenant_id")

        if not self._app_id or not self._app_password:
            self.logger.error("Microsoft Teams app_id and app_password are required")
            return False

        # Register services
        self.register_service(
            "send_message",
            self.send_message,
            schema={
                "channel_id": {"type": "string"},
                "message": {"type": "string"},
                "message_type": {"type": "string", "enum": ["text", "card", "adaptive"], "nullable": True},
            },
            description="Send a message to a Teams channel or chat",
        )

        self.register_service(
            "get_bot_status",
            self.get_bot_status,
            schema={"bot_id": {"type": "string", "nullable": True}},
            description="Get the status of the Teams bot",
        )

        self.register_service(
            "register_with_interpreter",
            self.register_with_interpreter,
            schema={"bot_id": {"type": "string"}},
            description="Register this bot with the Bot Interpreter system component",
        )

        # Auto-register with bot interpreter if available
        bot_interpreter = service_registry.get_service("bot_interpreter", "register_bot")
        if bot_interpreter:
            try:
                await bot_interpreter({
                    "bot_id": f"teams_{self._app_id}",
                    "bot_type": "teams",
                    "integration_domain": "microsoft_teams_bot",
                    "config": {"app_id": self._app_id}
                })
                self.logger.info("Bot registered with Bot Interpreter")
            except Exception as e:
                self.logger.warning(f"Failed to auto-register with Bot Interpreter: {e}")

        return True

    async def send_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to a Teams channel or chat."""
        channel_id = data.get("channel_id")
        message = data.get("message")
        message_type = data.get("message_type", "text")

        if not channel_id or not message:
            return {"success": False, "error": "channel_id and message are required"}

        try:
            # In a real implementation, this would use the Microsoft Bot Framework
            # For now, we'll simulate the API call
            self.logger.info(f"Sending message to Teams channel {channel_id}")

            # Emit event
            event_bus.emit("teams.message_sent", {
                "channel_id": channel_id,
                "message": message
            })

            return {
                "success": True,
                "message": "Message sent successfully",
                "channel_id": channel_id
            }
        except Exception as e:
            self.logger.error(f"Failed to send Teams message: {e}")
            return {"success": False, "error": str(e)}

    async def get_bot_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get the status of the Teams bot."""
        try:
            return {
                "success": True,
                "bot_id": self._app_id,
                "status": "active",
                "app_id": self._app_id
            }
        except Exception as e:
            self.logger.error(f"Failed to get bot status: {e}")
            return {"success": False, "error": str(e)}

    async def register_with_interpreter(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register this bot with the Bot Interpreter system component."""
        bot_id = data.get("bot_id")
        if not bot_id:
            return {"success": False, "error": "bot_id is required"}

        bot_interpreter = service_registry.get_service("bot_interpreter", "register_bot")
        if not bot_interpreter:
            return {"success": False, "error": "Bot Interpreter not available"}

        try:
            result = await bot_interpreter({
                "bot_id": bot_id,
                "bot_type": "teams",
                "integration_domain": "microsoft_teams_bot",
                "config": {"app_id": self._app_id}
            })
            return result
        except Exception as e:
            self.logger.error(f"Failed to register with Bot Interpreter: {e}")
            return {"success": False, "error": str(e)}

