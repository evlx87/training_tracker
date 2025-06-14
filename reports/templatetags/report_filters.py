from django import template

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
