from services.integration_base import Integration
from services.service_registry import service_registry
import logging
import requests

class SoSafeIntegration(Integration):
    async def async_setup(self):
        self.logger.info("Setting up SoSafe Integration")
        self.logger.warning("SoSafe API documentation is limited. This integration provides basic functionality.")

        service_registry.register(
            domain=self.domain,
            service="report_phishing",
            service_func=self.report_phishing,
            schema={
                "url": str,
                "sender": str,
                "description": str
            },
            description="Report a phishing attempt via SoSafe"
        )

        service_registry.register(
            domain=self.domain,
            service="get_user_status",
            service_func=self.get_user_status,
            schema={"user_email": str},
            description="Get user security awareness status"
        )

        return True

    def _get_headers(self):
        """Get API headers."""
        api_key = self.config.get("api_key")
        if not api_key:
            raise ValueError("SoSafe API key not configured")
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _get_base_url(self):
        """Get base SoSafe API URL."""
        url = self.config.get("api_url", "").rstrip("/")
        if not url:
            raise ValueError("SoSafe API URL not configured")
        return url

    async def report_phishing(self, data: dict):
        """Report a phishing attempt via SoSafe."""
        base_url = self._get_base_url()
        url = data.get("url", "")
        sender = data.get("sender")
        description = data.get("description", "")

        if not url:
            raise ValueError("url required")

        # Note: SoSafe API structure may vary - this is a best-effort implementation
        report_data = {
            "url": url,
            "sender": sender,
            "description": description
        }

        try:
            # SoSafe phishing report endpoint (structure may need adjustment)
            response = requests.post(
                f"{base_url}/api/phishing/report",
                json=report_data,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            self.logger.info(f"Phishing report sent to SoSafe: {url}")
            return {"success": True, "report_id": response.json().get("id")}
        except Exception as e:
            self.logger.error(f"Failed to report phishing to SoSafe: {e}")
            # Try alternative endpoint structure
            self.logger.warning("SoSafe API endpoint may need adjustment. Please check SoSafe documentation.")
            raise

    async def get_user_status(self, data: dict):
        """Get user security awareness status."""
        base_url = self._get_base_url()
        user_email = data.get("user_email", "")
        if not user_email:
            raise ValueError("user_email required")

        try:
            # SoSafe user status endpoint (structure may need adjustment)
            response = requests.get(
                f"{base_url}/api/users/{user_email}/status",
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "status": response.json()}
        except Exception as e:
            self.logger.error(f"Failed to get SoSafe user status: {e}")
            self.logger.warning("SoSafe API endpoint may need adjustment. Please check SoSafe documentation.")
            raise

