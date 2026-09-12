"""
Project-wide template context processors.
"""
from django.conf import settings


def static_origin(request):
    """
    Expose the origin (scheme + host) that static/media files are served
    from, so templates can preconnect to it early. When USE_AWS is off
    (local dev), assets are same-origin and no preconnect is needed.
    """
    if getattr(settings, "USE_AWS", False) and getattr(
        settings, "AWS_S3_CUSTOM_DOMAIN", None
    ):
        return {"static_origin": f"https://{settings.AWS_S3_CUSTOM_DOMAIN}"}
    return {"static_origin": None}
