"""
Vaultwarden Helper Integration for faneX-ID.
This is a helper integration that references the bitwarden integration.
Vaultwarden uses a Bitwarden-compatible API, so all functionality
is provided by the bitwarden integration.
"""
import logging

from services.integration_base import Integration
from services.service_registry import service_registry


class VaultwardenIntegration(Integration):
    async def async_setup(self):
        self.logger.info("Setting up Vaultwarden Helper Integration")
        self.logger.info("Vaultwarden is a helper integration. All functionality is provided by the bitwarden integration.")
        self.logger.info("Please configure the bitwarden integration with your Vaultwarden server URL.")

        # Helper integrations don't expose services directly
        # They redirect to the referenced integration
        return True


