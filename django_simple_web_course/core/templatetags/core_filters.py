from django import template
import markdown
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def modulus(value, arg):
    """Removes all values of arg from the given string"""
    return value % arg

@register.filter
def render_markdown(value):
    return mark_safe(markdown.markdown(value))