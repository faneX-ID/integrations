"""
Exchange On-Premises Integration for faneX-ID.
Provides integration with Exchange On-Premises via EWS.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from services.integration_base import Integration
from services.service_registry import service_registry

logger = logging.getLogger(__name__)

try:
    from exchangelib import (
        Account,
        CalendarItem,
        Credentials,
        EWSDateTime,
        EWSTimeZone,
        Mailbox,
        Message,
    )

    EXCHANGELIB_AVAILABLE = True
except ImportError:
    EXCHANGELIB_AVAILABLE = False
    logger.warning(
        "exchangelib not available. Exchange On-Premises integration will not work."
    )


class ExchangeOnPremIntegration(Integration):
    """Exchange On-Premises integration."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account: Optional[Account] = None

    async def async_setup(self) -> bool:
        self.logger.info("Setting up Exchange On-Premises Integration")

        if not EXCHANGELIB_AVAILABLE:
            self.logger.error("exchangelib library not available. Please install it.")
            return False

        service_registry.register(
            domain=self.domain,
            service="send_email",
            service_func=self.send_email,
            schema={
                "to": list,
                "subject": str,
                "body": str,
                "cc": list,
                "attachments": list,
            },
            description="Send an email via Exchange",
        )

        service_registry.register(
            domain=self.domain,
            service="get_mailbox",
            service_func=self.get_mailbox,
            schema={"email": str},
            description="Get mailbox information",
        )

        service_registry.register(
            domain=self.domain,
            service="create_calendar_event",
            service_func=self.create_calendar_event,
            schema={"subject": str, "start": str, "end": str, "attendees": list},
            description="Create a calendar event",
        )

        service_registry.register(
            domain=self.domain,
            service="get_calendar_events",
            service_func=self.get_calendar_events,
            schema={"start_date": str, "end_date": str},
            description="Get calendar events",
        )

        return True

    def _get_account(self) -> Optional[Any]:  # type: ignore
        """Get or create Exchange account."""
        if self.account is None:
            server_url = self.config.get("server_url")
            username = self.config.get("username")
            password = self.config.get("password")

            credentials = Credentials(username, password)
            self.account = Account(
                primary_smtp_address=username if "@" in username else None,
                credentials=credentials,
                autodiscover=False,
                service_endpoint=server_url,
            )
        return self.account

    async def send_email(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email via Exchange."""
        try:
            account = self._get_account()
            to_addresses = data.get("to", [])
            subject = data.get("subject", "")
            body = data.get("body", "")
            cc_addresses = data.get("cc", [])
            attachments = data.get("attachments", [])

            message = Message(
                account=account,
                subject=subject,
                body=body,
                to_recipients=[Mailbox(email_address=addr) for addr in to_addresses],
                cc_recipients=(
                    [Mailbox(email_address=addr) for addr in cc_addresses]
                    if cc_addresses
                    else None
                ),
            )

            # Handle attachments if provided
            # Note: Full attachment support would require file handling

            message.send()

            self.logger.info(f"Email sent via Exchange to {', '.join(to_addresses)}")
            return {"success": True, "message": "Email sent"}
        except Exception as e:
            self.logger.error(f"Failed to send email via Exchange: {e}")
            return {"success": False, "error": str(e)}

    async def get_mailbox(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get mailbox information."""
        try:
            email = data.get("email")
            account = self._get_account()

            if email and email != account.primary_smtp_address:
                # Access another mailbox
                target_mailbox = Account(
                    primary_smtp_address=email,
                    credentials=account.credentials,
                    autodiscover=False,
                    service_endpoint=account.protocol.service_endpoint,
                )
                mailbox_info = {
                    "email": target_mailbox.primary_smtp_address,
                    "display_name": target_mailbox.name,
                    "total_items": target_mailbox.inbox.total_count,
                }
            else:
                mailbox_info = {
                    "email": account.primary_smtp_address,
                    "display_name": account.name,
                    "total_items": account.inbox.total_count,
                }

            return {"success": True, "mailbox": mailbox_info}
        except Exception as e:
            self.logger.error(f"Failed to get Exchange mailbox: {e}")
            return {"success": False, "error": str(e)}

    async def create_calendar_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a calendar event."""
        try:
            account = self._get_account()
            subject = data.get("subject", "")
            start_str = data.get("start")
            end_str = data.get("end")
            attendees = data.get("attendees", [])

            # Parse datetime strings
            start_dt = EWSDateTime.from_datetime(
                datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            )
            end_dt = EWSDateTime.from_datetime(
                datetime.fromisoformat(end_str.replace("Z", "+00:00"))
            )

            item = CalendarItem(
                account=account,
                folder=account.calendar,
                subject=subject,
                start=start_dt,
                end=end_dt,
                required_attendees=(
                    [Mailbox(email_address=addr) for addr in attendees]
                    if attendees
                    else None
                ),
            )
            item.save()

            self.logger.info(f"Calendar event created: {subject}")
            return {"success": True, "event_id": item.id}
        except Exception as e:
            self.logger.error(f"Failed to create Exchange calendar event: {e}")
            return {"success": False, "error": str(e)}

    async def get_calendar_events(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get calendar events."""
        try:
            account = self._get_account()
            start_date_str = data.get("start_date")
            end_date_str = data.get("end_date")

            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)

            start_ews = EWSDateTime.from_datetime(start_date)
            end_ews = EWSDateTime.from_datetime(end_date)

            items = account.calendar.filter(start__gte=start_ews, end__lte=end_ews)

            events = []
            for item in items:
                events.append(
                    {
                        "subject": item.subject,
                        "start": item.start.isoformat() if item.start else None,
                        "end": item.end.isoformat() if item.end else None,
                        "location": item.location,
                    }
                )

            return {"success": True, "count": len(events), "events": events}
        except Exception as e:
            self.logger.error(f"Failed to get Exchange calendar events: {e}")
            return {"success": False, "error": str(e)}
