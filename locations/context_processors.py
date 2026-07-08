# Кастомные context processors — переменные, доступные во всех шаблонах автоматически.
from django.conf import settings


def is_dev(request):
    # DEBUG=True только локально (.env), на Railway в проде DEBUG=False.
    # Используется в base.html чтобы показать бейдж "DEV" в заголовке сайта.
    return {"IS_DEV": settings.DEBUG}
