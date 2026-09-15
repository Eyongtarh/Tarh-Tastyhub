from django.test import TestCase, override_settings

from home.templatetags.inline_assets import inline_static


class InlineStaticTests(TestCase):
    """
    Regression test for a real production bug: inline_static() reads a
    CSS file straight off disk, bypassing collectstatic's usual rewriting
    of its url() references to the real (hashed, S3-hosted) static URL.
    Left unrewritten, those references resolve relative to the HTML
    page's own URL once inlined, 404ing in production - this happened
    with base.css's and index.css's background-image rules.
    """

    def test_relative_url_is_rewritten_to_a_static_url(self):
        content = inline_static("css/index.css")
        self.assertIn('url("/static/images/testimonials_pic.jpg")', content)
        self.assertNotIn('url("../images/testimonials_pic.jpg")', content)

    def test_root_absolute_url_is_rewritten_to_a_static_url(self):
        content = inline_static("css/base.css")
        self.assertIn("url('/static/images/feedback_pic.jpg')", content)
        self.assertIn('url("/static/images/banner_error.jpg")', content)

    @override_settings(
        STATIC_URL="https://cdn.example.com/static/",
        STATICFILES_STORAGE=(
            "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
        ),
    )
    def test_root_absolute_url_strips_prefix_when_static_url_differs(self):
        """
        In production STATIC_URL is the full S3 URL, not "/static/" - a
        version of this code that matched settings.STATIC_URL (rather
        than the literal "/static/" prefix source CSS actually writes)
        never matched there, passed "/static/images/feedback_pic.jpg"
        (untouched) to staticfiles_storage.url(), and 500'd every page.
        ManifestStaticFilesStorage raises on a path with no manifest
        entry - used here just to observe which path was actually
        requested, without needing a real manifest built.
        """
        with self.assertRaises(ValueError) as ctx:
            inline_static("css/base.css")
        message = str(ctx.exception)
        # Whichever url() is encountered first raises - the assertion
        # that matters is that its path had "/static/" stripped, not
        # which specific reference that happened to be.
        self.assertNotIn("/static/", message)
