from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator

email_verification_token = PasswordResetTokenGenerator()


def send_verification_email(request, user):
    """
    Send an email to verify the user's email address.
    """
    current_site = get_current_site(request)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    verification_link = request.build_absolute_uri(
        reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
    )

    subject = 'Verify your email for your account'
    message = render_to_string('profiles/email_verification.html', {
        'user': user,
        'verification_link': verification_link,
        'domain': current_site.domain,
    })

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
