"""
Tests for the feedback form: honeypot spam rejection and field validation.
"""
from django.test import TestCase

from .forms import FeedbackForm
from .models import Feedback


class FeedbackFormTests(TestCase):
    def valid_data(self, **overrides):
        data = {
            "name": "Jane Doe",
            "email": "JANE@Example.com",
            "subject": "Great food",
            "message": "I really enjoyed my order, thank you!",
            "honeypot": "",
        }
        data.update(overrides)
        return data

    def test_valid_submission_is_accepted(self):
        form = FeedbackForm(data=self.valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_email_is_lowercased(self):
        form = FeedbackForm(data=self.valid_data())
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["email"], "jane@example.com")

    def test_honeypot_filled_in_is_rejected(self):
        form = FeedbackForm(data=self.valid_data(honeypot="I am a bot"))
        self.assertFalse(form.is_valid())

    def test_short_name_is_rejected(self):
        form = FeedbackForm(data=self.valid_data(name="J"))
        self.assertFalse(form.is_valid())

    def test_short_message_is_rejected(self):
        form = FeedbackForm(data=self.valid_data(message="Too short"))
        self.assertFalse(form.is_valid())

    def test_short_subject_is_rejected(self):
        form = FeedbackForm(data=self.valid_data(subject="Hi"))
        self.assertFalse(form.is_valid())


class FeedbackViewTests(TestCase):
    def test_get_renders_form(self):
        response = self.client.get("/feedback/")
        self.assertEqual(response.status_code, 200)

    def test_post_valid_data_creates_feedback(self):
        response = self.client.post(
            "/feedback/",
            {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "subject": "Great food",
                "message": "I really enjoyed my order, thank you!",
                "honeypot": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Feedback.objects.count(), 1)

    def test_post_honeypot_does_not_create_feedback(self):
        response = self.client.post(
            "/feedback/",
            {
                "name": "Bot",
                "email": "bot@example.com",
                "subject": "Spam subject",
                "message": "This is definitely spam content here.",
                "honeypot": "filled",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Feedback.objects.count(), 0)
