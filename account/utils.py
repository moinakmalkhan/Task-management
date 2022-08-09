import re


def is_email(email: str) -> bool:
    """
    Check if the given string is a valid email address.
    """
    if not email:
        return False
    if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
        return False
    return True
