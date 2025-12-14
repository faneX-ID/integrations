from services.integration_base import Integration
from services.service_registry import service_registry
import logging
import requests
from datetime import datetime
from typing import Optional

class CalendarSyncIntegration(Integration):
    async def async_setup(self):
        self.logger.info("Setting up Calendar Sync Integration")

        service_registry.register(
            domain=self.domain,
            service="create_event",
            service_func=self.create_event,
            schema={
                "title": str,
                "description": str,
                "start_time": str,
                "end_time": str,
                "attendees": list,
                "location": str
            },
            description="Create a calendar event"
        )

        service_registry.register(
            domain=self.domain,
            service="list_events",
            service_func=self.list_events,
            schema={"start_date": str, "end_date": str},
            description="List calendar events"
        )

        return True

    def _get_headers(self):
        """Get authentication headers."""
        api_key = self.config.get("api_key")
        if not api_key:
            raise ValueError("API key not configured")

        provider = self.config.get("provider", "google")
        if provider == "google":
            return {"Authorization": f"Bearer {api_key}"}
        elif provider == "outlook":
            return {"Authorization": f"Bearer {api_key}"}
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def create_event(self, data: dict):
        """Create a calendar event."""
        provider = self.config.get("provider", "google")
        calendar_id = self.config.get("calendar_id", "primary")
        timezone = self.config.get("timezone", "UTC")

        title = data.get("title", "")
        description = data.get("description", "")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        attendees = data.get("attendees", [])
        location = data.get("location")

        if provider == "google":
            url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
            event_data = {
                "summary": title,
                "description": description,
                "start": {
                    "dateTime": start_time,
                    "timeZone": timezone
                },
                "end": {
                    "dateTime": end_time,
                    "timeZone": timezone
                }
            }

            if attendees:
                event_data["attendees"] = [{"email": email} for email in attendees]

            if location:
                event_data["location"] = location

        elif provider == "outlook":
            url = "https://graph.microsoft.com/v1.0/me/events"
            event_data = {
                "subject": title,
                "body": {
                    "contentType": "HTML",
                    "content": description or ""
                },
                "start": {
                    "dateTime": start_time,
                    "timeZone": timezone
                },
                "end": {
                    "dateTime": end_time,
                    "timeZone": timezone
                }
            }

            if attendees:
                event_data["attendees"] = [{"emailAddress": {"address": email}} for email in attendees]

            if location:
                event_data["location"] = {"displayName": location}

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        try:
            response = requests.post(
                url,
                json=event_data,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            event_id = result.get("id") or result.get("iCalUId")
            self.logger.info(f"Calendar event created: {event_id}")
            return {"status": "created", "event_id": event_id}
        except Exception as e:
            self.logger.error(f"Failed to create calendar event: {e}")
            raise

    async def list_events(self, data: dict):
        """List calendar events."""
        provider = self.config.get("provider", "google")
        calendar_id = self.config.get("calendar_id", "primary")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if provider == "google":
            url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
            params = {"singleEvents": "true", "orderBy": "startTime"}
            if start_date:
                params["timeMin"] = start_date
            if end_date:
                params["timeMax"] = end_date

        elif provider == "outlook":
            url = "https://graph.microsoft.com/v1.0/me/events"
            params = {}
            if start_date:
                params["$filter"] = f"start/dateTime ge '{start_date}'"
            if end_date:
                if "$filter" in params:
                    params["$filter"] += f" and end/dateTime le '{end_date}'"
                else:
                    params["$filter"] = f"end/dateTime le '{end_date}'"

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        try:
            response = requests.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            events = result.get("items", []) if provider == "google" else result.get("value", [])
            self.logger.info(f"Retrieved {len(events)} calendar events")
            return {"events": events, "count": len(events)}
        except Exception as e:
            self.logger.error(f"Failed to list calendar events: {e}")
            raise

