import pytest
from datetime import timedelta
import jwt
from app.config import Config
from app.auth.jwt import JWTManager

class TestJWTManager:
    def test_encode_and_decode_success(self, jwt_data):
        token = JWTManager.encode(
            jwt_data["payload"],
            expire_delta=timedelta(minutes=5),
            issuer=jwt_data["issuer"],
            audience=jwt_data["audience"]
        )
        assert isinstance(token, str)

        decoded = JWTManager.decode(token, audience=jwt_data["audience"])
        assert decoded["sub"] == jwt_data["payload"]["sub"]
        assert decoded["iss"] == jwt_data["issuer"]
        assert decoded["aud"] == jwt_data["audience"]

    def test_expired_token(self, jwt_data):
        expired_token = JWTManager.encode(
            jwt_data["payload"],
            expire_delta=timedelta(minutes=-1),  # already expired
            issuer=jwt_data["issuer"],
            audience=jwt_data["audience"]
        )
        with pytest.raises(jwt.ExpiredSignatureError):
            JWTManager.decode(expired_token, audience=jwt_data["audience"])

    def test_invalid_audience(self, jwt_data):
        token = JWTManager.encode(
            jwt_data["payload"],
            expire_delta=timedelta(minutes=5),
            issuer=jwt_data["issuer"],
            audience=jwt_data["audience"]
        )
        with pytest.raises(jwt.InvalidAudienceError):
            JWTManager.decode(token, audience="wrong-audience")

    def test_invalid_issuer(self, jwt_data):
        token = JWTManager.encode(
            jwt_data["payload"],
            expire_delta=timedelta(minutes=5),
            issuer="fake-issuer",  # wrong issuer
            audience=jwt_data["audience"]
        )
        with pytest.raises(jwt.InvalidIssuerError):
            JWTManager.decode(token, audience=jwt_data["audience"])

    def test_missing_required_claim(self, jwt_data):
        # Missing exp, nbf, iat, iss, aud
        bad_token = jwt.encode(
            {"sub": "user"},
            key=Config.SECRET_KEY,
            algorithm=Config.TOKEN_ALGORITHM
        )
        with pytest.raises(jwt.MissingRequiredClaimError):
            JWTManager.decode(bad_token, audience=jwt_data["audience"])
