"""
Tests for checkout: Stripe webhook handling, PaymentIntent/session
binding, and the removal of the unauthenticated status-update endpoint.
"""
import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from dishes.models import Category, Dish, DishPortion
from .models import Order
from .webhook_handler import StripeWH_Handler


def make_dish_portion():
    category = Category.objects.create(name="Lunch", slug="lunch")
    dish = Dish.objects.create(
        category=category,
        name="Test Dish",
        slug="test-dish",
        description="A test dish",
        price=Decimal("9.99"),
    )
    return DishPortion.objects.create(
        dish=dish, size="Regular", price=Decimal("9.99")
    )


@override_settings(STRIPE_WEBHOOK_SECRET="whsec_test_secret")
class WebhookSecretTests(TestCase):
    """
    Regression test for the settings.STRIPE_WH_SECRET / STRIPE_WEBHOOK_SECRET
    attribute-name mismatch that made every webhook call fail with a 500.
    """

    def test_webhook_returns_500_when_secret_missing(self):
        with override_settings(STRIPE_WEBHOOK_SECRET=None):
            response = self.client.post(
                reverse("webhook"),
                data="{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="sig",
            )
        self.assertEqual(response.status_code, 500)

    def test_webhook_rejects_invalid_signature_once_secret_is_set(self):
        # With STRIPE_WEBHOOK_SECRET configured, a bogus payload/signature
        # should reach Stripe's verification and fail with 400 (not 500),
        # proving the view is reading the correct settings attribute.
        response = self.client.post(
            reverse("webhook"),
            data="not-real-stripe-payload",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="not-a-real-signature",
        )
        self.assertEqual(response.status_code, 400)

    @patch("stripe.Webhook.construct_event")
    def test_webhook_dispatches_to_handler_with_verified_event(
        self, mock_construct_event
    ):
        mock_construct_event.return_value = {
            "type": "payment_intent.payment_failed",
            "data": {"object": {"id": "pi_test123"}},
        }
        response = self.client.post(
            reverse("webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        self.assertEqual(response.status_code, 200)
        mock_construct_event.assert_called_once()
        # The secret passed to Stripe must be the configured setting.
        self.assertEqual(
            mock_construct_event.call_args[0][2], "whsec_test_secret"
        )


class StripeWebhookHandlerTests(TestCase):
    """
    Verifies handle_payment_intent_succeeded creates a real Order from a
    Stripe PaymentIntent payload, independent of the webhook view itself.
    """

    def test_successful_payment_creates_order_with_line_items(self):
        portion = make_dish_portion()
        event = {
            "data": {
                "object": {
                    "id": "pi_test_abc",
                    "metadata": {
                        "bag": json.dumps({str(portion.id): 2}),
                        "delivery_type": "delivery",
                        "email": "customer@example.com",
                        "username": "AnonymousUser",
                    },
                    "charges": {
                        "data": [
                            {
                                "billing_details": {
                                    "name": "Jane Customer",
                                    "phone": "12345",
                                    "address": {
                                        "line1": "1 Test St",
                                        "city": "Testville",
                                        "postal_code": "AB1 2CD",
                                    },
                                }
                            }
                        ]
                    },
                }
            }
        }
        handler = StripeWH_Handler(request=MagicMock())
        response = handler.handle_payment_intent_succeeded(event)

        self.assertEqual(response.status_code, 200)
        order = Order.objects.get(stripe_pid="pi_test_abc")
        self.assertEqual(order.email, "customer@example.com")
        self.assertEqual(order.lineitems.count(), 1)
        self.assertEqual(order.lineitems.first().quantity, 2)

    def test_duplicate_payment_intent_does_not_create_a_second_order(self):
        portion = make_dish_portion()
        event = {
            "data": {
                "object": {
                    "id": "pi_dup",
                    "metadata": {
                        "bag": json.dumps({str(portion.id): 1}),
                        "delivery_type": "pickup",
                        "email": "a@example.com",
                    },
                    "charges": {"data": [{}]},
                }
            }
        }
        handler = StripeWH_Handler(request=MagicMock())
        handler.handle_payment_intent_succeeded(event)
        handler.handle_payment_intent_succeeded(event)
        self.assertEqual(Order.objects.filter(stripe_pid="pi_dup").count(), 1)


class CacheCheckoutDataSessionBindingTests(TestCase):
    """
    Regression test for binding the created PaymentIntent to the session
    before trusting a client-supplied stripe_pid in cache_checkout_data.
    """

    def test_mismatched_pid_is_rejected(self):
        session = self.client.session
        session["stripe_pid"] = "pi_real_one"
        session.save()

        response = self.client.post(
            reverse("cache_checkout_data"),
            {"stripe_pid": "pi_attacker_supplied", "delivery_type": "delivery"},
        )
        self.assertEqual(response.status_code, 403)

    def test_missing_session_pid_is_rejected(self):
        response = self.client.post(
            reverse("cache_checkout_data"),
            {"stripe_pid": "pi_whatever", "delivery_type": "delivery"},
        )
        self.assertEqual(response.status_code, 403)

    @patch("stripe.PaymentIntent.modify")
    def test_matching_pid_is_accepted(self, mock_modify):
        session = self.client.session
        session["stripe_pid"] = "pi_real_one"
        session.save()

        response = self.client.post(
            reverse("cache_checkout_data"),
            {"stripe_pid": "pi_real_one", "delivery_type": "delivery"},
        )
        self.assertEqual(response.status_code, 200)
        mock_modify.assert_called_once()


class CheckoutViewCreatesSessionBoundPaymentIntentTests(TestCase):
    """
    Payment intent creation was moved out of the GET checkout() view
    into create_payment_intent() (see that view's docstring) so the
    page can render without blocking on a live Stripe call - these
    cover that split instead of the old moved-out behaviour.
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username="shopper", password="testpass12345"
        )
        self.portion = make_dish_portion()

    @patch("stripe.PaymentIntent.create")
    def test_create_payment_intent_stores_new_pid_in_session(
        self, mock_create
    ):
        mock_intent = MagicMock()
        mock_intent.id = "pi_new_one"
        mock_intent.client_secret = "pi_new_one_secret_xyz"
        mock_create.return_value = mock_intent

        self.client.login(username="shopper", password="testpass12345")
        session = self.client.session
        session["bag"] = {str(self.portion.id): 1}
        session.save()

        response = self.client.post(reverse("create_payment_intent"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get("stripe_pid"), "pi_new_one")

    @patch("stripe.PaymentIntent.create")
    def test_checkout_get_does_not_create_payment_intent(self, mock_create):
        self.client.login(username="shopper", password="testpass12345")
        session = self.client.session
        session["bag"] = {str(self.portion.id): 1}
        session.save()

        response = self.client.get(reverse("checkout"))

        self.assertEqual(response.status_code, 200)
        mock_create.assert_not_called()


class UpdateOrderStatusEndpointRemovedTests(TestCase):
    """
    Regression test: the unauthenticated checkout.views.update_order_status
    was removed as dead code; the only routed 'update_order_status' URL must
    be the staff-protected admin_dashboard_view version.
    """

    def setUp(self):
        self.portion = make_dish_portion()
        self.order = Order.objects.create(
            full_name="Test",
            email="a@example.com",
            phone_number="123",
            street_address1="1 St",
            town_or_city="Town",
            status="Pending",
        )

    def test_anonymous_user_cannot_update_order_status(self):
        url = reverse("update_order_status", args=[self.order.id])
        response = self.client.post(url, {"status": "Cancelled"})
        # Staff-only view redirects anonymous users to login rather than
        # applying the change.
        self.assertNotEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "Pending")

    def test_non_staff_user_cannot_update_order_status(self):
        User.objects.create_user(username="regular", password="testpass12345")
        self.client.login(username="regular", password="testpass12345")
        url = reverse("update_order_status", args=[self.order.id])
        response = self.client.post(url, {"status": "Cancelled"})
        self.assertNotEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "Pending")
