from django import template
from urllib.parse import urlencode

register = template.Library()

@register.filter
def int_key(dictionary, key):
    """
    Получает значение из словаря, используя ключ, преобразованный в целое число.
    Если ключ не может быть преобразован или отсутствует, возвращает None.
    """
    try:
        return dictionary[int(key)]
    except (ValueError, KeyError, TypeError):
        return None

@register.filter
def get_status_icon(status_class):
    icons = {
        'completed': '✔',
        'not-completed': '✖',
        # Другие статусы
    }
    return icons.get(status_class, '✖')

@register.filter
def dict_get(dictionary, key):
    """
    Получает значение из словаря по ключу. Возвращает None, если ключ отсутствует или словарь пуст.
    """
    return dictionary.get(key) if dictionary else None

@register.simple_tag(takes_context=True)
def query_string(context, add=None, remove=None):
    """
    Формирует строку запроса, добавляя или удаляя параметры из текущих GET-параметров запроса.
    Использование: {% query_string 'param=value' 'param_to_remove' %}
    """
    request = context.get('request')
    params = request.GET.copy()
    if add:
        key, value = add.split('=', 1)
        params[key] = value
    if remove:
        params.pop(remove, None)
    return params.urlencode()
