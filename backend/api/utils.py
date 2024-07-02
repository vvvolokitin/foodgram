import random
import string


from core.constants_recipes import MAX_LENGTH_SHORT_URL

def generate_short_url():
    """Генератор коротких url."""
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(MAX_LENGTH_SHORT_URL))
    return "http:/localhost/s/" + short_url

def redirect_to_full_link(request, short_link):
    try:
        link_obj = Link.objects.get(
            short_link="http:/localhost/s/" + short_link
        )
        full_link = link_obj.base_link.replace('/api', '', 1)
        return redirect(full_link)
    except Link.DoesNotExist:
        return HttpResponse(
            'Ссылка не найдена',
            status=status.HTTP_404_NOT_FOUND
        )