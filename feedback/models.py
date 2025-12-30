"""
Model for user Feedback submissions.
Supports optional user link, subject, message, and handling status.
"""
from django.db import models
from django.contrib.auth.models import User


class Feedback(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    handled = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
