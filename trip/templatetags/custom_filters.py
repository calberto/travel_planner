from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def add_days(value, arg):
    """Adiciona dias a uma data."""
    if value and isinstance(arg, int):
        return value + timedelta(days=arg)
    try:
        return value + timedelta(days=int(arg))
    except:
        return value
