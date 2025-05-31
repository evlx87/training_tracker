from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key)

@register.filter
def int_key(dictionary, key):
    try:
        return dictionary.get(int(key))
    except (ValueError, TypeError):
        return None

@register.filter
def get_status_icon(status):
    icons = {
        'not-completed': '✖',
        'overdue': '⏰',
        'warning': '⚠',
        'completed': '✔',
    }
    return icons.get(status, '✖')  # По умолчанию иконка для "не пройдено"