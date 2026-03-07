"""Tests for Yclients API wrapper (mocked HTTP)."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.booking.yclients import YclientsClient

FAKE_REQUEST = httpx.Request("GET", "https://api.yclients.com/test")


@pytest.fixture
def client():
    return YclientsClient(
        partner_token="test-partner",
        user_token="test-user",
        company_id="12345",
    )


def _resp(status: int, json_data=None):
    return httpx.Response(status, json=json_data, request=FAKE_REQUEST)


@pytest.mark.asyncio
async def test_get_services(client):
    mock_resp = _resp(200, {"data": [
        {"id": 1, "title": "Мужская стрижка"},
        {"id": 2, "title": "Стрижка бороды"},
    ]})

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_resp):
        services = await client.get_services()

    assert len(services) == 2
    assert services[0]["title"] == "Мужская стрижка"


@pytest.mark.asyncio
async def test_get_staff(client):
    mock_resp = _resp(200, {"data": [{"id": 10, "name": "Денис"}, {"id": 11, "name": "Артур"}]})

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_resp):
        staff = await client.get_staff()

    assert len(staff) == 2
    assert staff[0]["name"] == "Денис"


@pytest.mark.asyncio
async def test_get_available_slots(client):
    mock_resp = _resp(200, {"data": [{"time": "11:00"}, {"time": "14:30"}, {"time": "16:00"}]})

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_resp):
        from datetime import date
        slots = await client.get_available_slots(staff_id=10, service_id=1, target_date=date(2026, 3, 10))

    assert slots == ["11:00", "14:30", "16:00"]


@pytest.mark.asyncio
async def test_create_booking(client):
    mock_resp = _resp(200, {"data": {"id": 999, "status": "confirmed"}})

    with patch.object(client._client, "post", new_callable=AsyncMock, return_value=mock_resp):
        result = await client.create_booking(
            staff_id=10, service_id=1,
            booking_datetime="2026-03-10 14:30",
            client_name="Артём", client_phone="+79991234567",
        )

    assert result["id"] == 999


@pytest.mark.asyncio
async def test_cancel_booking(client):
    mock_resp = _resp(200)

    with patch.object(client._client, "delete", new_callable=AsyncMock, return_value=mock_resp):
        result = await client.cancel_booking(record_id=999)

    assert result is True


@pytest.mark.asyncio
async def test_get_services_error(client):
    mock_resp = _resp(500, {"error": "server error"})

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_resp):
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_services()
