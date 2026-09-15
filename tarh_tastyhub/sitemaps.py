"""
Sitemap definitions for the public, indexable pages of the site.
Account, bag, checkout and admin pages are deliberately left out - they
require a session/login, have no content of their own to rank on, and
have nothing to do with search visibility (see robots.txt for the
matching Disallow rules).
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from dishes.models import Dish


class StaticViewSitemap(Sitemap):
    """The site's small set of standalone, stable pages."""
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return ["home", "dish_list", "feedback", "privacy", "terms"]

    def location(self, item):
        return reverse(item)


class DishSitemap(Sitemap):
    """Every available dish's own detail page."""
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Dish.objects.available()

    def lastmod(self, dish):
        return dish.updated

    def location(self, dish):
        return dish.get_absolute_url()
