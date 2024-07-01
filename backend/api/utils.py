import random
import string


from core.constants_recipes import MAX_LENGTH_SHORT_URL

def generate_short_url():
    """Генератор коротких url."""
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(MAX_LENGTH_SHORT_URL))
    return "http:/localhost/s/" + short_url