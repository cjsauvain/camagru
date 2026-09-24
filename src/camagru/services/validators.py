import string

from camagru.services.errors import ValidationError


def validate_username(username: str) -> None:
    if not username or len(username) < 3:
        raise ValidationError("Username must be at least 3 characters long.")


def validate_email(email: str) -> None:
    if "@" not in email or "." not in email:
        raise ValidationError("Please enter a valid email address")


def validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not any(c.isalpha() for c in password):
        raise ValidationError("Password must contain letters.")
    if not any(c.isdigit() for c in password):
        raise ValidationError("Password must contain digits.")
    if not any(c in password for c in string.punctuation):
        raise ValidationError("Password must contain special characters.")
