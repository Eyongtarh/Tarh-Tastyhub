from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserProfile model.
    """
    list_display = ("id", "user")
    search_fields = ("user__username", "user__email")
    ordering = ("user__username",)
