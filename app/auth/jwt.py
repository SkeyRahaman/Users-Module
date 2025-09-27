from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import jwt
from app.config import Config
from app.utils.logger import log


class JWTManager:

    @staticmethod
    def _get_standard_claims(
        expire_delta: Optional[timedelta],
        issuer: str,
        audience: str,
        extra_claims: dict = {}
    ) -> dict:
        now = datetime.now(timezone.utc)
        expire = now + (expire_delta or timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES))
        claims = {
            "iat": now,
            "exp": expire,
            "nbf": now,
            "iss": issuer,
            "aud": audience if audience else "audience",
        }
        claims.update(extra_claims)
        return claims

    @staticmethod
    def _encode_token(
        data: dict,
        expire_delta: Optional[timedelta],
        issuer: str,
        audience: str,
        extra_claims: dict = {}
    ) -> str:
        to_encode = data.copy()
        to_encode.update(JWTManager._get_standard_claims(expire_delta, issuer, audience, extra_claims))
        token = jwt.encode(
            to_encode,
            key=Config.SECRET_KEY,
            algorithm=Config.TOKEN_ALGORITHM,
        )
        return token

    @staticmethod
    def _decode_token(
        token: str,
        audience: Optional[Union[str, list]],
        issuer: str,
        required_claims: list
    ) -> dict:
        decoded = jwt.decode(
            token,
            key=Config.SECRET_KEY,
            algorithms=[Config.TOKEN_ALGORITHM],
            audience=audience or "audience",
            issuer=issuer,
            options={
                "require": required_claims,
            },
            leeway=5,
        )
        log.debug("Token decoded successfully", extra={"sub": decoded.get("sub")})
        return decoded

    @staticmethod
    def encode_access_token(
        data: dict,
        expire_delta: Optional[timedelta] = None,
        issuer: str = "issuer",
        audience: str = "audience"
    ) -> str:
        return JWTManager._encode_token(data, expire_delta, issuer, audience)

    @staticmethod
    def decode_access_token(token: str, audience: Optional[Union[str, list]] = None) -> dict:
        required_claims = ["exp", "nbf", "iat", "iss", "aud"]
        return JWTManager._decode_token(token, audience if audience else "audience", "issuer", required_claims)

    @staticmethod
    def encode_refresh_token(
        data: dict,
        expire_delta: Optional[timedelta] = None,
        issuer: str = "issuer",
        audience: str = "audience"
    ) -> str:
        extra_claims = {"typ": "refresh"}
        default_expire = timedelta(days=30)
        return JWTManager._encode_token(data, expire_delta or default_expire, issuer, audience, extra_claims)

    @staticmethod
    def decode_refresh_token(token: str, audience: Optional[Union[str, list]] = None) -> dict:
        required_claims = ["exp", "nbf", "iat", "iss", "aud", "typ"]
        decoded = JWTManager._decode_token(token, audience if audience else "audience", "issuer", required_claims)
        if decoded.get("typ") != "refresh":
            log.error("Invalid token type", extra={"typ": decoded.get("typ")})
            raise jwt.InvalidTokenError("Invalid token type: expected refresh token")
        log.debug("Refresh token decoded successfully", extra={"sub": decoded.get("sub")})
        return decoded
