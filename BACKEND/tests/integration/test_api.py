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


@pytest.mark.asyncio
async def test_reset_db_success(client):
    response = await client.head(f"{Config.URL_PREFIX}/reset-db")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_prometheus_metrics_endpoint(client):
    response = await client.get(f"{Config.URL_PREFIX}/metrics")
    assert response.status_code == status.HTTP_200_OK
    assert "http_requests_total" in response.text or "python_info" in response.text


