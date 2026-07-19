import pytest
from fastapi import status
from app.config import Config

@pytest.mark.asyncio
async def test_health_check_success(client):
    response = await client.get(f"{Config.URL_PREFIX}/health")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "timestamp" in data
    assert "version" in data
    assert data["version"] == Config.VERSION
