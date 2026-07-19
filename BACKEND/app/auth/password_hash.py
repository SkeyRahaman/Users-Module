from passlib.context import CryptContext

class PasswordHasher:
    # We set deprecated="auto" and define bcrypt context
    _pwd_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
        bcrypt__min_rounds=12
    )

    @staticmethod
    def get_password_hash(password: str) -> str:
        return PasswordHasher._pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return PasswordHasher._pwd_context.verify(plain_password, hashed_password)
