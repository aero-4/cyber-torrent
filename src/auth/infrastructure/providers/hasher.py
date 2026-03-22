import bcrypt


class HasherProvider:

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        pwd_bytes = password.encode("utf-8")
        hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)

        return hashed_bytes.decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            password=password.encode("utf-8"),
            hashed_password=hashed_password.encode("utf-8"),
        )
