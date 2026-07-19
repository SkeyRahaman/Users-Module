import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.middlewares.logger_middlewares import LogCorrelationIdMiddleware
from app.utils.logger import log 

@pytest.fixture
def test_app():
    app = FastAPI()
    app.add_middleware(LogCorrelationIdMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"hello": "world"}

    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test exception")

    return app

class TestLogCorrelationIdMiddleware:
    def setup_method(self):
        # Runs before each test method in this class
        # Could add additional setup if needed
        pass

    def test_normal_flow(self, test_app):
        client = TestClient(test_app)

        with patch.object(log, "info") as mock_info:
            response = client.get("/test")
            assert response.status_code == 200

            # Confirm "request_received" and "request_completed" logs emitted
            mock_info.assert_any_call("request_received")
            mock_info.assert_any_call("request_completed", status_code=200)

    def test_exception_flow(self, test_app):
        client = TestClient(test_app, raise_server_exceptions=False)


        with patch.object(log, "info") as mock_info, patch.object(log, "error") as mock_error:
            response = client.get("/error")
            assert response.status_code == 500

            # Confirm request_received logged before error
            mock_info.assert_any_call("request_received")
            # Confirm error logged with exception info
            mock_error.assert_called()
            # Depending on your middleware you may or may not log request_completed on exceptions
