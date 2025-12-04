from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user__username", "user__email")
    list_filter = ("email_verified",)
    ordering = ("user__username",)
