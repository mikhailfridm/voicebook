"""
iiko Cloud API (iikoTransport) wrapper for VoiceBook.

Handles restaurant table reservations.
Docs: https://api-ru.iiko.services (all endpoints are POST).
"""

import asyncio
import logging
import time
from datetime import date, datetime, timedelta
from typing import Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://api-ru.iiko.services"


class IikoClient:
    """Async client for iiko Cloud API restaurant reservations."""

    def __init__(
        self,
        api_login: str = "",
        organization_id: str = "",
        terminal_group_id: str = "",
    ):
        self.api_login = api_login or settings.iiko_api_login
        self.organization_id = organization_id or settings.iiko_organization_id
        self.terminal_group_id = terminal_group_id or settings.iiko_terminal_group_id
        self._client = httpx.AsyncClient(base_url=BASE_URL, timeout=15.0)
        self._token: str = ""
        self._token_expires: float = 0

    async def _ensure_token(self):
        """Get or refresh access token (valid ~1 hour)."""
        if self._token and time.time() < self._token_expires:
            return
        resp = await self._client.post(
            "/api/1/access_token",
            json={"apiLogin": self.api_login},
        )
        resp.raise_for_status()
        self._token = resp.json()["token"]
        self._token_expires = time.time() + 3000  # refresh before 1hr expiry
        logger.info("iiko token refreshed")

    @property
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._token}"}

    async def get_restaurant_sections(self) -> list[dict]:
        """Get restaurant sections (halls) with tables."""
        await self._ensure_token()
        resp = await self._client.post(
            "/api/1/reserve/available_restaurant_sections",
            headers=self._headers,
            json={
                "terminalGroupIds": [self.terminal_group_id],
                "revision": None,
            },
        )
        resp.raise_for_status()
        return resp.json().get("restaurantSections", [])

    async def get_available_slots(
        self,
        target_date: Optional[date] = None,
        guests_count: int = 2,
        duration_minutes: int = 120,
    ) -> list[dict]:
        """Find available time slots by checking existing reservations.

        Returns list of {"time": "HH:MM", "table_id": "...", "table_name": "...", "capacity": N}
        """
        await self._ensure_token()
        if target_date is None:
            target_date = date.today()

        # Get all sections with tables
        sections = await self.get_restaurant_sections()
        all_tables = []
        section_ids = []
        for section in sections:
            section_ids.append(section["id"])
            for table in section.get("tables", []):
                if not table.get("isDeleted") and table.get("seatingCapacity", 0) >= guests_count:
                    all_tables.append({
                        "id": table["id"],
                        "name": table.get("name", f"Стол {table.get('number', '?')}"),
                        "capacity": table.get("seatingCapacity", 0),
                        "section_id": section["id"],
                        "section_name": section.get("name", ""),
                    })

        if not all_tables or not section_ids:
            return []

        # Get existing reservations for the date
        date_from = f"{target_date.isoformat()} 00:00:00.000"
        date_to = f"{target_date.isoformat()} 23:59:59.000"

        resp = await self._client.post(
            "/api/1/reserve/restaurant_sections_workload",
            headers=self._headers,
            json={
                "restaurantSectionIds": section_ids,
                "dateFrom": date_from,
                "dateTo": date_to,
            },
        )
        resp.raise_for_status()
        existing_reserves = resp.json().get("reserves", [])

        # Build occupied time ranges per table
        occupied: dict[str, list[tuple[int, int]]] = {}
        for res in existing_reserves:
            start_str = res.get("estimatedStartTime", "")
            duration = res.get("durationInMinutes", 120)
            try:
                start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S.%f")
                start_min = start_dt.hour * 60 + start_dt.minute
                end_min = start_min + duration
                for tid in res.get("tableIds", []):
                    occupied.setdefault(tid, []).append((start_min, end_min))
            except (ValueError, TypeError):
                continue

        # Find free slots (check every 30min from 11:00 to 22:00)
        available = []
        for hour in range(11, 22):
            for minute in (0, 30):
                slot_start = hour * 60 + minute
                slot_end = slot_start + duration_minutes

                if slot_end > 23 * 60:
                    continue

                for table in all_tables:
                    table_occ = occupied.get(table["id"], [])
                    is_free = all(
                        slot_end <= occ_start or slot_start >= occ_end
                        for occ_start, occ_end in table_occ
                    )
                    if is_free:
                        available.append({
                            "time": f"{hour:02d}:{minute:02d}",
                            "table_id": table["id"],
                            "table_name": table["name"],
                            "section_name": table["section_name"],
                            "capacity": table["capacity"],
                        })
                        break  # one table per slot is enough

        return available

    async def create_reservation(
        self,
        table_id: str,
        start_time: str,
        guests_count: int,
        client_name: str,
        client_phone: str,
        duration_minutes: int = 120,
        comment: str = "",
    ) -> dict:
        """Create a restaurant reservation.

        Args:
            table_id: UUID of the table
            start_time: "YYYY-MM-DD HH:MM:SS.000" format (local time)
            guests_count: number of guests
            client_name: guest name
            client_phone: phone starting with "+"
            duration_minutes: reservation duration
            comment: optional comment

        Returns:
            dict with reservation id and status
        """
        await self._ensure_token()

        if not client_phone.startswith("+"):
            client_phone = f"+{client_phone}"

        payload = {
            "organizationId": self.organization_id,
            "terminalGroupId": self.terminal_group_id,
            "customer": {
                "type": "regular",
                "id": None,
                "name": client_name,
            },
            "phone": client_phone,
            "guestsCount": guests_count,
            "guests": {"count": guests_count},
            "comment": comment,
            "durationInMinutes": duration_minutes,
            "shouldRemind": True,
            "tableIds": [table_id],
            "estimatedStartTime": start_time,
            "transportToFrontTimeout": 8,
        }

        resp = await self._client.post(
            "/api/1/reserve/create",
            headers=self._headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

        reserve_info = data.get("reserveInfo", {})
        reserve_id = reserve_info.get("id")
        status = reserve_info.get("creationStatus", "Unknown")

        # Poll for completion if InProgress
        if status == "InProgress" and reserve_id:
            for _ in range(5):
                await asyncio.sleep(1)
                check = await self.get_reservation_status(reserve_id)
                if check and check.get("creationStatus") != "InProgress":
                    status = check["creationStatus"]
                    break

        logger.info(f"iiko reservation created: {reserve_id} status={status}")
        return {"id": reserve_id, "status": status}

    async def get_reservation_status(self, reserve_id: str) -> Optional[dict]:
        """Check reservation status by ID."""
        await self._ensure_token()
        resp = await self._client.post(
            "/api/1/reserve/status_by_id",
            headers=self._headers,
            json={
                "organizationId": self.organization_id,
                "reserveIds": [reserve_id],
            },
        )
        resp.raise_for_status()
        reserves = resp.json().get("reserves", [])
        return reserves[0] if reserves else None

    async def close(self):
        await self._client.aclose()
