from django import template

register = template.Library()

@register.filter
def has_group(user, group_name):
    """
    Проверяет, состоит ли пользователь в указанной группе.
    Использование: {% if user|has_group:"Moderators" %} ... {% endif %}
    """
    return user.groups.filter(name=group_name).exists()
