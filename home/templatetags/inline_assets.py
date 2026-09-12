"""
Inlines a small, first-party static file's contents directly into the
page, so the browser doesn't pay a separate render-blocking round trip
(to S3, in production) to fetch it before it can paint. Only worth
doing for the couple of KB-sized stylesheets that are needed on every
page - see base.html/index.html for where this is used, and why.
"""
from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def inline_static(path):
    """Read a static file straight off disk and return its raw content."""
    absolute_path = finders.find(path)
    if not absolute_path:
        return ""
    with open(absolute_path, "r", encoding="utf-8") as f:
        return mark_safe(f.read())
