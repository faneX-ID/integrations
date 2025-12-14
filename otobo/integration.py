from services.integration_base import Integration
from services.service_registry import service_registry
import logging
import requests
from requests.auth import HTTPBasicAuth

class OtoboIntegration(Integration):
    async def async_setup(self):
        self.logger.info("Setting up Otobo Integration")

        service_registry.register(
            domain=self.domain,
            service="create_ticket",
            service_func=self.create_ticket,
            schema={
                "title": str,
                "queue": str,
                "priority": str,
                "state": str,
                "customer_user": str,
                "article": dict
            },
            description="Create a new ticket"
        )

        service_registry.register(
            domain=self.domain,
            service="get_ticket",
            service_func=self.get_ticket,
            schema={"ticket_id": int},
            description="Get ticket information"
        )

        service_registry.register(
            domain=self.domain,
            service="update_ticket",
            service_func=self.update_ticket,
            schema={"ticket_id": int, "fields": dict},
            description="Update a ticket"
        )

        service_registry.register(
            domain=self.domain,
            service="add_article",
            service_func=self.add_article,
            schema={"ticket_id": int, "subject": str, "body": str},
            description="Add an article to a ticket"
        )

        return True

    def _get_auth(self):
        """Get authentication for Otobo API."""
        username = self.config.get("username")
        password = self.config.get("password")
        if not username or not password:
            raise ValueError("Otobo credentials not configured")
        return HTTPBasicAuth(username, password)

    def _get_base_url(self):
        """Get base Otobo URL."""
        url = self.config.get("server_url", "").rstrip("/")
        if not url:
            raise ValueError("Otobo server URL not configured")
        return url

    async def create_ticket(self, data: dict):
        """Create a new ticket."""
        base_url = self._get_base_url()
        queue = data.get("queue") or self.config.get("default_queue")
        if not queue:
            raise ValueError("queue required")

        ticket_data = {
            "Title": data.get("title", ""),
            "Queue": queue,
            "Priority": data.get("priority", "3 normal"),
            "State": data.get("state", "new"),
            "CustomerUser": data.get("customer_user", ""),
            "Article": data.get("article", {
                "Subject": data.get("title", ""),
                "Body": ""
            })
        }

        try:
            response = requests.post(
                f"{base_url}/api/v1.0/tickets",
                json=ticket_data,
                auth=self._get_auth(),
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            ticket_id = result.get("TicketID")
            self.logger.info(f"Otobo ticket created: {ticket_id}")
            return {"success": True, "ticket_id": ticket_id, "ticket_number": result.get("TicketNumber")}
        except Exception as e:
            self.logger.error(f"Failed to create Otobo ticket: {e}")
            raise

    async def get_ticket(self, data: dict):
        """Get ticket information."""
        base_url = self._get_base_url()
        ticket_id = data.get("ticket_id")
        if not ticket_id:
            raise ValueError("ticket_id required")

        try:
            response = requests.get(
                f"{base_url}/api/v1.0/tickets/{ticket_id}",
                auth=self._get_auth(),
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "ticket": response.json()}
        except Exception as e:
            self.logger.error(f"Failed to get Otobo ticket: {e}")
            raise

    async def update_ticket(self, data: dict):
        """Update a ticket."""
        base_url = self._get_base_url()
        ticket_id = data.get("ticket_id")
        fields = data.get("fields", {})

        if not ticket_id:
            raise ValueError("ticket_id required")

        try:
            response = requests.patch(
                f"{base_url}/api/v1.0/tickets/{ticket_id}",
                json=fields,
                auth=self._get_auth(),
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            self.logger.info(f"Otobo ticket updated: {ticket_id}")
            return {"success": True, "ticket_id": ticket_id}
        except Exception as e:
            self.logger.error(f"Failed to update Otobo ticket: {e}")
            raise

    async def add_article(self, data: dict):
        """Add an article to a ticket."""
        base_url = self._get_base_url()
        ticket_id = data.get("ticket_id")
        subject = data.get("subject", "")
        body = data.get("body", "")

        if not ticket_id:
            raise ValueError("ticket_id required")

        article_data = {
            "Subject": subject,
            "Body": body,
            "ArticleType": "note"
        }

        try:
            response = requests.post(
                f"{base_url}/api/v1.0/tickets/{ticket_id}/articles",
                json=article_data,
                auth=self._get_auth(),
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            self.logger.info(f"Article added to Otobo ticket: {ticket_id}")
            return {"success": True, "article_id": result.get("ArticleID")}
        except Exception as e:
            self.logger.error(f"Failed to add article to Otobo ticket: {e}")
            raise

