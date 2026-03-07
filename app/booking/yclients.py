"""
Yclients API wrapper for VoiceBook.

Docs: https://api.yclients.com/
"""

import httpx
import logging
from datetime import date, datetime
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://api.yclients.com/api/v1"


class YclientsClient:
    def __init__(
        self,
        partner_token: str = "",
        user_token: str = "",
        company_id: str = "",
    ):
        self.partner_token = partner_token or settings.yclients_partner_token
        self.user_token = user_token or settings.yclients_user_token
        self.company_id = company_id or settings.yclients_company_id
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=10.0,
        )

    @property
    def _headers(self) -> dict:
        return {
            "Accept": "application/vnd.api.v2+json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.partner_token}, User {self.user_token}",
        }

    async def get_services(self) -> list[dict]:
        """Get list of services for the company."""
        resp = await self._client.get(
            f"/company/{self.company_id}/services",
            headers=self._headers,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])

    async def get_staff(self) -> list[dict]:
        """Get list of staff (masters) for the company."""
        resp = await self._client.get(
            f"/company/{self.company_id}/staff",
            headers=self._headers,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])

    async def get_available_slots(
        self,
        staff_id: int,
        service_id: int,
        target_date: Optional[date] = None,
    ) -> list[str]:
        """Get available time slots for a master on a given date."""
        if target_date is None:
            target_date = date.today()

        resp = await self._client.get(
            f"/book_times/{self.company_id}/{staff_id}/{target_date.isoformat()}",
            headers=self._headers,
            params={"service_id": service_id},
        )
        resp.raise_for_status()
        data = resp.json()
        # Returns list of available datetime strings
        return [slot["time"] for slot in data.get("data", []) if isinstance(slot, dict)]

    async def create_booking(
        self,
        staff_id: int,
        service_id: int,
        booking_datetime: str,
        client_name: str,
        client_phone: str,
    ) -> dict:
        """Create a booking in Yclients."""
        payload = {
            "staff_id": staff_id,
            "services": [{"id": service_id}],
            "client": {
                "name": client_name,
                "phone": client_phone,
            },
            "datetime": booking_datetime,
        }

        resp = await self._client.post(
            f"/book_record/{self.company_id}",
            headers=self._headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Booking created: {data}")
        return data.get("data", {})

    async def lookup_client(self, phone: str) -> Optional[dict]:
        """Look up a client by phone number. Returns client info with visit history."""
        try:
            resp = await self._client.get(
                f"/company/{self.company_id}/clients/search",
                headers=self._headers,
                params={"phone": phone},
            )
            resp.raise_for_status()
            data = resp.json()
            clients = data.get("data", [])
            if not clients:
                return None

            client = clients[0]
            client_id = client.get("id")

            # Fetch visit history
            visits = []
            if client_id:
                visits_resp = await self._client.get(
                    f"/company/{self.company_id}/clients/{client_id}/visits",
                    headers=self._headers,
                )
                if visits_resp.status_code == 200:
                    visits_data = visits_resp.json()
                    visits = visits_data.get("data", [])[:10]  # last 10 visits

            # Find most frequent service
            service_counts: dict[str, int] = {}
            for visit in visits:
                for svc in visit.get("services", []):
                    svc_name = svc.get("title", "")
                    if svc_name:
                        service_counts[svc_name] = service_counts.get(svc_name, 0) + 1

            favorite_service = max(service_counts, key=service_counts.get) if service_counts else None

            return {
                "id": client_id,
                "name": client.get("name", ""),
                "phone": client.get("phone", phone),
                "visits_count": len(visits),
                "favorite_service": favorite_service,
                "last_visit": visits[0] if visits else None,
                "service_history": service_counts,
            }
        except Exception as e:
            logger.warning(f"Client lookup failed for {phone}: {e}")
            return None

    async def cancel_booking(self, record_id: int) -> bool:
        """Cancel an existing booking."""
        resp = await self._client.delete(
            f"/record/{self.company_id}/{record_id}",
            headers=self._headers,
        )
        resp.raise_for_status()
        return resp.status_code == 200

    async def close(self):
        await self._client.aclose()
