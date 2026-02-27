import random
import string

def generate_short_code(length: int = 6) -> str:
    """
    Generate a simple 6-character random short code.
    Uses alphanumeric characters (A-Z, a-z, 0-9) to avoid confusing symbols.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
