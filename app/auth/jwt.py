from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import jwt
from app.config import Config

class JWTManager:
    @staticmethod
    def encode(
        data: dict,
        expire_delta: Optional[timedelta] = None,
        issuer: str = "your-issuer-identifier",
        audience: str = "your-audience-identifier"
    ) -> str:
        """
        Encode (create) a JWT access token.
        """
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        expire = now + (expire_delta or timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES))

        # Add standard claims
        to_encode.update({
            "iat": now,
            "exp": expire,
            "nbf": now,
            "iss": issuer,
            "aud": audience,
        })

        token = jwt.encode(
            to_encode,
            key=Config.SECRET_KEY,
            algorithm=Config.TOKEN_ALGORITHM
        )
        return token

    @staticmethod
    def decode(token: str, audience: Optional[Union[str, list]] = None) -> dict:
        """
        Decode & verify a JWT token with strict checks.
        Raises PyJWT exceptions for the caller to handle.
        """
        decoded = jwt.decode(
            token,
            key=Config.SECRET_KEY,
            algorithms=[Config.TOKEN_ALGORITHM],
            audience=audience or "your-audience-identifier", 
            issuer="your-issuer-identifier",                  
            options={
                "require": ["exp", "nbf", "iat", "iss", "aud"],
            },
            leeway=5
        )
        return decoded
