"""
Slack Bot Integration for faneX-ID
Provides Slack bot functionality for sending messages.
"""

import logging
from typing import Any, Dict, Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from services.integration_base import Integration
from services.service_registry import service_registry
from services.event_bus import event_bus

logger = logging.getLogger(__name__)


class SlackBotIntegration(Integration):
    """Slack bot integration."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client: Optional[WebClient] = None
        self._bot_token: Optional[str] = None
        self._app_token: Optional[str] = None

    async def async_setup(self) -> bool:
        """Set up the Slack Bot integration."""
        self.logger.info("Setting up Slack Bot Integration")

        # Get configuration
        self._bot_token = self.config.get("bot_token")
        self._app_token = self.config.get("app_token")

        if not self._bot_token:
            self.logger.error("Slack bot_token is required")
            return False

        try:
            # Initialize Slack client
            self._client = WebClient(token=self._bot_token)
            
            # Test connection
            auth_test = self._client.auth_test()
            self.logger.info(f"Slack bot connected: {auth_test['user']}")

            # Register services
            self.register_service(
                "send_message",
                self.send_message,
                schema={
                    "channel": {"type": "string"},
                    "message": {"type": "string"},
                    "thread_ts": {"type": "string", "nullable": True},
                    "blocks": {"type": "array", "nullable": True},
                },
                description="Send a message to a Slack channel or DM",
            )

            self.register_service(
                "get_bot_status",
                self.get_bot_status,
                schema={"bot_id": {"type": "string", "nullable": True}},
                description="Get the status of the Slack bot",
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
                        "bot_id": f"slack_{auth_test['user_id']}",
                        "bot_type": "slack",
                        "integration_domain": "slack_bot",
                        "config": {"bot_token": self._bot_token}
                    })
                    self.logger.info("Bot registered with Bot Interpreter")
                except Exception as e:
                    self.logger.warning(f"Failed to auto-register with Bot Interpreter: {e}")

            return True
        except SlackApiError as e:
            self.logger.error(f"Failed to set up Slack bot: {e}")
            return False

    async def send_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to a Slack channel or DM."""
        if not self._client:
            return {"success": False, "error": "Client not initialized"}

        channel = data.get("channel")
        message = data.get("message")
        thread_ts = data.get("thread_ts")
        blocks = data.get("blocks")

        if not channel or not message:
            return {"success": False, "error": "channel and message are required"}

        try:
            result = self._client.chat_postMessage(
                channel=channel,
                text=message,
                thread_ts=thread_ts,
                blocks=blocks
            )

            # Emit event
            event_bus.emit("slack.message_sent", {
                "channel": channel,
                "ts": result["ts"]
            })

            return {
                "success": True,
                "ts": result["ts"],
                "channel": result["channel"]
            }
        except SlackApiError as e:
            self.logger.error(f"Failed to send Slack message: {e}")
            return {"success": False, "error": str(e)}

    async def get_bot_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get the status of the Slack bot."""
        if not self._client:
            return {"success": False, "error": "Client not initialized"}

        try:
            auth_test = self._client.auth_test()
            return {
                "success": True,
                "bot_id": auth_test["user_id"],
                "user": auth_test["user"],
                "team": auth_test["team"],
                "status": "active"
            }
        except SlackApiError as e:
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
                "bot_type": "slack",
                "integration_domain": "slack_bot",
                "config": {"bot_token": self._bot_token}
            })
            return result
        except Exception as e:
            self.logger.error(f"Failed to register with Bot Interpreter: {e}")
            return {"success": False, "error": str(e)}

