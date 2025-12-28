import logging

import requests
from services.integration_base import Integration
from services.service_registry import service_registry


class WebhookGenericIntegration(Integration):
    async def async_setup(self):
        self.logger.info("Setting up Generic Webhook Integration")

        service_registry.register(
            domain=self.domain,
            service="send_webhook",
            service_func=self.send_webhook,
            schema={
                "url": str,
                "method": str,
                "payload": dict,
                "headers": dict
            },
            description="Send a webhook request"
        )

        return True

    async def send_webhook(self, data: dict):
        """Send a webhook request."""
        url = data.get("url") or self.config.get("default_url")
        if not url:
            raise ValueError("webhook URL not provided and no default_url configured")

        method = data.get("method", "POST").upper()
        payload = data.get("payload", {})
        custom_headers = data.get("headers", {})
        timeout = self.config.get("timeout", 30)

        # Merge default headers with custom headers
        headers = self.config.get("default_headers", {}).copy()
        headers.update(custom_headers)

        # Set Content-Type if not specified
        if "Content-Type" not in headers and method in ["POST", "PUT", "PATCH"]:
            headers["Content-Type"] = "application/json"

        try:
            if method == "GET":
                response = requests.get(url, params=payload, headers=headers, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            elif method == "PUT":
                response = requests.put(url, json=payload, headers=headers, timeout=timeout)
            elif method == "PATCH":
                response = requests.patch(url, json=payload, headers=headers, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            self.logger.info(f"Webhook sent to {url} with method {method}")

            return {
                "status": "sent",
                "status_code": response.status_code,
                "response": response.text[:500] if response.text else None
            }
        except Exception as e:
            self.logger.error(f"Failed to send webhook: {e}")
            raise


