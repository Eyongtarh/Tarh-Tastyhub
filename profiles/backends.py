from django.contrib.auth.backends import ModelBackend

class EmailVerifiedAuthBackend(ModelBackend):
    def user_can_authenticate(self, user):
        active = super().user_can_authenticate(user)
        return active and getattr(user, 'userprofile', None) and user.userprofile.email_verified
