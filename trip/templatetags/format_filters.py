from django import template

register = template.Library()

@register.filter
def format_number(value):
    return '{:,.0f}'.format(value).replace(',', '.')
