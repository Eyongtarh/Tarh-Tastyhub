"""
Admin configuration for Feedback model.
Displays feedback entries and allows filtering/searching in Django admin.
"""
from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'email',
        'subject',
        'created_at',
        'handled',
    )
    list_filter = ('handled', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
