"""
Inlines a small, first-party static file's contents directly into the
page, so the browser doesn't pay a separate render-blocking round trip
(to S3, in production) to fetch it before it can paint. Only worth
doing for the couple of KB-sized stylesheets that are needed on every
page - see base.html/index.html for where this is used, and why.
"""
import posixpath
import re

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.safestring import mark_safe

register = template.Library()

# Matches CSS url(...) references, capturing an optional quote and the
# URL itself, e.g. url("../images/x.jpg") or url(/static/images/x.jpg).
_URL_RE = re.compile(r"""url\(\s*(['"]?)([^'")]+)\1\s*\)""")


def _rewrite_css_urls(content, css_path):
    """
    Reading a static file straight off disk (see below) skips the
    hashed-filename rewriting collectstatic normally does to a linked
    stylesheet's own url() references, which breaks any background-image
    once inlined. Redo that rewriting here via the same storage API
    collectstatic uses, so it works whether that storage is a plain local
    directory (dev) or hashed S3 (production).
    """
    base_dir = posixpath.dirname(css_path)

    def rewrite(match):
        quote, url = match.group(1), match.group(2)
        if url.startswith(("data:", "http://", "https://", "//")):
            return match.group(0)
        if url.startswith(settings.STATIC_URL):
            static_path = url[len(settings.STATIC_URL):]
        else:
            static_path = posixpath.normpath(posixpath.join(base_dir, url))
        resolved_url = staticfiles_storage.url(static_path)
        return f"url({quote}{resolved_url}{quote})"

    return _URL_RE.sub(rewrite, content)


@register.simple_tag
def inline_static(path):
    """Read a static file straight off disk and return its content, with
    any url() references rewritten to the real (possibly hashed) static
    URL they'd get if the file were linked normally."""
    absolute_path = finders.find(path)
    if not absolute_path:
        return ""
    with open(absolute_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = _rewrite_css_urls(content, path)
    return mark_safe(content)
