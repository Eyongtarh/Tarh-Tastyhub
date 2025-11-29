import logging
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings

from .models import UserProfile

logger = logging.getLogger(__name__)

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        profile = getattr(user, 'userprofile', None)
        email_verified = getattr(profile, 'email_verified', False)
        return f"{user.pk}{timestamp}{email_verified}"

    def check_token(self, user, token):
        if not super().check_token(user, token):
            return False
        profile = getattr(user, 'userprofile', None)
        if profile and profile.last_verification_sent:
            expiry_time = profile.last_verification_sent + timedelta(hours=24)
            if timezone.now() > expiry_time:
                return False
        return True


email_verification_token = EmailVerificationTokenGenerator()


def send_verification_email(request, user):
    """
    Send a verification email using a single, canonical activation_link that
    is built server-side so the template is consistent.
    """
    try:
        profile = getattr(user, 'userprofile', None)
        if not profile:
            logger.warning(f"No UserProfile for user {user.pk}")
            return False

        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        activation_link = request.build_absolute_uri(
            f"/activate/{uid}/{token}/"
        )

        message = render_to_string('profiles/verification_email.html', {
            'user': user,
            'domain': current_site.domain,
            'activation_link': activation_link,
            'uid': uid,
            'token': token,
        })

        send_mail(
            subject=f'Verify Your {getattr(settings, "SITE_NAME", "Elah Tastyhub")} Account',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        profile.last_verification_sent = timezone.now()
        profile.save(update_fields=['last_verification_sent'])
        logger.info(f"Verification email sent to {user.email}")
        return True

    except BadHeaderError:
        logger.exception(f"BadHeaderError sending verification email to {user.email}")
        raise
    except Exception as e:
        logger.exception(f"Error sending verification email to {user.email}: {e}")
        return False
