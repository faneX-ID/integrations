import logging

import requests
from requests.auth import HTTPBasicAuth
from services.integration_base import Integration
from services.service_registry import service_registry


class JiraIntegration(Integration):
    async def async_setup(self):
        self.logger.info("Setting up Jira Integration")

        service_registry.register(
            domain=self.domain,
            service="create_ticket",
            service_func=self.create_ticket,
            schema={
                "project_key": str,
                "issue_type": str,
                "summary": str,
                "description": str,
                "assignee": str,
                "labels": list
            },
            description="Create a Jira ticket"
        )

        service_registry.register(
            domain=self.domain,
            service="get_ticket",
            service_func=self.get_ticket,
            schema={"ticket_key": str},
            description="Get Jira ticket information"
        )

        service_registry.register(
            domain=self.domain,
            service="update_ticket",
            service_func=self.update_ticket,
            schema={"ticket_key": str, "fields": dict},
            description="Update a Jira ticket"
        )

        return True

    def _get_auth(self):
        """Get authentication for Jira API."""
        username = self.config.get("username")
        api_token = self.config.get("api_token")
        if not username or not api_token:
            raise ValueError("Jira credentials not configured")
        return HTTPBasicAuth(username, api_token)

    def _get_base_url(self):
        """Get base Jira URL."""
        server_url = self.config.get("server_url", "").rstrip("/")
        if not server_url:
            raise ValueError("Jira server_url not configured")
        return server_url

    async def create_ticket(self, data: dict):
        """Create a new Jira ticket."""
        base_url = self._get_base_url()
        project_key = data.get("project_key") or self.config.get("default_project")
        if not project_key:
            raise ValueError("project_key required")

        issue_data = {
            "fields": {
                "project": {"key": project_key},
                "summary": data.get("summary", ""),
                "description": data.get("description", ""),
                "issuetype": {"name": data.get("issue_type", "Task")}
            }
        }

        if data.get("assignee"):
            issue_data["fields"]["assignee"] = {"name": data["assignee"]}

        if data.get("labels"):
            issue_data["fields"]["labels"] = data["labels"]

        try:
            response = requests.post(
                f"{base_url}/rest/api/3/issue",
                json=issue_data,
                auth=self._get_auth(),
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            ticket_key = result.get("key")
            self.logger.info(f"Jira ticket created: {ticket_key}")
            return {"status": "created", "ticket_key": ticket_key, "url": f"{base_url}/browse/{ticket_key}"}
        except Exception as e:
            self.logger.error(f"Failed to create Jira ticket: {e}")
            raise

    async def get_ticket(self, data: dict):
        """Get ticket information."""
        base_url = self._get_base_url()
        ticket_key = data.get("ticket_key")
        if not ticket_key:
            raise ValueError("ticket_key required")

        try:
            response = requests.get(
                f"{base_url}/rest/api/3/issue/{ticket_key}",
                auth=self._get_auth(),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return {
                "key": result.get("key"),
                "summary": result.get("fields", {}).get("summary"),
                "status": result.get("fields", {}).get("status", {}).get("name"),
                "assignee": result.get("fields", {}).get("assignee", {}).get("displayName") if result.get("fields", {}).get("assignee") else None
            }
        except Exception as e:
            self.logger.error(f"Failed to get Jira ticket: {e}")
            raise

    async def update_ticket(self, data: dict):
        """Update a Jira ticket."""
        base_url = self._get_base_url()
        ticket_key = data.get("ticket_key")
        fields = data.get("fields", {})

        if not ticket_key:
            raise ValueError("ticket_key required")

        update_data = {"fields": fields}

        try:
            response = requests.put(
                f"{base_url}/rest/api/3/issue/{ticket_key}",
                json=update_data,
                auth=self._get_auth(),
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            self.logger.info(f"Jira ticket updated: {ticket_key}")
            return {"status": "updated", "ticket_key": ticket_key}
        except Exception as e:
            self.logger.error(f"Failed to update Jira ticket: {e}")
            raise


