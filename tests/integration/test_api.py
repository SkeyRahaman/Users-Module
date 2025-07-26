from fastapi import status
from fastapi.testclient import TestClient
from app.config import Config
from app.main import app

def test_health_check_success(client: TestClient):
    # Act
    response = client.get(app.url_path_for("health"))
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    
    response_data = response.json()
    assert response_data["status"] == "HEALTHY"
    assert "version" in response_data
    assert response_data["version"] == Config.VERSION
    