# Startup_app/templatetags/markdown_extras.py
from django import template
import markdown

register = template.Library()

@register.filter
def render_markdown(text):
    return markdown.markdown(text)
