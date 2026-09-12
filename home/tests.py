from django.test import TestCase

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
