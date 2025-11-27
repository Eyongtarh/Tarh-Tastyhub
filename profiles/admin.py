from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'default_phone_number',
        'default_local',
        'email_verified'
    )
    list_filter = ('email_verified',)
