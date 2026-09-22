from hashlib import pbkdf2_hmac
import hmac
import secrets


def hash_password(
    password: str,
    salt: str | None = None,
    algorithm: str = "sha256",
    iterations: int = 600000,
) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    hash = pbkdf2_hmac(algorithm, password.encode(), salt.encode(), iterations)

    return f"{algorithm}${iterations}${salt}${hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    if (password_hash or "").count("$") != 3:
        return False

    algorithm, iterations, salt, _ = password_hash.split("$", 3)
    check_hash = hash_password(password, salt, algorithm, int(iterations))

    return hmac.compare_digest(check_hash, password_hash)


def generate_token() -> str:
    return secrets.token_urlsafe(32)
