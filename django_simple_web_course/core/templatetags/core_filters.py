from django import template
import markdown
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def modulus(value, arg):
    return value % arg

@register.filter
def render_markdown(value):
    return mark_safe(markdown.markdown(value))

@register.filter
def course_continue_url(course, student):
    return mark_safe(course.continue_url(student))

@register.filter
def course_recent_url_history(course, student):
    return course.url_recent_history(student)


@register.filter
def course_last_page_view_url(course, student):
    return course.last_page_view_url(student)