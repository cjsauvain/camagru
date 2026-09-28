import re
import string

from camagru.services.errors import ValidationError


def validate_username(username: str) -> None:
    if re.fullmatch(r"[0-9a-zA-Z_-]{3,20}", username) is None:
        raise ValidationError(
            "Username should be 3 to 20 characters long, "
            "and contain letters, digits, _ and - only."
        )


def validate_email(email: str) -> None:
    if len(email) > 254:
        raise ValidationError("Email is too long.")
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) is None:
        raise ValidationError("Please enter a valid email address")


def validate_password(password: str) -> None:
    if len(password) < 8 or len(password) > 128:
        raise ValidationError("Password must be 8 to 128 characters long.")
    if not any(c.isalpha() for c in password):
        raise ValidationError("Password must contain letters.")
    if not any(c.isdigit() for c in password):
        raise ValidationError("Password must contain digits.")
    if not any(c in password for c in string.punctuation):
        raise ValidationError("Password must contain special characters.")


def validate_comment(body: str) -> None:
    if body.strip() == "":
        raise ValidationError("Your comment must not contain only spaces.")
    if len(body) > 1000:
        raise ValidationError("Your comment is too long, 1000 characters is the limit.")