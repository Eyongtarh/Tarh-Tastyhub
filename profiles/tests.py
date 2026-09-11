"""
Tests for profiles: the order_history IDOR fix, profile page access,
and account deletion.
"""
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from checkout.models import Order
from dishes.models import Category, Dish, DishPortion
from .models import UserProfile


def make_order_for(profile):
    return Order.objects.create(
        user_profile=profile,
        full_name="Order Owner",
        email="owner@example.com",
        phone_number="123456",
        street_address1="1 Test St",
        town_or_city="Testville",
        delivery_type="delivery",
        status="Pending",
    )


class OrderHistoryOwnershipTests(TestCase):
    """
    Regression test for the IDOR in order_history: previously any logged-in
    user could view any other customer's order by number.
    """

    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", password="testpass12345"
        )
        self.owner_profile = UserProfile.objects.get(user=self.owner)
        self.order = make_order_for(self.owner_profile)

        self.other_user = User.objects.create_user(
            username="someone_else", password="testpass12345"
        )

    def test_owner_can_view_their_own_order(self):
        self.client.login(username="owner", password="testpass12345")
        response = self.client.get(
            reverse("order_history", args=[self.order.order_number])
        )
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_view_someone_elses_order(self):
        self.client.login(username="someone_else", password="testpass12345")
        response = self.client.get(
            reverse("order_history", args=[self.order.order_number])
        )
        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(
            reverse("order_history", args=[self.order.order_number])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_order_with_no_profile_is_not_viewable_by_other_users(self):
        # Orders placed anonymously (user_profile=None) must not be
        # reachable by any logged-in user via order_history either.
        orphan_order = Order.objects.create(
            full_name="Guest",
            email="guest@example.com",
            phone_number="000",
            street_address1="2 Test St",
            town_or_city="Testville",
        )
        self.client.login(username="someone_else", password="testpass12345")
        response = self.client.get(
            reverse("order_history", args=[orphan_order.order_number])
        )
        self.assertEqual(response.status_code, 404)


class ProfilePageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profileuser", password="testpass12345"
        )

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_sees_their_profile(self):
        self.client.login(username="profileuser", password="testpass12345")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)


class DeleteAccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="deleteme", password="testpass12345"
        )

    def test_post_deletes_the_logged_in_users_account_only(self):
        self.client.login(username="deleteme", password="testpass12345")
        response = self.client.post(reverse("delete_account"))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username="deleteme").exists())
