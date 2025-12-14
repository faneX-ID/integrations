from services.integration_base import Integration
from services.service_registry import service_registry
import logging

class MicrosoftGraphExchangeIntegration(Integration):
    async def async_setup(self):
        self.logger.info("Setting up Microsoft Graph Exchange Integration")

        # Get Graph base integration
        graph_integration = self.get_dependency("microsoft_graph")
        if not graph_integration:
            self.logger.error("microsoft_graph integration not found. Please install it first.")
            return False

        service_registry.register(
            domain=self.domain,
            service="send_email",
            service_func=self.send_email,
            schema={
                "to": list,
                "subject": str,
                "body": str,
                "cc": list
            },
            description="Send an email via Exchange Online"
        )

        service_registry.register(
            domain=self.domain,
            service="get_messages",
            service_func=self.get_messages,
            schema={"user_id": str, "folder": str, "limit": int},
            description="Get email messages"
        )

        service_registry.register(
            domain=self.domain,
            service="create_calendar_event",
            service_func=self.create_calendar_event,
            schema={
                "subject": str,
                "start": str,
                "end": str,
                "attendees": list
            },
            description="Create a calendar event"
        )

        return True

    def _get_graph_service(self):
        """Get Graph base integration service."""
        return self.get_dependency("microsoft_graph")

    async def send_email(self, data: dict):
        """Send an email via Exchange Online."""
        graph_service = self._get_graph_service()
        if not graph_service:
            raise ValueError("microsoft_graph integration not available")

        to_addresses = data.get("to", [])
        subject = data.get("subject", "")
        body = data.get("body", "")
        cc_addresses = data.get("cc", [])

        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body
                },
                "toRecipients": [{"emailAddress": {"address": addr}} for addr in to_addresses],
                "ccRecipients": [{"emailAddress": {"address": addr}} for addr in cc_addresses] if cc_addresses else []
            }
        }

        user_id = data.get("user_id") or "me"
        result = await graph_service.graph_request({
            "method": "POST",
            "endpoint": f"/users/{user_id}/sendMail",
            "body": message
        })

        return result

    async def get_messages(self, data: dict):
        """Get email messages."""
        graph_service = self._get_graph_service()
        if not graph_service:
            raise ValueError("microsoft_graph integration not available")

        user_id = data.get("user_id") or "me"
        folder = data.get("folder", "inbox")
        limit = data.get("limit", 10)

        result = await graph_service.graph_request({
            "method": "GET",
            "endpoint": f"/users/{user_id}/mailFolders/{folder}/messages",
            "params": {"$top": limit}
        })

        return result

    async def create_calendar_event(self, data: dict):
        """Create a calendar event."""
        graph_service = self._get_graph_service()
        if not graph_service:
            raise ValueError("microsoft_graph integration not available")

        subject = data.get("subject", "")
        start = data.get("start")
        end = data.get("end")
        attendees = data.get("attendees", [])

        event = {
            "subject": subject,
            "start": {
                "dateTime": start,
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end,
                "timeZone": "UTC"
            },
            "attendees": [{"emailAddress": {"address": addr}} for addr in attendees] if attendees else []
        }

        user_id = data.get("user_id") or "me"
        result = await graph_service.graph_request({
            "method": "POST",
            "endpoint": f"/users/{user_id}/calendar/events",
            "body": event
        })

        return result

