"""
HTTP client for Portal Email microservice (Email & OTP verification).
Inherits from BaseClient with X-API-KEY & X-API-SECRET authentication.
"""
import httpx
from typing import Optional, Dict, Any
from app.clients.base import BaseClient
from app.core.config import settings


class EmailClient(BaseClient):
    def __init__(self):
        super().__init__(
            base_url=settings.EMAIL_SERVICE_URL,
            api_key=settings.EMAIL_SERVICE_API_KEY,
            api_secret=settings.EMAIL_SERVICE_API_SECRET,
            service_name="email-service",
        )
        self._client.timeout = httpx.Timeout(timeout=15.0, connect=5.0)

    async def generate_otp(
        self,
        identifier: str,
        purpose: str = "login",
        app_name: str = "Store App",
        template_slug: str = "otp-verification",
    ) -> Dict[str, Any]:
        """Request OTP code generation & email dispatch."""
        payload = {
            "identifier": identifier,
            "purpose": purpose,
            "app_name": app_name,
            "template_slug": template_slug,
        }
        return await self.post("otp/generate", json=payload)

    async def verify_otp(
        self,
        identifier: str,
        otp_code: str,
        purpose: str = "login",
    ) -> Dict[str, Any]:
        """Validate 6-digit numeric OTP code."""
        payload = {
            "identifier": identifier,
            "otp_code": otp_code,
            "purpose": purpose,
        }
        return await self.post("otp/verify", json=payload)

    async def send_templated_email(
        self,
        template_slug: str,
        to_email: str,
        variables: Dict[str, Any],
        to_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatch email using pre-built HTML template."""
        payload = {
            "template_slug": template_slug,
            "to_email": to_email,
            "variables": variables,
        }
        if to_name:
            payload["to_name"] = to_name
        return await self.post("send", json=payload)

    async def send_raw_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        to_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatch freeform HTML email."""
        payload = {
            "to_email": to_email,
            "subject": subject,
            "html_body": html_body,
        }
        if to_name:
            payload["to_name"] = to_name
        return await self.post("send/raw", json=payload)


# Singleton instance for store app
email_client = EmailClient()
