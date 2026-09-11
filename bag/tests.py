"""
Tests for the shopping bag: auth gating, add/adjust/remove behaviour,
and the per-dish daily quantity limit.
"""
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from dishes.models import Category, Dish, DishPortion


class BagTestCase(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Lunch", slug="lunch")
        dish = Dish.objects.create(
            category=category,
            name="Test Dish",
            slug="test-dish",
            description="desc",
            price=Decimal("9.99"),
        )
        self.portion = DishPortion.objects.create(
            dish=dish, size="Regular", price=Decimal("9.99")
        )
        self.user = User.objects.create_user(
            username="shopper", password="testpass12345"
        )


class AnonymousAccessTests(BagTestCase):
    def test_view_bag_redirects_anonymous_user(self):
        response = self.client.get(reverse("bag"))
        self.assertEqual(response.status_code, 302)

    def test_add_to_bag_rejects_anonymous_user(self):
        response = self.client.post(
            reverse("add_to_bag", args=[self.portion.id]), {"quantity": 1}
        )
        self.assertEqual(response.status_code, 302)

    def test_add_to_bag_ajax_returns_401_for_anonymous_user(self):
        response = self.client.post(
            reverse("add_to_bag", args=[self.portion.id]),
            {"quantity": 1},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "AUTH_REQUIRED")


class AddAdjustRemoveTests(BagTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="shopper", password="testpass12345")

    def test_add_to_bag_stores_quantity_in_session(self):
        response = self.client.post(
            reverse("add_to_bag", args=[self.portion.id]), {"quantity": 3}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.client.session["bag"], {str(self.portion.id): 3}
        )

    def test_add_to_bag_enforces_daily_limit(self):
        response = self.client.post(
            reverse("add_to_bag", args=[self.portion.id]),
            {"quantity": 21},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "DAILY_LIMIT_REACHED")

    def test_adjust_bag_updates_quantity(self):
        self.client.post(
            reverse("add_to_bag", args=[self.portion.id]), {"quantity": 1}
        )
        response = self.client.post(
            reverse("adjust_bag", args=[self.portion.id]),
            {"quantity": 5},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(self.client.session["bag"][str(self.portion.id)], 5)

    def test_adjust_bag_to_zero_removes_item(self):
        self.client.post(
            reverse("add_to_bag", args=[self.portion.id]), {"quantity": 1}
        )
        self.client.post(
            reverse("adjust_bag", args=[self.portion.id]), {"quantity": 0}
        )
        self.assertNotIn(str(self.portion.id), self.client.session["bag"])

    def test_remove_from_bag_clears_item(self):
        self.client.post(
            reverse("add_to_bag", args=[self.portion.id]), {"quantity": 2}
        )
        self.client.post(reverse("remove_from_bag", args=[self.portion.id]))
        self.assertNotIn(str(self.portion.id), self.client.session["bag"])

    def test_view_bag_renders_for_logged_in_user(self):
        self.client.post(
            reverse("add_to_bag", args=[self.portion.id]), {"quantity": 1}
        )
        response = self.client.get(reverse("bag"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Dish")
