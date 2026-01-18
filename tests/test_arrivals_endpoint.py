import pytest
import respx
from datetime import datetime, timezone
from httpx import ASGITransport, AsyncClient, Response

from app.main import create_app
from app.dependencies import get_tenant_service
from domain.models.tenant import Tenant
from domain.models.tenant_config import TenantConfig


class StubTenantService:
    async def get_tenant_and_config(self, code: str):
        if code != "ABC123":
            return None, None
        tenant = Tenant(
            id="tenant-1",
            name="Test",
            short_code="ABC123",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        config = TenantConfig(
            tenant_id="tenant-1",
            layout="horizontal",
            refresh_seconds=10,
            swap_seconds=10,
            menu_mode="menuAndImage",
            theme="purple",
            board_header_text="Header",
            stops=["100", "200"],
            line_arrive_default="0",
            timezone=None,
        )
        return tenant, config


@pytest.mark.anyio
async def test_arrivals_merging():
    app = create_app()
    app.dependency_overrides[get_tenant_service] = lambda: StubTenantService()

    base_url = "https://openapi.emtmadrid.es"
    sample_100 = {
        "code": "00",
        "description": "Success",
        "datetime": datetime.utcnow().isoformat(),
        "data": [
            {
                "Arrive": [
                    {
                        "line": "10",
                        "stop": "100",
                        "isHead": "N",
                        "destination": "A",
                        "deviation": 0,
                        "bus": 1,
                        "geometry": None,
                        "estimateArrive": 300,
                        "DistanceBus": None,
                        "positionTypeBus": None,
                    }
                ],
                "StopInfo": [],
                "ExtraInfo": [],
                "Incident": {},
            }
        ],
    }
    sample_200 = {
        "code": "00",
        "description": "Success",
        "datetime": datetime.utcnow().isoformat(),
        "data": [
            {
                "Arrive": [
                    {
                        "line": "20",
                        "stop": "200",
                        "isHead": "N",
                        "destination": "B",
                        "deviation": 0,
                        "bus": 2,
                        "geometry": None,
                        "estimateArrive": 120,
                        "DistanceBus": None,
                        "positionTypeBus": None,
                    }
                ],
                "StopInfo": [],
                "ExtraInfo": [],
                "Incident": {},
            }
        ],
    }

    with respx.mock:
        respx.post(f"{base_url}/v2/transport/busemtmad/stops/100/arrives/0/").mock(
            return_value=Response(200, json=sample_100)
        )
        respx.post(f"{base_url}/v2/transport/busemtmad/stops/200/arrives/0/").mock(
            return_value=Response(200, json=sample_200)
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/tenants/ABC123/arrivals")

    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["stop"] == "200"
    assert data["items"][0]["etaMinutes"] == 2
    assert data["items"][1]["stop"] == "100"
