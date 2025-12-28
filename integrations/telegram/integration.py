"""
Telegram Bot Integration for faneX-ID
Provides Telegram bot functionality for sending and receiving messages.
"""

import logging
from typing import Any, Dict, Optional

from services.event_bus import event_bus
from services.integration_base import Integration
from services.service_registry import service_registry
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramIntegration(Integration):
    """Telegram bot integration."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bot: Optional[Bot] = None
        self._bot_token: Optional[str] = None
        self._webhook_url: Optional[str] = None

    async def async_setup(self) -> bool:
        """Set up the Telegram integration."""
        self.logger.info("Setting up Telegram Integration")

        # Get configuration
        self._bot_token = self.config.get("bot_token")
        self._webhook_url = self.config.get("webhook_url")

        if not self._bot_token:
            self.logger.error("Telegram bot_token is required")
            return False

        try:
            # Initialize bot
            self._bot = Bot(token=self._bot_token)
            
            # Test connection
            bot_info = await self._bot.get_me()
            self.logger.info(f"Telegram bot connected: @{bot_info.username}")

            # Register services
            self.register_service(
                "send_message",
                self.send_message,
                schema={
                    "chat_id": {"type": "string"},
                    "message": {"type": "string"},
                    "parse_mode": {"type": "string", "enum": ["HTML", "Markdown", "MarkdownV2"], "nullable": True},
                    "reply_to_message_id": {"type": "integer", "nullable": True},
                },
                description="Send a message through Telegram",
            )

            self.register_service(
                "get_bot_status",
                self.get_bot_status,
                schema={"bot_id": {"type": "string", "nullable": True}},
                description="Get the status of the Telegram bot",
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
                        "bot_id": f"telegram_{bot_info.id}",
                        "bot_type": "telegram",
                        "integration_domain": "telegram",
                        "config": {"bot_token": self._bot_token}
                    })
                    self.logger.info("Bot registered with Bot Interpreter")
                except Exception as e:
                    self.logger.warning(f"Failed to auto-register with Bot Interpreter: {e}")

            return True
        except TelegramError as e:
            self.logger.error(f"Failed to set up Telegram bot: {e}")
            return False

    async def send_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message through Telegram."""
        if not self._bot:
            return {"success": False, "error": "Bot not initialized"}

        chat_id = data.get("chat_id")
        message = data.get("message")
        parse_mode = data.get("parse_mode")
        reply_to_message_id = data.get("reply_to_message_id")

        if not chat_id or not message:
            return {"success": False, "error": "chat_id and message are required"}

        try:
            result = await self._bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode,
                reply_to_message_id=reply_to_message_id
            )

            # Emit event
            event_bus.emit("telegram.message_sent", {
                "chat_id": chat_id,
                "message_id": result.message_id
            })

            return {
                "success": True,
                "message_id": result.message_id,
                "chat_id": result.chat.id
            }
        except TelegramError as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            return {"success": False, "error": str(e)}

    async def get_bot_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get the status of the Telegram bot."""
        if not self._bot:
            return {"success": False, "error": "Bot not initialized"}

        try:
            bot_info = await self._bot.get_me()
            return {
                "success": True,
                "bot_id": bot_info.id,
                "username": bot_info.username,
                "first_name": bot_info.first_name,
                "is_bot": bot_info.is_bot,
                "status": "active"
            }
        except TelegramError as e:
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
                "bot_type": "telegram",
                "integration_domain": "telegram",
                "config": {"bot_token": self._bot_token}
            })
            return result
        except Exception as e:
            self.logger.error(f"Failed to register with Bot Interpreter: {e}")
            return {"success": False, "error": str(e)}

