import pytest
from datetime import datetime, timezone
from app.api.routers.health import health_check
from app.config import Config

@pytest.mark.asyncio
async def test_health_check_unit():
    response = await health_check()
    
    assert response["status"] == "HEALTHY"
    assert "timestamp" in response
    # Check that timestamp is a valid ISO8601 string ending with 'Z'
    assert response["timestamp"].endswith("Z")
    assert response["version"] == Config.VERSION
