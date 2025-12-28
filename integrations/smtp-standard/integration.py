import logging

from services.integration_base import Integration
from services.service_registry import service_registry


class SmtpIntegration(Integration):
    async def async_setup(self):
        self.logger.info("Setting up SMTP Integration")

        # Register Service
        service_registry.register(
            domain=self.domain,
            service="send_email",
            service_func=self.send_email,
            schema={"to": str, "subject": str, "body": str},
            description="Send an email via SMTP"
        )
        return True

    async def send_email(self, data: dict):
        recipient = data.get("to")
        subject = data.get("subject")
        body = data.get("body", "")

        self.logger.info(f"Sending email to {recipient}: {subject}")
        # Real SMTP logic would go here
        return {"status": "sent", "recipient": recipient}
