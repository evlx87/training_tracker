from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Проверяет, входит ли пользователь в указанную группу.
    Использование: {% if user|has_group:"Editors" %} ... {% endif %}
    """
    if user.is_authenticated:
        return user.groups.filter(name=group_name).exists()
    return False
