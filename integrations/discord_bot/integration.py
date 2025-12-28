"""
Discord Bot Integration for faneX-ID
Provides Discord bot functionality for sending messages.
"""

import logging
from typing import Any, Dict, Optional

try:
    import discord
    from discord.ext import commands
except ImportError:
    discord = None
    commands = None

from services.event_bus import event_bus
from services.integration_base import Integration
from services.service_registry import service_registry

logger = logging.getLogger(__name__)


class DiscordBotIntegration(Integration):
    """Discord bot integration."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bot: Optional[Any] = None
        self._bot_token: Optional[str] = None
        self._intents: Optional[Any] = None

    async def async_setup(self) -> bool:
        """Set up the Discord Bot integration."""
        self.logger.info("Setting up Discord Bot Integration")

        if discord is None:
            self.logger.error("discord.py library not installed")
            return False

        # Get configuration
        self._bot_token = self.config.get("bot_token")
        intents_config = self.config.get("intents", {})

        if not self._bot_token:
            self.logger.error("Discord bot_token is required")
            return False

        try:
            # Configure intents
            intents = discord.Intents.default()
            if intents_config.get("guilds", True):
                intents.guilds = True
            if intents_config.get("messages", True):
                intents.messages = True
            if intents_config.get("message_content", False):
                intents.message_content = True

            self._intents = intents

            # Initialize bot
            self._bot = commands.Bot(command_prefix='!', intents=intents)
            
            # Test connection (bot will connect in background)
            @self._bot.event
            async def on_ready():
                self.logger.info(f"Discord bot connected: {self._bot.user}")

            # Start bot in background
            # Note: In production, this should be properly managed
            import asyncio
            asyncio.create_task(self._bot.start(self._bot_token))

            # Register services
            self.register_service(
                "send_message",
                self.send_message,
                schema={
                    "channel_id": {"type": "string"},
                    "message": {"type": "string"},
                    "embed": {"type": "object", "nullable": True},
                    "reply_to_message_id": {"type": "string", "nullable": True},
                },
                description="Send a message to a Discord channel or DM",
            )

            self.register_service(
                "get_bot_status",
                self.get_bot_status,
                schema={"bot_id": {"type": "string", "nullable": True}},
                description="Get the status of the Discord bot",
            )

            self.register_service(
                "register_with_interpreter",
                self.register_with_interpreter,
                schema={"bot_id": {"type": "string"}},
                description="Register this bot with the Bot Interpreter system component",
            )

            # Auto-register with bot interpreter if available
            bot_interpreter = service_registry.get_service("bot_interpreter", "register_bot")
            if bot_interpreter and self._bot.user:
                try:
                    await bot_interpreter({
                        "bot_id": f"discord_{self._bot.user.id}",
                        "bot_type": "discord",
                        "integration_domain": "discord_bot",
                        "config": {"bot_token": self._bot_token}
                    })
                    self.logger.info("Bot registered with Bot Interpreter")
                except Exception as e:
                    self.logger.warning(f"Failed to auto-register with Bot Interpreter: {e}")

            return True
        except Exception as e:
            self.logger.error(f"Failed to set up Discord bot: {e}")
            return False

    async def send_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to a Discord channel or DM."""
        if not self._bot or not self._bot.is_ready():
            return {"success": False, "error": "Bot not initialized or not ready"}

        channel_id = data.get("channel_id")
        message = data.get("message")
        embed_data = data.get("embed")
        reply_to_message_id = data.get("reply_to_message_id")

        if not channel_id or not message:
            return {"success": False, "error": "channel_id and message are required"}

        try:
            channel = self._bot.get_channel(int(channel_id))
            if not channel:
                return {"success": False, "error": f"Channel {channel_id} not found"}

            # Build message content
            content = message
            embed = None
            if embed_data:
                embed = discord.Embed.from_dict(embed_data)

            # Send message
            if reply_to_message_id:
                reference = discord.MessageReference(message_id=int(reply_to_message_id), channel_id=int(channel_id))
                sent_message = await channel.send(content=content, embed=embed, reference=reference)
            else:
                sent_message = await channel.send(content=content, embed=embed)

            # Emit event
            event_bus.emit("discord.message_sent", {
                "channel_id": channel_id,
                "message_id": str(sent_message.id)
            })

            return {
                "success": True,
                "message_id": str(sent_message.id),
                "channel_id": channel_id
            }
        except Exception as e:
            self.logger.error(f"Failed to send Discord message: {e}")
            return {"success": False, "error": str(e)}

    async def get_bot_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get the status of the Discord bot."""
        if not self._bot:
            return {"success": False, "error": "Bot not initialized"}

        try:
            if not self._bot.user:
                return {"success": False, "error": "Bot not connected"}

            return {
                "success": True,
                "bot_id": str(self._bot.user.id),
                "username": self._bot.user.name,
                "discriminator": self._bot.user.discriminator,
                "status": "online" if self._bot.is_ready() else "offline",
                "guilds": len(self._bot.guilds) if self._bot.is_ready() else 0
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
                "bot_type": "discord",
                "integration_domain": "discord_bot",
                "config": {"bot_token": self._bot_token}
            })
            return result
        except Exception as e:
            self.logger.error(f"Failed to register with Bot Interpreter: {e}")
            return {"success": False, "error": str(e)}

