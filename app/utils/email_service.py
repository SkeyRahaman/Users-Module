# util/email_service.py
# This module provides email sending functionality using SMTP.
from app.utils.logger import log


class EmailService:
    @staticmethod
    async def send_password_rest_email(to_address, subject, body):
        # Placeholder for email sending logic
        print(f"Sending email to {to_address} with subject '{subject}' and body '{body}'")
        # Actual implementation would go here
        log.info("Password reset email sent", to_address=to_address)
        return True